# Retained OCR class comparisons

Use this diagnostic for native iOS development scorecards. It does not change production fusion.
The request format is `ocr-class-comparison-v1`.
Supply hash-pinned `labels`, `scorecard`, and `helper` files.
The helper uses the structured `--json` interface in `scripts/ocr_helper.swift`.

Compile a specification:

```sh
PYTHONPATH=scripts .venv-yolo/bin/python -B scripts/ocr_class_comparison493.py REQUEST.json --id NEW_ID --output NEW_SPEC.json
```

Submit and approve the exact specification through the existing queue interface.
The detached runner executes it. Do not start another scheduler.
The adapter verifies images, labels, raw predictions, model identity, dimensions, and coordinate conventions.
Its fixed group split prevents fitting on evaluation groups within the request.
Do not combine related device variants and claim independent evidence.

The rule uses exact normalized text, confidence 0.8, and overlap 0.1.
It requires a single text region and consistent class evidence from at least 2 fitting groups.
Conflicting tokens and missing text preserve the baseline prediction.
The comparison retains every supplied evaluation label and reports lost successes.
It never changes boxes, detector confidence, thresholds, or model weights.

Each job permits 800 s, 100 MB, and 1 attempt.
Each native OCR call permits at most 60 s within that total limit.
An optional `reuseAttempt` pin names a failed result from this adapter.
The adapter verifies its specification, input identities, and output hashes before reusing completed OCR.
Use a new job ID for this successor. Preserve the original attempt.
Malformed OCR, changed inputs, and insufficient groups fail explicitly.
Unknown label review and incomplete annotations remain visible in the report.
The report does not establish complete false-positive coverage or permit model promotion.

## Geometry comparison from retained outputs

Set `ruleMode` to `geometry-envelope`. Set `retainedAttempt` to the pinned completed result of the original comparison.
The adapter verifies original inputs and all output hashes. Missing retained OCR fails without starting OCR or capture.
The rule uses control aspect ratio, text width divided by control width, and text height divided by control height.
Each range uses fitting-group minimum and maximum values with a fixed 20 percent expansion.
Evaluation labels cannot change these ranges. Out-of-range predictions retain the original detector class.
The report includes the text-only comparison and all supplied-label regression cases.
This conservative rule tests error prevention. Unchanged baseline predictions do not establish a model improvement.
