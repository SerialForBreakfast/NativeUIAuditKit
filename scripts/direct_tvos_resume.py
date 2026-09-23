"""Explicit direct-pilot continuation and byte-backed development-only assembly.

Plan/assemble never contact a simulator. Execute is a separate, bounded mode;
no segment or failed source is independently admitted as a completed dataset.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import direct_tvos_capture as capture
from focus_dataset_contract import ROOT, digest, local, member

require = capture.require
SET_VERSION = "direct-tvos-capture-set-v1"
SEGMENT_VERSION = "direct-tvos-segment-v1"


def read_receipt(path):
    path = Path(path).absolute()
    require(not any(p.is_symlink() for p in (path, *path.parents)), "symlink_input")
    path = local(path)
    raw = path.read_bytes()
    require(len(raw) <= 64 * 1024 * 1024, "oversize_receipt")
    return {"path": path, "raw": raw, "sha256": hashlib.sha256(raw).hexdigest(), "doc": json.loads(raw)}


def stable_target(target):
    return {k: target.get(k) for k in ("simulatorUDID", "runtime", "deviceProfile", "xcode")}


def validate_repair(review, failed, binding, *, check_report=False):
    require(isinstance(review, dict) and review.get("version") == "direct-tvos-repair-review-v1"
            and review.get("accepted") is True
            and review.get("failedReceiptSHA256") == failed["sha256"]
            and review.get("targetPlanSourceHashes") == capture.SOURCE_HASHES
            and review.get("replacementBinaries") == binding["binaries"], "unbound_repair_review")
    report_hash = review.get("reportSHA256")
    require(isinstance(review.get("report"), str) and review["report"]
            and isinstance(report_hash, str) and len(report_hash) == 64
            and all(c in "0123456789abcdef" for c in report_hash), "invalid_repair_report")
    require(binding["binaries"] != failed["doc"]["target"]["binaries"], "unchanged_failed_build")
    if check_report:
        report = member(ROOT, review["report"])
        require(report.stat().st_size > 0 and hashlib.sha256(report.read_bytes()).hexdigest() == report_hash,
                "changed_repair_report")


def audit_chain(paths):
    require(1 <= len(paths) <= 43, "invalid_chain_length")
    entries = [read_receipt(p) for p in paths]
    require(len({e["sha256"] for e in entries}) == len(entries), "duplicate_receipt")
    first = entries[0]["doc"]
    require(first.get("catalog") == capture.catalog(), "pilot_catalog_required")
    require(first.get("state") == "failed", "failed_origin_required")
    offset, pairs, hashes = 0, 0, []
    for index, entry in enumerate(entries):
        doc = entry["doc"]
        require(doc.get("catalog") == first["catalog"], "changed_catalog")
        require(doc.get("evidenceKind") == first.get("evidenceKind"), "mixed_evidence_kind")
        require(stable_target(doc.get("target", {})) == stable_target(first.get("target", {})),
                "incompatible_target_runtime")
        if index:
            require(doc.get("recipeRange", [None])[0] == offset, "segment_gap_or_overlap")
            require(doc.get("predecessorSHA256") == hashes, "changed_predecessor_chain")
            if doc.get("evidenceKind") == "fixture-native-capture":
                tool_hash = doc.get("continuationRunnerSHA256")
                require(isinstance(tool_hash, str) and len(tool_hash) == 64
                        and all(c in "0123456789abcdef" for c in tool_hash), "missing_continuation_runner")
                if entries[index-1]["doc"]["state"] == "failed":
                    validate_repair(doc.get("repairReview"), entries[index-1], doc["target"])
        pairs += capture._audit_capture(doc, entry["path"].parent,
                                        failed_prefix=doc.get("state") == "failed", segment=index > 0)
        require(doc["recipes"] or index == 0, "zero_progress_segment")
        offset += len(doc["recipes"])
        hashes.append(entry["sha256"])
        require(entry["path"].read_bytes() == entry["raw"], "receipt_changed_during_audit")
    return entries, offset, pairs


def plan_resume(paths):
    entries, offset, pairs = audit_chain(paths)
    recipes = entries[0]["doc"]["catalog"]["recipes"]
    return {"version": "direct-tvos-continuation-plan-v1", "executionAllowed": False,
            "trainingEligible": False, "admittedPairs": 0, "catalogSHA256": capture.catalog()["sha256"],
            "predecessorSHA256": [e["sha256"] for e in entries],
            "verifiedRecipes": offset, "verifiedPairs": pairs,
            "remainingRecipes": [{"catalogIndex": i, "recipe": r, "expectedTargets": capture.expected_targets(r)}
                                 for i, r in enumerate(recipes) if i >= offset]}


def execute_resume(paths, target, endpoint, output, limit, repair_review=None):
    output = capture.new_output(output)
    entries, offset, _ = audit_chain(paths)
    require(offset < 42, "no_remaining_recipes")
    require(type(limit) is int and 1 <= limit <= 42, "invalid_recipe_limit")
    last = entries[-1]
    require(all(e["doc"]["evidenceKind"] == "fixture-native-capture" for e in entries), "test_only_resume")
    require(target == last["doc"]["target"]["simulatorUDID"], "wrong_resume_target")
    binding = capture.bind_target(target, endpoint)
    require(stable_target(binding) == stable_target(last["doc"]["target"]), "incompatible_target_runtime")
    review = None
    if last["doc"]["state"] == "failed":
        require(repair_review is not None, "repair_review_required")
        item = read_receipt(repair_review)
        review = item["doc"]
        validate_repair(review, last, binding, check_report=True)
        require(item["path"].read_bytes() == item["raw"], "changed_repair_review")
    # Final receipt fence before handing the bound target to the existing runner.
    require(all(e["path"].read_bytes() == e["raw"] for e in entries), "changed_predecessor_chain")
    return capture.execute(capture.catalog(), target, endpoint, output, continuation={
        "binding": binding, "recipeRange": [offset, min(42, offset + limit)],
        "predecessorSHA256": [e["sha256"] for e in entries], "repairReview": review,
        "continuationRunnerSHA256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})


def projected_set(entries):
    recipes, sources = [], []
    for index, entry in enumerate(entries):
        prefix = f"runs/{index:03d}"
        doc = entry["doc"]
        sources.append({"receipt": f"{prefix}/receipt.json", "sha256": entry["sha256"],
                        "state": doc["state"], "target": doc["target"],
                        "initialDevice": doc["initialDevice"], "runnerSHA256": doc.get("runnerSHA256")})
        for result in doc["recipes"]:
            result = copy.deepcopy(result)
            for frame in result["frames"]:
                frame["path"] = f"{prefix}/{frame['path']}"
            recipes.append(result)
    return {"version": SET_VERSION, "sourceKind": capture.SOURCE, "state": "completed",
            "purpose": "development-pilot", "trainingEligible": False,
            "evidenceKind": entries[0]["doc"]["evidenceKind"], "catalog": capture.catalog(),
            "target": {"runs": [s["target"] for s in sources]}, "sources": sources, "recipes": recipes,
            "acceptedPairs": sum(len(r["expectedTargets"]) for r in recipes)}


def validate_set(doc, root):
    require(doc.get("version") == SET_VERSION and doc.get("state") == "completed", "incomplete_capture_set")
    sources = doc.get("sources", [])
    require(2 <= len(sources) <= 43, "invalid_chain_length")
    paths = []
    for index, source in enumerate(sources):
        require(source.get("receipt") == f"runs/{index:03d}/receipt.json", "invalid_source_path")
        path = member(root, source["receipt"])
        require(hashlib.sha256(path.read_bytes()).hexdigest() == source.get("sha256"), "changed_source_receipt")
        paths.append(path)
    entries, offset, pairs = audit_chain(paths)
    require(offset == 42, "incomplete_pilot")
    require(doc == projected_set(entries), "changed_capture_projection")
    return pairs


def assemble(paths, output):
    output = capture.new_output(output)
    entries, offset, _ = audit_chain(paths)
    require(offset == 42, "incomplete_pilot")
    doc = projected_set(entries)
    output.mkdir(parents=True)
    # Copy only audited members, preserving raw receipts/sidecars verbatim. The
    # originals (including unindexed diagnostics/failed trial output) remain intact.
    for index, entry in enumerate(entries):
        dest = output / f"runs/{index:03d}"
        dest.mkdir(parents=True)
        with (dest / "receipt.json").open("xb") as stream:
            stream.write(entry["raw"])
        names = {f["path"] + suffix for r in entry["doc"]["recipes"] for f in r["frames"]
                 for suffix in ("", ".json")}
        for name in sorted(names):
            source = member(entry["path"].parent, name)
            target = dest / name
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("xb") as stream:
                stream.write(source.read_bytes())
    require(all(e["path"].read_bytes() == e["raw"] for e in entries), "changed_predecessor_chain")
    validate_set(doc, output)  # Validate copied bytes, not only the original inputs.
    capture.write_json(output / "direct-capture.json", doc)
    return doc


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--plan", action="store_true")
    mode.add_argument("--execute", action="store_true")
    mode.add_argument("--assemble", action="store_true")
    parser.add_argument("--receipts", nargs="+", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--target"); parser.add_argument("--endpoint")
    parser.add_argument("--recipe-limit", type=int, default=42)
    parser.add_argument("--repair-review", type=Path)
    args = parser.parse_args()
    try:
        if args.plan:
            output = capture.new_output(args.output)
            result = plan_resume(args.receipts)
            output.parent.mkdir(parents=True, exist_ok=True)
            capture.write_json(output, result)
        elif args.assemble:
            result = assemble(args.receipts, args.output)
        else:
            require(args.target and args.endpoint, "explicit_execution_inputs_required")
            result = execute_resume(args.receipts, args.target, args.endpoint, args.output,
                                    args.recipe_limit, args.repair_review)
        print(json.dumps({k: result[k] for k in ("version", "state", "verifiedRecipes", "acceptedPairs") if k in result}))
        return 0
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        print(str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
