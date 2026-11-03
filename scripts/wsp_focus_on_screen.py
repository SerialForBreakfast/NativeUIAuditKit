"""Run WSP FocusRing model on candidate crops of a detected screen.
Identifies the focused element with probability score and rank.
"""
import sys
from pathlib import Path
import json
import coremltools as ct
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import research_queue as q
import focus_runtime as fr

MODEL_PATH = q.ROOT / 'NativeUITrainer/focus_ring_runs/wsp01-head-conv050/export/FocusRingDetector.mlpackage'
DETECTIONS_JSON = q.ROOT / 'reports/work/RC561/rc561-detections-r5.json'
CAPTURES_DIR = q.ROOT / 'reports/work/RC561/captures'

def make_crop(image, box, expansion=0.16, target_size=(256, 256)):
    """Production 16% crop expansion with bilinear resize."""
    x, y, w, h = box
    cx, cy = x + w / 2, y + h / 2
    ew, eh = w * (1 + expansion), h * (1 + expansion)
    x1, y1 = max(0, cx - ew / 2), max(0, cy - eh / 2)
    x2, y2 = min(image.width, cx + ew / 2), min(image.height, cy + eh / 2)
    crop = image.crop((int(x1), int(y1), int(x2), int(y2)))
    return crop.resize(target_size, Image.BILINEAR)

def main():
    print(f"Loading WSP FocusRing model from {MODEL_PATH}...")
    model = ct.models.MLModel(str(MODEL_PATH))

    with open(DETECTIONS_JSON) as f:
        data = json.load(f)

    for screen_name, screen_data in data['screens'].items():
        image_path = CAPTURES_DIR / screen_name
        if not image_path.exists():
            continue
        im = Image.open(image_path).convert('RGB')
        print(f"\n==================== {screen_name} ====================")
        
        candidates = []
        for d in screen_data['detections']:
            # Evaluate non-text controls (buttons, cells, segmentedControl, bars)
            if d['role'] in ('button', 'cell', 'segmentedControl'):
                crop = make_crop(im, d['box'])
                y = model.predict({'image': crop})
                prob = float(y['is_focused_prob'][0]) if 'is_focused_prob' in y else float(y['confidence'][0])
                candidates.append({
                    'role': d['role'],
                    'box': d['box'],
                    'det_score': d['score'],
                    'focus_prob': round(prob, 4)
                })

        candidates.sort(key=lambda c: -c['focus_prob'])
        print(f"Top 5 Focus Candidates (out of {len(candidates)} non-text controls):")
        for rank, c in enumerate(candidates[:5], 1):
            is_focus_str = " [FOCUSED]" if c['focus_prob'] >= 0.85 else (" [AMBIGUOUS]" if c['focus_prob'] >= 0.70 else "")
            print(f"  {rank}. {c['role']:15} focus_prob={c['focus_prob']:.4f} (det_score={c['det_score']:.3f}) box={c['box']}{is_focus_str}")

if __name__ == '__main__':
    main()
