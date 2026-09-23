# FDR-008 — 30-epoch mixed-appearance development run

| Outcome | Evidence |
|---|---|
| Software verified | Existing trainer/preflight63-test evidence unchanged; offline Swift build/test passed again. |
| Data eligible | Approved bounded development use:126 train pairs /nine native-validation pairs; no production approval. |
| Integration qualified | Local MPS training and same-membership Torch CPU comparison completed; no new TTR or CoreML integration claim. |
| Model gate passed | Not assessed. No independent Fixture test corpus or physical qualification; shipped model unchanged. |

## Result

All30 epochs completed, exit0. Frozen checkpoint selection chose **epoch3**, not
the final epoch. Best native-validation BCE0.000002755059. Same-backend CPU
comparison at fixed0.85:

| Membership | FDR-007 | FDR-008 selected |
|---|---:|---:|
| Fixture training crops |129/172 (75%)|172/172 (100%)|
| Native training crops |80/80|80/80|
| Native validation crops |18/18|18/18|
| Reused native Remotes challenge |12/12|12/12|

Fixture false negatives43→0 with zero false positives before/after. At0.5,
Fixture accuracy77.33%→100%; native decisions unchanged. Detailed per-theme/control
support, predictions, metrics and checkpoint hashes: `comparison.json`.
The improvement is on **training members**, not unseen examples. Small correlated
native sets show no observed forgetting, not broad retention proof. The historical
shipped Remotes score5/12 is retained as labeled prior evidence, not newly inferred.

## Execution and configuration

User explicitly authorized the proposed30-epoch run. `approval.json` binds the
decision to protocol `fa1c7cffa8e42aac511353c9ccd99cf091dbf25a05cb3f5deba52e1ac458fca2`,
arm warm-stretch and output `fdr008-mixed-appearance`; ExperimentLog recorded it
before launch. PID11340,03:36:54–03:39:59Z;184.453s process including fresh
preflight,38.399s post-preflight. No retry. Exact command: `execution.json`.

Vendored MobileNetV4, warm FDR-007 with fresh AdamW,30epochs/batch64/lr0.0003/seed42,
no augmentation, production16%/256 preprocessing. Existing stratum sampling retained
(expected88.89% Fixture/11.11% native). Cooperative1800s budget; external2100s cap.
Torch2.7.0/MPS in the approved isolated environment; prior FDR-007 trained with2.13.0.
Before/after diagnostics both reran on current Torch CPU. This is not a causal
data-only ablation and no export parity is claimed.

Best checkpoint:
`NativeUITrainer/focus_ring_runs/fdr008-mixed-appearance/weights/best.pt`.
SHA256 `40f23078e0ca5b5b03ac2bc52b6f1c10e9477687a99b26fac327e8199d75d11c`.
Last checkpoint and all epoch losses preserved beside it. Evaluation rechecked
crop bytes and challenge source/runtime/lineage isolation against all experiment
frame/crop pixels. Challenge never selected checkpoints.

## Verification, preservation and next action

`run.py` exited0 and retained the log/ledger; `evaluate.py` assertions passed and
reported frozen-threshold metrics without tuning. `verification.json` records
offline Swift build/test exit0;14 XCTest and93 Swift Testing tests. Existing63
Python integration tests cover unchanged production code; no redundant full Python
rerun. New scripts are project-local execution/reporting, not library changes.
No images displayed; no capture, external repository edits, git writes or promotion.
Original source pixels, failed receipts and prior models/reports preserved.

Next: evaluate this fixed checkpoint on retained Home/Photos appearance diagnostics
and obtain independently qualified Fixture challenge groups before judging
generalization. Do not launch another same-data run just because30 epochs are
available. Any new capture/export/training is a separately scoped assignment.
SMB coordination not applicable: no peer request, contract or runtime status changed.
No process remains running. The authorized run/report slice is complete for review.

Worker-execution required the logged single-run boundary and evidence-backed
handoff; model-workflow guided isolated outputs, production preprocessing, fixed
evaluation and preservation of shipped assets.
