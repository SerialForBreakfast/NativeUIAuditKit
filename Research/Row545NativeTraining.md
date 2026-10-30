# ROW545 — Complete native rows unblock iOS training

Maximum-mini-NUIAK prepared this tranche on October 29, 2026.

## Delivered

- The detached runner completed 3 native capture jobs using the existing source build and T46 template.
- Qualification accepted 32 training frames from 16 seed groups.
- Qualification accepted 4 development frames from 2 separate seed groups.
- Each frame contains 17 source-derived control annotations.
- Group, encoded-image, and decoded-pixel checks find no training/development overlap.
- The training membership keeps 125 retained frames and adds the 32 native frames.
- All 21 training, scoring, reporting, and conditional diagnostic jobs have approval.
- The runner started `ios545-rows-train`. No service restart was needed.

## Question and limits

Do complete native row annotations recover row detections without losing retained iOS detections?
The fit uses Run013 initialization and the retained control configuration for 30 epochs.
The fit permits 30 min and 2 GiB. The earlier 125-image control took 13.8 min.
The 157-image fit has an estimated runtime of 17–20 min. This is not an overnight workload.
Additional images increase training exposure. This comparison does not isolate annotation changes from increased exposure.

The recipes restrict capture to fully visible Pro layouts with 4 plain rows and 2 toggle rows.
SE geometry and longer clipped lists remain outside this qualification.
Source-derived annotations are not blinded human reference labels.
No real-app benchmark images or historical data roles change.

## Baseline evidence

Run013 reports 16 missed row bodies among 24 row annotations across the 4 new development frames.
The report also flags 2 row localization errors. Other annotated classes report no misses on these frames.
These counts describe generated development scenes. They do not establish real-app accuracy.
The unavailable historical `row537-score-run013` output was excluded from the new graph.
No capture was repeated to replace that historical result.

## Execution graph

1. Train `ios545-rows-train` on the 157 admitted frames.
2. Score 6 retained conditions and the new row development set.
3. Compare the 6 retained conditions with the matched control.
4. Reuse predictions to compare retained conditions against Run013 and native-only results.
5. Score the retained control on the new row set and compare it with the candidate predictions.
6. Run existing class-agnostic diagnostics only if the compiled decision reports regressions.

Any lost previous success rejects replacement. Row gains require independent qualification before promotion.
Standard, shipped models, and optional HCF remain unchanged.

## Validation and evidence

The focused Python suite passes 23 tests.
Tests cover missing labels, duplicate labels, uncertain annotations, aliased row boxes, clipping, footer overlap, and partition leakage.
Existing training graph and rehearsal comparison tests also pass.

Local evidence is in `reports/work/ROW545/`:
`scope.json`, `partition-check.json`, `training-request.json`, `compiled/compiled.json`, and `handoff-admission.json`.
Capture manifests and results remain in the queue attempts.

## Remaining work

Review the candidate and all retention reports together after execution.
If rows improve without losses, qualify another native layout before broader training.
If rows improve but retained detections regress, use the class-linked losses to choose the next correction.
If rows do not improve, inspect proposal coverage and localization before another fit.

The independent tvOS benchmark still needs the published TTR replay source and complete input provenance.
The last coordinator check contained no new TTR source reply. NUIAK has not qualified that peer-reported implementation.
TTR owns its branch and publication process. This iOS experiment does not depend on it.


## Nightly result — October 30, 2026

The fit finishes in 16.77 min. New row matches increase from 8/24 to 24/24.
The six retained conditions lose 13 detections against control and 15 against Run013. Replacement is rejected.
The direct T65 report fails its same-weight requirement. The nightly review admits a T42 successor without new inference.
See [nightly review](NightlyReview20261030.md).
