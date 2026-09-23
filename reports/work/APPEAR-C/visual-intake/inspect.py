"""Inspect the delivered appearance archive using existing admission and crops."""
import hashlib
import io
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path.cwd()/"scripts"))
from PIL import Image, ImageDraw
from harvest_bundle_validation import validate_bundle
from ttr_focus_manifest import derive
from focus_runtime import rendered_items

ROOT = Path.cwd()
HERE = Path(__file__).resolve().parent
BASE = ROOT/"dataset/tvos_captures/appear-c-visual-intake-20260923"
summary = json.loads((BASE/"qualification-summary.json").read_text())
results = []
for recipe in summary["recipes"]:
    name = recipe["recipe"]
    bundle = BASE/(name+"-export")
    assert hashlib.sha256((bundle/"manifest.json").read_bytes()).hexdigest() == recipe["manifest_sha256"]
    files = [p for p in bundle.iterdir() if p.is_file()]
    assert len(files) == recipe["files"] and sum(p.stat().st_size for p in files) == recipe["bytes"]
    contract = validate_bundle(bundle)
    assert contract["acceptedRowCount"] == recipe["pairs"] and contract["unknownClassCount"] == 0
    doc = derive(bundle, ROOT/"dataset/focus_ring"/("appear-c-visual-"+name),
                 "appear-c-visual-"+name, "fb47e39a084a2ff20cdf34b85458f1e1ebbdca8a-dirty",
                 test_only=True, dry_run=True)
    assert [p["elementID"] for p in doc["pairs"]] == recipe["planned_ids"]
    sheet = Image.new("RGB", (1024, 580), "#303030")
    draw = ImageDraw.Draw(sheet)
    for i, (key, raw, _) in enumerate(rendered_items(doc)):
        x, y = (i%4)*256, (i//4)*290
        sheet.paste(Image.open(io.BytesIO(raw)), (x,y+25))
        draw.text((x+4,y+4), key, fill="white")
    sheet.save(HERE/(name+"-crops.png"))
    frames = Image.new("RGB", (1920,1620), "#303030")
    names = ["synth-0_unfocused.png"]+[f"synth-{i}_focused.png" for i in range(recipe["pairs"])]
    for i, filename in enumerate(names):
        meta = json.loads((bundle/(f"synth-{max(i-1,0)}_metadata.json")).read_text())
        scene = meta["baseline_scene" if i == 0 else "focused_scene"]
        with Image.open(bundle/filename) as image:
            image = image.convert("RGB")
            d = ImageDraw.Draw(image)
            for element in scene["elements"]:
                x,y,w,h = element["pixel_bounds"]
                d.rectangle((x,y,x+w,y+h), outline="lime" if element["is_focused"] else "orange", width=3)
            image.thumbnail((960,540))
            frames.paste(image,((i%2)*960,(i//2)*540))
    frames.save(HERE/(name+"-frames.png"))
    results.append({"recipe":name,"pairs":len(doc["pairs"]),"files":len(files),
                    "bundleIdentity":doc["bundleIdentity"],"targets":recipe["planned_ids"],
                    "fileHashes":{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}})
with (HERE/"integrity.json").open("x") as stream:
    json.dump(results,stream,indent=2)
print(json.dumps([{k:r[k] for k in ("recipe","pairs","files")} for r in results]))
