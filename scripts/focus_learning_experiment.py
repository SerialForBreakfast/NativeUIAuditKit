"""Bounded native-screen experiment preparation/preflight; never operates a simulator."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

from focus_dataset_contract import ROOT, FocusDataError, digest, local, member, image, pixel_digest
from focus_runtime import invoke, identity
from native_os_focus_dataset import read_journey, pair_frames

CONFIG = {"epochs": 8, "batch": 8, "lr": .0003, "seed": 42, "maxSeconds": 600,
          "augmentation": "none", "model": "mobilenetv4_conv_small"}
SPLITS = {"settings/root": "train", "settings/general": "train", "settings/accessibility": "validation"}
INCREMENTAL_SPLITS = {**SPLITS, "settings/apps": "train"}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rel(path):
    return str(local(path).relative_to(ROOT))


def checked(record):
    path = member(ROOT, record["path"])
    if sha(path) != record["sha256"]:
        raise FocusDataError("changed_experiment_input")
    return path


def reviewed_native(record):
    """Reconstruct a reviewed native source without assigning its experiment split."""
    path, review = checked(record["manifest"]), checked(record["review"])
    doc = json.loads(path.read_text())
    content = dict(doc); expected = content.pop("manifestSHA256", None)
    if expected != digest(content) or expected not in review.read_text():
        raise FocusDataError("unreviewed_manifest")
    if (doc.get("version") != "native-os-focus-dataset-v1" or doc.get("completion") != "completed"
            or doc.get("sourceKind") != "tvos_simulator_os" or doc.get("partition") != "development"
            or doc.get("screenID", "settings/root") != record["screenID"]):
        raise FocusDataError("unsupported_native_source")
    source = local(ROOT/doc["sourceRoot"])
    for name, expected_hash in doc["sourceHashes"].items():
        if sha(member(source, name)) != expected_hash:
            raise FocusDataError("changed_source_bytes")
    frames, _ = read_journey(source, doc["target"], record["screenID"])
    pairs, _ = pair_frames(frames, doc["lineage"])
    if {p["pair_id"] for p in pairs} != {p["pair_id"] for p in doc["pairs"]}:
        raise FocusDataError("changed_native_membership")
    return doc, source, pairs


def sources_for(records, incremental=False):
    splits = INCREMENTAL_SPLITS if incremental else SPLITS
    if len(records) != len(splits) or {r["screenID"] for r in records} != set(splits):
        raise FocusDataError("three_frozen_screen_groups_required")
    result = []
    lineages = set()
    for record in records:
        if record["split"] != splits[record["screenID"]]:
            raise FocusDataError("changed_frozen_screen_split")
        path = checked(record["manifest"])
        review = checked(record["review"])
        doc = json.loads(path.read_text())
        content = dict(doc); expected = content.pop("manifestSHA256", None)
        if expected != digest(content) or expected not in review.read_text():
            raise FocusDataError("unreviewed_manifest")
        if (doc.get("version") != "native-os-focus-dataset-v1" or doc.get("completion") != "completed"
                or doc.get("sourceKind") != "tvos_simulator_os" or doc.get("partition") != "development"
                or doc.get("screenID", "settings/root") != record["screenID"]):
            raise FocusDataError("unsupported_native_source")
        source = local(ROOT/doc["sourceRoot"])
        for name, expected_hash in doc["sourceHashes"].items():
            if sha(member(source, name)) != expected_hash:
                raise FocusDataError("changed_source_bytes")
        frames, _ = read_journey(source, doc["target"], record["screenID"])
        pairs, _ = pair_frames(frames, doc["lineage"])
        if {p["pair_id"] for p in pairs} != {p["pair_id"] for p in doc["pairs"]}:
            raise FocusDataError("changed_native_membership")
        if doc["lineage"] in lineages:
            raise FocusDataError("shared_screen_lineage")
        lineages.add(doc["lineage"])
        # Use reconstructed frame geometry/labels, not mutable derived crop claims.
        result.append((record, source, pairs))
    return result


def prepare(records, output, warm, incremental=False):
    output, warm = local(output), local(warm)
    if output.exists():
        raise FocusDataError("output_collision")
    sources = sources_for(records, incremental)
    runtime = identity()
    warm_sha = sha(warm)
    output.mkdir(parents=True, exist_ok=False)
    samples = []
    for record, root, pairs in sources:
        for pair in pairs:
            for role, label in (("focused", 1), ("unfocused", 0)):
                frame = pair["frames"][role]
                sid = digest([record["screenID"], pair["pair_id"], role])
                item = {"id": sid, "path": str(member(root, frame["path"])), "sha256": frame["sha256"], "bounds": frame["bounds"]}
                crops = {}
                for variant in ("stretch", "aspect-fit"):
                    row = invoke([item], experimental_aspect_fit=variant == "aspect-fit")["results"][0]
                    raw = base64.b64decode(row["png"], validate=True)
                    name = sid + "-" + variant + ".png"
                    with (output/name).open("xb") as stream:
                        stream.write(raw)
                    crops[variant] = {"path": rel(output/name), "sha256": sha(output/name)}
                    image(ROOT, crops[variant], (256, 256))
                    crops[variant]["pixelSHA256"] = pixel_digest(ROOT, crops[variant])
                samples.append({"id": sid, "label": label, "screenID": record["screenID"],
                                "group": pair["lineage"], "split": record["split"], "crops": crops,
                                "sourcePixelSHA256": frame["pixelSHA256"], "pairID": pair["pair_id"]})
    if identity() != runtime or sha(warm) != warm_sha:
        raise FocusDataError("runtime_or_checkpoint_changed")
    result = {"version": "focus-learning-protocol-v2" if incremental else "focus-learning-protocol-v1", "scope": "development-only-same-app-screen-groups",
              "configuration": CONFIG, "sources": records, "runtime": runtime,
              "warmCheckpoint": {"path": rel(warm), "sha256": warm_sha}, "samples": samples,
              "releaseEligible": False}
    validate_document(result)
    result["protocolSHA256"] = digest(result)
    with (output/"protocol.json").open("x") as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
    return result


def validate_document(doc):
    if doc.get("version") not in {"focus-learning-protocol-v1", "focus-learning-protocol-v2"} or doc.get("configuration") != CONFIG or doc.get("releaseEligible") is not False:
        raise FocusDataError("unsupported_experiment_protocol")
    splits = INCREMENTAL_SPLITS if doc["version"] == "focus-learning-protocol-v2" else SPLITS
    if doc.get("scope") != "development-only-same-app-screen-groups":
        raise FocusDataError("invalid_experiment_scope")
    checked(doc["warmCheckpoint"])
    if doc["runtime"] != identity():
        raise FocusDataError("changed_crop_runtime")
    seen, groups, content = set(), {}, {}
    support = {s: {0: 0, 1: 0} for s in ("train", "validation")}
    for row in doc["samples"]:
        if row["id"] in seen or type(row["label"]) is not int or row["label"] not in (0, 1):
            raise FocusDataError("duplicate_or_invalid_sample")
        seen.add(row["id"])
        split = row["split"]
        if split != splits.get(row["screenID"]):
            raise FocusDataError("changed_frozen_screen_split")
        if row["group"] in groups and groups[row["group"]] != split:
            raise FocusDataError("group_leakage")
        groups[row["group"]] = split
        support[split][row["label"]] += 1
        hashes = [row["sourcePixelSHA256"]]
        if set(row["crops"]) != {"stretch", "aspect-fit"}:
            raise FocusDataError("missing_crop_variant")
        for crop in row["crops"].values():
            image(ROOT, crop, (256, 256))
            pixels = pixel_digest(ROOT, crop)
            if pixels != crop["pixelSHA256"]:
                raise FocusDataError("changed_crop_pixels")
            hashes.append(pixels)
        for value in hashes:
            if value in content and content[value] != split:
                raise FocusDataError("cross_split_pixel_leakage")
            content[value] = split
    if not seen or any(count < 2 for counts in support.values() for count in counts.values()):
        raise FocusDataError("insufficient_experimental_support")
    return support


def load_protocol(path, arm, run_name, approval_path=None):
    doc = json.loads(local(path).read_text())
    if doc.get("version")=="focus-development-experiment-v1":
        from focus_development_experiment import load_protocol as development_protocol
        return development_protocol(path,arm,run_name,approval_path)
    if approval_path is not None:
        raise FocusDataError("approval_requires_development_protocol")
    base = dict(doc); expected = base.pop("protocolSHA256", None)
    if expected != digest(base):
        raise FocusDataError("changed_protocol")
    support = validate_document(doc)
    sources = sources_for(doc["sources"], doc["version"] == "focus-learning-protocol-v2")
    expected_members = {(r["screenID"], p["pair_id"], label):
                        (p["lineage"], p["frames"][role]["pixelSHA256"])
                        for r, _, pairs in sources for p in pairs
                        for role, label in (("focused", 1), ("unfocused", 0))}
    actual_members = {(s["screenID"], s["pairID"], s["label"]):
                      (s["group"], s["sourcePixelSHA256"]) for s in doc["samples"]}
    if expected_members != actual_members or len(actual_members) != len(doc["samples"]):
        raise FocusDataError("changed_protocol_membership")
    if arm not in {"scratch-stretch", "warm-stretch", "scratch-aspect-fit", "warm-aspect-fit"}:
        raise FocusDataError("unknown_experiment_arm")
    import re
    if not isinstance(run_name, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", run_name):
        raise FocusDataError("explicit_safe_run_name_required")
    out = ROOT/"NativeUITrainer/focus_ring_runs"/run_name
    if out.exists():
        raise FocusDataError("output_collision")
    variant = "aspect-fit" if arm.endswith("aspect-fit") else "stretch"
    rows = [{"id": s["id"], "path": checked(s["crops"][variant]), "label": float(s["label"]),
             "split": s["split"]} for s in doc["samples"]]
    report = {"launchEligible": True, "releaseEligible": False, "configurationValid": True,
              "configuration": CONFIG, "protocolSHA256": expected, "arm": arm, "support": support,
              "warmCheckpoint": doc["warmCheckpoint"] if arm.startswith("warm-") else None,
              "output": str(out.relative_to(ROOT))}
    return report, rows


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--sources", type=Path, required=True)
    p.add_argument("--warm", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--incremental-native", action="store_true", help="Frozen Apps train extension; Home/Remotes remain excluded")
    a = p.parse_args()
    try:
        doc = prepare(json.loads(local(a.sources).read_text()), a.output, a.warm, a.incremental_native)
        print(json.dumps({"protocolSHA256": doc["protocolSHA256"], "samples": len(doc["samples"])}))
    except (ValueError, OSError, KeyError, TypeError) as error:
        p.exit(2, str(error)+"\n")


if __name__ == "__main__": main()
