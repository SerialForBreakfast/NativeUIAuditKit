# Offline productivity tranche — completed for review

2026-09-30. All three assigned offline workstreams delivered. User clarification
removed CUDA/cloud comparison; efficiency scope is local Apple Silicon/MPS only.

| Outcome | Evidence |
|---|---|
| Software | Three offline CLIs and optional existing-editor filter; 62 focused/legacy Python tests; offline Swift build and 123 Swift tests pass. |
| Data | Eight retained annotation frames/78 reviewed controls replayed; 333 retained validation/retention scores per snapshot checked; 512 training-only benchmark members pinned. No labels changed or new data admitted. |
| Integration | Actual retained-artifact CLI executions and offscreen editor interactions pass. Future paired-score reader reuses existing manifest validation and score protocol; synthetic adapter tests only until TTR delivery. |
| Model gate | Unassessed. No new capture, corpus inference, training, export or promotion. Existing FDR020 remains ineligible. |

## 1. Annotation noise: a measured, optional improvement

`scripts/annotation_proposal_filter.py` consumes the frozen comparison and original
review references, verifies hashes/membership, and reuses maximum-cardinality IoU
matching. No detector/OCR rerun. Geometry-only policies are fixed: near-duplicate
IoU≥0.8; compact mode also suppresses rectangles smaller than0.1% of frame area.
Original proposals and annotations are preserved. OCR is not treated as a control.

| Eight development screens | Proposals | Matches @0.50 | Matches @0.75 |
|---|---:|---:|---:|
| Raster raw |65|32/78|23/78|
| Raster compact |62|32/78|23/78|
| Vision raw |244|44/78|33/78|
| Vision compact |193|44/78|33/78|

Vision clutter falls51proposals (20.9%) with no lost reviewed matches on this set.
Deduplication alone removes none. Remaining149unmatched proposals are not necessarily
all false controls because reviewed candidate coverage is incomplete. This is a
development result, not an independent annotation-quality or human-time benchmark.
Small keyboard keys/icons could be suppressed on other screens: default remains off.

The existing Auto-detect / Import TTR OCR-box preview now has **Hide duplicate / very
small rectangles (experimental)**. Toggling off restores previous checkbox states;
hidden suggestions cannot be added by Select all; OCR remains separate. Cancel,
existing labels and undo behavior are preserved. No user window was closed/reopened.
Invalid bounds are caught inside the Qt callback rather than escaping and crashing.

Evidence: `generated/annotation-release/report.json` and eight numbered-proposal
comparison sheets. Settings sheet visually inspected: many internal-text/container
boxes remain; the filter is helpful but does not solve semantic box selection.

## 2. One retained-score decision report

`scripts/focus_decision_report.py` uses the existing selection/stratum/frame metrics,
checks sealed protocol, exact prediction membership, score validity and source crop
hashes, and reproduces the published initial and terminal results. Comparisons here
are **initial versus terminal FDR020 on identical inputs**, not a causal data ablation.

| Terminal development stratum | Focused hits | False positives |
|---|---:|---:|
| Buttons |3/3|1/3|
| Tabs |2/3|0/21|
| Artwork |1/12|2/181|
| Rows |6/7|0/64|
| Other |2/2|0/19|

Complete-frame selection:9unique correct,4no focus,1multiple,0wrong;18additional
frames remain unavailable for complete-selection claims. Retention18/18. No threshold
change. The report separately lists each pending first3case and recipe hash; none has
fabricated scores or accepted-label claims.

An optional `--delivery` plus `--delivery-sha256` imports consumer-owned references to
**existing** `focus-baseline-protocol-v1` / `focus-baseline-scores-v1` envelopes and
production crop manifests. It verifies the manifest through the current validator,
one pair per case, native scene recipe identity, development role, exact samples,
preprocessing, artifact/protocol binding and scores using the existing scorer.
Incomplete deliveries stay unavailable. Paired-target scores cannot claim unique
frame selection without competitor scores. No new producer transport/schema required.

Evidence: `generated/decision-release/report.md` and `report.json`. Actual three-pair
capture/QA/inference remain dependencies, not completion claims of this offline tranche.

## 3. MPS-only efficiency audit and next measurement

`scripts/training_efficiency_audit.py` reads Run013args/results/log excerpts, installed
source and package metadata without importing Torch/Ultralytics. It pins source hashes
and512deterministically chosen training images/labels; no files are copied into new
training partitions. Counts:14,540train /2,800val /2,400test; present classes40/35/38.
These are inventory/support counts, not another full pixel-integrity qualification.

- Measured CSV/log duration:226,143seconds =62.8hours for106epochs; median epoch35.1minutes.
- Saved workers4, but log confirms **0actual workers**. Inspected source forces0on MPS.
- Saved AMPtrue, but inspected MPS source disables it; historical effective AMP was
  not independently traced. Recttrue disables requested mosaic1.0 in inspected source.
- Batch8/nbs64 implies steady accumulation8/effective batch64; warmup varies it.
- Saved initialization points at generic `yolo11m.pt`, resume false—not a Run009 UI
  checkpoint. This is recorded intent, not a new claim about historical loaded bytes.
- Best recorded fitness epoch91; installed fitness uses mAP50–95. Save-period−1
  avoids intermediate epoch checkpoints but does not disable last/best saves.
- Stage costs and actual batch tensor shapes are **unknown**. No honest GPU-loading
  attribution or speedup estimate can be extracted from aggregate elapsed time.

Actual callback fixtures confirm OHEM assigns a batch-loss proxy to all images,
invalidates decoded caches at epoch replacement, preserves file/label alignment,
but leaves rectangular batch metadata unchanged after moving images between slots.
That is a correctness risk requiring a focused repair/decision before performance
comparisons—not proven to explain the62.8hours. `last.prev` is a post-save mirror,
not guaranteed previous-epoch recovery. Trainer behavior was not modified here.

Evidence: `generated/mps-release/audit.json` and `benchmark.json`. Proposed future
MPS arms are batch8 and16, workers0/AMPfalse/recttrue, same initialization and512
training examples, ten warmup batches/two repetitions, maximum30minutes. Batch changes
also change warmup/OHEM proxy semantics; equal nominal effective batch is not proof
of equivalent learning. Execution remains blocked on separate local compute approval,
rectangular-OHEM decision and timing instrumentation in the existing trainer.
No CUDA, cloud allocation, dependency installation or launch command is implied.

## Verification and preservation

- `release-tests.log`:62tests,0failures (includes actual Qt preview and existing
  revision2intake compatibility). Reproduction commands in `usage.md`.
- `swift-build-host.log`: offline build, no warnings/errors. `swift-test-host.log`:
  14XCTest +109SwiftTesting,0failures. Initial restricted launch failed at
  `sandbox_apply`; scoped host execution passed with project-local caches.
- Failed initial GUI fixtures are retained in logs; corrected bounds/test placement
  and callback error handling verified. No failing test is represented as a pass.
- Prior dirty files preserved; no Git writes or trainer/model modification.
- Coordination: not applicable. TTR still owes the same manifest-access repair;
  this work introduces no new peer action. No shared status noise or monitoring.

## Next assignment

First, repair/test the rectangular OHEM replacement policy and add coarse timing to
the existing trainer (no new training required for implementation). Separately, when
TTR delivers its manifest-access fix, complete the already-approved three-pair capture
and label/crop QA. These two tracks do not depend on one another. No further broad
manual annotation batch or unchanged training run is recommended.
