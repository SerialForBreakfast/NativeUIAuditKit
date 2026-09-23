"""Bounded catalog evidence inspection; reuses existing validators/cropper."""
import hashlib
import io
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path.cwd()/"scripts"))
from PIL import Image, ImageDraw
from harvest_bundle_validation import validate_bundle
from ttr_focus_manifest import derive
from focus_runtime import rendered_items

ROOT=Path.cwd(); HERE=Path(__file__).resolve().parent
theme=sys.argv[1]
assert theme in {"light","dark","high_contrast"}
bundle=ROOT/"dataset/tvos_captures"/f"appear-c-{theme}"
export=json.loads((HERE/f"{theme}-export.json").read_text())
for f in export["files"]:
    raw=(bundle/f["path"]).read_bytes()
    assert len(raw)==f["bytes"] and hashlib.sha256(raw).hexdigest()==f["sha256"]
contract=validate_bundle(bundle)
assert contract["acceptedRowCount"]==4 and contract["unknownClassCount"]==0
doc=derive(bundle,ROOT/"dataset/focus_ring"/f"appear-c-{theme}",f"appear-c-{theme}",
    "fixture-dylib:5b697fb409e64a6187b60bd68d7ea38cf867c6620fdcefd1fd67cad9c7b5332a",
    test_only=True,dry_run=True)
sheet=Image.new("RGB",(1024,580),"#303030");draw=ImageDraw.Draw(sheet)
for i,(key,raw,_) in enumerate(rendered_items(doc)):
    x=(i%4)*256;y=(i//4)*290
    sheet.paste(Image.open(io.BytesIO(raw)),(x,y+25));draw.text((x+4,y+4),key,fill="white")
sheet.save(HERE/f"{theme}-crops.png")
frames=Image.new("RGB",(1920,1620),"#303030")
names=["synth-0_unfocused.png"]+[f"synth-{i}_focused.png" for i in range(4)]
for i,name in enumerate(names):
    meta=json.loads((bundle/("synth-0_metadata.json" if i==0 else f"synth-{i-1}_metadata.json")).read_text())
    scene=meta["baseline_scene" if i==0 else "focused_scene"]
    assert len(scene["elements"])==8 and len(meta["layout_exclusions"])==33
    assert set(meta["layout_exclusions"].values())=={"catalog_placeholder_not_training_sample"}
    with Image.open(bundle/name) as src:
        im=src.convert("RGB");d=ImageDraw.Draw(im)
        for e in scene["elements"]:
            x,y,w,h=e["pixel_bounds"]
            d.rectangle((x,y,x+w,y+h),outline="lime" if e["is_focused"] else "orange",width=3)
        im.thumbnail((960,540));frames.paste(im,((i%2)*960,(i//2)*540))
frames.save(HERE/f"{theme}-frames.png")
summary={"theme":theme,"pairs":4,"filesVerified":len(export["files"]),"annotationsPerFrame":8,
         "exclusionsPerFrame":33,"targets":[p["elementID"] for p in doc["pairs"]],
         "integrity":"pass","trainingApproval":False}
(HERE/f"{theme}-inspection.json").write_text(json.dumps(summary,indent=2))
print(json.dumps(summary))
