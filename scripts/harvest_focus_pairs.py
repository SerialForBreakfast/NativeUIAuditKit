#!/usr/bin/env python3
"""
harvest_focus_pairs.py — Extract 256×256 focus-ring crops for FocusRingDetector.

Phase A (default): read `dataset/tvos_fixture_captures/*.png` plus YOLO `*_result.json`
sidecars for diagnostics only, never trusted training labels. Trusted paired
extraction requires --fixture-bundle plus --pair-evidence. Legacy output cannot
pass the v1.2 candidate preflight.

Phase B (`--live`): closed-loop N-way aatv capture on a live Apple TV (BP-40).
Simulator is not sufficient (Metal glow / parallax). Requires `--device-id` and a
running TVTestRig coordinator (`--project`). Never presses Home or Select.

Crops and the extract-mode manifest default to `dataset/focus_ring/`.
Live harvest should pass `--output dataset/focus_ring` (in-package gitignored cache).
`--dry-run` never writes. Do not pass `dataset/dataset/train`.

Usage:
  .venv-yolo/bin/python scripts/harvest_focus_pairs.py --dry-run
  .venv-yolo/bin/python scripts/harvest_focus_pairs.py --output NativeUITrainer/.tmp/focus_ring_extract
  .venv-yolo/bin/python scripts/harvest_focus_pairs.py --live --device-id <UDID> \\
      --project /path/to/TVTestRig --output dataset/focus_ring
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from harvest_bundle_validation import HarvestValidationError, validate_bundle
from simulator_focus_manifest import SimulatorManifestError, build as build_simulator_manifest
from focus_dataset_contract import FocusDataError, PREPROCESSING, local, validate_frames, digest, crop_frame

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = PROJECT_ROOT / "dataset" / "tvos_fixture_captures"
DEFAULT_OUTPUT = PROJECT_ROOT / "dataset" / "focus_ring"
DEFAULT_LIVE_OUTPUT = PROJECT_ROOT / "dataset" / "focus_ring"
DEFAULT_DEVICE_ID = "8D80F616-6C12-49A6-9015-8F594EE5F24E"
DEFAULT_PROJECT = PROJECT_ROOT.parent / "TVTestRig"
DEFAULT_AATV = (
    Path.home()
    / "Library/Developer/Xcode/DerivedData/TVTestRig-bfjtodidumtdyagsgxcmwrmheuxr"
    / "Build/Products/Debug/TVTestRig.app/Contents/Helpers/aatv"
)
DEFAULT_WEIGHTS = PROJECT_ROOT / "NativeUITrainer" / "yolo_runs" / "phase6b_tvos_v3" / "weights" / "best.pt"
FIXTURE_BUNDLE_ID = "com.showblender.TVTestRigFixture"
CONTAINER_HOME = Path.home() / "Library/Containers/com.showblender.TVTestRig/Data"
CONTAINER_SOCKET = CONTAINER_HOME / ".tvtr" / ".tvtr" / "s"
AATV_HOME = PROJECT_ROOT / "NativeUITrainer" / ".tmp" / "aatv_home"

FOCUSABLE = frozenset(
    {
        "collectionItem",
        "listRow",
        "primaryButton",
        "secondaryButton",
        "tabBar",
        "cancelAction",
        "toggle",
        "secureField",
        "textField",
        "segmentedControl",
        "stepperControl",
        "slider",
    }
)
CROP_SIZE = 256
EXPANSION = 0.16
SPLIT_TEST_MOD = 0  # recipe_seed % 10
SPLIT_VAL_MOD = 1
AREA_RATIO_FOCUSED = 1.12
IOU_MATCH = 0.35
DIRECTION_CYCLE = ("right", "down", "left", "down", "right", "up", "left", "up")
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"

os_env_defaults = {
    "YOLO_CONFIG_DIR": str(PROJECT_ROOT / "NativeUITrainer" / ".ultralytics"),
    "MPLCONFIGDIR": str(PROJECT_ROOT / "NativeUITrainer" / ".mplconfig"),
    "TORCH_HOME": str(PROJECT_ROOT / "NativeUITrainer" / ".torch"),
}
for _k, _v in os_env_defaults.items():
    os.environ.setdefault(_k, _v)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Harvest FocusRingDetector 256×256 crops.")
    p.add_argument("--input", default=str(DEFAULT_INPUT), help="Directory of PNG + JSON captures")
    p.add_argument("--fixture-bundle", type=Path, help="Completed fixture bundle; validates before paired simulator extraction")
    p.add_argument("--corpus-id", help="Required with --fixture-bundle")
    p.add_argument("--producer-reference", help="Required source revision with --fixture-bundle")
    p.add_argument("--pair-evidence", type=Path, help="Explicit NUIAK focus-pair-evidence-v1 review artifact; never predicted labels")
    p.add_argument("--ttr-sidecar-v2", action="store_true", help="Use validated producer brackets and runtime crops; development only")
    p.add_argument("--visual-review", type=Path, help="Hash-bound v2 bundle geometry/source review")
    p.add_argument("--test-only", action="store_true", help="Mark v2 output as test-only; cannot qualify genuine data")
    p.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help="Manifest/crop root (defaults to sibling NativeUIAuditKit-Dataset/focus_ring)",
    )
    p.add_argument("--dry-run", action="store_true", help="Inventory only; write nothing")
    p.add_argument("--include-unlabeled", action="store_true", help="Keep crops with no isFocused label")
    p.add_argument("--live", action="store_true", help="Phase B: aatv N-way capture (needs hardware)")
    p.add_argument("--device-id", default=DEFAULT_DEVICE_ID, help="Apple TV identifier for --live")
    p.add_argument("--aatv", default="aatv", help="aatv CLI path")
    p.add_argument("--project", default=str(DEFAULT_PROJECT), help="TVTestRig repo root (AGENTS.md + xcodeproj)")
    p.add_argument("--weights", default=str(DEFAULT_WEIGHTS), help="YOLO11 tvOS weights for live pairing")
    p.add_argument("--max-pairs", type=int, default=1500, help="Stop live harvest after this many labeled pairs")
    p.add_argument("--max-steps", type=int, default=2500, help="Stop live harvest after this many navigate steps")
    p.add_argument("--area-ratio", type=float, default=AREA_RATIO_FOCUSED)
    p.add_argument("--iou", type=float, default=IOU_MATCH)
    p.add_argument("--expansion", type=float, default=EXPANSION)
    p.add_argument("--conf", type=float, default=0.25, help="YOLO confidence floor")
    return p.parse_args()


def load_json(path: Path) -> object | None:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return None


def recipe_seed_for(pair_id: str) -> int:
    digest = hashlib.sha256(pair_id.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % 10000


def split_for_seed(seed: int) -> str:
    lane = seed % 10
    if lane == SPLIT_TEST_MOD:
        return "test"
    if lane == SPLIT_VAL_MOD:
        return "val"
    return "train"


def box_to_xyxy(box: list) -> tuple[float, float, float, float] | None:
    if not isinstance(box, list) or len(box) < 4:
        return None
    x1, y1, x2, y2 = (float(box[0]), float(box[1]), float(box[2]), float(box[3]))
    if x2 <= x1 or y2 <= y1:
        return None
    return x1, y1, x2, y2


def expanded_clamp(
    x1: float, y1: float, x2: float, y2: float, width: int, height: int, expansion: float
) -> tuple[int, int, int, int]:
    bw = x2 - x1
    bh = y2 - y1
    ex = bw * expansion
    ey = bh * expansion
    nx1 = max(0.0, x1 - ex)
    ny1 = max(0.0, y1 - ey)
    nx2 = min(float(width), x2 + ex)
    ny2 = min(float(height), y2 + ey)
    if nx2 <= nx1 or ny2 <= ny1:
        return 0, 0, width, height
    return int(round(nx1)), int(round(ny1)), int(round(nx2)), int(round(ny2))


def label_from_detection(det: dict) -> bool | None:
    if "isFocused" in det and isinstance(det["isFocused"], bool):
        return det["isFocused"]
    state = det.get("state")
    if isinstance(state, dict) and isinstance(state.get("isFocused"), bool):
        return state["isFocused"]
    return None


def detections_from_sidecar(sidecar: dict | None) -> list[dict]:
    if not isinstance(sidecar, dict):
        return []
    elements = sidecar.get("elements") or []
    out: list[dict] = []
    for el in elements:
        if not isinstance(el, dict):
            continue
        elem_type = el.get("elementType") or el.get("type")
        bounds = el.get("boundsPixels") or el.get("boundingBoxPixels")
        box = None
        if isinstance(bounds, dict):
            x = float(bounds.get("x", 0))
            y = float(bounds.get("y", 0))
            w = float(bounds.get("width", 0))
            h = float(bounds.get("height", 0))
            box = [x, y, x + w, y + h]
        elif isinstance(el.get("box"), list):
            box = el["box"]
        if not elem_type or box is None:
            continue
        out.append({"type": elem_type, "box": box, "isFocused": label_from_detection(el), "confidence": el.get("confidence", 1.0)})
    return out


def detections_from_yolo(result: object) -> list[dict]:
    if not isinstance(result, list):
        return []
    out: list[dict] = []
    for det in result:
        if not isinstance(det, dict):
            continue
        out.append(
            {
                "type": det.get("type") or det.get("class"),
                "box": det.get("box"),
                "isFocused": label_from_detection(det),
                "confidence": det.get("confidence", 0.0),
            }
        )
    return out


def merge_detections(sidecar_dets: list[dict], yolo_dets: list[dict]) -> list[dict]:
    """Prefer sidecar ground truth; fall back to YOLO boxes."""
    if any(d.get("isFocused") is not None for d in sidecar_dets) or sidecar_dets:
        labeled = [d for d in sidecar_dets if d.get("type") in FOCUSABLE]
        if labeled:
            return labeled
    return [d for d in yolo_dets if d.get("type") in FOCUSABLE]


def crop_rgb(image, xyxy: tuple[int, int, int, int]):
    from PIL import Image

    x1, y1, x2, y2 = xyxy
    crop = image.crop((x1, y1, x2, y2))
    return crop.resize((CROP_SIZE, CROP_SIZE), Image.Resampling.BILINEAR)


def extract_from_directory(input_dir: Path, expansion: float) -> list[dict]:
    from PIL import Image

    records: list[dict] = []
    pngs = sorted(input_dir.glob("*.png"))
    for png in pngs:
        if png.name.endswith("_result.png"):
            continue
        sidecar = load_json(png.with_suffix(".json"))
        yolo = load_json(png.parent / f"{png.stem}_result.json")
        dets = merge_detections(detections_from_sidecar(sidecar if isinstance(sidecar, dict) else None), detections_from_yolo(yolo))
        try:
            image = Image.open(png).convert("RGB")
        except OSError:
            continue
        w, h = image.size
        theme = "system"
        scene = png.stem
        if isinstance(sidecar, dict):
            image_meta = sidecar.get("image") or {}
            theme = str(image_meta.get("colorScheme") or sidecar.get("theme") or theme)
            profile = sidecar.get("generatorProfile") or {}
            scene = str(profile.get("tab") or profile.get("templateFamily") or scene)
        for idx, det in enumerate(dets):
            xyxy = box_to_xyxy(det.get("box") or [])
            if xyxy is None:
                continue
            x1, y1, x2, y2 = xyxy
            pair_id = f"{png.stem}_{idx:04d}"
            seed = recipe_seed_for(pair_id)
            nx1, ny1, nx2, ny2 = expanded_clamp(x1, y1, x2, y2, w, h, expansion)
            label = det.get("isFocused")
            records.append(
                {
                    "pair_id": pair_id,
                    "recipe_seed": seed,
                    "fixture_scene": scene,
                    "theme": theme,
                    "element_type": det.get("type"),
                    "source_image": str(png.relative_to(PROJECT_ROOT)) if png.is_relative_to(PROJECT_ROOT) else str(png),
                    "bbox_normalized": [x1 / w, y1 / h, (x2 - x1) / w, (y2 - y1) / h],
                    "expanded_xyxy": [nx1, ny1, nx2, ny2],
                    "split": split_for_seed(seed),
                    "label": label,
                    "_pil": image,
                    "_crop_box": (nx1, ny1, nx2, ny2),
                }
            )
    return records


def write_records(records: list[dict], output: Path, include_unlabeled: bool) -> dict:
    crops_dir = output / "crops"
    crops_dir.mkdir(parents=True, exist_ok=True)
    pairs: list[dict] = []
    skipped_unlabeled = 0
    for rec in records:
        label = rec.get("label")
        if label is None and not include_unlabeled:
            skipped_unlabeled += 1
            continue
        suffix = "focused" if label is True else ("unfocused" if label is False else "unlabeled")
        crop_name = f"{rec['pair_id']}_{suffix}.png"
        crop_path = crops_dir / crop_name
        crop = crop_rgb(rec["_pil"], rec["_crop_box"])
        crop.save(crop_path)
        entry = {
            "pair_id": rec["pair_id"],
            "recipe_seed": rec["recipe_seed"],
            "fixture_scene": rec["fixture_scene"],
            "theme": rec["theme"],
            "element_type": rec["element_type"],
            "unfocused_crop": None if label is not False else f"crops/{crop_name}",
            "focused_crop": None if label is not True else f"crops/{crop_name}",
            "unlabeled_crop": f"crops/{crop_name}" if label is None else None,
            "bbox_normalized": rec["bbox_normalized"],
            "split": rec["split"],
        }
        pairs.append({k: v for k, v in entry.items() if v is not None})
    manifest = {
        "version": "1.0",
        "generatedAt": utc_now(),
        "source": "harvest_focus_pairs.py",
        "pairs": pairs,
        "skipped_unlabeled": skipped_unlabeled,
    }
    (output / "focus_dataset_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def extract_fixture_bundle(bundle: Path, output: Path, corpus_id: str, producer_reference: str, expansion: float, dry_run: bool, pair_evidence: dict | None = None) -> dict:
    """Extract true focused/unfocused crop pairs only from an integrity-checked bundle."""
    from PIL import Image

    output = local(output)
    bundle = local(bundle)
    if expansion != EXPANSION:
        raise SimulatorManifestError("crop_parity_mismatch")
    if output.exists():
        raise SimulatorManifestError("output_collision")
    contract = validate_bundle(bundle)
    if not isinstance(pair_evidence, dict) or pair_evidence.get("version") != "focus-pair-evidence-v1":
        raise SimulatorManifestError("missing_observed_pair_evidence")
    source_kind = pair_evidence.get("sourceKind")
    if pair_evidence.get("evidenceKind") not in {"test-only", "reviewed-fixture"} or source_kind not in {"simulatorFixture", "physicalFixture"} or pair_evidence.get("producerReference") != producer_reference:
        raise SimulatorManifestError("invalid_evidence_context")
    source_review = None
    if source_kind == "physicalFixture":
        from focus_dataset_contract import validate_physical_review
        source_review = pair_evidence.get("sourceReview")
        validate_physical_review(source_review, bundle)
    manifest = build_simulator_manifest(contract, corpus_id, producer_reference, None, source_kind)
    purpose = pair_evidence.get("purpose", "partition-preserving")
    if purpose not in {"partition-preserving", "development-pilot"}:
        raise SimulatorManifestError("unsupported_evidence_purpose")
    evidence_rows = pair_evidence.get("pairs")
    if not isinstance(evidence_rows, list) or any(not isinstance(v, dict) for v in evidence_rows):
        raise SimulatorManifestError("invalid_pair_evidence")
    evidence = {v.get("pairID"): v for v in evidence_rows}
    if len(evidence) != len(evidence_rows) or set(evidence) != {r["pairID"] for r in manifest["pairs"]}:
        raise SimulatorManifestError("evidence_membership_mismatch")
    pairs: list[dict] = []
    seen: set[str] = set()
    for row in manifest["pairs"]:
        focused = Image.open(bundle / row["focused"]["path"]).convert("RGB")
        unfocused = Image.open(bundle / row["unfocused"]["path"]).convert("RGB")
        if focused.size != unfocused.size:
            raise SimulatorManifestError("pair_dimension_mismatch")
        selected = [e for e in row["elements"] if e.get("is_focused") and e.get("taxonomy_class") in FOCUSABLE]
        if len(selected) != 1:
            raise SimulatorManifestError("unsupported_focus_target")
        element = selected[0]
        proof = evidence[row["pairID"]]
        if proof.get("elementID") != element["element_id"]:
            raise SimulatorManifestError("evidence_element_mismatch")
        crop_boxes = validate_frames(proof, bundle, require_native=source_kind == "physicalFixture")
        if proof["frames"]["focused"]["bounds"] != element["pixel_bounds"]:
            raise SimulatorManifestError("evidence_geometry_mismatch")
        x, y, width, height = element["pixel_bounds"]
        normalized = element["normalized_bounds"]
        expected = [x/focused.width, y/focused.height, (x+width)/focused.width, (y+height)/focused.height]
        if any(abs(a-b) > 1e-6 for a, b in zip(normalized, expected)):
            raise SimulatorManifestError("coordinate_representation_mismatch")
        for role in ("focused", "unfocused"):
            if any(proof["frames"][role].get(k) != row[role][k] for k in ("path", "sha256")):
                raise SimulatorManifestError("evidence_frame_mismatch")
        pair_id = f"{row['pairID']}:{element['element_id']}"
        if pair_id in seen:
            raise SimulatorManifestError("duplicate_pair_id")
        seen.add(pair_id)
        entry = {
            "pair_id": pair_id, "recipe_group": row["recipeGroup"], "recipe_seed": int(row["recipeGroup"].rsplit(":", 1)[1]),
            "fixture_scene": row["family"], "original_fixture_scene": row["originalFamily"],
            "theme": row["theme"], "original_theme": row["originalTheme"], "element_type": element["taxonomy_class"],
            "split": "development" if purpose == "development-pilot" else row["split"],
            "original_split": row["split"], "labelSource": "fixtureGroundTruth", "sourceKind": source_kind,
            "frames": proof["frames"], "elementID": proof["elementID"],
            "source": {"unfocused": row["unfocused"], "focused": row["focused"]},
            "validatedUnfocusedEvidence": proof["frames"]["unfocused"],
            "bbox_normalized": element["normalized_bounds"], "hardNegative": element["taxonomy_class"] in {"imageView", "collectionItem"},
        }
        for role in ("focused", "unfocused"):
            entry[role + "_crop_box"] = crop_boxes[role]
        pairs.append((entry, focused, unfocused, crop_boxes))
    if not pairs:
        raise SimulatorManifestError("no_focusable_pairs")
    if dry_run:
        return {"pairs": len(pairs), "corpusID": corpus_id, "dryRun": True}
    crops = output / "crops"
    output.mkdir(parents=True, exist_ok=False)
    crops.mkdir()
    output_pairs = []
    for entry, focused, unfocused, crop_boxes in pairs:
        crop_id = hashlib.sha256(entry["pair_id"].encode()).hexdigest()
        focused_name, unfocused_name = f"{crop_id}_focused.png", f"{crop_id}_unfocused.png"
        crop_frame(focused, crop_boxes["focused"]).save(crops / focused_name)
        crop_frame(unfocused, crop_boxes["unfocused"]).save(crops / unfocused_name)
        entry["focused_crop"] = f"crops/{focused_name}"
        entry["unfocused_crop"] = f"crops/{unfocused_name}"
        entry["focused_crop_sha256"] = hashlib.sha256((crops / focused_name).read_bytes()).hexdigest()
        entry["unfocused_crop_sha256"] = hashlib.sha256((crops / unfocused_name).read_bytes()).hexdigest()
        output_pairs.append(entry)
    result = {"version": "1.2", "sourceKind": source_kind, "corpusID": corpus_id, "pairs": output_pairs,
              "eligibility": manifest["eligibility"], "sourceRoot": str(bundle.relative_to(PROJECT_ROOT)),
              "producerReference": producer_reference, "preprocessing": PREPROCESSING,
              "evidenceKind": pair_evidence["evidenceKind"], "evidenceSHA256": digest(pair_evidence)}
    result["observedSource"] = contract.get("sourceDescription")
    if source_review is not None: result["sourceReview"] = source_review
    from focus_dataset_contract import validate_manifest
    # Publish membership only after checking the actual derived bytes and isolation.
    # Failed output is retained for diagnosis, never advertised as a completed corpus.
    validate_manifest(result, output)
    (output / "focus_dataset_manifest.json").write_text(json.dumps(result, indent=2) + "\n")
    return {"pairs": len(output_pairs), "corpusID": corpus_id, "output": str(output)}


def summarize(records: list[dict]) -> None:
    labels = Counter("focused" if r["label"] is True else ("unfocused" if r["label"] is False else "unlabeled") for r in records)
    types = Counter(r["element_type"] for r in records)
    splits = Counter(r["split"] for r in records)
    print(f"captures/crops: {len(records)}")
    print(f"labels: {dict(labels)}")
    print(f"splits (by recipe_seed): {dict(splits)}")
    print("types:")
    for name, n in types.most_common():
        print(f"  {name:20s} {n}")


def refuse_hang_path(output: Path) -> bool:
    return "dataset/dataset/train" in str(output)


def resolve_aatv(explicit: str) -> str:
    if explicit and explicit != "aatv":
        return explicit
    which = shutil.which("aatv")
    if which:
        return which
    if DEFAULT_AATV.exists():
        return str(DEFAULT_AATV)
    return "aatv"


def project_socket(project: str) -> Path:
    return Path(project).expanduser().resolve() / ".tvtr" / "s"


def resolve_ipc(project: str) -> tuple[str | None, dict[str, str]]:
    """
    Prefer the GitHub checkout socket. Sandboxed TVTestRig otherwise binds
    `Containers/.../Data/.tvtr/.tvtr/s`. Point aatv HOME at a tiny in-package
    directory with a symlink to that socket — do not set HOME to the container
    Data root (Evidence/Sessions listdir hangs).
    """
    env = os.environ.copy()
    if project_socket(project).exists():
        return project, env
    if CONTAINER_SOCKET.exists():
        sock_dir = AATV_HOME / ".tvtr" / ".tvtr"
        sock_dir.mkdir(parents=True, exist_ok=True)
        link = sock_dir / "s"
        if link.is_symlink() or link.exists():
            link.unlink()
        link.symlink_to(CONTAINER_SOCKET)
        env["HOME"] = str(AATV_HOME)
        env.pop("TVTESTRIG_PROJECT", None)
        return None, env
    return project, env


def parse_json_blob(text: str) -> dict | None:
    text = (text or "").strip()
    if not text:
        return None
    try:
        value = json.loads(text)
        return value if isinstance(value, dict) else None
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            try:
                value = json.loads(text[start : end + 1])
                return value if isinstance(value, dict) else None
            except json.JSONDecodeError:
                return None
    return None


def run_aatv(
    aatv: str,
    project: str | None,
    args: list[str],
    device_id: str | None,
    timeout_ms: int = 15000,
    binary: bool = False,
    extra_env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess:
    """
    Invoke aatv. Global flags precede the subcommand. `timeout_ms` is capped at 30000.
    Omit `--project` when talking to the sandboxed application-workspace socket.
    """
    timeout_ms = max(1, min(int(timeout_ms), 30000))
    cmd = [aatv, "--device-id", device_id or DEFAULT_DEVICE_ID, "--timeout-ms", str(timeout_ms)]
    if project:
        cmd[1:1] = ["--project", project]
    if not binary:
        cmd.append("--json")
    cmd.extend(args)
    return subprocess.run(
        cmd,
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=not binary,
        timeout=(timeout_ms / 1000.0) + 5.0,
        env=extra_env,
    )


def aatv_error_code(proc: subprocess.CompletedProcess) -> str | None:
    text = proc.stdout if isinstance(proc.stdout, str) else ""
    payload = parse_json_blob(text)
    if not isinstance(payload, dict):
        return None
    err = payload.get("error")
    if isinstance(err, dict) and isinstance(err.get("code"), str):
        return err["code"]
    return None


def aatv_ok(proc: subprocess.CompletedProcess) -> bool:
    if proc.returncode != 0:
        return False
    payload = parse_json_blob(proc.stdout if isinstance(proc.stdout, str) else "")
    if payload is None:
        return True
    if payload.get("success") is False:
        return False
    return "error" not in payload


def print_aatv_failure(proc: subprocess.CompletedProcess) -> None:
    stdout = proc.stdout if isinstance(proc.stdout, str) else ""
    stderr = proc.stderr if isinstance(proc.stderr, str) else ""
    if stdout:
        print(stdout[:2000])
    if stderr:
        print(stderr[:2000])


def looks_like_home(dets: list[dict]) -> bool:
    """Halt if the frame looks like tvOS Home (searchField + low collectionItems)."""
    types = [d.get("type") for d in dets]
    if "searchField" not in types:
        return False
    items = []
    for d in dets:
        if d.get("type") != "collectionItem":
            continue
        xyxy = box_to_xyxy(d.get("box") or [])
        if xyxy is None:
            continue
        items.append(xyxy)
    if len(items) < 8:
        return False
    ys = sorted((b[1] + b[3]) / 2.0 for b in items)
    median_y = ys[len(ys) // 2]
    return median_y > 800.0


def box_area(xyxy: tuple[float, float, float, float]) -> float:
    return max(0.0, xyxy[2] - xyxy[0]) * max(0.0, xyxy[3] - xyxy[1])


def iou_xyxy(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> float:
    ix1 = max(a[0], b[0])
    iy1 = max(a[1], b[1])
    ix2 = min(a[2], b[2])
    iy2 = min(a[3], b[3])
    inter = max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)
    union = box_area(a) + box_area(b) - inter
    return inter / union if union > 0 else 0.0


def match_grown(
    prev: list[dict], curr: list[dict], iou_thresh: float, area_ratio: float
) -> list[tuple[dict, dict, float, float]]:
    """Greedy same-type IoU match; keep pairs whose current box grew by area_ratio."""
    candidates: list[tuple[float, int, int]] = []
    prev_xy = []
    curr_xy = []
    for d in prev:
        xy = box_to_xyxy(d.get("box") or [])
        prev_xy.append(xy)
    for d in curr:
        xy = box_to_xyxy(d.get("box") or [])
        curr_xy.append(xy)
    for i, p in enumerate(prev):
        if prev_xy[i] is None:
            continue
        for j, c in enumerate(curr):
            if curr_xy[j] is None:
                continue
            if p.get("type") != c.get("type"):
                continue
            iou = iou_xyxy(prev_xy[i], curr_xy[j])  # type: ignore[arg-type]
            if iou >= iou_thresh:
                candidates.append((iou, i, j))
    candidates.sort(reverse=True)
    used_prev: set[int] = set()
    used_curr: set[int] = set()
    grown: list[tuple[dict, dict, float, float]] = []
    for iou, i, j in candidates:
        if i in used_prev or j in used_curr:
            continue
        used_prev.add(i)
        used_curr.add(j)
        ratio = box_area(curr_xy[j]) / max(box_area(prev_xy[i]), 1e-6)  # type: ignore[arg-type]
        if ratio >= area_ratio:
            grown.append((prev[i], curr[j], iou, ratio))
    return grown


def write_live_manifest(output: Path, pairs: list[dict], extra: dict | None = None) -> None:
    manifest = {
        "version": "1.0",
        "generatedAt": utc_now(),
        "source": "harvest_focus_pairs.py --live",
        "pairs": pairs,
        "skipped_unlabeled": 0,
    }
    if extra:
        manifest.update(extra)
    (output / "focus_dataset_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


def save_live_pair(
    pair_id: str,
    element_type: str,
    unfocused_image,
    unfocused_box: tuple[int, int, int, int],
    focused_image,
    focused_box: tuple[int, int, int, int],
    bbox_normalized: list[float],
    output: Path,
    scene: str,
) -> dict:
    crops_dir = output / "crops"
    crops_dir.mkdir(parents=True, exist_ok=True)
    seed = recipe_seed_for(pair_id)
    u_name = f"{pair_id}_unfocused.png"
    f_name = f"{pair_id}_focused.png"
    crop_rgb(unfocused_image, unfocused_box).save(crops_dir / u_name)
    crop_rgb(focused_image, focused_box).save(crops_dir / f_name)
    return {
        "pair_id": pair_id,
        "recipe_seed": seed,
        "fixture_scene": scene,
        "theme": "dark",
        "element_type": element_type,
        "unfocused_crop": f"crops/{u_name}",
        "focused_crop": f"crops/{f_name}",
        "bbox_normalized": bbox_normalized,
        "split": split_for_seed(seed),
    }


def yolo_focusable(model, image_path: Path, conf: float) -> list[dict]:
    results = model.predict(str(image_path), conf=conf, verbose=False)
    boxes = results[0].boxes
    names = model.names
    dets: list[dict] = []
    for b in boxes:
        cls_id = int(b.cls[0])
        name = names[cls_id]
        if name not in FOCUSABLE:
            continue
        xyxy = [round(x, 1) for x in b.xyxy[0].tolist()]
        dets.append({"type": name, "box": xyxy, "isFocused": None, "confidence": float(b.conf[0])})
    return dets


def capture_png(
    aatv: str,
    project: str | None,
    device_id: str,
    dest: Path,
    extra_env: dict[str, str] | None = None,
) -> bool:
    """
    Pull a settled frame via wait-stable --stdout (BP-45). Do not scrape
    TVTestRig container Sessions directories.
    """
    dest.parent.mkdir(parents=True, exist_ok=True)
    for sub in (["observe", "wait-stable", "--stdout"], ["observe", "latest", "--stdout"]):
        try:
            proc = run_aatv(
                aatv, project, sub, device_id, timeout_ms=20000, binary=True, extra_env=extra_env
            )
        except subprocess.TimeoutExpired:
            continue
        blob = proc.stdout if isinstance(proc.stdout, (bytes, bytearray)) else b""
        idx = blob.find(PNG_MAGIC)
        if idx >= 0:
            dest.write_bytes(blob[idx:])
            return True
        # Some builds wrap PNG after JSON; try stderr.
        err = proc.stderr if isinstance(proc.stderr, (bytes, bytearray)) else b""
        idx = err.find(PNG_MAGIC)
        if idx >= 0:
            dest.write_bytes(err[idx:])
            return True
    return False


def live_harvest(args: argparse.Namespace) -> int:
    """
    Plan A live path: closed-loop single-step (BP-40). Stay inside TVTestRigFixture.
    Label pairs geometrically: after one navigate, a same-type box that grew by
    --area-ratio is focused now and unfocused in the previous frame.
    Never sends Home or Select.
    """
    if not args.device_id:
        print("ERROR: --live requires --device-id")
        return 1
    aatv = resolve_aatv(args.aatv)
    project_arg = str(Path(args.project).expanduser())
    project, extra_env = resolve_ipc(project_arg)
    if project and not Path(project).is_dir():
        print(f"ERROR: TVTestRig --project not found: {project}")
        return 1
    print(f"ipc    : {'project ' + project if project else 'container HOME ' + extra_env.get('HOME', '')}")
    output = Path(args.output).expanduser()
    if not output.is_absolute():
        output = (PROJECT_ROOT / output).resolve()
    if refuse_hang_path(output):
        print("ERROR: refusing dest/train output path")
        return 1
    weights = Path(args.weights)
    if not weights.is_file():
        print(f"ERROR: YOLO weights not found: {weights}")
        return 1

    print(f"=== FocusRing live harvest {utc_now()} ===")
    print(f"device : {args.device_id}")
    print(f"project: {project or '(container application workspace)'}")
    print(f"aatv   : {aatv}")
    print(f"output : {output}")
    print(f"weights: {weights}")
    if args.dry_run:
        print("dry-run live: connect + one capture, no navigate, no writes")

    work_png = output / "_latest.png"

    def call_aatv(argv: list[str], timeout_ms: int = 15000, binary: bool = False) -> subprocess.CompletedProcess:
        return run_aatv(
            aatv, project, argv, args.device_id, timeout_ms=timeout_ms, binary=binary, extra_env=extra_env
        )

    def grab_png() -> bool:
        return capture_png(aatv, project, args.device_id, work_png, extra_env=extra_env)

    print("loading YOLO…", flush=True)
    from PIL import Image
    from ultralytics import settings as yolo_settings
    from ultralytics import YOLO

    # Keep Ultralytics off NativeUITrainer/yolo_dataset (dest/train glob hang).
    tmp_data = PROJECT_ROOT / "NativeUITrainer" / ".tmp" / "yolo_datasets"
    tmp_data.mkdir(parents=True, exist_ok=True)
    yolo_settings.update({"datasets_dir": str(tmp_data)})
    model = YOLO(str(weights))
    print("YOLO ready", flush=True)

    print("Phase B live harvest: connecting…", flush=True)
    try:
        connect = call_aatv(["device", "connect"], timeout_ms=12000)
    except subprocess.TimeoutExpired:
        print("ERROR: aatv device connect timed out")
        return 1
    if not aatv_ok(connect):
        print_aatv_failure(connect)
        print("ERROR: aatv device connect failed. Open TVTestRig, keep it running, attach Office, retry.")
        return 1
    print("connected", flush=True)

    if args.dry_run:
        ok = grab_png()
        print("capture:", "ok" if ok else "FAILED")
        if ok:
            dets = yolo_focusable(model, work_png, args.conf)
            print(f"focusable detections: {len(dets)}")
            types = Counter(d["type"] for d in dets)
            for name, n in types.most_common():
                print(f"  {name:20s} {n}")
            if looks_like_home(dets):
                print("NOTE: frame looks like tvOS Home. Launch TVTestRigFixture before the full run.")
        work_png.unlink(missing_ok=True)
        return 0 if ok else 1

    output.mkdir(parents=True, exist_ok=True)
    (output / "crops").mkdir(parents=True, exist_ok=True)
    pairs: list[dict] = []
    manifest_path = output / "focus_dataset_manifest.json"
    if manifest_path.is_file():
        try:
            prev = json.loads(manifest_path.read_text())
            pairs = [p for p in (prev.get("pairs") or []) if isinstance(p, dict)]
        except json.JSONDecodeError:
            pairs = []
        if pairs:
            print(f"resuming {len(pairs)} existing labeled pairs", flush=True)
    session = datetime.now(timezone.utc).strftime("%H%M%S")
    print("capturing frame 0…", flush=True)
    if not grab_png():
        print("ERROR: wait-stable/latest --stdout produced no PNG")
        return 1
    prev_image = Image.open(work_png).convert("RGB")
    prev_dets = yolo_focusable(model, work_png, args.conf)
    print(f"frame 0: {len(prev_dets)} focusable")
    if looks_like_home(prev_dets):
        print("Home-like frame. Launching TVTestRigFixture (no Home press)…")
        launch = call_aatv(["app", "launch", FIXTURE_BUNDLE_ID], timeout_ms=15000)
        if not aatv_ok(launch):
            print_aatv_failure(launch)
            print("ERROR: could not launch TVTestRigFixture. Open it on Office and retry.")
            return 1
        time.sleep(1.0)
        if not grab_png():
            print("ERROR: no PNG after fixture launch")
            return 1
        prev_image = Image.open(work_png).convert("RGB")
        prev_dets = yolo_focusable(model, work_png, args.conf)
        if looks_like_home(prev_dets):
            print("ERROR: still Home-like after fixture launch. Halt (BP-40/41).")
            return 1

    empty_streak = 0
    lost_streak = 0
    for step in range(1, args.max_steps + 1):
        if len(pairs) >= args.max_pairs:
            break
        direction = DIRECTION_CYCLE[(step - 1) % len(DIRECTION_CYCLE)]
        try:
            nav = call_aatv(["remote", "navigate", direction, "--count", "1"], timeout_ms=8000)
        except subprocess.TimeoutExpired:
            print(f"step {step}: navigate {direction} timed out")
            empty_streak += 1
            continue
        if not aatv_ok(nav):
            print(f"step {step}: navigate {direction} failed")
            print_aatv_failure(nav)
            empty_streak += 1
            if aatv_error_code(nav) == "connectionLost":
                lost_streak += 1
                if lost_streak == 1:
                    print("connectionLost — reconnecting once (no Home)", flush=True)
                    try:
                        call_aatv(["device", "connect"], timeout_ms=12000)
                    except subprocess.TimeoutExpired:
                        pass
                if lost_streak >= 8:
                    print("connectionLost ×8 — halt, keeping harvested pairs", flush=True)
                    write_live_manifest(output, pairs, {"halt": "connectionLost", "steps": step, "status": "partial"})
                    return 0 if pairs else 1
            continue
        lost_streak = 0
        if not grab_png():
            print(f"step {step}: no PNG")
            empty_streak += 1
            continue
        curr_image = Image.open(work_png).convert("RGB")
        curr_dets = yolo_focusable(model, work_png, args.conf)
        if looks_like_home(curr_dets):
            print(f"step {step}: Home-like screen detected. Halt. No Home press.")
            write_live_manifest(output, pairs, {"halt": "home_like", "steps": step})
            return 1
        w, h = curr_image.size
        grown = match_grown(prev_dets, curr_dets, args.iou, args.area_ratio)
        new_pairs = 0
        for prev_det, curr_det, iou, ratio in grown:
            curr_xy = box_to_xyxy(curr_det["box"])
            prev_xy = box_to_xyxy(prev_det["box"])
            if curr_xy is None or prev_xy is None:
                continue
            pair_id = f"live_{session}_{step:05d}_{new_pairs:02d}"
            nx1, ny1, nx2, ny2 = expanded_clamp(*curr_xy, w, h, args.expansion)
            px1, py1, px2, py2 = expanded_clamp(*prev_xy, prev_image.size[0], prev_image.size[1], args.expansion)
            x1, y1, x2, y2 = curr_xy
            entry = save_live_pair(
                pair_id=pair_id,
                element_type=str(curr_det.get("type")),
                unfocused_image=prev_image,
                unfocused_box=(px1, py1, px2, py2),
                focused_image=curr_image,
                focused_box=(nx1, ny1, nx2, ny2),
                bbox_normalized=[x1 / w, y1 / h, (x2 - x1) / w, (y2 - y1) / h],
                output=output,
                scene="TVTestRigFixture",
            )
            pairs.append(entry)
            new_pairs += 1
            if len(pairs) >= args.max_pairs:
                break
        if new_pairs:
            empty_streak = 0
        else:
            empty_streak += 1
        if step % 10 == 0 or new_pairs:
            print(
                f"step {step:4d} {direction:5s} dets={len(curr_dets):2d} "
                f"grown={new_pairs} pairs={len(pairs)}/{args.max_pairs}"
            )
        if step % 25 == 0:
            write_live_manifest(output, pairs, {"steps": step, "status": "in_progress"})
        if empty_streak == 8:
            print(f"step {step}: 8 empty steps — verified back once (no Home)")
            try:
                call_aatv(["remote", "press", "back"], timeout_ms=8000)
            except subprocess.TimeoutExpired:
                pass
            empty_streak = 0
        prev_image = curr_image
        prev_dets = curr_dets

    write_live_manifest(output, pairs, {"steps": min(args.max_steps, max(len(pairs), 1)), "status": "complete"})
    types = Counter(p["element_type"] for p in pairs)
    splits = Counter(p["split"] for p in pairs)
    print(f"wrote {len(pairs)} labeled pairs → {output / 'focus_dataset_manifest.json'}")
    print(f"splits: {dict(splits)}")
    print("types:")
    for name, n in types.most_common():
        print(f"  {name:20s} {n}")
    return 0 if pairs else 1


def main() -> int:
    args = parse_args()
    if (args.ttr_sidecar_v2 or args.visual_review or args.test_only) and not args.fixture_bundle:
        print("ERROR: v2 options require --fixture-bundle")
        return 1
    if args.fixture_bundle:
        if args.live or not args.corpus_id or not args.producer_reference:
            print("ERROR: --fixture-bundle requires --corpus-id and --producer-reference and cannot use --live")
            return 1
        output = Path(args.output).expanduser()
        if not output.is_absolute():
            output = (PROJECT_ROOT / output).resolve()
        try:
            output.relative_to(PROJECT_ROOT)
        except ValueError:
            print(f"ERROR: refusing to write outside package: {output}")
            return 1
        if output.exists() and not args.dry_run:
            print(f"ERROR: refusing to overwrite existing output: {output}")
            return 1
        try:
            if args.ttr_sidecar_v2:
                if args.pair_evidence or args.expansion != EXPANSION:
                    raise SimulatorManifestError("incompatible_v2_options")
                from ttr_focus_manifest import derive
                doc = derive(args.fixture_bundle, output, args.corpus_id, args.producer_reference,
                             review=json.loads(args.visual_review.read_text()) if args.visual_review else None,
                             test_only=args.test_only, dry_run=args.dry_run)
                result = {"pairs": len(doc["pairs"]), "version": "1.5", "dryRun": args.dry_run, "trainingApproval": False}
            else:
                if args.visual_review or args.test_only:
                    raise SimulatorManifestError("v2_mode_required")
                evidence = json.loads(args.pair_evidence.read_text()) if args.pair_evidence else None
                result = extract_fixture_bundle(args.fixture_bundle, output, args.corpus_id, args.producer_reference, args.expansion, args.dry_run, evidence)
        except (HarvestValidationError, SimulatorManifestError, OSError, ValueError) as error:
            print(f"ERROR: fixture bundle extraction failed: {error}")
            return 1
        print(json.dumps(result, sort_keys=True))
        return 0
    if args.live:
        if args.output == str(DEFAULT_OUTPUT):
            args.output = str(DEFAULT_LIVE_OUTPUT)
        return live_harvest(args)

    input_dir = Path(args.input).expanduser()
    if not input_dir.is_absolute():
        input_dir = (PROJECT_ROOT / input_dir).resolve()
    if not input_dir.is_dir():
        print(f"ERROR: input directory not found: {input_dir}")
        return 1

    print(f"=== FocusRing harvest {utc_now()} ===")
    print(f"input : {input_dir}")
    print(f"output: {args.output}  dry_run={args.dry_run}")
    records = extract_from_directory(input_dir, args.expansion)
    summarize(records)
    labeled = sum(1 for r in records if r["label"] is not None)
    if labeled == 0:
        print("NOTE: no isFocused labels on these captures (empty sidecar elements). Phase B --live is required for train pairs.")

    if args.dry_run:
        print("dry-run: no files written")
        return 0

    output = Path(args.output).expanduser()
    if not output.is_absolute():
        output = (PROJECT_ROOT / output).resolve()
    if refuse_hang_path(output):
        print("ERROR: refusing dest/train output path")
        return 1
    manifest = write_records(records, output, args.include_unlabeled)
    print(f"wrote {len(manifest['pairs'])} manifest entries → {output / 'focus_dataset_manifest.json'}")
    print(f"skipped unlabeled: {manifest['skipped_unlabeled']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
