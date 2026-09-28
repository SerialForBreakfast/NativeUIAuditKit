"""Cached-only FocusRing diagnostics. No model, runtime invocation or crop generation.

freeze --protocol ... --comparison ... --candidate ... --output fresh-index.json
report --index fresh-index.json --output fresh-directory
All paths are project-local. Source artifacts are never modified.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import platform
import statistics

from PIL import Image, ImageDraw, __version__ as PILLOW_VERSION
from focus_dataset_contract import ROOT, digest, image, member, pixel_digest
from focus_runtime import RUNTIME_PREPROCESSING
from focus_surface_evaluation import VERSION as PROTOCOL_VERSION, score, seal_check, validate_rows

VERSION = "focus-offline-diagnostic-v1"
MODELS = ("shipped", "fdr007", "fdr008")
FIELDS = ("metrics", "frameDecisions", "frameCounts", "accounted")
STRATA = ("dense-dark-media", "bright-unfocused-artwork", "gray-blank-placeholders",
          "dock-neighbor-focus", "fixture-detail-action", "photos-buttons")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def pairs_object(items):
    result = {}
    for key, value in items:
        require(key not in result, "duplicate_json_key:" + key)
        result[key] = value
    return result


def read(path):
    return json.loads(path.read_text(), object_pairs_hook=pairs_object)


def write(path, value):
    path.write_text(json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n")


def local(path):
    path = Path(path).resolve()
    require(path.is_relative_to(ROOT), "outside_project")
    return path


def ref(path):
    path = local(path)
    return {"path": str(path.relative_to(ROOT)), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def checked(record):
    path = member(ROOT, record["path"])
    require(ref(path)["sha256"] == record["sha256"], "changed_hash:" + record["path"])
    return path


def validate_membership(rows):
    validate_rows(rows)  # rejects final-challenge groups before any pixel reads
    pairs, frames = defaultdict(list), defaultdict(list)
    for row in rows:
        key = row["group"] + ":" + row["pairID"]
        if row["kind"] == "pair":
            pairs[key].append(row)
        else:
            require(row["frameID"] == key, "frame_pair_identity_mismatch")
            frames[key].append(row)
    require(set(pairs) == set(frames), "paired_frame_membership_mismatch")
    for key, pair in pairs.items():
        require(len(pair) == 2 and sorted(r["label"] for r in pair) == [0, 1], "incomplete_pair")
        require(len({r["elementID"] for r in pair}) == 1, "changed_pair_control")
        focused = next(r for r in pair if r["label"])
        target = next(r for r in frames[key] if r["label"])
        for field in ("elementID", "control", "stratum", "path", "sha256", "bounds"):
            require(focused[field] == target[field], "pair_frame_binding_mismatch:" + field)
        require(all(focused["crop"][k] == target["crop"][k] for k in ("sha256", "pixelSHA256")),
                "pair_frame_binding_mismatch:crop")
        require(len({r["path"] for r in frames[key]}) == 1, "mixed_frame_pixels")
    return pairs, frames


def validate_protocol(protocol):
    seal_check(protocol)
    require(protocol.get("version") == PROTOCOL_VERSION and protocol.get("threshold") == .85
            and protocol.get("variants") == ["base"] and protocol.get("preprocessing") == RUNTIME_PREPROCESSING
            and protocol.get("finalChallengeScored") is False
            and protocol.get("trainingEligible") is False
            and protocol.get("independentEvaluationEligible") is False, "incompatible_protocol")
    validate_membership(protocol["samples"])


def candidate_pairs(candidate):
    require(candidate.get("version") == "focus-appearance-experiment-v1", "incompatible_candidate")
    rows = candidate["samples"]
    require(bool(rows) and len({r["id"] for r in rows}) == len(rows), "candidate_membership")
    pairs = defaultdict(list)
    for row in rows:
        require(row["use"] in ("train-candidate", "retention-validation")
                and row.get("proposedRole", row["use"]) == row["use"], "protected_or_incompatible_candidate_role")
        require(type(row["label"]) is int and row["label"] in (0, 1), "invalid_candidate_label")
        pairs[(row["sourceID"], row["pairID"])].append(row)
    for pair in pairs.values():
        require(len(pair) == 2 and sorted(r["label"] for r in pair) == [0, 1], "candidate_incomplete_pair")
        for field in ("use", "control", "scene", "style", "labelSource", "relatedGroup", "intrinsicGroup"):
            require(pair[0].get(field) == pair[1].get(field), "candidate_pair_conflict:" + field)
    require(dict(Counter(r["use"] for r in rows)) == candidate["counts"], "candidate_counts")
    return pairs


def references_in(value):
    """Metadata references only; never recursively follow protected manifests."""
    if isinstance(value, dict):
        if isinstance(value.get("path"), str) and isinstance(value.get("sha256"), str):
            yield {k: value[k] for k in ("path", "sha256")}
        else:
            for item in value.values():
                yield from references_in(item)
    elif isinstance(value, list):
        for item in value:
            yield from references_in(item)


def inventory_for(protocol, candidate):
    images = []
    for row in protocol["samples"]:
        images.extend([{"path": row["path"], "sha256": row["sha256"],
                        "pixelSHA256": row["framePixelSHA256"], "kind": "frame"},
                       {**row["crop"], "kind": "crop"}])
    for row in candidate["samples"]:
        images.extend([{**row[kind], "kind": kind} for kind in ("frame", "crop")])
    inventory = {}
    for record in images:
        old = inventory.setdefault(record["path"], record)
        require(old == record, "conflicting_image_reference")
    return sorted(inventory.values(), key=lambda r: r["path"])


def geometry_manifests(candidate):
    proposal = read(checked(candidate["inputs"]["proposal"]))
    # Only the two candidate source manifests referenced by the original proposal.
    # Do not traverse its protected lineage or model references.
    manifests = [r for r in proposal.get("inputs", []) if r["path"].endswith("focus_dataset_manifest.json")]
    manifests += [a["manifest"] for a in candidate["inputs"].get("additions", [])]
    return manifests


def freeze(protocol_path, comparison_path, candidate_path, output):
    output = local(output)
    require(not output.exists(), "output_exists")
    protocol, comparison, candidate = map(read, (protocol_path, comparison_path, candidate_path))
    validate_protocol(protocol)
    candidate_pairs(candidate)
    require(comparison.get("protocol") == ref(protocol_path)
            and comparison.get("version") == PROTOCOL_VERSION
            and comparison.get("finalChallengeScored") is False
            and set(comparison["results"]) == set(MODELS), "incompatible_comparison")
    dependencies = [ref(p) for p in (protocol_path, comparison_path, candidate_path)]
    dependencies += list(references_in(candidate["inputs"]))
    dependencies += list(references_in(candidate["selection"]))
    dependencies += geometry_manifests(candidate)
    dependencies += [protocol["crops"], protocol["review"]]
    dependencies += protocol["implementation"]
    dependencies += [ref(Path(__file__)), ref(ROOT / "scripts/focus_dataset_contract.py")]
    for model in MODELS:
        path = comparison_path.parent / (model + ".json")
        require(read(path) == comparison["results"][model], "separate_prediction_artifact_mismatch")
        dependencies.append(ref(path))
    depmap = {}
    for record in dependencies:
        checked(record)
        old = depmap.setdefault(record["path"], record)
        require(old == record, "conflicting_metadata_reference")
    index = {"version": VERSION, "protocol": ref(protocol_path), "comparison": ref(comparison_path),
             "candidate": ref(candidate_path), "dependencies": sorted(depmap.values(), key=lambda r: r["path"]),
             "images": inventory_for(protocol, candidate),
             "analysisRuntime": {"python": platform.python_version(), "pillow": PILLOW_VERSION},
             "expected": {"validationRows": len(protocol["samples"]), "candidateRows": len(candidate["samples"]),
                          "predictions": len(protocol["samples"]) * len(MODELS)},
             "challengePixelAccess": False, "modelExecution": False}
    index["seal"] = digest(index)
    output.parent.mkdir(parents=True, exist_ok=True)
    write(output, index)
    return index


def distribution(values):
    values = sorted(values)
    def quantile(q):
        if not values:
            return None
        position = (len(values) - 1) * q
        lo, hi = math.floor(position), math.ceil(position)
        return values[lo] + (values[hi] - values[lo]) * (position - lo)
    return {"n": len(values), "status": "supported" if values else "unavailable",
            "min": min(values) if values else None, "max": max(values) if values else None,
            "mean": statistics.mean(values) if values else None,
            "p25": quantile(.25), "median": quantile(.5), "p75": quantile(.75)}


def analyze(rows, result):
    pairs, frames = validate_membership(rows)
    reproduced = score(rows, result["predictions"])
    require(result.get("state") == "complete", "incomplete_prediction_artifact")
    require(all(reproduced[key] == result[key] for key in FIELDS), "published_metrics_mismatch")
    values = {r["id"]: r["probability"] for r in result["predictions"]}
    groups = {}
    for kind in ("pair", "competition"):
        subset = [r for r in rows if r["kind"] == kind]
        selections = {"overall": subset}
        for field in ("group", "control", "stratum", "theme"):
            keys = sorted(set(r.get(field, "unknown") for r in subset) | (set(STRATA) if field == "stratum" else set()))
            for key in keys:
                selections[field + ":" + key] = [r for r in subset if r.get(field, "unknown") == key]
        groups[kind] = {key: {str(label): distribution([values[r["id"]] for r in members if r["label"] == label])
                             for label in (0, 1)} for key, members in selections.items()}
    paired = []
    for key, pair in sorted(pairs.items()):
        focused, unfocused = sorted(pair, key=lambda r: -r["label"])
        paired.append({"pairID": key, "focusedID": focused["id"], "unfocusedID": unfocused["id"],
                       "group": focused["group"], "control": focused["control"], "stratum": focused["stratum"],
                       "focused": values[focused["id"]], "unfocused": values[unfocused["id"]],
                       "difference": values[focused["id"]] - values[unfocused["id"]]})
    ranks = []
    decisions = {r["frameID"]: r["decision"] for r in reproduced["frameDecisions"]}
    for key, members in sorted(frames.items()):
        target = next(r for r in members if r["label"])
        competitors = sorted((r for r in members if not r["label"]), key=lambda r: (-values[r["id"]], r["id"]))
        p = values[target["id"]]
        ranks.append({"frameID": key, "targetID": target["id"], "group": target["group"],
                      "stratum": target["stratum"], "control": target["control"], "score": p,
                      "rankBest": 1 + sum(values[r["id"]] > p for r in competitors),
                      "rankWorst": 1 + sum(values[r["id"]] >= p for r in competitors),
                      "margin": p - values[competitors[0]["id"]] if competitors else None,
                      "topCompetitorID": competitors[0]["id"] if competitors else None,
                      "decision": decisions[key]})
    evidence = []
    for kind in ("pair", "competition"):
        for title, label, reverse in (("worst-miss", 1, False), ("highest-false-positive", 0, True)):
            selected = [r for r in rows if r["kind"] == kind and r["label"] == label
                        and ((values[r["id"]] < .85) if label else (values[r["id"]] >= .85))]
            selected.sort(key=lambda r: ((-1 if reverse else 1) * values[r["id"]], r["id"]))
            evidence += [{"reason": kind + ":" + title, "id": r["id"]} for r in selected[:3]]
    for status in ("wrong-focus", "multiple-focus", "unique-correct"):
        selected = sorted((r for r in ranks if r["decision"] == status),
                          key=lambda r: (r["margin"] if r["margin"] is not None else 0, r["frameID"]))
        if status != "unique-correct":
            selected = selected[:3]
        for row in selected:
            evidence.append({"reason": status, "id": row["targetID"], "competitor": row["topCompetitorID"]})
    return {"reproduced": reproduced, "distributions": groups, "paired": paired, "ranks": ranks,
            "pairedDifference": distribution([r["difference"] for r in paired]),
            "margin": distribution([r["margin"] for r in ranks if r["margin"] is not None]),
            "strictTopRank": sum(r["rankWorst"] == 1 for r in ranks), "evidence": evidence,
            "backend": result["backend"], "selectionPolicyUnchanged": True}


def candidate_geometry(candidate):
    """Join only exact candidate members to retained metadata; no protected pixels."""
    metadata = {}
    proposal = read(checked(candidate["inputs"]["proposal"]))
    for row in proposal.get("samples", []):
        metadata[(row["pairID"], row["label"], row["frame"]["sha256"])] = {
            "bounds": row.get("bounds"), "neighborCount": None, "appearance": "unknown",
            "evidence": candidate["inputs"]["proposal"]}
    for manifest_ref in geometry_manifests(candidate):
        manifest = read(checked(manifest_ref))
        for pair in manifest.get("pairs", []):
            for state, label in (("focused", 1), ("unfocused", 0)):
                frame = pair["frames"][state]
                scene = pair.get("observationBinding", {}).get("focusedScene" if label else "baselineScene", {})
                metadata[(pair["pair_id"], label, frame["sha256"])] = {
                    "bounds": frame.get("bounds"), "neighborCount": len(scene["elements"])-1 if "elements" in scene else None,
                    "appearance": scene.get("recipe", {}).get("appearance", "unknown"), "evidence": manifest_ref}
    result = {}
    for row in candidate["samples"]:
        value = metadata.get((row["pairID"], row["label"], row["frame"]["sha256"]),
                             {"bounds": None, "neighborCount": None, "appearance": "unknown"})
        result[row["id"]] = value
    return result


def audit(candidate):
    pairs = candidate_pairs(candidate)
    rows = candidate["samples"]
    summaries = {}
    for field in ("use", "sourceID", "sourceKind", "scene", "style", "control", "labelSource", "relatedGroup", "intrinsicGroup"):
        summaries[field] = dict(sorted(Counter(str(r.get(field, "unknown")) for r in rows).items()))
    geometry = candidate_geometry(candidate)
    pair_rows = []
    representatives = {}
    for key, members in sorted(pairs.items()):
        row = members[0]
        item = {field: row.get(field, "unknown") for field in ("sourceID", "pairID", "use", "scene", "style", "control", "labelSource")}
        item.update({"members": [r["id"] for r in sorted(members, key=lambda r: r["label"])],
                     "perFrameContext": {str(r["label"]): geometry[r["id"]] for r in members},
                     "completeNeighborLabels": "not-certified-by-assembly",
                     "sourceIndependence": "not-established"})
        pair_rows.append(item)
        repkey = (row["use"], row["sourceID"], row["scene"], row["style"], row["control"])
        representatives.setdefault(repkey, next(r["id"] for r in members if r["label"]))
    return {"counts": candidate["counts"], "pairs": pair_rows, "sampleCounts": summaries,
            "representatives": list(representatives.values()), "sampling": candidate["sampling"],
            "selection": candidate["selection"], "configuration": candidate["configuration"],
            "readinessBlockers": candidate["readinessBlockers"], "trainingEligible": candidate["trainingEligible"],
            "candidateScores": "unavailable-no-inference", "frameContextRetained": True,
            "geometry": geometry}


def page(output, number, row, heading, detail, competitor=None):
    """Display context only; retained production crops are pasted unchanged."""
    canvas = Image.new("RGB", (1280, 820), "#242424")
    draw = ImageDraw.Draw(canvas)
    draw.text((15, 12), f"{number:03d}  {heading}", fill="white")
    draw.text((15, 35), row["id"], fill="white")
    draw.text((15, 57), detail, fill="white")
    frame = row.get("frame", {"path": row.get("path")})
    with Image.open(ROOT / frame["path"]) as original:
        preview = original.convert("RGB")
        preview.thumbnail((960, 650))
        canvas.paste(preview, (10, 100))
        if "bounds" in row:
            x, y, w, h = row["bounds"]
            scale = preview.width / original.width
            draw.rectangle((10+x*scale, 100+y*scale, 10+(x+w)*scale, 100+(y+h)*scale), outline="lime", width=2)
    for offset, sample in enumerate([r for r in (row, competitor) if r is not None]):
        with Image.open(ROOT / sample["crop"]["path"]) as crop:
            canvas.paste(crop.convert("RGB"), (1005, 105 + offset * 310))
        draw.text((1005, 370 + offset*310), "target" if offset == 0 else
                  ("matched opposite state" if row.get("kind") == "pair" else "top competitor"), fill="white")
    filename = f"{number:03d}.png"
    canvas.save(output / filename)
    return filename


def report(index_path, output):
    output = local(output)
    require(not output.exists(), "output_exists")
    index = read(index_path)
    seal_check(index)
    require(index.get("version") == VERSION, "incompatible_index")
    # Validate roles before even checking image files from the inventory.
    protocol = read(checked(index["protocol"]))
    candidate = read(checked(index["candidate"]))
    validate_protocol(protocol)
    candidate_pairs(candidate)
    require(index["images"] == inventory_for(protocol, candidate), "image_inventory_membership_mismatch")
    output.mkdir(parents=True)
    errors, accounting = [], []
    for record in index["dependencies"]:
        try:
            checked(record)
        except (ValueError, OSError) as error:
            errors.append({"path": record["path"], "reason": str(error)})
    for record in index["images"]:
        try:
            size = image(ROOT, record, (256, 256) if record["kind"] == "crop" else None)
            require(pixel_digest(ROOT, record) == record["pixelSHA256"], "changed_pixel_hash")
            accounting.append({"path": record["path"], "state": "accepted", "dimensions": size})
        except (ValueError, OSError) as error:
            item = {"path": record["path"], "state": "blocked", "reason": str(error)}
            accounting.append(item)
            errors.append(item)
    write(output / "accounting.json", {"images": accounting, "errors": errors, "expected": index["expected"],
                                      "excluded": 0, "challenge": "out-of-scope-no-pixel-access"})
    require(not errors, "blocked_inputs_see_accounting.json")
    sizes = {r["path"]: r["dimensions"] for r in accounting}
    for row in protocol["samples"]:
        bounds = row["bounds"]
        require(len(bounds) == 4 and all(type(v) in (int, float) and math.isfinite(v) for v in bounds), "invalid_bounds")
        x, y, w, h = bounds
        width, height = sizes[row["path"]]
        require(x >= 0 and y >= 0 and w > 0 and h > 0 and x+w <= width and y+h <= height, "out_of_frame_bounds")
    comparison = read(checked(index["comparison"]))
    results = {}
    try:
        for name in MODELS:
            result = comparison["results"][name]
            require(result["protocolSHA256"] == protocol["seal"], "prediction_protocol_mismatch")
            results[name] = analyze(protocol["samples"], result)
    except (KeyError, ValueError) as error:
        write(output / "blocked.json", {"state": "blocked", "reason": str(error), "expected": index["expected"],
                                       "scored": 0, "partialModelDiagnostics": results})
        raise
    coverage = audit(candidate)
    sheets = output / "sheets"
    sheets.mkdir()
    rows = {r["id"]: r for r in protocol["samples"]}
    evidence = []
    for name, result in results.items():
        scores = {r["id"]: r["probability"] for r in comparison["results"][name]["predictions"]}
        for selection in result["evidence"]:
            row = rows[selection["id"]]
            other = rows.get(selection.get("competitor"))
            if other is None and row["kind"] == "pair":
                other = next(r for r in protocol["samples"] if r["kind"] == "pair" and r["group"] == row["group"]
                             and r["pairID"] == row["pairID"] and r["label"] != row["label"])
            number = len(evidence) + 1
            filename = page(sheets, number, row, name + " " + selection["reason"],
                            f"label={row['label']} score={scores[row['id']]:.8f} stratum={row['stratum']}",
                            other)
            evidence.append({"number": number, "model": name, **selection, "file": "sheets/" + filename})
    candidates = {r["id"]: r for r in candidate["samples"]}
    for sample_id in coverage["representatives"]:
        row = dict(candidates[sample_id])
        if coverage["geometry"][sample_id]["bounds"] is not None:
            row["bounds"] = coverage["geometry"][sample_id]["bounds"]
        number = len(evidence) + 1
        filename = page(sheets, number, row, "candidate metadata representative; no scores",
                        f"{row['sourceID']} {row['scene']} {row['style']} {row['control']} label={row['label']}")
        evidence.append({"number": number, "id": sample_id, "reason": "candidate-representative", "file": "sheets/" + filename})
    result = {"version": VERSION, "state": "complete-diagnostic-only", "input": ref(index_path),
              "results": results, "coverage": coverage, "evidence": evidence,
              "modelExecution": False, "finalChallengeAnalyzed": False, "trainingEligible": False,
              "modelGatePassed": "not_assessed", "accountedPredictions": sum(r["reproduced"]["accounted"] for r in results.values())}
    write(output / "diagnosis.json", result)
    write(output / "candidate-coverage.json", coverage)
    lines = ["# Numbered diagnostic evidence", "", "Retained production crops; display-only full-frame resize. No new inference.", ""]
    lines += [f"{r['number']:03d}. {r.get('model', 'candidate')} {r['reason']} — `{r['id']}` [sheet]({r['file']})" for r in evidence]
    (output / "evidence.md").write_text("\n\n".join(lines) + "\n")
    # Detect source modification during analysis as well as before it.
    for record in [*index["dependencies"], *index["images"]]:
        checked(record)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    freeze_parser = sub.add_parser("freeze")
    for name in ("protocol", "comparison", "candidate", "output"):
        freeze_parser.add_argument("--" + name, type=Path, required=True)
    report_parser = sub.add_parser("report")
    report_parser.add_argument("--index", type=Path, required=True)
    report_parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = (freeze(args.protocol, args.comparison, args.candidate, args.output) if args.command == "freeze"
                  else report(args.index, args.output))
        print(json.dumps({"state": result.get("state", "frozen"), "output": str(args.output)}))
        return 0
    except (ValueError, KeyError, OSError, TypeError) as error:
        print(json.dumps({"state": "blocked", "reason": str(error)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
