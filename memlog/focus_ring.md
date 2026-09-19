# FocusRingDetector — Phase B

- 2026-09-17: Stage 2 crop classifier scaffolding. Spec in
  `Research/FocusRingDetectorSpec.md`. Run FDR-001 in ExperimentLog.
- YOLO pipeline untouched. Heuristic `resolveTVOSFocus` kept as fallback.
- Simulator is insufficient (Metal glow / parallax). Live harvest uses Office.
- TVTestRig App Sandbox: aatv talks to container socket via HOME override; do
  not set TVTESTRIG_PROJECT; do not listdir Evidence/Sessions.
- Office connected 2026-09-17 20:20. Live `--live` harvest pass 1 wrote **454**
  labeled pairs to `dataset/focus_ring/` (908 crop PNGs). Target is 1,500.
  `connectionLost` from step 1731; do not overwrite the manifest on resume.
- 2026-09-17 21:36: Pass 2 complete. **1500** labeled pairs (train 1201 / val 164 /
  test 135). collectionItem 1055, primaryButton 225, secondaryButton 215,
  segmentedControl 5. Starting `train_focus_ring_detector.py --name fdr001`.
- 2026-09-17 22:27: fdr001 **TRAINING_COMPLETE** (11.1 min, MPS, 30/30).
  best val_loss=0.0001. Torch test 270/270 acc=1.0. Hard-neg n=0 (dark only).
  CoreML export blocked (`import coremltools` hangs). Do not ship `.mlmodelc`.
- 2026-09-18: Swift integration complete. `FocusRingClassifier.swift`,
  `resolveTVOSFocusML()`, `loadFocusClassifierIfAvailable()`, and
  `useFocusClassifier` config all wired up. `swift build` + 66/66 tests pass.
- 2026-09-18: CoreML export unblocked. `export_focus_ring_coreml.py` rewritten
  to use `torch.jit.trace → ct.convert` (no onnx package). `FocusRingDetector.mlpackage`
  = 4.80 MB (gate ≤5.0 MB PASS). Compiled to `.mlmodelc`. Installed in
  `NativeUIAuditKitModels/Sources/.../Resources/`. Package.swift updated.
  All 66 tests pass with the model bundled. FOCUS-DET-04 complete.
- 2026-09-18: FocusRing tests require the bundled model: URL non-nil, load
  succeeds, metadata `focusThreshold`/`ambiguityThreshold`, classify on
  `tvos_home_screen.png` returns prob in [0, 1].
