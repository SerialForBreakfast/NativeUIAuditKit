# TRAIN-MPS-DIAG-13 — diagnostic completed

**Superseding result:** user freed memory and authorized resume. Attempt02
completed on MPS in189.832s, two epochs/128batches, exit0. No resource limit hit.
[Measured costs, receipts and next decision](execution.md). Historical blocked
attempt01 and its resume command are retained below, not current blockers.

2026-09-30, owner Codex. Continues the repaired OHEM trainer with one bounded local
timing diagnostic. No full training, CUDA, capture, export or promotion.

| Outcome | Result |
|---|---|
| Software verified | Pass:30Python tests, offline Swift build,123Swift tests |
| Data eligible | Pass for diagnostic only:512train/64validation members verified; no cross-split identical pixels |
| Integration qualified | Pass: actual MPS trainer/timing/OHEM path completed; attempt02 receipt exit0 |
| Model gate passed | Not assessed: diagnostic weights isolated; no shipping/quality qualification |

## Historical attempt01 result

The input freeze completed. Launch preflight returned
`insufficient_available_memory`:5,410,406,400bytes available (5.04GiB) of24GiB,
below the conservative8GiB launch requirement. Disk free48,145,682,432bytes
(44.84GiB) exceeds the10GiB reserve. This is a safety-policy refusal, not a measured
OOM or proof the model cannot run on this Mac. No child PID, elapsed model time,
model output or stage timings exist. No user processes were closed.

Evidence: `generated/attempt-01/preflight.json`, `execute.log`, `prepare.log`.
The execute command exits0 with an explicit blocked receipt; that is not a
successful training result. No automatic retry/monitor was installed.

## Frozen experiment

- Plan: `generated/frozen/plan.json`
- SHA256:`21f83fffcb44e545d3c7299c2964bd122ca5647705eb73a1ad2b8ad096e3066a`
- Weight: `NativeUITrainer/weights/yolo11m.pt`
- Weight SHA256:`d5ffc1a674953a08e11a8d21e022781b1b23a19b730afc309290bd9fb5305b95`
-512existing training images and64original validation images, hashes, decoded-pixel
  integrity, finite YOLO labels, original split bindings and15source/runtime pins.
  No test images. Source pixels/labels and dataset caches are untouched.
- Torch2.13.0,Ultralytics8.4.124,NumPy2.3.5,Pillow12.3.0,psutil7.2.2.
-2epochs,batch8,imgsz640,MPS,workers0,seed42; repaired OHEM and existing optimizer,
  augmentations and3epoch warmup unchanged. This measures early-training costs,
  not steady-state throughput or quality. Diagnostic weights remain ineligible.
-1800s child deadline;8GiB RAM launch guard,3GiB runtime RAM reserve,10GiB disk
  reserve and2GiB artifact limit. Supervisor terminates only its owned child.

## Implementation and verification

`scripts/mps_training_diagnostic.py` provides prepare/execute/internal worker
paths. Preparation never imports Torch. Execute verifies frozen hashes before
resource checks, then stages copies only if eligible. Worker rechecks staged
hashes/configuration, pins local initialization, requires MPS and calls the existing
trainer with timing. Network attempts are denied; configurable caches stay local.
The supervisor preserves child exit/deadline/resource outcomes and partial logs.

Tests exercise real image/label integrity, changed hashes, protected/duplicate
membership, path boundaries, memory/disk/output guards, no spawn on blocked
preflight, actual staging/source preservation, worker arguments with fake model
runtime, child success/nonzero exit, deadline termination and supervisor failure.
Legacy OHEM/timing/preflight tests pass. Small subprocess tests only execute
exit/sleep commands; no model computation.

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts TMPDIR="$PWD/.build/debug-output" .venv-review/bin/python -m unittest scripts.test_mps_training_diagnostic scripts.test_ohem_timing scripts.test_ohem_callback scripts.test_training_preflight
```

30tests pass. Required offline Swift build succeeds without warnings;14XCTest+
109Swift Testing tests pass. CLI preparation, blocked preflight, frozen-input
reverification and `git diff --check` exit0. Logs are retained beside this handoff.

## Historical resume condition and command (attempt02 now complete)

Make at least8GiB RAM available without the agent closing unrelated apps. Then
explicitly resume the diagnostic; the guard checks again. Use a fresh attempt
directory and the unchanged plan hash. No blanket continuation into a full run.

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts TMPDIR="$PWD/.build/debug-output" .venv-yolo/bin/python scripts/mps_training_diagnostic.py execute --plan reports/work/TRAIN-MPS-DIAG-13/generated/frozen/plan.json --sha256 21f83fffcb44e545d3c7299c2964bd122ca5647705eb73a1ad2b8ad096e3066a --output reports/work/TRAIN-MPS-DIAG-13/generated/attempt-02
```

If source/runtime pins change, review and freeze a fresh plan; never just change
the expected hash. Once completed, inspect host-wall stage costs and resource
trace before proposing any optimization or another experiment. Host intervals
overlap and do not isolate GPU kernels. No speedup has been measured.

Scope complete for software/preparation and actual bounded timing. Independent
local work in this tranche is finished. TTR coordination
not applicable; no producer action changed and no shared metadata was published.
