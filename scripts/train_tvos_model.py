#!/usr/bin/env python3
"""
train_tvos_model.py — Train NativeUIModel_tvOS using YOLO11 on tvOS OS UI dataset.

Usage:
    .venv-yolo/bin/python scripts/train_tvos_model.py --dry-run
    .venv-yolo/bin/python scripts/train_tvos_model.py --epochs 100 --batch 8
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATASET = PROJECT_ROOT / "NativeUITrainer" / "yolo_dataset_tvos"
DEFAULT_RUNS = PROJECT_ROOT / "NativeUITrainer" / "yolo_runs"
WEIGHTS_DIR = PROJECT_ROOT / "NativeUITrainer" / "weights"

os_env_defaults = {
    "YOLO_CONFIG_DIR": str(PROJECT_ROOT / "NativeUITrainer" / ".ultralytics"),
}


def parse_args():
    p = argparse.ArgumentParser(description="Train tvOS OS UI detector with YOLO11")
    p.add_argument("--dataset", default=str(DEFAULT_DATASET))
    p.add_argument("--model", default="yolo11n", choices=["yolo11n", "yolo11s", "yolo11m"])
    p.add_argument("--epochs", type=int, default=100)
    p.add_argument("--imgsz", type=int, default=640)
    p.add_argument("--batch", type=int, default=8)
    p.add_argument("--patience", type=int, default=15)
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("--name", default="phase6b_tvos_v0")
    p.add_argument("--output-dir", default=str(DEFAULT_RUNS))
    p.add_argument("--dry-run", action="store_true", help="2 epochs smoke-test")
    return p.parse_args()


def resolve_weights(model_name: str) -> str:
    WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)
    local = WEIGHTS_DIR / f"{model_name}.pt"
    root_copy = PROJECT_ROOT / f"{model_name}.pt"
    if root_copy.exists():
        return str(root_copy)
    if local.exists():
        return str(local)
    return f"{model_name}.pt"


def main():
    for k, v in os_env_defaults.items():
        os.environ.setdefault(k, v)
        Path(v).mkdir(parents=True, exist_ok=True)

    args = parse_args()
    dataset_dir = Path(args.dataset).expanduser().resolve()
    yaml_path = dataset_dir / "dataset.yaml"

    if not yaml_path.exists():
        print(f"ERROR: dataset.yaml not found at {yaml_path}.", file=sys.stderr)
        print("Run scripts/export_tvos_coco.py first.", file=sys.stderr)
        sys.exit(1)

    try:
        from ultralytics import YOLO
    except ImportError:
        print("ERROR: ultralytics not installed in current environment.", file=sys.stderr)
        sys.exit(1)

    base_weights = resolve_weights(args.model)
    print(f"Loading base weights: {base_weights}")
    model = YOLO(base_weights)

    epochs = 2 if args.dry_run else args.epochs
    batch = 4 if args.dry_run else args.batch

    print(f"Starting tvOS YOLO11 training: {epochs} epochs, batch={batch}, imgsz={args.imgsz}")

    results = model.train(
        data=str(yaml_path),
        epochs=epochs,
        batch=batch,
        imgsz=args.imgsz,
        patience=args.patience,
        workers=args.workers,
        device="mps",
        project=args.output_dir,
        name=args.name,
        exist_ok=True,
        verbose=True,
    )

    print(f"\ntvOS Training Complete! Results saved in {args.output_dir}/{args.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
