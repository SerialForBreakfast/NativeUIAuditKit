"""Development-only temporal focus replay over frozen frames and cached scores.

Change boxes rank existing current-frame control boxes; never labels or crop boxes.
No device input, model inference, training, promotion or automatic retry.
"""
import argparse
from collections import Counter, defaultdict
import json
import math
from pathlib import Path
import subprocess

from PIL import Image
import transition_benchmark as t
from focus_mixed_assembly import checked
from focus_dataset_contract import local

ROOT = t.ROOT
POLICY = {"modelThreshold": .85, "minimumOverlap": .01, "minimumLead": .10,
          "noiseThreshold": 24, "toolTimeoutSeconds": 60}
KINDS = {"reference-to-focus", "constructed-focus-switch", "identical-frame-control"}


def require(ok, why):
    if not ok: raise ValueError(why)


def box(value, width, height):
    require(isinstance(value, list) and len(value) == 4
            and all(type(x) in (int, float) and math.isfinite(x) for x in value), "invalid_box")
    x,y,w,h = value
    require(x >= 0 and y >= 0 and w > 0 and h > 0 and x+w <= width and y+h <= height,
            "out_of_frame_box")


def overlap_score(bounds, regions):
    x,y,w,h = bounds
    area = sum(max(0,min(x+w,a+c)-max(x,a))*max(0,min(y+h,b+d)-max(y,b))
               for a,b,c,d in regions)
    # Bounding rectangles can overlap: this is a coarse ranking score, not changed pixels.
    return min(1., area / (w*h))


def predict(candidates, regions, model, mode):
    """No truth, expected input direction or previous native focus is consulted."""
    scored = [(c["id"], overlap_score(c["bounds"], regions), c["scores"][model]) for c in candidates]
    single = [sid for sid,_,p in scored if p >= POLICY["modelThreshold"]]
    if mode == "single-frame" or (mode == "combined" and not regions):
        return {"selected": single[0] if len(single)==1 else None,
                "reason": "single-frame" if len(single)==1 else "model-none-or-multiple"}
    require(mode in {"diff-only", "combined"}, "unsupported_arm")
    eligible = [(sid,score) for sid,score,p in scored
                if score >= POLICY["minimumOverlap"]
                and (mode == "diff-only" or p >= POLICY["modelThreshold"])]
    eligible.sort(key=lambda x:(-x[1],x[0]))
    if not eligible: return {"selected": None, "reason": "no-supported-change"}
    if len(eligible)>1 and eligible[0][1]-eligible[1][1] < POLICY["minimumLead"]:
        return {"selected": None, "reason": "ambiguous-change"}
    return {"selected": eligible[0][0], "reason": "unique-supported-change"}


def validate(doc):
    require(doc.get("version") == "temporal-focus-development-v1"
            and doc.get("partition") == "development" and doc.get("policy") == POLICY,
            "unsupported_protocol")
    require(doc.get("protocolSHA256") == t.digest({k:v for k,v in doc.items() if k != "protocolSHA256"}), "changed_protocol")
    prior = json.loads(checked(doc["cachedProtocol"]).read_text())
    results = json.loads(checked(doc["cachedResults"]).read_text())
    require(prior.get("protocolSHA256") == t.digest({k:v for k,v in prior.items() if k != "protocolSHA256"})
            and results.get("protocolSHA256") == prior["protocolSHA256"], "unbound_cached_results")
    require(prior.get("version") == "appearance-family-development-evaluation-v1", "unsupported_cached_protocol")
    admitted = defaultdict(set)
    focus_claims = defaultdict(set)
    for name, ref in prior["manifests"].items():
        manifest = json.loads(checked(ref).read_text())
        for pair in manifest["pairs"]:
            require(pair["split"] == "development", "nondevelopment_source")
            for f in pair["frames"].values():
                key = (str(Path(manifest["sourceRoot"])/f["path"]),f["sha256"])
                admitted[key].add((name,pair["recipe_group"]))
                focus_claims[key].add(f["observedFocusID"])
    cached = {r["id"]:r for r in prior["competitionSamples"] if r["variant"] == "base"}
    models = sorted(results["results"])
    require(models == ["fdr007", "fdr008", "shipped"], "missing_model_arm")
    cases = doc.get("cases")
    require(isinstance(cases,list) and 0 < len(cases) <= 128, "case_limit")
    require(len({c["id"] for c in cases}) == len(cases), "duplicate_case")
    seen = {}
    for c in cases:
        require(c.get("kind") in KINDS and c.get("geometryOrigin") == "reviewed-native-current-frame",
                "unsupported_case_or_geometry")
        require(isinstance(c.get("group"),str) and c["group"], "missing_group")
        before_key = (c["before"]["path"],c["before"]["sha256"])
        after_key = (c["after"]["path"],c["after"]["sha256"])
        require(bool(admitted[before_key] & admitted[after_key]), "unbound_or_cross_recipe_frames")
        require(focus_claims[after_key] == {c["truthID"]}, "conflicting_native_truth")
        if c["kind"] == "reference-to-focus":
            require(focus_claims[before_key] == {None}, "reference_has_focus")
        if c["kind"] == "constructed-focus-switch":
            require(len(focus_claims[before_key]) == 1 and None not in focus_claims[before_key]
                    and c["truthID"] not in focus_claims[before_key], "not_a_focus_switch")
        for f in (c["before"],c["after"]):
            raw = ROOT/f["path"]
            require(raw.absolute() == raw.resolve(), "symlink_frame")
            path = checked({k:f[k] for k in ("path","sha256")})
            require(path.stat().st_size <= 32*1024*1024, "oversized_image")
            if f["sha256"] not in seen:
                with Image.open(path) as im:
                    require(im.format == "PNG" and 0 < im.width*im.height <= 16_000_000, "invalid_image")
                    im.load(); seen[f["sha256"]] = im.size
            require(seen[f["sha256"]] == (f["width"],f["height"]), "image_dimensions")
        require(seen[c["before"]["sha256"]] == seen[c["after"]["sha256"]], "unregistered_dimensions")
        if c["kind"] == "identical-frame-control":
            require(c["before"]["sha256"] == c["after"]["sha256"], "nonidentical_control")
        members = c["candidates"]
        require(1 < len(members) <= 64 and len({m["id"] for m in members}) == len(members), "invalid_candidates")
        known_ids = {r["id"] for r in cached.values() if r["frameID"] == c["frameID"]}
        require({m["scoreID"] for m in members} == known_ids, "incomplete_competition")
        truth = []
        for m in members:
            box(m["bounds"],c["after"]["width"],c["after"]["height"])
            r = cached[m["scoreID"]]
            require((m["id"],m["bounds"],c["after"]["path"],c["after"]["sha256"])
                    == (r["elementID"],r["bounds"],r["path"],r["sha256"]), "changed_candidate_binding")
            require(set(m["scores"]) == set(models), "missing_scores")
            for model,p in m["scores"].items():
                require(type(p) in (int,float) and math.isfinite(p) and 0 <= p <= 1
                        and p == results["results"][model]["scores"][m["scoreID"]], "changed_or_invalid_score")
            if r["label"] == 1: truth.append(m["id"])
        require(truth == [c["truthID"]], "unbound_or_ambiguous_truth")
    return cases, models


def evaluate(doc, helper, measure=t.measure):
    cases, models = validate(doc)
    decisions = []; measurements = []; errors = []
    for c in cases:
        frames = [{**c[k], "id": k} for k in ("before","after")]
        try:
            values,timing = measure({"frames":frames},ROOT,POLICY,helper)
            measured = values[t.pair_id(*frames)]
            regions = measured["regions"]
            require(len(regions)<=128, "region_limit")
            for b in regions: box(b,c["after"]["width"],c["after"]["height"])
            measurements.append({"caseID":c["id"],"measurement":measured,"timing":timing})
            for model in models:
                for mode in ("single-frame","diff-only","combined"):
                    prediction = predict(c["candidates"],regions,model,mode)
                    # Join ground truth only after this arm's prediction.
                    outcome = "abstained" if prediction["selected"] is None else "correct" if prediction["selected"] == c["truthID"] else "wrong"
                    decisions.append({"caseID":c["id"],"group":c["group"],"kind":c["kind"],"model":model,
                                      "arm":mode,**prediction,"outcome":outcome})
        except (ValueError,OSError,KeyError,subprocess.TimeoutExpired) as error:
            errors.append({"caseID":c["id"],"error":str(error)})
            break  # Preserve failure; do not automatically retry the helper.
    summary = defaultdict(Counter)
    for r in decisions: summary[r["kind"]+"/"+r["model"]+"/"+r["arm"]][r["outcome"]] += 1
    return {"version":"temporal-focus-development-result-v1","protocolSHA256":doc["protocolSHA256"],
            "plannedCases":len(cases),"completedCases":len(measurements),"errors":errors,
            "decisions":decisions,"summary":dict(summary),"measurements":measurements,
            "trainingEligible":False,"integrationQualified":False,"modelGatePassed":"not_assessed",
            "limitations":["Oracle native boxes; cached scores; development-only source-related examples",
                           "Constructed switches/no-op controls are not recorded action journeys",
                           "No scrolling registration, settling, interruption or live safety qualification",
                           "Overlap is change bounding-box coverage, not fraction of changed pixels",
                           "Fixed exploratory thresholds; no tuning or generalization claim"]}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--helper",type=Path,default=ROOT/".build/debug/TransitionTool")
    args = p.parse_args()
    try:
        raw = args.output.absolute()
        require(raw.resolve() == raw, "symlink_output")
        out = local(raw); require(not out.exists(), "output_collision")
        helper = local(args.helper.absolute())
        require(helper.is_file(), "missing_helper")
        helper_hash = t.file_hash(helper)
        doc = json.loads(local(args.manifest.absolute()).read_text())
        result = evaluate(doc,helper)
        result["helperSHA256"] = helper_hash
        if t.file_hash(helper) != helper_hash:
            result["errors"].append({"error":"helper_changed_during_replay"})
        result["evaluatorSHA256"] = t.file_hash(__file__)
        out.parent.mkdir(parents=True,exist_ok=True)
        with out.open("x") as f: json.dump(result,f,indent=2,allow_nan=False)
        print(json.dumps({k:result[k] for k in ("plannedCases","completedCases","errors","summary")}))
        return 1 if result["errors"] else 0
    except (ValueError,OSError,KeyError,TypeError) as error:
        print(json.dumps({"error":str(error)})); return 2


if __name__ == "__main__": raise SystemExit(main())
