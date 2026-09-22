#!/usr/bin/env python3
"""
eval_focus_ring_detector.py — Held-out quality gates for FocusRingDetector.

Requires one explicit backend and a new in-project output directory. Legacy
corpora require --diagnostic-only and can never pass qualification gates.

Usage:
  .venv-yolo/bin/python scripts/eval_focus_ring_detector.py \\
      --dataset dataset/focus_ring/qualified-runtime-corpus \\
      --mlpackage NativeUITrainer/focus_ring_runs/<run>/export/FocusRingDetector.mlpackage \\
      --output-dir reports/focus-evaluation-<unique-id>
"""

from __future__ import annotations

import argparse
import json
import math
import hashlib
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
os_env_defaults = {
    "YOLO_CONFIG_DIR": str(PROJECT_ROOT / "NativeUITrainer" / ".ultralytics"),
    "MPLCONFIGDIR": str(PROJECT_ROOT / "NativeUITrainer" / ".mplconfig"),
    "TORCH_HOME": str(PROJECT_ROOT / "NativeUITrainer" / ".torch"),
}
DEFAULT_DATASET = PROJECT_ROOT / "dataset" / "focus_ring"
FOCUS_THR = 0.85
HARD_THEMES = frozenset({"light", "highContrast"})
HARD_TYPES = frozenset({"imageView", "collectionItem"})

GATES = {
    "accuracy": 0.99,
    "fpr": 0.005,
    "fnr": 0.01,
    "precision_at_085": 0.98,
    "recall_at_085": 0.98,
    "hard_negative_fpr": 0.005,
}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", default=str(DEFAULT_DATASET))
    backend=p.add_mutually_exclusive_group(required=True)
    backend.add_argument("--mlpackage", default=None)
    backend.add_argument("--weights", default=None)
    p.add_argument("--output-dir", required=True)
    p.add_argument("--diagnostic-only", action="store_true", help="Legacy byte-verified diagnostics; never model qualification")
    return p.parse_args()


def load_split(dataset: Path, split: str) -> list[dict]:
    manifest_path = dataset / "focus_dataset_manifest.json"
    if not manifest_path.is_file():
        raise ValueError("missing_manifest")
    data = json.loads(manifest_path.read_text())
    rows: list[dict] = []
    for pair in data.get("pairs") or []:
        if pair.get("split") != split:
            continue
        if not pair.get("focused_crop") or not pair.get("unfocused_crop"):
            raise ValueError("incomplete_pair")
        if pair.get("focused_crop"):
            rows.append(
                {
                    "path": dataset / pair["focused_crop"],
                    "label": 1,
                    "theme": pair.get("theme"),
                    "element_type": pair.get("element_type"),
                }
            )
        if pair.get("unfocused_crop"):
            rows.append(
                {
                    "path": dataset / pair["unfocused_crop"],
                    "label": 0,
                    "theme": pair.get("theme"),
                    "element_type": pair.get("element_type"),
                }
            )
    from audit_training_evidence import inspect_png
    for row in rows:
        result=inspect_png(dataset,str(row["path"].relative_to(dataset)),(256,256))
        if not result["valid"]: raise ValueError("invalid_test_member: "+result.get("error","unknown"))
    if not rows: raise ValueError("empty_test_split")
    return rows


def metrics(rows: list[dict], probs: list[float], thr: float = FOCUS_THR) -> dict:
    if not rows or len(rows)!=len(probs): raise ValueError("empty_or_incomplete_predictions")
    if any(type(p) not in (int,float) or not math.isfinite(p) or not 0<=p<=1 for p in probs): raise ValueError("invalid_probability")
    if any(r.get("label") not in (0,1) for r in rows): raise ValueError("invalid_label")
    tp = fp = tn = fn = 0
    for row, p in zip(rows, probs):
        pred = 1 if p >= thr else 0
        y = int(row["label"])
        if pred == 1 and y == 1:
            tp += 1
        elif pred == 1 and y == 0:
            fp += 1
        elif pred == 0 and y == 0:
            tn += 1
        else:
            fn += 1
    n = tp + fp + tn + fn
    precision = tp / max(1, tp + fp)
    recall = tp / max(1, tp + fn)
    fpr = fp / max(1, fp + tn)
    fnr = fn / max(1, fn + tp)
    acc = (tp + tn) / n
    return {
        "n": n,
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "accuracy": acc,
        "fpr": fpr,
        "fnr": fnr,
        "precision_at_085": precision,
        "recall_at_085": recall,
    }


def predict_torch(weights: Path, rows: list[dict]) -> list[float]:
    import importlib.util
    import numpy as np
    import torch
    from PIL import Image

    ckpt = torch.load(weights, map_location="cpu", weights_only=True)
    state = ckpt["state_dict"] if isinstance(ckpt, dict) and "state_dict" in ckpt else ckpt
    bb_path = Path(__file__).with_name("focus_ring_backbone.py")
    spec = importlib.util.spec_from_file_location("focus_ring_backbone", bb_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"could not load {bb_path}")
    bb = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bb)
    model = bb.mobilenetv4_conv_small(pretrained=False, num_classes=1)
    model.load_state_dict(state)
    model.eval()
    probs: list[float] = []
    with torch.no_grad():
        for row in rows:
            img = Image.open(row["path"]).convert("RGB").resize((256, 256), Image.Resampling.BILINEAR)
            x = torch.from_numpy(np.array(img, copy=True)).permute(2, 0, 1).float().div_(255.0).unsqueeze(0)
            logits = model(x).reshape(-1)[0]
            probs.append(float(torch.sigmoid(logits)))
    return probs


def predict_coreml(mlpackage: Path, rows: list[dict]) -> list[float] | None:
    try:
        import coremltools as ct
        from PIL import Image
    except ImportError:
        return None
    model = ct.models.MLModel(str(mlpackage))
    probs: list[float] = []
    for row in rows:
        img = Image.open(row["path"]).convert("RGB").resize((256, 256))
        out = model.predict({"image": img})
        raw = out.get("is_focused_prob")
        if hasattr(raw, "__len__"):
            probs.append(float(raw[0]))
        else:
            probs.append(float(raw))
    return probs


def gate_report(m: dict) -> dict:
    return {
        "accuracy": m["n"]>0 and m["accuracy"] >= GATES["accuracy"],
        "fpr": m["fp"]+m["tn"]>0 and m["fpr"] <= GATES["fpr"],
        "fnr": m["fn"]+m["tp"]>0 and m["fnr"] <= GATES["fnr"],
        "precision_at_085": m["tp"]+m["fp"]>0 and m["precision_at_085"] >= GATES["precision_at_085"],
        "recall_at_085": m["tp"]+m["fn"]>0 and m["recall_at_085"] >= GATES["recall_at_085"],
    }


def hard_negative_report(rows, probs):
    metrics(rows,probs)  # exact membership and finite probability validation
    counts={f"{t}/{k}":0 for t in sorted(HARD_THEMES) for k in sorted(HARD_TYPES)}
    indices=[]
    for i,row in enumerate(rows):
        key=f"{row.get('theme')}/{row.get('element_type')}"
        if row["label"]==0 and key in counts: counts[key]+=1; indices.append(i)
    n=len(indices); fpr=sum(probs[i]>=FOCUS_THR for i in indices)/n if n else None
    supported=n>=100 and all(counts.values())
    return {"n":n,"strata":counts,"fpr":fpr,"gate":GATES["hard_negative_fpr"],
            "supportSufficient":supported,"pass":supported and fpr<=GATES["hard_negative_fpr"]}


def main() -> int:
    args = parse_args()
    from focus_dataset_contract import local, validate_manifest, digest
    from audit_training_evidence import audit_focus
    from focus_ring_baseline import artifact_digest
    from focus_ring_readiness import validate
    try:
        dataset=local(args.dataset); out_dir=local(args.output_dir)
        if out_dir.exists(): raise ValueError("output_collision")
        artifact=local(args.mlpackage or args.weights)
        def model_hash():
            return artifact_digest(artifact) if args.mlpackage else hashlib.sha256(artifact.read_bytes()).hexdigest()
        model_sha=model_hash()
        audit=audit_focus(dataset)
        if audit["invalidMembers"] or audit["metadataErrors"] or audit["duplicatePairIDs"] or audit["seedCrossSplit"] or audit["crossSplitPixelGroups"]:
            raise ValueError("invalid_or_leaking_corpus")
        document=json.loads((dataset/"focus_dataset_manifest.json").read_text())
        if not args.diagnostic_only:
            if document.get("version")!="1.3" or document.get("evidenceKind")!="reviewed-fixture": raise ValueError("qualified_runtime_corpus_required_or_explicit_diagnostic_only")
            rows=validate_manifest(document,dataset)
            validate(rows,evidence_root=PROJECT_ROOT/document["sourceRoot"])
            approval=document.get("trainingApproval",{})
            if approval.get("approved") is not True or not approval.get("reviewReference") or approval.get("membershipSHA256")!=digest(document["pairs"]): raise ValueError("missing_corpus_review")
        test=load_split(dataset,"test")
        for key,value in os_env_defaults.items():
            os.environ[key]=value; Path(value).mkdir(parents=True,exist_ok=True)
        runtime_tmp=PROJECT_ROOT/".build/debug-output/focus-eval/tmp"
        runtime_tmp.mkdir(parents=True,exist_ok=True); os.environ["TMPDIR"]=str(runtime_tmp)
        backend="coreml" if args.mlpackage else "torch"
        probs=predict_coreml(artifact,test) if args.mlpackage else predict_torch(artifact,test)
        if probs is None: raise ValueError("requested_backend_unavailable_no_fallback")
        if model_hash()!=model_sha or audit_focus(dataset)!=audit: raise ValueError("inputs_changed_during_inference")
        m=metrics(test,probs); hard=hard_negative_report(test,probs)
        gates=gate_report(m); gates["hard_negative_fpr"]=hard["pass"]
        all_pass=not args.diagnostic_only and all(gates.values())
        report={"formatVersion":"focus-evaluation-v2","generatedAt":utc_now(),"backend":backend,
                "artifactSHA256":model_sha,"manifestSHA256":audit["manifestSHA256"],"auditSHA256":digest(audit),
                "evaluatorSHA256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "threshold":FOCUS_THR,"metrics":m,"diagnosticThresholdChecks":gates,
                "gates":gates if not args.diagnostic_only else None,"all_gates_pass":all_pass,
                "modelGatePassed":"not_assessed" if args.diagnostic_only else "passed" if all_pass else "failed",
                "scope":"legacy diagnostics; labels not requalified" if args.diagnostic_only else "numeric FocusRing gates only; not export parity or promotion"}
        hard["numericThresholdSatisfied"]=hard["pass"]
        hard["pass"]=not args.diagnostic_only and hard["pass"]
        out_dir.mkdir(parents=True,exist_ok=False)
        for name,value in (("focus_ring_detector_eval_report.json",report),("focus_ring_detector_hard_negative_eval.json",hard)):
            with (out_dir/name).open("x") as stream: json.dump(value,stream,indent=2)
        print(json.dumps({"backend":backend,"all_gates_pass":all_pass,"modelGatePassed":report["modelGatePassed"]}))
        return 0 if args.diagnostic_only or all_pass else 2
    except (OSError,ValueError) as error:
        print(f"ERROR: {error}",file=sys.stderr); return 2


if __name__ == "__main__":
    sys.exit(main())
