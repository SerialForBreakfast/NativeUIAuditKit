# Vision annotation comparison

Completed 2026-09-29 local time. Recommendation: retain the current helper and
trial Vision as an optional, filtered proposal source—not a direct replacement
or immediate TTR port. Neither engine identifies focus or semantic classes.

## Fixed development trial

Eight already-reviewed batch03 screenshots,78 reviewed controls; unchanged
heuristic versus native Vision rectangles. No settings sweep or annotation edits.
The frozen revision explicitly has completeFrameCandidates=false: unmatched
proposals are NOT automatically false positives. These are related development
screens, not independent qualification evidence.

| Measurement | Current raster helper | Vision rectangles |
|---|---:|---:|
| Valid proposals |65|244|
| Matched reviewed controls, IoU≥0.50 |32/78 (41.0%)|44/78 (56.4%)|
| Matched reviewed controls, IoU≥0.75 |23/78 (29.5%)|33/78 (42.3%)|
| Unmatched proposals, IoU≥0.50 |33|200|
| Median measured processing time/frame |128ms|25ms|

Vision emitted245raw rectangles; one outside recorded-751's image bounds was
rejected explicitly, not clamped. All8native requests completed without errors.
Vision hit the40proposal limit on2frames. OCR separately returned235text regions,
median86ms; text accuracy was not measured. First-frame rectangle/OCR times were
48/159ms. Times are sequential single-pass observations, not a controlled throughput
benchmark: original-resolution Vision versus internally downscaled raster helper,
with process startup/image decode excluded from native request timing.

## Per-screen matches at IoU0.50

| Frame / screen | Reviewed | Raster | Vision |
|---|---:|---:|---:|
|306 Settings|11|0|4|
|536 Home/top shelf|7|7|7|
|724 Featured|13|2|3|
|751 Now streaming|10|9|9|
|858 Categories/top free|12|3|8|
|1043 Search|13|3|5|
|1087 Search cards|6|4|4|
|1105 Search cards|6|4|4|

Reviewer observations from all eight comparison sheets: Vision can recover
individual Settings/category rows where the heuristic merges rows into a container.
Both struggle with artwork plus caption as one control. Vision frequently boxes
logos, text and internal artwork separately. Home coverage ties, with more Vision
clutter. OCR on search groups most letters into one line; it does not supply
individual keyboard key hit regions. No causal or production-accuracy claim.

## Evidence and reproducibility

- [Frozen protocol](comparison/protocol.json): image/revision/snapshot/source/binary
  hashes, fixed request settings, membership and cache provenance.
- [Comparison JSON](comparison/comparison.json): every frame, proposals, rejected
  coordinates, matching assignments, counts and timings.
- [Raw native output](comparison/vision.stdout): runtime macOS26.4.1/build25E253,
  request revisions, confidence, text and geometry.
- [Settings comparison](comparison/recorded-306-comparison.png),
  [Home comparison](comparison/recorded-536-comparison.png),
  [artwork comparison](comparison/recorded-724-comparison.png),
  [search comparison](comparison/recorded-1043-comparison.png),
  [search OCR](comparison/recorded-1043-ocr.png).
- All source input hashes preserved. Initial reporting stopped on invalid geometry;
  final reporting reuses that completed native output after compatibility checks.
  No repeat native inference on the development screenshots.

Reproduce with scripts/compare_annotation_proposals.py --revision <frozen revision>
--output <fresh project-local directory> --tool .build/debug-output/vision-annotation/probe
--reuse-run reports/work/VISION-ANNOTATION-COMPARE-01/run-01.
Build the probe from scripts/vision_annotation_probe.swift with a project-local
module cache; protocol hashes prevent mixing changed native implementations.

## Verification / outcomes

- Software:3focused matching/bounds tests pass; offline swift build passes without
  warnings, swift test passes14XCTest+109SwiftTesting tests. Native asymmetric
  rectangle integration check IoU0.9566 confirms orientation/scale conversion;
  changed image hash rejected. See tests.log, build.log, swift-test.log and native-check/.
- Data:8/8frames accounted for;78reviewed boxes,1rejected native proposal;
  original annotations and pixels unchanged. No data admission.
- Integration:standalone native probe and reporting CLI exercised end to end.
  No editor-engine swap, public API change or TTR implementation.
- Model gate:unassessed; no training, trained-model inference, export or promotion.
- Coordination:not applicable; local comparison creates no producer action or
  protocol change. No shared status published.

## Next assignment

Prototype optional Vision proposal filtering/ranking in the existing preview,
retaining raw provenance and manual selection. Evaluate retained reviewed-box
coverage alongside actual accept/edit/delete counts and annotation time on a small
approved development batch before changing the default. Keep OCR as separate text
assistance; do not substitute glyph boxes for whole-control bounds. Only after
measurable operator benefit should shared Swift/TTR integration be proposed.
