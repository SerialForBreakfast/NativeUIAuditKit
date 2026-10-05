# IOS-FIT-175 — historical launch checkpoint, superseded

Completed and evaluated2026-10-05; do not poll/restart the historical process or
rerun collision-protected inference. See [handoff](handoff.md). Fit gate failed;
development improved but retained classes regressed. Remaining text is historical.

Run020 PID34431, live exec84525. Do not restart. First training pass completed,
in-sample monitoring began. Fixed20epochs on216eligible training images,72per
placement. Initialization019last with fresh optimizer; no resume. Actual saved
args640/batch8/AdamW1e-4/biaswarmup1e-4/translate0 match the registered experiment.

Protocol seal070979f2194017e6eb5fc8c832728fb6f752def7b5ebc71b27e2ce6ea66a39e2.
Keep `scripts/fit175.py` and `scripts/train_ios_model.py` unchanged while pinned
execution is live. Config intentionally points train and val at the same training
images: trainer validation scores are in-sample diagnostics, never model gates.
Sources, labels, original splits and shipped models remain unchanged.

10focused tests pass (`.build/fit175-tests.log`); offline Swift build/test exec26187
exit0 (`.build/fit175-build.log`, `.build/fit175-swift-tests.log`). Prepare81471exit0.
Output limit2GiB; preflight>8GiBfree; no wall-time cap per standing approval.

## Completion path

1. Poll84525 and inspect compact `artifacts/training.log` / run `results.csv`.
2. Once terminal0, run `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts
   YOLO_OFFLINE=true YOLO_AUTOINSTALL=false .venv-yolo/bin/python
   scripts/fit175.py infer` in approved MPS context, then `report`.
   Existing ready check binds completed20finite epochs, saved settings, fixed-last
   selection and source/data/initializer hashes. Preserve failures; no auto-retry.
3. Reconcile216training-fit,96development probes and2400retained outcomes versus
   reused019artifacts. Fit success requires≥90%recall in every placement at.25/.5;
   no threshold changes. Report geometry/confidence cases and cancelAction tradeoffs.
4. Update Tasks, CurrentState, ExperimentLog and one handoff. No promotion or extra
   epochs. Fit failure leads to target-assignment/loss/geometry diagnosis; success
   leads to a controlled exposure/generalization proposal, not shipping.

Software checks passed; existing data eligible for training diagnostics; local
training live; model gates unassessed. No TTR-relevant consequence/SMB update.
