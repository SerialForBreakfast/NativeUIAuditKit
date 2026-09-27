#!/usr/bin/env python3
"""Frozen Run013 evaluation: prepare -> infer -> report. No training or export.

Reuses the explicit-manifest exporter and the r6 baseline's custom AP algorithm.
All source data/checkpoints are read-only; output collisions are errors.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.metadata
import json
import os
import platform
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for key, relative in {
    "TMPDIR": "NativeUITrainer/.tmp", "YOLO_CONFIG_DIR": "NativeUITrainer/.ultralytics",
    "MPLCONFIGDIR": "NativeUITrainer/.mplconfig", "TORCH_HOME": "NativeUITrainer/.torch",
}.items():
    os.environ[key] = str(ROOT / relative)
    (ROOT / relative).mkdir(parents=True, exist_ok=True)
sys.dont_write_bytecode = True

from prediction_artifact import (INPUT_FORMAT_VERSION, PredictionArtifactError,
    canonical_sha256, ensure_new_output, load_request, make_result, sha256_file, _validate_label)
from export_coco import (ADDON_FAMILIES, DEFAULT_HOLDOUT_FAMILIES, DROP_TYPES,
    bounds_vision, element_type, target_split, vision_to_yolo)
from eval_phase6a import CATEGORY_MAP, PREDICTION_SETTINGS, export_predictions, load_names
from eval_ios_r6_baseline import compute_ap_at_iou, iou_xyxy
from reference_comparison import ComparisonError, compare

DEFAULT_OUT = ROOT / "reports/work/IOS-R013-EVAL"
DATASET = ROOT / "NativeUITrainer/yolo_dataset_41class_r7"
SOURCE = ROOT / "NativeUITrainer/reconstructed_corpora/ios-41class-r7-combined"
CHECKPOINT = ROOT / "NativeUITrainer/yolo_runs/phase6a_r013/weights/best.pt"
BASE_CHECKPOINT = ROOT / "NativeUITrainer/yolo_runs/phase6a_r009/weights/best.pt"
BASE_PREDICTIONS = ROOT / "reports/work/IOS-R6-BASELINE-20260923/prediction_artifact.json"
CODE = ["scripts/eval_run013.py", "scripts/eval_phase6a.py", "scripts/prediction_artifact.py",
        "scripts/eval_ios_r6_baseline.py", "scripts/reference_comparison.py", "scripts/export_coco.py"]


def save(path, value):
    path = ensure_new_output(Path(path), ROOT)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as handle:
        json.dump(value, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")


def read(path):
    return json.loads(Path(path).read_text())


def population(family):
    if family in DEFAULT_HOLDOUT_FAMILIES:
        return "withheld"
    if family in ADDON_FAMILIES:
        return "addon"
    raise ValueError(f"unexpected test family: {family}")


def expected_label(sidecar, names):
    lines = []
    for el in sidecar["elements"]:
        name = element_type(el)
        if el.get("excluded") is True or name in DROP_TYPES:
            continue
        if name not in names:
            raise ValueError(f"unexpected source category {name}")
        box = vision_to_yolo(bounds_vision(el) or {})
        if box is not None:
            lines.append(f"{names.index(name)} " + " ".join(f"{v:.6f}" for v in box))
    return "\n".join(lines) + ("\n" if lines else "")


def prepare(out, dataset=DATASET, source=SOURCE, expected_counts=None):
    """Decode and freeze source-backed membership, with no model imports."""
    out = ensure_new_output(out, ROOT)
    out.mkdir(parents=True)
    names = load_names()
    entries = read(source / "manifest.json")["entries"]
    manifest_hash = sha256_file(source / "manifest.json")
    inventory, errors = [], []
    from PIL import Image
    for index, entry in enumerate(entries, 1):
        try:
            raw_path = Path(entry["fileName"])
            if raw_path.is_absolute() or ".." in raw_path.parts:
                raise ValueError("unsafe source path")
            png = source / raw_path
            ann = png.with_suffix(".json")
            sidecar = read(ann)
            family = entry["templateFamily"]
            if sidecar["generatorProfile"]["templateFamily"] != family:
                raise ValueError("source family mismatch")
            split = target_split(entry["split"], family, set(DEFAULT_HOLDOUT_FAMILIES))
            image = dataset / split / "images" / png.name
            label = dataset / split / "labels" / (png.stem + ".txt")
            digest = sha256_file(image)
            if digest != entry["sha256"] or digest != sidecar["imageSHA256"] or digest != sha256_file(png):
                raise ValueError("image/source/manifest hash mismatch")
            with Image.open(image) as decoded:
                decoded.load()
                width, height = decoded.size
                pixels = hashlib.sha256(str(decoded.size).encode() + decoded.convert("RGBA").tobytes()).hexdigest()
            if (width, height) != (sidecar["image"]["pixelWidth"], sidecar["image"]["pixelHeight"]):
                raise ValueError("sidecar dimensions mismatch")
            text = label.read_text()
            _validate_label(label, str(raw_path), len(names))
            if text != expected_label(sidecar, names):
                raise ValueError("YOLO labels disagree with source sidecar/export conversion")
            classes = [int(line.split()[0]) for line in text.splitlines() if line.strip()]
            inventory.append({"imageID": f"{split}/images/{png.name}", "source": str(raw_path),
                "split": split, "family": family, "seed": entry.get("generatorSeed"),
                "width": width, "height": height, "classes": classes,
                "imageSHA256": digest, "labelSHA256": sha256_file(label),
                "sidecarSHA256": sha256_file(ann), "pixelSHA256": pixels})
        except (OSError, ValueError, KeyError) as exc:
            errors.append({"member": entry.get("fileName"), "error": str(exc)})
        if index % 500 == 0 or index == len(entries):
            print(f"Preflight {index}/{len(entries)}, errors={len(errors)}", flush=True)
    ids = [r["imageID"] for r in inventory]
    if len(set(ids)) != len(ids):
        errors.append({"error": "duplicate exported member IDs"})
    counts = dict(Counter(r["split"] for r in inventory))
    if expected_counts and counts != expected_counts:
        errors.append({"error": "split counts differ from frozen assignment", "actual": counts})
    if expected_counts:
        populations = Counter(population(r["family"]) for r in inventory if r["split"] == "test")
        if populations != {"withheld": 2000, "addon": 400}:
            errors.append({"error": "evaluation population counts differ", "actual": dict(populations)})
    if manifest_hash != sha256_file(source / "manifest.json"):
        errors.append({"error": "source manifest changed during audit"})
    groups = defaultdict(list)
    families = defaultdict(Counter)
    for row in inventory:
        groups[row["pixelSHA256"]].append(row["imageID"])
        families[row["family"]][row["split"]] += 1
    duplicates = [members for members in groups.values() if len(members) > 1]
    cross_split = [g for g in duplicates if len({m.split('/')[0] for m in g}) > 1]
    family_overlap = {f: dict(s) for f, s in families.items() if "test" in s and ("train" in s or "val" in s)}
    unexpected_overlap = set(family_overlap) - ADDON_FAMILIES
    if unexpected_overlap:
        errors.append({"error": "unexpected test-family overlap", "families": sorted(unexpected_overlap)})
    coverage = {s: {name: sum(r["classes"].count(i) for r in inventory if r["split"] == s)
                    for i, name in enumerate(names)} for s in counts}
    audit = {"formatVersion": "run013-preflight-v1", "source": str(source), "dataset": str(dataset),
        "sourceManifestSHA256": manifest_hash, "memberCount": len(inventory), "splitCounts": counts,
        "errors": errors, "integrityPassed": not errors, "classSupport": coverage,
        "familySplit": families, "testFamilyOverlap": family_overlap,
        "decodedDuplicateGroups": duplicates, "crossSplitPixelGroups": cross_split,
        "inventorySHA256": canonical_sha256(inventory), "members": inventory}
    save(out / "preflight.json", audit)
    if errors:
        raise ValueError(f"preflight rejected {len(errors)} integrity errors; see preflight.json")
    (out / "inputs").symlink_to(dataset.resolve(), target_is_directory=True)
    for pop in ("withheld", "addon", "combined"):
        rows = sorted((r for r in inventory if r["split"] == "test" and
                       (pop == "combined" or population(r["family"]) == pop)), key=lambda r: r["imageID"])
        payload = {"formatVersion": INPUT_FORMAT_VERSION, "corpusID": f"ios-r7-{pop}", "images": [
            {"imageID": r["imageID"], "imagePath": "inputs/" + r["imageID"],
             "labelPath": "inputs/test/labels/" + Path(r["imageID"]).stem + ".txt",
             "imageSHA256": r["imageSHA256"], "labelSHA256": r["labelSHA256"]} for r in rows]}
        save(out / f"{pop}_manifest.json", payload)
        load_request(out / f"{pop}_manifest.json", len(names))
    versions = {n: importlib.metadata.version(n) for n in ("torch", "torchvision", "ultralytics", "numpy", "Pillow")}
    freeze = {"checkpoint": str(CHECKPOINT), "checkpointSHA256": sha256_file(CHECKPOINT),
        "baselineCheckpoint": str(BASE_CHECKPOINT), "baselineCheckpointSHA256": sha256_file(BASE_CHECKPOINT),
        "categoryMapSHA256": sha256_file(CATEGORY_MAP), "settings": PREDICTION_SETTINGS,
        "python": sys.version, "executable": sys.executable, "platform": platform.platform(),
        "packages": versions, "sourceHashes": {p: sha256_file(ROOT / p) for p in CODE},
        "auditSHA256": sha256_file(out / "preflight.json"),
        "manifestHashes": {p: sha256_file(out / f"{p}_manifest.json") for p in ("withheld", "addon", "combined")}}
    save(out / "freeze.json", freeze)
    print("Preflight frozen", counts, "cross-split pixel groups", len(cross_split), flush=True)


def verify_freeze(out):
    freeze = read(out / "freeze.json")
    for key in ("checkpoint", "baselineCheckpoint"):
        if sha256_file(Path(freeze[key])) != freeze[key + "SHA256"]:
            raise ValueError(f"changed {key}")
    if sha256_file(CATEGORY_MAP) != freeze["categoryMapSHA256"]:
        raise ValueError("changed category map")
    if sha256_file(out / "preflight.json") != freeze["auditSHA256"]:
        raise ValueError("changed audit")
    for pop, digest in freeze["manifestHashes"].items():
        if sha256_file(out / f"{pop}_manifest.json") != digest:
            raise ValueError("changed frozen manifest")
    for path, digest in freeze["sourceHashes"].items():
        if sha256_file(ROOT / path) != digest:
            raise ValueError(f"changed evaluator source: {path}")
    for name, version in freeze["packages"].items():
        if importlib.metadata.version(name) != version:
            raise ValueError(f"changed dependency: {name}")
    return freeze


def validated_artifact(document, request, checkpoint_hash):
    """Validate retained bytes, settings, completeness and detection payloads."""
    compare(document, document)
    if document["model"]["checkpointSHA256"] != checkpoint_hash:
        raise ComparisonError("checkpoint mismatch")
    if document["categoryMap"]["sha256"] != sha256_file(CATEGORY_MAP):
        raise ComparisonError("category map mismatch")
    if document["settings"] != PREDICTION_SETTINGS or document["settingsSHA256"] != canonical_sha256(PREDICTION_SETTINGS):
        raise ComparisonError("settings mismatch")
    if document["corpus"]["contentSHA256"] != request.content_sha256:
        raise ComparisonError("corpus mismatch")
    by_id = {r["imageID"]: r for r in document["results"]}
    if set(by_id) != {r.image_id for r in request.images}:
        raise ComparisonError("membership mismatch")
    for image in request.images:
        row = by_id[image.image_id]
        normalized = make_result(image, len(load_names()), detections=row["detections"])
        if any(normalized[k] != row.get(k) for k in normalized):
            raise ComparisonError(f"result identity/status mismatch: {image.image_id}")
    for field in ("requestedCount", "resultCount"):
        if document["completeness"].get(field) != len(request.images):
            raise ComparisonError("count mismatch")
    return document


def subset(document, request):
    result = copy.deepcopy(document)
    ids = [r.image_id for r in request.images]
    indexed = {r["imageID"]: r for r in document["results"]}
    result["results"] = [indexed[i] for i in ids]
    result["corpus"] = {"corpusID": request.corpus_id, "contentSHA256": request.content_sha256,
                        "inputManifestSHA256": request.manifest_sha256}
    result["completeness"] = {"requestedCount": len(ids), "resultCount": len(ids), "requestedImageIDs": ids,
        "missingImageIDs": [], "duplicateImageIDs": [], "unexpectedImageIDs": [], "complete": True}
    return result


def infer(out):
    freeze = verify_freeze(out)
    import torch
    if not torch.backends.mps.is_available():
        raise ValueError("approved MPS backend unavailable; no CPU fallback")
    started = time.perf_counter()
    export_predictions(out / "combined_manifest.json", Path(freeze["checkpoint"]), out / "candidate_predictions.json", "mps")
    save(out / "inference_runtime.json", {"device": "mps", "mpsAvailable": True,
         "candidateElapsedSeconds": time.perf_counter() - started, "torch": torch.__version__})
    request = load_request(out / "withheld_manifest.json", len(load_names()))
    try:
        baseline = validated_artifact(read(BASE_PREDICTIONS), request, freeze["baselineCheckpointSHA256"])
        receipt = {"mode": "reused", "path": str(BASE_PREDICTIONS), "sha256": sha256_file(BASE_PREDICTIONS)}
    except (OSError, ValueError, KeyError) as exc:
        receipt = {"mode": "fresh", "reuseRejected": str(exc)}
        export_predictions(out / "withheld_manifest.json", Path(freeze["baselineCheckpoint"]), out / "baseline_fresh.json", "mps")
        baseline = validated_artifact(read(out / "baseline_fresh.json"), request, freeze["baselineCheckpointSHA256"])
    save(out / "baseline_predictions.json", baseline)
    save(out / "baseline_receipt.json", receipt)
    verify_freeze(out)


def score(document, request, names):
    gt = defaultdict(lambda: defaultdict(list))
    preds = defaultdict(list)
    by_image = {}
    for image in request.images:
        boxes = []
        for line in image.label_path.read_text().splitlines():
            if not line.strip():
                continue
            c, cx, cy, w, h = map(float, line.split())
            box = ((cx-w/2)*image.width, (cy-h/2)*image.height,
                   (cx+w/2)*image.width, (cy+h/2)*image.height)
            gt[int(c)][image.image_id].append(box)
            boxes.append((int(c), box))
        by_image[image.image_id] = boxes
    for row in document["results"]:
        for d in row["detections"]:
            preds[d["classID"]].append((row["imageID"], d["score"], tuple(d["xyxyPixels"])))
    for values in preds.values():
        values.sort(key=lambda v: -v[1])
    metrics, classes = {}, []
    for c, name in enumerate(names):
        support = sum(len(v) for v in gt[c].values())
        ap = [compute_ap_at_iou(gt, preds, c, round(.5+.05*i, 2)) for i in range(10)] if support else [None]*10
        matched = defaultdict(set)
        tp = fp = 0
        for image_id, confidence, box in preds[c]:
            if confidence < .25:
                continue
            choices = [(iou_xyxy(box, g), j) for j, g in enumerate(gt[c].get(image_id, [])) if j not in matched[image_id]]
            overlap, j = max(choices, default=(0, -1))
            if overlap >= .5:
                tp += 1
                matched[image_id].add(j)
            else:
                fp += 1
        values = {"ap50": ap[0], "ap70": ap[4], "ap90": ap[8],
                  "ap50_95": sum(ap)/10 if support else None}
        classes.append({"class": name, "support": support, "predictions": len(preds[c]), **values,
            "precision": tp/(tp+fp) if support and tp+fp else (0.0 if support else None),
            "recall": tp/support if support else None, "tp": tp, "fp": fp, "fn": support-tp,
            "status": "evaluated" if support else "unavailable"})
        metrics.update({f"{k}_{name}": v for k, v in values.items()})
    for metric in ("ap50", "ap70", "ap90", "ap50_95"):
        values = [r[metric] for r in classes if r[metric] is not None]
        metrics["m"+metric] = sum(values)/len(values) if values else None
    # Greedy class-agnostic association is a diagnostic confusion count, not AP matching.
    confusion = Counter()
    errors = []
    for row in document["results"]:
        available = set(range(len(by_image[row["imageID"]])))
        for d in sorted(row["detections"], key=lambda d: -d["score"]):
            if d["score"] < .25:
                continue
            choices = [(iou_xyxy(d["xyxyPixels"], by_image[row["imageID"]][j][1]), j) for j in available]
            overlap, j = max(choices, default=(0, -1))
            truth = names[by_image[row["imageID"]][j][0]] if overlap >= .5 else "background"
            predicted = names[d["classID"]]
            if overlap >= .5:
                available.remove(j)
            confusion[(truth, predicted)] += 1
            if truth != predicted:
                errors.append({"imageID": row["imageID"], "truth": truth, "predicted": predicted, "score": d["score"], "iou": overlap})
        for j in sorted(available):
            truth = names[by_image[row["imageID"]][j][0]]
            confusion[(truth, "background")] += 1
            errors.append({"imageID": row["imageID"], "truth": truth, "predicted": "background"})
    return {"imageCount": len(request.images), "supportedClasses": sum(r["support"] > 0 for r in classes),
        "metricImplementation": "custom all-point interpolated VOC AP; not official Ultralytics/COCO AP",
        "operatingPoint": {"confidence": .25, "iou": .5}, "metrics": metrics, "perClass": classes,
        "confusion": [{"truth": a, "predicted": b, "count": n} for (a,b), n in sorted(confusion.items())],
        "errorExamples": errors[:100], "errorCount": len(errors)}


def report(out):
    freeze = verify_freeze(out)
    names = load_names()
    requests = {p: load_request(out / f"{p}_manifest.json", len(names)) for p in ("combined", "withheld", "addon")}
    candidate = validated_artifact(read(out / "candidate_predictions.json"), requests["combined"], freeze["checkpointSHA256"])
    baseline = validated_artifact(read(out / "baseline_predictions.json"), requests["withheld"], freeze["baselineCheckpointSHA256"])
    from dataclasses import replace
    populations = {}
    audit = read(out / "preflight.json")
    families = {r["imageID"]: r["family"] for r in audit["members"]}
    for pop, request in requests.items():
        document = subset(candidate, request)
        populations[pop] = score(document, request, names)
        if pop == "withheld":
            candidate_withheld = document
        family_metrics = {}
        for family in sorted({families[i.image_id] for i in request.images}):
            images = tuple(i for i in request.images if families[i.image_id] == family)
            family_req = replace(request, images=images)
            family_metrics[family] = score(subset(document, family_req), family_req, names)
        populations[pop]["perFamily"] = family_metrics
    baseline_metrics = score(baseline, requests["withheld"], names)
    baseline_metrics["perFamily"] = {}
    for family in sorted({families[i.image_id] for i in requests["withheld"].images}):
        family_req = replace(requests["withheld"], images=tuple(
            i for i in requests["withheld"].images if families[i.image_id] == family))
        baseline_metrics["perFamily"][family] = score(subset(baseline, family_req), family_req, names)
    baseline["metrics"] = baseline_metrics["metrics"]
    candidate_withheld["metrics"] = populations["withheld"]["metrics"]
    comparison = compare(baseline, candidate_withheld)
    gaps = [r["class"] for r in populations["combined"]["perClass"] if not r["support"]]
    low = [r["class"] for r in populations["withheld"]["perClass"] if r["ap50"] is not None and r["ap50"] < .65]
    gate = {"DS_G8": "open", "passed": False, "requiredMAP50": .85, "requiredClassAP50Floor": .65,
        "supportedWithheldMAP50AboveThreshold": populations["withheld"]["metrics"]["map50"] >= .85,
        "withheldClassesBelowFloor": low, "missingCombinedClasses": gaps,
        "withheldMissingClasses": [r["class"] for r in populations["withheld"]["perClass"] if not r["support"]],
        "addonIsWithheldFamily": False, "untouchedFinalChallenge": False,
        "crossSplitPixelGroups": len(audit["crossSplitPixelGroups"]),
        "releaseChecksNotRun": ["CoreML parity/size", "physical-device latency", "real-world corpus", "blur robustness", "centroid bias"],
        "reason": "Incomplete independent class coverage; addon families overlap training; r6 is a reused diagnostic, not an untouched release challenge."}
    save(out / "candidate_withheld_scored.json", candidate_withheld)
    save(out / "baseline_withheld_scored.json", baseline)
    save(out / "evaluation.json", {"populations": populations, "baseline": baseline_metrics, "comparison": comparison, "gate": gate})
    print(json.dumps({"candidateWithheld": populations["withheld"]["metrics"]["map50"],
        "baselineWithheld": baseline_metrics["metrics"]["map50"], "delta": comparison["deltas"]["map50"],
        "addon": populations["addon"]["metrics"]["map50"], "gate": gate}, indent=2), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("prepare", "infer", "report"))
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    started = time.perf_counter()
    out = args.output.resolve()
    if not out.is_relative_to(ROOT):
        parser.error("output must stay inside project")
    try:
        if args.stage == "prepare":
            prepare(out, expected_counts={"train":14540, "val":2800, "test":2400})
        else:
            {"infer": infer, "report": report}[args.stage](out)
    except (OSError, ValueError, KeyError) as exc:
        print(f"{args.stage} failed: {exc}", file=sys.stderr)
        return 1
    print(f"{args.stage} complete in {time.perf_counter()-started:.1f}s", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
