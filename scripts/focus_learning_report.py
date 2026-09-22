"""Report the frozen four-arm development experiment; no training or promotion."""
import argparse
import json
import math
from pathlib import Path

from focus_dataset_contract import ROOT, FocusDataError, digest, local, member
from focus_learning_experiment import sha, sources_for, validate_document, reviewed_native
from focus_ring_baseline import artifact_digest
from focus_runtime import invoke, identity


def metrics(rows):
    if not rows or len({r["id"] for r in rows}) != len(rows):
        raise FocusDataError("invalid_prediction_membership")
    if any(r["label"] not in (0, 1) or not math.isfinite(r["probability"])
           or not 0 <= r["probability"] <= 1 for r in rows):
        raise FocusDataError("invalid_prediction")
    positive = [r["probability"] for r in rows if r["label"] == 1]
    negative = [r["probability"] for r in rows if r["label"] == 0]
    if not positive or not negative: raise FocusDataError("missing_label_support")
    result = {"count": len(rows), "auroc": sum((a>b)+.5*(a==b) for a in positive for b in negative)/(len(positive)*len(negative))}
    for threshold in (.5, .85):
        tp = sum(p >= threshold for p in positive); fp = sum(p >= threshold for p in negative)
        result[str(threshold)] = {"tp": tp, "fn": len(positive)-tp, "fp": fp,
                                  "tn": len(negative)-fp, "accuracy": (tp+len(negative)-fp)/len(rows)}
    return result


def infer_bounded(items, model):
    """Respect the production helper's decoded-pixel and item limits."""
    from PIL import Image
    batches, batch, pixels = [], [], 0
    for item in items:
        with Image.open(item["path"]) as source_image: area = source_image.width*source_image.height
        if area > 80_000_000: raise FocusDataError("runtime_pixel_limit")
        if batch and (pixels+area > 80_000_000 or len(batch) == 128):
            batches.append(invoke(batch, model)); batch, pixels = [], 0
        batch.append(item); pixels += area
    if batch: batches.append(invoke(batch, model))
    return {"results": [r for b in batches for r in b["results"]],
            "batches": [{k:v for k,v in b.items() if k != "results"} for b in batches]}


def assert_challenge_isolation(rows, pairs, lineage, protocol):
    content = dict(protocol)
    expected = content.pop("protocolSHA256", None)
    if digest(content) != expected: raise FocusDataError("changed_protocol")
    known = {s["sourcePixelSHA256"] for s in protocol["samples"]}
    known.update(c["pixelSHA256"] for s in protocol["samples"] for c in s["crops"].values())
    if any(r["pixelSHA256"] in known for r in rows) or any(
            f["pixelSHA256"] in known for p in pairs for f in p["frames"].values()):
        raise FocusDataError("challenge_pixel_leakage")
    if lineage in {s["group"] for s in protocol["samples"]}:
        raise FocusDataError("challenge_lineage_leakage")


def native_challenge(source_record, checkpoint, output, training_protocol=None):
    """Evaluate frozen reviewed native challenge data; never select or train weights."""
    import os
    import time
    from focus_dataset_contract import image, pixel_digest
    output, checkpoint = local(output), local(checkpoint)
    if output.exists(): raise FocusDataError("output_collision")
    record = json.loads(local(source_record).read_text())
    if record.get("split") != "challenge": raise FocusDataError("challenge_partition_required")
    doc, source, pairs = reviewed_native(record)
    if doc["runtime"] != identity(): raise FocusDataError("changed_crop_runtime")
    crop_root = local(ROOT/record["manifest"]["path"]).parent
    manifest_pairs = {p["pair_id"]: p for p in doc["pairs"]}
    rows, items = [], []
    for pair in pairs:
        for role, label in (("focused", 1), ("unfocused", 0)):
            frame = pair["frames"][role]
            stored = manifest_pairs[pair["pair_id"]]["frames"][role]
            crop = {"path": stored["crop"], "sha256": stored["cropSHA256"]}
            image(crop_root, crop, (256, 256))
            sid = pair["pair_id"]+":"+role
            rows.append({"id": sid, "label": label, "elementID": pair["elementID"],
                         "crop": str(member(crop_root, crop["path"])),
                         "cropSHA256": crop["sha256"], "pixelSHA256": pixel_digest(crop_root, crop)})
            items.append({"id": sid, "path": str(member(source, frame["path"])),
                          "sha256": frame["sha256"], "bounds": frame["bounds"]})
    # Challenge content may not overlap any previously used experimental input.
    old = json.loads((ROOT/"reports/work/FOCUS-EXP-01/corpus-01/protocol.json").read_text())
    protocols = [old]
    if training_protocol:
        protocols.append(json.loads(local(training_protocol).read_text()))
    for protocol in protocols:
        assert_challenge_isolation(rows, pairs, doc["lineage"], protocol)
    model = ROOT/"NativeUIAuditKitModels/Sources/NativeUIAuditKitModels/Resources/FocusRingDetector.mlmodelc"
    model_hash, checkpoint_hash = artifact_digest(model), sha(checkpoint)
    reply = infer_bounded(items, model)
    if [r["id"] for r in reply["results"]] != [r["id"] for r in rows]:
        raise FocusDataError("prediction_membership_mismatch")
    coreml = [{**r, "probability": prediction["probability"]} for r, prediction in zip(rows, reply["results"], strict=True)]
    os.environ["TORCH_HOME"] = str(ROOT/"NativeUITrainer/.torch")
    import torch
    import numpy as np
    from PIL import Image
    from focus_ring_backbone import mobilenetv4_conv_small
    started = time.monotonic()
    classifier = mobilenetv4_conv_small(pretrained=False, num_classes=1)
    classifier.load_state_dict(torch.load(checkpoint, map_location="cpu", weights_only=True)["state_dict"], strict=True)
    classifier.eval()
    loaded = time.monotonic()-started
    predictions, times = [], []
    with torch.inference_mode():
        for row in rows:
            with Image.open(row["crop"]) as img:
                tensor = torch.from_numpy(np.array(img.convert("RGB"), copy=True)).permute(2, 0, 1).float().div(255).unsqueeze(0)
            start = time.monotonic()
            probability = float(torch.sigmoid(classifier(tensor)).item())
            times.append(time.monotonic()-start)
            predictions.append({**row, "probability": probability})
    if sha(checkpoint) != checkpoint_hash or artifact_digest(model) != model_hash or identity() != doc["runtime"]:
        raise FocusDataError("changed_runtime_or_model")
    reviewed_native(record)
    result = {"version": "native-focus-challenge-v1", "releaseEligible": False,
              "source": record, "lineage": doc["lineage"], "runtime": doc["runtime"],
              "isolationProtocols": [p["protocolSHA256"] for p in protocols],
              "shipped": {"sha256": model_hash, "metrics": metrics(coreml), "predictions": coreml,
                          "timing": reply["batches"]},
              "candidate": {"sha256": checkpoint_hash, "path": str(checkpoint.relative_to(ROOT)),
                            "backend": "torch-cpu", "metrics": metrics(predictions), "predictions": predictions,
                            "loadSeconds": loaded, "inferenceSeconds": times},
              "limitations": ["Reviewed native boxes, not detector proposals", "One layout/runtime challenge, not release qualification",
                              "Separate CoreML CPU and PyTorch CPU backends; no export-parity claim"]}
    with output.open("x") as stream: json.dump(result, stream, indent=2, allow_nan=False)
    print(json.dumps({"shipped": result["shipped"]["metrics"], "candidate": result["candidate"]["metrics"]}))


def report(protocol_path, output, baseline_only=False):
    output = local(output)
    if output.exists(): raise FocusDataError("output_collision")
    doc = json.loads(local(protocol_path).read_text())
    base = dict(doc); protocol_sha = base.pop("protocolSHA256", None)
    if digest(base) != protocol_sha: raise FocusDataError("changed_protocol")
    validate_document(doc)
    sources = sources_for(doc["sources"])
    samples = [s for s in doc["samples"] if s["split"] == "validation"]
    expected = {s["id"]: s["label"] for s in samples}
    def verify(rows):
        if {r["id"]: r["label"] for r in rows} != expected: raise FocusDataError("prediction_membership_mismatch")
        return metrics(rows)
    results, warm_rows = {}, []
    run_names = () if baseline_only else ("fdr006-warm-stretch", "fdr003-scratch-stretch", "fdr004-warm-aspect-fit", "fdr005-scratch-aspect-fit")
    for name in run_names:
        path = ROOT/"NativeUITrainer/focus_ring_runs"/name/"experiment-result.json"
        run = json.loads(path.read_text())
        if run["status"] != "completed" or run["releaseEligible"] or run["protocolSHA256"] != protocol_sha:
            raise FocusDataError("incompatible_run")
        if sha(path.parent/"weights/best.pt") != run["bestSHA256"]: raise FocusDataError("changed_candidate")
        selected_epoch = min(run["history"], key=lambda h: (h["validation"]["loss"], -h["epoch"]))["epoch"]
        results[run["arm"]] = {"run": name, "resultSHA256": sha(path), "bestSHA256": run["bestSHA256"],
            "elapsedSeconds": run["elapsedSeconds"], "pid": run["pid"], "device": run["device"],
            "selectedEpoch": selected_epoch, "initial": verify(run["initial"]["predictions"]),
            "selected": verify(run["selected"]["predictions"]), "initialLoss": run["initial"]["loss"],
            "selectedLoss": run["selected"]["loss"]}
        if run["arm"] == "warm-stretch": warm_rows = run["initial"]["predictions"]
    model = ROOT/"NativeUIAuditKitModels/Sources/NativeUIAuditKitModels/Resources/FocusRingDetector.mlmodelc"
    model_hash = artifact_digest(model)
    lookup = {(s["pairID"], s["label"]): s["id"] for s in samples}
    items = []
    for record, root, pairs in sources:
        if record["split"] != "validation": continue
        for pair in pairs:
            for role, label in (("focused", 1), ("unfocused", 0)):
                frame = pair["frames"][role]
                items.append({"id": lookup[pair["pair_id"], label], "path": str(member(root, frame["path"])),
                              "sha256": frame["sha256"], "bounds": frame["bounds"]})
    # The runtime caps decoded pixels, not just item count. These source frames
    # are 4K; keep each call under its existing 80M-pixel bound without weakening it.
    reply = infer_bounded(items, model)
    rows = [{"id": r["id"], "label": expected[r["id"]], "probability": r["probability"]} for r in reply["results"]]
    warm = {r["id"]: r["probability"] for r in warm_rows}
    differences = [abs(r["probability"]-warm[r["id"]]) for r in rows] if warm else []
    if model_hash != artifact_digest(model) or identity() != doc["runtime"]: raise FocusDataError("changed_runtime_or_model")
    result = {"version": "focus-learning-report-v1", "scope": doc["scope"], "releaseEligible": False,
        "protocolSHA256": protocol_sha, "arms": results,
        "shippedCoreML": {"artifactSHA256": model_hash, "metrics": verify(rows), "predictions": rows,
            "timing": {k:v for k,v in reply.items() if k != "results"},
            "samples": [{k:v for k,v in r.items() if k != "png"} for r in reply["results"]]},
        "initialTorchCoreMLDifference": {"meanAbsolute": sum(differences)/len(differences), "maxAbsolute": max(differences)} if differences else None,
        "limitations": ["Same-app, same-style screen groups; only 9 validation pairs.",
            "Validation selects checkpoints; not a final-test result.", "One seed and fixed 8-epoch budget, not convergence or statistical superiority.",
            "Native boxes supplied; no detector proposal or model-driven navigation qualification.",
            "No physical-device, fixture replay, catastrophic-forgetting or release-gate evidence."]}
    with output.open("x") as stream: json.dump(result, stream, indent=2, allow_nan=False)
    print(json.dumps({"arms": results, "shippedCoreML": result["shippedCoreML"]["metrics"],
                      "parity": result["initialTorchCoreMLDifference"]}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path)
    parser.add_argument("--native-challenge", type=Path)
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--training-protocol", type=Path, help="Additional training membership to exclude from challenge")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--baseline-only", action="store_true", help="Record shipped CoreML evidence without requiring completed training arms")
    args = parser.parse_args()
    try:
        if args.native_challenge:
            if not args.checkpoint or args.protocol or args.baseline_only: raise FocusDataError("invalid_challenge_arguments")
            native_challenge(args.native_challenge, args.checkpoint, args.output, args.training_protocol)
        elif args.protocol and not args.checkpoint and not args.training_protocol: report(args.protocol, args.output, args.baseline_only)
        else: raise FocusDataError("explicit_evaluation_input_required")
    except (OSError, ValueError, KeyError, TypeError) as error: parser.exit(2, str(error)+"\n")
