# Phase 6a — Run 007

Started: 2026-08-23
Goal: YOLO11m 41-class family-holdout training.

- Scripts: export_coco.py, compute_class_weights.py, ohem_callback.py, train_ios_model.py
- 2026-08-23: dataset at `dataset/dataset/`. Export 82 MB (symlinks). Dry-run OK.
  Full YOLO11m Run 007: epoch 1 done (mAP50=0.040). Epoch 2 crashed —
  OHEM appended 2,300 files without resizing `ims` (BP-29). last.pt is epoch 1.
- 2026-08-26: Power cut mid-epoch 46. `last.pt` is epoch 45 (best mAP50=0.984
  at epoch 39). Resumed PID **3889**, watchdog **3866** (`caffeinate` +
  `scripts/watch_phase6a.py`). Log `NativeUITrainer/training_6a.log`.
- 2026-08-27: TRAINING COMPLETE. Early-stop epoch 93. best.pt mAP@0.5=0.981
  mAP50-95=0.919. FP16 CoreML `best.mlpackage` 38.5 MB (no distill).
  Next: TASK-6a-5 INT8 bench + TASK-6a-7 holdout eval.
- Holdout families: CardDetail, WizardStepFlow, NotificationCenter, GalleryPage,
  MultiSectionForm, SettingsToggleDense, EmptyState, OnboardingPage
- Coverage gap: 36/41 taxonomy classes in the iOS generator
- Empty: statusBar, toolbar, scrollIndicator, tooltip, unknown
- Dropped extra label: tabBarItem
