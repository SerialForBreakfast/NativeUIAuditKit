#!/usr/bin/env python3
"""
train_ios_model.py — Phase 6a YOLO11m training on the 41-class family-holdout set.

Ultralytics YOLO11 has no `loss="focal"` train kwarg. Inverse-frequency α
(scripts/class_weights.json) is logged next to the run; OHEM oversamples the
hardest 20% of train images each epoch (scripts/ohem_callback.py).

Usage:
  .venv-yolo/bin/python scripts/train_ios_model.py --dry-run
  .venv-yolo/bin/python scripts/train_ios_model.py
  .venv-yolo/bin/python scripts/train_ios_model.py --model yolo11n --epochs 50
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATASET = PROJECT_ROOT / "NativeUITrainer" / "yolo_dataset_41class"
DEFAULT_RUNS = PROJECT_ROOT / "NativeUITrainer" / "yolo_runs"
WEIGHTS_DIR = PROJECT_ROOT / "NativeUITrainer" / "weights"
CLASS_WEIGHTS = PROJECT_ROOT / "scripts" / "class_weights.json"

# Keep Ultralytics caches inside the package (filesystem-boundary rule).
os_env_defaults = {
    "YOLO_CONFIG_DIR": str(PROJECT_ROOT / "NativeUITrainer" / ".ultralytics"),
}


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", default=str(DEFAULT_DATASET))
    p.add_argument(
        "--model",
        default="yolo11m",
        choices=["yolo11n", "yolo11s", "yolo11m", "yolo11l", "yolo11x"],
    )
    p.add_argument("--epochs", type=int, default=100)
    p.add_argument("--imgsz", type=int, default=640)
    p.add_argument(
        "--batch",
        type=int,
        default=4,
        help="Batch size. Default 4 fits YOLO11m on M4 MPS (~3.5 GB). -1 = AutoBatch.",
    )
    p.add_argument("--patience", type=int, default=15)
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("--name", default=None)
    p.add_argument("--output-dir", default=str(DEFAULT_RUNS))
    p.add_argument("--resume", default=None, help="Path to last.pt")
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="2 epochs, batch=4, 5% of images — smoke-test the pipeline",
    )
    p.add_argument("--no-ohem", action="store_true", help="Disable OHEM callback")
    return p.parse_args()


def resolve_weights(model_name: str) -> str:
    """Prefer in-package weights so Ultralytics does not write to ~."""
    WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)
    local = WEIGHTS_DIR / f"{model_name}.pt"
    scripts_copy = PROJECT_ROOT / "scripts" / f"{model_name}.pt"
    if local.exists():
        return str(local)
    if scripts_copy.exists():
        return str(scripts_copy)
    # Name-only so Ultralytics downloads into the current dir (WEIGHTS_DIR).
    return f"{model_name}.pt"


def main():
    import os

    for k, v in os_env_defaults.items():
        os.environ.setdefault(k, v)
        Path(v).mkdir(parents=True, exist_ok=True)

    args = parse_args()
    dataset_dir = Path(args.dataset).expanduser().resolve()
    yaml_path = dataset_dir / "dataset.yaml"
    if not yaml_path.exists():
        print(f"ERROR: dataset.yaml not found at {yaml_path}")
        print("Run: .venv-yolo/bin/python scripts/export_coco.py --dataset <root>")
        sys.exit(1)

    try:
        from ultralytics import YOLO
        from ultralytics.utils import SETTINGS
    except ImportError:
        print("ERROR: ultralytics not found. Use .venv-yolo/bin/python")
        sys.exit(1)

    SETTINGS.update(
        {
            "datasets_dir": str(PROJECT_ROOT / "NativeUITrainer"),
            "weights_dir": str(WEIGHTS_DIR),
            "runs_dir": str(DEFAULT_RUNS),
        }
    )

    epochs = args.epochs
    batch = args.batch
    fraction = 1.0
    rect = True
    run_name = args.name or f"phase6a_{args.model}_e{args.epochs}"
    if args.dry_run:
        epochs = 2
        batch = 4
        fraction = 0.05
        rect = False
        run_name = args.name or f"phase6a_{args.model}_dryrun"
        print("DRY-RUN: 2 epochs, batch=4, 5% fraction, OHEM still attached")

    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)

    # Resolve --resume before chdir. A relative last.pt is otherwise looked
    # up under NativeUITrainer/weights/ and raises FileNotFoundError (BP-30).
    if args.resume:
        resume_path = Path(args.resume).expanduser()
        if not resume_path.is_absolute():
            resume_path = (PROJECT_ROOT / resume_path).resolve()
        else:
            resume_path = resume_path.resolve()
        if not resume_path.is_file():
            print(f"ERROR: --resume not found: {resume_path}")
            sys.exit(1)
        args.resume = str(resume_path)

    # Point Ultralytics weight downloads at NativeUITrainer/weights.
    os.chdir(WEIGHTS_DIR)

    model_arg = args.resume or resolve_weights(args.model)
    print(f"\nPhase 6a training")
    print(f"  Model    : {args.model}")
    print(f"  Weights  : {model_arg}")
    print(f"  Epochs   : {epochs}")
    print(f"  Batch    : {'auto' if batch == -1 else batch}")
    print(f"  Dataset  : {yaml_path}")
    print(f"  Output   : {output_dir / run_name}")
    print(f"  OHEM     : {not args.no_ohem}")
    if CLASS_WEIGHTS.exists():
        print(f"  α weights: {CLASS_WEIGHTS.relative_to(PROJECT_ROOT)}")
    print()

    model = YOLO(model_arg)

    if not args.no_ohem:
        sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
        import ohem_callback as _ohem

        CB = getattr(_ohem, "OHEMCallback", None) or getattr(_ohem, "OHEMCallback")
        ohem = CB(fraction=0.2, factor=2.0)
        # Exact Ultralytics 8.4.124 event names (see engine/trainer.py run_callbacks).
        for event in (
            "on_pretrain_routine_end",
            "on_train_batch_end",
            "on_train_epoch_end",
        ):
            handler = getattr(ohem, event, None)
            if handler is None:
                print(f"WARNING: OHEM missing handler for {event!r}")
                continue
            model.add_callback(event, handler)

    def _backup_last_pt(trainer) -> None:
        """Copy last.pt → last.prev.pt after each save so a power cut cannot leave only a torn file."""
        last = Path(getattr(trainer, "last", "") or "")
        if last.exists():
            shutil.copy2(last, last.with_name("last.prev.pt"))

    model.add_callback("on_model_save", _backup_last_pt)

    train_kwargs = dict(
        data=str(yaml_path),
        epochs=epochs,
        imgsz=args.imgsz,
        batch=batch,
        patience=args.patience,
        rect=rect,
        fraction=fraction,
        device="mps",
        workers=args.workers,
        project=str(output_dir),
        name=run_name,
        exist_ok=True,
        pretrained=True,
        optimizer="AdamW",
        lr0=0.001,
        lrf=0.01,
        momentum=0.937,
        weight_decay=0.0005,
        warmup_epochs=3.0 if not args.dry_run else 0.0,
        warmup_momentum=0.8,
        box=7.5,
        cls=0.5,
        dfl=1.5,
        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4,
        degrees=0.0,
        translate=0.1,
        scale=0.5,
        shear=0.0,
        perspective=0.0,
        flipud=0.0,
        fliplr=0.5,
        mosaic=0.0 if args.dry_run else 1.0,
        mixup=0.0,
        copy_paste=0.0,
        cache=False,
        verbose=True,
        plots=not args.dry_run,
        save_period=1 if not args.dry_run else -1,
    )
    if args.resume:
        train_kwargs["resume"] = True

    print("Starting model.train()…", flush=True)
    results = model.train(**train_kwargs)
    best = output_dir / run_name / "weights" / "best.pt"
    print(f"\nTraining complete. best.pt → {best}")
    print("CoreML export (after a full run):")
    print(f"  .venv-yolo/bin/python scripts/export_yolo_coreml.py --weights {best}")
    return results


if __name__ == "__main__":
    import faulthandler
    import traceback

    faulthandler.enable()
    try:
        main()
    except Exception:
        traceback.print_exc()
        sys.exit(1)
