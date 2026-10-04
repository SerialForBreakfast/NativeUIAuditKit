# CHANGE-92 — candidate rejected; preparation reuse verified

Completed one authorized local experiment and independent preparation optimization.
No capture, new roles, export, promotion, external repository edits or Git writes.
All prior uncommitted work preserved. Goal remains open.

## Experiment

DTM021: existing DTM018absolute-difference change head, approved68train/5exposed
Settings,600epochs,Adam0.0001,seed42,full68batch,CPU2threads,no augmentation,fixed-last,
2GiB cap/no-wall-time override. Frozen geometry and DTM020boxes. Existing training
dispatcher/adapter extended; no second trainer. Corpus replay exact before launch.

| Group | Raw change before→after | Candidate abstentions | Joint before→after |
|---|---|---:|---|
| Original44train |44/44→44/44|6|44/44→38/44|
| Added24train |21/24→22/24|3|21/24→21/24|
| Exposed Settings5 |5/5→5/5|0|2/5→2/5|

Reject as replacement: joint train65/68→59/68 despite raw65/68→66/68. All20training
no-ops remain raw-correct, but6previously certain scroll-no-op cases fall below0.85
confidence. Compact-light p2rises0.01450→0.78491, now raw-correct but uncertain.
Wide-dark/light p2rise0.000031/0.000036→0.16373/0.17210, still wrong and uncertain.
No threshold tuning or automatic second run. Loss0.36859→0.08901 does not make
the operational metric better. Training fit is not independent generalization.

Representation diagnosis (no further inference/training): the wide pair mean
absolute encoded differences are0.000678/0.000720; compact-light0.003998 and
compact-dark0.008502. Nearest training no-op is an all-zero difference example;
none are exactly equal to it. Thus there is sparse surviving information, not
proof of an impossible collision. Whole-frame absolute difference discards source
appearance; a controlled paired/context representation test is justified, not a
claim that resolution alone or more epochs must fix this.

Protocol digest:
`d6f6319ba6292ee5c1f0b93d0adc029360b9d347b3ba0d8a54bbc2a1455896c3`.
Checkpoint:
`4d4e6ca7ed237afb39af4be82da1641f3f367539a83ebbfd67adb38c0dba7c4a`.
Completed PID54296,exit0. Preparation22.715s; fit12.968s,totalrun13.909s.
Initializer prediction parity1e-6, bit-identical frozen geometry and exact saved
checkpoint replay all verified by actual runner. Result/completion retained under
`NativeUITrainer/focus_ring_runs/change92-dtm021/`. Protocol/arrays under
`reports/work/CHANGE-92/ready/`; ExperimentLog registered exact digest before launch.

Execution used existing `scripts/train_focus_ring_detector.py` with
`--experiment-protocol reports/work/CHANGE-92/ready/protocol.json`,
`--experiment-approval reports/work/CHANGE-92/ready/approval.json`,
`--experiment-arm transition-change-adaptation --name change92-dtm021
--experiment-id DTM021 --execute`. Missing-approval preflight exit2, explicit approved
execution exit0. Logs `.build/change92-{no-approval,training}.log`.

## Preparation optimization and tests

Readiness returns its verified frames alongside its report; semantic preparation
reuses those values immediately instead of rebuilding the baseline. Existing `run`
output shape retained; no persistent cache, source hash skip or role change. Prepared
input pins now explicitly include decoded_identity implementation as well as its
wrapper, preventing an untracked helper change from validating stale input seals.
New protocols use current pins; no historical seal rewritten.

Actual73record `collect` equals the retained NATIVE87corpus exactly. Profile records
one baseline traversal vs two,4661source checks vs9031. Full collection24.602s versus
PREP91's36.746s (about33%observed reduction); single instrumented measurements include
system contention, so not a guaranteed throughput figure. The eliminated duplicate
traversal is directly established, not inferred from timing.

86focused Python tests pass (change80,campaign71,focus_recorded_comparison,
focus_reviewed_transitions,focus_readiness20,preparation_identity). Generated tests
cover frozen parameter/gradient/reload behavior, malformed tensors, source/control
bindings, tampered probabilities and one reviewed-frame traversal. Initial focused
11tests also pass. Offline Swift build/test exit0:14XCTest+120SwiftTesting; logs
`.build/change92-{build,test}.log`. Diff check clean.

## TTR coordination and next substantial tranche

Verified mounted SMB endpoint. Peer snapshot01:49:03Z/valid02:19:03Z reports new
native-collection-v2/version16layout28:24appearance+4observed scrolling pairs;
source changes uncommitted against50ff7fd8. Verified handoff Markdown6321bytes,
SHA256`e27d81b1f27d725d0e3468207867a74eb359a93665f08b77a054b78439ec22d1`.
No archive copied, no transfer receipt, no cleanup approval or intake claim.
Published/read back `nuiak/status.yaml` packetCHANGE-92 with receipt-of-message
acknowledgment and `nuiak-20261004-layout28-source-reference` requesting the published
branch/commit, not binaries or recapture. Unrelated parsed status preserved exactly;
peer acknowledgment of this new request pending.

Next: (1) freeze one context-preserving change-head comparison against DTM018 using
the existing73encoded pairs and fixed no-op/joint gates; (2) transfer the named
layout28archive with a hash receipt and reconcile source-backed version16intake;
(3) prepare its coverage/role proposal without silently adding examples to training.
Intake needs producer source publication; local comparison does not. Independent
native evaluation still needs EVAL90source/role/runtime qualification.

Outcomes: software verified; existing data eligibility unchanged; local runner
integration verified, new producer integration not assessed; model replacement
comparison failed and production gates not assessed. Shipped models unchanged.
