#!/usr/bin/env python3
"""
eval_reference_metrics.py — TASK-6a-11: multi-corpus PyTorch reference evaluation artifact.

Aggregates evaluation results across four named corpora into one standardized, hashed JSON so
"did this synthetic data actually fix the real-world failure" is answerable from a committed
artifact, not a chat transcript. Does not re-run YOLO inference itself — it reads
`eval_phase6a.py`'s existing output (that script owns the actual inference/mAP computation) and
is honest, per corpus, about what real data does or doesn't exist yet rather than filling in
placeholder numbers.

Corpora (see Tasks.md TASK-6a-11):
  1. synthetic_fixture_test_manifest — the withheld-template holdout `eval_phase6a.py` already
     evaluates. Available now.
  2. real_device_fixture_holdouts — TVTestRig fixture-batch `held-out` split. NOT available: no
     live hardware/simulator harvest has produced verified ground truth yet (Tasks.md TASK-6a-10).
  3. production_tvos_system_holdout — real Apple TV Settings screens crawled into
     `reports/tvos_settings_complete_tree.json`. NOT available: that file is OCR/hierarchy text
     from crawl exploration, not paired images with bounding-box ground truth — there is nothing
     to compute mAP against.
  4. frozen_regression_suite — NOT available: no such frozen set has been defined yet.

Usage:
  .venv-yolo/bin/python scripts/eval_reference_metrics.py [--previous PATH]

Output:
  reports/pytorch_reference_metrics.json (hashed; hash also printed to stdout for
  Research/ExperimentLog.md)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORTS = PROJECT_ROOT / "reports"
EVAL_PHASE6A_RESULT = REPORTS / "eval_results_phase6a.json"
OUTPUT_PATH = REPORTS / "pytorch_reference_metrics.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_of_json(obj: Dict[str, Any]) -> str:
    canonical = json.dumps(obj, sort_keys=True).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def build_synthetic_fixture_corpus() -> Dict[str, Any]:
    if not EVAL_PHASE6A_RESULT.exists():
        return {
            "available": False,
            "reason": f"{EVAL_PHASE6A_RESULT.relative_to(PROJECT_ROOT)} does not exist — run "
                       "scripts/eval_phase6a.py first.",
        }
    source = json.loads(EVAL_PHASE6A_RESULT.read_text())
    per_class = [
        {
            "class": entry["class"],
            "ap50": entry["ap50"],
            "ap50_95": entry["ap50_95"],
            "precision": entry["precision"],
            "recall": entry["recall"],
            "n": entry["n"],
        }
        for entry in source.get("perClass", [])
    ]
    return {
        "available": True,
        "sourceModel": source.get("model"),
        "sourceEvalDate": source.get("evalDate"),
        "split": source.get("split"),
        "nImages": source.get("n_images"),
        "mAP50": source.get("mAP50"),
        "mAP50_95": source.get("mAP50_95"),
        "perClass": per_class,
        "perImagePredictions": None,
        "perImagePredictionsNote": (
            "scripts/eval_phase6a.py does not currently dump per-image boxes/scores/classIDs — "
            "would need a --dump-predictions flag added there (re-running full inference), not "
            "fabricated here. See TASK-6a-11 in Tasks.md."
        ),
        "sourceArtifact": str(EVAL_PHASE6A_RESULT.relative_to(PROJECT_ROOT)),
    }


def build_r6_replacement_corpus(r6_report_path: Optional[Path]) -> Dict[str, Any]:
    if not r6_report_path or not r6_report_path.exists():
        return {
            "available": False,
            "reason": "r6 replacement baseline eval_report.json does not exist.",
        }
    source = json.loads(r6_report_path.read_text(encoding="utf-8"))
    per_class = [
        {
            "class": entry["name"],
            "supported": entry["supported"],
            "ap50": entry["ap50"],
            "ap50_95": entry["ap50_95"],
            "precision": entry["precision"],
            "recall": entry["recall"],
            "n": entry["n_gt"],
        }
        for entry in source.get("metrics", {}).get("perClass", [])
    ]
    return {
        "available": True,
        "sourceModel": source.get("model", {}).get("runName"),
        "sourceEvalDate": source.get("evaluationDate"),
        "split": source.get("corpus", {}).get("split"),
        "nImages": source.get("corpus", {}).get("imageCount"),
        "mAP50": source.get("metrics", {}).get("mAP50_supported"),
        "mAP50_95": source.get("metrics", {}).get("mAP50_95_supported"),
        "supportedClassCount": source.get("metrics", {}).get("supportedClassCount"),
        "unsupportedClassCount": source.get("metrics", {}).get("unsupportedClassCount"),
        "perClass": per_class,
        "perImagePredictions": "reports/work/IOS-R6-BASELINE-20260923/prediction_artifact.json",
        "sourceArtifact": str(r6_report_path.relative_to(PROJECT_ROOT)),
    }


def build_frozen_regression_corpus(reg_manifest_path: Optional[Path]) -> Dict[str, Any]:
    if not reg_manifest_path or not reg_manifest_path.exists():
        return {
            "available": False,
            "reason": "No frozen regression suite has been defined yet.",
        }
    reg_data = json.loads(reg_manifest_path.read_text(encoding="utf-8"))
    return {
        "available": True,
        "manifestPath": str(reg_manifest_path.relative_to(PROJECT_ROOT)),
        "formatVersion": reg_data.get("formatVersion"),
        "seed": reg_data.get("seed"),
        "target": reg_data.get("target"),
        "memberCount": len(reg_data.get("members", [])),
        "uncoveredClasses": reg_data.get("coverageExceptions", {}).get("uncoveredClasses", []),
    }


def build_unavailable(reason: str) -> Dict[str, Any]:
    return {"available": False, "reason": reason}


def compute_deltas(current: Dict[str, Any], previous: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if previous is None:
        return {"hasPrevious": False, "note": "First reference-metrics artifact — no prior run to diff against."}

    deltas: Dict[str, Any] = {"hasPrevious": True, "corpora": {}}
    for corpus_name, current_corpus in current["corpora"].items():
        previous_corpus = previous.get("corpora", {}).get(corpus_name, {})
        if not current_corpus.get("available") or not previous_corpus.get("available"):
            deltas["corpora"][corpus_name] = {"comparable": False}
            continue
        deltas["corpora"][corpus_name] = {
            "comparable": True,
            "mAP50Delta": current_corpus["mAP50"] - previous_corpus["mAP50"],
            "mAP50_95Delta": current_corpus["mAP50_95"] - previous_corpus["mAP50_95"],
            "previousModel": previous_corpus.get("sourceModel"),
            "currentModel": current_corpus.get("sourceModel"),
        }
    return deltas


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--previous", type=Path, default=None, help="Prior pytorch_reference_metrics.json to diff against")
    parser.add_argument(
        "--r6-baseline",
        type=Path,
        default=PROJECT_ROOT / "reports/work/IOS-R6-BASELINE-20260923/eval_report.json",
        help="Path to r6 baseline eval_report.json",
    )
    args = parser.parse_args()

    reg_manifest_path = PROJECT_ROOT / "reports/work/IOS-R6-BASELINE-20260923/synthetic_regression_manifest.json"

    corpora = {
        "synthetic_fixture_test_manifest": build_synthetic_fixture_corpus(),
        "r6_replacement_test_manifest": build_r6_replacement_corpus(args.r6_baseline),
        "real_device_fixture_holdouts": build_unavailable(
            "No live hardware/simulator harvest has produced verified ground truth yet "
            "(Tasks.md TASK-6a-10 — every existing capture sidecar has empty 'elements')."
        ),
        "production_tvos_system_holdout": build_unavailable(
            "reports/tvos_settings_complete_tree.json is OCR/hierarchy text from crawl "
            "exploration, not paired images with bounding-box ground truth — nothing to "
            "compute mAP against."
        ),
        "frozen_regression_suite": build_frozen_regression_corpus(reg_manifest_path),
    }

    artifact: Dict[str, Any] = {
        "generatedAt": utc_now(),
        "corpora": corpora,
    }

    previous_artifact = None
    if args.previous and args.previous.exists():
        previous_artifact = json.loads(args.previous.read_text())
    artifact["deltas"] = compute_deltas(artifact, previous_artifact)

    artifact["sha256"] = sha256_of_json({"corpora": corpora, "generatedAt": artifact["generatedAt"]})

    REPORTS.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n")

    available = [name for name, c in corpora.items() if c.get("available")]
    unavailable = [name for name, c in corpora.items() if not c.get("available")]
    print(f"Wrote {OUTPUT_PATH.relative_to(PROJECT_ROOT)}")
    print(f"SHA-256: {artifact['sha256']}")
    print(f"Available corpora ({len(available)}): {available}")
    print(f"Unavailable corpora ({len(unavailable)}): {unavailable}")
    for name in unavailable:
        print(f"  - {name}: {corpora[name]['reason']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
