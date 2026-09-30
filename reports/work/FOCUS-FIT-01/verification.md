# FOCUS-FIT-01 verification

Pre-existing working-tree changes from HUMAN-STATIC-ADMISSION/status reconciliation
preserved. No git writes. Research/Tasks updated before implementation.

- New versioned diagnostic adapter dispatches through existing
  `train_focus_ring_detector.py`; same AdamW/BCE, frozen feature validation and
  representative evaluator. Original training modes retain their behavior.
- Deterministic subset: four genuine pairs per native/Fixture appearance stratum,
  eight human positives/eight negatives (one each/frame),24/24overall. Every member
  was already admitted to training; no new human role amendment. Duplicate crop
  pixels, conflicting labels, missing support and development overlap fail preflight.
- Exact FDR017 cache/receipt/preflight and static protocol hashes are pinned. Full
  cached order/shape/dtype/labels/features checked before indexing the small subset.
  Original production crop hashes verified; no new cropper or encoder execution.
-42focused/legacy Python tests pass (`tests-final.log`), including real CLI preflight
  dispatch, changed configuration/approval rejection, deterministic balanced
  membership, validation leakage, malformed probabilities and training-only fit
  criterion. Tests use generated fixtures, not prior ignored experiment outputs.
- Offline Swift build/test pass (`swift-build-final.log`, `swift-test-final.log`):
 14XCTest plus109SwiftTesting tests. Project-local output/cache directories.
- One launch only:1000update/300model-second budget,600second external deadline;
  MPS required in launch and trainer. No CPU fallback, broad sweep, installation,
  capture, export or promotion. Development metrics cannot determine stopping.
- `report.py` validates saved prediction membership/losses, train-only stopping,
  representative metric replay, actual parameter change and preserved source hashes.
  Diagnostic success is not release eligibility; no best.pt is created.

Local training diagnosis only: TTR capture availability is not a dependency and
shared coordination is not applicable unless the result changes its next action.

## Executed outcome

Actual preflight eligible, MPS launch exit0; PID34480,68.756s including preflight.
Training-only stop at update162,48/48confident, BCE0.038574. Report replay exit0:
7,824training and1,665development/retention predictions accounted for, all pinned
input/code/crop hashes preserved, no best.pt. Development7/14unique correct,
38/288false positives; retention18/18. Diagnostic passed, release not qualified.

Retained FDR017/018 head audit also exit0, validates full original cache and reproduces
terminal development scores exactly (max error0.0). Native training focused hits
32/395 and27/395 at0.85; this adds observed training-fit evidence without retraining.
See `prior-training-fit.json` and `prior-fit.log`. No further model execution pending.
