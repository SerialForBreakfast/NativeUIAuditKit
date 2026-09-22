#!/usr/bin/env python3
"""Read-only P0-C decode/schema/membership audit. Never grants training authority."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import re
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
EXPECTED={"train":12340,"validation":2400,"test":2200}
TEST={"CardDetail","WizardStepFlow","NotificationCenter","GalleryPage","MultiSectionForm","SettingsToggleDense","EmptyState","OnboardingPage"}
VALIDATION={"TabViewNavigation","SearchResults","PickerDateEntry","SettingsDisclosure"}
SCHEMA=ROOT/"Research/schemas/annotation.schema.json"
GENERATOR=ROOT/"GeneratorRunner/GeneratorRunnerTests/GenerateDatasetTests.swift"

def require(ok,reason):
    if not ok: raise ValueError(reason)

def sha256(path):
    h=hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda:stream.read(1024*1024),b""):h.update(block)
    return h.hexdigest()

def read_json(path):
    require(path.stat().st_size<=128*1024*1024,"oversized_json")
    def pairs(items):
        d={}
        for k,v in items:
            require(k not in d,"duplicate_json_key");d[k]=v
        return d
    return json.loads(path.read_text(),object_pairs_hook=pairs)

def member(root,name):
    require(isinstance(name,str) and name and not Path(name).is_absolute() and ".." not in Path(name).parts,"unsafe_member")
    p=root/name
    require(p.resolve()==p.absolute() and p.resolve().is_relative_to(root),"symlink_or_escape")
    require(p.is_file(),"missing_member:"+name)
    return p

def check_schema(value,schema,root,where="annotation"):
    """Closed subset used by pinned local schema, NOT a general Draft-7 validator."""
    allowed={"$schema","$id","title","description","type","required","additionalProperties","properties","items","enum","const","pattern","minimum","maximum","$ref","definitions"}
    require(not set(schema)-allowed,"unsupported_schema_keyword")
    if "$ref" in schema:
        ref=schema["$ref"];require(ref.startswith("#/definitions/"),"unsupported_schema_ref")
        return check_schema(value,root["definitions"][ref.split("/")[-1]],root,where)
    types=schema.get("type",[]);types=[types] if isinstance(types,str) else types
    tests={"object":lambda:type(value) is dict,"array":lambda:type(value) is list,
           "string":lambda:type(value) is str,"integer":lambda:type(value) is int,
           "number":lambda:type(value) in (int,float) and math.isfinite(value),
           "boolean":lambda:type(value) is bool,"null":lambda:value is None}
    require(not types or any(tests[t]() for t in types),where+":type")
    if "const" in schema:require(value==schema["const"],where+":const")
    if "enum" in schema:require(value in schema["enum"],where+":enum")
    if "pattern" in schema:require(re.search(schema["pattern"],value) is not None,where+":pattern")
    if "minimum" in schema:require(value>=schema["minimum"],where+":minimum")
    if "maximum" in schema:require(value<=schema["maximum"],where+":maximum")
    if isinstance(value,dict):
        require(set(schema.get("required",[]))<=set(value),where+":required")
        props=schema.get("properties",{})
        if schema.get("additionalProperties") is False:require(not set(value)-set(props),where+":extra_field")
        for k,v in value.items():
            if k in props:check_schema(v,props[k],root,where+"."+k)
    if isinstance(value,list) and "items" in schema:
        for i,v in enumerate(value):check_schema(v,schema["items"],root,where+f"[{i}]")

def inspect_pair(corpus,entry,schema):
    name=entry["fileName"];png=member(corpus,name);annotation=member(corpus,str(Path(name).with_suffix(".json")))
    require(png.stat().st_size<=32*1024*1024,"oversized_png")
    h=sha256(png);require(h==entry.get("sha256"),"image_hash")
    with Image.open(png) as im:
        require(im.format=="PNG" and im.width*im.height<=16_000_000,"image_format_or_size")
        im.load();size=im.size
        pixel=hashlib.sha256(str(size).encode()+im.convert("RGB").tobytes()).hexdigest()
    ann=read_json(annotation);check_schema(ann,schema,schema)
    meta=ann["image"];profile=ann["generatorProfile"]
    require(ann["imageSHA256"]==h and meta["fileName"]==png.name and (meta["pixelWidth"],meta["pixelHeight"])==size,"annotation_image_binding")
    require(meta["platform"] in ("iOS","iPadOS") and meta["scale"]==entry.get("pixelScale"),"platform_scale_binding")
    require(profile["templateFamily"]==entry["templateFamily"] and profile["seed"]==entry.get("generatorSeed"),"annotation_generator_binding")
    require(meta["deviceName"]==entry.get("deviceName"),"device_binding")
    ids=set();classes=Counter();visible_classes=Counter();warnings=Counter();scale=meta["scale"]
    if meta["osVersion"]=="unknown":warnings["sidecar_os_unknown_use_pinned_environment"]+=1
    for e in ann["elements"]:
        require(e["id"] and e["id"] not in ids,"duplicate_element_id");ids.add(e["id"])
        require(e["elementType"]!="webContent","retired_webContent")
        pt,px,vn=(e[k] for k in ("boundsPoints","boundsPixels","boundsVisionNormalized"))
        require(all(abs(pt[k]*scale-px[k])<=.500001 for k in px),"point_pixel_disagreement")
        require(vn["x"]+vn["width"]<=1.000001 and vn["y"]+vn["height"]<=1.000001,"normalized_extent")
        x,y,w,hp=[pt[k]*scale for k in ("x","y","width","height")]
        left,top=max(0,min(size[0],x)),max(0,min(size[1],y))
        right,bottom=max(0,min(size[0],x+w)),max(0,min(size[1],y+hp))
        visible=[left/size[0],1-bottom/size[1],max(0,right-left)/size[0],max(0,bottom-top)/size[1]]
        if visible[2]>0 and visible[3]>0:
            require(all(abs(vn[k]-v)<=1e-5 for k,v in zip(("x","y","width","height"),visible)),"visible_geometry_disagreement:"+e["id"])
            if left!=x or top!=y or right!=x+w or bottom!=y+hp:
                require(e.get("occluded") is True and e.get("occlusionType")=="imageBoundary","missing_clipping_label")
        else:
            require(e.get("excluded") is True and e.get("exclusionReason")=="outsideImage","unexcluded_invisible_element")
            warnings["zero_visible_area_elements"]+=1
        classes[e["elementType"]]+=1
        if visible[2]>0 and visible[3]>0 and not e.get("excluded",False):visible_classes[e["elementType"]]+=1
    return {"imageSHA256":sha256(png),"annotationSHA256":sha256(annotation),"pixelSHA256":pixel,"dimensions":list(size),"visibleClassCounts":dict(visible_classes)},classes,meta,warnings

def validate(corpus,expected=None):
    expected=EXPECTED if expected is None else expected
    corpus=corpus.absolute();require(corpus.resolve()==corpus and corpus.is_relative_to(ROOT),"corpus_boundary")
    mp=member(corpus,"manifest.json");before=sha256(mp);doc=read_json(mp)
    require(isinstance(doc,dict) and isinstance(doc.get("entries"),list) and 0<len(doc["entries"])<=20000,"manifest_entries")
    schema=read_json(SCHEMA)
    taxonomy=schema["properties"]["elements"]["items"]["properties"]["elementType"]["enum"]
    block=GENERATOR.read_text().split("private static let allTemplateFamilies: Set<String> = [",1)[1].split("]",1)[0]
    families=set(re.findall(r'"([A-Za-z0-9_]+)"',block))
    counts=Counter();classes={s:Counter() for s in EXPECTED};styles={s:Counter() for s in EXPECTED}
    visible_classes={s:Counter() for s in EXPECTED}
    errors=[];records=[];seen=set();pixels=defaultdict(list);family_splits=defaultdict(set);warnings=Counter()
    expected_paths={"manifest.json","balance_report.md"}
    for index,entry in enumerate(doc["entries"]):
        row={"index":index,"valid":False};records.append(row)
        try:
            require(isinstance(entry,dict),"invalid_entry")
            name,split,family=(entry.get(k) for k in ("fileName","split","templateFamily"))
            row.update(path=name,split=split,family=family)
            require(split in EXPECTED and isinstance(name,str) and name and Path(name).parts[0]==split and name.endswith(".png"),"split_path")
            counts[split]+=1
            require(name not in seen,"duplicate_membership");seen.add(name)
            require(family in families and family!="HardNegative_2","unknown_or_retired_family")
            require(split==("test" if family in TEST else "validation" if family in VALIDATION else "train"),"wrong_family_split")
            family_splits[family].add(split)
            expected_paths.update((name,str(Path(name).with_suffix(".json"))))
            info,c,meta,warn=inspect_pair(corpus,entry,schema);row.update(info);row["valid"]=True
            pixels[info["pixelSHA256"]].append(name);classes[split].update(c);warnings.update(warn)
            visible_classes[split].update(info["visibleClassCounts"])
            styles[split].update(f"{k}:{meta[k]}" for k in ("colorScheme","dynamicTypeSize","locale","layoutDirection","scale","increaseContrast","boldText","reduceTransparency","buttonShapes"))
        except (ValueError,OSError,KeyError,TypeError,IndexError,Image.DecompressionBombError) as exc:
            row["error"]=str(exc);errors.append({"index":index,"path":row.get("path"),"split":row.get("split"),"error":str(exc)})
    for split,count in expected.items():
        if counts[split]!=count:errors.append({"split":split,"error":f"membership_count:{counts[split]}!={count}"})
    duplicates={h:n for h,n in pixels.items() if len(n)>1}
    crossing={h:n for h,n in duplicates.items() if len({Path(p).parts[0] for p in n})>1}
    for h,names in duplicates.items():errors.append({"error":"duplicate_decoded_pixels","members":names,"pixelSHA256":h})
    rejection_records=[]
    ledger_path=corpus/"capture-ledger.json"
    ledger_hash=None
    if ledger_path.exists():
        expected_paths.add("capture-ledger.json")
        try:
            ledger_hash=sha256(member(corpus,"capture-ledger.json"))
            ledger=read_json(member(corpus,"capture-ledger.json"))
            require(ledger.get("version")==1 and isinstance(ledger.get("accepted"),dict) and isinstance(ledger.get("rejected"),list),"capture_ledger_version_or_shape")
            require(len(ledger["accepted"])==len(seen) and set(ledger["accepted"].values())==seen,"capture_ledger_membership")
            require(all(re.fullmatch(r"[0-9a-f]{64}",k) for k in ledger["accepted"]),"capture_ledger_digest")
            require(len(ledger["rejected"])<=32*len(doc["entries"]),"capture_ledger_attempt_bound")
            accepted_records={r.get("path"):r for r in records if r["valid"]}
            for rejection in ledger["rejected"]:
                entry=rejection["entry"];name=entry["fileName"]
                require(name.startswith("rejected/") and name not in expected_paths,"rejection_path_or_duplicate")
                expected_paths.update((name,str(Path(name).with_suffix(".json"))))
                info,_,_,_=inspect_pair(corpus,entry,schema)
                original=accepted_records.get(rejection["duplicateOf"])
                require(original is not None and info["pixelSHA256"]==original["pixelSHA256"],"rejection_not_duplicate")
                require(ledger["accepted"].get(rejection["pixelSHA256"])==rejection["duplicateOf"],"rejection_ledger_binding")
                rejection_records.append({"path":name,"duplicateOf":rejection["duplicateOf"],**info})
            require(sha256(ledger_path)==ledger_hash,"capture_ledger_changed_during_validation")
        except (ValueError,OSError,KeyError,TypeError,Image.DecompressionBombError) as exc:
            errors.append({"error":"capture_ledger:"+str(exc)})
    extras=[str(p.relative_to(corpus)) for p in corpus.rglob("*") if p.is_symlink() or (p.is_file() and str(p.relative_to(corpus)) not in expected_paths)]
    if extras:errors.append({"error":"unindexed_members","members":sorted(extras)})
    if dict(sum(classes.values(),Counter()))!=doc.get("classDistribution"):errors.append({"error":"class_distribution_mismatch"})
    if sha256(mp)!=before:errors.append({"error":"manifest_changed_during_validation"})
    blocked_splits=set()
    for error in errors:
        if error.get("split") in EXPECTED:blocked_splits.add(error["split"])
        elif error.get("error")=="duplicate_decoded_pixels":
            blocked_splits.update(Path(name).parts[0] for name in error["members"])
        else:blocked_splits.update(EXPECTED)
    membership=hashlib.sha256(json.dumps(records,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()
    return {"validator":"p0-c-reconstructed-corpus-v2","manifestSHA256":before,"membershipSHA256":membership,
            "captureLedgerSHA256":ledger_hash,
            "schemaSHA256":sha256(SCHEMA),"generatorSHA256":sha256(GENERATOR),"validatorSHA256":sha256(Path(__file__)),
            "manifestEntries":len(records),"splitCounts":dict(counts),"expectedSplitCounts":expected,"members":records,
            "families":{k:sorted(v) for k,v in sorted(family_splits.items())},"decodedDuplicateGroups":duplicates,
            "rejectedDuplicateCount":len(rejection_records),"rejectedDuplicates":rejection_records,
            "crossSplitPixelGroups":crossing,"classCounts":{s:dict(c) for s,c in classes.items()},
            "missingClasses":{s:[k for k in taxonomy if not classes[s][k]] for s in EXPECTED},
            "visibleClassCounts":{s:dict(c) for s,c in visible_classes.items()},
            "missingVisibleClasses":{s:[k for k in taxonomy if not visible_classes[s][k]] for s in EXPECTED},
            "classEvidence":"classCounts reconciles all annotations; visibleClassCounts excludes flagged exclusions and zero visible area. Neither proves semantic correctness or model quality.",
            "styleCounts":{s:dict(c) for s,c in styles.items()},
            "styleEvidence":"Declared generator metadata, not independently verified rendered appearance or separate OS/device runtimes.",
            "warnings":dict(warnings),"errors":errors,
            "integrityValid":not errors,"splitReady":{s:s not in blocked_splits and counts[s]==expected.get(s,0) for s in EXPECTED},
            "trainingEligible":False,"modelGatePassed":"not_assessed","identity":"new-reconstruction-not-historical",
            "eligibilityNote":"Independent visual/source/coverage and DS-G8 review required; structural pass is not launch approval."}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--corpus",type=Path,required=True);p.add_argument("--report",type=Path,required=True);a=p.parse_args()
    try:
        out=a.report.absolute();require(out.resolve()==out and out.is_relative_to(ROOT) and not out.exists(),"output_boundary_or_collision")
        report=validate(a.corpus);out.parent.mkdir(parents=True,exist_ok=True)
        with out.open("x") as stream:json.dump(report,stream,indent=2,sort_keys=True,allow_nan=False)
        print(json.dumps({"integrityValid":report["integrityValid"],"entries":report["manifestEntries"],"errors":len(report["errors"])}))
        return 0 if report["integrityValid"] else 1
    except (ValueError,OSError,KeyError,TypeError) as exc:print(str(exc));return 2

if __name__=="__main__":raise SystemExit(main())
