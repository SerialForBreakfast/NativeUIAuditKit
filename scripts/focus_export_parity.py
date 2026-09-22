"""Compare isolated candidate CoreML against frozen reviewed Torch CPU challenge evidence."""
import argparse
import json
import math
import statistics
from pathlib import Path

from focus_dataset_contract import ROOT, FocusDataError, local, member, image, pixel_digest
from focus_learning_experiment import checked, reviewed_native, sha
from focus_learning_report import infer_bounded, assert_challenge_isolation, metrics
from focus_ring_baseline import artifact_digest, model_contract
from focus_runtime import identity

TOLERANCE = .01
THRESHOLDS = (.5, .70, .85)


def validate_model_identity(model, export):
    contract = model_contract(model)
    metadata = json.loads((model/"metadata.json").read_text())[0].get("userDefinedMetadata", {})
    expected = {"modelID": "focus-ring-experimental-"+export["experimentalID"],
        "checkpointSHA256": export["checkpointSHA256"], "releaseEligible": "false",
        "focusThreshold": "0.85", "ambiguityThreshold": "0.70"}
    if any(metadata.get(k) != v for k,v in expected.items()):
        raise FocusDataError("compiled_identity_mismatch")
    return contract


def compare(reference, observed):
    if not reference or [r["id"] for r in reference] != [r["id"] for r in observed]:
        raise FocusDataError("prediction_membership_mismatch")
    if len({r["id"] for r in reference}) != len(reference): raise FocusDataError("duplicate_prediction")
    differences = []
    for a, b in zip(reference, observed, strict=True):
        if a["label"] != b["label"]: raise FocusDataError("changed_labels")
        if any(not math.isfinite(r["probability"]) or not 0 <= r["probability"] <= 1 for r in (a, b)):
            raise FocusDataError("invalid_probability")
        differences.append({"id": a["id"], "label": a["label"], "torch": a["probability"],
            "coreml": b["probability"], "absoluteError": abs(a["probability"]-b["probability"]),
            "disagreedThresholds": [t for t in THRESHOLDS if (a["probability"] >= t) != (b["probability"] >= t)]})
    maximum = max(r["absoluteError"] for r in differences)
    return {"maxAbsoluteError": maximum, "meanAbsoluteError": statistics.mean(r["absoluteError"] for r in differences),
        "tolerance": TOLERANCE, "thresholds": THRESHOLDS,
        "ambiguityCounts": {name: sum(.70 <= r[key] < .85 for r in differences)
                            for name, key in (("torch", "torch"), ("coreml", "coreml"))},
        "referenceNearThresholdCount": sum(any(abs(r["torch"]-t) <= TOLERANCE for t in THRESHOLDS) for r in differences),
        "passed": maximum <= TOLERANCE and all(not r["disagreedThresholds"] for r in differences),
        "differences": differences}


def run(reference_path, reference_sha, model, export_report, protocol, output):
    output, model = local(output), local(model)
    if output.exists(): raise FocusDataError("output_collision")
    reference_path = checked({"path": str(local(reference_path).relative_to(ROOT)), "sha256": reference_sha})
    reference = json.loads(reference_path.read_text())
    if reference.get("version") != "native-focus-challenge-v1" or reference["candidate"]["backend"] != "torch-cpu":
        raise FocusDataError("unsupported_reference")
    checkpoint = checked({"path": reference["candidate"]["path"], "sha256": reference["candidate"]["sha256"]})
    report_path = local(export_report)
    report_hash = sha(report_path)
    export = json.loads(report_path.read_text())
    if export.get("releaseEligible") is not False or export["checkpointSHA256"] != sha(checkpoint):
        raise FocusDataError("export_checkpoint_mismatch")
    doc, source, pairs = reviewed_native(reference["source"])
    if reference["source"]["split"] != "challenge" or doc["runtime"] != identity() or reference["runtime"] != identity():
        raise FocusDataError("changed_runtime_or_partition")
    stored = {p["pair_id"]: p for p in doc["pairs"]}
    crop_root = local(ROOT/reference["source"]["manifest"]["path"]).parent
    rows, items = [], []
    for pair in pairs:
        for role, label in (("focused", 1), ("unfocused", 0)):
            frame = pair["frames"][role]; crop = stored[pair["pair_id"]]["frames"][role]
            record = {"path": crop["crop"], "sha256": crop["cropSHA256"]}
            image(crop_root, record, (256,256))
            rows.append({"id": pair["pair_id"]+":"+role, "label": label,
                         "pixelSHA256": pixel_digest(crop_root, record), "cropSHA256": record["sha256"]})
            items.append({"id": rows[-1]["id"], "path": str(member(source, frame["path"])),
                          "sha256": frame["sha256"], "bounds": frame["bounds"]})
    previous = reference["candidate"]["predictions"]
    if [{k:r[k] for k in rows[0]} for r in previous] != rows:
        raise FocusDataError("changed_reference_membership")
    protocol_doc = json.loads(local(protocol).read_text())
    assert_challenge_isolation(rows, pairs, doc["lineage"], protocol_doc)
    contract = validate_model_identity(model, export)
    before = contract["sha256"]
    # The compile step is explicit; this entrypoint never compiles or substitutes models.
    reply = infer_bounded(items, model)
    observed = [{**row, "probability": result["probability"]} for row, result in zip(rows, reply["results"], strict=True)]
    if [r["id"] for r in reply["results"]] != [r["id"] for r in rows]:
        raise FocusDataError("prediction_membership_mismatch")
    comparison = compare(previous, observed)
    reviewed_native(reference["source"])
    if before != artifact_digest(model) or sha(reference_path) != reference_sha or sha(report_path) != report_hash or sha(checkpoint) != export["checkpointSHA256"] or identity() != doc["runtime"]:
        raise FocusDataError("changed_input_during_evaluation")
    result = {"version": "focus-export-parity-v1", "releaseEligible": False,
        "referenceSHA256": reference_sha, "checkpointSHA256": sha(checkpoint),
        "model": str(model.relative_to(ROOT)), "compiledSHA256": before,
        "exportReportSHA256": report_hash, "protocolSHA256": protocol_doc["protocolSHA256"],
        "modelContract": contract,
        "runtime": identity(), "comparison": comparison, "coremlMetrics": metrics(observed),
        "torchMetrics": metrics(previous), "coremlTiming": reply["batches"],
        "coremlSamples": reply["results"], "torchTiming": reference["candidate"]["inferenceSeconds"],
        "limitations": ["12 correlated same-app development crops; saturated scores do not establish near-threshold parity", "CPU only; not ANE or device latency",
            "Native boxes supplied, no model-driven navigation", "No full corpus/model gate or promotion"]}
    with output.open("x") as stream: json.dump(result, stream, indent=2, allow_nan=False)
    print(json.dumps({k:v for k,v in comparison.items() if k != "differences"}))
    return 0 if comparison["passed"] else 1


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("reference", "model", "export-report", "protocol", "output"):
        p.add_argument("--"+name, type=Path, required=True)
    p.add_argument("--reference-sha256", required=True)
    a = p.parse_args()
    try: code = run(a.reference, a.reference_sha256, a.model, a.export_report, a.protocol, a.output)
    except (ValueError, OSError, KeyError, TypeError) as error: p.exit(2, str(error)+"\n")
    p.exit(code)
