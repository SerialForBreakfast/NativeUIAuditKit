"""Evaluate Shipped Standard model NativeUIModel_tvOS on RC561 captures."""
import sys
from pathlib import Path
import json
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import research_queue as q
import roles559 as r559
import coremltools as ct

SIZE = 640
FOLDER = q.ROOT / '.build/debug-output/parity562'
MLPACKAGE = q.ROOT / 'NativeUIAuditKitModels/Sources/NativeUIAuditKitModels/NativeUIModel_tvOS.mlpackage'
CAPTURES_DIR = q.ROOT / 'reports/work/RC561/captures'
OUTPUT_JSON = q.ROOT / 'reports/work/RC561/rc561-detections-standard.json'

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
    print(f"Loading Shipped Standard model from {MLPACKAGE}...")
    model = ct.models.MLModel(str(MLPACKAGE))

    # Load model manifest to get tensorChannelMapping
    manifest_path = q.ROOT / 'NativeUIAuditKitModels/Sources/NativeUIAuditKitModels/Resources/model_manifest_tvos_v1.json'
    with open(manifest_path) as f:
        manifest = json.load(f)
    channel_map = manifest['tensorChannelMapping']

    captures = sorted(CAPTURES_DIR.glob('*.png'))
    print(f"Found {len(captures)} capture frames in {CAPTURES_DIR}.")

    model_file = MLPACKAGE / 'Data/com.apple.CoreML/model.mlmodel'
    results = {
        'model': 'nativeui-tvos-v3.0 (shipped standard)',
        'sha256': q.digest(model_file) if model_file.exists() else 'mlpackage-dir',
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
            mapping = channel_map[i] if i < len(channel_map) else {'type': 'unknown', 'label': f'ch_{i}'}
            raw_cls = mapping.get('label', f'ch_{i}')
            mapped_role = r559.role(raw_cls) or 'unknown'
            
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
                'raw_class': raw_cls,
                'role': mapped_role,
                'class_id': i,
                'score': score,
                'box': box
            })
            screen_counts[mapped_role] = screen_counts.get(mapped_role, 0) + 1
            role_counts_total[mapped_role] = role_counts_total.get(mapped_role, 0) + 1

        dets.sort(key=lambda d: -d['score'])
        results['screens'][cap.name] = {
            'dimensions': [orig_w, orig_h],
            'total_detections': len(dets),
            'role_counts': screen_counts,
            'detections': dets
        }
        print(f"\n--- {cap.name} ({orig_w}x{orig_h}) ---")
        print(f"Total detections: {len(dets)}, roles: {screen_counts}")

    print(f"\nTotal detections across all 8 screens: {sum(role_counts_total.values())}")
    print(f"Role breakdown: {role_counts_total}")

    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_JSON, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Saved results to {OUTPUT_JSON}")

if __name__ == '__main__':
    main()
