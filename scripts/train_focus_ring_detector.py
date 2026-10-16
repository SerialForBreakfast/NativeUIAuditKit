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
import math
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
    p.add_argument("--experiment-arm", choices=["scratch-stretch", "warm-stretch", "scratch-aspect-fit", "warm-aspect-fit", "pretrained-stretch", "paired-stretch", "static-baseline", "static-human", "fit-diagnostic", "full-corpus-fit", "reviewed-full-fit", "native-body-dry-run", "native-body-full-fit", "context-local", "context-geometry", "context-scene", "visual-local-frozen", "visual-context-frozen", "visual-local-partial", "visual-context-partial", "artwork-readiness", "artwork-control-partial", "artwork-added-partial", "transfer-emphasis-partial", "transfer-aspect-partial", "native26-normalized", "native26-common", "transition-measurements", "transition-direct-pixels", "transition-candidate-ranker"])
    p._option_string_actions['--experiment-arm'].choices.append('transition-change-adaptation')
    p._option_string_actions['--experiment-arm'].choices.append('schema4-repair')
    return p.parse_args()


def load_samples(dataset: Path, split: str) -> list[dict]:
    manifest_path = dataset / "focus_dataset_manifest.json"
    if not manifest_path.is_file():
        raise ValueError("missing_manifest")
    data = json.loads(manifest_path.read_text())
    if data.get('version') in ('focus-transition-learning-v1', 'focus-transition-measurements-v1', 'focus-direct-transition-v1', 'focus-direct-corpus-v1'):
        raise ValueError('transition_requires_explicit_experiment_mode')
    if data.get('version') in ('focus-context-experiment-v1','focus-visual-experiment-v1','focus-artwork-experiment-v1','focus-transfer-experiment-v1'):
        raise ValueError('context_requires_explicit_experiment_mode')
    if data.get('version') == 'focus-native-body-full-fit-v1':
        raise ValueError('native_body_requires_explicit_experiment_mode')
    if data.get('version') == 'focus-native-body-assembly-v1':
        raise ValueError('native_body_requires_explicit_dry_run')
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
                "minimum-balanced-real-bce-guarded-earliest-tie",
                "minimum-retention-bce-floor-earliest-tie",
                "minimum-equal-source-validation-bce-retention-floor-earliest-tie"}
    return loss < best or (loss == best and configuration.get("selection") not in earliest)


def experiment_selection(predictions, rows, report):
    """Shared epoch/selected-checkpoint dispatch; also exercised without a model."""
    adapters = {"focus-appearance-preflight-v1": "focus_appearance_experiment",
                "focus-retention-preflight-v1": "focus_retention_experiment",
                "focus-representative-preflight-v1": "focus_representative_experiment"}
    name = adapters.get(report.get("formatVersion"))
    if name is None:
        return {}
    import importlib
    return importlib.import_module(name).selection_metrics(predictions, rows, report["selection"])


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


def train_native_hcf(rows, initialization, output, *, epochs=30, batch=16, seed=371, progress=None, profile='hcf',
                     selection='best-development', deduplicate=False, resume=None, stop_after_epoch=None):
    """Train the resident backbone on admitted crops. Keep audit rows out.

    selection='best-development' keeps the HCF371 behavior. selection='fixed-last' never uses development
    rows, so a later development comparison is not biased by checkpoint choice.
    deduplicate=True keeps 1 training row per (pixel hash, label), so repeated crops do not gain weight.
    """
    import random
    import numpy as np
    import torch
    from PIL import Image
    from torch import nn
    import hashlib
    if epochs != 30 or batch != 16 or any(r['role'] not in ('train', 'development') for r in rows):
        raise ValueError('hcf_training_contract')
    if (resume is not None or stop_after_epoch is not None) and selection != 'fixed-last':
        raise ValueError('hcf_resume_requires_fixed_last')
    if stop_after_epoch is not None and (type(stop_after_epoch) is not int or not 1 <= stop_after_epoch <= epochs):
        raise ValueError('hcf_stop_epoch')
    def file_hash(path):
        digest = hashlib.sha256()
        with Path(path).open('rb') as source:
            for chunk in iter(lambda: source.read(1024 * 1024), b''): digest.update(chunk)
        return digest.hexdigest()
    resume_contract = dict(version='hcf-crop-resume-v1', epochs=epochs, batch=batch, seed=seed,
        profile=profile, selection=selection, deduplicate=deduplicate,
        rows=[dict(row, actualSHA256=file_hash(row['path'])) for row in rows],
        initialization=file_hash(initialization), trainer=file_hash(__file__),
        backbone=file_hash(Path(__file__).with_name('focus_ring_backbone.py')),
        torchVersion=str(torch.__version__), numpyVersion=np.__version__, device='mps')
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
    torch.set_num_threads(2)
    if not torch.backends.mps.is_available():
        raise ValueError('hcf_requires_qualified_mps')
    device = torch.device('mps')
    model = load_mobilenetv4_conv_small()(pretrained=False, num_classes=1)
    model.load_state_dict(torch.load(initialization, map_location='cpu', weights_only=True)['state_dict'], strict=True)
    model.to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=3e-4)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=.5)
    if profile == 'balanced' or profile is None:
        train = [r for r in rows if r['role'] == 'train']
        development = [r for r in rows if r['role'] == 'development']
    else:
        train = [r for r in rows if r['role'] == 'train' and r['profile'] == profile]
        development = [r for r in rows if r['role'] == 'development' and r['profile'] == profile]
    if selection not in ('best-development', 'fixed-last'):
        raise ValueError('hcf_selection')
    if selection == 'fixed-last':
        development = []
    duplicates = 0
    if deduplicate:
        import hashlib
        unique = {}
        labels_by_pixel = {}
        for row in train:
            with Image.open(row['path']) as image:
                if image.size != (256, 256): raise ValueError('hcf_original_crop_size')
                pixels = hashlib.sha256(image.convert('RGB').tobytes()).hexdigest()
            if pixels in labels_by_pixel and labels_by_pixel[pixels] != row['label']:
                raise ValueError('hcf_duplicate_label_conflict')
            labels_by_pixel[pixels] = row['label']
            unique.setdefault((pixels, row['label']), row)
        duplicates, train = len(train) - len(unique), list(unique.values())
    if not train or (selection == 'best-development' and not development):
        raise ValueError('hcf_training_support')
    positive = sum(r['label'] for r in train)
    if not 0 < positive < len(train):
        raise ValueError('hcf_class_support')
    criterion = nn.BCEWithLogitsLoss(pos_weight=torch.tensor([(len(train)-positive)/positive], device=device))
    def tensors(selected):
        arrays = []
        for row in selected:
            with Image.open(row['path']) as image:
                if image.size != (256,256): raise ValueError('hcf_original_crop_size')
                arrays.append(np.array(image.convert('RGB'), copy=True))
        x = torch.from_numpy(np.stack(arrays)).permute(0,3,1,2).contiguous().float().div_(255).to(device)
        y = torch.tensor([r['label'] for r in selected], dtype=torch.float32, device=device)
        return x,y
    best, stale, history = float('inf'), 0, []
    first_epoch = 1
    if resume is not None:
        checkpoint = torch.load(resume, map_location='cpu', weights_only=False)
        if checkpoint.get('resumeContract') != resume_contract:
            raise ValueError('hcf_resume_contract_changed')
        required = {'state_dict','optimizer','scheduler','torchRNG','mpsRNG','pythonRNG','numpyRNG','history','stale','best','epoch'}
        if not required <= set(checkpoint): raise ValueError('hcf_resume_state_missing')
        completed = checkpoint['epoch']
        if type(completed) is not int or not 1 <= completed < epochs:
            raise ValueError('hcf_resume_epoch')
        history = checkpoint['history']
        if [r['epoch'] for r in history] != list(range(1, completed+1)):
            raise ValueError('hcf_resume_history')
        if stop_after_epoch is not None and stop_after_epoch <= completed:
            raise ValueError('hcf_resume_no_progress')
        model.load_state_dict(checkpoint['state_dict'], strict=True)
        optimizer.load_state_dict(checkpoint['optimizer'])
        scheduler.load_state_dict(checkpoint['scheduler'])
        torch.set_rng_state(checkpoint['torchRNG'])
        torch.mps.set_rng_state(checkpoint['mpsRNG'])
        random.setstate(checkpoint['pythonRNG']); np.random.set_state(checkpoint['numpyRNG'])
        best, stale = checkpoint['best'], checkpoint['stale']
        first_epoch = completed+1
    for epoch in range(first_epoch, epochs+1):
        model.train(); total = 0
        order = torch.randperm(len(train)).tolist()
        for start in range(0,len(order),batch):
            selected = [train[i] for i in order[start:start+batch]]
            # BatchNorm needs at least 2 examples at its final spatial stage.
            if len(selected) == 1: selected.append(selected[0])
            x,y = tensors(selected); optimizer.zero_grad()
            loss = criterion(model(x).reshape(-1), y)
            if not torch.isfinite(loss): raise ValueError('hcf_nonfinite_loss')
            loss.backward(); optimizer.step(); total += float(loss.item())*len(selected)
            if progress: progress(f'Train HCF crop model: epoch {epoch}/{epochs}', start+len(selected), len(train))
        model.eval(); validation = None
        if development:
            validation = 0
            with torch.no_grad():
                for start in range(0,len(development),batch):
                    x,y = tensors(development[start:start+batch])
                    validation += float(nn.functional.binary_cross_entropy_with_logits(model(x).reshape(-1), y).item())*len(y)
            validation /= len(development)
            if not math.isfinite(validation): raise ValueError('hcf_nonfinite_validation')
        scheduler.step()
        state = {k:v.detach().cpu() for k,v in model.state_dict().items()}
        history.append(dict(epoch=epoch, trainLoss=total/len(train), developmentLoss=validation))
        if selection == 'fixed-last':
            torch.save(dict(state_dict=state, epoch=epoch, model=MODEL_NAME), output/'final.pt')
        improved = validation is not None and validation < best
        if improved:
            best, stale = validation, 0
            torch.save(dict(state_dict=state, epoch=epoch, model=MODEL_NAME), output/'best.pt')
        elif validation is not None: stale += 1
        checkpoint = dict(resumeContract=resume_contract, state_dict=state, epoch=epoch, optimizer=optimizer.state_dict(), scheduler=scheduler.state_dict(),
            torchRNG=torch.get_rng_state(), mpsRNG=torch.mps.get_rng_state(), pythonRNG=random.getstate(),
            numpyRNG=np.random.get_state(), history=history, stale=stale, best=best)
        temporary = output/'last.partial'
        torch.save(checkpoint, temporary); temporary.replace(output/'last.pt')
        (output/'history.json').write_text(json.dumps(history, indent=2)+'\n')
        if stale >= 10: break
        if epoch == stop_after_epoch: break
    return dict(epochs=len(history), bestDevelopmentLoss=best if development else None, trainCrops=len(train),
        duplicateTrainRowsRemoved=duplicates, developmentCrops=len(development), selection=selection,
        earlyStopped=stale >= 10, resumeStateSaved=True, resumeQualified=False,
        resumedFromEpoch=first_epoch-1, boundaryStopped=len(history)<epochs and stale<10)


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
        if report.get("formatVersion") in {"focus-change-preflight-v1", "focus-ranking-preflight-v1", "focus-appearance-preflight-v1", "focus-retention-preflight-v1", "focus-representative-preflight-v1", "focus-transition-preflight-v1", "focus-direct-preflight-v1"}:
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
    if report.get('protocolVersion') == 'focus-change-adaptation-v1':
        from focus_change_adaptation import run as run_change
        return run_change(report,args.experiment_id)
    if report.get('protocolVersion') == 'focus-candidate-ranking-v1':
        from focus_candidate_ranker import run as run_ranking
        return run_ranking(report,args.experiment_id)
    if report.get('protocolVersion') == 'focus-direct-transition-v1':
        from focus_direct_transition import run as run_direct
        return run_direct(report,args.experiment_id)
    if report.get('protocolVersion') == 'focus-transition-learning-v1':
        from focus_transition_learning import run as run_transition
        return run_transition(report, args.experiment_id)
    deadline = started + report["configuration"]["maxSeconds"] if experimental else float("inf")
    for key, value in os_env_defaults.items():
        os.environ[key] = value
        Path(value).mkdir(parents=True, exist_ok=True)
    if report.get('protocolVersion') == 'native-focus-spike-model-v1':
        from native_focus_spike_model import run as run_native26
        return run_native26(report,args.experiment_id)
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
    if (report.get("staticHuman") or report.get("fitDiagnostic") or report.get("fullFit")) and device.type != "mps":
        raise ValueError("static_experiment_requires_mps_no_cpu_fallback")
    train_dataset = CropDataset(train, not experimental)
    val_dataset = CropDataset(val, False)
    if report.get('protocolVersion') == 'focus-transfer-experiment-v1':
        from focus_transfer_experiment import prepare_features
        model, train_dataset, val_dataset = prepare_features(report, train, val, device, out)
    elif report.get('protocolVersion') == 'focus-artwork-experiment-v1':
        from focus_artwork_experiment import prepare_features
        model, train_dataset, val_dataset = prepare_features(report, train, val, device, out)
    elif report.get('protocolVersion') == 'focus-visual-experiment-v1':
        from focus_visual_experiment import prepare_features
        model, train_dataset, val_dataset = prepare_features(report, train, val, device, out)
    elif report.get('protocolVersion') == 'focus-context-experiment-v1':
        from focus_context_experiment import prepare_features
        model, train_dataset, val_dataset = prepare_features(report, train, val, device, out)
    elif report.get('protocolVersion') == 'focus-native-body-full-fit-v1':
        from focus_native_body_experiment import prepare_features
        model, train_dataset, val_dataset = prepare_features(report, train, val, device, out)
    elif report.get('protocolVersion') == 'focus-reviewed-full-fit-v1':
        from focus_review_continuation import prepare_features
        model, train_dataset, val_dataset = prepare_features(report, train, val, device, out)
    elif report.get("fitDiagnostic") or report.get("fullFit"):
        from focus_fit_diagnostic import prepare_features
        model, train_dataset, val_dataset = prepare_features(report, train, val, device, out)
    elif report.get("pairedTraining"):
        from focus_paired_experiment import prepare_features
        print(f"device={device} reusing sealed features; no encoder loaded", flush=True)
        model, train_dataset, val_dataset = prepare_features(report, train, val, device, out)
    elif report.get("representation"):
        from focus_pretrained_experiment import prepare_features
        print(f"device={device} extracting frozen ImageNet features once", flush=True)
        model, train_dataset, val_dataset = prepare_features(report, train_dataset, val_dataset, device, deadline, out)
    else:
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
    if report.get("fullFit"):
        from focus_full_fit_experiment import run
        return run(model, train_dataset, val_dataset, report, train, val, device, out, started, deadline, args.experiment_id)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr)
    loss_fn = nn.BCEWithLogitsLoss()

    sampler = None
    if report.get("pairedTraining"):
        pair_config = report["pairedTraining"]
        sampler = WeightedRandomSampler([p["weight"] for p in pair_config["pairs"]], pair_config["draws"],
                                       replacement=True, generator=torch.Generator().manual_seed(42))
        batch = pair_config["pairBatch"]
    elif "sampling" in report and not report.get("staticHuman"):
        sampler = WeightedRandomSampler([r["samplingWeight"] for r in train], len(train), replacement=True,
                                       generator=torch.Generator().manual_seed(42))
    train_loader = DataLoader(
        train_dataset, batch_size=batch, shuffle=sampler is None and not report.get("fitDiagnostic"),
        sampler=sampler, num_workers=0, drop_last=False
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=max(2, min(batch, 32)),
        shuffle=False,
        num_workers=0,
    )

    best_val = float("inf")
    best_path = weights_dir / "best.pt"
    def evaluate(loader=None, rows=None, training_fit=False):
        loader = val_loader if loader is None else loader
        rows = val if rows is None else rows
        model.eval()
        predictions = []
        total_loss = 0.0
        count = 0
        with torch.no_grad():
            for x, y in loader:
                if time.monotonic() >= deadline: raise TimeoutError("experiment_compute_budget")
                x, y = x.to(device), y.to(device)
                logits = model(x)
                loss = loss_fn(logits.view_as(y), y)
                if not torch.isfinite(loss): raise ValueError("nonfinite_validation_loss")
                total_loss += float(loss.item()) * x.size(0)
                for probability, label in zip(torch.sigmoid(logits).view(-1).cpu().tolist(), y.view(-1).cpu().tolist()):
                    predictions.append({"id": rows[count].get("id", str(count)), "label": int(label), "probability": probability})
                    count += 1
        result = {"loss": total_loss / max(1, count), "predictions": predictions}
        if training_fit:
            from focus_fit_diagnostic import fit_metrics
            result.update(fit_metrics(predictions, rows, result["loss"]))
        else:
            result.update(experiment_selection(predictions, rows, report))
        return result
    history = []
    terminal_only = report.get('terminalOnly', False)
    initial = evaluate() if experimental and not terminal_only else None
    initial_fit = evaluate(train_loader, train, True) if report.get("fitDiagnostic") else None
    consecutive_fit = 0
    for epoch in range(1, epochs + 1):
        model.train()
        running = 0.0
        n = 0
        if report.get("staticHuman"):
            from focus_human_static_experiment import train_epoch
            running = train_epoch(model, train_dataset, report, epoch, device, opt, deadline)
            n = 1
        for x, y in (() if report.get("staticHuman") else train_loader):
            if time.monotonic() >= deadline: raise TimeoutError("experiment_compute_budget")
            x, y = x.to(device), y.to(device)
            opt.zero_grad()
            logits = model(x)
            if report.get("pairedTraining"):
                from focus_paired_experiment import paired_loss
                loss = paired_loss(logits, y)
            else:
                loss = loss_fn(logits.view_as(y), y)
            if not torch.isfinite(loss): raise ValueError("nonfinite_training_loss")
            loss.backward()
            if report.get("fitDiagnostic"):
                gradient_norm = sum(float(p.grad.detach().norm().item()) for p in model.parameters() if p.grad is not None)
                if not math.isfinite(gradient_norm): raise ValueError("nonfinite_fit_gradient")
            opt.step()
            running += float(loss.item()) * x.size(0)
            n += x.size(0)
        train_loss = running / max(1, n)

        if report.get("fitDiagnostic"):
            observation = evaluate(train_loader, train, True)
            consecutive_fit = consecutive_fit + 1 if observation["fitPass"] else 0
            done = consecutive_fit >= report["fitDiagnostic"]["consecutivePasses"] or epoch == epochs
            validation = evaluate() if done or epoch % 50 == 0 else None
            history.append(dict(epoch=epoch, trainLoss=train_loss, training=observation,
                                gradientNorm=gradient_norm, validation=validation))
            if validation is not None:
                print(f"fit update {epoch}/{epochs}: BCE={observation['loss']:.6f}, confident={observation['confidentCorrect']}/{len(train)}", flush=True)
                (out/"progress.json").write_text(json.dumps(dict(history=history,initial=initial,initialTraining=initial_fit),allow_nan=False))
            if done:
                torch.save(dict(epoch=epoch,model_name=args.model,state_dict=model.state_dict(),
                    checkpointKind="fit-diagnostic-not-selected",representation=report["representation"]),weights_dir/"last.pt")
                break
            continue
        validation = evaluate() if not terminal_only else {"loss": None, "predictions": [], "notAssessed": True}
        val_loss = validation.get("selectionLoss", validation["loss"])
        history.append({"epoch": epoch, "trainLoss": train_loss, "validation": validation})
        if report.get("staticHuman"):
            # Preserve each completed budget even if a subsequent deadline interrupts.
            (out/"progress.json").write_text(json.dumps(dict(history=history,initial=initial),allow_nan=False))
        validation_text = 'not assessed' if terminal_only else f'{val_loss:.4f}'
        print(f"epoch {epoch}/{epochs}  train_loss={train_loss:.4f}  val_loss={validation_text}", flush=True)
        ckpt = {
            "epoch": epoch,
            "model_name": args.model,
            "state_dict": model.state_dict(),
            "val_loss": val_loss,
        }
        if report.get("representation"):
            ckpt["representation"] = report["representation"]
            ckpt["checkpointKind"] = "frozen-pretrained-linear-head-v1"
        torch.save(ckpt, weights_dir / "last.pt")
        if (epoch == epochs if terminal_only else validation.get("checkpointEligible", True) and checkpoint_improved(val_loss, best_val, report["configuration"])):
            best_val = val_loss
            torch.save(ckpt, best_path)

    if report.get("fitDiagnostic"):
        from focus_pretrained_experiment import state_digest
        result=dict(status="diagnostic_completed",fitPassed=consecutive_fit >= report["fitDiagnostic"]["consecutivePasses"],
            releaseEligible=False,protocolSHA256=report["protocolSHA256"],history=history,initial=initial,
            initialTraining=initial_fit,experimentID=args.experiment_id,device=str(device),pid=os.getpid(),
            elapsedSeconds=time.monotonic()-started,torchVersion=str(torch.__version__),
            finalHeadSHA256=state_digest(model),
            stopReason="training_fit" if consecutive_fit >= report["fitDiagnostic"]["consecutivePasses"] else "update_cap")
        (out/"experiment-result.json").write_text(json.dumps(result,indent=2,allow_nan=False))
        print(f"Diagnostic complete: fitPassed={result['fitPassed']}; no selected/release checkpoint",flush=True)
        return 0
    if experimental:
        import hashlib
        if not best_path.exists():
            result = {"status":"failed_no_eligible_checkpoint","releaseEligible":False,
                      "protocolSHA256":report["protocolSHA256"],"selection":report.get("selection"),
                      "history":history,"initial":initial,"experimentID":args.experiment_id,
                      "elapsedSeconds":time.monotonic()-started}
            result.update(arm=args.experiment_arm, pid=os.getpid(), device=str(device),
                          torchVersion=str(torch.__version__), trainCount=len(train), validationCount=len(val))
            (out/"experiment-result.json").write_text(json.dumps(result,indent=2,allow_nan=False))
            print("ERROR: no checkpoint met the frozen retention floor; last.pt is not selected",file=sys.stderr)
            return 2
        model.load_state_dict(torch.load(best_path, map_location=device, weights_only=True)["state_dict"], strict=True)
        selected = evaluate() if not terminal_only else {"notAssessed": True, "selection": "fixed-last-epoch"}
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
