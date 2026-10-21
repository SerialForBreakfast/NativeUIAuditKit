# CROP474 — Matched second-seed graph

## Decision and scope

POLICY473 completes all 14 nodes.
CROP471 recovers 1 Standard tab selection across 91 observations.
The policy selects CROP471 on all 91 observations. The fallback adds no selection.
It loses no previous success and adds no wrong selection.
All 3 no-focus abstentions remain correct.
The result justifies a bounded repeatability comparison, not model promotion.

Change only the training seed from 371 to 372.
Reuse CROP471's verified preparation and eligible membership.
Do not add inspected development cases to training.
Keep fixed-last selection, 30 epochs, and the original initialization.
The new fit permits 1,800 s, 2 GiB, and 1 attempt.
The previous fit takes 1,217 s. Scoring and reports add separate execution time.

## Graph

1. Fit seed 372 from the pinned initialization.
2. Score all 17 retained conditions.
3. Compare those scores with the original control and seed 371.
4. Score all 12 full-screen conditions on frozen detector proposals.
5. Compare full-screen decisions with both controls.
6. If a comparison passes, report independent verification requirements.
7. If a comparison fails, report case-linked losses and missing proposals.
8. If evidence is inconclusive, stop with the unresolved question.

Reuse the same new scores where compatible.
Do not repeat completed baseline scoring or preparation.
Conditions use the existing typed queue gates.
Missing evidence blocks dependent nodes.
The graph does not create further fits, captures, or model promotions.

## Acceptance

Require retained successes against both controls.
Report wrong selections, misses, no-focus outcomes, and family support separately.
Keep Standard primary. HCF cannot justify a Standard regression.
Keep the earlier detector and consumer failures visible.
Supported development comparisons do not close runtime or independent evaluation gates.
Keep iOS models and Standard runtime unchanged.

This graph tests seed sensitivity, not independent data generalization.
Do not describe 2 seeds as deployment qualification.

## Execution inventory

The graph contains 88 immutable jobs.
It reuses existing preparation and baseline results.
Only 1 job trains a model.
The remaining jobs score conditions, compare results, or report conditional next actions.
Conditional follow-ups do not authorize another fit.
The prior fit takes about 20 min. Total scoring duration remains unmeasured.
This graph does not establish overnight capacity.

## Admission verification

All 88 exact specifications pass the combined admission review.
Only `seed` differs between the training configurations.
Approvals use 9 transactions, with at most 10 jobs per transaction.
The final snapshot shows 1 running fit and 87 dependent jobs.
The runner reports no error. It starts the fit without a restart.
Dependent jobs wait for verified outputs or branch conditions.
Local evidence resides under `reports/work/CROP474/`.
The combined review is `preflight-all.json`. The approval receipt is `admission-receipt.json`.
