#!/usr/bin/env python3
"""PER-06: offline journey-scoped identity candidates from supplied OCR/detections."""
import argparse
import hashlib
import json
import subprocess
import time
import unicodedata
from collections import Counter
from pathlib import Path
from PIL import Image
from transition_benchmark import ROOT, Invalid, require, number, text, digest, file_hash, read_json, percentiles, host_description

SCENARIOS = {"scroll", "changed-value", "repeated-label", "localization", "hidden-row", "overlay", "stale", "ordinary", "ambiguous-screen", "missing-anchor"}


def normalized(value):
    return " ".join(unicodedata.normalize("NFC", value).casefold().split())


def reference_key(reference):
    return digest([reference["screenID"],reference["locale"]])


def box(b):
    return isinstance(b,list) and len(b)==4 and all(number(v) for v in b) and min(b[:2])>=0 and min(b[2:])>0 and b[0]+b[2]<=1.000000001 and b[1]+b[3]<=1.000000001


def contains(a,b):
    return b[0]>=a[0]-1e-9 and b[1]>=a[1]-1e-9 and b[0]+b[2]<=a[0]+a[2]+1e-9 and b[1]+b[3]<=a[1]+a[3]+1e-9


def validate_policy(p):
    require(p.get("version")=="identity-policy-v1" and text(p.get("reference")),"policy_version")
    require(p.get("frozenOn") in ("development","validation","test-only"),"test_fitted_policy")
    require(isinstance(p.get("supportedLocales"),list) and 1<=len(p["supportedLocales"])<=32 and all(text(v) for v in p["supportedLocales"]),"locales")
    for k in ("confidenceThreshold","labelFraction","minHorizontalOverlap","minimumScreenScore","minimumMargin"):
        require(number(p.get(k)) and 0<p[k]<=1,"policy_"+k)
    require(number(p.get("maxWidthRatio")) and 1<=p["maxWidthRatio"]<=4,"width_ratio")
    require(type(p.get("minimumRowMatches")) is int and 1<=p["minimumRowMatches"]<=64,"row_support")
    require(number(p.get("maxAgeMs")) and 0<p["maxAgeMs"]<=5000,"max_age")
    require(number(p.get("toolTimeoutSeconds")) and 0<p["toolTimeoutSeconds"]<=30,"tool_timeout")


def validate_snapshot(s, case, root, pixels, contents):
    for k in ("observationID","contextEpoch","locale","adapterReference"):
        require(text(s.get(k)),"snapshot_"+k)
    require(s.get("status") in ("success","failed","unavailable"),"observation_status")
    require(all(number(s.get(k)) and s[k]>=0 for k in ("capturedMs","observedMs")),"timestamp")
    require(s.get("evidenceKind") in ("test-only","recorded-observations"),"evidence_kind")
    if case["sourceKind"]!="test-only":require(s["evidenceKind"]=="recorded-observations" and isinstance(s.get("image"),dict),"missing_recorded_image")
    for kind,limit in (("texts",256),("rows",64),("overlays",16)):
        require(isinstance(s.get(kind),list) and len(s[kind])<=limit,"snapshot_bound_"+kind)
        ids=set()
        for item in s[kind]:
            require(box(item.get("bounds")) and number(item.get("confidence")) and 0<=item["confidence"]<=1,"observation_box_or_confidence")
            if kind!="overlays":
                require(text(item.get("id")) and item["id"] not in ids,"observation_id");ids.add(item["id"])
            if kind=="texts":require(isinstance(item.get("text"),str) and 0<len(item["text"])<=1024,"ocr_text")
    require(s["status"]=="success" or not any(s[k] for k in ("texts","rows","overlays")),"failed_with_observations")
    image=s.get("image")
    if image is not None:
        require(isinstance(image,dict) and isinstance(image.get("path"),str),"image")
        path=root/image["path"]
        require(not Path(image["path"]).is_absolute() and ".." not in Path(image["path"]).parts and path.resolve()==path.absolute() and path.resolve().is_relative_to(root.resolve()),"image_escape")
        require(path.is_file() and 0<path.stat().st_size<=32*1024*1024,"missing_or_large_image")
        require(file_hash(path)==image.get("sha256")==s.get("imageSHA256"),"image_hash_binding")
        with Image.open(path) as im:
            require(im.format=="PNG" and im.width*im.height<=16_000_000,"image_format")
            require(type(image.get("width")) is int and type(image.get("height")) is int and im.size==(image["width"],image["height"]),"image_dimensions")
            im.load();h=hashlib.sha256(str(im.size).encode()+im.convert("RGB").tobytes()).hexdigest()
            require(pixels.setdefault(h,case["partition"])==case["partition"],"pixel_leakage")
    # Ignore backend IDs/timestamps: they must not disguise equivalent observation content.
    content={k:sorted([{a:v for a,v in x.items() if a!="id"} for x in s[k]],key=digest) for k in ("texts","rows","overlays")}
    if any(content.values()):
        h=digest(content);require(contents.setdefault(h,case["partition"])==case["partition"],"observation_leakage")


def validate(doc,root,p):
    validate_policy(p)
    require(doc.get("version")=="identity-benchmark-v1" and text(doc.get("corpusID")),"corpus_version")
    cases=doc.get("cases");require(isinstance(cases,list) and 1<=len(cases)<=128,"case_bound")
    ids=set();groups={};pixels={};contents={}
    for c in cases:
        require(text(c.get("id")) and c["id"] not in ids,"case_id");ids.add(c["id"])
        for k in ("group","sourceReference","reviewReference"):require(text(c.get(k)),"case_"+k)
        require(c.get("partition") in ("development","validation","test") and c.get("sourceKind") in ("test-only","simulator","physical"),"partition_or_source")
        require(groups.setdefault(c["group"],c["partition"])==c["partition"],"journey_leakage")
        require(c.get("scenario") in SCENARIOS and c.get("labelOrigin") in ("synthetic-generator","reviewed-human","fixture-callback"),"scenario_or_prediction_truth")
        if c["sourceKind"]!="test-only":require(c["labelOrigin"]!="synthetic-generator" and p["frozenOn"]!="test-only","false_real_evidence")
        refs=c.get("references");require(isinstance(refs,list) and 1<=len(refs)<=16,"reference_bound")
        screen_ids=set();reference_keys=set()
        for r in refs:
            require(text(r.get("screenID")) and text(r.get("locale")),"reference_id")
            key=reference_key(r);require(key not in reference_keys,"duplicate_reference_locale");reference_keys.add(key);screen_ids.add(r["screenID"])
            require(box(r.get("titleRegion")),"title_region")
            for k in ("required","optional","forbidden"):
                require(isinstance(r.get(k),list) and len(r[k])<=16 and all(text(a) for a in r[k]),"anchor_array")
            require(r["required"],"empty_required")
            validate_snapshot(r["snapshot"],c,root,pixels,contents)
            require(r["snapshot"]["status"]=="success" and r["snapshot"]["locale"]==r["locale"],"reference_status_or_locale")
            mapping=r.get("rowIDs")
            require(isinstance(mapping,dict) and set(mapping)=={x["id"] for x in r["snapshot"]["rows"]} and all(text(v) for v in mapping.values()) and len(set(mapping.values()))==len(mapping),"reference_row_mapping")
        validate_snapshot(c["query"],c,root,pixels,contents)
        truth=c.get("truth");require(isinstance(truth,dict) and "expectedScreenID" in truth,"truth")
        expected=truth["expectedScreenID"];require(expected is None or expected in screen_ids,"truth_screen")
        require(isinstance(truth.get("rows"),dict) and set(truth["rows"])=={x["id"] for x in c["query"]["rows"]},"truth_rows")
        permitted={v for r in refs if r["screenID"]==expected for v in r["rowIDs"].values()}
        require(all(v is None or v in permitted for v in truth["rows"].values()),"truth_row_target")
        for key in ("cachedScreenID","cachedEpoch"):
            require(key not in c or text(c[key]),"cache_context")
    return cases


def labels(snapshot,p):
    rows=[r for r in snapshot["rows"] if r["confidence"]>=p["confidenceThreshold"]]
    lines={r["id"]:[] for r in rows};ambiguous=set()
    for line in snapshot["texts"]:
        if line["confidence"]<p["confidenceThreshold"]:continue
        owners=[r for r in rows if contains(r["bounds"],line["bounds"])]
        if len(owners)>1:ambiguous.update(r["id"] for r in owners);continue
        if len(owners)==1:
            r=owners[0];x,w=r["bounds"][0],r["bounds"][2]
            if line["bounds"][0]+line["bounds"][2]/2 <= x+p["labelFraction"]*w:
                lines[r["id"]].append(line)
    return {r["id"]:("" if r["id"] in ambiguous else normalized(" ".join(x["text"] for x in sorted(lines[r["id"]],key=lambda x:(x["bounds"][1],x["bounds"][0]))))) for r in rows}


def match_rows(reference,query,p):
    a,b=labels(reference["snapshot"],p),labels(query,p)
    ca,cb=Counter(a.values()),Counter(b.values());boxes={r["id"]:r["bounds"] for r in reference["snapshot"]["rows"]}
    result={}
    for row in query["rows"]:
        label=b.get(row["id"],"");target=None;reason="missing_label"
        if label:
            possible=[key for key,value in a.items() if value==label]
            reason="no_registered_label"
            if ca[label]>1 or cb[label]>1:reason="ambiguous_label"
            elif len(possible)==1:
                key=possible[0];x,y,w,h=boxes[key];qx,qy,qw,qh=row["bounds"]
                overlap=max(0,min(x+w,qx+qw)-max(x,qx))/min(w,qw)
                if overlap>=p["minHorizontalOverlap"] and max(w,qw)/min(w,qw)<=p["maxWidthRatio"]:
                    target=reference["rowIDs"][key];reason="unique_label_geometry"
                else:reason="geometry_mismatch"
        result[row["id"]]={"candidate":target,"reason":reason,"label":label}
    return result


def anchor_results(references,query,p,helper):
    items=[]
    for r in references:
        regions=[{"text":x["text"],"bounds":x["bounds"]} for x in query["texts"] if x["confidence"]>=p["confidenceThreshold"] and contains(r["titleRegion"],x["bounds"])]
        items.append({"id":reference_key(r),**{k:r[k] for k in ("required","optional","forbidden")},"regions":regions})
    start=time.perf_counter()
    result=subprocess.run([str(helper)],input=json.dumps({"version":1,"items":items}),text=True,capture_output=True,timeout=p["toolTimeoutSeconds"])
    require(result.returncode==0,"anchor_execution_failed:"+result.stderr[-500:])
    reply=json.loads(result.stdout);require(reply.get("version")==1 and isinstance(reply.get("results"),list),"anchor_reply")
    rows=reply["results"];require([r["id"] for r in rows]==[i["id"] for i in items],"anchor_membership")
    for r,item in zip(rows,items):
        require(r.get("status") in ("verified","unverified","ambiguous") and number(r.get("milliseconds")) and r["milliseconds"]>=0,"anchor_result")
        for key,allowed in (("missingRequired",item["required"]),("matchedRequired",item["required"]),("matchedForbidden",item["forbidden"])):
            require(isinstance(r.get(key),list) and all(isinstance(v,str) and v in allowed for v in r[key]),"anchor_evidence")
        matched=set(r["matchedRequired"])
        require(set(r["missingRequired"])==set(item["required"])-matched,"anchor_missing_evidence")
        expected="ambiguous" if not item["required"] or not item["regions"] else ("unverified" if r["missingRequired"] or r["matchedForbidden"] else "verified")
        require(r["status"]==expected,"anchor_status_evidence")
    return {r["id"]:r for r in rows},{"host":reply["host"],"processMs":(time.perf_counter()-start)*1000,"anchorMs":[r["milliseconds"] for r in rows]}


def match(references,query,p,anchors,cached_screen=None,cached_epoch=None):
    """No query truth/group/split argument. Catalog registration is the only identity input."""
    reason=None
    if query["status"]!="success":reason="recognition_"+query["status"]
    elif not 0<=query["observedMs"]-query["capturedMs"]<=p["maxAgeMs"]:reason="stale_or_future"
    elif query["locale"] not in p["supportedLocales"]:reason="unsupported_locale"
    elif any(o["confidence"]>=p["confidenceThreshold"] for o in query["overlays"]):reason="overlay"
    refs=[r for r in references if r["locale"]==query["locale"]]
    if reason is None and not refs:reason="unregistered_locale"
    baseline=None;chosen=None;ranked=[];row_results={};evidence={}
    if reason is None:
        verified=[r for r in refs if anchors[reference_key(r)]["status"]=="verified"]
        if len(verified)==1:baseline=verified[0]["screenID"]
        for r in refs:
            a=anchors[reference_key(r)];evidence[r["screenID"]]={k:v for k,v in a.items() if k!="milliseconds"}
            title={normalized(x["text"]) for x in query["texts"] if x["confidence"]>=p["confidenceThreshold"] and contains(r["titleRegion"],x["bounds"])}
            if a["status"]!="verified" or not all(normalized(v) in title for v in r["required"]):continue
            rows=match_rows(r,query,p)
            matched=sum(v["candidate"] is not None for v in rows.values());support=sum(bool(v["label"]) for v in rows.values())
            score=matched/support if support else 0
            ranked.append({"screenID":r["screenID"],"score":score,"matchedRows":matched,"rows":rows})
        ranked.sort(key=lambda x:(-x["score"],x["screenID"]))
        if ranked:
            best=ranked[0];second=ranked[1]["score"] if len(ranked)>1 else 0
            if best["matchedRows"]>=p["minimumRowMatches"] and best["score"]>=p["minimumScreenScore"] and best["score"]-second>=p["minimumMargin"]:
                chosen=best["screenID"];row_results=best["rows"]
            else:reason="ambiguous_or_insufficient_rows"
        else:reason="missing_or_inexact_anchors"
    if not row_results:row_results={r["id"]:{"candidate":None,"reason":reason or "unknown_screen","label":""} for r in query["rows"]}
    invalidations=[]
    if chosen is None:invalidations.append(reason or "unknown_screen")
    if cached_epoch is not None and cached_epoch!=query["contextEpoch"]:invalidations.append("changed_epoch")
    if chosen is not None and cached_screen is not None and chosen!=cached_screen:invalidations.append("changed_screen")
    if any(v["candidate"] is None for v in row_results.values()):invalidations.append("unresolved_rows")
    return {"state":"candidate" if chosen else "unknown","screenID":chosen,"anchorOnlyScreenID":baseline,
            "reason":reason or "unique_title_rows_geometry","rows":row_results,"rankedScreens":ranked,"anchorEvidence":evidence,
            "observationID":query["observationID"],"contextEpoch":query["contextEpoch"],"capturedMs":query["capturedMs"],"observedMs":query["observedMs"],
            "routeInvalidations":invalidations,"actionAuthorized":False}


def score(c,pred):
    truth=c["truth"];expected=truth["expectedScreenID"]
    out={}
    for mode,actual in (("anchor-only",pred["anchorOnlyScreenID"]),("conservative",pred["screenID"])):
        counts=Counter(cases=1,matchable=int(expected is not None),openSet=int(expected is None),abstentions=int(actual is None))
        counts["correctRetrievals"]+=int(expected is not None and actual==expected)
        counts["falseMatches"]+=int(actual is not None and actual!=expected)
        counts["missedMatches"]+=int(expected is not None and actual!=expected)
        counts["correctOpenSetRejections"]+=int(expected is None and actual is None)
        if mode=="conservative":
            for row,want in truth["rows"].items():
                got=pred["rows"][row]["candidate"];correct=actual==expected and want is not None and got==want
                counts["rowSupport"]+=1;counts["matchableRows"]+=int(want is not None)
                counts["correctRows"]+=int(correct);counts["rowAbstentions"]+=int(got is None)
                counts["falseRowMatches"]+=int(got is not None and not correct)
                counts["missedRows"]+=int(want is not None and not correct)
        out[mode]=dict(counts)
    return out


def summarize(rows):
    counts=Counter();groups=set()
    for row in rows:counts.update(row["counts"]);groups.add(row["group"])
    def rate(k,d):return counts[k]/counts[d] if counts[d] else None
    return {"counts":dict(counts),"journeys":len(groups),"retrievalAccuracy":rate("correctRetrievals","matchable"),
            "falseMatchRate":rate("falseMatches","cases"),"missRate":rate("missedMatches","matchable"),"abstentionRate":rate("abstentions","cases"),
            "rowRetrievalAccuracy":rate("correctRows","matchableRows"),"falseRowMatchRate":rate("falseRowMatches","rowSupport")}


def evaluate(doc,root,p,helper,measure=anchor_results):
    cases=validate(doc,root,p);results=[];failures=[];timings=[]
    for c in cases:
        started=time.perf_counter()
        try:
            anchors,timing=measure(c["references"],c["query"],p,helper)
            pred=match(c["references"],c["query"],p,anchors,c.get("cachedScreenID"),c.get("cachedEpoch"))
            timing["matchingAndAdapterMs"]=(time.perf_counter()-started)*1000;timings.append(timing)
        except (Invalid,subprocess.TimeoutExpired,OSError,ValueError,KeyError,TypeError) as exc:
            failures.append({"id":c["id"],"reason":str(exc)[:800]});continue
        results.append({"id":c["id"],"group":c["group"],"partition":c["partition"],"sourceKind":c["sourceKind"],"locale":c["query"]["locale"],"scenario":c["scenario"],"prediction":pred,"metrics":score(c,pred)})
    summary={}
    for mode in ("anchor-only","conservative"):
        def collect(rs):return summarize([{"counts":r["metrics"][mode],"group":r["group"]} for r in rs])
        slices={"overall":collect(results)}
        for k,values in (("sourceKind",("test-only","physical","simulator")),("partition",("development","validation","test")),("scenario",SCENARIOS),("locale",{c["query"]["locale"] for c in cases})):
            for value in sorted(values):slices[k+":"+value]=collect([r for r in results if r[k]==value])
        summary[mode]=slices
    sources=["scripts/identity_benchmark.py","scripts/generate_identity_fixture.py","scripts/transition_benchmark.py","Tools/AnchorTool/main.swift","Sources/NativeUIAuditKit/Perception/TextAnchorVerifier.swift"]
    return {"version":"identity-report-v1","status":"partial" if failures else "complete","corpusSHA256":digest(doc),"policySHA256":digest(p),"helperSHA256":file_hash(helper),"sourceHashes":{s:file_hash(ROOT/s) for s in sources},"policy":p,
            "accounting":{"expectedCases":len(cases),"evaluatedCases":len(results),"failedCases":len(failures)},"results":results,"summary":summary,"failures":failures,
            "latency":{"scope":"offline supplied-observation matching, excludes OCR/capture/navigation","host":host_description(),"helperHosts":sorted({t["host"] for t in timings}),"coldProcessMs":percentiles([t["processMs"] for t in timings]),"anchorEvaluationMs":percentiles([v for t in timings for v in t["anchorMs"]]),"matchingAndAdapterMs":percentiles([t["matchingAndAdapterMs"] for t in timings])},
            "outcomes":{"dataEligible":False,"liveIntegrationQualified":False,"modelGatePassed":None},
            "recommendation":"No model training or route execution: review identity/locale support and evaluate independent held-out recorded journeys; candidate scores are not probabilities."}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest",type=Path,required=True);parser.add_argument("--policy",type=Path,required=True)
    parser.add_argument("--helper",type=Path,default=ROOT/".build/debug/AnchorTool");parser.add_argument("--output",type=Path,required=True)
    a=parser.parse_args()
    try:
        output=a.output.absolute();require(output.resolve().is_relative_to(ROOT) and output.parent.is_dir() and not output.exists() and not output.is_symlink(),"output_collision_or_boundary")
        manifest=a.manifest.absolute();require(manifest.resolve().is_relative_to(ROOT),"manifest_boundary")
        helper=a.helper.resolve();require(helper.is_relative_to(ROOT) and helper.is_file(),"helper_missing_or_boundary")
        report=evaluate(read_json(manifest),manifest.parent,read_json(a.policy),helper)
        with output.open("x") as stream:json.dump(report,stream,indent=2,sort_keys=True,allow_nan=False)
        print(json.dumps({"status":report["status"],"accounting":report["accounting"],"output":str(output)}));return 1 if report["failures"] else 0
    except (Invalid,OSError,ValueError,KeyError,TypeError) as exc:
        print(json.dumps({"error":str(exc)}));return 2


if __name__=="__main__":raise SystemExit(main())
