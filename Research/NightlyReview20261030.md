# Nightly research review — October 30, 2026 UTC

Owner: Maximum-mini-NUIAK.
Window: October 29, 18:48:09.477 UTC through October 30, 06:41:17.635 UTC.
This begins at the last successful review cutoff. The mounted USB has about 1.5 TiB free.
Exact attempt IDs, hashes, and intervals are in `reports/work/NIGHTLY-20261030/review-window.json`.

## What improved

Adding complete native row training improves matched row detections from 8/24 to 24/24 on 4 generated iOS development screens, with broader retention regressions.
These screens represent 2 seed groups, not 4 independent applications.
The baseline here is Run013. The retained trained control also detects 8/24 rows.
The candidate preserves other Run013 successes on this small subset.
This is a development gain, not a qualified replacement or real-app accuracy estimate.
No model is promoted. Standard and shipped models remain unchanged.

The row training path now admits 32 complete native frames from 16 groups.
The fit uses 157 images and finishes 30 epochs in 1,006.35 s, or 16.77 min.
The prior estimate was 17–20 min. Execution completion does not establish model acceptance.

## What we learned

The ROW545 graph selects and completes its predefined regression diagnostics automatically.
Across 6 retained iOS conditions, class-aware matching loses 9 row detections against the matched control.
Class-agnostic matching loses 4. Class confusion therefore explains part of the row regression, not all of it.
The class-agnostic report also flags 25 row localization errors across 340 annotations.
These overlapping diagnostics are not independent error counts and must not be added together.

For tvOS temporal focus, 3 retained models classify the unchanged and movement pairs correctly.
Removing before-frame information loses the movement result while preserving unchanged focus.
Both pairs share one sample ancestry. Moving backgrounds, dismissal, and independent departure groups remain missing.
No new full-screen Standard focus or verified no-focus accuracy is established.

Sillycon-TTR reports local commit `bc7987affbbc1a2e013eece6eed5b922be1ff91a`, not pushed.
It separates partial provider results from incomplete model scoring and adds SDK readiness diagnostics.
Its retained geometry suggests proposals in letterbox padding. Raw tensor confirmation remains missing.
These are peer findings. Maximum-mini-NUIAK has not received and qualified the source revision.
TTR retains ownership of its branch and publication workflow.

## What regressed

The candidate gains 12 retained detections but loses 13 against the matched control.
Against Run013, it gains 20 and loses 15. Replacement is rejected.
Run013 losses include 9 rows, 3 labels, 1 disclosure group, 1 navigation bar, and 1 home indicator.
The development gain does not override these losses.

The direct new-row comparison fails with `comparison_weights`.
T65 requires identical model weights; this experiment compares different weights.
The nightly review registers `row546-retained-comparison` using existing T42 and both retained scorecards.
The successor repeats no capture, training, or inference. The original failed attempt remains preserved.
No template source or service changes are needed.

## What runs next and what each test decides

One job is admitted: `row546-retained-comparison`.
It measures direct gains and losses between the matched control and candidate on the new row development set.
Its measured analogue takes about 0.5 s. Its ceiling remains 800 s and 100 MB.
This is useful reporting recovery, not an overnight workload.

The existing 7 conditional diagnostics already finished. Do not duplicate them.
No training continuation is justified: ROW545 completed its fixed 30 epochs and failed retention acceptance.
The next training correction needs a frozen class-preservation comparison informed by the 9 lost retained rows.
Keep the new development groups excluded from training. Preserve all original annotations and checkpoints.

## Queue health

The single maintenance snapshot records 0 ready jobs and 0 running jobs before the successor admission.
It records 403 active blocked entries: 391 dependency-related and 12 other blockers.
There are 105 exhausted attempts, 22 unselected branches, 400 verified superseded entries, and 3,510 completed jobs.
The 12 other blockers comprise 10 changed inputs, 1 restoration qualification, and 1 TTR requirement.
The runner is active and waiting. It needs no restart.
After admission, the successor passes readiness with no blockers. Its remaining expected duration is about 0.5 s.
This report does not claim the queue has an overnight reserve.

The window contains 37 attempts with terminal receipts: 36 successful and 1 failed.
All recorded output inventories pass verification.
Non-overlapping completed execution is 1172.111 s; failed execution is 0.500 s.
Total recorded occupancy is 2.741% of 42788.158 s.
The remaining 41615.547 s has no recorded queue execution.
Historical idle versus stopped time is unavailable. Occupancy is not scientific progress.

## Blockers and approvals

REAL543 needs published TTR replay source and complete model, preprocessing, taxonomy, and image provenance.
The 50-screen pilot still has 0 qualified independent applications and 0 scored benchmark screens.
NewsTV activation, other application SDK qualification, and blinded human labels remain required.
WeatherFeels also needs the missing Apple Metal toolchain; no download is performed here.

PIPELINE538 training remains blocked by the producer's test-only role contract and independent training groups.
TVOS515 consumer qualification still needs the exact retained Standard fallback through TTR.
TEMPORAL544 extensions need qualified content-only negatives and destination reporting support.
Those are implementation or data tasks. The nightly scope does not build the missing adapters.
The approved shared volume is not mounted. No offered archive is substituted with peer summary evidence.
No new budget, installation, schedule, or promotion approval is requested in this review.

## Priority changes and reasons

Keep Standard consumer parity and independent accuracy qualification first.
Prioritize class-preserving iOS correction over more row generation: complete row data now works, but retention fails.
Stop unchanged ROW545 training and completed diagnostic repeats.
Continue application preparation independently of TTR publication during the next implementation tranche.
Keep HCF separate and optional.

Evidence: [ROW545](Row545NativeTraining.md), [temporal findings](Temporal544Ablation.md), and [independent validation](RealAppValidation543.md).
