#!/usr/bin/env python3
"""
train_focus_ring_detector.py — Train MobileNetV4-Conv-Small as a binary focus classifier.

Reads `focus_dataset_manifest.json` produced by harvest_focus_pairs.py. Each focused
crop is label 1; each unfocused crop is label 0. Split assignment follows recipe_seed
in the manifest (pairs never straddle train/test).

Usage:
  .venv-yolo/bin/python scripts/train_focus_ring_detector.py --dry-run
  .venv-yolo/bin/python scripts/train_focus_ring_detector.py \\
      --dataset ../NativeUIAuditKit-Dataset/focus_ring --name fdr001
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
RUNS = PROJECT_ROOT / "NativeUITrainer" / "focus_ring_runs"
MODEL_NAME = "mobilenetv4_conv_small"
INPUT_SIZE = 256
BATCH_SIZE = 64
EPOCHS = 30
LR = 3e-4
HARD_THEMES = frozenset({"light", "highContrast"})
HARD_TYPES = frozenset({"imageView", "collectionItem"})


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", default=str(DEFAULT_DATASET))
    p.add_argument("--name", default=None)
    p.add_argument("--epochs", type=int, default=EPOCHS)
    p.add_argument("--batch", type=int, default=BATCH_SIZE)
    p.add_argument("--lr", type=float, default=LR)
    p.add_argument("--model", default=MODEL_NAME)
    p.add_argument("--dry-run", action="store_true", help="1 epoch, tiny batch, skip if no labeled crops")
    return p.parse_args()


def load_samples(dataset: Path, split: str) -> list[dict]:
    manifest_path = dataset / "focus_dataset_manifest.json"
    if not manifest_path.is_file():
        return []
    data = json.loads(manifest_path.read_text())
    samples: list[dict] = []
    for pair in data.get("pairs") or []:
        if pair.get("split") != split:
            continue
        focused = pair.get("focused_crop")
        unfocused = pair.get("unfocused_crop")
        meta = {
            "theme": pair.get("theme"),
            "element_type": pair.get("element_type"),
            "pair_id": pair.get("pair_id"),
        }
        if focused:
            samples.append({"path": dataset / focused, "label": 1.0, **meta})
        if unfocused:
            samples.append({"path": dataset / unfocused, "label": 0.0, **meta})
    return [s for s in samples if Path(s["path"]).is_file()]


def is_hard_negative(sample: dict) -> bool:
    return sample["label"] == 0.0 and sample.get("theme") in HARD_THEMES and sample.get("element_type") in HARD_TYPES


def load_mobilenetv4_conv_small():
    """
    Load the vendored MobileNetV4-Conv-Small.

    Do not `import timm` here. `timm.models.__init__` and `timm.layers.__init__`
    star-import FX / torchvision and hang in this venv (see BP-47).
    """
    import importlib.util

    path = Path(__file__).with_name("focus_ring_backbone.py")
    spec = importlib.util.spec_from_file_location("focus_ring_backbone", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"could not load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.mobilenetv4_conv_small


def main() -> int:
    args = parse_args()
    dataset = Path(args.dataset).expanduser()
    if not dataset.is_absolute():
        dataset = (PROJECT_ROOT / dataset).resolve()

    train = load_samples(dataset, "train")
    val = load_samples(dataset, "val")
    hard = [s for s in val + load_samples(dataset, "test") if is_hard_negative(s)]
    print(f"=== FocusRing train {utc_now()} ===")
    print(f"dataset: {dataset}")
    print(f"train={len(train)} val={len(val)} hard_neg={len(hard)}")

    if args.dry_run and not train:
        print("dry-run: no labeled train crops (Phase B harvest required). Script OK.")
        return 0
    if not train:
        print("ERROR: no labeled train crops. Run harvest with sidecar isFocused labels or --live.")
        return 1

    print("importing torch…", flush=True)
    import torch
    from torch import nn
    from torch.utils.data import DataLoader, Dataset
    from PIL import Image
    print("torch ready", flush=True)

    try:
        print("loading MobileNetV4-Conv-Small (vendored, no timm)…", flush=True)
        mobilenetv4_conv_small = load_mobilenetv4_conv_small()
        print("factory ready", flush=True)
    except Exception as exc:
        print(f"ERROR: could not load timm MobileNetV4 ({exc})")
        return 1

    class CropDataset(Dataset):
        def __init__(self, rows: list[dict], augment: bool):
            self.rows = rows
            self.augment = augment

        def __len__(self) -> int:
            return len(self.rows)

        def __getitem__(self, idx: int):
            import random
            import numpy as np

            row = self.rows[idx]
            img = Image.open(row["path"]).convert("RGB").resize((INPUT_SIZE, INPUT_SIZE), Image.Resampling.BILINEAR)
            if self.augment and random.random() < 0.5:
                img = img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            x = torch.from_numpy(np.array(img, copy=True)).permute(2, 0, 1).float().div_(255.0)
            y = torch.tensor([row["label"]], dtype=torch.float32)
            return x, y

    epochs = 1 if args.dry_run else args.epochs
    batch = min(4, args.batch) if args.dry_run else args.batch
    run_name = args.name or ("fdr_dryrun" if args.dry_run else datetime.now(timezone.utc).strftime("fdr_%Y%m%dT%H%M%SZ"))
    out = RUNS / run_name
    weights_dir = out / "weights"
    weights_dir.mkdir(parents=True, exist_ok=True)

    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    print(f"device={device}  creating {args.model} pretrained=False (HF hub skipped)", flush=True)
    model = mobilenetv4_conv_small(pretrained=False, num_classes=1)
    print("model ready", flush=True)
    model.to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr)
    loss_fn = nn.BCEWithLogitsLoss()

    train_loader = DataLoader(
        CropDataset(train, True), batch_size=batch, shuffle=True, num_workers=0, drop_last=True
    )
    val_loader = DataLoader(
        CropDataset(val or train[: min(8, len(train))], False),
        batch_size=max(2, min(batch, 32)),
        shuffle=False,
        num_workers=0,
    )

    best_val = float("inf")
    best_path = weights_dir / "best.pt"
    for epoch in range(1, epochs + 1):
        model.train()
        running = 0.0
        n = 0
        for x, y in train_loader:
            x, y = x.to(device), y.to(device)
            opt.zero_grad()
            logits = model(x)
            loss = loss_fn(logits.view_as(y), y)
            loss.backward()
            opt.step()
            running += float(loss.item()) * x.size(0)
            n += x.size(0)
        train_loss = running / max(1, n)

        model.eval()
        vloss = 0.0
        vn = 0
        with torch.no_grad():
            for x, y in val_loader:
                x, y = x.to(device), y.to(device)
                logits = model(x)
                loss = loss_fn(logits.view_as(y), y)
                vloss += float(loss.item()) * x.size(0)
                vn += x.size(0)
        val_loss = vloss / max(1, vn)
        print(f"epoch {epoch}/{epochs}  train_loss={train_loss:.4f}  val_loss={val_loss:.4f}")
        ckpt = {
            "epoch": epoch,
            "model_name": args.model,
            "state_dict": model.state_dict(),
            "val_loss": val_loss,
        }
        torch.save(ckpt, weights_dir / "last.pt")
        if val_loss <= best_val:
            best_val = val_loss
            torch.save(ckpt, best_path)

        if hard:
            hard_loader = DataLoader(CropDataset(hard, False), batch_size=batch, shuffle=False, num_workers=0)
            fp = 0
            total = 0
            with torch.no_grad():
                for x, y in hard_loader:
                    x = x.to(device)
                    prob = torch.sigmoid(model(x).view(-1))
                    fp += int((prob >= 0.85).sum().item())
                    total += x.size(0)
            fpr = fp / max(1, total)
            print(f"  hard-negative FPR@0.85={fpr:.4f} ({fp}/{total})")

    print(f"best.pt → {best_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
