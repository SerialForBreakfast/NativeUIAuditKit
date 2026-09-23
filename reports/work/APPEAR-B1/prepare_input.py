"""Freeze B1 references; no capture, training approval, or model execution."""
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path.cwd()/"scripts"))
from focus_mixed_assembly import reference
from focus_dataset_contract import ROOT

here=Path(__file__).resolve().parent
entries=[]
for name in ("grid-artwork","dock-bright","media-placeholder"):
    path=ROOT/"dataset/focus_ring"/("appear-c-visual-"+name)/"focus_dataset_manifest.json"
    doc=json.loads(path.read_text())
    review={"version":"focus-source-review-v1","manifestSHA256":reference(path)["sha256"],
            "priorUse":"development","relationshipsKnown":True,"trainingApproved":False,
            "reviewer":"NUIAK architect","reviewReference":"APPEAR-C independent visual intake; B1 development proposal only",
            "priorReview":reference(ROOT/"reports/work/APPEAR-C/visual-intake/visual-review.md"),
            "pairs":{p["pair_id"]:{"partition":"development","relatedGroup":"appearance-seed7-all-presets"} for p in doc["pairs"]}}
    target=here/(name+"-review.json")
    with target.open("x") as f:json.dump(review,f,indent=2)
    entries.append({"id":"appear-c-"+name,"manifest":reference(path),"review":reference(target)})
spec={"version":"focus-appearance-input-v1",
      "proposal":reference(ROOT/"reports/work/APPEAR-B/proposal.json"),
      "protected":reference(ROOT/"reports/work/APPEAR-B/protected-evidence.json"),
      "additions":entries,"evaluation":[],"selection":None}
with (here/"input.json").open("x") as f:json.dump(spec,f,indent=2)
print("Frozen B1 input; no evaluation, selection floor or execution approval invented")
