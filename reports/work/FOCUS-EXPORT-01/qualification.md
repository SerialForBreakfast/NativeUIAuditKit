# Isolated export and parity — 2026-09-22

| Outcome | Result |
| --- | --- |
| Software verified | Existing real export/compile/parity entrypoints pass;5 focused safety/parity tests pass in new environment |
| Data eligible | Unchanged frozen12-crop Remotes development challenge; not full training or release eligibility |
| Integration qualified | Passed for experimental FDR-007 on this host's CoreML CPU path and exact challenge |
| Model gate passed | Not established; decimal5MB size limit fails and full FocusRing gates remain open |

## Dependency repair completed

User explicitly approved package downloads/installation and the external environment
`/Users/josephmccraw/Library/Application Support/NativeUIAuditKit/Environments/focus-export-01`.
Created it only after confirming absence. Python3.12.9, PyTorch2.7.0,
coremltools9.0, NumPy1.26.4; no scikit-learn/SciPy or old-environment imports.
[Apple release support](https://github.com/apple/coremltools/releases) identifies
PyTorch2.7 support. Conversion-runtime version differs from training/reference;
comparison uses the unchanged frozen reference, not a redefined baseline.

Direct pins: `export-requirements.txt`; resolved24 package versions:
`export-lock.txt`; downloaded wheel URLs/SHA256 hashes: `install-report.json`.
Wheel-only installation exited0 (`install.log`); `pip check` reports no broken
requirements. Metadata scan found22915 regular files and **zero dataless files**
inside the new environment. Old `.venv-yolo`, provider settings and dependencies
remain unchanged. This bypasses the current cloud-residency defect; it does not
repair iCloud or promise immunity to future eviction/configuration changes.

## Real execution

All explicit logs, temporary/cache paths and model outputs remained in-project;
normal host CoreML cache access was separately approved. The wrappers retain exact
commands, exit codes and durations; output collisions fail rather than overwrite.

| Stage | Exit | Seconds | Evidence |
| --- | --- | --- | --- |
| Import Torch/CoreML | 0 | 8.904 | isolated-import.json/.log |
| Trace/FP16 export | 0 | 3.466 | isolated-export.json/.log |
| coremlc compile | 0 | 1.145 | compile-execution.json/compile.log |
| Actual production CPU parity | 0 | 3.885 | compare-execution.json/compare.log/parity.json |

Artifact: `NativeUITrainer/focus_ring_runs/fdr007-native-incremental/export-01/`.
Checkpoint SHA256: `a5c7f2f44368feb4ec81477aab33f1e0f5e2f380c43fb5d9ebca3bd26c3499f0`.
Package SHA256: `4d43d6f4aedb7d26e820c7c33d79fa4e21b28d64a25a683f03c6219e64ccdf02`.
Compiled SHA256: `a669a4111e145d9c57127e71ad6c6abe7268e16fbc013632094f84ffb44dcde9`.
`artifact.json` and export metadata bind the experimental identity/checkpoint;
`releaseEligible=false`. No shipped resource or public API was changed.

## Parity, latency and size

Actual parity validates source/crop bytes, reviewed labels, native runtime identity,
checkpoint, frozen reference hash and training/challenge isolation before inference.
Production crop behavior remains16% expansion/256×256; no new cropper.

- Twelve predictions,6 positive/6 negative:12/12 correct at0.5 and0.85.
- Maximum absolute probability error **0.00000357628**, mean0.00000138507,
  versus frozen tolerance0.01. Zero decision differences at0.5/0.70/0.85.
- No near-threshold reference examples or ambiguity examples. This saturated,
  correlated same-app development set does **not** establish general calibration.
- Two helper processes (pixel-budget batches9+3): model load45.91/14.83ms;
  first inference4.96/4.20ms; remaining10 warm predictions median1.36ms.
  CPU host inference only, excluding separate crop time; not ANE/device/navigation latency.
- Package **5,038,123 bytes = 4.80473MiB = 5.038123MB**. Existing exporter exit0
  reflects its5MiB calculation. The specification's literal5,000,000-byte limit
  **fails by38,123 bytes**. Do not waive it or call all model gates passed.

## Verification, preservation and next action

`isolated-tests.log`:5 focused export/parity tests, exit0,0.004s in the new runtime.
No production source changed this turn; retained prior68 Python/93 Swift evidence
belongs to that earlier source/runtime scope, not newly rerun tests. No Swift
rebuild was needed and the hash-bound inference helper stayed unchanged.
`git diff --check` passed. Only the report wrapper changed to use `sys.executable`
so its child parity process cannot silently return to the broken old environment.

All authorized installation/export/compile/parity work is complete for review.
No new training run, capture, promotion, background job or automatic retry remains.
SMB not applicable: local export success does not assert TTR integration.

Next bounded work: reconcile/enforce explicit package-size units without relaxing
the existing gate; separately investigate a smaller experimental export if needed.
Then expand independent, differently styled and near-threshold evaluation evidence
before any promotion decision. Preserve this package and parity report as baseline;
the12 successful crops do not justify another same-style training loop.
