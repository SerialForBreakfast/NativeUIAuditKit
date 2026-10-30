# QUEUE548 — Retained results and independent work

Owner: Maximum-mini-NUIAK. October 30, 2026.

## Verified iOS result

Frozen-feature training finishes in 792.2 s. All 19 jobs complete.
The candidate preserves 24/24 new row detections on four development frames.
Across six retained conditions, it gains 17 Run013 detections but loses 16.
Against ROW545, it gains 6 detections but loses 10.
Each retained comparison contains 2,030 annotated objects. The candidate misses 210 at the fixed threshold.
These conditions are development evidence. They do not establish real-app accuracy.
Catalog B405-267 is closed as contradicted. No model changes occur.

## Approved queue additions

Eight Standard reporting jobs compare completed Standard-only and joint-profile fits on 17 matched retained conditions.
They reuse existing predictions through model_decision_batch434.
The reports separate supplied-box performance from proposal-based selection and retain lost-success checks.
Their decision determines whether joint-profile training helps Standard or creates transfer losses.

Six iOS reports use T42 with fixed geometry bins on the frozen candidate and ROW545.
They determine whether losses concentrate in small controls or wide rows.
Class-agnostic diagnostics already completed. These jobs do not repeat those diagnostics.
All 14 jobs are approved. Readiness verifies 11 ready jobs and 3 jobs waiting for their report dependencies.
The detached runner owns execution.
Each report permits 800 s and 100 MB. These ceilings are not expected runtime.
These short reports do not constitute overnight training.

## Longer work

The wider additive fit is running at review. The wider control is queued.
The matched arms use 1,030 and 998 training images, respectively.
Each retains 30 epochs, 3 h, 2 GiB, and one attempt.
Comparable execution suggests 3.5–4 h total training, including the running fit.
That estimate is not a measurement of remaining duration.
The next training correction waits for the matched coverage result.
If coverage also fails preservation, use training-only anchors to define a class-preserving objective.
Do not expand the dataset again without a changed hypothesis.

## Exhausted-work audit

DEDUP486 already has completed continuation successors. Its timeout does not justify another run.
PROFILE425 HCF stops at the original time limit with checkpoint epoch 26.
Its checkpoint includes optimizer, scheduler, and random state.
Its trainer hash differs from the current trainer. The current continuation adapter also forces different deduplication.
Extra time alone cannot preserve this experiment.
The next bounded repair must restore the pinned trainer and deduplication=False, then qualify continuation parity.
Preserve the original checkpoint and attempts. Complete the original 30 epochs only after qualification and a recorded cumulative budget.
This optional HCF repair does not block Standard or iOS.

## TTR

The last received reply identifies local commit bc7987affbbc1a2e013eece6eed5b922be1ff91a as not pushed.
TTR chooses its publication workflow. Consumer qualification requires a published Git revision.
The latest channel check returns no messages after cursor 1796.
The exact response is retained in reports/work/QUEUE548/peer-check.json.
Missing TTR source blocks real-app consumer qualification, not the admitted independent work.

## Evidence and next tranche

Admission and readiness records are in reports/work/QUEUE548/.
Frozen decisions are in the retained ios547-frozen queue outputs.
Research/Retention547Training.md records the fixed training controls and original acceptance criteria.

1. Review both wider fits against Run013 and their matched control.
2. Use the Standard transfer reports to choose separate-profile or joint-profile follow-up work.
3. Qualify the original HCF restoration contract before admitting its remaining epochs.
4. Intake the TTR Git revision when published, then finish the Standard consumer replay check.

Standard, shipped models, previous successes, and original evidence remain unchanged.
No runner restart, direct training, capture, dependency installation, or promotion occurs.
