"""Deterministic relation baseline over independent detector/OCR observations.

No model loading, label-derived proposals, network access or inference side effects.
"""
from __future__ import annotations

import copy
import math
import random
import hashlib
import re
from collections import Counter

from focus_dataset_contract import digest
from perception_benchmark import BenchmarkError, ROOT, _box, _iou, _sha256, _string, score

SETTINGS = {"version": "geometry-ocr-v1", "confidence": .75, "focusThreshold": .85,
            "iou": .5, "rowVerticalOverlap": .5, "semanticLocale": "en",
            "destructivePhrases": ["delete", "erase", "factory reset"],
            "informationalPhrases": ["information", "about this", "version"],
            "bootstrapSeed": 41, "bootstrapReplicates": 200}


def inside(box, parent):
    x, y, w, h = box; px, py, pw, ph = parent
    return px <= x+w/2 <= px+pw and py <= y+h/2 <= py+ph


def baseline(observation):
    """Only observation data enters this function; truth is unavailable here."""
    keep = lambda values: [v for v in values if v["confidence"] >= SETTINGS["confidence"]]
    rows = keep(observation["rows"])
    chevrons = []
    for arrow in keep(observation["chevrons"]):
        x, y, w, h = arrow["box"]
        matches = []
        for row in rows:
            rx, ry, rw, rh = row["box"]
            overlap = max(0, min(y+h, ry+rh)-max(y, ry))/h
            if overlap >= SETTINGS["rowVerticalOverlap"] and rx+rw*.5 <= x+w/2 <= rx+rw+rh:
                matches.append(row["id"])
        chevrons.append({"box": arrow["box"], "rowID": matches[0] if len(matches) == 1 else None})
    dialogs = keep(observation["dialogs"])
    dialog = None
    if len(dialogs) == 1:
        box = dialogs[0]["box"]
        buttons = [r for r in rows if r["role"] == "button" and inside(r["box"], box)]
        focused = [r["id"] for r in buttons if r.get("focusScore", 0) >= SETTINGS["focusThreshold"]]
        words = " ".join(t["text"].lower() for t in keep(observation["ocr"]) if inside(t["box"], box))
        semantics = "unknown"
        if observation["locale"].split("_")[0].split("-")[0] == "en":
            contains = lambda phrases: any(re.search(r"\b"+re.escape(p)+r"\b", words) for p in phrases)
            if contains(SETTINGS["destructivePhrases"]): semantics = "destructive"
            elif contains(SETTINGS["informationalPhrases"]): semantics = "informational"
        dialog = {"box": box, "buttonIDs": [r["id"] for r in buttons],
                  "focusedButtonID": focused[0] if len(focused) == 1 else None,
                  "semantic": semantics}
    return {"rows": rows, "chevrons": chevrons, "dialog": dialog,
            "dialogProposalCount": len(dialogs), "ambiguousDialog": len(dialogs) > 1}


def observation_predictions(document, cases):
    if not isinstance(document, dict) or document.get("formatVersion") != "perception-observations-v1":
        raise BenchmarkError("unsupported_observations")
    adapter = document.get("adapter")
    if not isinstance(adapter, dict) or adapter.get("kind") not in {"test-only", "imported-detector-ocr"}:
        raise BenchmarkError("invalid_observation_adapter")
    _string(adapter.get("id"), "missing_adapter_id")
    for field in ("artifactSHA256", "preprocessingSHA256"):
        _sha256(adapter.get(field))
    supplied = document.get("cases")
    if not isinstance(supplied, list): raise BenchmarkError("missing_observation_cases")
    known = {c["caseID"]: c for c in cases}; seen = set(); result = []
    for entry in supplied:
        if not isinstance(entry, dict) or entry.get("caseID") not in known or entry["caseID"] in seen:
            raise BenchmarkError("observation_membership_mismatch")
        seen.add(entry["caseID"]); case = known[entry["caseID"]]
        if entry.get("imageSHA256") != case["imageSHA256"]:
            raise BenchmarkError("observation_image_mismatch")
        state = entry.get("status")
        if state in {"failed", "unavailable"}:
            _string(entry.get("reason"), "missing_observation_failure")
            result.append({"caseID": entry["caseID"], "status": state, "reason": entry["reason"]})
            continue
        if state != "success": raise BenchmarkError("invalid_observation_status")
        # Explicit allowlist prevents accidental truth/context copying into baseline.
        observation = {"locale": _string(entry.get("locale"), "missing_observation_locale")}
        for kind in ("rows", "chevrons", "dialogs", "ocr"):
            values = entry.get(kind)
            if not isinstance(values, list): raise BenchmarkError("missing_observation_modality")
            observation[kind] = []
            ids = set()
            for value in values:
                if not isinstance(value, dict): raise BenchmarkError("invalid_observation")
                confidence = value.get("confidence")
                if type(confidence) not in (float, int) or not math.isfinite(confidence) or not 0 <= confidence <= 1:
                    raise BenchmarkError("invalid_observation_confidence")
                out = {"box": _box(value.get("box"), case["width"], case["height"]), "confidence": confidence}
                if kind == "rows":
                    rid = _string(value.get("id"), "missing_observation_row_id")
                    if rid in ids: raise BenchmarkError("duplicate_observation_row")
                    ids.add(rid)
                    if value.get("role") not in {"row", "button"}: raise BenchmarkError("invalid_observation_role")
                    out.update(id=rid, role=value["role"])
                    if "focusScore" in value:
                        v = value["focusScore"]
                        if type(v) not in (float, int) or not math.isfinite(v) or not 0 <= v <= 1:
                            raise BenchmarkError("invalid_focus_score")
                        out["focusScore"] = v
                if kind == "ocr": out["text"] = _string(value.get("text"), "invalid_ocr_text")
                observation[kind].append(out)
        actual = baseline(observation)
        # Oracle component experiment: boxes/element roles only; OCR and focus
        # scores remain observed inputs, not reviewed semantic/focus truth.
        oracle = copy.deepcopy(observation)
        oracle["rows"] = []
        for truth in case["labels"].get("rows", []):
            if "box" not in truth: continue
            matches = [r for r in observation["rows"] if _iou(r["box"], truth["box"]) >= .5]
            row = {"id": truth["id"], "box": truth["box"], "confidence": 1,
                   "role": "button" if truth["id"] in (case["labels"].get("dialog") or {}).get("buttonIDs", []) else "row"}
            if len(matches) == 1 and "focusScore" in matches[0]: row["focusScore"] = matches[0]["focusScore"]
            oracle["rows"].append(row)
        oracle["chevrons"] = [{"box": c["box"], "confidence": 1} for c in case["labels"].get("chevrons", []) if c["visibility"] in {"visible", "clipped"} and "box" in c]
        truth_dialog = case["labels"].get("dialog")
        oracle["dialogs"] = [{"box": truth_dialog["box"], "confidence": 1}] if truth_dialog else []
        result.append({"caseID": entry["caseID"], "status": "success", "proposals": actual, "oracle": baseline(oracle)})
    if seen != set(known): raise BenchmarkError("incomplete_observations")
    return {"formatVersion": "perception-predictions-v1", "status": "available", "cases": result}


def latency_report(document):
    timing = document.get("latency") if document else None
    if timing is None: return {"status": "unavailable", "reason": "no_measured_timing"}
    if not isinstance(timing, dict) or timing.get("kind") not in {"test-only", "measured-import"}:
        raise BenchmarkError("invalid_latency")
    for k in ("machine", "os", "scope"): _string(timing.get(k), "missing_latency_context")
    if timing["scope"] not in {"inference", "end-to-end"}: raise BenchmarkError("invalid_latency_scope")
    result = {k: timing[k] for k in ("kind", "machine", "os", "scope")}
    for kind in ("cold", "warm"):
        values = timing.get(kind)
        if not isinstance(values, list) or any(type(v) not in (int, float) or not math.isfinite(v) or v < 0 for v in values):
            raise BenchmarkError("invalid_latency_samples")
        values = sorted(values)
        result[kind] = {"n": len(values), **{key: values[math.ceil(p*len(values))-1] if values else None for key, p in (("p50", .5), ("p95", .95))}}
    result["status"] = "reported_not_independently_measured"
    result["deploymentQualified"] = False
    return result


def sliced_score(predictions, cases):
    overall = score(predictions, cases)
    slices = {}
    for field in ("sourceKind", "partition", "theme", "control", "locale", "focusTreatment", "rowState"):
        for value in sorted({str(c.get(field, "unknown")) for c in cases}):
            members = [c for c in cases if str(c.get(field, "unknown")) == value]
            ids = {c["caseID"] for c in members}
            sub = {**predictions, "cases": [e for e in predictions.get("cases", []) if e["caseID"] in ids]}
            slices[f"{field}:{value}"] = {"n": len(members), "journeys": len({c["journeyID"] for c in members}), **score(sub, members)}
    overall["slices"] = slices
    groups = {}
    for c in cases: groups.setdefault(c["splitGroup"], []).append(c)
    group_counts = []
    for members in groups.values():
        ids = {c["caseID"] for c in members}
        sub = {**predictions, "cases": [e for e in predictions.get("cases", []) if e["caseID"] in ids]}
        value = score(sub, members).get("actualProposals")
        if value: group_counts.append(value["counts"])
    interval = None
    if len(group_counts) >= 2:
        rng = random.Random(SETTINGS["bootstrapSeed"]); draws = []
        for _ in range(SETTINGS["bootstrapReplicates"]):
            counts = sum((Counter(rng.choice(group_counts)) for _ in group_counts), Counter())
            if counts["truthChevron"]: draws.append(counts["associatedTP"]/counts["truthChevron"])
        if draws:
            draws.sort(); interval = [draws[int(.025*(len(draws)-1))], draws[int(.975*(len(draws)-1))]]
    overall["uncertainty"] = {"method": "split-group-bootstrap-percentile-95", "groups": len(groups),
                               "disclosureRecallInterval": interval, "independentGeneralizationEstablished": False}
    return overall


def report(manifest, predictions, observations, cases, verification):
    bindings = {"manifestSHA256": digest(manifest), "predictionsSHA256": digest(predictions),
                "observationsSHA256": digest(observations) if observations else None,
                "settingsSHA256": digest(SETTINGS), "evaluatorSHA256": digest({
                    n: hashlib.sha256((ROOT/"scripts"/n).read_bytes()).hexdigest()
                    for n in ("perception_benchmark.py", "perception_adapters.py")})}
    imported = sliced_score(predictions, cases)
    comparisons = {"suppliedPredictions": {"execution": "external-assertion-not-executed-here", **imported},
                   "ttrRaster": {"status": "unavailable", "reason": "no_independent_ttr_raster_artifact_supplied"}}
    if observations:
        comparisons["geometryOCR"] = {"inputAdapter": observations.get("adapter"),
                                      **sliced_score(observation_predictions(observations, cases), cases)}
    else: comparisons["geometryOCR"] = {"status": "unavailable", "reason": "independent_observations_not_supplied"}
    analysis = []
    for case in cases:
        if case["partition"] != "development": continue
        entry = next((p for p in predictions.get("cases", []) if p["caseID"] == case["caseID"]), None)
        if entry is None or entry.get("status") in {"failed", "unavailable"}:
            analysis.append({"caseID": case["caseID"], "category": "missing_adapter_or_execution_failure",
                             "next": "Supply independent observations; do not infer a classifier deficit."})
            continue
        one = score({**predictions, "cases": [entry]}, [case])
        actual = one["actualProposals"]["counts"]; oracle = one["oracleBoxes"]["counts"]
        category = "no_measured_gap"
        if actual.get("abstentions", 0) > oracle.get("abstentions", 0) or actual.get("dialogLocalizationMiss", 0):
            category = "proposal_geometry"
        elif actual.get("wrongRowLink", 0) or actual.get("associationAbstentions", 0) or actual.get("buttonMembershipError", 0): category = "association_geometry"
        elif actual.get("destructiveAsBenign", 0) or actual.get("semanticAbstentions", 0): category = "ocr_semantics_or_missing_labels"
        elif actual.get("dialogFocusError", 0): category = "focus_classifier_or_proposal"
        analysis.append({"caseID": case["caseID"], "category": category, "diagnosis": "rule-based triage; requires reviewed evidence"})
    return {"formatVersion": "perception-benchmark-report-v1.1", "bindings": bindings,
            "settings": SETTINGS, "prediction": imported, "comparisons": comparisons,
            "latency": latency_report(observations or predictions),
            "byteVerification": verification, "trainingEligible": False, "modelGatePassed": "not_assessed",
            "developmentErrorAnalysis": analysis,
            "suppliedAdapter": predictions.get("adapter", {"status": "unavailable", "reason": "no_model_or_preprocessing_identity_declared"}),
            "recommendation": {"action": "no_training", "reason": "offline_or_imported_evidence_requires_review_and_assigned_real_baseline",
                               "requiredBeforeTraining": ["eligible_held_out_support", "measured_gap", "reviewed_numeric_gates", "latency_budget", "explicit_authorization"]},
            "next": "Review development errors by slice; prefer a geometry/OCR correction when oracle components succeed. Missing input/labels and producer runtime failures are not model failures."}
