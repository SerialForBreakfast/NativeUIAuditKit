"""Render reviewed crops through the production helper, not a second cropper."""
import base64
import io
import json
import sys
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
from focus_visual_comparison import validate_protocol
from focus_runtime import invoke

HERE = Path(__file__).resolve().parent
doc = json.loads((HERE / "protocol.json").read_text())
validate_protocol(doc)
out = ROOT / ".build/debug-output/focus-visual-02"
out.mkdir(exist_ok=False)
rows = [r for r in doc["samples"] if r["variant"] == "base"]
results = []
for start in range(0, len(rows), 16):
    items = [{"id":r["id"], "path":str(ROOT/r["path"]), "sha256":r["sha256"],
              "bounds":r["bounds"]} for r in rows[start:start+16]]
    results.extend(invoke(items)["results"])
for frame in dict.fromkeys(r["frameID"] for r in rows):
    selected = [(r,v) for r,v in zip(rows,results,strict=True) if r["frameID"] == frame]
    sheet = Image.new("RGB", (1536, 280*((len(selected)+5)//6)), "#303030")
    draw = ImageDraw.Draw(sheet)
    for i,(row,result) in enumerate(selected):
        if result["id"] != row["id"]: raise ValueError("membership_changed")
        crop = Image.open(io.BytesIO(base64.b64decode(result["png"], validate=True)))
        crop.load()
        if crop.size != (256,256): raise ValueError("wrong_crop_dimensions")
        x,y = (i%6)*256,(i//6)*280
        sheet.paste(crop,(x,y))
        draw.text((x+4,y+259), f'{row["elementID"]}: label {row["label"]}', fill="white")
    sheet.save(out/(frame+".png"))
    print(out/(frame+".png"), flush=True)
