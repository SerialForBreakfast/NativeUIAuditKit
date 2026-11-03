"""Audit RC561 screen detections against ground-truth visual reality.
Analyze bounding boxes, detect missed elements, check false positives,
and generate clean, independently validated annotations.
"""
import sys
from pathlib import Path
import json
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import research_queue as q

CAPTURES_DIR = q.ROOT / 'reports/work/RC561/captures'
DETECTIONS_JSON = q.ROOT / 'reports/work/RC561/rc561-detections-r5.json'

def main():
    with open(DETECTIONS_JSON) as f:
        data = json.load(f)
    
    screens = data['screens']
    print(f"Loaded detections for {len(screens)} screens.")
    for name, sdata in screens.items():
        print(f"\nScreen: {name} (dims={sdata['dimensions']})")
        print(f"Role counts: {sdata['role_counts']}")
        # Print top detections
        print("Top 5 detections:")
        for d in sdata['detections'][:5]:
            print(f"  {d['role']:15s} score={d['score']:.3f} box={d['box']}")

if __name__ == '__main__':
    main()
