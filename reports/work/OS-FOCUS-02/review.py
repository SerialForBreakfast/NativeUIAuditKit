"""Local diagnostic contact sheet; no alteration of training/source pixels."""
import json
from pathlib import Path
from PIL import Image, ImageDraw

root = Path(__file__).resolve().parent / "root-sweep-02/dataset-02"
doc = json.loads((root / "manifest.json").read_text())
sheet = Image.new("RGB", (1056, 6*294), "#cccccc")
draw = ImageDraw.Draw(sheet)
scores = {r["id"]: r["probability"] for r in doc["scores"]}
for i, pair in enumerate(doc["pairs"]):
    x, y = (i%2)*528, (i//2)*294
    draw.text((x+3,y+2), pair["elementID"], fill="black")
    for j, role in enumerate(("focused", "unfocused")):
        im = Image.open(root/pair["frames"][role]["crop"])
        sheet.paste(im, (x+j*264,y+20))
        draw.text((x+j*264,y+278), f"{role}: {scores[pair['pair_id']+':'+role]:.4f}", fill="black")
sheet.save(root.parent/"review-crops.png")
