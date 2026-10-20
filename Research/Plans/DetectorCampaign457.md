# Reusable detector campaigns — DETECTOR457

Owner: Maximum-mini-NUIAK. Standard remains first. HCF remains separate and optional.

## Implemented workflow

`scripts/detector_campaign457.py` compiles one request through the existing queue.
It reuses T89 training, T56 detector scoring, and T57 full-screen focus scoring.
The final report compares identical frames and the same crop model across detector candidates.
Known-box scores, labels, thresholds, and preprocessing remain fixed.
The compiler also accepts completed comparisons without repeating training or inference.

Each request supplies these fields:

- `version`: `detector-campaign-v1`.
- `id` and `question`: stable identity and the decision question.
- `membership`: a pinned development membership with case, group, profile, and condition.
- `training`: a T89 description, or `null` for completed comparisons.
- `pairs`: conditions and exact baseline and candidate job IDs.
- `retainedFailures`: unresolved regressions and their pinned evidence.
- `budget`: maximum jobs, seconds, and output bytes across the new graph.

For new training, set each candidate reference to `null`. The compiler binds the new model automatically.
Run `scripts/detector_campaign457.py REQUEST --output DESTINATION` to compile.
Use the existing registration and approval interfaces after readiness checks.
Compilation does not approve jobs or start execution.

## Admission and comparison gates

New training requires complete admitted labels and training-only membership.
The compiler rejects shared groups and identical image hashes across training and development.
These checks do not prove independence between related layouts. The data review still owns ancestry checks.
The fit uses 30 epochs, a 2 h limit, fixed initialization, and the existing output budget.
T56 retains detector class reports and case-level errors. T57 supplies full-screen focus and proposal presence.
The terminal report separates Standard and HCF gains, losses, wrong selections, and no-focus abstentions.
It preserves unresolved regressions even when a narrower comparison improves.
No result grants model acceptance or navigation authority.

## Current qualification

The isolated tests cover two campaigns through the actual queue, immutable compilation, changed evidence, leakage, and regression rejection.
The new-fit test validates T89 to T56 to T57 bindings without running synthetic training.
Two real campaigns reuse all 8 completed detector comparison conditions.
The controls campaign covers 54 profile frames across 9 groups.
The robustness campaign covers 32 profile frames across 2 groups.
Frames and profiles do not count as independent groups.

Standard control selections improve from 19/24 to 24/24. All 3 no-focus abstentions remain correct.
Standard robustness selections fall from 14/16 to 8/16, with 6 lost successes.
The candidate remains rejected. These are retained development results, not a new model improvement.

## Remaining producer requirement

The 18 proposed training groups are reservations, not qualified captured data.
They target 72 Standard frames and 72 matched HCF counterparts.
The six existing capture jobs remain development data. Do not convert them into training examples.
Recovery passes, but the first dependent capture exhausts the retained TTR evidence budget.
The other five captures stop at the recovery guard.
Preserve all attempts, recovery journals, and failed sessions.

Maximum-mini-TTR needs bounded evidence retention or verified offload before another capture attempt.
Sillycon-TTR receives the failure through the existing repair discussion.
Do not increase the quota again or remove failed evidence automatically.
After recovery, validate native inventory, focus, rendered geometry, hashes, duplicates, ancestry, and exact training roles.
Then compile one matched fit and all retained comparisons through this adapter.
Require a separate T88 check for the lost tab case before replacement review.

## Workflow milestone boundaries

This tranche extends reusable compilation to detector training and complete focus comparisons.
RESEARCH451-07 qualifies the existing shared approval read on a fixed 5-job snapshot.
Across 3 paired trials, median time falls from 0.958 s to 0.181 s with identical approval decisions.
Full source hashing remains active. No live approval record changes.
This measures warm local reads, not training speed or concurrent dispatch behavior.
The three-campaign measurement requirement in RESEARCH451-08 remains open.
Existing receipts provide execution durations. They do not measure preparation time or avoidable idle time.
Do not repeat completed scoring solely to measure workflow speed.

Private requests, exact pins, receipts, and validation logs stay under `reports/work/DETECTOR457`.
