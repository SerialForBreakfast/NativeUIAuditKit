"""Freeze delivered appearance membership; compare against pinned prior evidence."""
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path.cwd()/"scripts"))
from focus_dataset_contract import pixel_digest, digest, validate_manifest

ROOT=Path.cwd(); HERE=Path(__file__).resolve().parent
prior_paths=[ROOT/"reports/work/APPEAR-B/proposal.json",
             ROOT/"reports/work/APPEAR-B/protected-evidence.json",
             ROOT/"reports/work/APPEAR-C/reservation.json"]
previous={}; cache={}
def checked(record):
    key=(record["path"],record["sha256"])
    if key not in cache:
        assert hashlib.sha256((ROOT/record["path"]).read_bytes()).hexdigest()==record["sha256"]
        cache[key]=pixel_digest(ROOT,record)
        assert record.get("pixelSHA256",cache[key])==cache[key]
    return cache[key]
previous_count=0
for path in prior_paths:
    doc=json.loads(path.read_text())
    for row in doc.get("samples",doc.get("remotesSamples",[])):
        previous_count+=1
        for kind in ("frame","crop"):
            previous.setdefault(checked(row[kind]),[]).append({"id":row["id"],"kind":kind,"source":str(path.relative_to(ROOT))})
rows=[];refs=[]
for name in ("grid-artwork","dock-bright","media-placeholder"):
    path=ROOT/"dataset/focus_ring"/("appear-c-visual-"+name)/"focus_dataset_manifest.json"
    doc=json.loads(path.read_text());validate_manifest(doc,path.parent)
    refs.append({"path":str(path.relative_to(ROOT)),"sha256":hashlib.sha256(path.read_bytes()).hexdigest()})
    for pair in doc["pairs"]:
        assert pair["split"]=="development" and pair["recipe_group"]=="seed:7"
        for role,label in (("focused",1),("unfocused",0)):
            f=pair["frames"][role]
            frame={"path":str(Path(doc["sourceRoot"])/f["path"]),"sha256":f["sha256"]}
            crop={"path":str((path.parent/pair[role+"_crop"]).relative_to(ROOT)),"sha256":pair[role+"_crop_sha256"]}
            rows.append({"id":f"{name}:{pair['pair_id']}:{role}","label":label,"group":"appearance-seed7-all-presets",
                         "split":"development","elementID":pair["elementID"],
                         "frame":{**frame,"pixelSHA256":checked(frame)},"crop":{**crop,"pixelSHA256":checked(crop)}})
overlap=[{"id":r["id"],"kind":k,"previous":previous[r[k]["pixelSHA256"]]} for r in rows
         for k in ("frame","crop") if r[k]["pixelSHA256"] in previous]
duplicates={}
for r in rows: duplicates.setdefault(r["crop"]["pixelSHA256"],[]).append(r["id"])
result={"version":"appearance-development-reservation-v1","trainingApproval":False,
        "independentEvaluationEligible":False,"modelScoresComputed":False,"manifests":refs,"samples":rows,
        "previousSampleCount":previous_count,"previousPixelOverlap":overlap,
        "uniqueCrops":len(duplicates),"duplicateCropGroups":[v for v in duplicates.values() if len(v)>1],
        "lineageRule":"All seed7 appearance/layout siblings remain development, including related prior seed7 data; never promote by zero exact-pixel overlap.",
        "protectedInputs":[{"path":str(p.relative_to(ROOT)),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()} for p in prior_paths]}
result["reservationSHA256"]=digest(result)
with (HERE/"reservation.json").open("x") as stream:json.dump(result,stream,indent=2)
print(json.dumps({"samples":len(rows),"uniqueCrops":len(duplicates),"previousSamples":previous_count,"overlaps":len(overlap),"independent":False}))
