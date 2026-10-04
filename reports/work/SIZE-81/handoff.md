# SIZE-81 — size-aware comparison and coverage audit

One authorized DTM019 comparison completed; no capture, export, promotion or Git
writes. Existing dirty-worktree changes and all prior evidence preserved.

## Results

| Membership | DTM017 endpoints | DTM019 endpoints | DTM019 paired |
|---|---:|---:|---:|
| Original training (32) | 64/64 | 64/64 | 32/32 |
| Added native training (12) | 24/24 | 24/24 | 12/12 |
| Exposed Settings development (5) | 1/10 | 2/10 | 0/5 |

No abstentions. Primary comparison retains DTM013 change control: 40/44 joint train
pairs. Separately combining DTM018 change decisions gives 44/44 train and 0/5 Settings.
These are development results, not independent evaluation or reliable navigation.

## Implementation and controlled inputs

Existing ranker gains normalized candidate width/height, not position, app identity
or labels. 770→32→1 network; common seed42 visual weights copied exactly, new columns
zero-initialized. Same 44/5 roles, 83 images, 2337 candidate encodings, 74 unique train
frames, 600 epochs/full batch, Adam .001, CPU two threads, fixed-last checkpoint.
Existing preparer, trainer and replay entrypoints extended; no new cropper/trainer.

Preparation 0.386925s, fit 1.414892s, full execution 2.591725s. PID44805, exit0.
Zero new crop invocations; no external wait or capture needed for this comparison.
Protocol: 369eb295a5dce5a8be4b3cfbc00bd5f8bad6c1f7f4805c27ab5a2ae128ac63f3.
Checkpoint: d1058de1e75cd685f4a8fbe4821535b743cef4bc0d60e36c9f4a72337df284a6.

## Independent coverage companion

Deduplicated frame/candidate counts: train positives136 (zero below100px largest
extent), negatives1978 (154 below100px); development positives9 (zero below100px),
negatives214 (90 below100px). Overlapping proposals remain correlated. This bin is
descriptive, not a minimum-size rule. Small actual controls require coverage before
we can conclude that rejecting small proposals is safe.

Zeroing the two size features on the frozen DTM019 checkpoint reduces Settings
2/10→1/10 while training remains88/88. This out-of-distribution diagnostic suggests
the model uses the inputs; it does not demonstrate robust generalization.

## Verification and evidence

- 21 Python tests pass (1.506s): test_size81, test_rank75, test_batch79,
  test_change80, test_native77. Covers shape/finite/bounds rejection, normalized
  geometry, initialization parity, legacy behavior, reload and cache/admission guards.
- Offline Swift build and 134 tests pass (14 XCTest + 120 Swift Testing).
- Actual saved checkpoint replay and candidate-order parity pass.
- Automated artifacts: ready/, completion.json, replay.json, combined.json,
  size-ablation.json, coverage.json in this directory; model/result in
  NativeUITrainer/focus_ring_runs/size81-dtm019/. Raw artifacts remain ignored.
- Logs: .build/size81-{prepare,training,replay,tests,swift-build,swift-test}.log.

## Coordination and next tranche

Published coverage follow-up to verified SMB:
`nuiak/responses/nuiak-20261004-size81-coverage-followup.yaml` and owned
`packets.SIZE-81` in `nuiak/status.yaml`. YAML readback passed; unrelated status
digest unchanged (64a4a639c3f337c093205377652e949ce3c4c98f3504f04e66abacf2536f38c2).
Existing request nuiak-20261003-transfer62-stationary-compatibility retained;
peer acknowledgment not established. No duplicate capture assignment issued.
Uses the repository SharedStatusSkill.md metadata-only, owned-entry/readback protocol.

Next substantial outcome: qualify retained rich24 against published producer source,
reconcile grouped coverage with true small controls and large-row/distractor cases,
reserve genuinely independent evaluation groups, then prepare the next bounded
candidate. Source publication remains the rich intake blocker; do not recapture
retained evidence or claim that approval substitutes for runtime/label verification.

Software verified; existing development-training eligibility preserved; local
experiment integration verified; independent/production model gates not passed.
Maintainer execution approval is recorded, but no promotion is justified by 0/5 pairs.
