"""Score independent focus proposals; never manufacture model decisions from labels."""
import math
from focus_dataset_contract import digest, FocusDataError, image, local, ROOT


def iou(a, b):
    x = max(0, min(a[0]+a[2], b[0]+b[2])-max(a[0], b[0]))
    y = max(0, min(a[1]+a[3], b[1]+b[3])-max(a[1], b[1]))
    intersection = x*y
    return intersection/(a[2]*a[3]+b[2]*b[3]-intersection)


def evaluate_proposals(manifest, protocol, document):
    if document.get("formatVersion") != "focus-proposals-v1" or document.get("protocolSHA256") != protocol["protocolSHA256"]:
        raise FocusDataError("incompatible_focus_proposals")
    if document.get("inferenceKind") not in {"test-only", "imported"} or document.get("artifactSHA256") != protocol["artifact"]["sha256"]:
        raise FocusDataError("incompatible_focus_proposal_artifact")
    entries = document.get("samples")
    if not isinstance(entries, list): raise FocusDataError("invalid_focus_proposals")
    by_id = {}
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("id"), str) or entry["id"] in by_id:
            raise FocusDataError("duplicate_or_invalid_focus_proposal")
        by_id[entry["id"]] = entry
    if set(by_id) != {s["id"] for s in protocol["samples"]}: raise FocusDataError("focus_proposal_membership")
    outcomes = []; groups = {}
    root = local(ROOT/manifest["sourceRoot"])
    for pair in manifest["pairs"]:
        for role, label in (("focused", 1), ("unfocused", 0)):
            sid = f"{pair['pair_id']}:{label}"; row = by_id[sid]; frame = pair["frames"][role]
            if row.get("imageSHA256") != frame["sha256"]: raise FocusDataError("focus_proposal_frame_mismatch")
            state = row.get("status")
            if state in {"failed", "unavailable"}:
                if not isinstance(row.get("reason"), str) or not row["reason"]: raise FocusDataError("missing_focus_failure_reason")
                outcome = state
                localized = False
            elif state == "success":
                proposals = row.get("proposals")
                if not isinstance(proposals, list): raise FocusDataError("missing_focus_proposals")
                size = image(root, frame)
                from focus_dataset_contract import expanded_box
                matches = []; positives = []; ambiguous = False
                for p in proposals:
                    if not isinstance(p, dict): raise FocusDataError("invalid_focus_proposal")
                    expanded_box(p.get("bounds"), size)
                    value = p.get("score")
                    if type(value) not in (float, int) or not math.isfinite(value) or not 0 <= value <= 1:
                        raise FocusDataError("invalid_focus_proposal_score")
                    match = iou(p["bounds"], frame["bounds"]) >= .5
                    if match: matches.append(p)
                    if value >= .85: positives.append(match)
                    ambiguous |= .70 <= value < .85
                localized = bool(matches)
                if len(positives) > 1: outcome = "multiple_focus"
                elif positives: outcome = "correct" if label == 1 and positives[0] else "wrong_focus"
                elif ambiguous: outcome = "abstained"
                else: outcome = "no_focus" if label else "correct"
            else: raise FocusDataError("invalid_focus_proposal_status")
            record = {"id": sid, "outcome": outcome, "localized": localized,
                      "family": pair["fixture_scene"], "theme": pair["theme"], "control": pair["element_type"]}
            outcomes.append(record)
            from collections import Counter
            for key in ("overall", *[f"{k}:{record[k]}" for k in ("family", "theme", "control")]):
                c = groups.setdefault(key, Counter()); c["n"] += 1; c[outcome] += 1
                c["localized"] += int(localized)
    return {"status": "available", "scope": "pair-target proposals; not exhaustive screen/navigation accuracy",
            "execution": "supplied_scores_not_executed_here", "inferenceKind": document["inferenceKind"],
            "inputSHA256": digest(document), "groups": {k: dict(v) for k, v in groups.items()},
            "outcomes": outcomes, "modelGatePassed": "not_assessed"}
