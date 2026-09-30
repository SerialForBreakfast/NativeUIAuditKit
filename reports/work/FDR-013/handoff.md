# FDR-013 handoff — completed experiment, rejected candidate

- Software verified: passed. Frozen implementation hashes match the77-test and
  offline Swift build/14XCTest/109Swift Testing evidence from FOCUS-SELECTION-01.
  Every stored selection calculation reproduced. No implementation changed.
- Data eligible: passed for the approved363training+9retention development pairs
  and453selection crops only. Original artifacts and all exclusions preserved.
- Integration qualified: passed for approved training and fail-closed selection.
  Same-process MPS verification, full30epochs and owned-process exit receipt.
- Model gate: failed.0/30eligible epochs; no selected checkpoint, export or promotion.

Approval: `approval.json`. Protocol SHA256:
`1c39256bf41e133d1e9532d35f4b2d6d6f7e24240729eb0375fc04e866326ae7`.
Output: `NativeUITrainer/focus_ring_runs/fdr013-representative-mps/`.
PID63806,21:56:46–22:00:24UTC;124.34s trainer/217.41s overall;exit2.
Exact invocation and same-process MPS assertion: `started.json`; backend/version:
`backend.json`; owned process completion: `execution.json`; full log: `training.log`.
The trainer's actual approval-bound preflight is saved inside the run directory.

FDR007 initialization, freshAdamW,50/50native–Fixture,30epochs,batch64,lr0.0003,
seed42,noaugmentation,1800second deadline. Training examples never include the
453real selection crops;64other real labels remain explicitly excluded.

`frozen-comparison.json` pins the prior comparison by hash, exact six input
protocols and membership digests:517real/312related-synthetic scores. Baseline
metrics were recomputed without inference. The selected-checkpoint comparison
was conditional on an eligible best.pt; none exists, so no further model inference
was run and last.pt was not evaluated as a substitute.

`selection-verification.json` replays initialization+30epochs, all14,601scores and
all eligibility guards, identifies persistent false positives/misses, and verifies
unchanged software hashes. [Results](results.md) explain the false-positive failure
and next targeted data assignment. This is not a production qualification result.

Artifacts are project-local/gitignored and retained; no independent backup claimed.
No source pixels, annotations, old checkpoints, shipped models or Git state changed.
No training process remains; no automatic retry or monitor was installed.

Assigned run is complete and no candidate qualifies for its conditional comparison.
Next assignment: receipt/coverage audit of existing native100-r2 and canvas-v2,
prioritizing artwork hard negatives and tab focus contrasts, before further training.
Coordination publication is recorded separately in coordination.md.
