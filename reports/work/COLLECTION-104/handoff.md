# COLLECTION104 — two completed comparisons; retain change improvement, reject ranker regression

October3local/October4UTC. Scope complete for review. Maintainer explicitly approved
the40pair admission after its prerequisite was stated, then standing training applied.
Fresh admission under `admitted/` preserves108train/5Settings development and all
exclusions. PREP103's earlier invalidated admission remains rejected evidence.
No capture, external transfer, export, promotion, deletion or Git writes.

## Results on identical membership

Joint requires correct change at confidence>=0.85 and both boxes IoU>=0.5.

| Configuration | Old68 joint | New40 joint | Settings5 joint | New endpoints |
|---|---:|---:|---:|---:|
| DTM024 + DTM020 baseline |66/68|2/40|2/5|10/80|
| DTM025 + DTM020 |66/68|4/40|2/5|10/80|
| DTM024 + DTM026 |66/68|28/40|0/5|80/80|
| DTM025 + DTM026 diagnostic |66/68|40/40|0/5|80/80|

DTM025: new change correctness28/40→40/40;12/12content-only false alarms removed;
16moves/12boundary no-ops retained. Original122same-frame negatives retain zero
false changes/abstentions. Two old genuine changes remain uncertain. Frozen geometry
weights unchanged and saved-checkpoint replay exact. Development advancement passes.

DTM026: all108training pairs' boxes fit, but exposed Settings endpoints regress
5/10→0/10. **Retention fails.** Newly wrong selections include large multi-row regions
and fragments, not a single minimum-size defect. The five formerly correct endpoint
occurrences are lost; old training136/136endpoints remain correct. This is observed
domain-transfer regression, not proof of its causal mechanism. Reject replacement
of DTM020 and combined deployment. No automatic third fit or threshold tuning.

All40new cases are now training, not independent evaluation; all Fixture ancestry
remains excluded from final. Settings remains exposed development, never training.
Light/dark support is20pairs each; all sectioned, no new small-control action claim.
Canonical per-group metrics are in `evaluation/evaluation.json`; trainer's legacy
original/native bucket summary is not the old68/new40 decomposition.

## Implementation, efficiency and evidence

Existing `train_focus_ring_detector.py` dispatches both extended adapters. Existing
collector, production crop derivatives, encoders and supervised losses are reused.
Added strict nine-channel initializer continuation, original122negative binding,
exact role/row/source checks, ranker checkpoint initialization, saved-ranker replay,
and an evaluator for all four component combinations. Joint ranking metrics now
exclude abstentions. No new cropper, trainer, architecture or dependency.

Preparation reused113cached pair tensors and187frame derivatives, taking1.935s with
zero native crop invocations. Both training outputs total1,593,145bytes, below2GiB;
small code/metadata/checkpoints stay local, with bulk retained storage unchanged.
No external waits or simulator setup. USB availability was verified, not benchmarked.

| Run | Fit / run seconds | PID / exit | Checkpoint SHA256 |
|---|---|---|---|
| DTM025 |177.573 /178.771|69089 /0|`28f10dc5ac2c6a0fb324cabeb778b2acad2539c97f7f9cc48a20c8ff534a9409`|
| DTM026 |3.424 /4.799|69088 /0|`bb5ab7f21eb860ebff6a98f08c92a6327fb70fdc53dbcefb7bd4c19db1d20f9e`|

Both600epochs,fixed-last,CPU2threads,seed42; Adam0.0001change /0.001ranker.
Change full230example update uses equal means of108real and122derived examples.
Ranker178train/9development frames, production crop256→RGB16 plus normalized size.
Protocols and approvals are in `ready/`; exact hashes pre-logged in ExperimentLog.
Prepared artifacts and raw results stay gitignored; this summary is the durable record.

Commands, all from package root with `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts`:

```
.venv-yolo/bin/python scripts/prepare_collection103.py --proposal reports/work/CALIBRATION-102/proposal/proposal.json --decision reports/work/PREP-103/role-decision-approved.json --output reports/work/COLLECTION-104/admitted
.venv-yolo/bin/python scripts/prepare_collection103.py --proposal reports/work/CALIBRATION-102/proposal/proposal.json --admission-root reports/work/COLLECTION-104/admitted --preparation reports/work/PREP-103/pending/preparation.json --output reports/work/COLLECTION-104/ready
.venv-yolo/bin/python scripts/train_focus_ring_detector.py --experiment-protocol reports/work/COLLECTION-104/ready/change-protocol.json --experiment-arm transition-change-adaptation --experiment-approval reports/work/COLLECTION-104/ready/change-approval.json --name collection104-dtm025 --experiment-id DTM025 --execute
.venv-yolo/bin/python scripts/train_focus_ring_detector.py --experiment-protocol reports/work/COLLECTION-104/ready/rank-protocol.json --experiment-arm transition-candidate-ranker --experiment-approval reports/work/COLLECTION-104/ready/rank-approval.json --name collection104-dtm026 --experiment-id DTM026 --execute
.venv-yolo/bin/python scripts/evaluate_collection104.py --ready reports/work/COLLECTION-104/ready --change-result NativeUITrainer/focus_ring_runs/collection104-dtm025/result.json --rank-result NativeUITrainer/focus_ring_runs/collection104-dtm026/result.json --output reports/work/COLLECTION-104/evaluation
```

Initial preparation failed before output because the diagnostic-only seal validator
was used for an admission receipt. Corrected to the generic strict seal validator;
preserved `.build/collection104-ready.log`; repaired preparation exited0. No fit retry.
One collision-check harness expected the wrong text; corrected assertion verifies
both actual trainer dry-runs exit2 with `output_collision`, leaving models intact.

59 focused/regression Python tests pass: collection101/102/103/104,derived98,
rank75,change80,size81,batch79,native86,native88. Logs `.build/collection104-tests-final.log`
(33,2.055s) and `collection104-regressions.log` (26,1.978s), exit0. Coverage includes
rejected approval/leakage/tampering, initializer parity, same architecture/features,
negative counts, confidence-aware joint scoring, source/crop cache contracts.
Actual dispatcher preflights passed before fitting; post-run collisions reject.
Offline Swift build/test exit0:14XCTest+120SwiftTesting pass. Project-local caches;
Apple test-helper cache access explicitly approved. Logs `collection104-swift-{build,test}.log`.

## Outcomes and next substantial tranche

- Software verification: PASS; existing dirty work preserved.
- Data eligibility: PASS for exact108training/5development scope, not final.
- Integration: cached trainer/evaluator PASS; live TTR shadow NOT ASSESSED.
- Model: DTM025 development advancement PASS; DTM026/combined FAIL retention;
  production gates NOT ASSESSED, shipped models unchanged.

Next priority: ingest the published TTR shadow source/permitted sample and validate
FDR021 evidence-only integration. Peer05:22:57Zsnapshot acknowledges our adapter
response;127intervals remain producer-local, source uncommitted, sample egress
approval pending. No archive transfer or new capture inferred.
In parallel, diagnose ranker logit/feature drift on retained candidates and prepare
one bounded retention-aware comparison using approved training data. Keep Settings
development held out of fitting; a different batch of Fixture seeds is not an
independent native-app test. Broader labeled native-domain data still needs explicit
membership/role/privacy approval. Do not spend another run on unchanged epochs.

## Coordination delivery

Published `packets.COLLECTION-104` in the verified
`/Volumes/SharedStatusFile/nuiak/status.yaml` at05:28Z with a targeted patch.
Duplicate-key-safe YAML readback exactly matches local `peer-status.yaml`; existing
packets/top-level summary preserved. Message limits peer consequences to unchanged
FDR021 delivery and useful negative/whole-control feedback; no new capture requested.
Peer acknowledgment of this update is pending, separate from its acknowledged
earlier adapter response. The reported127intervals are producer claims, not intake.
