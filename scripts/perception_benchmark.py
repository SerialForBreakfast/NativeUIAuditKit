#!/usr/bin/env python3
"""Validate and score the versioned chevron/dialog perception benchmark offline."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
VERSION = "perception-benchmark-v1"
PREDICTION_VERSION = "perception-predictions-v1"
SOURCE_KINDS = {"physicalFixture", "simulatorFixture", "testOnly"}
PARTITIONS = {"development", "validation", "test"}
LABEL_ORIGINS = {"reviewedVisual", "fixtureGroundTruth"}
VISIBILITIES = {"visible", "occluded", "clipped", "absent", "unknown"}
SEMANTICS = {"destructive", "informational", "unknown"}
IOU = 0.5


class BenchmarkError(ValueError):
    pass


def _string(value: Any, error: str) -> str:
    if not isinstance(value, str) or not value:
        raise BenchmarkError(error)
    return value


def _sha256(value: Any, error: str = "invalid_sha256") -> str:
    value = _string(value, error)
    if len(value) != 64 or any(char not in "0123456789abcdef" for char in value.lower()):
        raise BenchmarkError(error)
    return value.lower()


def _box(value: Any, width: int, height: int) -> list[float]:
    if not isinstance(value, list) or len(value) != 4 or not all(type(item) in (int, float) and math.isfinite(item) for item in value):
        raise BenchmarkError("invalid_box")
    x, y, w, h = map(float, value)
    if x < 0 or y < 0 or w <= 0 or h <= 0 or x + w > width or y + h > height:
        raise BenchmarkError("box_out_of_frame")
    return [x, y, w, h]


def _iou(left: list[float], right: list[float]) -> float:
    lx, ly, lw, lh = left; rx, ry, rw, rh = right
    ix = max(0.0, min(lx + lw, rx + rw) - max(lx, rx))
    iy = max(0.0, min(ly + lh, ry + rh) - max(ly, ry))
    union = lw * lh + rw * rh - ix * iy
    return 0.0 if union <= 0 else ix * iy / union


def validate_manifest(document: dict[str, Any]) -> list[dict[str, Any]]:
    if document.get("formatVersion") != VERSION or not isinstance(document.get("cases"), list):
        raise BenchmarkError("unsupported_manifest")
    seen_ids: set[str] = set(); image_groups: dict[str, str] = {}; group_partitions: dict[str, str] = {}; journey_partitions: dict[str, str] = {}
    cases: list[dict[str, Any]] = []
    for case in document["cases"]:
        if not isinstance(case, dict):
            raise BenchmarkError("invalid_case")
        case_id = _string(case.get("caseID"), "invalid_case_id")
        if case_id in seen_ids: raise BenchmarkError("duplicate_case_id")
        seen_ids.add(case_id)
        source = case.get("sourceKind")
        if source not in SOURCE_KINDS: raise BenchmarkError("unsupported_source_kind")
        width, height = case.get("width"), case.get("height")
        if type(width) is not int or type(height) is not int or width <= 0 or height <= 0:
            raise BenchmarkError("invalid_dimensions")
        digest = _sha256(case.get("imageSHA256"))
        journey = _string(case.get("journeyID"), "invalid_journey")
        group = _string(case.get("splitGroup"), "invalid_split_group")
        partition = case.get("partition")
        if partition not in PARTITIONS: raise BenchmarkError("invalid_partition")
        if group in group_partitions and group_partitions[group] != partition: raise BenchmarkError("split_group_leakage")
        if journey in journey_partitions and journey_partitions[journey] != partition: raise BenchmarkError("journey_leakage")
        if digest in image_groups and image_groups[digest] != group: raise BenchmarkError("duplicate_content_leakage")
        group_partitions[group] = partition; journey_partitions[journey] = partition; image_groups[digest] = group
        labels = case.get("labels")
        if not isinstance(labels, dict) or labels.get("origin") not in LABEL_ORIGINS:
            raise BenchmarkError("unreviewed_or_prediction_labels")
        if labels.get("origin") == "modelPrediction": raise BenchmarkError("prediction_labels_forbidden")
        rows = labels.get("rows", [])
        if not isinstance(rows, list): raise BenchmarkError("invalid_rows")
        row_ids = set()
        for row in rows:
            if not isinstance(row, dict): raise BenchmarkError("invalid_row")
            row_id = _string(row.get("id"), "invalid_row_id")
            if row_id in row_ids: raise BenchmarkError("duplicate_row_id")
            row_ids.add(row_id)
            if "box" in row: _box(row["box"], width, height)
        chevrons = labels.get("chevrons", [])
        if not isinstance(chevrons, list): raise BenchmarkError("invalid_chevrons")
        chevron_ids = set()
        for chevron in chevrons:
            if not isinstance(chevron, dict): raise BenchmarkError("invalid_chevron")
            chevron_id = _string(chevron.get("id"), "invalid_chevron_id")
            if chevron_id in chevron_ids: raise BenchmarkError("duplicate_chevron_id")
            chevron_ids.add(chevron_id)
            visibility = chevron.get("visibility")
            if visibility not in VISIBILITIES: raise BenchmarkError("invalid_chevron_visibility")
            if visibility == "visible" or (visibility == "clipped" and chevron.get("box") is not None):
                _box(chevron.get("box"), width, height)
                if chevron.get("rowID") not in row_ids: raise BenchmarkError("ambiguous_chevron_relation")
            elif chevron.get("rowID") is not None or chevron.get("box") is not None:
                raise BenchmarkError("nonvisible_chevron_has_relation")
        dialog = labels.get("dialog")
        if dialog is not None:
            if not isinstance(dialog, dict): raise BenchmarkError("invalid_dialog")
            _box(dialog.get("box"), width, height)
            buttons = dialog.get("buttonIDs")
            if not isinstance(buttons, list) or not buttons or not all(button in row_ids for button in buttons):
                raise BenchmarkError("invalid_dialog_buttons")
            focused = dialog.get("focusedButtonID")
            if focused is not None and focused not in buttons: raise BenchmarkError("invalid_dialog_focus")
            if dialog.get("semantic") not in SEMANTICS: raise BenchmarkError("invalid_dialog_semantic")
            if dialog.get("semantic") != "unknown" and dialog.get("semanticOrigin") != "reviewed":
                raise BenchmarkError("unreviewed_dialog_semantic")
        focus = labels.get("focus")
        if focus is not None:
            if not isinstance(focus, dict) or focus.get("elementID") not in row_ids or focus.get("frameID") != case_id:
                raise BenchmarkError("stale_or_invalid_focus")
        cases.append(case)
    return cases


def inventory(cases: list[dict[str, Any]]) -> dict[str, Any]:
    coverage: Counter[str] = Counter(); sources: Counter[str] = Counter(); partitions: Counter[str] = Counter()
    for case in cases:
        labels = case["labels"]; sources[case["sourceKind"]] += 1; partitions[case["partition"]] += 1
        for chevron in labels.get("chevrons", []): coverage[f"chevron:{chevron['visibility']}"] += 1
        if labels.get("dialog"):
            coverage[f"dialog:{labels['dialog']['semantic']}"] += 1
            coverage["dialog:withFocus" if labels["dialog"].get("focusedButtonID") else "dialog:noFocus"] += 1
        if labels.get("focus"): coverage["focus:observed"] += 1
    return {"caseCount": len(cases), "sourceKinds": dict(sources), "partitions": dict(partitions), "coverage": dict(coverage)}


def verify_evidence(cases: list[dict[str, Any]]) -> dict[str, int]:
    """Verify explicitly listed local evidence bytes without scanning for replacements."""
    verified = 0
    pixel_partitions = {}
    for case in cases:
        raw_path = _string(case.get("imagePath"), "missing_image_path")
        path = Path(raw_path).resolve()
        try:
            path.relative_to(ROOT)
        except ValueError as error:
            raise BenchmarkError("image_path_outside_package") from error
        if not path.is_file(): raise BenchmarkError("missing_image")
        from focus_dataset_contract import image, pixel_digest, FocusDataError
        try:
            record = {"path": str(path.relative_to(ROOT)), "sha256":case["imageSHA256"]}
            image(ROOT, record, (case["width"],case["height"]))
            pixels = pixel_digest(ROOT, record)
            if pixels in pixel_partitions and pixel_partitions[pixels] != case["partition"]:
                raise BenchmarkError("decoded_content_split_leakage")
            pixel_partitions[pixels] = case["partition"]
        except FocusDataError as error:
            raise BenchmarkError("image_hash_mismatch" if str(error)=="changed_hash" else str(error)) from error
        verified += 1
    return {"verifiedImageCount": verified}


def _predictions(document: dict[str, Any], cases: list[dict[str, Any]]) -> dict[str, dict[str, Any]] | None:
    if document.get("formatVersion") != PREDICTION_VERSION: raise BenchmarkError("unsupported_predictions")
    if document.get("status") == "unavailable":
        _string(document.get("reason"), "missing_prediction_reason")
        return None
    if document.get("status") != "available" or not isinstance(document.get("cases"), list): raise BenchmarkError("invalid_predictions")
    entries: dict[str, dict[str, Any]] = {}
    valid_ids = {case["caseID"] for case in cases}
    for entry in document["cases"]:
        if not isinstance(entry, dict): raise BenchmarkError("invalid_prediction_case")
        case_id = _string(entry.get("caseID"), "invalid_prediction_case")
        if case_id not in valid_ids or case_id in entries: raise BenchmarkError("prediction_membership_mismatch")
        entries[case_id] = entry
    if set(entries) != valid_ids: raise BenchmarkError("incomplete_predictions")
    return entries


def _score_relation(cases: list[dict[str, Any]], entries: dict[str, dict[str, Any]], key: str) -> dict[str, Any]:
    counts = Counter()
    for case in cases:
        width, height = case["width"], case["height"]; labels = case["labels"]
        if key not in entries[case["caseID"]]: raise BenchmarkError("missing_oracle_or_proposal_predictions")
        candidate = entries[case["caseID"]][key]
        if not isinstance(candidate, dict): raise BenchmarkError("invalid_prediction_payload")
        if "chevrons" not in candidate or "dialog" not in candidate:
            raise BenchmarkError("missing_prediction_modality")
        row_map = None
        if "rows" in candidate:
            if not isinstance(candidate["rows"], list): raise BenchmarkError("invalid_predicted_rows")
            row_map = {}
            for row in candidate["rows"]:
                if not isinstance(row, dict): raise BenchmarkError("invalid_predicted_row")
                rid = _string(row.get("id"), "invalid_predicted_row_id")
                if rid in row_map: raise BenchmarkError("duplicate_predicted_row")
                box = _box(row.get("box"), width, height)
                matches = [r["id"] for r in labels.get("rows", []) if "box" in r and _iou(box, r["box"]) >= IOU]
                row_map[rid] = matches[0] if len(matches) == 1 else None
        resolve = lambda rid: row_map.get(rid) if row_map is not None else rid
        predicted = candidate.get("chevrons", [])
        if not isinstance(predicted, list): raise BenchmarkError("invalid_predicted_chevrons")
        truth = [item for item in labels.get("chevrons", []) if item["visibility"] in {"visible", "clipped"} and "box" in item]
        used: set[int] = set()
        for proposal in predicted:
            if not isinstance(proposal, dict): raise BenchmarkError("invalid_predicted_chevron")
            box = _box(proposal.get("box"), width, height); best = None; best_iou = 0.0
            for index, expected in enumerate(truth):
                if index not in used and _iou(box, expected["box"]) > best_iou: best, best_iou = index, _iou(box, expected["box"])
            if best is None or best_iou < IOU:
                counts["decorativeArrowFP"] += 1; continue
            used.add(best); counts["localizedTP"] += 1
            if proposal.get("rowID") is not None and not isinstance(proposal["rowID"], str): raise BenchmarkError("invalid_predicted_row_id")
            if proposal.get("rowID") is None: counts["associationAbstentions"] += 1
            elif resolve(proposal.get("rowID")) == truth[best]["rowID"]: counts["associatedTP"] += 1
            else: counts["wrongRowLink"] += 1
        counts["truthChevron"] += len(truth); counts["abstentions"] += max(0, len(truth) - len(used))
        dialog_truth = labels.get("dialog"); dialog = candidate.get("dialog")
        if dialog is not None:
            if not isinstance(dialog, dict): raise BenchmarkError("invalid_predicted_dialog")
            _box(dialog.get("box"), width, height)
            buttons = dialog.get("buttonIDs")
            if not isinstance(buttons, list) or any(not isinstance(b, str) for b in buttons) or len(set(buttons)) != len(buttons):
                raise BenchmarkError("invalid_predicted_buttons")
            focus = dialog.get("focusedButtonID")
            if focus is not None and (not isinstance(focus, str) or focus not in buttons): raise BenchmarkError("invalid_predicted_focus")
            if dialog.get("semantic") not in SEMANTICS: raise BenchmarkError("invalid_predicted_semantic")
        if dialog_truth is not None:
            counts["truthDialogs"] += 1
            counts["truthDestructive"] += int(dialog_truth["semantic"] == "destructive")
            if dialog is None: counts["dialogAbstentions"] += 1
            elif not isinstance(dialog, dict): raise BenchmarkError("invalid_predicted_dialog")
            elif _iou(_box(dialog.get("box"), width, height), dialog_truth["box"]) < IOU: counts["dialogLocalizationMiss"] += 1
            else:
                counts["dialogLocalizedTP"] += 1
                if {resolve(b) for b in dialog["buttonIDs"]} == set(dialog_truth["buttonIDs"]): counts["buttonMembershipTP"] += 1
                else: counts["buttonMembershipError"] += 1
                if dialog_truth.get("focusedButtonID") is not None:
                    if resolve(dialog.get("focusedButtonID")) == dialog_truth["focusedButtonID"]: counts["dialogFocusTP"] += 1
                    else: counts["dialogFocusError"] += 1
                elif dialog.get("focusedButtonID") is not None: counts["unexpectedDialogFocus"] += 1
                semantic = dialog.get("semantic")
                if semantic not in SEMANTICS: raise BenchmarkError("invalid_predicted_semantic")
                if semantic == "unknown": counts["semanticAbstentions"] += 1
                if semantic == "unknown" and dialog_truth["semantic"] == "destructive": counts["destructiveAbstentions"] += 1
                if dialog_truth["semantic"] == "destructive" and semantic == "informational": counts["destructiveAsBenign"] += 1
        elif dialog is not None: counts["dialogFP"] += 1
    recall = counts["associatedTP"] / counts["truthChevron"] if counts["truthChevron"] else None
    return {"counts": dict(counts), "endToEndDisclosureRecall": recall}


def score(document: dict[str, Any], cases: list[dict[str, Any]]) -> dict[str, Any]:
    entries = _predictions(document, cases)
    if entries is None:
        return {"status": "unavailable", "reason": document["reason"], "actualProposals": None, "oracleBoxes": None}
    usable = []
    failures = []
    for case in cases:
        entry = entries[case["caseID"]]; state = entry.get("status", "success")
        if state in {"failed", "unavailable"}:
            failures.append({"caseID": case["caseID"], "status": state, "reason": _string(entry.get("reason"), "missing_prediction_reason")})
        elif state == "success": usable.append(case)
        else: raise BenchmarkError("invalid_prediction_status")
    return {"status": "partial" if failures else "available", "attemptedCases": len(cases), "scoredCases": len(usable),
            "failures": failures, "actualProposals": _score_relation(usable, entries, "proposals"),
            "oracleBoxes": _score_relation(usable, entries, "oracle")}


def recommendation(cases: list[dict[str, Any]], result: dict[str, Any]) -> dict[str, Any]:
    eligible = [case for case in cases if case["sourceKind"] == "physicalFixture" and case["partition"] == "test"]
    if not eligible or result["status"] != "available":
        return {"action": "no_training", "reason": "no_eligible_held_out_physical_benchmark_with_available_inference", "heldOutSupport": len(eligible)}
    actual = result["actualProposals"]; counts = actual["counts"]
    if counts.get("wrongRowLink", 0) or counts.get("destructiveAsBenign", 0):
        return {"action": "review_targeted_training", "reason": "measured_relation_or_safety_gap", "heldOutSupport": len(eligible), "requiredBeforeTraining": ["reviewed_numeric_gates", "held_out_support", "latency_budget"]}
    return {"action": "no_training", "reason": "no_measured_targeted_gap", "heldOutSupport": len(eligible)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True); parser.add_argument("--predictions", type=Path, required=True); parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--verify-bytes", action="store_true", help="Verify explicitly declared in-package image paths and hashes")
    parser.add_argument("--observations", type=Path, help="Independent detector/OCR observations for deterministic geometry baseline")
    args = parser.parse_args(); output = args.output.resolve()
    try: output.relative_to(ROOT)
    except ValueError: print("ERROR: output must stay inside package", file=sys.stderr); return 2
    if output.exists(): print("ERROR: refusing output collision", file=sys.stderr); return 2
    try:
        manifest = json.loads(args.manifest.read_text())
        predictions = json.loads(args.predictions.read_text())
        cases = validate_manifest(manifest)
        verification = verify_evidence(cases) if args.verify_bytes or any(c["sourceKind"] != "testOnly" for c in cases) else {"status": "test_only_not_requested"}
        from perception_adapters import report as make_report
        observations = json.loads(args.observations.read_text()) if args.observations else None
        report = make_report(manifest, predictions, observations, cases, verification)
        report["inventory"] = inventory(cases)
    except (OSError, json.JSONDecodeError, BenchmarkError) as error: print(f"ERROR: {error}", file=sys.stderr); return 2
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x") as stream: stream.write(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"cases": report["inventory"]["caseCount"], "recommendation": report["recommendation"]["action"]})); return 0


if __name__ == "__main__": raise SystemExit(main())
