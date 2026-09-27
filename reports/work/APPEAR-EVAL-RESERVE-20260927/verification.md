# Verification and execution receipt

2026-09-27; user-approved local intake, validation-only inference, necessary
consumer/evaluator changes and candidate preparation. No training, device operation,
challenge scoring, export, promotion, Git write or external artifact transfer.

## Software

- 105 focused/integration Python tests pass (`final-integration-tests-passed.log`).
  Modules: test_focus_runtime_replay, test_focus_surface_evaluation,
  test_ttr_sidecar_v2, test_ttr_appearance, test_focus_visual_comparison,
  test_focus_appearance_experiment, test_focus_runtime_batching,
  test_focus_mixed_assembly, test_focus_consumer_integration,
  test_focus_development_experiment and test_focus_appearance_proposal.
- Offline `swift build`: pass, zero compiler warnings (`swift-build-final.log`).
- Offline `swift test`:14 XCTest+109 Swift Testing pass, zero compiler warnings
  (`swift-test-final.log`).
- Surface regressions cover four producer recipe vectors, closed fields/versions,
  real native-bracket intake, preserved recipe-bucket splits, changed source/membership,
  corrupt/missing pixels, unsafe archive members, pixel leakage, incomplete candidate
  sets, all four focus decisions, unavailable Photos support, invalid/incomplete
  predictions, protocol drift and unconditional final-challenge scoring rejection.
- Existing reservation-v2 tests cover source/membership binding, reused/related
  evaluation, unsupported reservations and changed checkpoints. The actual new
  sources remain unadmitted, not synthetic-positive-test qualified.
- Runtime replay tests reject missing/changed pixels, input/source/runtime drift
  and changed reconstructed membership. Scope restoration and unchanged default
  strict behavior pass. Actual460-crop replay and actual assembly supplement tests.

The first surface test expected the wrong error for an explicit v1 schema marker;
fixed it to exercise genuine absent-marker legacy input. A later integration run
exposed mocked runtime-provider boundaries changed by the new helper; preserved the
existing injected provider and reran all105 tests. Both failed logs are retained,
not reported as passes. No source/data gate was lowered to satisfy a test.

## Actual entrypoints

All commands ran from the package root. New destinations reject collisions.

1. `scripts/focus_surface_intake.py extract`: all four archive hashes, bounds,
   paths/types/counts and storage reserve pass; AppleDouble metadata excluded from
   extraction but accounted for. `extraction.log` and extracted `extraction.json`.
2. `scripts/focus_surface_intake.py intake`:96/96 rows accepted for diagnostics;
   strict raw exports, native observations, four-endpoint capture brackets and
   complete geometry validated. `intake.log`, `intake/{group,intake}.json`.
3. `scripts/focus_surface_evaluation.py prepare`:1,344 production crops including
   192 paired crops for all96 pairs and1,152 validation competition crops. Challenge
   processing is crop/label QA only. `crops.log`, `crop-audit/crops.json` and four
   reviewed paired sheets. Pixels live in gitignored dataset storage.
4. `scripts/focus_surface_audit.py`: rechecked3,789 prior images and all current
   references; zero prior exact overlaps, cross-role pixel groups or contradictory
   crop labels. `overlap.log`/`overlap.json`. No source-independence assertion.
5. `scripts/focus_surface_evaluation.py freeze` and `run`: immutable protocol;
   shipped CoreML CPU and FDR007/008 Torch CPU load exact local artifacts. All3,744
   predictions complete; per-model files retained before aggregate report. Fixed
   threshold0.85, no perturbations. `freeze.log`, `comparison.log`, `protocol.json`
   and `comparison/`. Missing predictions cannot silently reduce membership.
6. Existing assembly and trainer preflight initially exit2 with
   `unsupported_or_changed_native_manifest` (`assembly.log`, `trainer-preflight.json`).
   The current classifier diff adds artifact identity metadata but leaves makeCrop
   unchanged. Assignment-local `replay_candidate.py` verifies all460 current crops
   exactly match the retained candidate; selection reference remains valid. It
   retains a byte-identical protocol copy, never edits historical metadata.
7. `finish_candidate.py` invokes the existing real assembly and trainer `--preflight`
   using an explicit hash-bound runtimeReplay input. Exact command/exit/timing
   records are in `candidate-execution.json`; the initial failed evidence remains
   separate. Preflight has been inspected: it returns before model imports,
   training or run-directory creation. `appearance-readiness-only` is a non-allocated
   preflight name, not a training run ID or authorization.
   Final observed results: assembly exit0 in225.10s; trainer preflight exit2 in227.09s.
   Configuration valid, counts442 training/18 retention,50/50 source mass; launch,
   execution and release authorization false. Ten independent-coverage blockers
   plus missing_experiment_approval remain. Protocol seal:
   `5674102f9d7fa0cd73d03770f53e51c5430e2822d047a443dd50e3b2519cb8da`.

## Execution context and preservation

Analysis/tests use resident `focus-export-01` Python3.12.9 consistently for model
and helper paths; no dependency reinstall or download. Simple receipt/source checks
also used the repository Python without model loading. Actual evaluation pins
Torch2.7.0, NumPy1.26.4 and Pillow11.3.0. CoreML/helper/test commands received scoped
normal-host approval for ordinary macOS runtime/cache access; explicit artifacts
and configurable TMPDIR/TORCH_HOME/MPLCONFIGDIR stay project-local.

Swift uses `--disable-automatic-resolution --manifest-cache local` and project-local
cache/config/security/module-cache/TMPDIR paths under `.build/focus-surface-check/`.
No simulator, Xcode external build system or network resolution is used.

Received originals, old manifests, retained checkpoints and shipped resources remain
unchanged. No producer files or shared copies are removed. At16:58Z the filesystem
reported~42.30GB available; extraction/crops did not require cleanup.
Shared metadata publication is separately recorded in coordination.md. A disconnected
share does not block completed local work and is not a request for recapture.

## Final readback

`final_verify.py` completed successfully with output `final-verification.json`.
It validates the sealed protocol/runtime/implementation/model/input hashes without
inference, recomputes all metrics from retained probabilities, verifies3,744/3,744
predictions and zero challenge scores, and compares all460 candidate rows, sampling,
selection, initialization, configuration and lineage to the original assembly.
The historical manifest's byte-identical copy and hash-bound preflight are intact;
no appearance-readiness-only training directory exists.

Actual frame accounting is192 distinct file paths but100 distinct byte hashes for
96 pairs. Repeated within-role baseline images are not independent observations;
the absence of cross-role overlap is a separate check. The final checker initially
expected a boolean model-gate field; corrected its assertion to the evaluator's
explicit not_assessed value (the diagnostic evaluator never claims qualification).
No frozen evaluator, predictions or protocol was altered for that correction.

Duplicate-key-rejecting safe YAML readback passes. After removing only the newly
owned APPEAR-EVAL-RESERVE entry, canonical status content matches the pre-edit hash
`2ec2f0b8594c36cf10f1aa2039a13ab889fb326b000dba209d42c7d4926eaea8`.
Other owners and top-level fields are preserved; their historical stale claims are
not refreshed. The owned entry is explicitly unpublished. `git diff --check` passes;
new raw data, crops and frozen JSON artifacts match existing gitignore rules.
