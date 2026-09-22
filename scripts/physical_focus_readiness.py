#!/usr/bin/env python3
"""Metadata inspection only; real physical eligibility requires byte-backed intake."""
from __future__ import annotations
import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
VERSION = "focus-ring-physical-readiness-v1"

class PhysicalReadinessError(ValueError): pass

def _text(value: Any, error: str) -> str:
    if not isinstance(value, str) or not value: raise PhysicalReadinessError(error)
    return value

def _sha(value: Any) -> str:
    value = _text(value, "invalid_source_hash")
    if len(value) != 64 or any(c not in "0123456789abcdef" for c in value): raise PhysicalReadinessError("invalid_source_hash")
    return value

def validate(document: dict[str, Any]) -> dict[str, Any]:
    if document.get("formatVersion") != VERSION or not isinstance(document.get("pairs"), list): raise PhysicalReadinessError("unsupported_physical_manifest")
    pairs = document["pairs"]
    if not pairs: return {"eligible": False, "reason": "no_physical_pairs", "pairCount": 0, "coverage": {}}
    seen: set[str] = set(); partitions: dict[str, str] = {}; coverage: Counter[str] = Counter()
    for pair in pairs:
        if not isinstance(pair, dict) or pair.get("sourceKind") != "physicalFixture": raise PhysicalReadinessError("false_or_missing_physical_source")
        pair_id = _text(pair.get("pairID"), "invalid_pair_id")
        if pair_id in seen: raise PhysicalReadinessError("duplicate_pair_id")
        seen.add(pair_id)
        source = pair.get("source")
        if not isinstance(source, dict): raise PhysicalReadinessError("missing_physical_provenance")
        for field in ("producerRevision", "captureID", "frameID"): _text(source.get(field), "missing_physical_provenance")
        _sha(source.get("imageSHA256"))
        if pair.get("focusLabelOrigin") != "fixtureCallback" or pair.get("focusFrameID") != source["frameID"]: raise PhysicalReadinessError("stale_or_untrusted_focus_label")
        if not _text(pair.get("focusedCrop"), "missing_crop") or not _text(pair.get("unfocusedCrop"), "missing_crop"): raise PhysicalReadinessError("missing_crop")
        if pair.get("cropSize") != [256, 256] or pair.get("expansion") != 0.16: raise PhysicalReadinessError("crop_parity_mismatch")
        group, partition = _text(pair.get("recipeGroup"), "missing_recipe_group"), pair.get("partition")
        if partition not in {"development", "validation", "test"}: raise PhysicalReadinessError("invalid_partition")
        if group in partitions and partitions[group] != partition: raise PhysicalReadinessError("recipe_group_leakage")
        partitions[group] = partition
        scene, theme, control = (_text(pair.get(key), "missing_pair_metadata") for key in ("scene", "theme", "control"))
        coverage[f"{scene}/{theme}/{control}"] += 1
        if pair.get("hardNegative"):
            evidence = pair.get("unfocusedEvidence")
            if not isinstance(evidence, dict): raise PhysicalReadinessError("missing_hard_negative_evidence")
            _sha(evidence.get("sha256"))
    return {"eligible": False, "reason": "metadata_only_requires_byte_backed_intake",
            "metadataValid": True, "integrityVerified": False,
            "pairCount": len(pairs), "coverage": dict(coverage)}


def validate_dataset(document, dataset):
    from focus_dataset_contract import validate_manifest, digest
    if document.get("sourceKind") != "physicalFixture":
        raise PhysicalReadinessError("false_or_missing_physical_source")
    rows = validate_manifest(document, dataset)
    coverage = Counter(f"{r['scene']}/{r['theme']}/{r['class']}" for r in rows)
    negatives = Counter(f"{r['theme']}/{r['class']}" for r in rows
                        if r["theme"] in {"light", "highContrast"} and r["class"] in {"imageView", "collectionItem"})
    return {"formatVersion": "physical-focus-intake-report-v2", "integrityVerified": True,
            "inspectionValid": True, "eligible": False, "trainingEligible": False,
            "reason": "test_only" if document["evidenceKind"] == "test-only" else "requires_independent_corpus_and_operation_review",
            "sourceKind": document["sourceKind"], "evidenceKind": document["evidenceKind"],
            "sourceAssurance": "reported-source; not-attested", "sourceReview": document["sourceReview"],
            "manifestSHA256": digest(document), "pairCount": len(rows), "coverage": dict(coverage),
            "verifiedUnfocusedSupport": dict(negatives), "partitions": dict(Counter(r["split"] for r in rows)),
            "cropParity": "production-runtime" if document["version"] == "1.3" else "legacy-pillow-not-runtime-qualified",
            "executionAuthorized": False, "modelGatePassed": "not_assessed"}

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--manifest", type=Path, required=True); parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--model", type=Path, help="Prepare existing development baseline protocol; does not infer")
    parser.add_argument("--protocol", type=Path, help="Existing protocol required with --scores")
    parser.add_argument("--scores", type=Path, help="Explicit bound score envelope, not a model launch")
    parser.add_argument("--proposals", type=Path, help="Independent pair-target box/score envelope; no inference")
    args = parser.parse_args(); output = args.output.resolve()
    try: output.relative_to(ROOT)
    except ValueError: print("ERROR: output must stay inside package", file=sys.stderr); return 2
    if output.exists(): print("ERROR: refusing output collision", file=sys.stderr); return 2
    try:
        document = json.loads(args.manifest.read_text())
        if document.get("version") in {"1.2", "1.3"}:
            report = validate_dataset(document, args.manifest.parent)
            if args.model:
                from focus_ring_baseline import prepare_protocol, score_protocol
                protocol = prepare_protocol(document, args.manifest.parent, args.model)
                report["baselineProtocol"] = protocol
                if args.scores:
                    if not args.protocol or json.loads(args.protocol.read_text()) != protocol:
                        raise PhysicalReadinessError("changed_or_missing_protocol")
                    report["baseline"] = score_protocol(protocol, json.loads(args.scores.read_text()))
                elif args.protocol: raise PhysicalReadinessError("scores_required_with_protocol")
                if args.proposals:
                    from focus_proposal_evaluation import evaluate_proposals
                    report["proposedBoxEvaluation"] = evaluate_proposals(document, protocol, json.loads(args.proposals.read_text()))
                else: report["proposedBoxEvaluation"] = {"status": "unavailable", "reason": "independent_proposals_not_supplied"}
            elif args.protocol or args.scores or args.proposals: raise PhysicalReadinessError("model_required_for_baseline")
        else:
            if args.model or args.protocol or args.scores or args.proposals: raise PhysicalReadinessError("byte_backed_manifest_required")
            report = validate(document)
    except (OSError, ValueError) as error: print(f"ERROR: {error}", file=sys.stderr); return 2
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x") as stream: stream.write(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report)); return 0

if __name__ == "__main__": raise SystemExit(main())
