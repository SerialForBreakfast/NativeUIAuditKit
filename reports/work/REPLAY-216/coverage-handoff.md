# Full-frame coverage and worker lineage — October6

Previous turn made model-decision progress. This tranche adds an independent
whole-model coverage proposal and resolves Big Dog's concrete reporting dependency.

## Existing full-frame data, not more capture

The1509ROI replay pool has zero positives for scrollIndicator, sheet, cancelAction
and mapView. Its page-donor experiment cannot establish whole-model improvement
on those classes. Audited labels from14804training members of sealed173; no val/test
examples selected. Deterministic rare-class-first selection uses only training
labels and stable ID hashes, at most one frame/original group, cap512.

189frames suffice for>=16supporting groups for all40represented categories.
`webContent` has no training support and remains unavailable. Existing source support:

| Class | Training images | Original groups | Selected groups |
|---|---:|---:|---:|
| cancelAction |2260|2130|60|
| mapView |1100|1100|16|
| scrollIndicator |700|700|24|
| sheet |569|569|16|

All selected original image/annotation/label hashes verified. Selected decoded RGB
digests with dimension prefix match sealed identities; zero selected duplicates or
reserved-pixel/group overlap. The remaining pool's images were not redecoded; their
existing admission evidence is reused, while every training label hash was checked.
No new role admission, copies, capture, training or deployment decision.
`artifacts/fullframe-pool02.json` SHA
`4f9d0cd0eb448f7b6f564185b5857c36c648536a742642c67aff09afa05face0`.
Initial missing-family assumption was corrected without inventing metadata: selection
uses original group and label coverage; full source rows retain original fields.
Earlier pool01 remains a preliminary report;02adds explicit decoded-pixel binding.

## Big Dog request resolved

Receipt01matches exact216archive,512resident/997supplement/96native inputs and
reports8tests. Start reports14:15:20UTC,PID164961,RTX2070SUPER. Correction01 binds
`nuiak-20261006-worker216-replay` without restart, unchanged source/data/config.
These are peer reports, not independently inspected process handles.

Worker asked for evaluation lineage, not new data. Actual exporter verified frozen
ROI manifests/content hashes against135fit/37page/413combined mapping records,
original-frame hashes and crop-window dimensions. All585parent/window mappings
available.548higher groups bind by identical image hash to sealed173;37page cases
are outside that corpus, so higher group is explicitly null/unavailable.
Do not infer unseen-family independence from parent identity alone.

SMB `nuiak/worker216-evaluation-lineage02.json`:425895bytes,
SHA `87fc95bd82954ebd3848ef9b4b909c47689d16f79a45207e81a471b4be0fb37a`.
Response `nuiak/responses/nuiak-20261006-worker216-lineage-response.json`:2032bytes,
SHA `8e001efc0f231e436a872e19c7bd7d5ed0da2b26daf00afb8cbe38618eff453f`.
Both copied/readback-verified; exact receiver receipt pending. No cleanup or peer
acknowledgment inferred. No training contract change or extra run requested.

## Checks and next

Actual fullframe_replay_audit and export_lineage216 CLIs exit0.10focused tests pass
(selection determinism, unique groups/caps/gaps, invalid windows, output collisions,
existing216input guards). Offline build/test logs `.build/replay216-coverage-*`.
Software/data-proposal checks pass; worker integration is publication verified,
receipt/result acceptance pending. Model gates not assessed by these preparations.
Next: accept031/032 and compare raw and composed retention; then define one bounded
whole-model replay experiment with this189-frame proposal if evidence supports it.
Qualified native tvOS focus inputs retain priority when available.

## Native-label consistency and fixed baseline

Verified189annotation schemas/image-hash bindings and exact source-to-YOLO label
conversion with the existing exporter checker. Existing load_request additionally
decodes pixels, validates labels and freezes189identities. No annotation edits.
Initial preparation used absolute manifest paths, rejected before inference; retained
baseline01evidence. Baseline02uses relative references to new owned staging links to
verified existing input files, not a dataset migration or replacement of original paths.

Run022existing exporter/MPS/640 completed in13.142491seconds,exit0. Pre/post input
and checkpoint checks passed; all189results accepted. No training or threshold tuning.
Report `artifacts/fullframe-baseline02/report.json` SHA
`9e6d592891ad6fabab38c969447248d1db1be5df110d3577780f98ddf0f175ca`.

| Class | TP/support | FP |
|---|---:|---:|
| scrollIndicator |3/24|3|
| cancelAction |56/60|2|
| sheet |16/16|1|
| mapView |16/16|0|
| pageControl |17/19|0|
| imageView |102/102|0|

These are in-sample training diagnostics. Strong fit does not resolve retained gates.
Scroll minimum-side after640letterbox ranges2.2536–6.7168pixels (median5.2583).
12targets have same-class IoU>=.5 candidates at export floor;9are below0.25confidence.
This suggests testing resolution, not assuming all misses arise from one cause or
lowering production thresholds. Next bounded local work: compare the same24training
source frames at1280with unchanged checkpoint and scoring; no final-evaluation tuning.

Restricted preflight reported MPS unavailable before launching a child. Scoped host
Metal access succeeded with resident dependencies and project-local outputs.6focused
tests pass including timeout/no retry and output collisions; offline build and
140Swift Testing+14XCTest pass (`.build/fullframe-replay-*`).

Big Dog lineage-receipt01 at14:22:43UTC verifies exact425895bytes/hash plus585rows,
retains null page groups and confirms use in the original pair's report. No new GPU
job requested. Shared metadata retained; sender cleanup not claimed.216terminal and
independent source/config/model acceptance are still pending.

## Resolution diagnostic and worker feedback

Completed the preregistered24-frame1280 comparison in5.087081seconds, exit0.
At identical checkpoint and operating thresholds,640 yields3TP/3FP/21FN and
1280 yields0TP/0FP/24FN. AP50 .326656→0. Reject blanket inference upscaling;
resolution-aware training remains untested. This is training-fit diagnosis only.
Report: artifacts/scroll-resolution01/report.json, SHA
a14f1dc7858b8e69bd649ae4bafc2decb43bb74a0210aa4a2470673c6d21ce08.
19focused tests pass. Offline Swift build,140Swift Testing and14XCTest pass;
logs `.build/scroll-resolution-build.log` and `.build/scroll-resolution-swift-tests.log`.
`git diff --check` passes. No Git writes.

Big Dog reports6control epochs at14:27:22UTC and integrated lineage. No restart,
additional job or contract change requested. Its acceptance receipt has correct
archive identity but not the required cleanup state/verified fields. Preserve the
shared archive until a matching standard receipt arrives; local original retained.
Receipt-format request published/read back at
`nuiak/responses/nuiak-20261006-worker216-receipt-request.json`,1145bytes,
SHA0cda42288be691f80e03586b2ea9952cc13ada8bb6be1256efc048c2cbc1d4d8.
Peer acknowledgment pending. Initial helper call omitted required transaction keys
and failed before mutation; complete metadata publication then verified successfully.
Next substantial tranche: independently verify031/032 returns and compare native
gains, per-class retention, size strata and composed consumer behavior; then choose
one evidence-backed full-frame replay candidate, not an arbitrary resolution sweep.

### Case-level follow-through

Reused both prediction artifacts; no inference, capture, threshold tuning or training.
Reconciled independent greedy associations to the existing scorer at both resolutions.
At640, twelve of24targets have no same-class IoU>=0.5 proposal at the retained
export floor; nine have a geometric match below operating confidence; three pass.
At1280, all24lack a matching same-class proposal even at the export floor. Neither
resolution has an alternative-class box overlapping these targets at IoU>=0.5.
Thus confidence alone cannot explain all misses, and lowering the operating threshold
cannot recover1280 misses from these artifacts. Absence below the export floor is
unknown; this is not evidence of internal activation absence or incorrect labels.
Case report `artifacts/scroll-resolution01/case-diagnosis01.json`, SHA
de8cc558b25acb8c95f7c1efacfd6202ee85fc1a5111c94dcebbbd6e9ec836e1.
Next candidate decision should separate training coverage/scale exposure from
confidence calibration, retaining the original full-frame geometry and independent
evaluation. Do not request more artwork to fix a failure not shown to be artwork-related.

Peer recheck:216progress01 and TTR geometry-journey checkpoint remain unchanged;
no terminal results or new qualified focus pairs. This is not a verified live-process
wait. Focus205/206 admission remains blocked specifically by native label/geometry
qualification, not by CUDA capacity. Existing peer requests remain in place.

### Return acceptance prepared

Extended `scripts/review_worker213.py` rather than adding a second reviewer. Explicit
`--profile216` (CLI spelling: `--profile 216`) pins the reported wrapper/trainer,
031/032 identities,1569slots,393batches/epoch and continuous16-batch accumulation.
The partial final minibatch remains counted. Ten epochs yield245updates; resetting
accumulation each epoch would be rejected. Exact ten arm/partition cells, checkpoint
hashes and reported prediction hashes remain required; scoring is separate and uses
the unchanged `evaluate_artwork213.py pair --native-layout split` entrypoint.

Positive/negative synthetic216 entrypoint tests pass, including changed source,
output collision, missing epochs, dropped last minibatch, reset accumulation,
reordered slots, nonfinite losses and duplicate evaluation cells. Retained actual213
return re-reviewed through the generalized entrypoint; checkpoint hashes/counts agree
with its accepted record (`artifacts/retained213-training-review02.json`). No returned
code or checkpoint is executed by this review. Byte pins prove identity, not source
semantics;216 implementation must still be inspected on arrival.

Worker control-terminal01 at14:36:23UTC reports1179.433seconds,3930batches and245updates,
checkpoint da414f856ad1ef017d41c24a64ac250104cef87cc9180e3745eca4ed956905f6.
Treatment remains peer-reported running. No duplicate launch or changed instructions.
Integrated verification:30Python tests, offline Swift build and140Swift Testing+
14XCTest; logs `.build/review216-*`. No model gate or new data admission claimed.
