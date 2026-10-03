# Control eligibility39 — local tranche completed for review

| Outcome | Result |
|---|---|
| Software verified | 35 Python tests; offline Swift build and134Swift tests; two modified iOS templates parse successfully |
| Data eligible | Native26 originals and all full-scene labels verified; full-screen admission draft remains unapproved |
| Integration qualified | Offline replay/preparation works; new iOS rendered boxes and USB training loader remain to qualify |
| Model gate | Unchanged; no new model fit or promotion |

## Concrete iOS defect found and source repaired

MediaCardGrid and ProgressActivity captured `pageControl_0` **after**
`.frame(maxWidth: .infinity)`. Their666training labels describe the whole row,
although the image shows a small centered dot group. Evaluation captures the
intrinsic group. Both source templates now fix the intrinsic size and capture
before applying outer alignment. Old screenshots/labels are preserved.

Verified label audit:

| Split/family | Frames | Median box aspect ratio |
|---|---:|---:|
| Train/MediaCardGrid |266|39.30|
| Train/ProgressActivity |400|38.40|
| Train/KitchenSink |200|14.04|
| Train/UIKitControls |700|12.92|
| Test/GalleryPage |200|5.50|
| Test/OnboardingPage |400|5.50|

There are **zero validation pageControl examples**. No training family has the
tight4–7aspect convention used by evaluation. The900native/container examples have
a separate geometry convention; source repair addresses the666manual-dot examples,
not a silent reinterpretation of native UIPageControl bounds.

All666affected image hashes verified and a seed/ID-preserving
[regeneration plan](pages/regeneration-plan.json) prepared. Visual inspection of
img_007101 and img_009481 confirms centered dot groups rather than whole-row bodies.
At640 the best available page prediction has median width3.34times truth; higher
resolution changes box geometry/confidence but does not repair training targets.
This explains a concrete supervision mismatch; improved model accuracy still needs
corrected rendering and a matched training comparison. [Audit](pages/audit.json).

Source-order regression tests and Swift parsing pass. These do not substitute for
fresh iOS rendering. Resume rendered qualification with a scoped local iOS generator
run across page counts/device sizes before replacing any training corpus version.

## Conservative proposal filtering

Frozen rule uses predicted focusable YOLO anchors, not reviewed truth: new boxes
needIoU≥.50 with an anchor and cannot enclose two disjoint anchor centers. Original
eligible bodies remain. No threshold tuning or inference.

| Method | Candidates | Focused bodies covered /46 | Complete-screen result /7 |
|---|---:|---:|---|
| All geometry |2,289|42|6wrong,1tie|
| Preserve known YOLO role exclusions |1,620|42|2correct,5wrong|
| Supported whole-control refinement |594|19|4correct,3target missing|

Refinement restores the production4/7result but does not improve it. It cannot
discover a target YOLO never anchors. Reject blanket union; keep whole-control
localization the priority. [Replay](proposals/result.json).
The46screens span7acquisition directories, but all are exposed development evidence;
all7complete screens share one Settings batch. **No untouched evaluation set can be
created by relabeling those directories.**

## Full-screen synthetic corpus prepared

Revalidated1,250native26pairs through the existing harvest/observed-focus/measured-body
validator. Exported2,500full-scene annotations containing7,500controls and2,500focused
targets, preserving2,000train/500evaluation frames and10configuration groups.
No decoded duplicate frames or cross-split pixel collisions. Before frames correctly
label the focused competitor, not an invented all-unfocused scene.

Original image bytes:13,866,999,437 (~13.87GB); validation270.73seconds. USB originals
remain in place. Bound all1,250metadata files and2,500image hashes to original
verified transfer receipts. [Data readiness](fullscreen/readiness.json),
[exact membership draft](fullscreen/draft.json), [run draft](fullscreen/run-draft.json).

Execution prerequisites are concrete:

1. Bind approval to the expanded full-screen membership; prior execution used only
   nominated target crops. Actual runner rejects the draft with `membership_not_admitted`.
2. Add a tested USB read-through loader; current runner only accepts project-local
   copied images. Copying13.87GB would exceed the2GiBoutput envelope.
3. Preserve the evaluation role and evaluate only after fitting. Current runner
   accepts train/development; do not silently map evaluation into per-epoch validation.

These are consumer-side tasks, independent of the TTR update. Shared renderer and
already-exposed synthetic evaluation remain limitations, not real-app independence.

## Verification and next substantial tranche

13new Python checks +13runner +9replay tests passed. Offline package build and
14XCTest+120Swift Testing tests passed. Template syntax parsing and diff checks pass.
No active processes remain. TTR coordination deferred by maintainer.

Recommended priority: implement USB read-through plus terminal-only evaluation and
qualify full-screen execution against this exact draft; in parallel, render/QA the
corrected iOS dot groups into a new corpus version and close validation coverage.
Then run matched bounded comparisons using the approved memberships/budgets. This
targets supervision/input failures rather than another unchanged classifier run.
