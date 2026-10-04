# RANK-RETENTION105 — diagnose transfer loss; reject DTM027

Scope complete for review, October3local/4UTC. No new capture, corpus admission,
external writes, export, promotion or Git changes. Existing dirty work preserved.
The separately delivered DTM025 change-only consumer remains available to TTR.

## Decision and evidence

All187unique frames contain a correct candidate. The ranker—not proposal recall—is
the observed bottleneck here. Replay exactly reproduced DTM020/DTM026 selections.
Nine unique Settings frames occur in ten pair endpoints; do not call those ten
independent images. Old/new training contain122/56unique frames respectively.

| Ranker | Old unique correct | New unique correct | Settings unique correct | Settings pair joint with DTM025 |
|---|---:|---:|---:|---:|
| DTM020 retained |122/122|6/56|5/9|2/5|
| DTM026 rejected |122/122|56/56|0/9|0/5|
| DTM027 frozen readout |122/122|56/56|1/9|0/5|

DTM027 lost **all five previously correct Settings frames**; its one success was
formerly wrong. The predeclared retention gate therefore fails. Combined new40
joint improves4/40→40/40, but these are training pairs, not generalization evidence.
Retain DTM020. Do not export DTM027 or automatically try another coefficient/epoch.

Frozen weight swaps provided the diagnosis before fitting: old hidden/new readout
retained4Settings but fit only4new frames; new hidden/old readout retained3Settings
and fit56new. This motivated one test of a stable final readout, not a claim that
the readout alone caused regression. Its failure shows that hidden-feature changes
can still destroy transfer. Border detail/context and training-domain coverage
remain hypotheses for the next audit, not established causes.

## Implementation and experiment

`diagnose_retention105.py` emits candidate logits, positive margins, normalized
geometry, hidden activation and parameter drift, unique-frame counts and diagnostic
layer swaps. Existing `focus_candidate_ranker.py` adds one explicit hidden-only
configuration and preparation mode; existing trainer dispatch executes it. Existing
`evaluate_collection104.py` accepts the pinned rank protocol and verifies exact
data binding, unique-frame retention, optimizer membership and saved frozen tensors.

DTM027 initialized DTM020, trained770→32 hidden weights/bias only, final32→1 fixed.
108train/5exposed development,178train/9development unique frames;600epochs,
Adam0.001,seed42,CPU2threads,fixed-last,2GiBcap,no-wall-time override. No Settings
loss/teacher/selection or threshold tuning. DTM025 fixed for final comparisons.

- PID75357,exit0; fit3.146s,total4.517s;258,881run bytes.
- Diagnosis0.971s; preparation0.595s; zero native crop calls or external waits.
- Protocol `57d9a75984a537afb3a15e6f545937efd5088e0f82923b123e55c87b66ee745a`.
- Checkpoint `b391087237e84499d82c5824602ddfd305c38ad4fc7863b321991a26837a5e4b`.
- Final evaluation `1c72e804c11502815919ace90411af314ba82fbda41805478703ff38ed8af756`.

Canonical raw evidence stays gitignored in `artifacts/diagnosis-components/`,
`artifacts/ready/`, `artifacts/evaluation-verified/` and
`NativeUITrainer/focus_ring_runs/retention105-dtm027/`. Source membership is unchanged.

## Verification and preserved discrepancy

27focused/regression Python tests pass, including an actual synthetic trainer run
that verifies parameter names, frozen tensor equality, and exclusion of development
frames from optimization. Integrated offline Swift build/test exit0:14XCTest plus
123SwiftTesting. Saved candidate replay is exact. Actual changed-code protocol
replay and existing-output collisions reject before another launch. `git diff
--check` passes. Logs `.build/retention105-{diagnosis,prepare,training,evaluation,
regressions,swift-build,swift-test}.log` contain commands' results.

The first trainer receipt's `frozenParameterNames` incorrectly contained control-row
IDs due to variable reuse **after** the successful frozen-weight assertion. Source
is fixed; original sealed result and initial evaluation remain untouched. Final
evaluation independently loads both checkpoints and confirms `2.bias`/`2.weight`
exact equality, while truthfully reporting `trainerFrozenNamesMatch:false`.
No extra scientific fit was run to make the receipt look clean; no retroactive
protocol resealing. Original protocol now correctly rejects changed implementation.

## Outcomes and next tranche

- Software:PASS—focused tests, real dispatcher, checkpoint/evaluator integration,
  required offline checks and corrected future receipt path.
- Data:unchanged108/5eligibility; no final evaluation or new source admission.
- Integration:local cached training/evaluation PASS; live TTR not part of this task.
- Model:retention FAIL; no deployment/promotion. Settings remains exposed development.

Coordination not applicable: this local failed comparison changes neither TTR's
delivered change model nor its requested next action, so no SMB noise was published.

Next substantial tranche: RANK-REPRESENTATION107 audits feature collisions/nearest
opposing candidates and crop detail before proposing one richer-context comparison.
Reuse retained sources/crops; no simulator needed. A new encoding/backbone fit needs
its explicit scope/budget recorded, not another unchanged training loop. In parallel,
intake TTR feedback only when its permitted artifact/receipt and roles are available;
keep independent journey evaluation out of training.
