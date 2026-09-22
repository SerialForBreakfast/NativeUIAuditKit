"""Shared, byte-backed FocusRing v1.2 contract. No model imports or writes."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPLITS = {"train": "train", "val": "validation", "validation": "validation", "test": "test", "development": "development"}
PREPROCESSING = {"expansion": 0.16, "cropSize": [256, 256], "coordinates": "xywh-top-left-pixels", "resize": "Pillow-affine-bilinear-v1"}


class FocusDataError(ValueError):
    pass


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def text(value):
    if not isinstance(value, str) or not value.strip():
        raise FocusDataError("missing_identity")
    return value


def local(path):
    path = Path(path).resolve()
    if not path.is_relative_to(ROOT):
        raise FocusDataError("outside_project")
    return path


def member(root, name):
    name = text(name)
    p = Path(name)
    if p.is_absolute() or ".." in p.parts:
        raise FocusDataError("unsafe_member")
    root = local(root)
    target = root / p
    if not target.resolve().is_relative_to(root) or any(v.is_symlink() for v in [target, *target.parents] if v != root.parent):
        raise FocusDataError("unsafe_member")
    if not target.is_file():
        raise FocusDataError("missing_pixels")
    return target


def image(root, record, expected_size=None):
    from PIL import Image
    p = member(root, record.get("path"))
    if p.stat().st_size > 32 * 1024 * 1024:
        raise FocusDataError("image_too_large")
    if hashlib.sha256(p.read_bytes()).hexdigest() != record.get("sha256"):
        raise FocusDataError("changed_hash")
    try:
        with Image.open(p, formats=["PNG"]) as im:
            if im.format != "PNG" or im.width * im.height > 40_000_000:
                raise FocusDataError("invalid_png")
            im.load()
            size = im.size
    except (OSError, ValueError) as e:
        raise FocusDataError("corrupt_image") from e
    if expected_size and tuple(expected_size) != size:
        raise FocusDataError("wrong_crop_dimensions")
    return size


def pixel_digest(root, record):
    """Decoded content, not PNG compression/container identity, controls isolation."""
    from PIL import Image
    with Image.open(member(root, record["path"])) as im:
        im.load()
        return hashlib.sha256(str(im.size).encode() + b"\0" + im.convert("RGB").tobytes()).hexdigest()


def validate_physical_review(review, source_root):
    if not isinstance(review, dict) or review.get("sourceKind") != "physicalFixture":
        raise FocusDataError("missing_physical_source_review")
    for key in ("reviewReference", "deviceReference", "runID", "captureID"):
        text(review.get(key))
    for field, name in (("indexSHA256", "dataset-index.json"), ("receiptSHA256", "harvest-receipt.json")):
        value = review.get(field)
        if not isinstance(value, str) or len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
            raise FocusDataError("invalid_physical_review_hash")
        if hashlib.sha256(member(source_root, name).read_bytes()).hexdigest() != value:
            raise FocusDataError("physical_review_binding_mismatch")
    # A source declaration remains reported, not authenticated. Contradictory
    # explicit simulator context cannot be relabeled by this review envelope.
    from harvest_bundle_validation import validate_bundle
    contract = validate_bundle(source_root)
    context = contract.get("sourceDescription") or {}
    method = context.get("captureMethod", "").lower()
    environment = context.get("environment") or {}
    if "simulator" in method or any(environment.get(k) for k in ("simulatorUDID", "simulator_udid", "isSimulator")):
        raise FocusDataError("conflicting_physical_source_context")
    return contract


def expanded_box(bounds, size):
    if not isinstance(bounds, list) or len(bounds) != 4 or any(type(v) not in (float, int) or not math.isfinite(v) for v in bounds):
        raise FocusDataError("invalid_frame_geometry")
    x, y, w, h = bounds
    if x < 0 or y < 0 or w <= 0 or h <= 0 or x + w > size[0] or y + h > size[1]:
        raise FocusDataError("invalid_frame_geometry")
    # makeCrop preserves fractional origin and rounds the intermediate canvas size.
    return [max(0, x - w * .16), max(0, y - h * .16),
            min(size[0], x + w + w * .16), min(size[1], y + h + h * .16)]


def crop_frame(raw, box):
    from PIL import Image
    x1, y1, x2, y2 = box
    size = (max(1, math.floor(x2 - x1 + .5)), max(1, math.floor(y2 - y1 + .5)))
    return raw.convert("RGB").transform(size, Image.Transform.AFFINE, (1, 0, x1, 0, 1, y1),
                                        Image.Resampling.BILINEAR).resize((256, 256), Image.Resampling.BILINEAR)


def validate_frames(pair, source_root, *, require_native=False):
    element = text(pair.get("elementID"))
    frames = pair.get("frames")
    if not isinstance(frames, dict) or set(frames) != {"focused", "unfocused"}:
        raise FocusDataError("missing_frame_evidence")
    sizes, boxes = {}, {}
    for role in ("focused", "unfocused"):
        frame = frames[role]
        if not isinstance(frame, dict) or frame.get("labelSource") != "fixtureCallback":
            raise FocusDataError("untrusted_focus_label")
        frame_id = text(frame.get("frameID"))
        if frame.get("focusFrameID") != frame_id or "observedFocusID" not in frame or frame["observedFocusID"] != (element if role == "focused" else None):
            raise FocusDataError("stale_or_mismatched_focus")
        if require_native:
            callback = frame.get("nativeObservation")
            expected = element if role == "focused" else "tvtr.reference-focus"
            if not isinstance(callback, dict) or callback.get("frameID") != frame_id or callback.get("imageSHA256") != frame.get("sha256"):
                raise FocusDataError("missing_or_unbound_native_observation")
            if callback.get("nativeFocusResolved") is not True or callback.get("observedElementIDs") != [expected]:
                raise FocusDataError("unknown_or_multiple_native_focus")
            age = callback.get("sampleAgeMilliseconds")
            stable = callback.get("stableMilliseconds")
            if (type(age) not in (int, float) or not math.isfinite(age) or not 0 <= age <= 150
                    or type(stable) not in (int, float) or not math.isfinite(stable) or stable < 150):
                raise FocusDataError("stale_or_unsettled_native_observation")
        sizes[role] = image(source_root, frame)
        boxes[role] = expanded_box(frame.get("bounds"), sizes[role])
    if sizes["focused"] != sizes["unfocused"] or frames["focused"]["frameID"] == frames["unfocused"]["frameID"]:
        raise FocusDataError("invalid_pair_frames")
    return boxes


def validate_manifest(document, dataset):
    """Validate actual crops and their raw-frame evidence; never grant launch approval."""
    if not isinstance(document, dict) or document.get("version") not in {"1.2", "1.3"}:
        raise FocusDataError("unsupported_crop_manifest")
    runtime = document["version"] == "1.3"
    from focus_runtime import RUNTIME_PREPROCESSING, identity, rendered_items
    if document.get("preprocessing") != (RUNTIME_PREPROCESSING if runtime else PREPROCESSING):
        raise FocusDataError("crop_parity_mismatch")
    if runtime and document.get("runtimeCrop") != identity():
        raise FocusDataError("runtime_crop_implementation_changed")
    if document.get("evidenceKind") not in {"test-only", "reviewed-fixture"}:
        raise FocusDataError("missing_evidence_kind")
    if document.get("sourceKind") not in {"simulatorFixture", "physicalFixture"}:
        raise FocusDataError("invalid_source_kind")
    text(document.get("corpusID")); text(document.get("producerReference"))
    root_name = text(document.get("sourceRoot"))
    if Path(root_name).is_absolute() or ".." in Path(root_name).parts:
        raise FocusDataError("unsafe_source_root")
    source_root = local(ROOT / root_name)
    if document["sourceKind"] == "physicalFixture":
        validate_physical_review(document.get("sourceReview"), source_root)
    pairs = document.get("pairs")
    if not isinstance(pairs, list) or not pairs:
        raise FocusDataError("empty_membership")
    ids, identities, ownership = set(), set(), {}
    rows = []
    pixel_cache = {}
    runtime_images = None
    for pair in pairs:
        if not isinstance(pair, dict):
            raise FocusDataError("invalid_pair")
        pid = text(pair.get("pair_id"))
        split = SPLITS.get(pair.get("split"))
        if split is None:
            raise FocusDataError("invalid_partition")
        if pid in ids:
            raise FocusDataError("duplicate_pair_id")
        ids.add(pid)
        if pair.get("labelSource") != "fixtureGroundTruth" or pair.get("sourceKind") != document["sourceKind"]:
            raise FocusDataError("untrusted_pair_source")
        group = text(pair.get("recipe_group"))
        seed_value = pair.get("recipe_seed")
        if type(seed_value) is not int or seed_value < 0:
            raise FocusDataError("invalid_recipe_seed")
        seed = str(seed_value)
        scene = text(pair.get("fixture_scene")); theme = text(pair.get("theme")); control = text(pair.get("element_type"))
        from simulator_focus_manifest import FAMILY_MAP, THEME_MAP
        if scene not in FAMILY_MAP.values() or theme not in THEME_MAP.values():
            raise FocusDataError("unsupported_pair_metadata")
        boxes = validate_frames(pair, source_root, require_native=document["sourceKind"] == "physicalFixture")
        identity = (pair["frames"]["focused"]["sha256"], pair["frames"]["unfocused"]["sha256"], pair["elementID"])
        if identity in identities:
            raise FocusDataError("duplicate_pair_content")
        identities.add(identity)
        keys = [("group", group), ("seed", seed)]
        for role in ("focused", "unfocused"):
            crop = {"path": pair.get(role + "_crop"), "sha256": pair.get(role + "_crop_sha256")}
            image(dataset, crop, (256, 256))
            if pair.get(role + "_crop_box") != boxes[role]:
                raise FocusDataError("crop_geometry_mismatch")
            from PIL import Image
            with Image.open(member(source_root, pair["frames"][role]["path"])) as raw, Image.open(member(dataset, crop["path"])) as actual:
                if runtime:
                    if runtime_images is None:
                        runtime_images = rendered_items(document)
                    key, _, expected = next(runtime_images)
                    if key != f"{pid}:{1 if role == 'focused' else 0}":
                        raise FocusDataError("runtime_membership_mismatch")
                else:
                    expected = crop_frame(raw, boxes[role])
                if expected.tobytes() != actual.convert("RGB").tobytes():
                    raise FocusDataError("crop_pixel_mismatch")
            keys += [("pixels", crop["sha256"]), ("pixels", pair["frames"][role]["sha256"])]
            for r, record in ((dataset, crop), (source_root, pair["frames"][role])):
                cache_key = (str(r), record["path"], record["sha256"])
                if cache_key not in pixel_cache: pixel_cache[cache_key] = pixel_digest(r, record)
                keys.append(("decoded_pixels", pixel_cache[cache_key]))
        for key in keys:
            if key in ownership and ownership[key] != split:
                raise FocusDataError("split_leakage")
            ownership[key] = split
        rows.append({"pairID": pid, "focused": pair["focused_crop"], "unfocused": pair["unfocused_crop"],
                     "seed": seed, "recipeGroup": group, "split": split, "scene": scene, "theme": theme,
                     "class": control, "labelSource": "fixtureGroundTruth", "sourceKind": pair["sourceKind"],
                     "validatedUnfocusedEvidence": pair["frames"]["unfocused"]})
        if "alignment" in pair:
            from focus_ring_readiness import validate_alignment
            validate_alignment(pair["alignment"])
            rows[-1]["alignment"] = pair["alignment"]
    return rows
