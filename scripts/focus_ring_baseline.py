#!/usr/bin/env python3
"""Fail-closed reporting for the shipped FocusRing baseline.

Offline tests supply a deterministic score file. Actual CoreML inference is deliberately
not hidden here: it is enabled only after a genuine SIM-DATA-03 pilot exists.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
# This is deliberately a shipped-model comparison point, not the operating threshold for
# an untrained candidate. FR-SIM-CAND completes its fixed 30-epoch run, then selects and
# locks its own threshold from validation membership before it reads the final holdout.
SHIPPED_COMPARISON_THRESHOLD = 0.85


class BaselineError(ValueError):
    pass


def artifact_digest(model: Path) -> str:
    if not model.is_dir():
        raise BaselineError("missing_compiled_model")
    h = hashlib.sha256()
    files = sorted(path for path in model.rglob("*") if path.is_file())
    if not files:
        raise BaselineError("empty_compiled_model")
    for path in files:
        h.update(str(path.relative_to(model)).encode() + b"\0")
        h.update(path.read_bytes())
    return h.hexdigest()


def model_contract(model: Path) -> dict[str, Any]:
    metadata = model / "metadata.json"
    if not metadata.is_file():
        raise BaselineError("missing_model_metadata")
    try:
        data = json.loads(metadata.read_text())
    except json.JSONDecodeError as error:
        raise BaselineError("invalid_model_metadata") from error
    # Compiled CoreML metadata is an array of model records, unlike the export-time
    # package metadata object. A baseline must reject ambiguous compiled metadata.
    if not isinstance(data, list) or len(data) != 1 or not isinstance(data[0], dict):
        raise BaselineError("invalid_model_metadata")
    names = {item.get("name") for item in data[0].get("outputSchema", []) if isinstance(item, dict)}
    if "is_focused_prob" not in names:
        raise BaselineError("unexpected_model_output")
    return {"sha256": artifact_digest(model), "metadataSHA256": hashlib.sha256(metadata.read_bytes()).hexdigest(), "outputs": sorted(name for name in names if isinstance(name, str))}


def rows(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    result = []
    for pair in manifest.get("pairs", []):
        if not isinstance(pair, dict):
            raise BaselineError("invalid_membership")
        pair_id = pair.get("pair_id") or pair.get("pairID")
        family = pair.get("fixture_scene") or pair.get("family")
        theme, control = pair.get("theme"), pair.get("element_type")
        if not all(isinstance(value, str) and value for value in (pair_id, family, theme, control)):
            raise BaselineError("invalid_membership")
        for label, key in ((1, "focused_crop"), (0, "unfocused_crop")):
            if pair.get(key):
                result.append({"id": f"{pair_id}:{label}", "label": label, "family": family, "theme": theme, "control": control, "hard": bool(pair.get("hardNegative")) and label == 0})
    if not result:
        raise BaselineError("empty_membership")
    return result


def evaluate(samples: list[dict[str, Any]], scores: dict[str, Any]) -> dict[str, Any]:
    groups: dict[str, Counter[str]] = {}
    required = {"overall"}
    for sample in samples:
        value = scores.get(sample["id"])
        if not isinstance(value, (int, float)) or not 0 <= value <= 1:
            raise BaselineError("missing_or_invalid_inference")
        keys = ("overall", f"family:{sample['family']}", f"theme:{sample['theme']}", f"control:{sample['control']}")
        for key in keys:
            required.add(key); groups.setdefault(key, Counter())
            predicted = int(value >= SHIPPED_COMPARISON_THRESHOLD)
            actual = sample["label"]
            groups[key]["n"] += 1
            groups[key]["tp" if predicted and actual else "fp" if predicted else "tn" if not actual else "fn"] += 1
    hard = [sample for sample in samples if sample["hard"]]
    if not hard:
        raise BaselineError("empty_hard_negative_support")
    hard_fp = sum(scores[sample["id"]] >= SHIPPED_COMPARISON_THRESHOLD for sample in hard)
    report = {}
    for key in sorted(required):
        c = groups.get(key, Counter())
        if not c["n"]:
            raise BaselineError("empty_group_support")
        report[key] = dict(c)
        report[key]["accuracy"] = (c["tp"] + c["tn"]) / c["n"]
        report[key]["precision"] = c["tp"] / max(1, c["tp"] + c["fp"])
        report[key]["recall"] = c["tp"] / max(1, c["tp"] + c["fn"])
    return {
        "threshold": {
            "value": SHIPPED_COMPARISON_THRESHOLD,
            "purpose": "shipped_baseline_comparison",
            "candidatePolicy": "complete_30_epochs_then_select_on_validation_and_lock_before_test",
        },
        "groups": report,
        "hardNegative": {"n": len(hard), "fp": hard_fp, "fpr": hard_fp / len(hard)},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--scores", type=Path, required=True, help="Deterministic inference result map for offline/report validation")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    try: output.relative_to(ROOT)
    except ValueError:
        print("ERROR: output must stay inside package", file=sys.stderr); return 2
    if output.exists():
        print("ERROR: refusing output collision", file=sys.stderr); return 2
    try:
        manifest = json.loads(args.manifest.read_text())
        scores = json.loads(args.scores.read_text())
        if not isinstance(manifest, dict) or not isinstance(scores, dict): raise BaselineError("invalid_input")
        result = {"artifact": model_contract(args.model), "evaluation": evaluate(rows(manifest), scores), "inference": "externally-supplied-deterministic-scores"}
    except (OSError, json.JSONDecodeError, BaselineError) as error:
        print(f"ERROR: {error}", file=sys.stderr); return 2
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"artifactSHA256": result["artifact"]["sha256"], "samples": result["evaluation"]["groups"]["overall"]["n"]}))
    return 0


if __name__ == "__main__": raise SystemExit(main())
