# Focus Transition49 — integrated handoff

October 3, 2026. Separate from single-frame FocusRing and full-screen detector work.
Software/audit complete; real candidate training remains data-blocked. No capture,
training experiment, export, production change, external-repository edit or Git write.

## Delivered

- `focus_transition_learning.py`: source-pinned inventory, guarded per-control/action
  baseline, exact-member admission, group/endpoint/decoded-pixel leakage checks,
  deterministic three-class paired-measurement head and actual two-frame prediction
  adapter using existing pixel tracking and production crop measurements.
- Existing experiment dispatcher/trainer accept the new arm; ordinary static training
  rejects the temporal manifest. Planning loads no model or runtime service. Launch
  requires bound admission, execution record, experiment log and isolated output.
- Labels/after rectangles never enter predictor inputs. Missing absolute measurements
  have an explicit mask. Missing/unsettled context, incomplete predictions and unknown
  controls cannot create complete-action success. No public Swift API was added.
- Independent companion outcome: reconciled retained action accounting, rejected
  movement trials and complete-scene versus subset scores, without new inference.

This first learner is a softmax head over ordered paired-pixel measurements, **not**
a new image encoder, CoreML export or qualified navigation model. Unit-test numerical
fits and a generated execution receipt verify software only.

## Retained evidence and baseline

17 usable action pairs; four native movement cases remain rejected.82 control records:
72 unchanged, two arrivals, two departures, six unmatched.65 records have usable
features and labels. All genuine switches belong to one exposed Settings journey.
The accepted native transition34 corpus supplies no actual switches.

| Scope | Scorable | Correct | Wrong | Abstained |
|---|---:|---:|---:|---:|
| Control comparisons | 76 | 55 | 0 | 21 |
| Complete-screen actions | 0 | not available | not available | 17 |

Reviewed-subset action decisions:11 truth-scorable of17, four correct;13 predictions
abstain overall, including unscorable subsets. This is not complete-screen navigation
accuracy. No results establish generalization to unseen apps or journeys.

Original reports remain unchanged:

- Settings23 `retained-final/result.json` SHA256
  `0c569110967f68874cc0e44c2a5ee903385f38c4abec7e7094b7881fa8933d97`.
- Native34 `replay-final/audit.json` SHA256
  `d45cb85b9ab05a97b478dcdfdcb97452565a19b9fa88fa5f95bc1cb1785779b3`.

Local artifact paths below are intentionally gitignored; concise evidence stays here.

- `inventory-final/audit.json` SHA256
  `0b5a23d3f0a9ef8fcb9cc0a802708edf143ee17eea9f8a845feb1f7c09547ef5`.
- `inventory-final/protocol.json` file SHA256
  `c17f7d0c28e738cc2cc285f661e3e76763e90c2cd087bdf01aee9380f02f18dd`;
  protocol identity `7a9f9f9729375328bc1ed216c8659fa58743fe2ec0f40bf2c2c692f2c5d0748a`.
- `preflight.json` SHA256
  `ab355202b5a8022b09f7b6f42bd4011a0bfa02e6c25102e915ac24a41c16d8f5`.
- Initial `inventory/` is superseded by `inventory-final/`, retained rather than erased.

## Verification

- Inventory CLI on `sources.json` → `inventory-final/`: exit0, hash-checked native
  input references and decoded endpoints; Settings report replay retains its original
  seal without claiming a new raw-frame replay. Settings raw pixel references remain
  additionally required for training admission.
- Actual trainer `--experiment-protocol .../inventory-final/protocol.json
  --experiment-arm transition-measurements --name focus-transition49-candidate
  --preflight`: expected exit2, configuration valid, launch ineligible. Missing exact
  role admission, train/development class support and bound execution record.
- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts .venv-yolo/bin/python -m unittest
  test_focus_transition_learning test_focus_learning_experiment
  test_focus_scene_transition test_focus_paired_experiment test_settings_focus_stability
  test_focus_recorded_comparison test_focus_corrected_transition_audit`: exit0,
  78 tests in2.844s (16new). Generated prediction-service boundaries, not live capture.
  Log `.build/transition49-python-tests-final.log`, SHA256
  `a7611749f0b6f0e59c1e992f1b3c6ea3e48b4d306d66233d4883e2886e09e46a`.
- Offline `swift build --skip-update --cache-path .build/transition49-spm-cache` and
  equivalent `swift test`: exit0, build6.20s,14XCTest+120Swift Testing checks pass.
  TMPDIR and Clang/Swift module caches explicitly redirected into `.build/transition49-*`.
  Initial default-cache and nested-sandbox failures are retained in separate logs;
  scoped escalation resolved the sandbox restriction, without code/signing changes.
  Build log SHA256 `24f24b993aa2a809251cdbaa6a263f191bbf8a2080a9c9717ef8c91b17e6c211`;
  test log SHA256 `fe1f401264312682febd1497151c91b62b59c37c24a74fe4140da02cfd549a8c`.
- `git diff --check`: pass. Existing repository changes were absent at tranche start;
  preserved all existing artifacts, roles and unrelated task entries.

## Outcomes and exact next tranche

Software: verified. Real training data: **not admitted**. Producer integration:
unchanged diagnostic-only/partial prior evidence. Model gates: **not assessed**.
The assignment's conditional model execution cannot run honestly on this membership.

1. Resolve existing request `nuiak-20261002-transition34-native-readiness`; don't ask
   for another build-only handoff or retry unchanged rejected frames.
2. Freeze independent journey/recipe-ancestry groups with genuine moves and no-op,
   content-change and scroll negatives. Require observed identities/geometry, complete
   candidate accounting, raw endpoint hashes, reviewed labels and decoded-pixel checks.
   At least two move-bearing groups is a minimum split condition, not sufficient
   generalization evidence. Hold future final evaluation groups outside development.
3. Obtain exact-member training/development admission and any new capture authority.
   Then log and execute one fixed30-epoch comparison versus the same guarded baseline.
   Preserve all failures and abstentions; no automatic retraining or promotion.

TTR coordination is published/read back in `nuiak/status.yaml`, packet
`FOCUS-TRANSITION-49`, on verified `smb://sillycon.local/SharedStatusFile` at07:31:26UTC.
Reused request34 with additional coverage requirements; preserved all95previous packet
entries and top-level data by parsed-object hash check. No new peer acknowledgment
verified, no capture authority conveyed. No data/images crossed the share.
