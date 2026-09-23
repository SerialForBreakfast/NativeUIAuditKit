"""Production Swift crop/inference adapter. No implicit builds or model downloads."""
import argparse
import base64
import hashlib
import io
import json
import os
import platform
import subprocess
import sys
from pathlib import Path

from focus_dataset_contract import ROOT, FocusDataError, digest, local, member

TOOL = ROOT / ".build/debug/FocusRingTool"
SOURCE = ROOT / "Sources/NativeUIAuditKit/Detection/FocusRingClassifier.swift"
RUNTIME_PREPROCESSING = {"expansion": .16, "cropSize": [256, 256],
                         "coordinates": "xywh-top-left-pixels", "resize": "FocusRingClassifier.makeCrop-v1"}


def identity():
    if not TOOL.is_file():
        raise FocusDataError("missing_runtime_tool_run_offline_swift_build")
    return {"sourceSHA256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "helperSHA256": hashlib.sha256(TOOL.read_bytes()).hexdigest(),
            "hostOS": platform.mac_ver()[0], "architecture": platform.machine()}


def invoke(items, model=None, *, experimental_aspect_fit=False):
    identity()
    if not items or len(items) > 128:
        raise FocusDataError("invalid_runtime_batch")
    # The caller creates in-project runtime storage explicitly; no HOME override.
    tmp = ROOT / ".build/debug-output/focus-launch/tmp"
    if not tmp.is_dir(): raise FocusDataError("missing_project_runtime_tmp_setup")
    request = {"version": 1, "root": str(ROOT), "mode": "infer" if model else "crop",
               "model": str(local(model)) if model else None, "items": items,
               "experimentalAspectFit": experimental_aspect_fit}
    try:
        result = subprocess.run([str(TOOL)], input=json.dumps(request, allow_nan=False),
                                text=True, capture_output=True, timeout=120,
                                env={**os.environ, "TMPDIR": str(tmp)})
    except (OSError, subprocess.TimeoutExpired) as error:
        raise FocusDataError("runtime_unavailable_or_timeout") from error
    if result.returncode:
        raise FocusDataError("runtime_failed: " + result.stderr[-1000:])
    reply = json.loads(result.stdout)
    if reply.get("version") != 1 or [r.get("id") for r in reply.get("results", [])] != [i["id"] for i in items]:
        raise FocusDataError("runtime_membership_mismatch")
    return reply


def items_for(document):
    root = local(ROOT / document["sourceRoot"])
    items = []
    for pair in document["pairs"]:
        for role, label in (("focused", 1), ("unfocused", 0)):
            frame = pair["frames"][role]
            items.append({"id": f"{pair['pair_id']}:{label}", "path": str(member(root, frame["path"])),
                          "sha256": frame["sha256"], "bounds": frame["bounds"]})
    return items


def bounded_batches(items):
    """Keep existing16-item batching while respecting the helper's decoded budget."""
    from PIL import Image
    batch, pixels = [], 0
    for item in items:
        with Image.open(item["path"]) as source:
            area = source.width * source.height
        if area <= 0 or area > 80_000_000:
            raise FocusDataError("runtime_pixel_limit")
        if batch and (len(batch) == 16 or pixels + area > 80_000_000):
            yield batch
            batch, pixels = [], 0
        batch.append(item)
        pixels += area
    if batch:
        yield batch


def rendered_items(document):
    from PIL import Image
    items = items_for(document)
    for batch in bounded_batches(items):
        reply = invoke(batch)
        for row in reply["results"]:
            raw = base64.b64decode(row["png"], validate=True)
            im = Image.open(io.BytesIO(raw)); im.load()
            if im.size != (256, 256): raise FocusDataError("runtime_crop_size")
            yield row["id"], raw, im.convert("RGB")


def render(document):
    """Small-fixture convenience; production validation streams bounded batches."""
    return {key:(raw,im) for key,raw,im in rendered_items(document)}


def recrop(manifest, dataset, output):
    from focus_dataset_contract import validate_manifest
    validate_manifest(manifest, dataset)
    output = local(output)
    if output.exists(): raise FocusDataError("output_collision")
    result = json.loads(json.dumps(manifest))
    images = rendered_items(result)
    result.update(version=manifest["version"] if manifest["version"] in {"1.4", "1.5"} else "1.3", preprocessing=RUNTIME_PREPROCESSING, runtimeCrop=identity())
    result.pop("trainingApproval", None)  # New pixels require a new corpus review.
    result["corpusID"] += "-runtime-crops"
    result["derivedFromManifestSHA256"] = digest(manifest)
    output.mkdir(parents=True, exist_ok=False)
    for pair in result["pairs"]:
        for role, label in (("focused", 1), ("unfocused", 0)):
            key, raw, _ = next(images)
            if key != f"{pair['pair_id']}:{label}": raise FocusDataError("runtime_membership_mismatch")
            name = hashlib.sha256(f"{pair['pair_id']}:{label}".encode()).hexdigest() + ".png"
            with (output / name).open("xb") as stream: stream.write(raw)
            pair[role + "_crop"] = name
            pair[role + "_crop_sha256"] = hashlib.sha256(raw).hexdigest()
    validate_manifest(result, output)
    with (output / "focus_dataset_manifest.json").open("x") as stream:
        json.dump(result, stream, indent=2)
    return result


def infer(document, model, protocol):
    from focus_ring_baseline import artifact_digest
    if artifact_digest(model) != protocol["artifact"]["sha256"]:
        raise FocusDataError("changed_model")
    runtime_identity = identity()
    if document.get("runtimeCrop") != runtime_identity: raise FocusDataError("changed_runtime")
    items = items_for(document)
    scores, batches = {}, []
    for batch in bounded_batches(items):
        reply = invoke(batch, model)
        batches.append({k: v for k, v in reply.items() if k != "results"})
        batches[-1]["samples"] = [{k:v for k,v in row.items() if k != "png"} for row in reply["results"]]
        for row in reply["results"]: scores[row["id"]] = row["probability"]
    if artifact_digest(model) != protocol["artifact"]["sha256"]:
        raise FocusDataError("changed_model_during_inference")
    if identity() != runtime_identity: raise FocusDataError("changed_runtime_during_inference")
    return {"formatVersion": "focus-baseline-scores-v1", "protocolSHA256": protocol["protocolSHA256"],
            "artifactSHA256": protocol["artifact"]["sha256"], "inferenceKind": "coreml",
            "scores": scores, "runtime": identity(), "timingBatches": batches,
            "timingScope": "CPU-only; model-load and first-prediction per process batch; remaining predictions warm; crop separate"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = recrop(json.loads(args.manifest.read_text()), args.manifest.parent, args.output)
        print(json.dumps({"pairs": len(result["pairs"]), "version": result["version"], "trainingApproval": False}))
        return 0
    except (OSError, ValueError) as error:
        print(str(error), file=sys.stderr); return 2

if __name__ == "__main__": raise SystemExit(main())
