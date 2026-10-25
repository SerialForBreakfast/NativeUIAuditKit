# STREAM511 — Independent model investigations

Owner: Maximum-mini-NUIAK. Date: October 24, 2026.

## Decisions from completed evidence

The six MATCHED499 iOS comparisons lose 32 detections under class-agnostic matching.
The losses include 24 labels, 6 list rows, 1 progress view, and 1 scroll indicator.
Of these losses, 26 are misses and 6 are mislocalized boxes. Class-agnostic failure does not mean every loss is localization.
All losses occur in conditions 02 and 05. Related observations do not establish independent accuracy.
The prior mixed membership removes 45 original labels and 23 original list rows during fixed-order replacement.
This suggests a training coverage comparison. It does not prove that removal causes the losses.

The GEOMETRY500 reports find only 2 matching row bodies among 64 observations for each detector source.
Scoped proposals retain 10 correct Standard selections across 24 observations. General proposals retain 3.
Both results favor proposal recovery over another crop fit on these retained conditions.
These observations differ from SDK505, where supplied-box crop scoring also fails.
Do not combine these scopes or describe either result as release accuracy.

## Independent executable graphs

### IOS511: preserve original class coverage

Use 128 qualified training images: 112 original images and the same 16 native images.
Change only the original-image selection rule. Keep initialization, frozen backbone, learning rate, seed, and epochs unchanged.
Greedily minimize squared fractional loss of original class counts. Break ties by row ID.
Preserve at least one original example per class and recipe family. Selection uses training labels only.
Original label counts increase from 322 to 327. Original list-row counts increase from 185 to 196.
Original primary-button counts fall from 98 to 84. The comparison must measure this tradeoff.
All image hashes, dimensions, box bounds, labels, roles, and development exclusions pass qualification.
The SDK505 test group is not used.

The graph has 17 jobs: 1 fit, 6 scores, 4 reports, and 6 conditional diagnostics.
Use 30 epochs, fixed-last selection, 1800 s, 2 GiB, and one attempt for the fit.
Each diagnostic permits 800 s and 100 MB. These ceilings are not runtime estimates.
Comparable frozen fits take 689.5 s and 698.6 s. Expect approximately 12 min plus scoring and reporting.

Compare against frozen mixed, frozen original-only, native-only, and Run013 results.
Reject replacement if any retained success is lost. Inspect button losses explicitly.
If the matched correction gains detections without retention losses, prepare independent qualification.
If it regresses, use the registered class-agnostic diagnostics. Do not start another fit automatically.
If it changes no useful outcome, stop this selection rule without another seed.
No report authorizes model promotion.

### TVOS511: test proposal scale before another fit

Change detector input size from 1280 to 960 pixels with the same scoped detector.
Use existing button, row, and tab captures. Preserve crop models, confidence, NMS, thresholds, and labels.
The graph has 3 inference jobs, 3 full-screen focus jobs, and 1 comparison report.
Each job permits 800 s and 100 MB. No capture or training occurs.
This is a short independent investigation, not an overnight workload.

The existing detector campaign adapter now supports an explicit image-size intervention.
It checks unchanged model identity and all other settings. The default weights comparison remains strict.
The compiler accepts a future scorecard while checking fixed crop inputs before execution.
Two isolated campaigns exercise the same adapter without another script.

Require recovered Standard selections without lost successes or new wrong selections.
Keep HCF results separate. Missing no-focus coverage prevents release qualification.
If scale helps, qualify the same correction on additional retained negative and position groups.
If scale does not help, prioritize eligible body annotations instead of another scale sweep.
If evidence fails validation, preserve the attempt and repair the exact dependency.

## Separate data-dependent streams

| Stream | Next experiment | Exact missing input | Owner |
|---|---|---|---|
| Standard crop focus | Train matched native appearance with original-data rehearsal | Separate training groups with observed focus appearance and eligible crop labels | Maximum-mini-NUIAK and Sillycon-TTR |
| Optional HCF | Compare real focus rings against decorative and selected-but-unfocused controls | Explicit HCF mode and observed condition evidence; visible no-focus controls | Maximum-mini-NUIAK and Sillycon-TTR |
| Temporal focus | Compare departure and arrival against unchanged-focus background changes | Separate eligible training pairs; observed focus and image-aligned state | Maximum-mini-NUIAK and Sillycon-TTR |
| General detector training | Train body coverage with retained class checks | Complete target-class annotations and exclusions; registered inventory alone is insufficient | Maximum-mini-NUIAK and Sillycon-TTR |
| Session efficiency | Complete the approved reused-session comparison | Matching pinned application runtime for three unattempted sessions | Maximum-mini-TTR |

These are data prerequisites, not executable jobs or unselected branches.
The received SDK505 group remains excluded from training.
Unknown HCF mode, presentation bounds, occlusion, and pixel settling remain unknown.
Geometry stability does not prove pixel settling. Preferred focus does not establish observed focus.

## Producer follow-up

Maximum-mini-NUIAK reads and acknowledges coordinator replies through cursor 1384.
Sillycon-TTR reports optional visual provenance and native context support, but source remains uncommitted.
No matching native qualification or new eligible training export is supplied.
Request 1387 consolidates the missing dataset requirements through BigDog-Coordinator.
Storage is confirmed. Forwarding and producer acceptance are not inferred from storage.
A later reply reports two expired capture brackets: 1.403 s and 1.511 s.
Telemetry propagation passes, but fresh-packet qualification fails. No new eligible archive is offered.
Maximum-mini-NUIAK reads this reply and acknowledges through cursor 1387.
The producer must qualify capture timing without relaxing labels or replaying completed work.
Request existing supported recipes and eligible exports before new capture dispatch.
Do not duplicate completed captures or request features that already exist.

## Admission and validation

All 24 current jobs have exact approvals. The background runner starts ios511-coverage-train.
The handoff snapshot has 1 running fit, 3 ready inference jobs, 14 dependent jobs, and 6 conditional diagnostics.
Conditional diagnostics run only after the specified regression outcome. They are not independent research streams.
The original unstarted tvOS report is revoked. Its immutable successor is tvos511-size-r2-decision.
The successor treats missing no-focus coverage as inconclusive rather than a measured regression.
Actual losses still contradict the correction. Both specifications remain available.

All 34 focused Python tests pass. Two isolated input-size campaigns pass through the queue.
Wrong model identity and changed confidence fail the comparison tests.
The offline Swift build passes. Concurrent Swift test invocations stall in Vision waits.
Their logs and a process sample remain available. Explicit serial execution passes all 177 Swift tests in 56.482 s.
No production Swift change is needed. The failed test attempts are not counted as passing.
No experiment worker is stopped or restarted.

## Evidence and limits

- [Verified retained review](../reports/work/STREAM511/retained-review.json)
- [Queue snapshot](../reports/work/STREAM511/handoff-queue-classified.json)
- [Training qualification](../reports/work/STREAM511/ios-qualification.json)
- [iOS compiled graph](../reports/work/STREAM511/ios-full-compiled.json)
- [tvOS experiment definitions](../reports/work/STREAM511/tvos-batch.json)
- [tvOS comparison request](../reports/work/STREAM511/tvos-request-r2.json)
- [Model baseline review](ModelStatus500.md)
- [SDK correction results](SDK509CorrectionTranche.md)

These graphs answer 2 independent questions. Job count does not measure research progress.
The tranche does not supply a full overnight reserve. Longer work needs qualified data and a justified correction.
Standard, shipped models, original captures, and previous success evidence remain unchanged.
The detached runner owns execution. No service restart or active-job interruption occurs.

Recorded preparation and validation take 11.3 min after the initial untimed repository review.
The initial estimate is 45–75 min. Background experiment runtime is separate.
