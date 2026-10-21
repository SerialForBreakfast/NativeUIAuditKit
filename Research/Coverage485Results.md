# COVERAGE485 — Compare original-data coverage

## Reviewed finding

The IOS482 128-image control gains 28 detections and loses 30 against Run013.
The retained development comparison rejects replacement. This is not release accuracy.
The IOS480 64-image control previously gains 40 detections and loses 47.
These aggregate counts do not show which cases change between controls.
IOS482 mixed training remains incomplete at this review. Do not infer its result from the control.

## Prepared comparisons

Reuse the existing comparison adapter for 2 graphs with 3 jobs each.
Each graph compares all 6 retained conditions and publishes case-linked gains and losses.

| Graph | Control | Candidate | Decision |
|---|---|---|---|
| 128 versus 64 | Completed IOS480 original-data control | Completed IOS482 original-data control | Identify recovered and newly lost cases before attributing gains to coverage. |
| 1,024 versus 128 | Completed IOS482 original-data control | Approved COVERAGE484 candidate | Determine whether broader coverage reduces regression or warrants an optimization correction. |

Both graphs retain Run013 and native-only comparisons through the existing adapter.
The second graph waits for COVERAGE484 scoring. It does not wait for IOS482 mixed training.
No training, capture, inference, or source change repeats for these reports.
Fixed epochs change the number of optimizer updates when corpus size changes.
Do not interpret this comparison as an equal-update test.

Any Run013 loss rejects replacement. Review matched-control losses even when that gate passes.
Neither outcome promotes a model or starts another fit.
If broader coverage still regresses, prioritize the existing bounded optimization-adapter task.
Do not start further coverage scaling without a useful result.

## Queue capacity

RESERVE483 already contains 4 independent campaigns with 89 approved jobs.
Their estimated duration remains 3–4 hours, not a full night.
These 6 cached comparisons add useful decisions, not meaningful overnight duration.
Dependency waits and unselected branches do not count as ready execution.
Standard, shipped models, previous successes, and original evidence remain unchanged.

## Evidence

Local receipts reside under `reports/work/COVERAGE485/128-vs-64/` and `reports/work/COVERAGE485/1024-vs-128/`.
Each graph records its immutable request, specifications, preflight, and admission receipt.
The control decision resides under `reports/work/research-queue/jobs/ios482-control-decision/attempts/1/out/`.
