#!/usr/bin/env python3
"""
train_focus_ring_detector.py — Train MobileNetV4-Conv-Small as a binary focus classifier.

Reads `focus_dataset_manifest.json` produced by harvest_focus_pairs.py. Each focused
crop is label 1; each unfocused crop is label 0. Split assignment follows recipe_seed
in the manifest (pairs never straddle train/test).

Usage:
  .venv-yolo/bin/python scripts/train_focus_ring_detector.py --dry-run
  .venv-yolo/bin/python scripts/train_focus_ring_detector.py \\
      --dataset dataset/focus_ring/QUALIFIED_CORPUS --name NEW_RUN --preflight

Execution additionally requires --execute --experiment-id LOGGED_ID and separate
maintainer authorization. Historical v1.0 crops require requalification, not relabeling.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
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

DEFAULT_DATASET = PROJECT_ROOT / "dataset" / "focus_ring"
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
    p.add_argument("--dry-run", action="store_true", help="Alias for side-effect-free preflight; never trains")
    p.add_argument("--preflight", action="store_true", help="Validate only; no model imports or writes")
    p.add_argument("--execute", action="store_true", help="Launch only after separate maintainer authorization and logged experiment")
    p.add_argument("--experiment-id", help="Exact logged run ID required for execution")
    p.add_argument("--experiment-protocol", type=Path, help="Separately reviewed small learning experiment; never release qualification")
    p.add_argument("--experiment-approval", type=Path, help="Maintainer decision bound to mixed-development protocol, arm and output")
    p.add_argument("--experiment-arm", choices=["scratch-stretch", "warm-stretch", "scratch-aspect-fit", "warm-aspect-fit"])
    return p.parse_args()


def load_samples(dataset: Path, split: str) -> list[dict]:
    manifest_path = dataset / "focus_dataset_manifest.json"
    if not manifest_path.is_file():
        raise ValueError("missing_manifest")
    data = json.loads(manifest_path.read_text())
    if data.get("version") == "focus-mixed-assembly-v1":
        from focus_mixed_assembly import load_samples as mixed_samples
        return mixed_samples(dataset, {"val":"validation"}.get(split,split))
    samples: list[dict] = []
    for pair in data.get("pairs") or []:
        from focus_dataset_contract import SPLITS, member
        if SPLITS.get(pair.get("split")) != SPLITS.get(split):
            continue
        focused = pair.get("focused_crop")
        unfocused = pair.get("unfocused_crop")
        meta = {
            "theme": pair.get("theme"),
            "element_type": pair.get("element_type"),
            "pair_id": pair.get("pair_id"),
        }
        if focused:
            samples.append({"path": member(dataset, focused), "label": 1.0, **meta})
        if unfocused:
            samples.append({"path": member(dataset, unfocused), "label": 0.0, **meta})
        if not focused or not unfocused:
            raise ValueError("incomplete_pair")
    return samples


def is_hard_negative(sample: dict) -> bool:
    return sample["label"] == 0.0 and sample.get("theme") in HARD_THEMES and sample.get("element_type") in HARD_TYPES


def checkpoint_improved(loss, best, configuration):
    earliest = {"minimum-native-validation-bce-earliest-tie",
                "minimum-equal-source-validation-bce-retention-floor-earliest-tie"}
    return loss < best or (loss == best and configuration.get("selection") not in earliest)


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

    experimental = args.experiment_protocol is not None
    experiment_rows = None
    if experimental:
        from focus_learning_experiment import load_protocol
        try:
            report, experiment_rows = load_protocol(args.experiment_protocol, args.experiment_arm, args.name, args.experiment_approval)
        except (OSError, ValueError, KeyError, TypeError) as error:
            print(json.dumps({"launchEligible": False, "blockers": [str(error)]})); return 2
        if report.get("formatVersion") == "focus-appearance-preflight-v1":
            for flag, field in (("--epochs","epochs"),("--batch","batch"),("--lr","lr"),("--model","model")):
                if any(x == flag or x.startswith(flag+"=") for x in sys.argv[1:]) and getattr(args,field) != report["configuration"][field]:
                    print(json.dumps({"launchEligible":False,"blockers":["protocol_configuration_override"]})); return 2
        args.epochs = report["configuration"]["epochs"]
        args.batch = report["configuration"]["batch"]
        args.lr = report["configuration"]["lr"]
        args.model = report["configuration"]["model"]
    else:
        if args.experiment_arm or args.experiment_approval:
            print("ERROR: experiment arm requires a protocol", file=sys.stderr); return 2
        from focus_training_preflight import preflight
        report = preflight(dataset, args.name, args.epochs, args.batch, args.lr, args.model)
    print(json.dumps(report, sort_keys=True))
    if args.dry_run or args.preflight or not args.execute:
        return 0 if report["launchEligible"] else 2
    if not report["launchEligible"]:
        return 2
    if not args.experiment_id or f"## Run {args.experiment_id} " not in (PROJECT_ROOT / "Research/ExperimentLog.md").read_text():
        print("ERROR: explicit experiment-log entry required", file=sys.stderr)
        return 2
    if experimental:
        entry = (PROJECT_ROOT / "Research/ExperimentLog.md").read_text().split(f"## Run {args.experiment_id} ", 1)[1].split("\n## Run ", 1)[0]
        if report["protocolSHA256"] not in entry or args.experiment_arm not in entry or args.name not in entry:
            print("ERROR: experiment log must bind exact protocol, arm and output", file=sys.stderr); return 2
        if report.get("approval"):
            from focus_mixed_assembly import checked
            checked(report["approval"])
            checked(report["protocolFile"])
    if "assemblySHA256" in report:
        entry = (PROJECT_ROOT / "Research/ExperimentLog.md").read_text().split(f"## Run {args.experiment_id} ",1)[1].split("\n## Run ",1)[0]
        if report["assemblySHA256"] not in entry or args.name not in entry:
            print("ERROR: experiment log must bind exact assembly and output",file=sys.stderr); return 2
        from focus_dataset_contract import digest
        if digest(json.loads((dataset/"focus_dataset_manifest.json").read_text())) != report["manifestSHA256"]:
            print("ERROR: assembly changed after preflight",file=sys.stderr); return 2
    started = time.monotonic()
    deadline = started + report["configuration"]["maxSeconds"] if experimental else float("inf")
    for key, value in os_env_defaults.items():
        os.environ[key] = value
        Path(value).mkdir(parents=True, exist_ok=True)
    train = [r for r in experiment_rows if r["split"] == "train"] if experimental else load_samples(dataset, "train")
    val = [r for r in experiment_rows if r["split"] == "validation"] if experimental else load_samples(dataset, "validation")
    print(f"=== FocusRing train {utc_now()} ===")
    print(f"dataset: {dataset}")
    print(f"train={len(train)} val={len(val)}; final test is not loaded for training")

    if not train:
        print("ERROR: no labeled train crops. Run harvest with sidecar isFocused labels or --live.")
        return 1

    print("importing torch…", flush=True)
    import torch
    from torch import nn
    from torch.utils.data import DataLoader, Dataset, WeightedRandomSampler
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

    epochs = args.epochs
    batch = args.batch
    run_name = args.name
    out = RUNS / run_name
    weights_dir = out / "weights"
    out.mkdir(parents=True, exist_ok=False)
    weights_dir.mkdir()
    (out / "preflight.json").write_text(json.dumps(report, indent=2) + "\n")
    import random
    random.seed(42)
    torch.manual_seed(42)

    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    print(f"device={device}  creating {args.model} pretrained=False (HF hub skipped)", flush=True)
    model = mobilenetv4_conv_small(pretrained=False, num_classes=1)
    if experimental and report["warmCheckpoint"]:
        from focus_learning_experiment import checked
        checkpoint = torch.load(checked(report["warmCheckpoint"]), map_location="cpu", weights_only=True)
        state = checkpoint["state_dict"]
        if any(not torch.isfinite(value).all() for value in state.values()):
            raise ValueError("nonfinite_checkpoint")
        model.load_state_dict(state, strict=True)
    print("model ready", flush=True)
    model.to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr)
    loss_fn = nn.BCEWithLogitsLoss()

    sampler = None
    if "sampling" in report:
        sampler = WeightedRandomSampler([r["samplingWeight"] for r in train], len(train), replacement=True,
                                       generator=torch.Generator().manual_seed(42))
    train_loader = DataLoader(
        CropDataset(train, not experimental), batch_size=batch, shuffle=sampler is None,
        sampler=sampler, num_workers=0, drop_last=False
    )
    val_loader = DataLoader(
        CropDataset(val, False),
        batch_size=max(2, min(batch, 32)),
        shuffle=False,
        num_workers=0,
    )

    best_val = float("inf")
    best_path = weights_dir / "best.pt"
    def evaluate():
        model.eval()
        predictions = []
        total_loss = 0.0
        count = 0
        with torch.no_grad():
            for x, y in val_loader:
                if time.monotonic() >= deadline: raise TimeoutError("experiment_compute_budget")
                x, y = x.to(device), y.to(device)
                logits = model(x)
                loss = loss_fn(logits.view_as(y), y)
                if not torch.isfinite(loss): raise ValueError("nonfinite_validation_loss")
                total_loss += float(loss.item()) * x.size(0)
                for probability, label in zip(torch.sigmoid(logits).view(-1).cpu().tolist(), y.view(-1).cpu().tolist()):
                    predictions.append({"id": val[count].get("id", str(count)), "label": int(label), "probability": probability})
                    count += 1
        result = {"loss": total_loss / max(1, count), "predictions": predictions}
        if report.get("formatVersion") == "focus-appearance-preflight-v1":
            from focus_appearance_experiment import selection_metrics
            result.update(selection_metrics(predictions,val,report["selection"]))
        return result
    history = []
    initial = evaluate() if experimental else None
    for epoch in range(1, epochs + 1):
        model.train()
        running = 0.0
        n = 0
        for x, y in train_loader:
            if time.monotonic() >= deadline: raise TimeoutError("experiment_compute_budget")
            x, y = x.to(device), y.to(device)
            opt.zero_grad()
            logits = model(x)
            loss = loss_fn(logits.view_as(y), y)
            if not torch.isfinite(loss): raise ValueError("nonfinite_training_loss")
            loss.backward()
            opt.step()
            running += float(loss.item()) * x.size(0)
            n += x.size(0)
        train_loss = running / max(1, n)

        validation = evaluate()
        val_loss = validation.get("selectionLoss", validation["loss"])
        history.append({"epoch": epoch, "trainLoss": train_loss, "validation": validation})
        print(f"epoch {epoch}/{epochs}  train_loss={train_loss:.4f}  val_loss={val_loss:.4f}")
        ckpt = {
            "epoch": epoch,
            "model_name": args.model,
            "state_dict": model.state_dict(),
            "val_loss": val_loss,
        }
        torch.save(ckpt, weights_dir / "last.pt")
        if validation.get("checkpointEligible", True) and checkpoint_improved(val_loss, best_val, report["configuration"]):
            best_val = val_loss
            torch.save(ckpt, best_path)

    if experimental:
        import hashlib
        if not best_path.exists():
            result = {"status":"failed_no_eligible_checkpoint","releaseEligible":False,
                      "protocolSHA256":report["protocolSHA256"],"selection":report.get("selection"),
                      "history":history,"initial":initial,"experimentID":args.experiment_id,
                      "elapsedSeconds":time.monotonic()-started}
            (out/"experiment-result.json").write_text(json.dumps(result,indent=2,allow_nan=False))
            print("ERROR: no checkpoint met the frozen retention floor; last.pt is not selected",file=sys.stderr)
            return 2
        model.load_state_dict(torch.load(best_path, map_location=device, weights_only=True)["state_dict"], strict=True)
        selected = evaluate()
        result = {"status": "completed", "releaseEligible": False, "protocolSHA256": report["protocolSHA256"],
                  "arm": args.experiment_arm, "experimentID": args.experiment_id, "pid": os.getpid(),
                  "endedAt": utc_now(), "elapsedSeconds": time.monotonic()-started,
                  "device": str(device), "torchVersion": str(torch.__version__),
                  "trainerSHA256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  "backboneSHA256": hashlib.sha256(Path(__file__).with_name("focus_ring_backbone.py").read_bytes()).hexdigest(),
                  "trainCount": len(train), "validationCount": len(val), "initial": initial,
                  "selected": selected, "history": history, "bestSHA256": hashlib.sha256(best_path.read_bytes()).hexdigest()}
        (out/"experiment-result.json").write_text(json.dumps(result, indent=2, allow_nan=False))

    print(f"best.pt → {best_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
