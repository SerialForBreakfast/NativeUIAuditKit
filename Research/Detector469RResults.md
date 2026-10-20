# DETECTOR469R — Matched results

Review date: 2026-10-19. This report does not claim a model improvement.

## Execution

The background runner completes 30 training epochs in 433.62 s.
The fit uses 97 distinct training images and fixed-last selection.
Trainer validation uses training images. It does not measure held-out accuracy.
The ID correction resolves the preparation failure. The original DETECTOR469 attempt remains preserved.

## Completed controls comparison

The matched baseline is DETECTOR422-v2. Both candidates use the same crop models and evaluation inputs.

| Profile | Baseline selections | Candidate selections | Correct abstentions, both | Lost successes | New wrong selections |
| --- | ---: | ---: | ---: | ---: | ---: |
| Standard | 24 | 24 | 3 | 0 | 0 |
| HCF | 24 | 24 | 3 | 0 | 0 |

Each profile covers 9 groups. These are inspected development cases, not release qualification.
The controls comparison shows parity, not improvement.
The decision report retains its rejection gate because historical Standard row and tab failures remain declared.
That gate does not mean this controls comparison introduces a new regression.

## Position and robustness results

All 3 comparison reports complete and pass output-integrity verification.

| Scope | Profile | Correct selections, baseline → candidate | Gains | Lost successes | New wrong selections |
| --- | --- | --- | ---: | ---: | ---: |
| Positions, 48 frames | Standard | 26 → 24 | 1 | 3 | 0 |
| Positions, 48 frames | HCF | 26 → 24 | 1 | 3 | 0 |
| Robustness, 16 frames | Standard | 8 → 9 | 2 | 1 | 0 |
| Robustness, 16 frames | HCF | 0 → 7 | 7 | 0 | 2 |

Position cases cover 4 groups. Robustness cases cover 2 groups. Counterpart profiles are not independent evidence.
Standard robustness wrong selections decrease from 1 to 0. HCF wrong selections decrease from 5 to 3, but introduce 2 new wrong cases.
Aggregate counts therefore hide regressions. The candidate does not pass the previous-success gate.

The Standard bottom-row losses are `native424-row-bottom-light-standard-item-0-0`, `item-2-0`, and `item-3-0` under that prefix.
All 3 retain a focused-control proposal. Their failure is downstream of proposal presence.
The Standard edge loss is `hcf402-edge-clearance-standard-item-2-0`. Its focused proposal disappears.
Keep these cases in every relevant follow-up. Do not use their measured offsets as training data.

## Next decision

REVIEW470 tests a fixed baseline-first fallback across all 12 retained conditions.
The rule preserves a unique baseline selection. It consults the new detector only when the baseline abstains.
Truth labels evaluate the result but do not select the branch. Reject new wrong selections or lost no-focus abstentions.
Eight paired geometry diagnostics separate missing proposals from box changes and crop-score failures.
These jobs reuse retained predictions. They require no training, captures, or production changes.

The next training correction remains conditional on that diagnosis. More data alone does not resolve these measured regressions.

Compare proposal recovery, full-screen selection, abstentions, and case-linked regressions across all 3 reports.
Standard, iOS, shipped models, and previous-success requirements remain unchanged.

## Evidence

- Fit: `reports/work/research-queue/jobs/detector469r-train/attempts/1/out/fit.json`.
- Controls: `reports/work/research-queue/jobs/detector469r-controls-decision/attempts/1/out/decision.json`.
- The controls receipt passes output-integrity verification.
- Derived ID mapping: `reports/work/DETECTOR469R/id-map.json`.
