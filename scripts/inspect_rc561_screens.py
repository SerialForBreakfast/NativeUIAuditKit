"""Inspect RC561 capture screens to verify visual layout and elements for independent ground truth labeling."""
import sys
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import research_queue as q

CAPTURES = sorted((q.ROOT / 'reports/work/RC561/captures').glob('*.png'))

def main():
    print(f"Found {len(CAPTURES)} capture images:")
    for cap in CAPTURES:
        im = Image.open(cap)
        print(f"  {cap.name}: {im.size}, mode={im.mode}, size_bytes={cap.stat().st_size}")

if __name__ == '__main__':
    main()
