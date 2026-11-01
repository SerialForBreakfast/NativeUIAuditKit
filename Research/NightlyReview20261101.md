# Research review — November 1, 2026

Owner: Maximum-mini-NUIAK. The trigger runs at 11:40 a.m. America/Los_Angeles, outside the intended nightly time.
Review window: October 31, 06:46:06.133 UTC through November 1, 19:40:29.660 UTC.
This follows the last successful nightly cutoff. Exact attempts and hashes are in reports/work/NIGHTLY-20261101/review-window.json.
The verified USB volume has approximately 1.5 TiB free.

## What improved

No verified model improvement this review period.
Measurement improves: reviewed real-app references now expose actual consumer failures.
The runner completes 37 attempts. All 37 output inventories pass size and hash verification.
These include the iOS preservation fit, the HCF continuation, and retained comparisons. Execution completion does not establish model acceptance.

Maximum-mini-TTR now runs published source ac85177b. Three retained Standard replays preserve the earlier predictions.
Source, preprocessing, and taxonomy identities are observed. Executed crop identity remains unavailable.

## What we learned

The reviewed Simulator pilot contains 21 distinct frames from 3 apps. Detection references cover 9 NewsTV frames only.
NewsTV control recall is 23/207: article cards 22/54 and tab pills 1/153. Article precision is 22/24.
Official COCO AP50 is 0.206, AP75 is 0, and AP50–95 is 0.021. These are selected-pilot metrics.
Text references are absent. Unmatched text predictions cannot establish text precision.
The current manifest passes asset and label validation. It preserves 1 rejected duplicate alongside the 9 scored NewsTV cases.

Across all 21 frames, the selector finds 0/15 visibly focused controls, with 1 wrong selection and 14 focused-frame abstentions.
It selects on 2/6 frames reviewed as having no visible focus effect. Native focus can still exist on those frames.
These are visual-reference outcomes, not proof that UIKit has no focused object.
The separate development set has 21 focused frames from 2 apps. The shipped selector finds 0/21.
Supplied-box scores exceed 0.85 on 4/21 development frames. This diagnostic is separate from full-screen selection.

The NewsTV inactive-scene discrepancy has a local cause: its notification permission prompt.
The controlled-content build removes that prompt and produces an active scene. No TTR lifecycle repair is required for that cause.

CAPTURE553 provides 74 development rows with verified capture receipts.
At 4K, the detector matches 17/116 secondaryButton labels; 73 receive primaryButton predictions.
At 1080p, it matches 0/40 secondaryButton labels, with 35 wrong classes. Taxonomy review precedes a training interpretation.

## What regressed

IOS551 classification preservation changes no matched decisions against ROW545.
Against Run013 it gains 20 detections and loses 15. Replacement is rejected. B405-270 is confirmed contradicted.
The fit completes in 1,122.94 s. Repeating coefficient 1.0 without a changed hypothesis is not justified.
Its 7 conditional diagnoses remain unselected because the matched-control decision is inconclusive.
The separate Run013 retention decision is contradicted. Unselected nodes are not readiness failures.

The restored HCF fit completes its original 30 epochs within the approved cumulative budget.
Its comparisons lose 6 known-box Standard successes without gains on 15 screen sets.
On 2 matched crop sets it labels all 8 negatives as focused. Do not extend this rejected fit.
Standard, shipped models, and the optional observer remain unchanged.

## What runs next and what each test decides

This review admits 3 exact T42 jobs through the existing template interface:

- capture553-geometry-4k-controls: separate control-class errors from missing boxes at 4K.
- capture553-geometry-4k-artwork: separate artwork-class errors from missing boxes at 4K.
- capture553-geometry-1080p: identify the same distinction at 1080p on its retained inputs.

These jobs reuse predictions and labels. They perform no capture, training, threshold change, or model promotion.
Improved class-agnostic coverage triggers taxonomy review. Remaining missing geometry directs coverage or localization work.
The 4K and 1080p sets are not declared a matched resolution experiment.
Historical T42 median runtime is 0.48 s across 155 completed diagnostic jobs. The new batch is seconds-scale, not overnight work.

FOCUS556 S1 is the next substantial independent task: qualify the in-progress candidate scorer, then compare retained models on development data.
Do not dispatch its uncommitted implementation as a qualified template. Preserve its current owner's edits.
S2–S4 require training-only Fixture membership and corpus preparation before approved training can execute.
The current nightly task cannot implement or capture those inputs.

## Queue health

One initial snapshot records 0 ready, 0 running, 403 blocked, 29 unselected, 105 exhausted, 400 superseded, and 3,648 completed jobs.
Of the blocked entries, 391 are dependency-related: 387 incomplete, 3 changed specifications, and 1 missing output.
The other 12 comprise 10 changed inputs, 1 unqualified restoration chain, and 1 Maximum-mini-TTR requirement.
The runner is active and waiting. No start, restart, service change, or lock change is required.
The review adds 3 approved independent diagnostics after that snapshot. It does not poll their execution.
No longer fit or continuation is admitted. No useful overnight reserve is established.

Completed execution occupies 1,498.56 s of 132,863.53 s: 1.13% non-overlapping wall-clock occupancy.
Failed terminal execution occupies 0 s. The other 131,364.97 s has no recorded queue execution.
Historical idle versus stopped time is unavailable. Direct app qualification and manual review fall outside this queue metric.
Occupancy is not scientific progress.

## Blockers and approvals

Sillycon-TTR still owns the requested suppression correction and executed crop identity.
The coordinator has no new substantive TTR reply in this review. Storage alone does not prove forwarding or acceptance.
The CAPTURE553 request at cursor 1840 used an invalid event kind. This review corrects that envelope at cursor 1845.
The correction preserves its original scope. Forwarding remains unconfirmed.
No new transfer offer is present. No dataset transfer is performed.

Maximum-mini-NUIAK owns FOCUS556 scorer qualification, training corpus preparation, and matched graph admission.
The maintainer already approved the training-only Fixture scope. No repeated consent is needed within that scope.
Additional app content and toolchain decisions remain separate. They do not block the existing focus-development comparison.
The pilot already informs diagnosis and training design. Preserve it as a retained regression set; do not call it untouched independent qualification.
Fresh flows remain necessary for the planned 200-screen qualification.

## Priority changes and reasons

Prioritize Standard focus hard negatives, tab-pill representation, and detector taxonomy because the real-app pilot identifies frequent consumer failures.
Keep iOS independent, but stop unchanged preservation runs after the failed retention result.
Stop the completed HCF continuation. More time cannot repair its observed classification regressions.
Keep the 3 cached comparisons short. Do not fill the queue with repeated diagnostics to improve occupancy.

Evidence: [reviewed pilot](../reports/work/REALAPP554/pilot-v2/baseline-report.md),
[focus development](../reports/work/REALAPP554/focus-dev-baseline.md),
[FOCUS556 plan](Plans/FocusRealApp556.md), and [parallel workflow](Parallel551Workflow.md).
