# POLICY473 — Conditional selection-policy comparison

## Question

Can a fixed classifier fallback recover Standard selections without losing either classifier's previous successes?

CROP471 improves the controls slice but leaves position failures unchanged.
Its detector-controls comparison recovers 1 Standard selection.
Historical detector and consumer failures still prevent replacement.
Another training seed does not yet answer those failures.

## Fixed policy

Use the existing T60 `abstention-fallback` policy.
Use the candidate's unique selection when available.
Otherwise, use the baseline's unique selection when available.
Use scores only for selection. Use labels only to evaluate the result.
Keep the threshold at 0.85.

This is candidate-first fallback, not a promise of automatic preservation.
The decision gate tests preservation against both classifiers.
Keep Standard results primary. HCF results cannot unlock the next stage.
Standard runtime behavior and iOS models remain unchanged.

## Execution graph

1. Run 4 cached policy tests for buttons, rows, tabs, and no-focus scenes.
2. Verify exact membership and the common model, tool, and mapping identities.
3. Require at least 1 Standard gain against the baseline.
4. Require no lost successes against either classifier.
5. Require no new wrong selections against either classifier.
6. Require no-focus evidence and at least 3 recorded groups.
7. If all checks pass, run 8 position and robustness tests.
8. Combine the controls and expansion evidence in the final report.

The group requirement is a support floor, not proof of independent evidence.
If a preservation check fails, the gate reports `contradicted`.
If gains or support are insufficient, the gate reports `inconclusive`.
Neither outcome unlocks expansion.
Invalid or changed evidence fails the job and blocks its dependents.

The gate report supplies the reason when expansion stops.
The final report does not require another conversation when expansion qualifies.
No branch starts training, capture, export, or promotion.
No branch creates additional jobs.

## Inputs and limits

Reuse all 12 completed CROP471 full-screen reports and their verified receipts.
Preserve the 3 no-focus scenes and all retained position and robustness cases.
Keep original data roles, images, models, proposals, scores, and thresholds.
Do not create new training labels from these inspected cases.

The graph contains 14 jobs.
Each job permits 800 s, 100 MB, and 1 attempt.
The total ceiling is 11,200 s and 1,400 MB.
These ceilings are not predicted duration or reserved storage.
Cached comparisons should be short. This graph is not overnight training capacity.

## Reuse and completion

T60 performs the policy comparisons.
The reusable `policy_campaign.py` adapter summarizes reports and emits the existing typed condition.
Both the initial gate and the final report use that adapter with separate memberships.
The queue continues to own execution.

Tests cover accepted evidence, regressions, insufficient support, HCF-only gains, changed membership, and false counts.
Isolated queue tests cover accepted and rejected branches, restart, and duplicate prevention.
Missing support never becomes acceptance.
Retain all earlier failure evidence even when this policy improves the inspected cases.

If the final comparison passes, review independent native verification before a consumer trial.
If it fails, use its case-linked failures to choose one correction.
Do not increase epochs or repeat the fit merely to occupy the queue.

## Admission evidence

All 14 exact jobs are registered and approved.
The initial snapshot contains 4 pending policy tests and 10 dependent nodes.
The dependent count includes the initial decision gate and final report.
The runner remains unchanged.

All 23 focused tests pass.
The isolated queue confirms accepted branches, rejected branches, restart, and duplicate prevention.
The offline Swift check passes, including 177 Swift Testing cases.
Preflight reports no admission blockers.
Graph validation confirms the declared job count and cumulative ceilings.
