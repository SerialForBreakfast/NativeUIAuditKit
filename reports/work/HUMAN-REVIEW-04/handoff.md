# HUMAN-REVIEW-04 — complete for review

2026-09-28. Base `a7eb2868b482f24b3d19b3dc20673a15583a6719`; checkout clean at start.
No git writes. Owner: current NUIAK review-tool worker.

| Outcome | State | Evidence |
|---|---|---|
| Software verified |Pass|New explicit adapter/CLI,154 generated-fixture Python tests; offline Swift build/123 tests|
| Data eligible |Pass, development-only|8 reviewed frames/113 controls/2 explicit pairs; original diagnostic flags unchanged; training and independent evaluation remain ineligible|
| Integration qualified |Pass, local comparison only|Actual frozen CLI run,113/113 scores from each exact model, CPU receipts, epoch3 load, unchanged-input postflight|
| Model gate passed |Not assessed|Candidate regresses:1/8 positives and15 false positives versus4/8 and11; no independent/full-frame qualification|

See [results](results.md) for metrics and numbered error evidence, and
[next assignment](next-assignment.md) for prioritized collection. Shipped models unchanged.

## Acceptance map

| Criterion | Evidence |
|---|---|
| Explicit new human development policy, not flipped diagnostic flags |Research/schemas/human-focus-development-evaluation-v1.md; approval.json; protocol.json; legacy-loader rejection tests|
| Frozen human/source/pixel/crop/model/runtime/implementation binding |protocol.json,143 original input references; human Joe attestation; authorization.md|
| Actual training/retention/protected role check |protocol.overlap:564+1344+20 rows; no exact matches; ancestry unknown, historical frame-only gaps explicit|
| Every member/pair and duplicate retained |113 ordered rows,8 positives,105 negatives,2 pairs;111 unique-pixel sensitivity reported separately|
| Fixed production inference paths and loaded identities |comparison/shipped.json and fdr009.json:CPU receipts, checkpoint epoch3, exact artifacts; retained helper/crop identity|
| Complete predictions and failure handling |226 actual scores, zero failures/unscored; synthetic partial/nonfinite failure tests; no subset metrics on failure|
| Correct metrics without unsupported claims |comparison/comparison.json; results.md; frame selection unavailable; no inferred extra pairs|
| Error analysis and next assignment |37 numbered context/crop sheets; results.md and next-assignment.md|
| Preserved originals, reproducible counts |verification.json; independent offline metric replay; all original references and37 sheet hashes rechecked|
| Required verification |integrated-tests.log154 pass; integrated-swift-build.log exit0; integrated-swift-test.log14 XCTest+109 Swift Testing pass|

## Execution and reproducibility

`human_focus_evaluation.py freeze approval.json protocol.json`, `run protocol.json
comparison`, and `render protocol.json error-sheets --comparison comparison/comparison.json`
all executed successfully through their real CLI using the pinned resident Python3.12.9
environment. Exact settings/environment are in authorization.md and protocol.json.
Shipped inference phase≈2.52s and candidate≈3.47s include different load/batch paths;
these are execution-accounting times, not directly comparable production latency.
No second inference run. Approval's exclusive started marker remains present.

After successful execution/render, self-review added a fail-path hardening test:
non-finite engine scores must serialize as explicit invalid/unscored failures rather
than prevent the receipt from being written. No inference, preprocessing, successful
scoring or membership behavior changed. Exact executed source is preserved in
`executed-implementation.json`, verified against the frozen code hashes. The current
metric function's AST matches the executed one and reproduced all counts. The old
protocol deliberately rejects changed implementation for a new launch; do not repin
it or delete the launch marker to rerun. New code received154 tests and final offline
Swift verification. Original execution postflight passed before this hardening.
Retained rendering also now follows BP-106: it checks approved human pixels and
score bindings without model/runtime residency or protected-corpus traversal.
The actual CLI replay in the ordinary Python environment produced the same37 sheets
under `error-sheets-replay/`, without inference. New learning: BP-109 failure receipts.
Replay preserved all37 error identities/scores/order and decoded sheet pixels.
PNG byte hashes differ between Pillow11.3.0 and12.3.0 render environments; an initial
byte-equality assertion failed, then decoded-pixel comparison confirmed37/37 equal.
Original rendered files were preserved, not overwritten or silently rehashed.

Focused tests: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts .venv-yolo/bin/python
-m unittest -v test_human_focus_evaluation test_human_review_audit test_human_review_finish
test_human_annotation_review test_photos_focus_pilot test_focus_retained_review
test_native_os_focus_dataset test_focus_surface_evaluation test_focus_appearance_experiment
test_focus_visual_comparison test_focus_runtime_batching` (project TMPDIR).
Swift commands: `swift build`/`swift test` with `--disable-automatic-resolution`,
`--manifest-cache local` and project-local cache/config/security/module/temp paths.
Scoped host execution, no downloads, dependency resolution, device operations or installs.

## Boundaries and handoff

All acceptance items evidenced. No human review corrections are currently requested.
This was a single development test, not an independent exam or training run. Several
crop errors repeat the same artwork; only8 positive controls in one session. No claim
that training data alone caused the failures or that lowering0.85 would solve them.
Keep original frames, immutable revision, models, approval/protocol, predictions,
source snapshot and crops. No cleanup performed; no owned process remains running.

Next meaningful assignment: approve a separate matched-data collection/admission
tranche after the batch recorder path is ready. TTR coordination is not applicable:
the model finding supplies local data priorities but does not change TTR's existing
recorder/transport next action. No SMB publication or peer acknowledgment implied.
