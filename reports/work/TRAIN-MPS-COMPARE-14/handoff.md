# TRAIN-MPS-COMPARE-14 — completed for review

Owner Codex,2026-09-30. User continued the bounded batch8/16MPS comparison.
No full training, default change, CUDA, export or model promotion.

## Result and decision

All four trials exited0; aggregate712.116s (11m52s), below1800s. No resource stop.
**Retain batch8as the default on this24GiB M4.** Batch16produced modest higher
throughput but materially less memory headroom. This is a completed decision,
not a request for an unchanged full training run or a larger-batch sweep.

| Trial | Batch | Epoch1 training seconds | Images/s | Whole trial seconds | Lowest sampled available RAM GiB |
|---|---:|---:|---:|---:|---:|
|1|8|77.810|6.580|181.614|6.213|
|2|16|71.320|7.179|171.228|3.575|
|3|16|72.182|7.093|173.388|3.374|
|4|8|76.707|6.675|181.663|5.465|

Median epoch1training wall:77.258s(batch8) versus71.751s(batch16).
Batch16takes7.13%less time, equivalent to7.67%higher throughput (6.627→7.136images/s).
Whole-trial medians181.638→172.308s are supplementary because epoch2OHEM membership
differs. Peak logged MPS driver allocation5.62→10.60GiB; not total RAM or a sampled
process RSS. Minimum batch16available RAM3.374GiB leaves only0.374GiB above the
runtime reserve. No guard was breached; these are sampled extrema, not every transient.

Epoch1optimizer steps were19(batch8) versus15(batch16), so the measured gain is
not pure GPU scaling or constant optimizer work. Two repeats do not establish
quality equivalence or a statistical confidence interval. No qualification claims
are drawn from these tiny diagnostic validation results.

Per-trial sampled output peaks724.4MiB; minimum free disk43.33GiB. Final retained
comparison footprint1976.6MiB. All eight epochs and384training batches accounted
for; no process remains running. Generated weights are isolated diagnostic outputs.

Result:`generated/comparison-01/comparison-result.json`, SHA256
`1a73cd75e28bc6605080c56ec24d2dd5f9abf99b48378863059a5b78f22df034`.
It contains every trial PID, duration, resource disposition and timing/receipt hash.
PIDs87684,88127,88576,88973all exited0. Post-run replay exactly reproduces all
four timing records;576input members, checkpoint and current source pins reverified.

Next priority: return to tvOS focus's representative data/validation work. Refresh
the TTR handoff and complete the already-approved three-pair intake/crop QA when
producer delivery is ready. This iOS hardware-tuning result does not resolve
focus-model transfer/coverage gaps. Any different model-size/precision experiment
would require a separately defined quality comparison, not an automatic run.

## Frozen contract and evidence

Bundle:`generated/comparison-01/comparison-plan.json`.
SHA256:`519da3f7336f8699fc015edc8e2f98efae46cffa7e896db52d359fbca4725d28`.
The two arm plans pin identical576members, taxonomy, initial checkpoint, runtime
versions and trainer sources; only batch differs. Trial order8,16,16,8. Each trial
starts a fresh model/optimizer from local yolo11m.pt, runs2epochs on512train/
64validation images with seed42, MPS,workers0,rect640, existing OHEM and warmup.

Primary measurement: epoch1training batch intervals plus between-batch gaps.
Each arm sees the same512source images before OHEM changes next-epoch membership.
Batch grouping changes padding and warmup optimizer scheduling. Later OHEM sample
membership can differ. No pure GPU, steady-state or quality-equivalence claim.
Two repeats provide a range, not a population confidence interval.

One1800s execution deadline includes staging; supervision polls every2s and allows
up to10s owned-child termination grace. Per-trial guards:8GiB available RAM at
launch,3GiB runtime reserve,10GiB disk reserve,2GiB output. No automatic retries;
any blocked/failed/stopped trial ends the comparison and preserves partial data.

## Verification

35offline Python tests pass, including matched-input rejection, complete epoch/
batch accounting, wrong backend/batch, nonfinite timing, missing repeats, stopped
trial/no retry, worker batch16arguments and strict v1batch8compatibility. Required
offline Swift build succeeds;14XCTest+109Swift Testing tests pass. Logs retained.

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts TMPDIR="$PWD/.build/debug-output" .venv-review/bin/python -m unittest scripts.test_mps_batch_comparison scripts.test_mps_training_diagnostic scripts.test_ohem_timing scripts.test_ohem_callback scripts.test_training_preflight
```

Actual execution uses `.venv-yolo/bin/python scripts/mps_batch_comparison.py execute`
with the above bundle/hash. `execute.log` records each trial's start/end/PID/result.
The comparison result records raw trial metrics, resource minima, timing/receipt
hashes and aggregate disposition. Trial outputs remain diagnostic-only.

## Independent outcomes

- Software: offline verified and integrated with existing trainer/supervisor.
- Data: frozen diagnostic subset; no new admission or protected test use.
- Integration: pass; actual MPS trainer/supervisor completed all four trials,
  matching runtime metadata, two epochs and expected batch counts in every trial.
- Model gate: not assessed. Default batch and shipped models remain unchanged.

TTR coordination not applicable: this local iOS efficiency experiment changes no
producer action. Software/data/runtime evidence and recommendation are complete;
model gates remain unchanged. No shared publication or monitoring was needed.
