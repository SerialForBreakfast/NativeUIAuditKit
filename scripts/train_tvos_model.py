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
    "MPLCONFIGDIR": str(PROJECT_ROOT / "NativeUITrainer" / ".mplconfig"),
    "TORCH_HOME": str(PROJECT_ROOT / "NativeUITrainer" / ".torch"),
}

for _k, _v in os_env_defaults.items():
    os.environ[_k] = _v
    Path(_v).mkdir(parents=True, exist_ok=True)



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
        from ultralytics.utils import SETTINGS
    except ImportError:
        print("ERROR: ultralytics not installed in current environment.", file=sys.stderr, flush=True)
        sys.exit(1)

    SETTINGS.update(
        {
            "datasets_dir": str(PROJECT_ROOT / "NativeUITrainer"),
            "weights_dir": str(WEIGHTS_DIR),
            "runs_dir": str(DEFAULT_RUNS),
        }
    )

    base_weights = resolve_weights(args.model)
    print(f"Loading base weights: {base_weights}", flush=True)
    model = YOLO(base_weights)

    import shutil

    def _backup_last_pt(trainer) -> None:
        last = Path(getattr(trainer, "last", "") or "")
        if last.exists():
            shutil.copy2(last, last.with_name("last.prev.pt"))

    model.add_callback("on_model_save", _backup_last_pt)

    epochs = 2 if args.dry_run else args.epochs
    batch = 8 if args.dry_run else args.batch
    fraction = 0.05 if args.dry_run else 1.0
    rect = False if args.dry_run else True
    workers = 2 if args.dry_run else args.workers
    run_name = args.name if not args.dry_run else f"{args.name}_dryrun"

    print(f"Starting tvOS YOLO11 training: {epochs} epochs, batch={batch}, imgsz={args.imgsz}, fraction={fraction}, rect={rect}", flush=True)

    train_kwargs = dict(
        data=str(yaml_path),
        epochs=epochs,
        batch=batch,
        imgsz=args.imgsz,
        fraction=fraction,
        rect=rect,
        patience=args.patience,
        workers=workers,
        device="mps",
        project=args.output_dir,
        name=run_name,
        exist_ok=True,
        verbose=True,
        optimizer="AdamW",
        lr0=0.001,
        lrf=0.01,
        warmup_epochs=3.0 if not args.dry_run else 0.0,
        box=7.5,
        cls=0.5,
        dfl=1.5,
        mosaic=0.0 if args.dry_run else 1.0,
        plots=True,
    )

    results = model.train(**train_kwargs)

    best_pt = Path(args.output_dir) / run_name / "weights" / "best.pt"
    print(f"\ntvOS Training Complete! Best weights: {best_pt}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
