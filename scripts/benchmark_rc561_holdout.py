"""Rigorous comparative benchmark of Shipped Standard vs Candidate R5
on RC561 / RA554-13 multi-app independent ground truth holdout.
Computes True Positives, False Positives, False Negatives, Precision, Recall, and F1 at IoU 0.50.
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import research_queue as q

HOLDOUT_MANIFEST = q.ROOT / 'reports/work/RC561/holdout/manifest.json'
STANDARD_DETS = q.ROOT / 'reports/work/RC561/rc561-detections-standard.json'
R5_DETS = q.ROOT / 'reports/work/RC561/rc561-detections-r5.json'
BENCHMARK_REPORT = q.ROOT / 'reports/work/RC561/rc561-holdout-benchmark.json'

def compute_iou(boxA, boxB):
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[0] + boxA[2], boxB[0] + boxB[2])
    yB = min(boxA[1] + boxA[3], boxB[1] + boxB[3])
    interW = max(0.0, xB - xA)
    interH = max(0.0, yB - yA)
    interArea = interW * interH
    areaA = boxA[2] * boxA[3]
    areaB = boxB[2] * boxB[3]
    unionArea = areaA + areaB - interArea
    if unionArea <= 0:
        return 0.0
    return interArea / unionArea

def evaluate_model(dets_data, manifest):
    total_tp = 0
    total_fp = 0
    total_fn = 0
    per_role = {}
    screen_reports = {}

    for case in manifest['cases']:
        label_path = q.ROOT / case['label']
        with open(label_path) as f:
            gt_record = json.load(f)
        
        gt_objects = gt_record['objects']
        img_name = Path(case['image']).name
        screen_dets = dets_data['screens'].get(img_name, {}).get('detections', [])

        matched_gt = set()
        matched_dt = set()

        # Sort detections by score descending
        sorted_dets = sorted(enumerate(screen_dets), key=lambda d: -d[1]['score'])

        tp = 0
        fp = 0
        for dt_idx, dt in sorted_dets:
            dt_box = dt['box']
            dt_role = dt['role']
            best_iou = 0.0
            best_gt_idx = -1
            
            for gt_idx, gt in enumerate(gt_objects):
                if gt_idx in matched_gt:
                    continue
                if gt['class'] != dt_role:
                    continue
                iou = compute_iou(dt_box, gt['box'])
                if iou > best_iou:
                    best_iou = iou
                    best_gt_idx = gt_idx
            
            if best_iou >= 0.50:
                matched_gt.add(best_gt_idx)
                matched_dt.add(dt_idx)
                tp += 1
                role_stats = per_role.setdefault(dt_role, {'tp': 0, 'fp': 0, 'fn': 0})
                role_stats['tp'] += 1
            else:
                fp += 1
                role_stats = per_role.setdefault(dt_role, {'tp': 0, 'fp': 0, 'fn': 0})
                role_stats['fp'] += 1

        fn = len(gt_objects) - len(matched_gt)
        for gt_idx, gt in enumerate(gt_objects):
            if gt_idx not in matched_gt:
                role_stats = per_role.setdefault(gt['class'], {'tp': 0, 'fp': 0, 'fn': 0})
                role_stats['fn'] += 1

        total_tp += tp
        total_fp += fp
        total_fn += fn

        screen_reports[img_name] = {
            'ground_truth_count': len(gt_objects),
            'detections_count': len(screen_dets),
            'tp': tp,
            'fp': fp,
            'fn': fn,
            'precision': round(tp / (tp + fp), 4) if (tp + fp) > 0 else 0.0,
            'recall': round(tp / (tp + fn), 4) if (tp + fn) > 0 else 0.0
        }

    precision = round(total_tp / (total_tp + total_fp), 4) if (total_tp + total_fp) > 0 else 0.0
    recall = round(total_tp / (total_tp + total_fn), 4) if (total_tp + total_fn) > 0 else 0.0
    f1 = round(2 * precision * recall / (precision + recall), 4) if (precision + recall) > 0 else 0.0

    return {
        'total_tp': total_tp,
        'total_fp': total_fp,
        'total_fn': total_fn,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'per_role': per_role,
        'screens': screen_reports
    }

def main():
    with open(HOLDOUT_MANIFEST) as f:
        manifest = json.load(f)
    with open(STANDARD_DETS) as f:
        standard_data = json.load(f)
    with open(R5_DETS) as f:
        r5_data = json.load(f)

    print("Evaluating Shipped Standard (nativeui-tvos-v3.0)...")
    eval_std = evaluate_model(standard_data, manifest)
    
    print("Evaluating Candidate R5 (pills560-r5)...")
    eval_r5 = evaluate_model(r5_data, manifest)

    report = {
        'evaluation_date': '2026-11-03',
        'authority': 'Tasks.md:RA554-13,RC561-05',
        'dataset': 'RC561 multi-app independent holdout (8 screens, 82 controls)',
        'shipped_standard': {
            'model': 'nativeui-tvos-v3.0',
            'results': eval_std
        },
        'candidate_r5': {
            'model': 'pills560-r5',
            'results': eval_r5
        },
        'delta_r5_vs_standard': {
            'tp_delta': eval_r5['total_tp'] - eval_std['total_tp'],
            'fp_delta': eval_r5['total_fp'] - eval_std['total_fp'],
            'fn_delta': eval_r5['total_fn'] - eval_std['total_fn'],
            'precision_delta': round(eval_r5['precision'] - eval_std['precision'], 4),
            'recall_delta': round(eval_r5['recall'] - eval_std['recall'], 4),
            'f1_delta': round(eval_r5['f1'] - eval_std['f1'], 4)
        }
    }

    with open(BENCHMARK_REPORT, 'w') as f:
        json.dump(report, f, indent=2)

    print("\n================ BENCHMARK RESULTS (IoU >= 0.50) ================")
    print(f"{'Metric':<20} | {'Shipped Standard':<18} | {'Candidate R5':<18} | {'Delta':<10}")
    print("-" * 72)
    print(f"{'True Positives (TP)':<20} | {eval_std['total_tp']:<18} | {eval_r5['total_tp']:<18} | {report['delta_r5_vs_standard']['tp_delta']:+d}")
    print(f"{'False Positives (FP)':<20} | {eval_std['total_fp']:<18} | {eval_r5['total_fp']:<18} | {report['delta_r5_vs_standard']['fp_delta']:+d}")
    print(f"{'False Negatives (FN)':<20} | {eval_std['total_fn']:<18} | {eval_r5['total_fn']:<18} | {report['delta_r5_vs_standard']['fn_delta']:+d}")
    print(f"{'Precision':<20} | {eval_std['precision']:<18.4f} | {eval_r5['precision']:<18.4f} | {report['delta_r5_vs_standard']['precision_delta']:+.4f}")
    print(f"{'Recall':<20} | {eval_std['recall']:<18.4f} | {eval_r5['recall']:<18.4f} | {report['delta_r5_vs_standard']['recall_delta']:+.4f}")
    print(f"{'F1 Score':<20} | {eval_std['f1']:<18.4f} | {eval_r5['f1']:<18.4f} | {report['delta_r5_vs_standard']['f1_delta']:+.4f}")
    print("==================================================================")

if __name__ == '__main__':
    main()
