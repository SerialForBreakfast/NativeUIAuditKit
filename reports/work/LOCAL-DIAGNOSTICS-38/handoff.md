# Local diagnostics38 — complete for review

## Decisions

- Keep geometry union experimental. It recovers42/46target bodies, but accepting
  every rectangle as a focus candidate harms selection. Preserve semantic eligibility
  and distinguish whole controls from text fragments/panels before integration.
- Higher resolution alone does not repair iOS page-control detection. Keep640 as
  the deployed configuration; investigate annotation granularity/training coverage.

## Focus result

Unchanged bundled CoreML classifier and production16%-expanded cropper scored all
2,289fixed candidates from46real frames, CPU-only. Successful pass PID42070,
67.789seconds. Model tree, input, executable and script hashes retained in
[protocol](focus-v3/protocol.json). This is a geometry-only diagnostic, not the
production role-filtered caller or FDR036.

On seven explicitly complete screens: six wrong winners and one tied maximum.
All46frames:3unique correct target winners,17distractor winners,22ties,4missing
target bodies. Partial annotations do not establish whole-frame accuracy.
35/46frames have maximum score exactly1.0; the282joint highest-scoring boxes
include fragments and enclosing regions. The classifier is not a general-purpose
rectangle-validity test. [Top-box accounting](focus-v3/top-diagnosis.json).

Additional retained-score diagnosis preserves known production YOLO role exclusions
while provisionally accepting new geometry:2/7complete correct,5wrong; all46target
outcomes7correct/17distractor/18ties/4missing. Baseline production4/7remains stronger.
This is post-result diagnostic replay, not a separately qualified replacement or
threshold selection. [Role-filter result](focus-v3/role-filter-replay.json).

Initial pass stopped on an edge-crossing box; second stopped on a body entirely
below frame whose expanded crop overlaps it. Preserved both aborted outputs.
Tool now explicitly opts into original proposal bounds, expands then clamps exactly
as production. Default containment remains strict. Real-tool contract checks verify
default rejection, opted-in success and rejection of wholly nonintersecting expanded
regions. Do not pre-clamp a body before production expansion.

## iOS result

Frozen first20test GalleryPage +20OnboardingPage IDs, same resident Run013 weights,
fresh inference at640/960/1280, fixed .001capture confidence/.7NMS; evaluation
operating confidence.25. Same40page-control truths across arms.

| Input | Body recall at .50 / .75 | Typed predictions at .25 | AP50 | AP75 | Seconds |
|---|---|---|---|---|---|
|640|0/40 /0/40|10(all unmatched)|.000625|0|3.012|
|960|0/40 /0/40|3(all unmatched)|.078542|0|2.910|
|1280|0/40 /0/40|0|.108696|.001389|4.351|

AP includes detections below .25; it must not be confused with operational recall.
Mean short side grows8.55→17.11pixels. GalleryPage1280AP50.2722 versus
OnboardingPage.0321, so family behavior differs. Tiny selected retained development
sample, not a new benchmark or DS-G8 result. PID41749,120image evaluations,10.273
seconds across arms including per-arm overhead; not controlled warm benchmarking.
[Inputs](ios/protocol.json), [results](ios/result.json), [families](ios/family-diagnosis.json).

## Verification and next tranche

9focused Python tests, offline Swift build and134Swift tests passed. Both main
results replay successfully from retained outputs. Real tool bounds contract passed.
1.2MiB output including aborted diagnostics. All data roles unchanged.
Software: verified. Data admission: unchanged diagnostic. Integration: experimental
only. Model gate: not advanced. TTR coordination deferred per maintainer.

Next sizeable local tranche: (1) qualify whole-control candidate eligibility using
the retained scores and independent split before tuning; (2) audit iOS dot-group
annotation versus detector box granularity and source-family support; (3) assemble
full-screen training contracts from already admitted synthetic groups, explicitly
checking ancestry/completeness. Execute training only when its exact membership and
assigned budget pass. Source-dependent coverage remains queued for the TTR update.
