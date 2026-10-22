# Restore Standard execution and test iOS retention

Owner: Maximum-mini-NUIAK. Date: 2026-10-22.
Standard behavior, shipped models, original checkpoints, and the optional observer remain unchanged.

## Readiness repair

Queue enumeration ignores non-directory metadata files, including `.DS_Store`.
Malformed job directories still fail visibly. Execution and reporting use the same directory filter.
Both regression tests pass. The live CLI reports 0 ready jobs before the new admissions, rather than crashing.
The 415 blocked entries are queue records, not independent blocked investigations.
The running dashboard process keeps its loaded modules. Do not restart it during active work to load this change.

## Standard restoration

`recovery488-repeat9-parity` completes with verified outputs.
The existing trainer uses 16 original training rows, the retained initialization, and repeat 9.
Uninterrupted training and a separate-process restoration both reach epoch 30.
Weights, optimizer, scheduler, Torch/MPS random state, and loss history have exactly zero difference.
Python and NumPy random state also match. The boundary checkpoint remains unchanged.
Qualification takes about 66 s. It is a mechanism test, not a model accuracy result.

The full DEDUP486 checkpoint remains at epoch 16. Its trainer and backbone hashes match the qualified code.
Its settings match the qualification checkpoint. Every qualification row belongs to the original checkpoint membership.
The restore adapter still checks the complete original training contract before executing the full continuation.
Wrong repeat settings and foreign subset rows fail unit tests. Old qualification records still require exact membership.

`recovery488-repeat9-negatives` checks missing optimizer state, changed seed, and changed row order through the queue.
`dedup486-exposure-resume23` was registered but revoked before execution. Preserve its specification and reservation record.
The proposed endpoint change altered a module pinned by active iOS training. The approved module bytes were restored immediately.
The running iOS approval verifies again. Its approval record was not changed. Its final execution checks remain required.
The original restore adapter has no clean partial-epoch endpoint. Do not describe the withdrawn job as runnable.
At the next idle boundary, qualify bounded endpoint support and reconcile the unstarted revoked reservation before a successor.
The continuation registry reserves cumulative time and storage against the original failed attempt.
The maintainer's additional allowance remains 1,800 s. The total storage allowance remains 2 GiB.
Keep the final epoch-30 continuation and all 17 comparisons pending until the new checkpoint and usage receipts verify.
Do not reuse the original failed producer identity to release downstream comparisons.

## Independent iOS comparison

`ios491-lowlr` reuses the IOS482 mixed membership and Run013 initialization.
Change initial AdamW learning rate from 0.001 to 0.0001. Keep seed, epochs, preprocessing, and evaluation groups unchanged.
Retain last, best, and final checkpoints, as in the existing mixed-data comparison.
The fit has a 1,800 s limit and 2 GiB output limit. No new data or capture is needed.

The compiled graph contains 14 approved jobs:

- 1 detector fit.
- 6 retained evaluations against Run013.
- 1 terminal decision report.
- 6 class-error diagnostics selected only after regression.

Three additional approved reports compare the new outputs against the previous mixed-data run, native-only run, and Run013.
These reports reuse predictions. They do not repeat baseline inference or training.
Any lost Run013 detection rejects replacement. Report unmatched predictions without claiming verified false positives.
Training metrics remain training diagnostics. No fit or terminal result automatically promotes a model.

## Validation and remaining boundaries

The integrated Python suite passes 63 tests. The bounded endpoint change is withdrawn, not delivered.
The caller test verifies that only learning rate changes in the resident trainer arguments.
Swift tests start but make no progress for 10 min. Only this turn's test processes are stopped; the log remains preserved.
The complete Swift suite is not passed. The experiment runner remains untouched.
The separate offline Swift build passes in 1.02 s.
Log: `.build/recovery488-swift-test.log`.
The runner owns all experiment execution. New code and specifications do not establish model improvement.
Useful ready duration must come from current readiness and measured runtimes, not cumulative timeout ceilings.

Private definitions: `reports/work/RECOVERY488/` and `reports/work/IOS491/`.

## Handoff snapshot

The detached runner starts `ios491-lowlr-train`. Its restored source approval verifies.
The negative restoration job remains pending. Six iOS regression diagnostics remain conditional, not independent blockers.
Ten iOS evaluation and reporting jobs depend on the current fit. The 3 matched reports have valid refreshed approvals before execution.
The comparable mixed-data fit took 1,124 s, about 19 min. This is a planning reference, not an overnight duration claim.
No claim of 24–48 h ready work follows. Standard continuation admission and dashboard activation remain incomplete.

Next idle tranche: qualify bounded continuation endpoints, account for revoked unused reservations, and admit the remaining Standard chunks with terminal comparisons.
Check active approval code through `checks.code`, not a top-level `code` field, before changing any imported source.
