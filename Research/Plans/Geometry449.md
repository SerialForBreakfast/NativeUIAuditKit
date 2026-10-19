# GEOMETRY449 — Diagnose the remaining Standard misses

Owner: Maximum-mini-NUIAK. Date: 2026-10-18.

## Completed coverage result

All 30 COVERAGE447 jobs and 7 VALIDATION448 jobs complete.
The frozen cascade adds no gains on the extension. It loses no successes and adds no wrong selections.
Standard remains at 12 correct selections and 8 misses across 20 focused frames.
The single no-focus frame produces a correct abstention.
The result is inconclusive for wider efficacy. It is not a model improvement.
The retained comparison still has 2 gains, both within 1 original group.
HCF remains unchanged. Its separate outcomes do not control Standard acceptance.

The extension contains 21 Standard frames across 4 original groups.
The 8 frames with distinct group identifiers add no gains.
The 13 related stress frames also add no gains.
No case becomes training data or final-audit evidence.

## Failure diagnosis

The retained classifier succeeds with known boxes on all 20 focused frames.
On detector boxes, 6 of its 8 misses lack a matching focused-control proposal at IoU 0.5.
Those cases are 3 dark-background frames, 1 grid frame, 1 large-control frame, and 1 neighbor-spacing frame.
The other misses are neighbor-spacing item 0 and shelf item 3.
Both have matching proposals but fail crop selection.

The supplemental detector supplies some missing boxes but loses others.
Its neighbor-spacing item 0 produces a wrong selection with the retained classifier.
Do not replace the retained detector or weaken the cascade agreement requirement from these observations.

## Next batch

Use T61 on both detectors across all 6 retained conditions: 12 jobs.
Reuse verified T57 reports and receipts. Do not repeat inference, capture, or training.
Measure missing controls, overlap, size ratios, center offsets, ambiguous matches, and crop-score differences.
Use successful cases and no-focus cases as controls, not only failures.
Keep original crops, models, thresholds, and previous attempts unchanged.

T61 reports score differences for both crop models.
Its `knownOutcome` and `detectorOutcome` fields describe the candidate, not the retained baseline.
Use the source T57 rows when interpreting baseline selection failures.
Its raw group field remains a case identifier. Use the frozen COVERAGE447 membership for original-group interpretation.
Do not sum related cases as independent trials.

## Decisions

If both detectors miss the same focused controls, prioritize training-only coverage for those conditions.
If a matching box exists but scoring fails, measure crop geometry before proposing classifier training.
If supplemental boxes recover controls but cause wrong selections, keep the current conservative policy.
Any proposed fit needs admitted training-only examples and matched regression checks.
Do not train on these development offsets. Do not sweep thresholds on these inspected cases.

Each job permits 800 s, 100 MB, and 1 attempt.
These are short cached diagnostics, not an overnight workload.
The detached runner owns execution. Standard stays unchanged. HCF stays optional.
Local batch, preflight, tests, and admission receipts live under `reports/work/GEOMETRY449`.

## Admission

All 12 focused tests pass. All 12 jobs pass preflight and receive exact approvals in groups of 10 and 2.
The existing runner receives the jobs without a restart. No training or capture starts from this review.
No source code changes. The prior integrated Swift checks remain applicable.
