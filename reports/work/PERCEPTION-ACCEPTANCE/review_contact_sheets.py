"""Bounded visual-review index for the audited, explicitly supplied capture directory.

Thumbnails are inspection aids only, never labels or dataset inputs.
"""
from pathlib import Path
import json
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
audit = json.loads((Path(__file__).parent / "audit.json").read_text())
members = [r["image"] for r in audit["captures"]["captures"] if "image" in r]
members += audit["captures"]["orphans"]
members.sort(key=lambda r: r["path"])
output = ROOT / ".build/debug-output/perception-acceptance"
for page in range((len(members)+11)//12):
    sheet = Image.new("RGB", (1440, 1000), "#333333")
    draw = ImageDraw.Draw(sheet)
    for slot, row in enumerate(members[page*12:(page+1)*12]):
        x, y = (slot%3)*480, (slot//3)*250
        if row["valid"]:
            with Image.open(ROOT/"dataset/tvos_captures"/row["path"]) as im:
                im.thumbnail((474, 218)); sheet.paste(im, (x,y))
        draw.text((x+3,y+220), f"{page*12+slot+1}: {row['path']}", fill="white")
    destination = output/f"review-{page+1}.png"
    if destination.exists(): raise ValueError("output collision")
    sheet.save(destination)
