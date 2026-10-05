# CONDITIONED-FEASIBILITY-142 — equivalent solve, rejected numerical witness

Implemented one source-bound interior-point comparison on the unchanged DTM040
993-constraint problem. Exactly zero rows/columns reduced; column L2 scaling and
row scaling preserve the original minimum-infinity-norm objective. No SVD truncation,
new labels, lowered thresholds, altered data roles or collection.

DTM041, PID34362: status0 (solver reports optimal), 33 iterations, 3.976226 seconds
solve / 6.214883 seconds total. Maximum original constraint violation
2.8524338688e-5 exceeds the preregistered 1e-6 gate. Rejected: no checkpoint, no
float32 scoring or stress report. This is not an infeasibility proof. The original
60-second timeout is preserved separately; no unchanged solve retried.

## Evidence and verification

- Entry point: `scripts/conditioned142.py --ready reports/work/CONDITIONED-FEASIBILITY-142/artifacts/ready`.
- Result: `NativeUITrainer/focus_ring_runs/conditioned142-dtm041/result.json`.
- Protocol SHA256: `8b1cc99083e625e3642122015bf88a21fcb7e97812a88060677b6560da10f404`.
- Python: existing `.venv-yolo`, `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPATH=scripts`,
  project-local TMPDIR, two BLAS threads. No dependency downloads.
- 40 focused Python tests pass in 0.577s, including unequal-scale objective parity,
  exact zero reduction, contradictions, input/budget rejection and mocked optimal
  status that fails independent original residual verification.
- Offline Swift build passes (1.86s), serial tests pass: 14 XCTest + 128 Swift
  Testing checks. Logs `.build/conditioned142-{build,test}.log`; project-local
  cache/config/security/module-cache/TMPDIR; scoped host permission for native tests.
- Documentation/diff review; no Git writes or shipped-model changes.

Software verified. Data eligible only for the existing exposed diagnostic.
Fresh producer integration not assessed. Model qualification not established;
numerical witness gate failed. Model-workflow skill kept these outcomes separate.
Preserved all pre-existing changes; new implementation/test plus task, plan, log,
current-state and lesson updates are this tranche's scope.

## Limitation and next tranche

The rejected vector was not serialized by the solver adapter; the aggregate residual
is preserved but cannot identify the worst row without another fit. Do not invent
that attribution or relaunch silently. Next bounded experiment: retain all finite
solver vectors as explicitly rejected diagnostics, record row-wise original and
scaled residuals, test a stricter equivalent numerical formulation, then attempt
actual float32 replay only after original-space acceptance. Keep model decisions
and nuisance robustness checks unchanged. One result, not a solver sweep.

Worker141 remains separately blocked on an approved PyTorch environment; no install
authority inferred. Fresh SMB inspection found no newer worker result or TTR snapshot
(TTR18:46:20Z, expired19:46:20Z). No redundant shared status publication: this local
numerical result does not change the peer's next action. Existing passive models
remain unchanged and no navigation authority is granted.
