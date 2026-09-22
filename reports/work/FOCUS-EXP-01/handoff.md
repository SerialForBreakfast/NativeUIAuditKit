# FOCUS-EXP-01 — completed for review, 2026-09-22

## Outcome and recommendation

Completed the authorized native-focus learning experiment independently of TTR:
34 new reviewed pairs,46 total with the prior Root group, four8-epoch training
arms, shipped-model reference and initial-checkpoint runtime comparison.
Keep production stretch crops and prefer warm initialization for the next
controlled experiment. Fine-tuning learned this row style sooner; aspect-fit
provided no demonstrated advantage. No model, public API or default preprocessing
was promoted/changed. The scope is development learning, not release qualification.

At fixed threshold0.85 on18 validation crops (9 Accessibility pairs):

| Artifact/arm | TP / FN / FP / TN | Selected epoch | Validation BCE |
|---|---|---|---|
| Unchanged shipped CoreML | 0 / 9 / 2 / 7 | not applicable | not computed |
| Initial FDR-001 PyTorch, production crops | 0 / 9 / 1 / 8 | before training | 0.825865 |
| FDR-006 warm + stretch | 9 / 0 / 0 / 9 | 7 | 0.0000125763 |
| FDR-003 scratch + stretch | 9 / 0 / 0 / 9 | 8 | 0.0234107 |
| FDR-004 warm + aspect-fit | 9 / 0 / 0 / 9 | 5 | 0.000692525 |
| FDR-005 scratch + aspect-fit | 0 / 9 / 0 / 9 | 8 | 0.825227 |

Warm arms achieved18/18 at epoch1; scratch+stretch first did so at epoch7.
Scratch+aspect-fit ranked examples perfectly (AUROC1.0) but failed the fixed
thresholds. Ranking alone is not usable focus decision performance. All selected
trained arms have the same confusion counts at0.5 as at0.85. Shipped CoreML at0.5
is TP5/FN4/FP4/TN5. No threshold was tuned to rescue a result.

The initial PyTorch checkpoint and shipped CoreML probabilities differ: mean
absolute0.004849, maximum0.016776; one decision differs at each threshold.
This compares MPS PyTorch with CPU CoreML, not a controlled attribution to FP16,
export or device. Exact runtime parity is **not** established. Do not silently
substitute these artifacts when reporting historical results.

## Data, lineage and scope

- Exact simulator: `9026ECA9-77DB-4AE6-8FE6-BB239E9571FA`, tvOS26.5/23L470,
  Apple TV4K3rd-generation4K,3840×2160 captures; no Office or TTR operation.
- Training:12 existing Root pairs +25 General pairs =74 crops.
- Validation:9 Accessibility pairs =18 crops, assigned before model scoring.
- All pairs/related frames in a screen lineage stay together. Fresh raw-telemetry
  reconstruction, source hashes, PNG decoding and zero exact pixel overlap across
  train/validation were rechecked before launch and during final reporting.
- This is **same-app, same-style screen-group validation**, not unseen-app/style,
  physical-device or final-test evidence. Validation selected checkpoints. Only
  nine correlated pairs support the validation metrics; no confidence/reliability
  claim or6,000-pair qualification follows from18/18.
- Native observed focus and measured bounds provide labels. Requests and model
  predictions do not. Detector proposals/model-driven navigation were not tested.
- General trial01 reached its40-input budget before the redundant reverse leg;
  Accessibility trial01 expected an absent VoiceOver row. Both remain failed,
  excluded evidence. The latter page was passively inspected before correcting
  the entry marker to its actual Hover Text row. No setting/value was selected.
- Successful General02:26 capture directions,2 boundaries,27 observations,
  25 pairs, verified return to Root. Accessibility02:10 directions,2 boundaries,
  11 observations,9 pairs, verified return. Exact runner hashes are retained in
  each trial's `runner-hashes.txt`; scene checks/postflight are in raw attachments.
- All default crops visually reviewed, including disabled text, adjacent focus
  treatment, clipping and row stretching. Aspect-fit uses the same production
  crop geometry and a tested opt-in scaling branch; a padded representative was
  inspected. Review receipt: `review.md`; source inventory: `sources.json`.

## Frozen artifacts

- Canonical protocol content SHA256:
  `cec58e37c4f0a181acf20fc484c5bcce75cf8c059f1d64cdfb44664d6a2fe414`.
- `corpus-01/protocol.json` file SHA256:
  `1fbd27026bf5d66f61ed892a4ebb5e6a1f0b7de76f738a4309668e1319d48ac8`.
- `comparison.json` file SHA256:
  `0503e3a8837d5ce71e26a2ed74f30ff20e085bdb069053730f44652ab2c55c5e`.
- Shipped CoreML artifact SHA256:
  `9e5ba294e545b4ae0c54aa5d483b1a1f681b6c30477882700b4dbe139b9c66b7`.
- Trainer SHA256:
  `a52737b7e9d95efd8d81afce1a07e31ac7e893ba55b3a0d3d3b41c8057adfa`.
- Full candidate/result hashes and predictions: `comparison.json` and
  `NativeUITrainer/focus_ring_runs/fdr{003,004,005,006}-*/experiment-result.json`.
  Warm source checkpoint, runtime helper/source identities, crop byte/pixel hashes,
  source manifests and review hashes are bound by the protocol.

Raw `.xcresult`, attachments, derived crops and checkpoints are retained locally
and gitignored; no pixels/weights are committed or uploaded. Maintainer owns their
retention. There is **no verified off-device backup**; an immutable manifest and
two local representations are not a disaster-recovery copy. Do not delete them
while using these candidates as evidence.

## Implementation and verification

Real entrypoints extended, not a second trainer/cropper:

- `NativeOSFocusTests`: bounded General/Accessibility sweeps, versioned screen IDs.
- `native_os_focus_dataset.py`: screen-specific admission and verified return.
- `FocusRingClassifier.makeCrop` / `FocusRingTool`: package-only opt-in aspect-fit;
  old/default stretch is byte-identical in its regression test.
- `focus_learning_experiment.py`: hash-bound source review, fixed screen grouping,
  crop preparation, experimental eligibility; ordinary production gates unchanged.
- `train_focus_ring_detector.py`: isolated experiment entrypoint, strict warm load,
  same training loop, finite checks, histories/predictions and selected checkpoints.
- `focus_learning_report.py`: compatible membership/results, reference inference,
  decoded-pixel-aware batching and diagnostic metrics.

Commands/results:

| Check | Evidence | Result |
|---|---|---|
| Offline `swift build` | `swift-build.log` | exit0,2.58s |
| Offline `swift test` | `swift-test.log` | exit0,93 tests,2.551s test runtime |
| `python -m unittest discover -s scripts -p 'test_focus*.py'` | `focus-tests-final.log` | exit0,60 tests |
| `python -m unittest discover -s scripts -p 'test_native_os_focus_dataset.py'` | `native-tests-final.log` | exit0,15 tests |
| Native General test-without-building | `general-02/execution.log` (exact command) | exit0,52.574s test runtime |
| Native Accessibility test-without-building | `accessibility-02/execution.log` (exact command) | exit0,18.920s test runtime |
| Actual native intake CLIs | successful trial `intake.log` | exit0,25/9 pairs |
| Protocol preparation | `prepare.log` | exit0,92 samples/two crop variants |
| Logged training launches | `run_remaining.py`, `execution.log`, individual logs | four exit0,8 epochs each |
| Real reference/comparison CLI | `comparison.log`, `comparison.json` | exit0,hash/membership checks pass |
| `git diff --check` | final working-tree check | exit0 |

All Python commands use `.venv-yolo/bin/python` and `PYTHONDONTWRITEBYTECODE=1`.
Preparation command arguments are preserved in the canonical plan/source inventory;
`run_remaining.py` records exact training commands and exclusive outputs. It is
one-shot, not safe to rerun against existing outputs. Final report command:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv-yolo/bin/python scripts/focus_learning_report.py \
  --protocol reports/work/FOCUS-EXP-01/corpus-01/protocol.json \
  --output reports/work/FOCUS-EXP-01/comparison.json
```

Choose a new output for any separately requested replay; existing evidence is immutable.
Tests cover tampering, missing/unreviewed sources, versions, labels, group/pixel
leakage, collisions, production-preflight preservation, crop defaults and4K batching.
No package code changed after the successful integrated Swift checks; subsequent
Python/report changes received focused checks rather than another identical build.

## Runtime failures and efficiency

FDR-002: PID72087,600s,exit143 from its verified owned-process watchdog; cold
torch import,zero epochs/checkpoints. Preserved, not called a model failure.
Warm import then took0.717s, but optimizer initialization lazily read cold SymPy.
Stack/open-file samples and bounded read-only probes are retained. No reinstall,
download, daemon restart, signing repair or permission weakening occurred.
MPS scalar check passed; standard OS-managed Metal cache received scoped host
approval. Explicit artifacts/configured caches remain project-local.

Successful process wall times (including≈10s source preflight each): FDR-006419.131s,
FDR-00319.995s, FDR-00419.567s, FDR-00519.300s. Post-preflight times are in results.
Fine-grained import/optimizer/epoch timing was not instrumented; do not turn these
wall times into an initialization-method speed benchmark. No TTR/external wait.
First oversized CoreML batch failed safely; pixel-bounded9+9 inference succeeded.
BP-69/70 preserve both observed workflow lessons.

## Independent outcomes and next action

- Software verified: yes, integrated experimental path and required checks.
- Data eligible: yes **for this reviewed development experiment only**; production
  dataset readiness remains false. Legacy fixture crops were not reused as training.
- Integration qualified: native capture→intake→crop→PyTorch training/reference
  reporting for this exact scope. No TTR, candidate CoreML export or navigation claim.
- Model gate passed: **not assessed**; no final-test/release/promotion decision.

Next proposed tranche: freeze a genuinely different native Home/style challenge
set, especially bright unfocused tiles/cards and alternative focus treatments;
benchmark unchanged shipped and FDR-006 artifacts before further training. Keep
its screen/journey groups separate and reserve untouched final groups before any
model selection. Separately isolate CPU/MPS/export probability differences before
candidate CoreML qualification. Qualified Fixture/TTR light/high-contrast examples
and retention checks add complementary evidence when available, not a prerequisite
for this native challenge. New capture/training/export needs its scoped assignment.

Tasks.md is the only ownership/status queue. Coordination: **not applicable**;
this local experiment changes no producer interface or peer action, so no SMB noise.
Existing unrelated iOS reconstruction, TTR/direct-lane, skill and documentation
edits were preserved. No git writes or external-repository edits.
