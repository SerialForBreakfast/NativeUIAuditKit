"""Offline review of completed recipes in a failed pilot. Never publishes a dataset."""
import argparse
import base64
from collections import Counter, defaultdict
import hashlib
import io
import json
from pathlib import Path

from PIL import Image
from direct_tvos_resume import audit_chain
from direct_focus_manifest import pairs_from_capture
from focus_dataset_contract import ROOT, FocusDataError, digest, local, member, image, pixel_digest
from focus_runtime import identity, invoke, RUNTIME_PREPROCESSING


def analyze(pairs):
    """Seed groups join when any original or crop pixels repeat; roles never lost."""
    parent={str(p["seed"]):str(p["seed"]) for p in pairs}
    def find(k):
        while parent[k]!=k: k=parent[k]
        return k
    def join(a,b):
        a,b=find(a),find(b)
        if a!=b: parent[max(a,b)]=min(a,b)
    uses=defaultdict(list); pair_pixels=defaultdict(list)
    for p in pairs:
        for role in ("focused","unfocused"):
            for kind in ("frame","crop"):
                uses[(kind,p[role][kind+"PixelSHA256"])].append({"pairID":p["pairID"],"seed":p["seed"],"role":role})
        pair_pixels[(p["focused"]["cropPixelSHA256"],p["unfocused"]["cropPixelSHA256"])].append(p["pairID"])
    contradictions=[]; duplicates=[]
    for (kind,sha),records in sorted(uses.items()):
        if len(records)>1:
            duplicates.append({"kind":kind,"pixelSHA256":sha,"uses":records})
            for r in records[1:]: join(str(records[0]["seed"]),str(r["seed"]))
        # A raw frame legitimately holds both focused and unfocused different controls.
        if kind=="crop" and len({r["role"] for r in records})>1:
            contradictions.append({"pixelSHA256":sha,"uses":records})
    groups=defaultdict(list)
    for seed in sorted(parent): groups[find(seed)].append(int(seed))
    return {"seedComponents":list(groups.values()),"duplicatePixelGroups":duplicates,
            "contradictoryCropGroups":contradictions,
            "duplicatePairGroups":[v for _,v in sorted(pair_pixels.items()) if len(v)>1]}


def review(paths,output):
    raw=Path(output).absolute()
    if any(p.is_symlink() for p in [raw,*raw.parents]): raise FocusDataError("symlink_output")
    output=local(raw)
    if output.exists(): raise FocusDataError("output_collision")
    entries,count,expected_pairs=audit_chain(paths)
    runtime=identity()
    output.mkdir(parents=True,exist_ok=False)
    (output/"crops").mkdir()
    pairs=[]; recipes=[]; offset=0; pixel_cache={}
    for entry in entries:
        root=entry["path"].parent
        for result in entry["doc"]["recipes"]:
            recipe=result["recipe"]; index=offset; offset+=1
            recipe_rows=pairs_from_capture({"recipes":[result]})
            recipes.append({"catalogIndex":index,"recipe":recipe,"pairs":len(recipe_rows),
                            "sourceReceiptSHA256":entry["sha256"],"sourceState":entry["doc"]["state"]})
            for p in recipe_rows:
                row={"pairID":p["pair_id"],"catalogIndex":index,"seed":p["recipe_seed"],
                     "family":p["fixture_scene"],"theme":p["theme"],"control":p["element_type"],
                     "elementID":p["elementID"],"labelSource":"fixtureNativeInterval", "partition":"development",
                     "sourceReceiptSHA256":entry["sha256"],"edgeFlags":[]}
                items=[]
                for role in ("focused","unfocused"):
                    frame=p["frames"][role]
                    size=image(root,frame); x,y,w,h=frame["bounds"]
                    if x<=0 or y<=0 or x+w>=size[0] or y+h>=size[1]: row["edgeFlags"].append(role+":viewport-edge")
                    key=(str(root),frame["path"],frame["sha256"])
                    if key not in pixel_cache: pixel_cache[key]=pixel_digest(root,frame)
                    row[role]={"path":str(member(root,frame["path"]).relative_to(ROOT)),"sha256":frame["sha256"],
                               "bounds":frame["bounds"],"dimensions":list(size),"framePixelSHA256":pixel_cache[key],
                               "intervalSHA256":digest(frame["interval"])}
                    items.append({"id":p["pair_id"]+":"+role,"path":str(member(root,frame["path"])),
                                  "sha256":frame["sha256"],"bounds":frame["bounds"]})
                reply=invoke(items)["results"] # two frames always fit the80MP helper cap
                if [r["id"] for r in reply]!=[i["id"] for i in items]: raise FocusDataError("runtime_membership_mismatch")
                for role,result_crop in zip(("focused","unfocused"),reply,strict=True):
                    png=base64.b64decode(result_crop["png"],validate=True)
                    with Image.open(io.BytesIO(png),formats=["PNG"]) as crop:
                        crop.load()
                        if crop.size!=(256,256): raise FocusDataError("invalid_crop_dimensions")
                    name="crops/"+p["pair_id"]+"-"+role+".png"
                    with (output/name).open("xb") as f: f.write(png)
                    record={"path":name,"sha256":hashlib.sha256(png).hexdigest()}
                    row[role].update(cropPath=str((output/name).relative_to(ROOT)),cropSHA256=record["sha256"],
                                     cropPixelSHA256=pixel_digest(output,record))
                pairs.append(row)
    if len(pairs)!=expected_pairs or len({p["pairID"] for p in pairs})!=len(pairs): raise FocusDataError("pair_accounting_mismatch")
    if runtime!=identity() or any(e["path"].read_bytes()!=e["raw"] for e in entries): raise FocusDataError("source_or_runtime_changed")
    # Original source pixels/sidecars were checked by audit_chain; fence again after rendering.
    audit_chain(paths)
    analysis=analyze(pairs)
    doc={"version":"focus-retained-review-v1","purpose":"offline-development-review-not-capture-publication",
         "trainingEligible":False,"fullPilotComplete":count==42,"visualReview":"pending",
         "runtime":runtime,"preprocessing":RUNTIME_PREPROCESSING,
         "sources":[{"path":str(e["path"].relative_to(ROOT)),"sha256":e["sha256"],
                     "state":e["doc"]["state"],"target":e["doc"]["target"],"postflight":e["doc"]["postflight"]} for e in entries],
         "accounting":{"catalogRecipes":42,"completedRecipes":count,"retainedPairs":len(pairs),
                       "missingRecipes":list(range(count,42)),"derivedCrops":2*len(pairs)},
         "recipes":recipes,"pairs":pairs,"analysis":analysis,
         "coverage":[{"family":k[0],"theme":k[1],"pairs":v} for k,v in sorted(Counter((p["family"],p["theme"]) for p in pairs).items())],
         "limitations":["Failed receipts remain failed; no new completed capture receipt or admitted dataset",
                         "Postflight is historical recorded health, not current runtime readiness",
                         "Interval correlation is not atomic framebuffer identity; visual review and training approval separate"]}
    doc["reviewSHA256"]=digest(doc)
    with (output/"review.json").open("x") as f: json.dump(doc,f,indent=2,allow_nan=False)
    return doc


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--receipts",nargs="+",type=Path,required=True); p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    try:
        doc=review(a.receipts,a.output)
        print(json.dumps({**doc["accounting"],"seedComponents":doc["analysis"]["seedComponents"],
                          "contradictoryCropGroups":len(doc["analysis"]["contradictoryCropGroups"]),"reviewSHA256":doc["reviewSHA256"]}))
    except (OSError,ValueError,KeyError,TypeError) as error: p.exit(2,str(error)+"\n")


if __name__=="__main__": main()
