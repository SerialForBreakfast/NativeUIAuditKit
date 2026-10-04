# Region112 — reviewed admission and rejected DTM028 comparison

Completed full95label visual review, exact94transition training admission and one
600epoch change-head comparison. Agent visual transcription matches every native
label. Four hash-bound contact sheets show original focus strips with adjacent-row
context; first full frame establishes layout. Inspection strips are not model crops.
All model inputs remain original full frames through the existing192×128 encoder.

## Results (confident correctness at unchanged0.15/0.85 thresholds)

| Group | DTM025 | DTM028 | Candidate abstentions |
| --- | ---: | ---: | ---: |
| Existing108training transitions |106|97|6|
| Region94training transitions |0|26|68|
| Related/exposed Settings5 |5|4|0|
| Existing122identical negatives |122|117|5|
| Region95identical negatives |95|0|95|

Reject DTM028. Preserve DTM025 and the shipped models. All94Region transitions are
visually supported identity changes; now they are training, not independent tests.
DTM028gets79raw Region decisions right, but that does not waive68abstentions.
Eight of nine lost old successes were negatives. All new identical pairs score
0.2330–0.2557 despite containing no difference. Context shortcut or insufficient
separation is a hypothesis, not proven causality. No repeated fit or threshold tuning.

## Reproducibility and verification

- [Admission decision](admission.md) and [visual transcription](visual-labels.txt).
  Source manifest/every image bound in ignored `artifacts/ready02/admission.json`.
  No precision-box/FocusRing-crop admission. Whole Settings ancestry excluded from
  final evaluation; existing five Settings examples are related-domain diagnostics.
- `region112_experiment.py prepare --ready reports/work/REGION-REVIEW-112/artifacts/ready02`;
  execution uses `execute` with the same path. Existing `fit_change_head` does fitting;
  no new architecture, optimizer, cropper or external dependency.202original/217
  derived training examples,CPU2threads,Adam0.0001,seed42,600epochs,fixed-last.
- ProtocolSHA256 `0915f76ef6c1547e3bd8894c57d521c306a7b0f63072dfe9e7a4bb9c93a5a386`.
  Registered DTM028 before launch; PID86026,exit0;fit319.139s,total321.286s.
  First preparation13.88s; repaired preparation preserves old attempt and source pins.
- Checkpoint `NativeUITrainer/focus_ring_runs/region112-dtm028/last.pt`,SHA256
  `84708ff404a57c282a744431735ce0f6b06e1eca6cfb9748dcb792db6e41b55b`.
  Frozen geometry weights and exact checkpoint replay pass. Initial old113probabilities
  match retained DTM025 within4.48e-8.419encoded inputs have415distinct byte tensors,
  zero opposite-label exact collisions; all217derived pairs are identical endpoints.
-34Python tests pass:derived98,collection104,shadow111,shadow_feedback_contract.
  Existing trainer loss/frozen-weight tests reused. Actual execution verified positive
  path, preflight rejection and post-run collision rejection without checkpoint change.
  Offline Swift build/test pass14XCTest+123SwiftTesting; logs `.build/region112-*`.
- Two pre-training failures preserved: bounded-reader default32MB rejected old66MB
  inputs (fixed explicit64MiB bound); diagnostic-only output helper rejected model
  run path (fixed existing model allocator). No training occurred in those attempts.
  No capture/setup, USB migration, external wait, model export or Git write this tranche.

Software verified:passed. Data eligible:exact reviewed change-only training subset.
Integration:retained producer evidence only, no live hook qualification. Model
development retention gates:failed. Production gates:not assessed; no promotion.

## Next substantial tranche

Run an error-localization/input-evidence audit on these existing tensors: distinguish
focus-local text/appearance change from unrelated content motion and global image
context. Freeze one justified retention-aware comparison only after that diagnosis.
Request TTR retain real same-focus motion/no-op examples and separately designated
unseen screen/layout journeys; do not randomly split adjacent Region frames. Existing
derived negatives cannot substitute for those qualification cases. Geometry109
source correction and optional-module integration remain independent workstreams.

## Coordination

Published/read back `nuiak/responses/nuiak-20261004-region112-reviewed-fit-v2.yaml`
and own REGION-REVIEW-112 entry on verified SharedStatusFile. Version2 adds missing
message timestamps; original publication remains preserved, not overwritten.
Exact local response bytes and duplicate-key-rejecting YAML validation pass.
Peer acknowledgment remains unverified. No images or new weights transferred;
TTR is explicitly told not to adopt the rejected candidate. Existing request ID
retained, with negative coverage and independent-group needs attached.
