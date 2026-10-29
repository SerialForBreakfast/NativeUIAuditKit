# STREAM520 — Retained endpoint focus and geometry

Owner: Maximum-mini-NUIAK. Review date: October 24, 2026.

## Completed comparison findings

All 18 STREAM519 jobs complete. Their output hashes verify.
The iOS training-selected checkpoint gains 20 detections and loses 43 against Run013.
It gains 10 and loses 36 against the retained matched control.
It gains 61 and loses 28 against native-only training.
Reject replacement. Choosing this checkpoint does not solve preservation.
Training diagnostics selected the checkpoint. These are development comparisons, not release qualification.

The tvOS fallback adds no gain over the candidate crop model alone.
Standard has 29 correct selections, 11 misses, and 3 correct abstentions across 43 observations.
The retained baseline has 28 correct selections. The candidate already supplies the additional success.
The aggregate gate calls that baseline-relative gain supported. It does not establish additional value from fallback.
HCF has 37 correct selections, 3 misses, and 3 correct abstentions across 43 observations.
No new wrong selections or lost successes occur. Keep Standard unchanged.
Do not add fallback complexity solely on this result.

## Two independent tracks

The retained archive contains 48 pairs across 8 content groups and 56 unique endpoint images.
Related images and groups do not establish independent-app accuracy.
Historical profiles and action timing remain unknown. These gaps do not invalidate verified endpoint observations.
The new comparison does not claim action causality, background-motion robustness, or transition timing.

1. Focus: compare TEACHER495 and TEACHER496 using identical registered boxes and production crops.
2. Geometry: compare the scoped DETECTOR422-v2 detector with the retained general tvOS detector on identical endpoints.

Each track has 8 bounded jobs and 1 dependency report. Both tracks can execute independently.
Focus reports preserve no-focus cases and separate wrong selections from abstentions.
Geometry reports measure registered-control coverage at IoU 0.5.
Partial registered labels do not support full-screen precision or class accuracy.
The jobs preserve producer splits, original pixels, review-only admission, and unknown profiles.
Repeated source case IDs receive image-hash suffixes in derived comparison IDs. Original manifests remain unchanged.
Identical images execute once per track. No capture or training occurs.

## Reusable adapter

sdk_endpoint_focus520.py accepts endpoint manifests, 2 pinned models, and the production crop tool.
It reuses existing packet checks, geometry checks, scoring outcomes, and production cropping.
It does not relax the existing action-pair adapter's timing checks.
Eight configurations reuse the same adapter without separate experiment scripts.
The existing sdk_geometry506.py adapter supplies the independent detector comparison.
Both reports retain case-linked evidence and prohibit automatic promotion.

## Validation and budgets

Eleven focused tests pass. They cover valid intake, changed hashes, duplicate pixels, wrong case identity, unknown focus, and no-focus selection.
Both graphs pass complete dependency and input preflight.
Each job permits 800 s, 100 MB, and 1 attempt. These are ceilings, not estimated workload.
Initial background focus jobs complete in approximately 3–4 s each.
This is useful diagnostic work, not an overnight workload.
No shared execution module or running service changes. The background runner owns execution.
The existing broad Swift test stall remains unresolved. No native code changes or new Swift suite pass are claimed.
The rejected draft remains preserved. Successor requests avoid overwriting it.

## Next decisions

If known boxes fail, inspect the specific crop errors before further detector training.
If known boxes succeed but geometry fails, prioritize the missing proposal classes and layouts.
If a candidate loses prior successes, retain the previous model and report each lost case.
Require independent eligible training groups before turning this review archive into a training proposal.
Do not infer training authority or complete class labels from SDK geometry.

## Evidence

Reports and immutable requests: reports/work/STREAM520/.
review519.json and verified519.json preserve reviewed results and hashes.
prepared-r2/compiled.json defines both tracks and their reports.
The detached runner records execution and results under the exact sdk520 job IDs.
