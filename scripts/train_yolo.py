#!/usr/bin/env python3
"""
train_yolo.py  —  Train YOLO11 on the NativeUIAuditKit iOS UI dataset.

Prerequisites:
  1. Run convert_cml_to_yolo.py to produce the YOLO dataset directory.
  2. Activate the project venv:  source .venv-yolo/bin/activate
     or call this script via:   .venv-yolo/bin/python scripts/train_yolo.py

Usage:
  # Smoke test (10 epochs, fast):
  .venv-yolo/bin/python scripts/train_yolo.py \\
    --dataset NativeUITrainer/yolo_dataset \\
    --smoke-test

  # Full run (adjust epochs/model as needed):
  .venv-yolo/bin/python scripts/train_yolo.py \\
    --dataset NativeUITrainer/yolo_dataset \\
    --model   yolo11s \\
    --epochs  150

Outputs:
  NativeUITrainer/yolo_runs/<name>/
    weights/best.pt      — best checkpoint (use this for CoreML export)
    weights/last.pt      — final epoch checkpoint
    results.csv          — per-epoch metrics
    args.yaml            — full hyperparameter record

Notes:
  - rect=True groups batches by aspect ratio, which matters for our
    mix of portrait full-images (750×1334, 1179×2556) and wide strips
    (750×293, 1179×562).
  - device="mps" uses Apple Silicon GPU on this Mac.
  - For 41-class expansion, just re-convert the dataset with more classes
    and re-run this script with the new dataset.yaml.
"""

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_RUNS = PROJECT_ROOT / "NativeUITrainer" / "yolo_runs"


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--dataset",    required=True,
                   help="Path to YOLO dataset directory (must contain dataset.yaml)")
    p.add_argument("--model",      default="yolo11n",
                   choices=["yolo11n", "yolo11s", "yolo11m", "yolo11l", "yolo11x"],
                   help="YOLO11 model variant (default: yolo11n)")
    p.add_argument("--epochs",     type=int, default=100,
                   help="Training epochs (default: 100)")
    p.add_argument("--imgsz",      type=int, default=640,
                   help="Training image size (default: 640)")
    p.add_argument("--batch",      type=int, default=-1,
                   help="Batch size; -1 = auto-scale to 60%% GPU memory (default: -1)")
    p.add_argument("--name",       default=None,
                   help="Run name (default: <model>_e<epochs>)")
    p.add_argument("--output-dir", default=str(DEFAULT_RUNS),
                   help=f"Parent dir for training runs (default: {DEFAULT_RUNS})")
    p.add_argument("--workers",    type=int, default=4,
                   help="Dataloader workers (default: 4)")
    p.add_argument("--smoke-test", action="store_true",
                   help="Quick validation: 10 epochs, batch=8, no rect (fast startup)")
    p.add_argument("--resume",     default=None,
                   help="Path to checkpoint to resume from (last.pt)")
    return p.parse_args()


class FrozenYOLOBackbone:
    """Verify the resident YOLO11 backbone and preserve its normalization buffers."""

    def __init__(self, model):
        import torch
        backbone = model.yaml.get('backbone', [])
        expected = ['Conv','Conv','C3k2','Conv','C3k2','Conv','C3k2','Conv','C3k2','SPPF','C2PSA']
        if (len(backbone) != 11 or type(model.model[-1]).__name__ != 'Detect' or
                [type(layer).__name__ for layer in model.model[:11]] != expected):
            raise ValueError('detector_frozen_architecture')
        self.prefixes = tuple(f'model.{i}.' for i in range(len(backbone)))
        self.reference = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()
                          if k.startswith(self.prefixes)}
        if not self.reference or not all(torch.isfinite(v).all() for v in self.reference.values()):
            raise ValueError('detector_frozen_state')
        self.checks = 0

    def verify(self, trainer):
        import torch
        state = trainer.model.state_dict()
        if any(not torch.equal(state[k].detach().cpu(), v) for k, v in self.reference.items()):
            raise ValueError('detector_frozen_backbone_changed')
        if any(p.requires_grad for k, p in trainer.model.named_parameters() if k.startswith(self.prefixes)):
            raise ValueError('detector_frozen_backbone_trainable')
        self.checks += 1
        # EMA arithmetic can round unchanged tensors. Preserve the frozen initializer exactly.
        if getattr(trainer, 'ema', None) is not None:
            ema = trainer.ema.ema.state_dict()
            with torch.no_grad():
                for key, value in self.reference.items():
                    ema[key].copy_(value.to(device=ema[key].device, dtype=ema[key].dtype))


def train_native_hcf(dataset_yaml, initialization, output, progress=None, weights='best', patience=10, learning_rate=.001, freeze_backbone=False):
    """Use the resident YOLO trainer with fixed native HCF settings.

    weights='best' keeps the HCF371 behavior (validation fitness). weights='last' returns the final epoch.
    """
    if weights not in ('best', 'last'):
        raise ValueError('hcf_weights_choice')
    if type(patience) is not int or patience not in (0, 10):
        raise ValueError('hcf_patience_choice')
    if type(learning_rate) not in (int,float) or learning_rate not in (.001,.0001):
        raise ValueError('hcf_learning_rate_choice')
    if type(freeze_backbone) is not bool:
        raise ValueError('detector_freeze_backbone_boolean')
    import os
    os.environ.setdefault('YOLO_CONFIG_DIR', str(PROJECT_ROOT/'NativeUITrainer/.ultralytics'))
    os.environ.setdefault('MPLCONFIGDIR', str(PROJECT_ROOT/'NativeUITrainer/.mplconfig'))
    os.environ['YOLO_OFFLINE'] = 'true'
    if not Path(initialization).is_file(): raise ValueError('hcf_initialization_missing')
    from ultralytics import YOLO
    model = YOLO(str(initialization))
    options = {}
    if freeze_backbone:
        frozen = FrozenYOLOBackbone(model.model)
        options['freeze'] = 11
        model.add_callback('on_pretrain_routine_end', frozen.verify)
        model.add_callback('on_train_epoch_end', frozen.verify)
    if progress:
        model.add_callback('on_train_epoch_end', lambda trainer: progress(
            'Train HCF full-screen detector', trainer.epoch+1, trainer.epochs))
    model.train(data=str(dataset_yaml), epochs=30, patience=patience, batch=8, imgsz=640, device='mps', workers=0,
        project=str(output), name='detector', exist_ok=False, seed=371, deterministic=True,
        optimizer='AdamW', lr0=learning_rate, lrf=.01, pretrained=True, plots=False, save=True, save_period=1,
        rect=True, cache=False, amp=False, mosaic=0, mixup=0, copy_paste=0, fliplr=0, flipud=0,
        degrees=0, translate=0, scale=0, shear=0, perspective=0, hsv_h=0, hsv_s=0, hsv_v=0, **options)
    if freeze_backbone:
        import json
        if frozen.checks != 31:
            raise ValueError('detector_frozen_verification_incomplete')
        (output/'frozen-backbone.json').write_text(json.dumps(dict(
            layers=list(range(11)), tensors=len(frozen.reference), checks=frozen.checks,
            parametersAndBuffersUnchanged=True, emaFrozenStatePreserved=True)))
    return output/'detector/weights'/(weights + '.pt')


def main():
    args   = parse_args()
    dataset_dir = Path(args.dataset).expanduser().resolve()
    yaml_path   = dataset_dir / "dataset.yaml"

    if not yaml_path.exists():
        print(f"ERROR: dataset.yaml not found at {yaml_path}")
        print("Run convert_cml_to_yolo.py first.")
        sys.exit(1)

    try:
        from ultralytics import YOLO
    except ImportError:
        print("ERROR: ultralytics not found. Use:")
        print("  .venv-yolo/bin/python scripts/train_yolo.py ...")
        sys.exit(1)

    # Apply smoke-test overrides.
    epochs   = args.epochs
    batch    = args.batch
    rect     = True
    fraction = 1.0
    if args.smoke_test:
        epochs   = 3
        batch    = 16
        rect     = False    # rect needs many images to form valid batches
        fraction = 0.05     # 5% of 20K = ~1000 images → ~190 steps/epoch ≈ 3 min total
        print("SMOKE TEST MODE: 3 epochs, batch=16, 5% dataset fraction")

    run_name = args.name or f"{args.model}_e{epochs}"
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    model_id = f"{args.model}.pt"
    # Use local weights if available (downloaded by eval_yolo_zeroshot.py).
    local_weights = PROJECT_ROOT / "scripts" / model_id
    if local_weights.exists():
        model_arg = str(local_weights)
        print(f"Using local weights: {local_weights.relative_to(PROJECT_ROOT)}")
    else:
        model_arg = model_id
        print(f"Weights will be downloaded: {model_id}")

    print(f"\nTraining config:")
    print(f"  Model   : {args.model}")
    print(f"  Epochs  : {epochs}")
    print(f"  Imgsz   : {args.imgsz}")
    print(f"  Batch   : {'auto' if batch == -1 else batch}")
    print(f"  Rect    : {rect}")
    print(f"  Dataset : {yaml_path}")
    print(f"  Output  : {output_dir / run_name}")
    print()

    model = YOLO(model_arg)

    train_kwargs = dict(
        data        = str(yaml_path),
        epochs      = epochs,
        imgsz       = args.imgsz,
        batch       = batch,
        rect        = rect,
        fraction    = fraction,
        device      = "mps",        # Apple Silicon GPU
        workers     = args.workers,
        project     = str(output_dir),
        name        = run_name,
        exist_ok    = False,
        pretrained  = True,
        optimizer   = "AdamW",
        lr0         = 0.001,
        lrf         = 0.01,
        momentum    = 0.937,
        weight_decay= 0.0005,
        warmup_epochs    = 3.0,
        warmup_momentum  = 0.8,
        box          = 7.5,
        cls          = 0.5,
        dfl          = 1.5,
        hsv_h        = 0.015,
        hsv_s        = 0.7,
        hsv_v        = 0.4,
        degrees      = 0.0,      # no rotation (UI elements are always upright)
        translate    = 0.1,
        scale        = 0.5,
        shear        = 0.0,
        perspective  = 0.0,
        flipud       = 0.0,      # no vertical flip (UI has top/bottom meaning)
        fliplr       = 0.5,
        mosaic       = 1.0,
        mixup        = 0.0,
        copy_paste   = 0.0,
        verbose      = True,
    )

    if args.resume:
        train_kwargs["resume"] = True
        model_arg = args.resume
        model = YOLO(model_arg)

    results = model.train(**train_kwargs)

    best = output_dir / run_name / "weights" / "best.pt"
    print(f"\nTraining complete.")
    print(f"  Best weights : {best}")
    print(f"\nExport to CoreML with:")
    print(f"  .venv-yolo/bin/python scripts/export_yolo_coreml.py --weights {best}")


if __name__ == "__main__":
    main()
