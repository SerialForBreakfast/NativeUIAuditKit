"""Ground Truth Builder for RC561 / RA554-13 multi-app holdout.
Generates genuine, independent reference annotations without model predictions.
Applies NUIAK ROLES559 taxonomy and Rule B (text inside button belongs to button).
"""
import sys
import json
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import research_queue as q

CAPTURES_DIR = q.ROOT / 'reports/work/RC561/captures'
HOLDOUT_DIR = q.ROOT / 'reports/work/RC561/holdout'
LABELS_DIR = HOLDOUT_DIR / 'labels'
OVERLAYS_DIR = q.ROOT / '.build/debug-output/rc561-gt-overlays'

OVERLAYS_DIR.mkdir(parents=True, exist_ok=True)
LABELS_DIR.mkdir(parents=True, exist_ok=True)

def verify_and_draw(image_path, objects, out_path):
    im = Image.open(image_path).convert('RGB')
    draw = ImageDraw.Draw(im)
    colors = {
        'button': (0, 255, 0),
        'text': (255, 255, 0),
        'picture': (0, 200, 255),
        'cell': (255, 128, 0),
        'bar': (255, 0, 255),
        'textField': (0, 128, 255),
        'segmentedControl': (128, 255, 128),
    }
    for obj in objects:
        x, y, w, h = obj['box']
        role = obj['class']
        color = colors.get(role, (255, 255, 255))
        draw.rectangle([x, y, x + w, y + h], outline=color, width=4)
    # Save thumbnail overlay for fast visual inspection
    thumb = im.resize((1280, 720), Image.Resampling.LANCZOS)
    thumb.save(out_path)

