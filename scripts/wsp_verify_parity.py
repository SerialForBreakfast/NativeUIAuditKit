"""Verify Core ML parity against PyTorch for the winning WSP FocusRing model.
Evaluates both backends on:
1. The 270-crop legacy test split.
2. The 187-crop REALAPP554 development set.
"""
import sys
from pathlib import Path
import json
import statistics
import coremltools as ct
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import research_queue as q
import focus_candidates556 as fc
from eval_focus_ring_detector import load_split, metrics, predict_torch

RUNS = q.ROOT / 'NativeUITrainer/focus_ring_runs'
PT_PATH = RUNS / 'wsp01-head-conv050/weights/best.pt'
ML_PATH = RUNS / 'wsp01-head-conv050/export/FocusRingDetector.mlpackage'
OUT_REPORT = q.ROOT / 'reports/work/WSP/wsp-parity-report.json'

def predict_coreml_crops(model, image_paths):
    out = []
    for p in image_paths:
        im = Image.open(p).convert('RGB')
        y = model.predict({'image': im})
        prob = float(y['is_focused_prob'][0]) if 'is_focused_prob' in y else float(y['confidence'][0])
        out.append(prob)
    return out

def main():
    print("Loading PyTorch and Core ML models...")
    ml_model = ct.models.MLModel(str(ML_PATH))

    # 1. 270 Legacy Retention
    print("\n--- Evaluating 270 Legacy Retention ---")
    test_rows = load_split(q.ROOT / 'dataset/focus_ring', 'test')
    test_paths = [r['path'] for r in test_rows]

    pt_test_probs = predict_torch(PT_PATH, test_rows)
    ml_test_probs = predict_coreml_crops(ml_model, test_paths)

    pt_ret_m = metrics(test_rows, pt_test_probs, thr=0.85)
    ml_ret_m = metrics(test_rows, ml_test_probs, thr=0.85)

    test_diffs = [abs(p - m) for p, m in zip(pt_test_probs, ml_test_probs)]
    print(f"PyTorch 270 Retention: {pt_ret_m['tp']+pt_ret_m['tn']}/270 (FN={pt_ret_m['fn']}, FP={pt_ret_m['fp']})")
    print(f"Core ML 270 Retention: {ml_ret_m['tp']+ml_ret_m['tn']}/270 (FN={ml_ret_m['fn']}, FP={ml_ret_m['fp']})")
    print(f"Max abs prob diff: {max(test_diffs):.6f}, Median diff: {statistics.median(test_diffs):.6f}")

    # 2. REALAPP554 Dev Set
    print("\n--- Evaluating REALAPP554 Development Set ---")
    dev_rows, dev_batch = fc.items()
    dev_paths = fc.crops(dev_batch)
    dev_keys = [b['id'] for b in dev_batch]
    dev_crop_paths = [dev_paths[k] for k in dev_keys]
    dev_crop_dicts = [dict(path=dev_paths[k]) for k in dev_keys]

    pt_dev_probs = predict_torch(PT_PATH, dev_crop_dicts)
    ml_dev_probs = predict_coreml_crops(ml_model, dev_crop_paths)

    pt_scores = dict(zip(dev_keys, pt_dev_probs))
    ml_scores = dict(zip(dev_keys, ml_dev_probs))

    pt_dev_m = fc.measure(dev_rows, pt_scores)
    ml_dev_m = fc.measure(dev_rows, ml_scores)

    dev_diffs = [abs(p - m) for p, m in zip(pt_dev_probs, ml_dev_probs)]
    print("PyTorch Dev Metrics:", pt_dev_m)
    print("Core ML Dev Metrics:", ml_dev_m)
    print(f"Max abs prob diff: {max(dev_diffs):.6f}, Median diff: {statistics.median(dev_diffs):.6f}")

    report = {
        'pytorch': str(PT_PATH.relative_to(q.ROOT)),
        'coreml': str(ML_PATH.relative_to(q.ROOT)),
        'retention_270': {
            'pytorch': pt_ret_m,
            'coreml': ml_ret_m,
            'max_diff': max(test_diffs),
            'median_diff': statistics.median(test_diffs)
        },
        'dev_metrics': {
            'pytorch': pt_dev_m,
            'coreml': ml_dev_m,
            'max_diff': max(dev_diffs),
            'median_diff': statistics.median(dev_diffs)
        }
    }

    OUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_REPORT, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"\nParity report saved to {OUT_REPORT}")

if __name__ == '__main__':
    main()
