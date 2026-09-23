"""Compact review sheets from production crops; no new cropper or labels."""
import json
from pathlib import Path
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[3]; HERE=Path(__file__).resolve().parent
doc=json.loads((HERE/"audit/review.json").read_text())
out=HERE/"sheets"; out.mkdir(exist_ok=False)
for theme in ("light","dark","highContrast"):
    rows=[p for p in doc["pairs"] if p["theme"]==theme and p["family"]!="focusMaze"]
    sheet=Image.new("RGB",(1152,144*((len(rows)+3)//4)),"#202020"); draw=ImageDraw.Draw(sheet)
    for i,pair in enumerate(rows):
        x,y=(i%4)*288,(i//4)*144
        for j,role in enumerate(("focused","unfocused")):
            with Image.open(ROOT/pair[role]["cropPath"]) as im:
                im.thumbnail((128,128)); sheet.paste(im,(x+j*132,y))
        draw.text((x,y+128),f'{pair["catalogIndex"]} {pair["elementID"]} + / -',fill="white")
    sheet.save(out/(theme+".png"))
# Only goal-edge pairs are uncertain; prior full-scene review already flags all maze recipes.
rows=[p for p in doc["pairs"] if p["edgeFlags"]]
sheet=Image.new("RGB",(1024,280*((len(rows)+1)//2)),"#202020"); draw=ImageDraw.Draw(sheet)
for i,pair in enumerate(rows):
    x,y=(i%2)*512,(i//2)*280
    for j,role in enumerate(("focused","unfocused")):
        with Image.open(ROOT/pair[role]["cropPath"]) as im: sheet.paste(im,(x+j*256,y))
    draw.text((x,y+258),f'{pair["catalogIndex"]} {pair["theme"]} {pair["elementID"]} + / -',fill="white")
if rows: sheet.save(out/"edge-anomalies.png")
print(json.dumps({"cleanCandidatePairs":sum(p["family"]!="focusMaze" for p in doc["pairs"]),"edgePairs":len(rows)}))
