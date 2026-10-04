# PROPOSALS-73 — candidate geometry exists; focus ranking remains unsolved

Source-bound audit of five exposed Settings pairs/nine unique images, using unchanged
admitted corpus, retained native Vision results and frozen DTM013/014/015 predictions.
No model launch, OCR/rectangle rerun, capture, labeling or role change.

Saved annotation proposal lists:8endpoint appearances empty,2missing. Those lists
do not establish detector failure. Retained native-ocr.json also includes independent
Vision rectangle detections:19–24rectangles/image, focus-box recall10/10 atIoU0.5,
bestIoU0.851–0.939. This measures candidate recall only, not focus decisions or overall
object precision. The repeated image is not an independent observation.

Human box oracle-pool snapping of frozen predicted geometry:
- DTM013 nearest-center3/10endpoints,1/5pairs; maximum-IoU2/10,1/5pairs.
- DTM014 and DTM015 both0/10endpoints and0/5pairs for either rule.
Automatic Vision pool endpoint selection: DTM013 center1/10,IoU2/10;
DTM0140/10both; DTM015center0/10,IoU1/10. Raw paired geometry remains0/5.
Invalid predictions remain unavailable; no truth-based choice or clipped repair.

Implication: candidate geometry is a plausible input for a new visual ranking
formulation on these cases. Snapping bad coordinates is not that formulation and
has not solved focus. No independent generalization or model gate passes.

Actual script: diagnose_proposals73.py --output reports/work/PROPOSALS-73/final.json,
exit0. Initial annotation-only and retained-Vision intermediate reports preserved.
Final report pins corpus, semantics, native raw source, models and retained comparison;
image hashes/dimensions and approved focus boxes are independently checked.
Only geometry/IDs enter selection; focus truth used after selection to score.

10focused Python tests pass (selection, label rejection, ties, source/dimension/error
binding, invalid bounds/confidence, empty pools, existing evaluation regressions).
Offline Swift build/test pass14XCTest+120SwiftTesting. git diff --check passes.
Logs .build/proposals73-*. No new SMB consequence requiring publication.

Software verified; data roles unchanged; offline retained-artifact integration verified;
model gates not passed. Next PROPOSAL-RANK-74: training-side automatic candidate coverage
and separate actual/oracle banks, source-bound ranker contract and bounded experiment
decision. Genuine stationary capture remains a parallel producer-dependent lane.
