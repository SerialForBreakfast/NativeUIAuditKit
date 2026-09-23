"""Inspect real production base crops; no alternate crop implementation."""
import base64
import io
import json
from pathlib import Path
import sys
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/"scripts"))
from focus_visual_comparison import validate_protocol
from focus_runtime import invoke

HERE=Path(__file__).resolve().parent
doc=json.loads((HERE/"protocol.json").read_text()); validate_protocol(doc)
output=ROOT/".build/debug-output/focus-visual-01"
if output.exists(): raise SystemExit("output_collision")
rows=[r for r in doc["samples"] if r["variant"]=="base"]
items=[{"id":r["id"],"path":str(ROOT/r["path"]),"sha256":r["sha256"],"bounds":r["bounds"]} for r in rows]
reply=invoke(items)
output.mkdir(parents=True)
sheet=Image.new("RGB",(1024,300),"#303030"); draw=ImageDraw.Draw(sheet)
for i,(row,result) in enumerate(zip(rows,reply["results"],strict=True)):
    raw=base64.b64decode(result["png"],validate=True)
    with (output/(str(i)+".png")).open("xb") as f: f.write(raw)
    crop=Image.open(io.BytesIO(raw)); crop.load()
    if crop.size!=(256,256): raise ValueError("wrong_production_crop")
    sheet.paste(crop,(256*i,0)); draw.text((256*i+5,265),f'{row["elementID"]}: visual label {row["label"]}',fill="white")
sheet.save(output/"base-crops.png")
print(output/"base-crops.png")
