"""WSP-02 & WSP-03: Weight-Space Programming for FocusRing Detector.

Implements closed-form weight-space task vector arithmetic (ADR-0033) between
fdr001 (baseline anchor), fdr003 (pill sensitivity), and fdr014 (false positive suppression).
Evaluates on the REALAPP554 focus development set without backpropagation.
"""
import sys
import copy
from pathlib import Path
import json
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import research_queue as q
import focus_candidates556 as fc
from eval_focus_ring_detector import predict_torch

RUNS = q.ROOT / 'NativeUITrainer/focus_ring_runs'
FDR001_PATH = RUNS / 'fdr001/weights/best.pt'
FDR003_PATH = RUNS / 'fdr003-scratch-stretch/weights/last.pt'
FDR014_PATH = RUNS / 'fdr014-appearance-sampling-mps/weights/last.pt'
OUTPUT_DIR = q.ROOT / 'reports/work/WSP'

def load_ckpt(path):
    return torch.load(path, map_location='cpu')

def blend_state_dicts(base_sd, v1_sd, v2_sd, alpha=0.0, beta=0.0, delta_b=0.0):
    """Compute theta* = base + alpha*(v1 - base) + beta*(v2 - base), with optional delta_b."""
    out_sd = copy.deepcopy(base_sd)
    for k in base_sd.keys():
        if not torch.is_floating_point(base_sd[k]):
            continue
        # Task vector arithmetic
        tau1 = v1_sd[k] - base_sd[k]
        tau2 = v2_sd[k] - base_sd[k]
        out_sd[k] = base_sd[k] + alpha * tau1 + beta * tau2
    
    if delta_b != 0.0 and 'classifier.bias' in out_sd:
        out_sd['classifier.bias'] = out_sd['classifier.bias'] + delta_b
    return out_sd

def main():
    torch.set_num_threads(4)
    print("Loading base and expert checkpoints...")
    ckpt0 = load_ckpt(FDR001_PATH)
    ckpt3 = load_ckpt(FDR003_PATH)
    ckpt14 = load_ckpt(FDR014_PATH)

    sd0 = ckpt0['state_dict']
    sd3 = ckpt3['state_dict']
    sd14 = ckpt14['state_dict']

    print("Loading dev items and crops...")
    rows, batch = fc.items()
    paths = fc.crops(batch)
    keys = [b['id'] for b in batch]
    crop_dicts = [dict(path=paths[k]) for k in keys]

    # Baseline scores
    print("\n--- Baseline FDR-001 ---")
    base_scores = dict(zip(keys, predict_torch(FDR001_PATH, crop_dicts)))
    base_m = fc.measure(rows, base_scores)
    print("FDR-001 baseline:", base_m)

    # Grid search over weight-space blend coefficients
    trials = [
        # (alpha for fdr003, beta for fdr014, delta_b)
        (0.0, 0.0, 0.5),   # WSP-02 pure bias shift
        (0.0, 0.0, 1.0),
        (0.0, 0.0, 1.5),
        (0.1, 0.0, 0.0),   # WSP-03 partial task vectors
        (0.2, 0.0, 0.0),
        (0.3, 0.0, 0.0),
        (0.5, 0.0, 0.0),
        (0.0, 0.2, 0.0),
        (0.0, 0.5, 0.0),
        (0.2, 0.2, 0.0),   # dual task vector fusion
        (0.3, 0.3, 0.0),
        (0.2, 0.4, 0.0),
        (0.3, 0.2, 0.5),   # fused vector + bias calibration
        (0.2, 0.3, 0.5),
    ]

    results = []
    tmp_ckpt_path = q.ROOT / '.build/debug-output/wsp_trial.pt'
    tmp_ckpt_path.parent.mkdir(parents=True, exist_ok=True)

    print("\nEvaluating WSP Weight Blends...")
    print(f"{'alpha':<6} {'beta':<6} {'delta_b':<8} {'D1':<4} {'Pills>0':<8} {'D2':<4} {'D3':<4} {'FalseHigh':<10}")
    print("-" * 55)

    for alpha, beta, db in trials:
        trial_sd = blend_state_dicts(sd0, sd3, sd14, alpha=alpha, beta=beta, delta_b=db)
        trial_ckpt = copy.deepcopy(ckpt0)
        trial_ckpt['state_dict'] = trial_sd
        torch.save(trial_ckpt, tmp_ckpt_path)

        scores = dict(zip(keys, predict_torch(tmp_ckpt_path, crop_dicts)))
        m = fc.measure(rows, scores)
        print(f"{alpha:<6.2f} {beta:<6.2f} {db:<8.2f} {m['D1']:<4} {m['newstvPillsAbove001']:<8} {m['D2']:<4} {m['D3']:<4} {m['falseHigh']:<10}")
        results.append({
            'alpha': alpha,
            'beta': beta,
            'delta_b': db,
            'metrics': m
        })

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_json = OUTPUT_DIR / 'wsp-focus-results.json'
    with open(out_json, 'w') as f:
        json.dump({
            'baseline': base_m,
            'trials': results
        }, f, indent=2)
    print(f"\nSaved WSP results to {out_json}")

if __name__ == '__main__':
    main()
