"""Freeze reviewed membership and exact-pixel isolation evidence, never train."""
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path.cwd()/"scripts"))
from focus_dataset_contract import pixel_digest, digest, validate_manifest

ROOT=Path.cwd(); HERE=Path(__file__).resolve().parent
old=json.loads((ROOT/"reports/work/APPEAR-B/proposal.json").read_text())
protected=json.loads((ROOT/"reports/work/APPEAR-B/protected-evidence.json").read_text())
assert old["proposalSHA256"]==digest({k:v for k,v in old.items() if k!="proposalSHA256"})
cache={}
def checked(record):
    key=(record["path"],record["sha256"])
    if key not in cache:
        assert hashlib.sha256((ROOT/record["path"]).read_bytes()).hexdigest()==record["sha256"]
        cache[key]=pixel_digest(ROOT,record)
        assert record.get("pixelSHA256",cache[key])==cache[key]
    return cache[key]
previous={}
for row in old["samples"]+protected["remotesSamples"]:
    for kind in ("frame","crop"):
        previous.setdefault(checked(row[kind]),[]).append({"id":row["id"],"kind":kind,"split":row["split"]})
rows=[];refs=[]
for theme in ("light","dark","high_contrast"):
    path=ROOT/"dataset/focus_ring"/f"appear-c-{theme}"/"focus_dataset_manifest.json"
    doc=json.loads(path.read_text());validate_manifest(doc,path.parent)
    refs.append({"path":str(path.relative_to(ROOT)),"sha256":hashlib.sha256(path.read_bytes()).hexdigest()})
    for pair in doc["pairs"]:
        for role,label in (("focused",1),("unfocused",0)):
            f=pair["frames"][role]
            frame={"path":str(Path(doc["sourceRoot"])/f["path"]),"sha256":f["sha256"]}
            crop={"path":str((path.parent/pair[role+"_crop"]).relative_to(ROOT)),"sha256":pair[role+"_crop_sha256"]}
            rows.append({"id":f"{theme}:{pair['pair_id']}:{role}","theme":theme,"label":label,
                "elementID":pair["elementID"],"control":pair["element_type"],
                "family":"catalog-native-samples-v1","group":"catalog-seed307-all-themes",
                "frame":{**frame,"pixelSHA256":checked(frame)},"crop":{**crop,"pixelSHA256":checked(crop)}})
overlap=[{"id":r["id"],"kind":k,"previous":previous[r[k]["pixelSHA256"]]}
         for r in rows for k in ("frame","crop") if r[k]["pixelSHA256"] in previous]
duplicates={}
for r in rows: duplicates.setdefault(r["crop"]["pixelSHA256"],[]).append(r["id"])
doc={"version":"catalog-evaluation-reservation-v1","role":"candidate-evaluation-quarantine",
     "independentEvaluationEligible":False,"trainingApproval":False,"modelScoresComputed":False,
     "manifests":refs,"samples":rows,"previousSampleCount":len(old["samples"])+len(protected["remotesSamples"]),
     "previousPixelOverlap":overlap,"duplicateCropGroups":[v for v in duplicates.values() if len(v)>1],
     "distinctRecipeFamilies":1,"validationGroupsApproved":0,"finalChallengeGroupsApproved":0,
     "reason":"One shared catalog/layout/focus-treatment family cannot supply separate independent validation and final challenge across five required strata. Themes/seeds do not establish independence.",
     "protectedInputs":[{"path":str(p.relative_to(ROOT)),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
         for p in (ROOT/"reports/work/APPEAR-B/proposal.json",ROOT/"reports/work/APPEAR-B/protected-evidence.json")]}
doc["reservationSHA256"]=digest(doc)
with (HERE/"reservation.json").open("x") as stream:json.dump(doc,stream,indent=2)
print(json.dumps({"samples":len(rows),"oldSamples":doc["previousSampleCount"],"overlaps":len(overlap),
    "uniqueCrops":len(duplicates),"duplicateGroups":doc["duplicateCropGroups"],"independent":False}))
