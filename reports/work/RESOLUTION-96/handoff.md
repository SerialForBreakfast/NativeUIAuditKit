# RESOLUTION-96 — better fitted decisions, failed identity invariant

Completed the predeclared192×128comparison and independent same-frame diagnostic.
Prior goal turn and this turn are progress; overall goal remains active. No capture,
new training roles, producer edits, Git writes, export or promotion. Existing work
preserved. DTM018+DTM020remain experimental references; shipped artifacts unchanged.

## Controlled comparison

DTM023uses DTM022's9channel change architecture at192×128instead of96×64. DTM018
initial weights with six zero-added channels,approved68train/5exposed development,
600epochs,Adam0.0001,seed42,CPU2threads,fullbatch,noaugmentation,fixed-last,2GiB output
cap/no-wall-time override. Geometry remains its original96×64contract and bit-identical;
DTM020ranker boxes frozen. Change input size is explicit adaptation metadata; callers
must use the shape-checked change scorer, not pass192inputs through old geometry.

| Group | Raw change | Confident joint | Candidate abstentions |
|---|---|---|---:|
| Original44train |44/44|44/44|0|
| Added24train |23/24|23/24|1|
| Exposed Settings5 |5/5|2/5|0|

Joint train67/68versus retained control65/68,DTM02159/68,DTM02263/68. All20admitted
training no-ops retained. Rich compact-light and wide-light now confident-correct;
wide-dark remains uncertain at0.273508. Loss0.32503→0.03334. This is training fit,
not independent evaluation; exposed Settings localization remains unchanged.

Completed PID56848,exit0. Preparation22.549s,43,057,152tensor bytes (4×96inputs);
fit59.605s,total60.857s. Same-resolution initialization parity against the original
difference head,96control parity, frozen geometry and saved-checkpoint replay pass.
ProtocolSHA256:
`a424a4662016e8155128a278e1e12fa7bec3ef34cfae545b0f15f3926b90089b`.
CheckpointSHA256:
`ed3ed4ca60864c44c2dfd4139f33d1dcc98bd13b59632c59c0e9acaa07fa0b2b`.
Artifacts: `reports/work/RESOLUTION-96/ready/` and
`NativeUITrainer/focus_ring_runs/resolution96-dtm023/`.

Prepare: existing adapter `--prepare reports/work/RESOLUTION-96/ready --approve
--higher-resolution`. Execute: existing trainer with those protocol/approval files,
`--experiment-arm transition-change-adaptation --name resolution96-dtm023
--experiment-id DTM023 --execute`. Exact digest registered before launch;
`.build/resolution96-training.log` and completion receipt establish termination.

## Independent companion: same-frame invariant fails

Deduplicated131existing endpoint frames by verified byte hash, rejecting split/tensor
conflicts. Constructed each input as the same frame twice, no action/no new label
admission. Batches of8; frozen DTM018at96and DTM023at192with actual preprocessing.

| Model/source | Frames | Raw false changes | Confident false changes | Abstentions |
|---|---:|---:|---:|---:|
| DTM018training endpoints |122|0|0|0|
| DTM023training endpoints |122|36|35|8|
| DTM018development endpoints |9|0|0|0|
| DTM023development endpoints |9|0|0|0|

Reject replacement despite higher joint fit. Evidence demonstrates an appearance
shortcut on these constructed inputs; missing matched native negatives is a plausible
contributor, not proven sole cause. It does not establish performance on real no-op
navigation or background animation. Do not insert a pixel-equality guard and call
the underlying classifier fixed. Report/code at `self-pairs/diagnostic.json` and
`focus_change_adaptation.evaluate_self_pairs`; original source pixels untouched.

## Verification, coordination and next decision

14focused Python tests pass (change80,temporal68,signal95), including192shape contracts,
zero-channel initialization parity, unchanged geometry, checkpoint reload and
unbound-result/output-collision rejection. Real companion reports262model/frame
decisions with exact model/protocol bindings. Offline Swift build/test134tests pass;
final logs `.build/resolution96-final-{build,test}.log`. Earlier pre-companion Swift
checks retained. Diff check clean.

Local TTRHEADstill50ff7fd8; peer observation remains01:49:03Z and no acknowledgment
of source/negative requests was present. No repeated device operation or refreshed
claim of runtime availability. Existing published requests remain applicable; local
model results do not change the peer's assigned next action, so no redundant SMB write.

Asked maintainer to approve122training-only derived identical-frame negative pairs
as augmentation for one controlled comparison. This is pending, not an admission.
Do not use9development frames for training or claim synthetic self-pairs replace
genuine matched native negatives. Next substantial tranche, if approved: materialize
the source-bound augmentation, run one fixed comparison with old no-op/p2/self-pair
retention gates, and reconcile received layout28against version16source when published.
No new capture or promotion is part of that role decision. Preserve failed candidate.

Outcomes: software and local experimental integration verified; existing data
eligibility unchanged; new augmentation pending decision; candidate replacement fails
identity probe; independent/production model gates not assessed.
