"""Evaluate candidate model R5 (Core ML) on RC561 fresh real app captures.
Outputs JSON report with detections per screen and summary statistics.
"""
import sys
from pathlib import Path
import json
import statistics

# Ensure scripts directory is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import research_queue as q
import coremltools as ct
from PIL import Image

SIZE = 640
FOLDER = q.ROOT / '.build/debug-output/parity562'
MLPACKAGE = q.ROOT / 'NativeUITrainer/pills560-r5/final.mlpackage'
CAPTURES_DIR = q.ROOT / 'reports/work/RC561/captures'
OUTPUT_JSON = q.ROOT / 'reports/work/RC561/rc561-detections-r5.json'

ROLE_NAMES = {
    0: 'button', 1: 'text', 2: 'picture', 3: 'textField', 4: 'toggle',
    5: 'adjustable', 6: 'segmentedControl', 7: 'pageControl', 8: 'cell',
    9: 'bar', 10: 'dialog', 11: 'indicator', 12: 'container'
}

def letterbox(path):
    im = Image.open(path).convert('RGB')
    s = min(SIZE / im.width, SIZE / im.height)
    w, h = int(im.width * s), int(im.height * s)
    px, py = (SIZE - w) // 2, (SIZE - h) // 2
    FOLDER.mkdir(parents=True, exist_ok=True)
    dst = FOLDER / (q.digest(path)[:16] + '.png')
    if not dst.exists():
        canvas = Image.new('RGB', (SIZE, SIZE), (114, 114, 114))
        canvas.paste(im.resize((w, h), Image.BILINEAR), (px, py))
        canvas.save(dst)
    return dst, s, px, py

def main():
    print(f"Loading Core ML model from {MLPACKAGE}...")
    model = ct.models.MLModel(str(MLPACKAGE))

    captures = sorted(CAPTURES_DIR.glob('*.png'))
    print(f"Found {len(captures)} capture frames in {CAPTURES_DIR}.")

    pt_file = q.ROOT / 'NativeUITrainer/pills560-r5/final.pt'
    results = {
        'model': str(MLPACKAGE.relative_to(q.ROOT)),
        'sha256': q.digest(pt_file) if pt_file.exists() else 'mlpackage-dir',
        'confidenceThreshold': 0.25,
        'iouThreshold': 0.45,
        'screens': {}
    }

    role_counts_total = {}

    for cap in captures:
        sq, s, px, py = letterbox(cap)
        im_orig = Image.open(cap)
        orig_w, orig_h = im_orig.size
        
        y = model.predict({
            'image': Image.open(sq).convert('RGB'),
            'iouThreshold': 0.45,
            'confidenceThreshold': 0.25
        })

        dets = []
        screen_counts = {}
        for c, (cx, cy, bw, bh) in zip(y['confidence'], y['coordinates']):
            i = int(c.argmax())
            cls_name = ROLE_NAMES.get(i, f'class_{i}')
            x1 = (cx - bw / 2) * SIZE
            y1 = (cy - bh / 2) * SIZE
            box = [
                round(float((x1 - px) / s), 1),
                round(float((y1 - py) / s), 1),
                round(float(bw * SIZE / s), 1),
                round(float(bh * SIZE / s), 1)
            ]
            score = round(float(c[i]), 4)
            dets.append({
                'role': cls_name,
                'class_id': i,
                'score': score,
                'box': box
            })
            screen_counts[cls_name] = screen_counts.get(cls_name, 0) + 1
            role_counts_total[cls_name] = role_counts_total.get(cls_name, 0) + 1

        dets.sort(key=lambda d: -d['score'])
        results['screens'][cap.name] = {
            'dimensions': [orig_w, orig_h],
            'total_detections': len(dets),
            'role_counts': screen_counts,
            'detections': dets
        }
        print(f"\n--- {cap.name} ({orig_w}x{orig_h}) ---")
        print(f"Total detections: {len(dets)}")
        for role, cnt in sorted(screen_counts.items(), key=lambda x: -x[1]):
            print(f"  {role}: {cnt}")

    results['total_detections'] = sum(s['total_detections'] for s in results['screens'].values())
    results['aggregate_role_counts'] = role_counts_total

    print("\n================ AGGREGATE SUMMARY ================")
    print(f"Total screens evaluated: {len(captures)}")
    print(f"Total detections across all screens: {results['total_detections']}")
    for role, cnt in sorted(role_counts_total.items(), key=lambda x: -x[1]):
        print(f"  {role:18}: {cnt}")

    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_JSON, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved evaluation results to {OUTPUT_JSON}")

if __name__ == '__main__':
    main()
