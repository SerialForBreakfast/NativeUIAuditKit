"""Explicit human-reviewed development evaluation. No training or challenge scoring."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import time

import human_annotation_review as h
from human_review_audit import audit
from focus_ring_baseline import evaluate, model_contract
from focus_runtime import RUNTIME_PREPROCESSING, bounded_batches, invoke
from focus_surface_evaluation import runtime, seal_check
from focus_surface_intake import fresh, write

VERSION = "human-focus-development-evaluation-v1"
ROLE = "development-regression"
POLICY = dict(trainingEligible=False, independentEvaluationEligible=False,
              developmentEvaluationEligible=True, completeFrameCandidates=False,
              finalChallengeScored=False, modelGatePassed="not_assessed")
CODE = ("human_focus_evaluation.py", "human_review_audit.py", "human_annotation_review.py",
        "photos_focus_pilot.py", "focus_ring_baseline.py", "focus_ring_backbone.py",
        "focus_runtime.py", "focus_surface_evaluation.py", "focus_dataset_contract.py")


def check(ref):
    return h.checked(h.ROOT, ref)


def admitted(revision, crops):
    h.require(h.read_revision(revision)['version'] == h.REVISION,
              'focus_role_evaluation_requires_separate_admission')
    report = audit(revision, crops)
    h.require(report["reviewer"]["kind"] == "human", "human_review_required")
    h.require(not any(i["severity"] == "hard" for i in report["issues"]), "unresolved_audit_errors")
    h.require(report["samples"] and all(s["disposition"] == "reviewed" for s in report["samples"]),
              "incomplete_review")
    frames = {f["id"]: f for f in report["frames"]}
    rows = [{**s, "label": int(s["state"] == "focused"), "family": s["screen"],
             "theme": "unknown", "control": s["class"], "hard": False,
             "image": frames[s["frameID"]]["image"]} for s in report["samples"]]
    return report, rows


def role_audit(report, specs):
    """Read protected metadata/hashes only; never expose protected rows to inference."""
    h.require({s["kind"] for s in specs} == {"training-retention", "reserved", "historical-protected"},
              "missing_role_inventory")
    local_hashes = {r["sha256"] for r in report["inputs"]}
    local_pixels = {s["pixelSHA256"] for s in report["samples"]} | {f["pixelSHA256"] for f in report["frames"]}
    source_session = report["coverage"]["sessionID"]
    result = []
    for spec in specs:
        doc = h.read(check(spec["manifest"]))
        rows = doc.get("remotesSamples") if spec["kind"] == "historical-protected" else doc.get("samples")
        if spec["kind"] == "historical-protected" and isinstance(rows, list):
            rows = list(rows)
            for visual in doc.get("visualDiagnostics", []):
                check(visual["protocol"])
                rows.extend(dict(id=visual["surface"]+":"+str(i), frame=frame,
                                 relatedGroup=visual["surface"], role=visual["role"])
                            for i,frame in enumerate(visual["frames"]))
        h.require(isinstance(rows, list) and rows, "empty_role_manifest")
        matches, sources, missing = [], set(), 0
        for row in rows:
            sources.add(str(row.get("relatedGroup", row.get("group", "unknown"))))
            records = [row.get("frame", {k: row[k] for k in ("path", "sha256") if k in row}), row.get("crop", {})]
            pixels = [records[0].get("pixelSHA256", row.get("framePixelSHA256")), records[1].get("pixelSHA256")]
            for rec, pixel in zip(records, pixels):
                if not rec.get("path") or not rec.get("sha256") or not pixel:
                    missing += 1
                    continue
                # The manifest is the retained provenance index. Byte hashes verify the
                # referenced pixels still exist; decoded hash assertions stay attributed
                # to that manifest rather than pretending this is a new corpus audit.
                check(rec)
                if rec["sha256"] in local_hashes or pixel in local_pixels:
                    matches.append(dict(id=row["id"], path=rec["path"], kind="exact-content"))
            if row.get("sessionID") == source_session:
                matches.append(dict(id=row["id"], kind="same-session"))
        result.append(dict(kind=spec["kind"], manifest=spec["manifest"], members=len(rows),
                           roles=dict(Counter(r.get("use", r.get("role", r.get("split", "unknown"))) for r in rows)),
                           relatedGroups=sorted(sources), matches=matches, missingPixelReferences=missing))
    return dict(inventories=result, sourceGroup="office:"+source_session,
                independence="unknown", pixelEvidence="verified byte references; retained decoded-hash index",
                caveats=["Different devices/sessions do not prove independent UI layouts.",
                         "Home and Settings are related OS screen families; no unseen-family claim.",
                         "Shipped training ancestry is not exhaustively represented by these retained manifests."])


def approval_check(approval, report, revision, crops):
    h.require(approval.get("version") == "human-focus-evaluation-approval-v1"
              and approval.get("approved") is True and approval.get("maxRuns") == 1
              and approval.get("role") == ROLE and approval.get("reviewer")
              and approval.get("authorizationReference") and approval.get("threshold") == .85
              and approval.get("trainingApproved") is False and approval.get("promotionApproved") is False,
              "missing_or_wrong_approval")
    h.require(approval["revision"] == h.ref(revision) and approval["crops"] == h.ref(crops), "wrong_approved_revision")
    h.require(approval["membership"] == [s["id"] for s in report["samples"]]
              and approval["pairs"] == report["pairs"] and approval["coverage"] == report["coverage"],
              "changed_approved_membership")
    h.require(set(approval["models"]) == {"shipped", "fdr009"}, "wrong_model_roles")


def freeze(approval_path, output):
    output = fresh(output)
    approval = h.read(approval_path)
    revision, crops = check(approval["revision"]), check(approval["crops"])
    report, rows = admitted(revision, crops)
    approval_check(approval, report, revision, crops)
    doc = dict(version=VERSION, **POLICY, role=ROLE, approval=h.ref(approval_path),
               revision=h.ref(revision), crops=h.ref(crops), samples=rows, pairs=report["pairs"],
               source=report["coverage"], reviewer=report["reviewer"], inputs=report["inputs"],
               duplicateGroups=report["exactCropDuplicateGroups"],
               overlap=role_audit(report, approval["roleManifests"]), threshold=.85,
               preprocessing=RUNTIME_PREPROCESSING, models=approval["models"], runtime=runtime(),
               implementation=[h.ref(h.ROOT/"scripts"/name) for name in CODE], output=approval["output"])
    doc["seal"] = h.digest(doc)
    validate(doc)
    output.parent.mkdir(parents=True, exist_ok=True)
    write(output, doc)
    return doc


def validate(doc):
    seal_check(doc)
    h.require(doc.get("version") == VERSION and doc.get("role") == ROLE
              and all(doc.get(k) == v for k, v in POLICY.items())
              and doc.get("threshold") == .85 and doc.get("preprocessing") == RUNTIME_PREPROCESSING,
              "unsupported_human_evaluation_policy")
    approval = h.read(check(doc["approval"]))
    revision, crops = check(doc["revision"]), check(doc["crops"])
    report, rows = admitted(revision, crops)
    approval_check(approval, report, revision, crops)
    h.require(doc["samples"] == rows and doc["pairs"] == report["pairs"] and doc["inputs"] == report["inputs"]
              and doc["source"] == report["coverage"] and doc["reviewer"] == report["reviewer"]
              and doc["duplicateGroups"] == report["exactCropDuplicateGroups"], "changed_membership")
    h.require(doc["overlap"] == role_audit(report, approval["roleManifests"]), "changed_role_inventory")
    h.require(doc["runtime"] == runtime() and doc["runtime"]["crop"] == h.read(crops)["runtime"], "changed_runtime")
    h.require(doc["implementation"] == [h.ref(h.ROOT/"scripts"/name) for name in CODE], "changed_implementation")
    h.require(doc["models"] == approval["models"] and doc["output"] == approval["output"], "changed_execution_binding")
    check(doc["models"]["fdr009"])
    shipped = doc["models"]["shipped"]
    h.require(model_contract(h.local(h.ROOT/shipped["path"])) == {k:v for k,v in shipped.items() if k != "path"},
              "changed_shipped_model")


def metrics(rows, predictions, pairs):
    h.require([r["id"] for r in rows] == [p.get("id") for p in predictions], "prediction_membership")
    h.require(all(type(p.get("probability")) in (float, int) and math.isfinite(p["probability"])
                  and 0 <= p["probability"] <= 1 for p in predictions), "invalid_probability")
    values = {p["id"]:p["probability"] for p in predictions}
    def summarize(subset):
        if not subset:
            return {"status":"unavailable", "n":0}
        result = evaluate(subset, {r["id"]:values[r["id"]] for r in subset}, require_hard=False)
        result["threshold"] = {"value":.85, "purpose":"fixed human development comparison; no tuning"}
        for g in result["groups"].values():
            for k in ("tp", "tn", "fp", "fn"): g.setdefault(k, 0)
            g["positiveSupport"], g["negativeSupport"] = g["tp"]+g["fn"], g["tn"]+g["fp"]
            if not g["positiveSupport"]: g["recall"] = None
            if not g["tp"]+g["fp"]: g["precision"] = None
        return result
    unique, seen = [], set()
    for row in rows:
        if row["pixelSHA256"] not in seen:
            unique.append(row); seen.add(row["pixelSHA256"])
    by_id = {r["id"]:r for r in rows}
    outcomes = []
    for pair in pairs:
        ids = [f+":"+pair["controlID"] for f in pair["frames"]]
        h.require(len(ids) == 2 and len(set(ids)) == 2 and all(i in by_id for i in ids)
                  and {by_id[i]["label"] for i in ids} == {0, 1}, "invalid_pair_membership")
        pos = next(i for i in ids if by_id[i]["label"])
        neg = next(i for i in ids if not by_id[i]["label"])
        outcomes.append(dict(id=pair["id"], members=ids, focusedScore=values[pos], unfocusedScore=values[neg],
                             delta=values[pos]-values[neg], bothCorrect=values[pos] >= .85 and values[neg] < .85))
    return dict(full=summarize(rows), duplicateSensitivity=summarize(unique), pairs=outcomes,
                completeFrameSelection={"status":"unavailable", "reason":"candidate completeness unknown"},
                accounted=len(rows))


def infer(name, doc, predictions, receipts):
    """Established production crop/helper and vendored CPU candidate path."""
    rows = doc["samples"]
    if name == "shipped":
        items = [dict(id=r["id"], path=str(check(r["image"])), sha256=r["image"]["sha256"], bounds=r["bounds"]) for r in rows]
        for batch in bounded_batches(items):
            reply = invoke(batch, h.ROOT/doc["models"][name]["path"])
            h.require(reply.get("computeUnits") == "cpuOnly", "wrong_coreml_backend")
            predictions.extend({k:r[k] for k in ("id", "probability")} for r in reply["results"])
            receipts.append({k:v for k,v in reply.items() if k != "results"})
    else:
        import numpy as np
        import torch
        from PIL import Image
        from focus_ring_backbone import mobilenetv4_conv_small
        torch.set_num_threads(2)
        model = mobilenetv4_conv_small(pretrained=False, num_classes=1)
        checkpoint = torch.load(check(doc["models"][name]), map_location="cpu", weights_only=True)
        model.load_state_dict(checkpoint["state_dict"], strict=True)
        model.eval()
        receipts.append(dict(device=str(next(model.parameters()).device), threads=torch.get_num_threads(),
                             epoch=checkpoint.get("epoch"), artifact=doc["models"][name]))
        with torch.inference_mode():
            for offset in range(0, len(rows), 32):
                members = rows[offset:offset+32]
                tensors = []
                for r in members:
                    with Image.open(check(r["crop"])) as im:
                        tensors.append(torch.from_numpy(np.array(im.convert("RGB"), copy=True)).permute(2,0,1).float().div(255))
                values = torch.sigmoid(model(torch.stack(tensors))).view(-1).tolist()
                predictions.extend(dict(id=r["id"], probability=p) for r,p in zip(members,values,strict=True))


def run(protocol_path, output):
    doc = h.read(protocol_path)
    validate(doc)
    output = fresh(output)
    h.require(str(output.relative_to(h.ROOT)) == doc["output"], "unapproved_output")
    # One approval permits one launch, even if a caller proposes another directory.
    marker = check(doc["approval"]).with_suffix(".started.json")
    write(marker, dict(protocol=h.ref(protocol_path), startedAt=datetime.now(timezone.utc).isoformat()))
    output.mkdir(parents=True)
    results = {}
    for name in ("shipped", "fdr009"):
        predictions, receipts = [], []
        started = time.monotonic()
        try:
            infer(name, doc, predictions, receipts)
            result = dict(state="complete", metrics=metrics(doc["samples"], predictions, doc["pairs"]))
        except Exception as error:
            result = dict(state="failed", error=f"{type(error).__name__}: {error}", metrics=None)
        # Preserve invalid-score diagnostics as strings, never non-finite JSON.
        # A bad engine must still leave a complete accounting receipt.
        invalid = []
        valid = []
        expected_ids = {r["id"] for r in doc["samples"]}
        seen = set()
        for p in predictions:
            value = p.get("probability")
            if (p.get("id") not in expected_ids or p.get("id") in seen
                    or type(value) not in (int,float) or not math.isfinite(value) or not 0 <= value <= 1):
                invalid.append(dict(id=str(p.get("id")), probability=repr(value)))
            else:
                valid.append(p); seen.add(p["id"])
        predictions = valid
        ids = {p.get("id") for p in predictions}
        result.update(predictions=predictions, invalidPredictions=invalid, receipts=receipts, model=doc["models"][name],
                      expected=len(doc["samples"]), scored=len(predictions),
                      unscored=[r["id"] for r in doc["samples"] if r["id"] not in ids],
                      protocol=h.ref(protocol_path), runtime=doc["runtime"],
                      backend="CoreML CPU" if name == "shipped" else "PyTorch CPU",
                      elapsedSeconds=time.monotonic()-started)
        write(output/(name+".json"), result)
        results[name] = result
        print(json.dumps(dict(model=name,state=result["state"],scored=len(predictions))), flush=True)
    postflight = None
    try: validate(doc)
    except Exception as error: postflight = str(error)
    report = dict(version=VERSION, **POLICY, protocol=h.ref(protocol_path), results=results,
                  postflightError=postflight, completed=postflight is None and all(r["state"] == "complete" for r in results.values()))
    write(output/"comparison.json", report)
    return report


def render(protocol_path, comparison_path, output):
    """No inference; deterministic numbered misses/FPs with full-frame context."""
    from PIL import Image, ImageDraw
    doc, result = h.read(protocol_path), h.read(comparison_path)
    # BP-106: retained-score reporting needs reviewed pixels and bindings, not
    # model residency, the old runtime or traversal of protected corpora.
    seal_check(doc)
    h.require(doc.get("version") == VERSION and doc.get("role") == ROLE
              and all(doc.get(k) == v for k,v in POLICY.items()) and doc.get("threshold") == .85
              and doc.get("preprocessing") == RUNTIME_PREPROCESSING, "unsupported_retained_protocol")
    approval = h.read(check(doc["approval"]))
    revision, crops = check(doc["revision"]), check(doc["crops"])
    reviewed, rows = admitted(revision,crops)
    approval_check(approval,reviewed,revision,crops)
    h.require(rows == doc["samples"] and reviewed["pairs"] == doc["pairs"]
              and doc["models"] == approval["models"], "changed_retained_membership")
    h.require(result["protocol"] == h.ref(protocol_path) and result["completed"], "incomplete_comparison")
    output = fresh(output); output.mkdir(parents=True)
    index = []
    for name in ("shipped", "fdr009"):
        outcome = result["results"][name]
        h.require(outcome["state"] == "complete" and outcome["model"] == doc["models"][name]
                  and outcome["protocol"] == h.ref(protocol_path), "incompatible_retained_scores")
        measured = metrics(doc["samples"], outcome["predictions"], doc["pairs"])
        h.require(measured == outcome["metrics"], "changed_metrics")
        values = {p["id"]:p["probability"] for p in outcome["predictions"]}
        errors = [r for r in doc["samples"] if (values[r["id"]] >= .85) != bool(r["label"])]
        errors.sort(key=lambda r:(-r["label"], values[r["id"]] if r["label"] else -values[r["id"]], r["id"]))
        for row in errors:
            number = len(index)+1
            with Image.open(check(row["image"])) as im: context = im.convert("RGB")
            x,y,w,height = row["bounds"]
            ImageDraw.Draw(context).rectangle((x,y,x+w,y+height),outline="red",width=6)
            context.thumbnail((960,540))
            sheet = Image.new("RGB", (1240,600), "white"); sheet.paste(context,(0,45))
            with Image.open(check(row["crop"])) as im: sheet.paste(im.convert("RGB"),(970,45))
            kind = "miss" if row["label"] else "false-positive"
            text = f"{number:03d} {name} {row['id']} {row['control']} {kind} p={values[row['id']]:.6f} threshold=0.85"
            ImageDraw.Draw(sheet).text((10,10),text,fill="black")
            path = output/f"{number:03d}-{name}.png"; sheet.save(path)
            index.append(dict(number=number, model=name, sample=row["id"], kind=kind,
                              probability=values[row["id"]], sheet=h.ref(path)))
    write(output/"index.json", dict(protocol=h.ref(protocol_path), comparison=h.ref(comparison_path), errors=index))
    return index


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("freeze", "run", "render"))
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--comparison", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "freeze": freeze(args.input, args.output)
        elif args.command == "render": render(args.input, args.comparison, args.output)
        else: h.require(run(args.input, args.output)["completed"], "incomplete_comparison")
    except (ValueError, OSError, KeyError, TypeError) as error: parser.exit(2,str(error)+"\n")


if __name__ == "__main__": main()
