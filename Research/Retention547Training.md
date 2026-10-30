# RETENTION547 — Preserve iOS detections while learning native rows

Owner: Maximum-mini-NUIAK. Prepared October 29, 2026.

## Observed failure

ROW545 detects 24/24 native development rows versus Run013 at 8/24.
Across six retained conditions, it loses 15 Run013 detections and 13 matched-control detections.
Nine matched-control losses are rows. Class-agnostic matching reduces row losses from 9 to 4.
The remaining failures require coverage or geometry diagnosis. Class confusion explains only part of the loss.
The corrected T42 direct report completes. The failed same-weight T65 report remains preserved.

## Admitted experiment: feature preservation

`ios547-frozen-train` changes only backbone freezing against ROW545.
It preserves the 157 training frames, Run013 initialization, rates, fixed seed, and 30 epochs.
The graph includes seven matched scores, a decision, seven conditional class diagnostics, and three retention reports.
All 19 jobs have approval. The existing detached runner starts the fit without restart.
Budget: 30 min and 2 GiB for training. Estimate: 13–17 min from previous frozen fits.
The decision requires preserved native row gains and zero lost successes against Run013 and ROW545.

## Admitted independent comparison: original-data coverage

Two fits test whether broader original-data coverage reduces forgetting.
The control has 998 original training frames. The additive arm uses those frames plus 32 qualified native row frames.
Both arms exclude all 26 historical RTLMirror frames from the existing 1,024-image corpus.
Every retained image from the smaller 125-frame control remains present.
Qualification verifies file hashes, dimensions, complete labels, class support, and group and decoded-pixel exclusions.
The larger corpus contains 40 annotated classes. This does not authorize shipping unsupported classes.
No development images enter training. Original annotations remain unchanged.

Each arm preserves Run013 initialization, the unfrozen configuration, learning rates, fixed seed, and 30 epochs.
The additive arm changes image count and training exposure. It is not an equal-update causal experiment.
Seven scores per arm measure the six retained conditions and the reserved new row set.
The matched retention reports compare both larger arms and Run013 on identical retained inputs.
Existing conditional diagnostics follow regressions. No automatic retraining or model promotion occurs.

The prepared set contains 38 jobs: two fits plus dependent scoring, reporting, and conditional diagnostics.
These are two training arms for one coverage question, not 38 independent experiments.
The fits do not depend on TTR or each other. Matched reporting waits for both.

A comparable 1,024-image fit takes 6,558.98 s, or 109.3 min.
Estimated training is 3.5–4 h total, plus short comparisons.
Requested limits are 3 h and 2 GiB per fit, with 30 fixed epochs and one attempt each.
The maintainer approves both exact larger budgets on October 30. The queue records each specification hash.
Admission applies the approved 3 h limits. The graph preserves fixed epochs, original membership, and retention gates.

## Acceptance and next actions

Require zero lost retained detections against Run013 and the relevant matched control.
Require preservation of the native row gains. Report class and geometry outcomes separately.
If freezing preserves retention and row gains, qualify another independent layout before promotion.
If broader coverage reduces losses, retain that evidence and examine remaining case-linked failures.
If both corrections fail, stop coverage expansion and define a class-preserving objective using training-only anchors.
Do not train again merely to occupy hardware. Preserve all checkpoints and failed evidence.

## TTR and Standard

The coordinator check after cursor 1796 returns no newer reply.
Sillycon-TTR last reports commit bc7987affbbc1a2e013eece6eed5b922be1ff91a as local and not pushed.
Git intake and local source qualification remain pending. TTR owns its branch and publication workflow.
Standard, optional HCF, shipped models, and the independent real-app benchmark remain unchanged.
The missing TTR publication does not block these iOS fits.

## Evidence

Local records: `reports/work/RETENTION547/`.
`coverage-qualification.json` records the image and class checks.
`prepared-graph-verification.json` verifies all 38 prepared specifications and dependency hashes.
`large-approval-scope.json` identifies the exact two proposed training specifications.
`frozen-admission.json` records the admitted fit, scoring, and conditional jobs.
The three additional frozen retention reports are approved in the existing queue.
No source implementation changes or new dependencies are needed for this tranche.


## October 30 admission

The maintainer approves both longer fits. All 38 specifications are registered and approved.
Each fit keeps 30 epochs, 10800 s, 2 GiB, and one attempt.
The existing runner owns execution. No service is restarted and no active job is cancelled.
Exact admission and health records are in `reports/work/RETENTION547/large-admission.json` and `large-handoff.json`.

## October 30 frozen result

The frozen fit completes in 792.2 s. All 19 graph jobs complete.
It preserves 24/24 new native row detections on four development frames.
Across six retained conditions, it gains 17 Run013 detections but loses 16.
Against ROW545, it gains 6 detections but loses 10. Both comparisons contain 2,030 labeled objects.
The candidate misses 210 objects at the fixed operating threshold. These are development counts, not deployment accuracy.
Replacement is rejected. Standard and shipped models remain unchanged.
The wider additive fit is running at review. The wider control remains queued.
The next decision uses their matched retention reports before another training change.
