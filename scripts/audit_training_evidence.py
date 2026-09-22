"""Read-only byte audit of explicitly supplied legacy crops/captures; never approves labels."""
import argparse
from collections import Counter, defaultdict
import hashlib
import io
import json
import sys
from pathlib import Path
from PIL import Image
from focus_dataset_contract import ROOT, SPLITS, digest, local, member, FocusDataError


def inspect_png(root, name, size=None):
    record={"path":name, "valid":False}
    try:
        p=member(root,name)
        if p.stat().st_size > 32*1024*1024: raise ValueError("image_too_large")
        raw=p.read_bytes(); record["sha256"]=hashlib.sha256(raw).hexdigest()
        with Image.open(io.BytesIO(raw), formats=["PNG"]) as im:
            if im.width*im.height > 40_000_000: raise ValueError("image_too_large")
            im.load()
            record.update(dimensions=list(im.size), mode=im.mode)
            record["pixelSHA256"]=hashlib.sha256(str(im.size).encode()+im.convert("RGB").tobytes()).hexdigest()
            if size is not None and tuple(size)!=im.size: raise ValueError("wrong_dimensions")
        record["valid"]=True
    except (OSError, ValueError, Image.DecompressionBombError) as error:
        record["error"]=str(error)
    return record


def audit_focus(dataset):
    dataset=local(dataset); manifest=member(dataset,"focus_dataset_manifest.json")
    before=manifest.read_bytes(); doc=json.loads(before)
    if not isinstance(doc,dict) or not isinstance(doc.get("pairs"),list): raise ValueError("invalid_manifest")
    members=[]; seeds=defaultdict(set); hashes=defaultdict(list); ids=Counter()
    splits=Counter(); themes=Counter(); complete=0; errors=[]
    for index,pair in enumerate(doc["pairs"]):
        if not isinstance(pair,dict): raise ValueError("invalid_pair")
        pid=pair.get("pair_id"); ids[str(pid)]+=1
        split=SPLITS.get(pair.get("split")); seed=pair.get("recipe_seed")
        if split is None or type(seed) is not int or not isinstance(pid,str) or not pid:
            errors.append({"index":index,"error":"invalid_identity_split_or_seed"})
        else: seeds[str(seed)].add(split)
        splits[str(split)]+=1; themes[str(pair.get("theme"))]+=1
        pair_members=[]
        for role in ("focused","unfocused"):
            row=inspect_png(dataset,pair.get(role+"_crop"),(256,256))
            row.update(pairID=pid,role=role,split=split)
            pair_members.append(row); members.append(row)
            if row["valid"]: hashes[row["pixelSHA256"]].append({"pairID":pid,"role":role,"split":split})
        complete+=int(all(r["valid"] for r in pair_members))
    if manifest.read_bytes()!=before: raise ValueError("manifest_changed_during_audit")
    collisions=[{"pixelSHA256":h,"members":v} for h,v in sorted(hashes.items()) if len(v)>1]
    leakage=[v for v in collisions if len({m["split"] for m in v["members"]})>1]
    return {"manifestVersion":doc.get("version"),"manifestSHA256":hashlib.sha256(before).hexdigest(),
        "pairCount":len(doc["pairs"]),"decodedCompletePairs":complete,"members":members,
        "splitCounts":dict(splits),"themeCounts":dict(themes),"invalidMembers":sum(not r["valid"] for r in members),
        "metadataErrors":errors,"duplicatePairIDs":[k for k,v in ids.items() if v>1],
        "seedCrossSplit":[s for s,v in sorted(seeds.items()) if len(v)>1],
        "duplicatePixelGroups":collisions,"crossSplitPixelGroups":leakage,
        "frameEvidencePairs":sum(isinstance(p.get("frames"),dict) and bool(p["frames"]) for p in doc["pairs"]),
        "trainingEligible":False,"labelStatus":"not_requalified",
        "scope":"Byte/pixel equality only; related-journey and near-duplicate independence not established."}


def audit_captures(root):
    root=local(root)
    if not root.is_dir(): raise ValueError("missing_capture_directory")
    pngs=sorted(p.name for p in root.glob("*.png"))
    sidecars=sorted(p.name for p in root.glob("*.json") if not p.name.endswith("_result.json"))
    results=sorted(p.name for p in root.glob("*_result.json"))
    records=[]; attached=set()
    for name in sidecars:
        row={"sidecar":name,"trainingEligible":False}
        try:
            p=member(root,name); raw=p.read_bytes(); doc=json.loads(raw)
            row["sidecarSHA256"]=hashlib.sha256(raw).hexdigest()
            image_name=Path(name).stem+".png"; attached.add(image_name)
            meta=doc.get("image",{})
            image=inspect_png(root,image_name,(meta.get("pixelWidth"),meta.get("pixelHeight")))
            row.update(image=image, declaredCaptureSource=doc.get("captureSource"),
                declaredSHA256=doc.get("imageSHA256"), shaMatches=image.get("sha256")==doc.get("imageSHA256") and image.get("sha256") is not None,
                elementsCount=len(doc.get("elements",[])), labelStatus="unreviewed")
        except (OSError,ValueError,TypeError,AttributeError) as error: row["error"]=str(error)
        records.append(row)
    return {"pngCount":len(pngs),"sidecarCount":len(sidecars),"predictionFiles":results,
        "captures":records,"orphans":[inspect_png(root,n) for n in pngs if n not in attached],
        "trainingEligible":False,"scope":"Flat explicitly supplied directory; predictions excluded from labels; source claims unauthenticated."}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--focus",type=Path,required=True); p.add_argument("--captures",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True); a=p.parse_args()
    try:
        out=local(a.output)
        if out.exists(): raise ValueError("output_collision")
        report={"formatVersion":"training-evidence-audit-v1","focus":audit_focus(a.focus),"captures":audit_captures(a.captures),
            "implementationSHA256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"trainingEligible":False,"modelGatePassed":"not_assessed"}
        report["reportSHA256"]=digest(report)
        out.parent.mkdir(parents=True,exist_ok=True)
        with out.open("x") as stream: json.dump(report,stream,indent=2)
        print(json.dumps({"reportSHA256":report["reportSHA256"],"pairs":report["focus"]["pairCount"],"invalidMembers":report["focus"]["invalidMembers"],"crossSplitPixelGroups":len(report["focus"]["crossSplitPixelGroups"]),"trainingEligible":False})); return 0
    except (OSError,ValueError) as error:
        print(str(error),file=sys.stderr); return 2

if __name__=="__main__": raise SystemExit(main())
