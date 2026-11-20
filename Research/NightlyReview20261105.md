# Nightly research review — November 5, 2026

Owner: Maximum-mini-NUIAK. Computed model results remain provisional for Joe’s review.
Window: November 5, 07:43:31.976 UTC through November 6, 07:48:20.089 UTC.
This follows the last successful nightly cutoff. The trigger is November 5, 23:48:20.089 America/Los_Angeles.
The verified USB checkout has approximately 1.5 TiB free. No substitute checkout is used.
Exact attempt IDs and hashes are retained in `reports/work/NIGHTLY-20261105/review-window.json`.

## What improved

No verified model improvement this review period.

All 15 UNBLOCK575 attempts complete. Their final output inventories pass size and hash verification.
Eight jobs acquire and review native packets. Seven jobs compare cached iOS predictions and summarize retained losses.
Execution completion, output integrity, data eligibility, and model acceptance remain separate.
No model is trained, promoted, or replaced during this review.

## What we learned

The native sample supplies 12 aligned capture events: 9 focused and 3 known no-focus observations.
These events cover 8 unique image payloads and 3 related construction groups in one sample application.
Moving and no-focus variants share q1 ancestry. Do not count them as independent groups.
They are not independent real-app qualification. No input is sent, so they do not establish action-driven temporal behavior.

The existing crop consumer accepts all four episode requests without taxonomy guesses.
Exact repeated images produce one crop set. The expected output contains 24 crops: 5 focused and 19 unfocused.
Profile observations remain unknown. All outputs remain review_only with training admission disabled.
That profile gap blocks profile-specific training and HCF qualification, not model-free static crop preparation.

IOS575 attributes 16 retained Run013 losses to 8 misses, 3 localization failures, 3 class/assignment cases, and 2 baseline-assignment changes.
The losses involve 9 list rows, 3 labels, 2 navigation bars, 1 home indicator, and 1 disclosure group.
The existing scorecards retain predictions only at confidence 0.5 or higher.
A recorded miss therefore does not prove that no useful lower-score box exists.
This uncertainty motivates a fixed diagnostic floor, not deployment threshold tuning or another unchanged training fit.

## What regressed

No new model comparison establishes a new regression in this window. The prior rejected candidates remain rejected.
The current corpus and diagnosis do not establish improved real-app detection or focus selection.
No attempt fails in the review window. Earlier exhausted and superseded attempts remain preserved.

The existing consumer frame summary labels zero selections as a miss, including known no-focus frames.
Its scoring entry point also requires development rows and cannot consume these review_only crops unchanged.
Prepare a bounded correction that preserves roles and separates correct abstention, false selection, and unknown references.
Do not bypass either limitation or count invalid outcomes as model evidence.

## What runs next and what each test decides

The next batch reuses existing adapters. No new code, capture, training, or service change is needed for admission.
Every job retains an 800 s limit, a 100 MB output limit, and one attempt.
The combined reservation is 5600 s and 700 MB. This is not an estimated workload duration.

| Exact job | Decision |
| --- | --- |
| `native576-opaque-train-crops` | Prepare production crops from the observed opaque-control packet. Keep the role review_only. |
| `native576-motion-qualification-crops` | Prepare unchanged-focus crops from the declared moving-content scene. Do not infer verified background motion. |
| `native576-ring-qualification-crops` | Prepare the declared ring appearance. Do not infer an observed system HCF profile. |
| `native576-nofocus-qualification-crops` | Preserve observed unfocused controls as negative crops without inventing focus. |
| `ios577-baseline-lowfloor` | Record Run013 predictions at the fixed 0.01 diagnostic floor. |
| `ios577-candidate-lowfloor` | Compare exact IOS573 weights on the same 12 images and unchanged annotations. |
| `ios577-lowfloor-classagnostic` | Reuse those scorecards to distinguish box placement from class or assignment errors. |

The iOS subset contains 12 previously inspected failure images and 194 unchanged reference controls.
The original 16 loss IDs remain the target. Incomplete labels do not support verified false-positive rates.
Production confidence stays at 0.5; input size stays at 640 and NMS IoU stays at 0.45.
If good boxes return below 0.5, prepare a distinct training-only confidence correction.
If boxes remain absent or misplaced at 0.01, prioritize proposal or geometry learning.
Preserve unresolved cases. Do not claim qualification from this selected development subset.

Exact specifications, roles, hashes, groups, budgets, and branch decisions are in [the batch plan](../reports/work/NIGHTLY-20261105/next-batch.md).
All seven exact jobs are admitted and approved. Admission disposition is retained in `reports/work/NIGHTLY-20261105/admission.json`.
No jobs are continued. No exhausted attempt receives an unverified extension.

## Queue health

One health and readiness pass observes an active continuous runner, no current job, and no runner error.
Before refill: 0 ready, 0 running, 399 dependency blockers, and 3 other blocked jobs.
There are also 117 exhausted jobs, 29 unselected branches, 410 superseded records, and 3799 completed jobs.
These are disjoint display categories. Exhausted and historical jobs are not ready work.

The new seven-job graph has five initially satisfied dependency paths and two producer-dependent paths.
Prior crop preparation takes about 0.58 s per job; prior iOS scores take about 4–7 s per condition.
The batch is expected to take tens of seconds, with startup variation. It is not an overnight reserve.
The ready reserve before refill is 0 s. Remaining work after dispatch is not resampled during this maintenance pass.
The runner already owns continuous execution. No start, stop, or restart occurs.

Recorded queue execution occupies 57.68 s of the 86688.11 s review window: **0.067%**.
Completed execution accounts for 57.68 s; failed execution accounts for 0 s.
The remaining 86630.43 s has no recorded queue execution. It is not independently verified idle or stopped time.
Manual builds, review, and visualization work are outside this queue occupancy measure.
Attempt ends use recorded start time plus wallSeconds because terminal receipts omit an end timestamp.
Occupancy is not scientific progress.

## Blockers and approvals

Maximum-mini-NUIAK owns review-only crop scoring and correct no-focus frame accounting.
This bounded correction unblocks 24 crop diagnostics, including 9 negative crops from known no-focus scenes.
Acceptance must cover focused, known no-focus, unknown-reference, wrong-choice, and multiple-choice frames.
Preserve production preprocessing, fixed thresholds 0.85/0.70, candidate counts, roles, and prior successes.
Existing implementation authority covers that work; the nightly review does not implement it.

Standard consumer verification still lacks an executed-input receipt through TTR.
Sillycon-TTR acknowledges the distinction between reconstructed crop RGB and the buffer Vision actually executes.
The original update reaches TTR through forward1904 and reply1907, relayed1908. This is acknowledgment, not implementation delivery.
NUIAK owns its package-hook Git handoff before consumer qualification. No Git publication occurs in this review.

Sillycon-TTR reports source 7320f49e merged to master and a separate 1.9.0 release qualification.
The relevant Git objects are present in Developer/TVTestRig. This review performs no source build, app activation, or runtime acceptance.
Preserve TTR’s reported build/test pause. No recovery choice is made on the user’s behalf.
No new NUIAK artifact transfer is offered. Unrelated accessibility enrollment and token benchmarks are excluded from this report.

The replay-boost receipt still lacks evidence pins. Its scientific condition is contradicted; keep the branch unselected.
Two retained recovery records also remain blocked by changed inputs or a missing exact route repair.
Do not bypass those checks or let them block unrelated work.

## Priority changes and reasons

1. P0: use the aligned native corpus through existing production crop preparation. It advances several focus tracks without another capture.
2. P0: connect review-only scoring and correct no-focus accounting. These are precise consumer gaps, not reasons to change data roles.
3. P0: finish Standard input provenance through the supported package and TTR path. A reconstructed hash cannot substitute for executed-input evidence.
4. P1: distinguish low confidence from missing iOS geometry before choosing another training correction.
5. Keep HCF profile qualification and action-linked temporal tests independent. Do not lower thresholds on inspected cases or infer motion from a declared recipe.
6. Do not repeat rejected fits or fill the queue with unchanged diagnostics. The larger overnight reserve remains unprepared and explicitly unresolved.
