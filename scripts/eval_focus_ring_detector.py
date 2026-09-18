#!/usr/bin/env python3
"""
eval_focus_ring_detector.py — Held-out quality gates for FocusRingDetector.

Prefers the exported CoreML `.mlpackage` when coremltools can load it; otherwise
scores the PyTorch `best.pt` on the same test split.

Usage:
  .venv-yolo/bin/python scripts/eval_focus_ring_detector.py \\
      --dataset ../NativeUIAuditKit-Dataset/focus_ring \\
      --mlpackage NativeUITrainer/focus_ring_runs/<run>/export/FocusRingDetector.mlpackage
"""

from __future__ import annotations

import argparse
import json
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
for _k, _v in os_env_defaults.items():
    os.environ.setdefault(_k, _v)
    Path(_v).mkdir(parents=True, exist_ok=True)

DEFAULT_DATASET = PROJECT_ROOT.parent / "NativeUIAuditKit-Dataset" / "focus_ring"
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
    p.add_argument("--mlpackage", default=None)
    p.add_argument("--weights", default=None)
    p.add_argument("--output-dir", default=None)
    return p.parse_args()


def load_split(dataset: Path, split: str) -> list[dict]:
    manifest_path = dataset / "focus_dataset_manifest.json"
    if not manifest_path.is_file():
        return []
    data = json.loads(manifest_path.read_text())
    rows: list[dict] = []
    for pair in data.get("pairs") or []:
        if pair.get("split") != split:
            continue
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
    return [r for r in rows if Path(r["path"]).is_file()]


def metrics(rows: list[dict], probs: list[float], thr: float = FOCUS_THR) -> dict:
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
    n = max(1, tp + fp + tn + fn)
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

    ckpt = torch.load(weights, map_location="cpu", weights_only=False)
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
        "accuracy": m["accuracy"] >= GATES["accuracy"],
        "fpr": m["fpr"] <= GATES["fpr"],
        "fnr": m["fnr"] <= GATES["fnr"],
        "precision_at_085": m["precision_at_085"] >= GATES["precision_at_085"],
        "recall_at_085": m["recall_at_085"] >= GATES["recall_at_085"],
    }


def main() -> int:
    args = parse_args()
    dataset = Path(args.dataset).expanduser()
    if not dataset.is_absolute():
        dataset = (PROJECT_ROOT / dataset).resolve()
    test = load_split(dataset, "test")
    print(f"=== FocusRing eval {utc_now()} ===")
    print(f"dataset: {dataset}  test_n={len(test)}")
    if not test:
        print("ERROR: no labeled test crops. Phase B harvest required.")
        return 1

    mlpackage = Path(args.mlpackage).expanduser().resolve() if args.mlpackage else None
    weights = Path(args.weights).expanduser().resolve() if args.weights else None
    probs = None
    backend = None
    if mlpackage and mlpackage.exists():
        probs = predict_coreml(mlpackage, test)
        backend = "coreml" if probs is not None else None
    if probs is None and weights and weights.is_file():
        probs = predict_torch(weights, test)
        backend = "torch"
    if probs is None:
        print("ERROR: provide a loadable --mlpackage or --weights")
        return 1

    m = metrics(test, probs)
    hard_idx = [
        i
        for i, row in enumerate(test)
        if row["label"] == 0 and row.get("theme") in HARD_THEMES and row.get("element_type") in HARD_TYPES
    ]
    hard_fpr = 0.0
    if hard_idx:
        hard_fp = sum(1 for i in hard_idx if probs[i] >= FOCUS_THR)
        hard_fpr = hard_fp / len(hard_idx)
    gates = gate_report(m)
    gates["hard_negative_fpr"] = hard_fpr <= GATES["hard_negative_fpr"]
    all_pass = all(gates.values())

    out_dir = Path(args.output_dir).expanduser().resolve() if args.output_dir else (
        mlpackage.parent if mlpackage else (weights.parent.parent / "export" if weights else PROJECT_ROOT / "reports")
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    eval_report = {
        "generatedAt": utc_now(),
        "backend": backend,
        "threshold": FOCUS_THR,
        "metrics": m,
        "gates": gates,
        "all_gates_pass": all_pass,
    }
    hard_report = {
        "generatedAt": utc_now(),
        "n": len(hard_idx),
        "fpr": hard_fpr,
        "gate": GATES["hard_negative_fpr"],
        "pass": gates["hard_negative_fpr"],
    }
    (out_dir / "focus_ring_detector_eval_report.json").write_text(json.dumps(eval_report, indent=2) + "\n")
    (out_dir / "focus_ring_detector_hard_negative_eval.json").write_text(json.dumps(hard_report, indent=2) + "\n")
    print(json.dumps({k: round(v, 4) if isinstance(v, float) else v for k, v in m.items()}))
    print(f"hard-negative FPR={hard_fpr:.4f}  all_gates_pass={all_pass}")
    print(f"wrote reports under {out_dir}")
    return 0 if all_pass else 2


if __name__ == "__main__":
    sys.exit(main())
