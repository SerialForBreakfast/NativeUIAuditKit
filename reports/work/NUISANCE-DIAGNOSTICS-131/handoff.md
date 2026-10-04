# NUISANCE-DIAGNOSTICS-131 — October4

## Post-update check

Xcode27.0/27A266a selected at `/Applications/Xcode.app/Contents/Developer`.
Offline `swift build` passed (14.18s). `swift test` compiled (7.18s) and14XCTest
passed, but Swift Testing did not complete. One-second sample of helper11510 shows
concurrent Vision request/semaphore/capacity-queue waits; cause not established.
Preserved `.build/nuisance131-{build,test}.log` and
`.build/nuisance131-test-sample.txt`; stopped only owned helper11510/runner10364.
No daemon resets or repeated unchanged run. Full native verification remains blocked
pending a focused Vision concurrency/backend diagnosis; earlier139pass is not a
pass on this updated environment. SMB reconnected and owned status published/read
back; see coordination.md. New peer archives acknowledged, not yet copied.

| Outcome | Evidence |
|---|---|
| Software verified |14Python tests pass; real diagnostic CLI completed. Required Swift build/test pending while Xcode updates; not a complete software gate.|
| Data eligible |Existing exposed membership unchanged; no new admission or independent final evidence.|
| Integration qualified |Local source/feature replay verified after storage rebind; no TTR/native operation.|
| Model gate passed |Not assessed. No fit/export/promotion; guard is diagnostic only.|

Base75a2364, initially clean. Two frozen experiments complete in36.270s, including
4.750s feature diagnostics; report1,727,888bytes, below2GiB cap. All source tensor,
mask, labels, groups, model/cache hashes and parent seals verified. Source setup
also replays DTM030 exactly. No source bytes or model weights changed.

## Results

Fixed max-residual thresholds1e-5 and1/255 produce identical guard decisions.
Fit robust affine parameters on80% support; check residual over **all** content.
Only confident changed becomes abstention; identity or unchanged output preserved.

- Originals207/207 and exact identities226/226 retained, no new abstention.
- Each one-sided dim condition:6/226correct unchanged,220abstain,0confident wrong.
- Each contrast/bright condition:0correct unchanged,226abstain,0confident wrong.
- No additional lost successes across all11conditions. This does not recover
  transformed positive misses or make the corpus independently qualified.
- After-only left/right motion still has150/190confident negative errors;
  respective negative correct counts76/31. Guard does not address alignment.
-1299cached fit rows: no exact opposing-label collisions in raw, normalized or
  combined residual features. Active standard deviations1.14e-6…8.027 in raw/
  combined blocks; numerical ranks527/391/748. Condition numbers at the declared
  relative1e-7 rank cutoff~9–10million; cutoff-dependent, not proof of optimizer cause.
  Opposing/within-class median-distance ratios25.2/679151.5/36.8; normalized ratio
  is inflated by near-identical derived views and is not generalization evidence.

Evidence: local ignored `artifacts/audit/report.json`, SHA256
`e02c0a7b8b7167a0e98bd71be1ea4c154fb8427654bcc0ca800f66ade91c3d5e`.
Per-case residuals, flags, outputs, nearest opposing indices and all parents retained.

## Commands / runtime recovery

`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts TMPDIR="$PWD/.build" OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 .venv-yolo/bin/python scripts/diagnose131.py --output reports/work/NUISANCE-DIAGNOSTICS-131/artifacts/audit`

First attempt stopped before inference/output with `storage_wrong_volume`. OS update
renumbered SSD fromdisk25s1 todisk7s1. Read-only mount/diskutil inspection established
local USB/APFS,2TB capacity,~1.909TB free, UUID
`FD8D8E36-FAAC-4205-87ED-86134C3582B1`. Local/SSD campaign receipt SHA256 both
`33e7e41bfdd0aa53648a1b97f0d0f0eee55953fecf3fc86f535a2208ec706742`.
Rebound only ignored local registry device field; unchanged per-input hashes then
passed. No disk writes, moves, deletion, daemon or Simulator operations.

Corrected invocation exit0. Focused suite:
`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts TMPDIR="$PWD/.build" .venv-yolo/bin/python -m unittest scripts/test_diagnose131.py scripts/test_dual130.py scripts/test_nuisance129.py`
exit0,14tests,1.035s. `git diff --check` exit0. No Git writes.

## Remaining / next substantial tranche

Native checks explicitly pending until Xcode finishes; do not disturb installer.
Then verify selected toolchain and run required offline build/test once. Experiments
and local tests complete; no process left running. SMB absent; latest peer unknown.
Preserve deployed passive models. No new TTR feature/capture request follows from
these exposed diagnostics; [coordination draft](coordination.md) remains unpublished.

Next: a fixed train-only feature-scale-conditioned DTM032 comparison (prelog exact
configuration, no sweep), plus quantization/localized-appearance falsification of
the guard. Retain strict207/226original gates and report all unfitted probes. Neither
scaling nor native robustness follows merely from this feature audit.
