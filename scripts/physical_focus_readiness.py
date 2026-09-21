#!/usr/bin/env python3
"""Fail-closed provenance and geometry readiness check for physical FocusRing pairs."""
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
    if len(value) != 64: raise PhysicalReadinessError("invalid_source_hash")
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
    return {"eligible": True, "reason": None, "pairCount": len(pairs), "coverage": dict(coverage)}

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--manifest", type=Path, required=True); parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(); output = args.output.resolve()
    try: output.relative_to(ROOT)
    except ValueError: print("ERROR: output must stay inside package", file=sys.stderr); return 2
    if output.exists(): print("ERROR: refusing output collision", file=sys.stderr); return 2
    try: report = validate(json.loads(args.manifest.read_text()))
    except (OSError, json.JSONDecodeError, PhysicalReadinessError) as error: print(f"ERROR: {error}", file=sys.stderr); return 2
    output.parent.mkdir(parents=True, exist_ok=True); output.write_text(json.dumps(report, indent=2) + "\n"); print(json.dumps(report)); return 0

if __name__ == "__main__": raise SystemExit(main())
