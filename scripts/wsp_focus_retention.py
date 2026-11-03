"""WSP-04: Retention Guard and Precision Tuning for Weight-Space Focus Models.

Evaluates base FDR-001 vs task-vector blended checkpoints across:
1. The 270-crop legacy retention benchmark (must achieve zero regressions / 270 correct).
2. The REALAPP554 focus development set (10 NewsTV pill frames + false positive checks).
Includes layer-selective blending and magnitude pruning (ADR-0033).
"""
import sys
import copy
from pathlib import Path
import json
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import research_queue as q
import focus_candidates556 as fc
from eval_focus_ring_detector import load_split, metrics, predict_torch

RUNS = q.ROOT / 'NativeUITrainer/focus_ring_runs'
FDR001_PATH = RUNS / 'fdr001/weights/best.pt'
FDR003_PATH = RUNS / 'fdr003-scratch-stretch/weights/last.pt'
FDR014_PATH = RUNS / 'fdr014-appearance-sampling-mps/weights/last.pt'
OUTPUT_DIR = q.ROOT / 'reports/work/WSP'
TMP_CKPT = q.ROOT / '.build/debug-output/wsp_retention_trial.pt'

def load_ckpt(path):
    return torch.load(path, map_location='cpu')

def blend_weights(base_sd, v_pill, v_neg, alpha=0.0, beta=0.0, delta_b=0.0, top_k_ratio=1.0, layers_filter=None):
    """Blend weights with optional magnitude pruning (top_k_ratio) and layer filtering."""
    out = copy.deepcopy(base_sd)
    for k in base_sd.keys():
        if not torch.is_floating_point(base_sd[k]):
            continue
        if layers_filter and not any(f in k for f in layers_filter):
            continue

        tau1 = v_pill[k] - base_sd[k] if alpha != 0.0 else torch.zeros_like(base_sd[k])
        tau2 = v_neg[k] - base_sd[k] if beta != 0.0 else torch.zeros_like(base_sd[k])
        tau = alpha * tau1 + beta * tau2

        if top_k_ratio < 1.0 and tau.numel() > 10:
            k_val = max(1, int(tau.numel() * top_k_ratio))
            threshold = torch.topk(tau.abs().flatten(), k_val).values[-1]
            tau = torch.where(tau.abs() >= threshold, tau, torch.zeros_like(tau))

        out[k] = base_sd[k] + tau

    if delta_b != 0.0 and 'classifier.bias' in out:
        out['classifier.bias'] = out['classifier.bias'] + delta_b
    return out

def main():
    torch.set_num_threads(4)
    TMP_CKPT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading test split (270 legacy crops)...")
    test_rows = load_split(q.ROOT / 'dataset/focus_ring', 'test')

    print("Loading REALAPP554 dev frames...")
    dev_rows, dev_batch = fc.items()
    dev_paths = fc.crops(dev_batch)
    dev_keys = [b['id'] for b in dev_batch]
    dev_crop_dicts = [dict(path=dev_paths[k]) for k in dev_keys]

    ckpt0 = load_ckpt(FDR001_PATH)
    ckpt3 = load_ckpt(FDR003_PATH)
    ckpt14 = load_ckpt(FDR014_PATH)

    sd0 = ckpt0['state_dict']
    sd3 = ckpt3['state_dict']
    sd14 = ckpt14['state_dict']

    experiments = [
        # Label, alpha (pill), beta (neg), delta_b, top_k_ratio, layers_filter
        ("Baseline FDR-001", 0.0, 0.0, 0.0, 1.0, None),
        ("FDR-003 Alone", 1.0, 0.0, 0.0, 1.0, None),
        ("FDR-014 Alone", 0.0, 1.0, 0.0, 1.0, None),
        ("WSP Dense 0.05", 0.05, 0.0, 0.0, 1.0, None),
        ("WSP Dense 0.10", 0.10, 0.0, 0.0, 1.0, None),
        ("WSP Dense 0.20", 0.20, 0.0, 0.0, 1.0, None),
        ("WSP Head-Only (classifier) 0.50", 0.50, 0.0, 0.0, 1.0, ['classifier']),
        ("WSP Head-Only (conv_head+classifier) 0.50", 0.50, 0.0, 0.0, 1.0, ['conv_head', 'classifier']),
        ("WSP Head-Only (conv_head+classifier) 1.00", 1.00, 0.0, 0.0, 1.0, ['conv_head', 'classifier']),
        ("WSP Top 10% Sparse 0.20", 0.20, 0.0, 0.0, 0.10, None),
        ("WSP Top 5% Sparse 0.20", 0.20, 0.0, 0.0, 0.05, None),
        ("WSP Dual Dense (a=0.10, b=0.20)", 0.10, 0.20, 0.0, 1.0, None),
        ("WSP Dual Head (a=0.30, b=0.30)", 0.30, 0.30, 0.0, 1.0, ['conv_head', 'classifier']),
    ]

    results = []
    print("\n" + "=" * 90)
    print(f"{'Experiment':<38} {'270 Correct':<12} {'270 FN':<8} {'270 FP':<8} {'Pills>0':<9} {'FalseHigh':<10}")
    print("=" * 90)

    for name, alpha, beta, db, top_k, flt in experiments:
        if name == "Baseline FDR-001":
            trial_path = FDR001_PATH
        elif name == "FDR-003 Alone":
            trial_path = FDR003_PATH
        elif name == "FDR-014 Alone":
            trial_path = FDR014_PATH
        else:
            sd_blend = blend_weights(sd0, sd3, sd14, alpha=alpha, beta=beta, delta_b=db, top_k_ratio=top_k, layers_filter=flt)
            trial_ckpt = copy.deepcopy(ckpt0)
            trial_ckpt['state_dict'] = sd_blend
            torch.save(trial_ckpt, TMP_CKPT)
            trial_path = TMP_CKPT

        # 1. 270 Legacy Retention
        test_probs = predict_torch(trial_path, test_rows)
        ret_m = metrics(test_rows, test_probs, thr=0.85)
        correct_270 = ret_m['tp'] + ret_m['tn']

        # 2. REALAPP554 Dev Set
        dev_scores = dict(zip(dev_keys, predict_torch(trial_path, dev_crop_dicts)))
        dev_m = fc.measure(dev_rows, dev_scores)

        pills_str = f"{dev_m['newstvPillsAbove001']}/10"
        false_str = f"{dev_m['falseHigh']}/157"
        corr_str = f"{correct_270}/270"
        print(f"{name:<38} {corr_str:<12} {ret_m['fn']:<8} {ret_m['fp']:<8} {pills_str:<9} {false_str:<10}")

        results.append({
            'name': name,
            'alpha': alpha,
            'beta': beta,
            'delta_b': db,
            'top_k_ratio': top_k,
            'layers_filter': flt,
            'retention_270': ret_m,
            'dev_metrics': dev_m
        })

    out_file = OUTPUT_DIR / 'wsp-retention-analysis.json'
    with open(out_file, 'w') as f:
        json.dump(results, f, indent=2)
    print("=" * 90)
    print(f"Results written to {out_file}")

if __name__ == '__main__':
    main()
