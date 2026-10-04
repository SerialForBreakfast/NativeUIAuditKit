# REPAIR-100 — approved false-change comparison

October3local/October4UTC. DTM024 completed PID61874,exit0;600epochs with no retries.
Maintainer expressly approved122derived training negatives. Original68train/5exposed
development pairs unchanged; all TTR calibration remains unadmitted.

| Outcome | Evidence |
|---|---|
| Software verified |16Python tests; offline Swift build and134tests pass|
| Data eligible |122source-bound training-only self-pairs approved for this run; nine development frames excluded|
| Integration qualified |Real preparation/preflight/dispatcher/training, initializer parity, frozen geometry and checkpoint replay pass|
| Model gate passed |Development advancement criteria pass; production/independent-final gates not assessed|

## Controlled result

| Metric | Retained DTM018+DTM020 | Rejected DTM023 | DTM024 |
|---|---:|---:|---:|
| Original68confident joint |65|67|66|
| Original20no-ops confident correct |20|20|20|
| Identical-frame confident false changes /122 |0|35|0|
| Identical-frame abstentions /122 |0|8|0|
| Exposed Settings joint /5 |2|2|2|

DTM024has44/44old training and22/24added-native joint; the two remaining transitions
abstain. Wide-dark-s31-p2probability0.169763 and wide-light-s31-p2probability0.323501
remain below the unchanged0.85confidence threshold. Do not hide them by lowering it.
All122derived examples have raw unchanged predictions, no false changes or abstentions.
Nine excluded-development self-pairs also pass (max change probability0.00232918),
but these are exposed development, not independent-final evidence.

All four predeclared advancement criteria pass: zero confident derived errors,
all20genuine no-ops retained,66>=65joint original decisions, no Settings regression.
Relative to DTM023, repaired consistency trades one difficult-transition decision
for abstention. Relative to retained control, one more original pair becomes jointly
correct without losing original no-ops. This supports retaining DTM024 as a challenger,
not shipping it. Same-frame results after training are fit evidence; genuine changing-
content/boundary no-ops remain necessary. Shipped artifacts are unchanged.

## Execution and verification

Existing model workflow/dispatcher extended, not a parallel trainer.192×128nine-channel
context initialized from DTM018 with six extra channels zeroed;600epochs,Adam0.0001,
seed42,CPU2threads,fixed-last selection. Full190example batch; equal means for original68
and derived122. `batch=68` in inherited configuration binds original membership;
explicit originalGroupCount/derivedGroupCount define the190example optimizer input.
Frozen96geometry and DTM020ranker;2GiB output cap; approved no-wall-time override.
No MPS contention, capture, new backbone, export or promotion.

Fit145.450s,total146.641s;loss0.162520→0.032901. Protocol digest
`5785b6b4125b8838ebdcbe641955785e13fc32c43b0bd97d219148b48b9488e5`.
ModelSHA256 `7a482e8b651f2b1354a4dd47f39fbcaa21fee4b0515ee0f56e0fa9d0ed0edf07`.
Preparation under `ready/`; results/checkpoint/completion under
`NativeUITrainer/focus_ring_runs/repair100-dtm024/`. Training log
`.build/repair100-training.log`. ExperimentLog entry bound before launch.

Command: `scripts/train_focus_ring_detector.py --name repair100-dtm024
--experiment-protocol reports/work/REPAIR-100/ready/protocol.json
--experiment-approval reports/work/REPAIR-100/ready/approval.json
--experiment-arm transition-change-adaptation --experiment-id DTM024 --execute`,
using resident .venv-yolo/PYTHONPATH=scripts,exit0.
Focused `test_derived98`/`test_change80`:16tests pass1.190s, including equal-group
loss calculation and invalid grouping; geometry unchanged. Swift offline build/test
pass with scoped normal CoreML cache access,logs `.build/repair100-{build,test}.log`.
One optional post-run tensor diagnostic initially hit default file-size bound; rerun
with the existing protocol's explicit64MiB bound passed. No model rerun involved.

TTR local source remains50ff7fd8; user will update Git. No repeated request or local
training chatter published to SMB. Existing context60receipt remains the actionable
handoff; source-backed intake is independent. No Git writes, cleanup or source changes
outside NUIAK. Previous RANKING97/PREP98and other dirty changes preserved.

Next substantial tranche: qualify context60/layout28against published v16/v17,
audit genuine-negative and small-control coverage, propose exact training roles and
reserve genuinely separate native evaluation. Then one controlled comparison using
qualified new coverage; no unchanged extra epochs or automatic sweep.
