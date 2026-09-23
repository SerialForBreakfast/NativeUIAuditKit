"""Bind previously reviewed sources for inspection; grant no new training approval."""
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/"scripts"))
from focus_mixed_assembly import reference, checked

HERE=Path(__file__).resolve().parent
records=json.loads((ROOT/"reports/work/OS-FOCUS-03/sources.json").read_text())
entries=[]
for record in records:
    manifest=checked(record["manifest"])
    checked(record["review"])
    doc=json.loads(manifest.read_text())
    sid=record["screenID"].replace("/","-")
    review={"version":"focus-source-review-v1","manifestSHA256":record["manifest"]["sha256"],
            "reviewer":"NUIAK architect — prior review binding only", "reviewReference":record["review"]["path"],
            "priorReview":record["review"], "priorUse":"development", "relationshipsKnown":True,
            "trainingApproved":False,
            "pairs":{p["pair_id"]:{"partition":record["split"],"relatedGroup":doc["lineage"]} for p in doc["pairs"]}}
    path=HERE/(sid+"-review.json")
    with path.open("x") as f: json.dump(review,f,indent=2)
    entries.append({"id":sid,"manifest":reference(manifest),"review":reference(path)})
baseline=ROOT/"NativeUITrainer/focus_ring_runs/fdr007-native-incremental/weights/best.pt"
spec={"version":"focus-assembly-input-v1","baseline":reference(baseline),"sources":entries}
with (HERE/"native-input.json").open("x") as f: json.dump(spec,f,indent=2)
path=ROOT/"dataset/focus_ring/direct-dialog-20260922-2147/focus_dataset_manifest.json"
doc=json.loads(path.read_text())
review={"version":"focus-source-review-v1","manifestSHA256":reference(path)["sha256"],
        "reviewer":"NUIAK architect — prior direct review binding only", "reviewReference":doc["visualReview"]["report"],
        "priorUse":"development","relationshipsKnown":True,"trainingApproved":False,
        "pairs":{p["pair_id"]:{"partition":"development","relatedGroup":p["recipe_group"]} for p in doc["pairs"]}}
review_path=HERE/"dialog-review.json"
with review_path.open("x") as f: json.dump(review,f,indent=2)
spec["sources"]=[*entries,{"id":"direct-dialog","manifest":reference(path),"review":reference(review_path)}]
# Bind the additive version after the first real CLI assembly has completed.
with (HERE/"mixed-input-template.json").open("x") as f: json.dump(spec,f,indent=2)
print(json.dumps({"nativeSources":len(entries),"additionalDirectPairs":len(doc["pairs"])}))
