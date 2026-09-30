# VISION-ANNOTATION-COMPARE-01

Authorized: “Lets do a test with vision and compare the results”. Current NUIAK
worker; local offline diagnostic on all8reviewed batch03 development frames from
revision20260929T042837Z-d83e7466. Freeze revision, original image hashes, source
implementations, runtime and request settings before running. No annotation edits,
new capture, training, deployment or TTR code changes.

Compare current human_auto_boxes.detect unchanged (640longest-edge internal raster,
40max proposals) with VNDetectRectanglesRequest on original PNGs, orientation up:
minimumSize0.01, minimumAspectRatio0.05, maximumAspectRatio1, minimumConfidence0.5,
quadratureTolerance15degrees, maximumObservations40, current revision recorded.
One fixed configuration, no tuning/sweep. Convert Vision normalized bottom-left
boxes to original top-left pixel xywh exactly once. Run accurate en-US Vision OCR,
language correction off, as separate text evidence—not whole-control proposals.

Measure one-to-one maximum-cardinality geometry matches at IoU0.50 and0.75,
using existing perception_benchmark._iou. These are descriptive comparison cutoffs,
not new qualification gates. Count unmatched proposals, missed reviewed boxes and
per-frame latency separately; no claim of measured annotation-time savings. Unknown
annotation completeness means unmatched proposals are not automatically false positives.
OCR text has no text ground truth here, so report observations/overlays, not OCR accuracy.
Record cold-first request and sequential request timings, excluding process launch.

Deliver exact inputs/results, paired overlays and concrete recommendation, with
focused conversion/matching/accounting tests and required offline Swift build/test.
No automatic replacement of the annotator engine. Shared coordination applicable
only if a finding changes a current producer request.

Observed raw Vision result:1rectangle crosses the image boundary. Preserve it in
raw output and explicit rejected-proposal accounting; do not clamp it into a new
control label. Report valid-proposal metrics plus rejected count. Native execution
completed all8frames without errors; report generation reuses that exact output,
checking source/binary/config/input compatibility rather than repeating inference.

Completed:78reviewed controls across8frames (not88). Vision44matches versus32
heuristic atIoU0.5;33versus23atIoU0.75. Three unit tests, actual asymmetric-image
coordinate check (IoU0.9566), changed-hash rejection and123Swift tests pass.
See reports/work/VISION-ANNOTATION-COMPARE-01/handoff.md for limitations and decision.
