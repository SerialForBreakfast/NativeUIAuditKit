"""Crop and inspect regions of interest for each of the 8 screens."""
import sys
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import research_queue as q

CAPTURES_DIR = q.ROOT / 'reports/work/RC561/captures'
CROPS_OUT = q.ROOT / '.build/debug-output/rc561-audit-crops'
CROPS_OUT.mkdir(parents=True, exist_ok=True)

def inspect_swiftfin():
    im = Image.open(CAPTURES_DIR / 'swiftfin-screen-01.png')
    # Save a downscaled thumbnail to easily inspect
    thumb = im.resize((960, 540), Image.Resampling.LANCZOS)
    thumb.save(CROPS_OUT / 'swiftfin_thumb.png')
    print("Swiftfin thumbnail saved.")

def inspect_strimr():
    im = Image.open(CAPTURES_DIR / 'strimr-screen-01.png')
    thumb = im.resize((960, 540), Image.Resampling.LANCZOS)
    thumb.save(CROPS_OUT / 'strimr_thumb.png')
    print("Strimr thumbnail saved.")

def inspect_plozz():
    im = Image.open(CAPTURES_DIR / 'plozz-screen-01.png')
    thumb = im.resize((960, 540), Image.Resampling.LANCZOS)
    thumb.save(CROPS_OUT / 'plozz_thumb.png')
    print("Plozz thumbnail saved.")

def main():
    inspect_swiftfin()
    inspect_strimr()
    inspect_plozz()

if __name__ == '__main__':
    main()
