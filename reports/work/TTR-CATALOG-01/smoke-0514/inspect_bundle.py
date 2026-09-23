"""Bounded evidence inspection; no capture or training."""
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

here = Path(__file__).resolve().parent
root = Path.cwd()
bundle = root/"dataset/tvos_captures/ttr-dialog-20260923-0514"
export = json.loads((here/"chunk-export.json").read_text())
for f in export["files"]:
    raw = (bundle/f["path"]).read_bytes()
    assert len(raw) == f["bytes"] and hashlib.sha256(raw).hexdigest() == f["sha256"]
contract = validate_bundle(bundle)
(here/"intake-contract.json").write_text(json.dumps(contract, indent=2))
# Inspection only. This transient test-only document is not dataset admission.
doc = derive(bundle, root/"dataset/focus_ring/ttr-dialog-20260923-0514", "ttr-dialog-0514",
             "installed-fixture-dylib:5b697fb409e64a6187b60bd68d7ea38cf867c6620fdcefd1fd67cad9c7b5332a",
             test_only=True, dry_run=True)
sheet = Image.new("RGB", (1024,300), "#303030")
draw = ImageDraw.Draw(sheet)
for i,(key,raw,_) in enumerate(rendered_items(doc)):
    sheet.paste(Image.open(io.BytesIO(raw)), (i*256,30))
    draw.text((i*256+5,8), key, fill="white")
sheet.save(here/"inspection-crops.png")
print(json.dumps({"filesVerified":len(export["files"]),"integrity":contract["integrity"],
                  "pairs":len(doc["pairs"]),"unknownClasses":contract["unknownClassCount"]}))
