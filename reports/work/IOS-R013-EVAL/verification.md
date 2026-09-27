# IOS-R013-EVAL verification

Owner: current NUIAK evaluation worker. Assignment: maintainer-approved local
Run013 evaluation, 2026-09-27. No training, export, promotion or capture.

## Software checks

All commands run from the package root with `.venv-yolo/bin/python -B`.

- `-m unittest discover -s scripts -p 'test_prediction_artifact.py' -v`:
  6 passed; [log](test-prediction-artifact.log).
- `-m unittest discover -s scripts -p 'test_reference_comparison.py' -v`:
  7 passed; [log](test-reference-comparison.log).
- `-m unittest discover -s scripts -p 'test_eval_run013.py' -v`:
  10 passed; [log](test-eval-run013.log).
- Offline `swift build`: passed, no compiler warnings; [log](swift-build.log).
- Offline `swift test`: 14 XCTest + 109 Swift Testing tests passed, no compiler
  warnings; [log](swift-test.log).

Tests cover null unsupported metrics, AP at different localization thresholds,
valid empty versus failed predictions, frozen image/label integrity, corrupt images,
duplicate/missing membership, altered settings/checkpoints/dimensions, taxonomy
mismatch, output collisions/boundaries, and source-backed preparation into disjoint
withheld/addon populations whose union is the complete manifest. Rejected preflight
retains diagnostic evidence without a freeze or inference.

Swift commands used host-approved execution, `--disable-automatic-resolution
--manifest-cache local --cache-path .build/ios-retention-check/cache --config-path
.build/ios-retention-check/config --security-path .build/ios-retention-check/security`.
TMPDIR was the absolute project `.build/ios-retention-check/tmp`; both
CLANG_MODULE_CACHE_PATH and SWIFT_MODULECACHE_PATH were the absolute project
`.build/ios-retention-check/module-cache`. No simulator, Xcode build or network
resolution was invoked. Python configurable caches/temp are project-local under
NativeUITrainer; synthetic test fixtures are cleaned from owned `.build/debug-output`
directories. No source data or checkpoints are modified.

## Reproduction

The three CLI stages are `scripts/eval_run013.py prepare`, `infer`, then `report`.
They use the explicit pinned checkpoints, not legacy evaluator defaults. Existing
outputs are rejected. For a deliberate reproduction use a new project-local output
directory with `--output`; do not overwrite this evidence or rerun inference merely
to reformat a report. Preparation freezes evaluator hashes and runtime versions;
inference/report reject drift. The manifests' `inputs` symlink points to retained
project-local r7 pixels and labels; the manifests are identities, not an independent
backup of those bytes. Moving/deleting the data invalidates replay.

Preparation completed in219.9seconds: all19,740 image/label pairs passed, with zero
decoded duplicate groups and zero cross-split pixel groups. Expected addon family
overlap is explicitly recorded, not treated as a withheld-family pass.

Execution receipt: restricted Codex shell → pinned venv → MPS availability check
failed before inference ([log](inference.log)); same approved command with scoped
host access → MPS available ([host log](inference-host.log)). No CPU fallback,
permission changes, device restart or source/checkpoint mutation was used.

Coordination: not applicable. This local iOS tranche does not change TTR's next
action and does not acquire hardware or require Photos dialogue data.
