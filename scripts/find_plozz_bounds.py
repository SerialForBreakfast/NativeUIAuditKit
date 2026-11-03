"""Analyze elements on plozz-screen-01.png."""
from PIL import Image
import numpy as np

im = Image.open('reports/work/RC561/captures/plozz-screen-01.png')
# Check top right time text/button
crop_tr = im.crop((3200, 80, 3700, 240))
crop_tr.save('.build/debug-output/rc561-audit-crops/plozz_top_right.png')

# Check center logo
crop_c = im.crop((1600, 600, 2300, 1000))
crop_c.save('.build/debug-output/rc561-audit-crops/plozz_center_logo.png')

# Check bottom row cells
crop_cells = im.crop((700, 1550, 3150, 2050))
crop_cells.save('.build/debug-output/rc561-audit-crops/plozz_cells.png')

print("Plozz regions cropped for inspection.")
