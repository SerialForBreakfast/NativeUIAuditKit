#!/usr/bin/env python3
"""Fail-closed reporting for the shipped FocusRing baseline.

Offline tests may use generated test-only images and the shipped CoreML artifact.
Genuine development inference requires its separately authorized qualified pilot.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any
from focus_dataset_contract import FocusDataError, PREPROCESSING, digest, validate_manifest

ROOT = Path(__file__).resolve().parents[1]
# This is deliberately a shipped-model comparison point, not the operating threshold for
# an untrained candidate. FR-SIM-CAND completes its fixed 30-epoch run, then selects and
# locks its own threshold from validation membership before it reads the final holdout.
SHIPPED_COMPARISON_THRESHOLD = 0.85


class BaselineError(ValueError):
    pass


def artifact_digest(model: Path) -> str:
    if model.is_symlink() or not model.is_dir():
        raise BaselineError("missing_compiled_model")
    h = hashlib.sha256()
    files = sorted(path for path in model.rglob("*") if path.is_file())
    if not files:
        raise BaselineError("empty_compiled_model")
    for path in files:
        if path.is_symlink() or not path.resolve().is_relative_to(model.resolve()):
            raise BaselineError("unsafe_model_member")
        h.update(str(path.relative_to(model)).encode() + b"\0")
        h.update(path.read_bytes())
    return h.hexdigest()


def model_contract(model: Path) -> dict[str, Any]:
    metadata = model / "metadata.json"
    if not metadata.is_file():
        raise BaselineError("missing_model_metadata")
    try:
        data = json.loads(metadata.read_text())
    except json.JSONDecodeError as error:
        raise BaselineError("invalid_model_metadata") from error
    # Compiled CoreML metadata is an array of model records, unlike the export-time
    # package metadata object. A baseline must reject ambiguous compiled metadata.
    if not isinstance(data, list) or len(data) != 1 or not isinstance(data[0], dict):
        raise BaselineError("invalid_model_metadata")
    names = {item.get("name") for item in data[0].get("outputSchema", []) if isinstance(item, dict)}
    if "is_focused_prob" not in names:
        raise BaselineError("unexpected_model_output")
    return {"sha256": artifact_digest(model), "metadataSHA256": hashlib.sha256(metadata.read_bytes()).hexdigest(), "outputs": sorted(name for name in names if isinstance(name, str))}


def rows(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    result = []
    seen = set()
    for pair in manifest.get("pairs", []):
        if not isinstance(pair, dict):
            raise BaselineError("invalid_membership")
        pair_id = pair.get("pair_id") or pair.get("pairID")
        family = pair.get("fixture_scene") or pair.get("family")
        theme, control = pair.get("theme"), pair.get("element_type")
        if not all(isinstance(value, str) and value for value in (pair_id, family, theme, control)):
            raise BaselineError("invalid_membership")
        if pair_id in seen or not pair.get("focused_crop") or not pair.get("unfocused_crop"):
            raise BaselineError("invalid_membership")
        seen.add(pair_id)
        for label, key in ((1, "focused_crop"), (0, "unfocused_crop")):
            if pair.get(key):
                result.append({"id": f"{pair_id}:{label}", "label": label, "family": family, "theme": theme, "control": control, "hard": bool(pair.get("hardNegative")) and label == 0})
    if not result:
        raise BaselineError("empty_membership")
    return result


def evaluate(samples: list[dict[str, Any]], scores: dict[str, Any], *, require_hard: bool = True) -> dict[str, Any]:
    if not samples or len({s["id"] for s in samples}) != len(samples):
        raise BaselineError("empty_or_duplicate_membership")
    if set(scores) != {s["id"] for s in samples}:
        raise BaselineError("missing_or_invalid_inference")
    groups: dict[str, Counter[str]] = {}
    required = {"overall"}
    for sample in samples:
        value = scores.get(sample["id"])
        if type(value) not in (int, float) or not 0 <= value <= 1:
            raise BaselineError("missing_or_invalid_inference")
        keys = ("overall", f"family:{sample['family']}", f"theme:{sample['theme']}", f"control:{sample['control']}")
        for key in keys:
            required.add(key); groups.setdefault(key, Counter())
            predicted = int(value >= SHIPPED_COMPARISON_THRESHOLD)
            actual = sample["label"]
            groups[key]["n"] += 1
            groups[key]["tp" if predicted and actual else "fp" if predicted else "tn" if not actual else "fn"] += 1
            abstained = .70 <= value < .85
            groups[key]["abstained"] += int(abstained)
            groups[key]["decided"] += int(not abstained)
            groups[key]["correctDecisions"] += int(not abstained and predicted == actual)
    hard = [sample for sample in samples if sample["hard"]]
    if not hard and require_hard:
        raise BaselineError("empty_hard_negative_support")
    hard_fp = sum(scores[sample["id"]] >= SHIPPED_COMPARISON_THRESHOLD for sample in hard)
    report = {}
    for key in sorted(required):
        c = groups.get(key, Counter())
        if not c["n"]:
            raise BaselineError("empty_group_support")
        report[key] = dict(c)
        report[key]["accuracy"] = (c["tp"] + c["tn"]) / c["n"]
        report[key]["decisionCoverage"] = c["decided"] / c["n"]
        report[key]["selectiveAccuracy"] = c["correctDecisions"] / c["decided"] if c["decided"] else None
        report[key]["precision"] = c["tp"] / max(1, c["tp"] + c["fp"])
        report[key]["recall"] = c["tp"] / max(1, c["tp"] + c["fn"])
        report[key]["fpr"] = c["fp"] / (c["fp"] + c["tn"]) if c["fp"] + c["tn"] else None
        report[key]["fnr"] = c["fn"] / (c["fn"] + c["tp"]) if c["fn"] + c["tp"] else None
    return {
        "threshold": {
            "value": SHIPPED_COMPARISON_THRESHOLD,
            "purpose": "shipped_baseline_comparison",
            "candidatePolicy": "complete_30_epochs_then_select_on_validation_and_lock_before_test",
        },
        "groups": report,
        "hardNegative": {"n": len(hard), "fp": hard_fp, "fpr": hard_fp / len(hard) if hard else None,
                         "status": "available" if hard else "unavailable", "gatePassed": "not_assessed"},
        "errors": [{"id": s["id"], "kind": "false_positive" if s["label"] == 0 else "false_negative",
                    "theme": s["theme"], "control": s["control"], "family": s["family"]}
                   for s in samples if int(scores[s["id"]] >= SHIPPED_COMPARISON_THRESHOLD) != s["label"]],
    }


def prepare_protocol(manifest, dataset, model):
    validated = validate_manifest(manifest, dataset)
    # The development baseline cannot inspect final held-out examples by accident.
    if any(r["split"] != "development" for r in validated):
        raise BaselineError("development_only_baseline")
    samples = rows(manifest)
    hard_ids = {r["pairID"] for r in validated if r["theme"] in {"light", "highContrast"} and r["class"] in {"imageView", "collectionItem"}}
    for sample in samples:
        sample["hard"] = sample["label"] == 0 and sample["id"].rsplit(":", 1)[0] in hard_ids
    value = {"formatVersion": "focus-baseline-protocol-v1", "artifact": model_contract(model),
             "manifestSHA256": digest(manifest), "preprocessing": manifest["preprocessing"],
             "evidenceKind": manifest["evidenceKind"], "partition": "development",
             "sourceKind": manifest["sourceKind"],
             "threshold": SHIPPED_COMPARISON_THRESHOLD, "samples": samples,
             "modelGatePassed": "not_assessed"}
    value["implementationSHA256"] = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in
        ("scripts/focus_ring_baseline.py", "scripts/focus_dataset_contract.py", "Sources/NativeUIAuditKit/Detection/FocusRingClassifier.swift")}
    value["cropParity"] = {"geometry": "fractional-origin-rounded-intermediate-canvas", "pixelInterpolation": "not-CoreGraphics-qualified"}
    if manifest["version"] in {"1.3", "1.4", "1.5"}:
        value["cropParity"] = {"backend": "production-makeCrop", "runtime": manifest["runtimeCrop"]}
    value["implementationSHA256"]["scripts/focus_runtime.py"] = hashlib.sha256((ROOT / "scripts/focus_runtime.py").read_bytes()).hexdigest()
    return {**value, "protocolSHA256": digest(value)}


def score_protocol(protocol, scores):
    if not isinstance(protocol, dict) or protocol.get("formatVersion") != "focus-baseline-protocol-v1":
        raise BaselineError("unsupported_protocol")
    identity = {k: v for k, v in protocol.items() if k != "protocolSHA256"}
    if digest(identity) != protocol.get("protocolSHA256"):
        raise BaselineError("changed_protocol")
    if not isinstance(scores, dict) or scores.get("formatVersion") != "focus-baseline-scores-v1" or scores.get("protocolSHA256") != protocol["protocolSHA256"] or scores.get("artifactSHA256") != protocol["artifact"]["sha256"]:
        raise BaselineError("incompatible_scores")
    if scores.get("inferenceKind") not in {"test-only", "coreml"}:
        raise BaselineError("missing_inference_kind")
    if not isinstance(scores.get("scores"), dict):
        raise BaselineError("invalid_scores")
    result = {"protocolSHA256": protocol["protocolSHA256"], "artifact": protocol["artifact"],
            "evaluation": evaluate(protocol["samples"], scores["scores"], require_hard=False),
            "inference": scores["inferenceKind"], "modelGatePassed": "not_assessed",
            "evidenceKind": protocol["evidenceKind"]}
    result["sourceKind"] = protocol["sourceKind"]
    result["executionEvidence"] = "supplied-score-envelope; not independently executed by scorer"
    result["evaluationScope"] = "oracle-frame-box-crops; no detector-proposal evaluation"
    result["proposedBoxEvaluation"] = {"status": "unavailable", "reason": "independent_proposals_not_supplied"}
    values = scores["scores"]
    result["decisions"] = {"focused": sum(v >= .85 for v in values.values()),
                           "unfocused": sum(v < .70 for v in values.values()),
                           "abstained": sum(.70 <= v < .85 for v in values.values()),
                           "policy": "fixed shipped ambiguity band [0.70,0.85); binary metrics separately at0.85"}
    if "timingBatches" in scores:
        result["timingBatches"] = scores["timingBatches"]
        result["timingScope"] = scores["timingScope"]
        timings = [s["inferenceMilliseconds"] for b in scores["timingBatches"] for s in b["samples"][1:]]
        import math
        timings.sort()
        result["warmLatencyMs"] = {"n": len(timings), **{key: timings[max(0, math.ceil(p*len(timings))-1)] if timings else None for key,p in (("p50",.5),("p95",.95))}}
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--prepare", action="store_true", help="Freeze development protocol; does not infer")
    parser.add_argument("--infer", action="store_true", help="Explicit CoreML development inference; requires runtime crops and frozen protocol")
    parser.add_argument("--protocol", type=Path)
    parser.add_argument("--scores", type=Path, help="Hash-bound score envelope; no inferred or missing results")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    try: output.relative_to(ROOT)
    except ValueError:
        print("ERROR: output must stay inside package", file=sys.stderr); return 2
    if output.exists():
        print("ERROR: refusing output collision", file=sys.stderr); return 2
    try:
        manifest = json.loads(args.manifest.read_text())
        current = prepare_protocol(manifest, args.manifest.parent, args.model)
        if args.prepare:
            if args.scores or args.protocol or args.infer: raise BaselineError("conflicting_modes")
            result = current
        else:
            if not args.protocol or (not args.scores and not args.infer): raise BaselineError("protocol_and_scores_required")
            protocol = json.loads(args.protocol.read_text())
            if current != protocol: raise BaselineError("changed_protocol_or_membership")
            if args.infer:
                if args.scores or manifest["version"] not in {"1.3", "1.4", "1.5"}: raise BaselineError("runtime_crops_required_no_external_scores")
                from focus_runtime import infer
                result = score_protocol(protocol, infer(manifest, args.model, protocol))
                result["executionEvidence"] = "production-runtime-invoked-by-this-command"
            else:
                result = score_protocol(protocol, json.loads(args.scores.read_text()))
    except (OSError, ValueError, BaselineError, FocusDataError) as error:
        print(f"ERROR: {error}", file=sys.stderr); return 2
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x") as stream:
        stream.write(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"artifactSHA256": result["artifact"]["sha256"], "protocolSHA256": result["protocolSHA256"]}))
    return 0


if __name__ == "__main__": raise SystemExit(main())
