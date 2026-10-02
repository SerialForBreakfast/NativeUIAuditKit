# Reviewed transitions — implementation and findings

October 1,2026 PDT. Software and companion experiment complete. Human-dependent
correctness evaluation remains pending in Tasks.md.

## Delivered

- Saved human revision → exact batch/image/snapshot validation → endpoint readiness
  → actual pixel/native-crop comparison → separate geometric scoring and error report.
- Prediction receives only before-bounds and the two images. After-labels and bounds
  are isolated in scoring. Ambiguous matches, abstentions and missing review remain
  explicit; frozen accepted labels are protected against conflicting overlays.
- Optional pixel-only diagnostics work while after-image review is pending. Mutable
  editor checkboxes and copied rectangle proposals cannot become accepted truth.
- All seven existing Settings frames opened together. Cocoa startup receipt passed;
  original editor files remain the user's working batch.

## Evidence and useful result

| Check | Result |
|---|---|
| Fixed generated pixel experiment |9/9: unchanged, highlight, dim, scrolling highlight, growth, scroll-only, duplicate target, missing target, illumination |
| Real retained387→391transition |10before controls;9tracked;9unknown and1ambiguous/unavailable; correctness unscored |
| Recording inventory |166actions;14timing-ready;0pairs with both endpoints reviewed in the accepted scope |
| Integrated regression suite |111Python tests pass |
| Offline Swift |Build clean;14XCTest+120Swift Testing=134tests pass |

The real result is informative: the simple manipulations work, but this actual
transition produces no decisive focus-change prediction. Nine tracked controls have
brightness change below the existing threshold and clipped crop context suppresses
growth evidence; the tenth has ambiguous texture. Labels are needed to distinguish
appropriate caution from missed focus changes. This does not justify training or
threshold changes yet.

The frozen before-image label is `voiceover-settings`; the prepared after-image is
named `voiceover-settings-transition`. This naming convention is retained, not
silently converted to runtime context evidence. Scored runs exclude differing labels
until that correspondence is resolved. Full-scene claims additionally need complete
control coverage, not merely a reviewed focused rectangle.

## Verification links

- [111Python tests](artifacts/regression-tests.log), including actual recording CLI,
  native crops, immutable revision, partial review, tampering, label conflicts,
  truth isolation, ambiguity and output collision.
- [Swift build](artifacts/swift-build.log), [134Swift tests](artifacts/swift-test.log).
- [Fixed pixel experiment](artifacts/pixel-stress-final/results.json).
- [Retained pixel observations](artifacts/retained-pixel-observations-v2.json).
- [Initial retained reviewed-only replay](artifacts/retained-transition-eval.json).

Reports retain implementation hashes at execution. Earlier logs/reports remain as
iteration evidence; the final fixed experiment pins the final implementation.
New model/data eligibility and live runtime qualification remain unassessed here.
Shared coordination is not applicable to these local implementation results; existing
structural-data/source requests remain the producer's actionable work.

## Next substantial tranche

1. Finish the open seven-frame review; ingest its immutable revision, run production
   crop QA, resolve annotation screen-name correspondence, and publish per-control
   errors/abstentions for all supported recorded actions.
2. Use the actual failures to select the next bounded comparison: highlight-only,
   growth-only and combined signal with fixed membership; preserve unchanged
   evaluation data and report coverage alongside correctness.
3. When structural originals arrive, complete campaign intake/all-crop QA and one
   combined sampled review, then resolve exact source role/admission for the
   approved changed-data comparison. Continue the existing export request.
