# Handoff: iOS r6 Run 009 Replacement Baseline

**Status:** Assigned tranche complete for review.  
**Owner:** NUIAK Architect / iOS Baseline Evaluator.  
**Date:** 2026-09-24T02:24:31Z  

## 1. Deliverables and Evidence

- **Prediction Artifact:** `reports/work/IOS-R6-BASELINE-20260923/prediction_artifact.json` (versioned `prediction-artifact-v1`, self-compared and validated with `reference_comparison.py`).
- **Evaluation Report:** `reports/work/IOS-R6-BASELINE-20260923/eval_report.json` (complete accounting of all 2,000 replacement test images).
- **Synthetic Regression Suite:** `reports/work/IOS-R6-BASELINE-20260923/synthetic_regression_manifest.json` (250 members deterministically selected via `regression_selector.py`).
- **Actionable Error Analysis:** `reports/work/IOS-R6-BASELINE-20260923/error_analysis.md`.

## 2. Key Metrics Summary

- **Evaluated Images:** 2000 / 2000 (100% accounted for, 0 failures).
- **Supported Class Count:** 13 / 41 classes.
- **Unsupported Class Count:** 28 / 41 classes (explicitly unavailable, AP 0.0 not imputed).
- **mAP@0.50 (Supported 13 classes):** **0.5549**.
- **mAP@0.50:0.95 (Supported 13 classes):** **0.3982**.
- **Device / Runtime:** mps, cold load 0.0299s, mean inference 48.32ms.

## 3. Independent Outcomes

- **Software:** Passed. Evaluator, prediction-artifact exporter, reference comparison, and regression selector all pass strict assertions and package boundaries.
- **Data:** 2,000 replacement test images evaluated honestly; 13 supported vs 28 unsupported classes documented without leakage or invented metrics.
- **Integration:** Toolchain fully connected from reconstructed r6 corpus through YOLO layout export, inference, and prediction artifact serialization.
- **Model Gate:** DS-G8 remains **open** (requires full 41-class coverage and mAP ≥ 0.85; r6 replacement test split covers only 13 classes).

## 4. Next Steps

- Review baseline metrics against future candidate models evaluated on identical r6 test splits.
- Address the 28 missing classes in a supplementary dataset tranche before attempting 41-class production training.

