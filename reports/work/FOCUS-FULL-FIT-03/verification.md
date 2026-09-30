# FOCUS-FULL-FIT-03 verification

Research-first amendment/ExperimentLog recorded prior to implementation and launch.
Existing uncommitted FOCUS-FIT-PREP-02 docs/receipts preserved. No Git writes.

- New `focus-full-fit-v1` adapter through existing trainer dispatch. Cached feature
  preparation and representative selection evaluator reused; legacy48crop mode unchanged.
- Exact approved proposal/928IDs/weights/315development/18retention; raw crop hashes,
  cache receipt/order/labels and finite tensors rechecked. No encoder execution.
-47focused/legacy tests pass: source/label mass, duplicate weighting/conflicting
  labels, role and pixel overlap, invalid scores/missing predictions, training-only
  streak stop, actual trainer preflight and override/stale approval rejection.
- Actual optimizer-loop tests use isolated generated four-example CPU fixtures,
  never corpus data; cover scheduled25/terminal26snapshots, no eligible best.pt,
  eligible selection and earliest tie. Production requires MPS without fallback.
- Offline Swift build and123tests pass (14XCTest/109SwiftTesting). No network.
- Single1000update/300model-second run with600second external deadline. Per-update
  full training predictions streamed to JSONL; history holds source/class metrics.
  Development every25/terminal only; unchanged gates determine eligible checkpoints.
- `report.py` replays every training/development observation and stop/selection
  decisions, checks code/input/crop hashes and parameter change. Execution result
  and diagnosis are recorded separately; software passes do not imply model passes.

Commands/results retained in tests.log, swift-build.log, swift-test.log, prepare.log,
preflight.json, training.log and execution.json. Shared coordination not applicable
unless the completed outcome changes TTR's next action.

## Actual execution and replay

Frozen protocol b650da4919583d57180ca0f29c6577529c2b6984f7582ce0c2c3ab695b5644b7;
actual trainer preflight launchEligible=true. MPS verified inside launch process.
PID40455,19:03:08–19:04:40UTC; exit0/no timeout;1000updates completed.
All40scheduled checkpoints evaluated; none eligible; no best.pt. Last.pt retained
diagnostically. Model loop21.342s, external process91.530s including preflight.

Report replay exit0:928,928training predictions and13,653development/retention
predictions accounted for; training-only stop/selection rules, finite gradients,
head parameter change and all pinned code/source/crop identities verified.
Training classification928/928at0.5; strict confidence901/928means fitPass=false.
Development9/14unique correct,14/27focused hits,3/288FP; retention18/18. Software
and execution pass, model gate fails. No new run authorized or process left running.
