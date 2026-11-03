"""Find exact button platter bounds in strimr-screen-01.png."""
from PIL import Image
import numpy as np

im = Image.open('reports/work/RC561/captures/strimr-screen-01.png')
# Crop around Retry button
crop = im.crop((1750, 1250, 2100, 1420))
crop.save('.build/debug-output/rc561-audit-crops/strimr_button_region.png')

arr = np.array(crop.convert('L'))
bg = np.median(arr[:10, :10])
mask = np.abs(arr.astype(int) - bg) > 20

rows = np.where(mask.any(axis=1))[0]
cols = np.where(mask.any(axis=0))[0]

if len(rows) and len(cols):
    y_min, y_max = rows[0] + 1250, rows[-1] + 1250
    x_min, x_max = cols[0] + 1750, cols[-1] + 1750
    print(f"Strimr Retry Button Platter: x={x_min}, y={y_min}, w={x_max - x_min}, h={y_max - y_min}")

# Also check app icon
crop_icon = im.crop((1800, 720, 2050, 950))
arr_icon = np.array(crop_icon.convert('L'))
bg_icon = np.median(arr_icon[:10, :10])
mask_icon = np.abs(arr_icon.astype(int) - bg_icon) > 20
rows_i = np.where(mask_icon.any(axis=1))[0]
cols_i = np.where(mask_icon.any(axis=0))[0]
if len(rows_i) and len(cols_i):
    print(f"Strimr App Icon: x={cols_i[0]+1800}, y={rows_i[0]+720}, w={cols_i[-1]-cols_i[0]}, h={rows_i[-1]-rows_i[0]}")
