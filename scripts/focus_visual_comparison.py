"""Frozen, visual-review-only FocusRing comparison. No capture, training or promotion."""
import argparse
import hashlib
import json
import math
from pathlib import Path

from focus_dataset_contract import ROOT, FocusDataError, digest, local
from focus_ring_baseline import model_contract
from focus_runtime import identity, RUNTIME_PREPROCESSING
from focus_learning_report import infer_bounded, metrics
from perception_benchmark import validate_manifest, verify_evidence

VARIANTS = {"base": (0,0,0), "left4": (-4,0,0), "right4": (4,0,0),
    "up4": (0,-4,0), "down4": (0,4,0), "pad4": (0,0,4), "inset4": (0,0,-4)}
THRESHOLDS = [.5,.70,.85]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def destination(path):
    raw = Path(path).absolute()
    if any(p.is_symlink() for p in [raw,*raw.parents]): raise FocusDataError("symlink_output")
    path = local(raw)
    if path.exists(): raise FocusDataError("output_collision")
    if not path.is_relative_to(ROOT / "reports/work"):
        raise FocusDataError("report_output_required")
    return path


def samples(manifest):
    cases = validate_manifest(manifest)
    verify_evidence(cases)
    rows = []
    for case in cases:
        focus = case["labels"].get("focus")
        if not focus: continue
        if (case["sourceKind"] != "reviewedNativeCapture" or focus.get("basis") != "visualAppearanceOnly"):
            raise FocusDataError("reviewed_appearance_required")
        controls = case["labels"]["rows"]
        if len(controls) < 2 or any("box" not in r for r in controls):
            raise FocusDataError("missing_competing_control_boxes")
        for variant, (dx,dy,pad) in VARIANTS.items():
            for row in controls:
                x,y,w,h = row["box"]
                left,top = max(0,x+dx-pad),max(0,y+dy-pad)
                right,bottom = min(case["width"],x+w+dx+pad),min(case["height"],y+h+dy+pad)
                if right<=left or bottom<=top: raise FocusDataError("invalid_variant_geometry")
                rows.append({"id": case["caseID"]+":"+row["id"]+":"+variant,
                    "frameID":case["caseID"], "elementID":row["id"], "variant":variant,
                    "label":int(row["id"]==focus["elementID"]),
                    "path":case["imagePath"], "sha256":case["imageSHA256"],
                    "bounds":[left,top,right-left,bottom-top]})
    if not rows: raise FocusDataError("no_reviewed_focus_cases")
    if len({r["id"] for r in rows}) != len(rows): raise FocusDataError("duplicate_sample")
    return rows


def freeze(manifest_path, models_path, output):
    output = destination(output)
    manifest_path,models_path = local(manifest_path),local(models_path)
    rows = samples(json.loads(manifest_path.read_text()))
    paths = json.loads(models_path.read_text())
    if set(paths) != {"shipped","fp16","int8"}: raise FocusDataError("model_roles_required")
    models = {name:{"path":str(local(path).relative_to(ROOT)), **model_contract(local(path))}
              for name,path in paths.items()}
    doc = {"version":"focus-visual-protocol-v1", "manifest":str(manifest_path.relative_to(ROOT)),
        "manifestSHA256":sha(manifest_path), "models":models, "samples":rows,
        "runtime":identity(), "preprocessing":RUNTIME_PREPROCESSING,
        "thresholds":THRESHOLDS, "variants":list(VARIANTS), "trainingEligible":False,
        "releaseEligible":False, "labelBasis":"visualAppearanceOnly", "partition":"development"}
    doc["protocolSHA256"] = digest(doc)
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open("x") as f: json.dump(doc,f,indent=2)
    return doc


def validate_protocol(doc):
    copy = dict(doc); expected = copy.pop("protocolSHA256",None)
    if digest(copy) != expected: raise FocusDataError("changed_protocol")
    if (doc.get("version") != "focus-visual-protocol-v1" or doc.get("thresholds") != THRESHOLDS or
        doc.get("variants") != list(VARIANTS) or doc.get("trainingEligible") is not False or
        doc.get("releaseEligible") is not False or doc.get("partition") != "development" or
        doc.get("preprocessing") != RUNTIME_PREPROCESSING or doc.get("labelBasis") != "visualAppearanceOnly"):
        raise FocusDataError("unsupported_protocol")
    manifest = local(ROOT/doc["manifest"])
    if sha(manifest) != doc["manifestSHA256"]: raise FocusDataError("changed_manifest")
    if samples(json.loads(manifest.read_text())) != doc["samples"]: raise FocusDataError("changed_samples")
    if identity() != doc["runtime"]: raise FocusDataError("changed_runtime")
    if set(doc["models"]) != {"shipped","fp16","int8"}: raise FocusDataError("model_roles_required")
    for model in doc["models"].values():
        if model_contract(local(ROOT/model["path"])) != {k:v for k,v in model.items() if k!="path"}:
            raise FocusDataError("changed_model")


def score(rows, predictions):
    if [r["id"] for r in rows] != [r.get("id") for r in predictions]:
        raise FocusDataError("prediction_membership_mismatch")
    probabilities = [r.get("probability") for r in predictions]
    if any(type(p) not in (int,float) or not math.isfinite(p) or not 0<=p<=1 for p in probabilities):
        raise FocusDataError("invalid_probability")
    observed = [{**r,"probability":p} for r,p in zip(rows,probabilities)]
    result = {}
    for variant in VARIANTS:
        selected = [r for r in observed if r["variant"]==variant]
        if not selected: continue
        decisions = []
        for frame in dict.fromkeys(r["frameID"] for r in selected):
            frame_rows = [r for r in selected if r["frameID"]==frame]
            positive = [r for r in frame_rows if r["probability"]>=.85]
            status = "multiple-focus-abstention" if len(positive)>1 else "no-focus" if not positive else "correct" if positive[0]["label"] else "wrong-focus"
            decisions.append({"frameID":frame,"decision":status,
                "selectedElementID":positive[0]["elementID"] if len(positive)==1 else None})
        result[variant] = {"metrics":metrics(selected), "frameDecisions":decisions,
            "ambiguityBandCount":sum(.70<=r["probability"]<.85 for r in selected),
            "nearThresholdCount":sum(any(abs(r["probability"]-t)<=.01 for t in THRESHOLDS) for r in selected)}
    return result


def run(protocol_path, output):
    output = destination(output)
    protocol_path = local(protocol_path); protocol_hash = sha(protocol_path)
    doc = json.loads(protocol_path.read_text()); validate_protocol(doc)
    output.mkdir(parents=True,exist_ok=False)
    items = [{"id":r["id"],"path":str(ROOT/r["path"]),"sha256":r["sha256"],"bounds":r["bounds"]} for r in doc["samples"]]
    results = {}
    for name in ("shipped","fp16","int8"):
        reply = infer_bounded(items,local(ROOT/doc["models"][name]["path"]))
        evaluated = score(doc["samples"],reply["results"])
        results[name] = {"scores":reply["results"],"timing":reply["batches"],"evaluation":evaluated}
        with (output/(name+".json")).open("x") as f: json.dump(results[name],f,indent=2,allow_nan=False)
    validate_protocol(doc)
    if sha(protocol_path) != protocol_hash: raise FocusDataError("changed_protocol_file")
    differences = [{"id":a["id"],"absoluteError":abs(a["probability"]-b["probability"]),
        "disagreedThresholds":[t for t in THRESHOLDS if (a["probability"]>=t)!=(b["probability"]>=t)]}
        for a,b in zip(results["fp16"]["scores"],results["int8"]["scores"],strict=True)]
    report = {"version":"focus-visual-comparison-v1", "protocolSHA256":doc["protocolSHA256"],
        "models":doc["models"], "results":results,"compressionDifferences":differences,
        "trainingEligible":False,"releaseEligible":False,
        "support":{"reviewedFrames":len({r["frameID"] for r in doc["samples"]}),
                   "reviewedBoxes":sum(r["variant"]=="base" for r in doc["samples"]),
                   "correlatedVariantsPerBox":len(VARIANTS)},
        "limitations":["Reviewed legacy frames with visual-only labels; correlated development membership, not an independent holdout",
            "Box perturbations are correlated sensitivity diagnostics, not extra training data",
            "CPU helper only, no TTR navigation or end-to-end latency qualification",
            "Boxes supplied by reviewer; detector localization not measured"]}
    with (output/"report.json").open("x") as f: json.dump(report,f,indent=2,allow_nan=False)
    print(json.dumps({name:r["evaluation"]["base"] for name,r in results.items()}))
    return report


if __name__ == "__main__":
    p=argparse.ArgumentParser(description=__doc__); sub=p.add_subparsers(dest="command",required=True)
    f=sub.add_parser("freeze"); f.add_argument("--manifest",type=Path,required=True); f.add_argument("--models",type=Path,required=True); f.add_argument("--output",type=Path,required=True)
    r=sub.add_parser("run"); r.add_argument("--protocol",type=Path,required=True); r.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    try:
        if a.command=="freeze": freeze(a.manifest,a.models,a.output)
        else: run(a.protocol,a.output)
    except (ValueError,OSError,KeyError,TypeError) as error: p.exit(2,str(error)+"\n")
