# FIT-61 — full training fit established; transfer remains open

October3,2026. Goal continuation. Preserved all pre-existing GEOMETRY-58/59/60 dirty
work at base24964ec. No Git writes, new data roles, capture, export or promotion.

| Outcome | Evidence |
|---|---|
| Software verified |43Python tests2.061s; offline Swift build/134tests pass |
| Data eligible | Unchanged24Fixture/train and5exposed Settings/development |
| Integration qualified | Actual trainer/evaluator/diagnosis and8checkpoint prediction CLI parity |
| Model gate passed | Training-fit passes24/24; transfer fails0/5localization; production not qualified |

## DTM009 controlled duration test

SameDTM008model/loss/data/preprocessing/seed/optimizer/fixed-last, epochs30→120.
Fresh initialization,120epochs/360updates,CPU2threads. Train paired boxes24/24,
raw change24/24,joint24/24,48/48cells,minimum endpointIoU0.75963. Cell CE0.035083,
geometry L10.008204,change BCE0.000920. DTM008had8/24paired and12/24change.
Full tiny-corpus fit is established; no independent generalization claim.

Settings5: paired0/5,raw change2/5,all5decided(allchanged),3false change decisions.
More duration did not fix transfer. No threshold adjustment or additional run.

PID19047 exited0. Protocol60ada4a814f1667e091596b3fef80fe9105c5841a08194a8feccfc9b4b54aa0a.
Checkpoint6838c641b17931b5b896e5c886e29714b1f39d4f15313b8c42c98a95cdaac85b.
Run3,551,878bytes under2GiB. Wrapper20.726s: intake15.728,fit4.860,checkpoint0.006,
scoring0.133. Initial CLI preflight is additional; fit includes tensors/optimizer init.
Timing components verified nonnegative. CPU warm median4.540ms,p954.671ms excluding
PNG load. No running processes or external waits remain.

## Compatibility and reporting deliverable

`compatibility-baseline.json` was sealed before edits while originalDTM007pins matched.
`prepare_fit61.py` verifies unchanged ASTs of twelve numerical functions, unchanged
spatial model/source dependencies, allowed reporting/registration/preparation changes,
and original source/result/checkpoint/evaluation hashes before reusing the4/4gate.
New protocol pins bind the changed wrapper. No old evidence was rewritten or code
pin bypass introduced. Actual prediction parity passesDTM009throughDTM002(8models).

Evaluator now emits fittedMembership independently of full train-role summaries;
missing legacy trainingIDs stays unavailable, not inferred. Tests cover4fitted/20other
members, duplicate/missing/wrong-partition IDs and numerical compatibility rejection.
Actual DTM009report explicitly scores all24fitted IDs. Trainer phaseTiming distinguishes
intake,fit,checkpoint and scoring without changing numerical fit code. Generic diagnosis
and coordinate-gradient tools now validate and handle the full fitted membership.

Evidence: `evaluation.json`, `fit-diagnosis.json`, `gradients.json`, `cli-parity.json`,
`ready/{protocol,approval}.json`. Logs `.build/fit61-{focused,prepare,dtm009,tests,eval,
diagnosis,gradients,parity,swift-build,swift-test}.log`. Actual entrypoints exit0;
43Python/134Swift checks and `git diff --check` pass. Swift used scoped host execution
with project-local configurable outputs. No SMB publication: local training finding.

Assigned tranche complete; broad goal remains active. Next TRANSFER-62: freezeDTM009,
measure order/translation sensitivity, implement no-scroll consumer cases and prepare
the bounded producer request. Capture and new admission still need exact authority.
Do not train longer on this now-fitted corpus as a substitute for missing coverage.
