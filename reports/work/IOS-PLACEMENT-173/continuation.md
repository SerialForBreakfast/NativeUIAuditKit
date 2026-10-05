# IOS-PLACEMENT-173 — complete; candidate not accepted

Terminal update: training51642, inference43363 and reporting53559 all exited0.
All2496evaluation records validate. Left/native hits remain0/48each and combined
AP50regresses .887166→.882978: development acceptance failed. No promotion or
extra epochs. See [final handoff](handoff.md); IOS-DIAG-174 is the next scoped task.
The launch/continuation notes below are retained as historical execution evidence,
not commands to rerun completed work.

Run019 PID20948 / exec51642 exited0, confirmed from the execution handle.
Elapsed11455.514seconds; completion seal
c932855a83a5e9c6a133b99c7ecbcaee56dbdc9240bedd9ce5d7e457b48caf50.
Fixed last.pt SHA256ecfb0195250e65d9bbbc0954e9e1714af60685d5e1123d5dd0e0784dcdadb378.
Matched evaluation `eval_placement173.py infer` launched in the approved MPS context,
exec43363 subsequently exited0. Do not relaunch training or collide with evaluation outputs.

## Verified before launch

-172sealed admission includes264unique new training rows and excludes24reused controls.
- Existing exporter generated/validated full YOLO labels. Staged20004members:
  14804train/2800val/2400test; every image/annotation/label verified during preparation,
  staged image/label bytes and resolution checked again at launch.
- Fresh Run013best and fixed-last selection; same5epochs/full-frame settings as017.
  Actual saved args differ only data/name/save_dir; no translation treatment.
- Protocol SHA256d85f6226ae52926eaae605ade453eff6b012169e9d534d14c2e398ee5ae80b11.
- MPS verified available in launch context;40.3GiBfree at initial check;2GiBoutput
  budget and standing no-wall-time-limit authority. No capture, downloads or promotion.
-13focused tests pass (`.build/placement173-tests.log`); offline Swift build/test
  exit0 (`.build/placement173-{build,swift-tests}.log`). Preparation driver57257exit0.

Evaluation wrapper refinement while training:14focused tests now pass, including
actual infer-entrypoint success/failure orchestration with deterministic fakes.
Separate combined/page export timing includes validation/model loading and is
explicitly not model-only or comparable to absent control timing. Failed export
cannot create a successful timing receipt. Training driver/trainer sources untouched.
First epoch completed in2227.42seconds (37.12minutes): validation precision0.88059,
recall0.80006, mAP50=0.83893, mAP50-95=0.81204. Source: run results.csv epoch1.
These are trainer validation metrics, not the matched retained-test/custom-AP report.
Epoch2 completed at4514.35seconds cumulative (38.12minutes for this epoch):
validation precision0.89188, recall0.79912, mAP50=0.83927, mAP50-95=0.82058.
Epoch3 completed at6799.78seconds cumulative (38.09minutes for this epoch):
validation precision0.91891, recall0.82546, mAP50=0.85926, mAP50-95=0.82783.
Epoch4 completed at9063.99seconds cumulative (37.74minutes for this epoch):
validation precision0.89893, recall0.80468, mAP50=0.84508, mAP50-95=0.82591.
Epoch5 completed at11284.6seconds cumulative (37.01minutes for this epoch):
validation precision0.92151, recall0.82122, mAP50=0.86622, mAP50-95=0.83498.
All five epochs completed without restart or configuration change. No model gate is established.

Training artifacts: `artifacts/{protocol,membership,execution}.json`,training.log;
weights/output: `NativeUITrainer/yolo_runs/placement173-r019/` from repo root.
Keep scripts/placement173.py and scripts/train_ios_model.py unchanged during the
registered run; their source hashes are pinned. completion.json is written only
after terminal child execution. A transient poll timeout is not terminal.

## Exact continuation

1. Poll evaluation exec43363; preserve its outputs on failure. Training is terminal0.
2. `infer` verifies sealed completion, five finite epoch records, exact saved arguments
   and fixed `last.pt`; do not select best post hoc.
3. After infer exits0 run:
   `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts .venv-yolo/bin/python scripts/eval_placement173.py report`.
   This reuses existing score/export machinery,
   positive-area rejection audit and017control predictions; no repeated control inference.
4. Report all2400retained images and96development probes, class/stratum AP, hits,
   false positives, missing/low-confidence candidates. Development success requires
   increased left/native hits without cancelAction/mapView FP growth or aggregate
   AP50loss. Any failed criterion yields diagnosis, not automatic more epochs.
5. Update ExperimentLog, Tasks, CurrentState and one final handoff. Do not claim
   independent qualification or DS-G8; coverage and exposed-probe restrictions remain.

Software checks passed; data admitted; training/evaluation complete;
development model acceptance failed; production gates not established.
TTR remains separately source-blocked: fresh local HEAD46dce7b; exact peer source
b98402df1825e30f2cdd151aeaeeed3267a51c1c is absent (`git cat-file -t` failed).
No unchanged SMB publication; local iOS work is not cross-project status noise.
