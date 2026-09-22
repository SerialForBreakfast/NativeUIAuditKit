"""Make paginated diagnostic contact sheets without changing source/crop bytes."""
import json
import sys
from pathlib import Path
from PIL import Image, ImageDraw

root = Path(sys.argv[1])
doc = json.loads((root/"manifest.json").read_text())
for start in range(0, len(doc["pairs"]), 6):
    pairs = doc["pairs"][start:start+6]
    sheet = Image.new("RGB", (1056, ((len(pairs)+1)//2)*294), "#cccccc")
    draw = ImageDraw.Draw(sheet)
    for i, pair in enumerate(pairs):
        x, y = (i%2)*528, (i//2)*294
        draw.text((x+3,y+2), pair["elementID"], fill="black")
        for j, role in enumerate(("focused", "unfocused")):
            sheet.paste(Image.open(root/pair["frames"][role]["crop"]), (x+j*264,y+20))
            draw.text((x+j*264,y+278), role, fill="black")
    name = root.parent/f"review-{start//6+1}.png"
    if name.exists(): raise ValueError("output_collision")
    sheet.save(name)
    print(name)
