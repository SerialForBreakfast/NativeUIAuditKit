# Retained-bundle intake and independent direct pilot

2026-09-22 21:46 UTC. Supersedes the initial export-blocked handoff where noted.

## Completed

- `receive.py` used documented, read-only manifest/read-job IPC and a NUA-owned
  writer. All 12 original files and every chunk/file hash verified in 5.14 seconds.
  No app-container access, permission change, recapture or source-byte edits.
  TTR's `export-job` remains failed; this is a separately identified transfer route.
- All four TTR PNGs decode as 3840x2160. Both focused states and the shared reference
  were visually reviewed. `intake-audit.json` records per-frame nominal boxes and
  source observations; four inspection-only production crops render at 256x256.
- Corrected NUA's source-description validator to preserve finite numeric Swift
  Date values as emitted by TTR's default JSONEncoder, as well as existing strings.
  Booleans, missing/empty/container values and nonfinite numbers still fail.
  Bundle integrity now passes with two usable rows and no training approval.
  Actual simulator-manifest CLI exits2 `unsupported_theme`: resolved theme was
  discarded by producer `HarvestRecipeHeader`. No replacement metadata was invented.
- Independent direct smoke succeeded with all three frames/two pairs, native
  before/after interval evidence, current recipe metadata and healthy postflight.
  Four pinned recipe-planning source hashes still match. Raw evidence lives at
  `dataset/tvos_captures/direct-dialog-20260922-2147`; reviewed v1.4 production crops
  at `dataset/focus_ring/direct-dialog-20260922-2147`. Development-only, not final
  evaluation or full training readiness. Crop expansion contains visible effects
  beyond nominal native-view bounds; it is not a new visual-bound measurement.

## Genuine development baseline

`direct-baseline-protocol.json` freezes model, runtime preprocessing and four samples
before inference; `direct-baseline.json` is actual CPU CoreML inference.
Shipped artifact SHA256 `9e5ba294e545b4ae0c54aa5d483b1a1f681b6c30477882700b4dbe139b9c66b7`.
At frozen threshold0.85: TP2, FP2, FN0, TN0, abstentions0; 2/4 correct. Both
unfocused primary/cancel examples scored1.0. This tiny diagnostic is not a general
accuracy estimate. No threshold tuning or model changes. Model load76.79ms,
first inference9.68ms, three warm samples p50=1.72ms/p95=2.00ms; crops roughly54ms.
Oracle boxes only; proposal/navigation performance not assessed.

## Frozen pilot attempt and exact blocker

Executed the existing42-recipe catalog without modifying membership. Completed
recipes1–12: six action-dialog and six grid recipes,30 captured pairs/42 frames.
Recipe13 (media_shelf/light/seed7) failed before reference capture; recipes14–42
not attempted. Preserve `dataset/tvos_captures/direct-pilot-20260922-2152/failed.json`
and completed per-recipe files. The overall pilot is partial: **zero pairs admitted
from this partial run**, not a manually completed subset. Total expected pilot
membership remains246 pairs/288 frames. Remaining coverage is not waived.

The runtime returned `settle_timeout`; offline replay of `scene_signature` on its
retained last observation identifies `coordinate_conflict`, not missing native focus.
`header_shelf` pixel_bounds=[40,120,600,48], normalized_bounds=
[0.02083333,0.11111111,0.33333333,0.15555556] correspond to1920x1080, while reported
scene dimensions are3840x2160. Native diagnostic excludes this header as
unattached_or_hidden, yet it remains an annotated element. All four media cards
are measured; native reference focus is resolved/fresh/settled. Do not double
coordinates or delete the header in consumer evidence merely to make it pass.
Fixture HTTP postflight is responsive, same instance; no retry or restart.

## Validation and scope

12 focused harvest-consumer tests pass (0.098s). Approved offline `swift build`
passes (2.39s), `swift test` passes14 XCTest plus93 Swift Testing tests; no warnings
in final logs. Initial restricted build failed at sandbox_apply, not source; retained
separately. Three regression tests cover real numeric-date shape, invalid shapes and
missing theme still rejected. Prior unrelated changes/worker ownership preserved.

Software verified: passed for date correction and existing direct entrypoints.
Data eligible: two direct pairs development-only; TTR bundle integrity-only and
partial pilot ineligible. Integration qualified: direct dialog capture/crops/inference
pass; multi-family pilot and TTR dataset normalization blocked as above.
Model gate passed: not assessed. No training, scale collection, Office or promotion.

## Resume

1. TTR owns header geometry/exclusion repair and exported resolved-scene metadata;
   current source evidence allows targeted fixes without another exploratory capture.
2. NUA replays corrected contract through existing validators; never fake callback
   frame IDs from image observation IDs. Preserve numeric dates without producer rewrite.
3. After changed geometry evidence, resume the pilot under a reviewed missing-group
   plan and explicit completion accounting. Existing partial run stays immutable;
   current runner has no qualified partial-to-complete promotion route.
4. Full pilot baseline, quota corpus and candidate training remain downstream. The
   immediate training hypothesis is suppression of unfocused-button false positives,
   tested across themes/control styles, not more same-style epochs.

No authorized capture can safely continue past this concrete coordinate mismatch;
no full-corpus or model gate is lowered to call the pilot complete.
