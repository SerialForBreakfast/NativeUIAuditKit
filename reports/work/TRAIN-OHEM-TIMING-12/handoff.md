# TRAIN-OHEM-TIMING-12 — completed for review

Owner: Codex. Scope: OHEM batching repair, optional timing and offline verification.

## Delivered

- OHEM replacements retain original rectangular output-shape compatibility.
  Shortfalls are counted rather than silently inserting incompatible images.
- Each epoch starts from original membership. Labels are copied independently;
  decoded caches and augmentation buffer reset, followed by loader reset.
- Changed membership, identity, label binding or batch geometry fails before
  mutation. Automatic loader rebuild fails before the next model forward rather
  than using stale snapshots. A restart with explicit batch size is required.
- `train_ios_model.py --timing` opts into a fresh `host-timing-<uuid>.jsonl` in
  the run directory. Default remains off. No other training setting changes.
- Records include actual backend/workers/AMP/setup accumulation, batch intervals,
  inter-batch gaps, preprocessing, optimizer step, validation, checkpoint save/mirror,
  OHEM recording/replacement, epoch totals, replacement shortfalls and terminal
  completed/failed outcome. Partial timing is retained on training exceptions.

Host wall-clock measurements are nested, not additive; they do not isolate GPU
kernel or pure loader time. No synchronization is injected. Initial model loading,
final best-checkpoint evaluation outside trainer.validate, and exact forward/backward
separation are not independently timed. No performance or quality gain is claimed.

## Acceptance evidence

`scripts/test_ohem_timing.py` covers mixed rectangular groups, partial final batch,
exhausted compatible slots, independent duplicate labels, noncompounding epochs,
drift/malformed metadata, missing/nonfinite loss, loader rebuild and timing errors.
Tests invoke the real trainer main with an entirely fake runtime: timing enabled,
disabled, OHEM disabled, normal completion and raised training failure. Fake clock
assertions verify durations and suppression of duplicate final-eval epoch records.
Legacy OHEM, preflight and offline productivity tests also run. The earlier
rectangular-risk regression now asserts the repaired behavior.

Commands (from repository root):

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts TMPDIR="$PWD/.build/debug-output" QT_QPA_PLATFORM=offscreen .venv-review/bin/python -m unittest scripts.test_ohem_callback scripts.test_ohem_timing scripts.test_training_preflight scripts.test_offline_productivity
```

Offline Swift build/test use `--disable-automatic-resolution` and project-local
SPM/cache/temp paths. Logs: `python-tests.log`, `swift-build.log`, `swift-test.log`.
Final results:43Python tests pass; Swift build succeeds without warnings;14XCTest
and109Swift Testing tests pass (123total). CLI help exposes `--timing` and
`git diff --check` passes. All checks exit0. No trainer/model runtime was imported
by the Python tests; the actual main integration uses explicitly fake modules.

## Independent outcomes and next step

- Software: repaired and offline-tested; no production model execution.
- Data: unchanged; no capture, admission or corpus migration.
- Integration: actual trainer entrypoint tested with fake runtime; live training
  timings remain unmeasured. Shared coordination not applicable: no TTR action changes.
- Model gate: unchanged/unassessed. No CUDA, training, export or promotion.

Next: prepare/approve one bounded local MPS timing experiment with pinned inputs,
checkpoint, duration and memory limits. Use these diagnostics to find dominant
costs before another full run. OHEM is still a batch-loss proxy; this repair alone
does not establish its benefit. A synchronized comparative benchmark requires
its own harness and approval, not merely adding `--timing` to a full training run.
