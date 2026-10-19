# SELECTION444 — Bounded selection from Standard results

Owner: Maximum-mini-NUIAK. Date: 2026-10-18.

## Decision from STANDARD443

Reject the Standard-only crop model as a replacement.
The completed comparison covers 43 Standard observations across 13 related scene groups.
These include 40 focused observations and 3 no-focus observations.
These are inspected development cases, not independent release qualification.

| Proposal source | Crop model | Correct focus selections | Wrong selections | Misses | Correct no-focus abstentions |
| --- | --- | ---: | ---: | ---: | ---: |
| Retained detector | Retained mixed model | 29 | 1 | 10 | 3 |
| Retained detector | Standard-only model | 18 | 0 | 22 | 3 |
| Experimental detector | Retained mixed model | 19 | 1 | 20 | 3 |
| Experimental detector | Standard-only model | 13 | 2 | 25 | 3 |

With retained detector proposals, the Standard-only model gains 1 selection and loses 12.
Changing detector source with that model gains 9 selections but loses 14 and adds 2 wrong selections.
The earlier 3 tab-selection losses and 1 consumer-crop loss remain recorded.
No candidate passes the preservation requirement.

## Approved finite graph

Use the existing runner, T61 geometry adapter, and supplemental proposal adapter.
The new compiler adds typed selection gates and terminal summaries. It does not add a scheduler.
The request names 3 completed source jobs and fixed integer rules.
It contains no commands, arbitrary code, model mutations, or automatic retries.

1. Verify matched campaign reports and their cross-detector comparison.
2. Count Standard observations, groups, losses, score failures, and detector gains and losses.
3. Release only the diagnostic branches whose frozen rules pass.
4. Run each selected branch once within its fixed budget.
5. Publish case-linked findings and a next requirement. End the graph.

Require focused observations, no-focus observations, and at least 3 groups before branch selection.
This support floor does not establish statistical confidence or deployment safety.
Insufficient support produces an inconclusive gate and releases neither branch.
HCF results cannot satisfy Standard support or select a Standard branch.

### Branch 1 — Geometry and score diagnosis

Select this branch when the retained-detector comparison has at least 1 crop loss and 1 score failure.
Use T61 on the 16 completed scoring reports, covering 8 conditions and both detector sources.
Measure overlap, size, center error, ambiguous matches, and paired score differences.
Produce 1 summary per detector source within the existing dependency limit.

The result decides whether to prepare training-only geometry correction or investigate score competition.
Do not use the measured development offsets as training data.
Do not claim a geometry association proves that a correction improves the model.

### Branch 2 — Baseline-first supplemental detector

Select this branch when changing the detector yields at least 1 Standard gain and 1 Standard loss.
Run 8 cached comparisons through the existing supplemental adapter.
Keep a single retained-detector selection. Consult the experimental detector only after retained-detector abstention.
Use scores to choose the path. Use labels only to evaluate that choice.
Keep the existing 0.85 focus threshold and proposal settings.

Compare both crop models separately. Do not count their observations as independent trials.
Report unchanged wrong baseline selections as well as new wrong selections.
Require gains, zero lost successes, zero new wrong selections, and no-focus support before recommending independent verification.
Existing crop regressions still block replacement of the crop model.
A passing development policy receives no runtime or navigation authority.

## Limits and preservation

The graph has 28 jobs: 1 selector, 16 geometry audits, 8 supplemental comparisons, and 3 terminal summaries.
Every job permits 800 s, 100 MB, and 1 attempt. These ceilings are not runtime estimates.
No model inference, training, capture, download, export, or promotion occurs.
The adapters reuse verified predictions. They do not alter original images, groups, scores, or attempts.
The runner retains its existing 5-job dispatch cycles and priority rules.
Shared runner modules and submitted STANDARD443 specifications remain unchanged.

The compiler accepts at most 8 matched conditions. It rejects missing receipts, unmatched membership, and incompatible producers.
All future requests still need explicit scope and exact-job approval.
The worker cannot invent descendants or extend budgets.
Failed workers remain failed. They require an explicit repair successor, not automatic retry.

## Validation and next scope

Test supported, unselected, and inconclusive branches.
Test changed comparisons, invalid metrics, missing support, false counts, and duplicate execution prevention.
Run positive and negative requests through an isolated queue before live admission.
Run offline Swift checks after integration.

The next implementation depends on these terminal findings.
If supplemental selection adds wrong selections, reject that policy.
If geometry explains losses, prepare a matched correction using training groups and the complete retained regression suite.
If evidence remains inconclusive, name the missing input. Do not fill the queue with repeated comparisons.

## Qualification and admission

All 25 focused tests pass, including complete isolated execution of both selected branches.
A second request selects neither branch. No child attempts occur.
An invalid selector fails predictably and blocks its child. Restarting completed work creates no duplicate attempts.
Offline Swift checks pass 177 Swift Testing cases and 14 XCTest cases.

All 28 jobs are registered and individually approved in groups of at most 10.
The handoff snapshot shows 2 complete, 23 ready, and 3 summaries waiting on dependencies.
No execution failures appear. The existing runner continues without a restart.
Receipts and the snapshot remain under `reports/work/SELECTION444`.
These are short cached diagnostics, not overnight training capacity. No comparable live ETA is claimed.
