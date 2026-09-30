# FDR-014 handoff

Assigned sampler correction and one bounded comparison are complete. Model gate failed.

- Software: additive versioned sampler adapter integrated in the actual trainer
  preflight; legacy selectors preserved. 82 focused tests pass, offline Swift build
  passes, 14 XCTest and 109 Swift Testing tests pass. Logs retained here.
- Data: exact original 363 training and nine retention pairs preserved; 453 real
  selection crops and 64 exclusions unchanged. Training appearance mapping uses
  hash-bound recipe/target metadata. No evaluation data entered training.
- Integration: actual seed-42 sampler draws verified; actual approved trainer
  execution completed on same-process-verified MPS/PyTorch 2.7.0. PID 67225,
  2026-09-29 22:22:30–22:26:06 UTC; 123.54s training, 216.07s overall. Exit 2 is
  the intentional no-eligible-checkpoint result, not a crash or timeout.
- Model: 0/30 eligible epochs. All 18 retention decisions preserved every epoch,
  but real false positives/misses and full-frame errors remain unacceptable.
  Conditional selected-checkpoint comparison unavailable; no export or promotion.

Protocol content SHA256:
`e807725468811a02af7c775d881e8582a1a9a3d6caa69e20e139b9bd2291298a`.
`inputs.json`, `protocol.json`, `approval.json`, `sampler-draw-verification.json`,
`started.json`, `backend.json`, `execution.json`, `training.log`, and
`selection-verification.json` retain the reproducible evidence. Large JSON/log/model
artifacts are gitignored and project-local; no independent backup is claimed.
Run output: `NativeUITrainer/focus_ring_runs/fdr014-appearance-sampling-mps/`.

All 14,601 initialization/epoch scores and selector metrics replayed. Code hashes
were rechecked after execution. No training process or automatic retry remains.
Source images, annotations, prior checkpoints and shipped models are unchanged.

[Results and prioritized next assignment](results.md): audit existing offered
native100/canvas-v2 against concrete artwork/tab contrast failures before another
training proposal. This is a completed experiment, not a successful release.
