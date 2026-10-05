# IOS170 — complete for review; no active process

Supersedes historical checkpoints below: training and corrected matched evaluation
finished exit0. See [handoff](handoff.md). New artifacts in
`attempt02/artifacts/matched-positive-area-v1/`; all2496records/armvalidate.
No promotion: left-position goal still0/48 and class regressions. Do not relaunch
training or infer into any existing destination. Next source-backed coverage tranche
requires frozen new membership/labels; native24 still awaits source compatibility.

Driver91179 terminal exit0; elapsed11412.904 seconds. Fixed-last checkpoint SHA256
3ab45129317e988626c6581196701b074c3d4c72dfd8c5fbd923096e81f50be4.
Epoch5 P.91735,R.83682,mAP50.88196,mAP50:95.84610; cumulative11258.40seconds.
Evaluation session63128 terminated exit1 at report validation after both exports.
combined-predictions.json:1426ok/974failed;page-predictions.json:96ok.
Preserve these outputs; no evaluation.json exists. Logs `.build/translation170-infer.log`
and `.build/translation170-report.log`. Do not rerun infer into these destinations.

Diagnostic session78750 terminal0, `.build/translation170-coordinate-diagnostic.log`:
img_002003 native output shape2556x1179 agrees with manifest; detections10/13/14/15
are class14 low-confidence zero-width boxes x1=x2=0 after resident Ultralytics clipping.
They fail the strict positive-area artifact condition, not an actual out-of-bounds
coordinate. Next: inspect production/evaluation handling of degenerate post-clipping
boxes; implement a source-backed explicit policy with rejection accounting and tests,
then apply compatible settings to candidate and control. Never drop failed images,
overwrite first exports, weaken geometry admission, or claim complete comparison.
Training itself needs no retry. Prior live observations below are historical.

Epoch4 validation completed: cumulative8989.45 seconds (epoch increment2402.35),
P.91558,R.84127,mAP50.88137,mAP50:95.84340. Epoch5 confirmed live in driver91179,
batch16/1818 with finite losses. Do not start terminal evaluation before completion.

Epoch3 validation completed: cumulative6587.10 seconds (epoch increment2216.41),
P.92886,R.82601,mAP50.88068,mAP50:95.84371. Epoch4 confirmed live in driver91179,
batch22/1818 with finite losses. Fixed five-epoch scope and terminal evaluation unchanged.

Epoch2 validation completed: cumulative4370.69seconds (epoch increment2125.03),
P.90750,R.84077,mAP50.88100,mAP50:95.84240. Epoch3 confirmed live,driver91179.
No terminal comparison or per-position efficacy claim; fixed five-epoch run continues.

Epoch1 plus2800-image validation completed:2245.66seconds, P.90256,R.84896,
mAP50.88123,mAP50:95.84397. Epoch2 confirmed live in driver91179. These are
Ultralytics validation metrics, not the custom retained/probe comparison or
evidence of recovered left-position detections. No change to five-epoch scope.

Latest verified observation: driver91179 remains live; epoch1 batch204/1818,
finite losses,5.63GBMPS. Consumer-only hardening requires full epoch metric fields,
matches evaluation references to frozen protocol, and checks control predictions
against actual pinned checkpoint bytes rather than a self-declared hash. All96
retained page results and13strata reproduce exactly.21focused tests plus fresh
offline Swift build/tests pass (`.build/translation170-audit-*`). Training driver,
trainer, launch pins and inputs untouched. No epoch-completion or quality claim.

Run018 PID4888 under exec91179; initial epoch1 updates finite,5.59GBMPS. Poll this
handle rather than restart. Fixed fiveepochs with no wall-time cap.
Exact19740membership verified (14540train,2800val,2400test), prior017control reused.
Protocol [attempt02](attempt02/artifacts/protocol.json) hash
901ca62950dab1058170c8f9c0ac7c44dbf529837e31d7cab054a346da74a511.

Only actual saved-args differences versus017: translate0→.35, name,save_dir.
Resident RandomPerspective tests verify pixel/box motion, partial clipping,
fully clipped target removal and two-axis parameter range. This is intentionally
not native re-layout or unchanged full-frame content. No evaluation roles changed.

First preflight failed before child launch due source-hash Path handling; preserved
`.build/translation170-driver.log` and empty original artifact destination. Corrected
attempt02 fully reverified inputs and launched fresh018, not a training retry.

Terminal sequence: verify completion.json exit0 and checkpoint, then run
`scripts/eval_translation170.py infer` followed by `report` with resident interpreter
and host MPS authority. Evaluator rejects incomplete epochs, altered config,
wrong checkpoints, changed frozen references and output collisions. Reports all2400
retained and96page cases, plus page family/theme/renderer/position/count/seed strata.
No automatic extension or promotion; reject failures with evidence.

Software tests/build verified; actual training integration observed; model outcomes
pending. Original corpora/control/shipped models preserved. TTR native24 remains
source-blocked locally, no repeated status publication needed for this iOS work.
