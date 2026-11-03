"""Find exact button platter bounds in swiftfin-screen-01.png by pixel gradient/contrast."""
from PIL import Image
import numpy as np

im = Image.open('reports/work/RC561/captures/swiftfin-screen-01.png')
# Crop around (1450, 1150) to (2400, 1400)
crop = im.crop((1450, 1150, 2400, 1400))
crop.save('.build/debug-output/rc561-audit-crops/swiftfin_button_region.png')

# Find where the button background differs from the dark background
arr = np.array(crop.convert('L'))
bg = np.median(arr[:10, :10])
mask = np.abs(arr.astype(int) - bg) > 20

rows = np.where(mask.any(axis=1))[0]
cols = np.where(mask.any(axis=0))[0]

if len(rows) and len(cols):
    y_min, y_max = rows[0] + 1150, rows[-1] + 1150
    x_min, x_max = cols[0] + 1450, cols[-1] + 1450
    print(f"Swiftfin Connect Button Platter: x={x_min}, y={y_min}, w={x_max - x_min}, h={y_max - y_min}")
