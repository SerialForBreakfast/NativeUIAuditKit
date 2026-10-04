# CONTEXT-93 / INTAKE-94 — experiment and data handoff complete for review

One scoped architecture comparison and independent retained-data transfer/intake.
Previous goal turn was progress; this turn also changes implementation and evidence.
Overall model goal remains open. Prior uncommitted work preserved; no Git writes,
capture, producer edits, new roles, export or promotion.

## DTM022: context helps relative to DTM021, but fails replacement criteria

Input to change head: absolute RGB difference followed by ordered before/after RGB.
9channels versus3; only432extra parameters. DTM018first3channel weights copied,
six new channels zero-initialized. Actual starting predictions match frozen control
within1e-6. Geometry and DTM020box predictions fixed.600epochs,Adam0.0001,seed42,
CPU2threads,full68training-pair batch,no augmentation,fixed-last,2GiB cap with
standing no-wall-time override. Five Settings pairs remain exposed development.

| Group | Raw change before→after | Candidate abstentions | Joint before→after |
|---|---|---:|---|
| Original44train |44/44→44/44|3|44/44→41/44|
| Added24train |21/24→23/24|1|21/24→22/24|
| Exposed Settings5 |5/5→5/5|0|2/5→2/5|

Total raw67/68; confident joint63/68 versus65/68retained control and59/68DTM021.
Reject as replacement. Three light scroll-no-op examples remain raw-correct but
uncertain. Rich compact-light p2is now confident-correct at0.95427; wide-light
is raw-correct but uncertain at0.72817; wide-dark confidently wrong at0.05034.
All20training no-ops retain raw correctness;17retain confidence. No thresholds
changed, no automatic follow-up run, no independent generalization claim.

ProtocolSHA256:
`756af1b9e748cd17c32f0431f2374d180f6705b4d9a59d4011eecc2767e7a236`.
CheckpointSHA256:
`b428ba8decbe474cb1bd5aa664b2e699e6ef3440113070366e96c12bffbc427d`.
PID55227,exit0; preparation22.039s,fit15.785s,totalrun16.871s. Exact saved-checkpoint
replay and bit-identical frozen geometry verified. Evidence at
`reports/work/CONTEXT-93/ready/` and `NativeUITrainer/focus_ring_runs/context93-dtm022/`.
Model configuration declares paired-context-difference-v1; old checkpoints retain
their original difference-only shape. Existing adapter/trainer used, not a new trainer.

Commands: prepare through `focus_change_adaptation.py --prepare
reports/work/CONTEXT-93/ready --approve --paired-context`; execute existing
`train_focus_ring_detector.py --experiment-protocol reports/work/CONTEXT-93/ready/protocol.json
--experiment-approval reports/work/CONTEXT-93/ready/approval.json
--experiment-arm transition-change-adaptation --name context93-dtm022
--experiment-id DTM022 --execute`. Log `.build/context93-training.log`.
Exact digest registered before launch. No new layout28example entered training.

## INTAKE94: bytes received, semantics explicitly blocked

Verified actual SMB mount sillycon.local/SharedStatusFile and65.18GiB local free.
Existing bounded receiver copied the named archive, verified SHA, rejected unsafe
member forms and extracted462members/45,449,650bytes into a fresh ignored directory.

- Request: `tvtestrig-20261003-native-layout28`.
- File: `tvtestrig/ttr-native-layout-diversity-28-20261003.tar.gz`.
- Bytes:13,951,938.
- SHA256:`57df23ca32b7f9215566fe5511e055d8b4134ce8df2250d77dc2409fb5c1b444`.
- Verified at2026-10-04T02:11:19.774515+00:00.

Local archive/original evidence retained under `reports/work/INTAKE-94/received/`.
Extended the existing collection accounting caller with explicit `--layout28`:
four completed campaign receipts,24appearance+4transition cases,312case files,
41,260,817member bytes,56distinct valid PNGs all verify. Real CLI exit0 in2.922s
means inspection finished, not semantic acceptance. Every case rejects
`invalid_metadata: canvas_collection_contract`. No producer fields stripped or
rewritten; native-collection-v2/version16remains unsupported pending source review.
Local TTRHEAD50ff7fd8 lacks this source; producer says its changes are uncommitted.
Report `reports/work/INTAKE-94/inspection/intake.json` preserves each rejection.

Published/read back exact receipt:
`nuiak/responses/nuiak-20261004-layout28-receipt.yaml`, plus packetINTAKE-94 in
`nuiak/status.yaml`. Duplicate-key-safe parsing and unrelated-status digest verify
preservation. Followed existing source-reference request, no duplicate capture/build
request. Peer acknowledgment/sender cleanup not yet established. Sender owns exact
shared-copy deletion after matching receipt; NUIAK deleted nothing. No new roles.

## Verification and next substantial tranche

15Python tests pass: native83,native84,change80,temporal68. Initial8model tests pass.
New cases prove context channels initialize at zero, original function parity,
learnable new weights, frozen geometry, reload parity and wrong initializer rejection.
Collection tests reject shrinking36into28and unsupported count scopes; real28caller
uses every existing strict validator. Swift build/test exit0,14XCTest+120SwiftTesting;
logs `.build/context93-{build,test}.log`. Diff check clean.

Next combine source-backed version16consumer support and a coverage/role proposal
with a local sparse-change diagnostic: compare the failed wide-dark transition and
uncertain no-ops at current versus higher-resolution encoding, preserving membership
and labeling. Establish whether discriminating evidence survives before choosing a
new resolution or regional model experiment. Do not launch an unchanged longer run.
New producer source is a dependency for intake compatibility, not local diagnostics.

Software verified; existing training eligibility unchanged, new data blocked;
local model/transfer integration verified, new producer semantic integration blocked;
replacement comparison failed, independent/production gates not assessed. Keep
DTM018+DTM020experimental reference and all shipped artifacts unchanged.
