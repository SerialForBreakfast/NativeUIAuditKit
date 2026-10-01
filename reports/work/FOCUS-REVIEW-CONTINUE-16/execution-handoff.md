# FDR-021 — development improvement, eligible experimental checkpoint

2026-09-30. Approved admission→encoding→training→comparison completed, no retry.

| Fixed0.85development measure | FDR020 terminal | FDR021 selected775 |
|---|---:|---:|
|Focused controls detected|14/27|16/27|
|False positives|3/288|3/288|
|Unique-correct complete frames|9/14|12/14|
|Complete frames with no focus|4|2|
|Complete frames with multiple focus|1|0|
|Retention classifications|18/18|18/18|
|Buttons positive hits / false positives|3/3;1|3/3;0|
|Tabs positive hits / false positives|2/3;0|2/3;0|
|Artwork positive hits / false positives|1/12;2|2/12;3|
|Rows positive hits / false positives|6/7;0|7/7;0|
|Other positive hits / false positives|2/2;0|2/2;0|

18incomplete frames remain unavailable for unique-selection accuracy. Comparison
uses exact unchanged315development+18retention controls and same metric code.
FDR020had no eligible selected checkpoint, so its retained terminal predictions
are explicitly the baseline. FDR021terminal1000has the same headline counts as775;
selection775is minimum eligible development loss under unchanged rules, not cherry-
picking a visually appealing example. Full strata/errors in comparison-selected.json.

## What changed and what did not

58approved control crops added to928training samples, yielding986(790native,
196human).21text/decorative crops remain annotated but excluded. Four positive
additions include the first focused human button in this subset. Whole-session
training reservation verified; no independent-source claim. Human20%loss is now
distributed over12frames rather than8; native80%unchanged. This changes data and
within-human weighting together, so cannot isolate a causal explanation.

Frozen ImageNet MobileNetV3-small encoder unchanged;58new features encoded on MPS.
Original928train and333evaluation features reused. Fresh577parameter linear head,
seed42; identical initial evaluation predictions verified against FDR020. No change
to cropper, thresholds, final-challenge membership or shipped artifacts.

## Wins and regressions

Photos all-iCloud unfocused score0.983845→0.766655 removes its positive decision,
but remains in the uncertain band; do not call it a confidently solved negative.
Gains include Settings, Home grid and App Store search-results focused controls.
App Store featured positive regresses0.889582→0.383987. A now-streaming unfocused
card rises0.405707→0.984190, becoming a new false positive.10/12artwork positives
are still missed; home/top-shelf transfer remains weak. Tab hit counts are unchanged,
but an already-missed focused tab falls0.623998→0.186749. All errors preserved.

Predeclared development objective met: artwork>1/12, overallFP≤3, retention18/18.
That is not production qualification. Training-fit criterion did not pass; loop
stopped at1000updates rather than five consecutive confident-fit observations.

## Receipts and verification

- Encoding PID94705:5.683s external, exit0, no timeout.
- Training PID94800:21.115s external/17.701s model, exit0, no timeout.
- Selected head: NativeUITrainer/focus_ring_runs/fdr021-reviewed-contrast/weights/best.pt;
  epoch775,4813bytes, SHA256bc1b5978f1febbf86ba57ae51d13c8f0fb68ffa4107e303f2f6ccf57fb0c2ec8.
  This is a linear-head checkpoint, NOT a standalone deployable detector; it requires
  the pinned encoder and preprocessing. No CoreML export was performed.
- Final protocol SHA2561140910f741a048cefe155b4146087c6f5831ff55860c514416367e773097543.
- Replay checked every986986training and13653evaluation predictions, every recorded
  evaluation metric, selection eligibility/minimum loss, checkpoint presence and
  original input/runtime hashes. Both runs rescored without model loading.
-15focused tests pass; offline Swift build and109Swift Testing tests pass.
  Existing broader73test evidence remains applicable to unchanged implementation.

Software: verified. Data:58admitted for this bounded development experiment, no
independent-test claim. Integration: local encoding/trainer/metric chain verified;
TTR/CoreML runtime not tested. Model: development candidate eligible, release gates
open; no export or promotion. Coordination: no TTR runtime/model-delivery action
assigned or changed, so local results only. No shared publication attempted.

## Recommended next tranche

Freeze and preserve selected775. Separately approve export feasibility and PyTorch/
CoreML parity of the **whole pinned encoder+head**, then observer-only TTR testing
if that passes. In parallel prepare targeted artwork/top-shelf contrast collection
from training sources; never train on these development failures. Do not repeat
this unchanged run or lower the threshold. Release requires representative coverage
and physical transfer evidence beyond this development set.
