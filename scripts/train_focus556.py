"""Train FOCUS556 FocusRing models F1 (control replay) and F2 (all S2 + replay).
Evaluates R1 (270 legacy retention) and D1-D3 (21 real-app dev frames).
Bound by standing training authority: <= 30 epochs, <= 30 min, <= 2 GiB per fit.
"""
import sys
import os
import time
import json
import random
from pathlib import Path
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import research_queue as q
import focus_candidates556 as fc
from eval_focus_ring_detector import load_split, metrics, predict_torch
import torch
import torch.nn as nn

PROJECT_ROOT = q.ROOT
RUNS_DIR = PROJECT_ROOT / 'NativeUITrainer/focus_ring_runs'
FDR001_WEIGHTS = RUNS_DIR / 'fdr001/weights/best.pt'
CORPUS_MANIFEST = PROJECT_ROOT / 'dataset/focus_ring/focus556_corpus/focus_dataset_manifest.json'
REPORTS_DIR = PROJECT_ROOT / 'reports/work/FOCUS556'

def load_mobilenetv4():
    import importlib.util
    path = Path(__file__).resolve().parent / "focus_ring_backbone.py"
    spec = importlib.util.spec_from_file_location("focus_ring_backbone", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.mobilenetv4_conv_small(pretrained=False, num_classes=1)

def build_samples(run_name):
    with open(CORPUS_MANIFEST) as f:
        data = json.load(f)
    
    samples = []
    for pair in data['pairs']:
        if pair['split'] != 'train':
            continue
        if run_name == 'F1' and pair['source'] != 'fdr038_legacy_replay' and pair['source'] != 'fdr038_procedural_artwork':
            continue # F1 uses replay data only
        
        f_path = PROJECT_ROOT / 'dataset/focus_ring/focus556_corpus' / pair['focused_crop']
        u_path = PROJECT_ROOT / 'dataset/focus_ring/focus556_corpus' / pair['unfocused_crop']
        
        samples.append({'path': str(f_path), 'label': 1.0, 'pair_id': pair['pair_id']})
        samples.append({'path': str(u_path), 'label': 0.0, 'pair_id': pair['pair_id']})
        
    return samples

def train_model(run_name, out_dir, epochs=30, batch_size=64, lr=3e-5, seed=42, *, samples=None, initialization=None, epoch_callback=None):
    print(f"\n================ STARTING {run_name} TRAINING ================")
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)

    device = torch.device('mps' if torch.backends.mps.is_available() else 'cpu')
    print(f"Device: {device}")

    samples = build_samples(run_name) if samples is None else list(samples)
    print(f"Training samples: {len(samples)} crops ({len(samples)//2} pairs)")

    model = load_mobilenetv4()
    initial_path = FDR001_WEIGHTS if initialization is None else initialization
    print(f"Loading initial weights from {initial_path}...")
    fdr001_ckpt = torch.load(initial_path, map_location='cpu', weights_only=True)
    sd = fdr001_ckpt['state_dict'] if 'state_dict' in fdr001_ckpt else fdr001_ckpt
    model.load_state_dict(sd, strict=True)
    model.to(device)

    # Pre-load images into memory
    images = []
    labels = []
    for s in samples:
        with Image.open(s['path']) as im:
            images.append(np.array(im.convert('RGB'), copy=True))
            labels.append(s['label'])
    
    x_train = torch.from_numpy(np.stack(images)).permute(0, 3, 1, 2).contiguous().float().div_(255.0)
    y_train = torch.tensor(labels, dtype=torch.float32)

    optimizer = torch.optim.AdamW(model.parameters(), lr=lr)
    criterion = nn.BCEWithLogitsLoss()

    start_time = time.monotonic()
    dataset_size = len(samples)

    for epoch in range(1, epochs + 1):
        model.train()
        permutation = torch.randperm(dataset_size)
        epoch_loss = 0.0
        batches = 0

        for i in range(0, dataset_size, batch_size):
            indices = permutation[i:i + batch_size]
            bx = x_train[indices].to(device)
            by = y_train[indices].to(device)

            optimizer.zero_grad()
            logits = model(bx).squeeze(-1)
            loss = criterion(logits, by)
            loss.backward()
            optimizer.step()

            epoch_loss += loss.item() * len(indices)
            batches += 1

        avg_loss = epoch_loss / dataset_size
        if epoch_callback is not None:epoch_callback(epoch,avg_loss)
        if epoch % 5 == 0 or epoch == epochs:
            print(f"Epoch {epoch:2d}/{epochs:2d} | Loss: {avg_loss:.4f} | Elapsed: {time.monotonic() - start_time:.1f}s")

    elapsed = time.monotonic() - start_time
    print(f"Training completed in {elapsed:.2f} s.")

    # Save checkpoint
    out_dir.mkdir(parents=True, exist_ok=True)
    weights_dir = out_dir / 'weights'
    weights_dir.mkdir(parents=True, exist_ok=True)
    ckpt_path = weights_dir / 'best.pt'
    
    torch.save({
        'state_dict': model.state_dict(),
        'epoch': epochs,
        'loss': avg_loss,
        'elapsed': elapsed,
        'run_name': run_name
    }, ckpt_path)
    print(f"Saved weights to {ckpt_path} (size={ckpt_path.stat().st_size} bytes)")
    return ckpt_path

def evaluate_checkpoint(ckpt_path, run_name):
    print(f"\n--- Evaluating {run_name} on Legacy 270 Retention (R1) ---")
    test_crops = load_split(PROJECT_ROOT / 'dataset/focus_ring', 'test')
    test_scores = predict_torch(ckpt_path, test_crops)
    r1 = metrics(test_crops, test_scores)
    correct = r1['tp'] + r1['tn']
    total = r1['n']
    print(f"R1 (Legacy 270): {correct}/{total} correct (FN={r1['fn']}, FP={r1['fp']})")

    print(f"\n--- Evaluating {run_name} on Real-App Development Set (D1-D3) ---")
    rows, batch = fc.items()
    paths = fc.crops(batch)
    keys = [b['id'] for b in batch]
    dev_crops = [dict(path=paths[k]) for k in keys]
    dev_scores_list = predict_torch(ckpt_path, dev_crops)
    dev_scores = dict(zip(keys, dev_scores_list))
    d_metrics = fc.measure(rows, dev_scores)
    print(f"D1 (Focus box >= 0.85): {d_metrics['D1']}/21 (gate >= 12)")
    print(f"NewsTV Pills > 0.01: {d_metrics['newstvPillsAbove001']}/10 (gate >= 5)")
    print(f"D2 (Frames with >= 2 high cand): {d_metrics['D2']}/21 (gate <= 8)")
    print(f"D3 (Exact correct selection): {d_metrics['D3']}/21 (gate >= 5)")
    print(f"False Highs: {d_metrics['falseHigh']}/{d_metrics['negatives']}")

    return {
        'run': run_name,
        'checkpoint': str(ckpt_path.relative_to(PROJECT_ROOT)),
        'R1_correct': correct,
        'R1_total': total,
        'R1_fn': r1['fn'],
        'R1_fp': r1['fp'],
        'D1': d_metrics['D1'],
        'newstv_pills_gt_001': d_metrics['newstvPillsAbove001'],
        'D2': d_metrics['D2'],
        'D3': d_metrics['D3'],
        'false_high': d_metrics['falseHigh'],
        'negatives': d_metrics['negatives']
    }

def main():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Train F1 (Control Replay)
    f1_dir = RUNS_DIR / 'focus556-f1-replay'
    f1_ckpt = train_model('F1', f1_dir, epochs=30, batch_size=64, lr=3e-5)
    f1_eval = evaluate_checkpoint(f1_ckpt, 'F1')

    # Train F2 (Full Corpus: S2 + Replay)
    f2_dir = RUNS_DIR / 'focus556-f2-all'
    f2_ckpt = train_model('F2', f2_dir, epochs=30, batch_size=64, lr=3e-5)
    f2_eval = evaluate_checkpoint(f2_ckpt, 'F2')

    summary = {
        'evaluation_date': '2026-11-03',
        'authority': 'Tasks.md:RA554-16,Research/Plans/FocusRealApp556.md:S4',
        'models': {
            'F1_control_replay': f1_eval,
            'F2_full_corpus': f2_eval
        }
    }

    out_file = REPORTS_DIR / 'focus556-s4-results.json'
    with open(out_file, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"\nSaved S4 results to {out_file.relative_to(PROJECT_ROOT)}")

if __name__ == '__main__':
    main()
