# IOS-REPAIR-165 — historical execution notes

Superseded by [completed handoff](handoff.md): both runs and evaluations exited0.
No live process remains from this campaign. Everything below records historical
checkpoints, not current execution instructions; do not relaunch either arm.

## Current corrected attempt (supersedes historical details below)

Newest live observation:016completed epoch1 plus2800-image validation and entered
epoch2. CSV row1:2279.06seconds, P.91119/R.83606,mAP50.87628,mAP50:95.83209;
optimizer lr/pg0=.00009989,pg1=.00009989,pg2=.0001. Session71394stilllive.
These validation metrics do not replace terminal fixed-last retained-test evaluation.

Integrated page geometry diagnostics into both candidates' actual report path.
Retained Run013 replay:36/96images with candidates,60missing; median width ratio
4.5316568107661865 at both export and.25operating thresholds. Evidence
`artifacts/run013-page-geometry.json` pins source,manifest,predictions. Best-IoU
selection is explicitly oracle diagnosis, not model selection or an AP replacement.
24focused tests and integrated offline Swift build/serialized host tests pass
(`.build/repair165-geometry-{build,test}.log`, session84349exit0).
Tests include missing/low-confidence/wide-box cases. Training
driver/trainer sources untouched;016observed epoch1/batch231,5.63GBMPS,finite loss.

Evaluation read-through completed while016trained: all frozen reference hashes,
actual manifest loaders and artifact validation pass for2400combined/2000withheld/
400addon plus96page cases. Existing page baseline reproduces AP50=0,48FP/96FN at
the fixed operating point. This reuses predictions, not new inference, and verifies
the reporting path before terminal candidates exist. Session38395 exited0.

Run014 stopped exit-2 before first epoch;015 never launched. Preserve both original
launch evidence and failed output. Corrected Run016prior PID78043 is live in driver
session71394;017repair starts only after successful016 completion. Observed epoch1
batch12/1818, finite losses,5.59GBMPS. Saved args lr0 andwarmup_bias_lr both.0001.
Fresh Run013 initialization, not partial014. No validation metrics yet.
`artifacts/launch-corrected.json` SHA256
2c3ed451cbc69a5a95d834d738b7f8e49e19f4faa4e6c2373ebf4336b2a28d45.
32Python checks pass; Swift build passes. Sandboxed Swift run failed Apple service
access; scoped host serialized rerun exits0 (`.build/repair165-corrected-host-test.log`).
Evaluator now accepts only016/017 and rejects mismatched bias warmup. Continue
polling the existing driver; never restart because an observation times out.
After terminal receipts use eval_repair165.py infer/report for each corrected arm.
No candidate promotion, incomplete comparison until both evaluation reports exist.

## Historical initial attempt (terminal, not running)

Run014prior-r8 PID75555; driver exec session99046. Run015repair waits for successful
Run014terminal return in the same driver. No automatic retry after failure. Process
handle/live process is authoritative; a stale log is not permission to restart.

Frozen `artifacts/launch.json` SHA256
b7b7fdf9a1a42c4450c2054cc04c00c217cd1e7bcdb442dae41caf3b72298fcd.
Explicit full14540train/2800val/2400test per arm; all source bytes verified before
staging and first launch. Both arms fresh Run013best, samefive-epoch profile. Repair
changes900rendered images/labels together; do not claim a labels-only causal result.
Originals/666prior repairs/evaluation untouched; stage uses explicit image/label
symlinks so loader cache writes are local to this experiment.

Startup: real updates epoch1,batch35/1818,finite losses,5.68GBMPS. Saved args.yaml
checked against profile. Rectangular batch display384is compatible with configured
640long-edge input. Loader reports80background images,0corrupt; they are included,
not silently filtered. Execution record and logs under artifacts; driver log
`.build/ios-repair165.log`. Model outputs NativeUITrainer/yolo_runs/repair165-*.

Next: poll same live handle; read results.csv/checkpoint and completion receipt when
terminal. Do not edit pinned trainer/driver while campaign runs. For each completed
arm, eval_repair165.py infer/report reuses existing prediction/AP contracts on2400
retained cases and96page-development cases. Fixed-last only, no threshold tuning.
All model gates pending, no export/promotion. Independent final challenge still open.

Integration: focused tests and fresh offline Swift build/serialized142test suite
passed before launch; final31Python checks include evaluation readiness, retained
artifact compatibility, missing/corrupt inputs and reference comparison failures.
All pass; diff check clean. This qualifies software, not the unfinished candidates.
Terminal acceptance hardened while training stayed untouched: evaluator now rejects
wrong-arm/best-instead-of-last paths, mismatched saved training configuration,
missing/duplicate epochs and nonfinite five-epoch evidence.23focused tests pass;
fresh serialized offline Swift build/142tests pass. Original launch source pins
and active process remain unchanged; this is consumer-only validation.
SMB irrelevant to this local iOS run. Worker163request still lacks acknowledgment;
no peer workload has been presumed started. Goal remains active.
