# DATA-67 — improved training fit, transfer still fails

## Candidate and outcome

DTM012 completed600epochs,PID27092,exit0,2,400updates/19,200samples. Same architecture,
encoding, loss, optimizer and augmentation asDTM011. Added only the eight explicitly
approved native negatives; original29records unchanged. Class balance and update
count changed, so this is not an equal-compute causal comparison.

| Baseline paired localization | DTM011 | DTM012 |
|---|---:|---:|
| Original training |24/24|24/24|
| Added negatives |0/8|8/8|
| Exposed Settings |0/5|0/5|
| Trained translations, all training |96/128|128/128|

Added negative change decisions improve4/8→8/8raw correct,2decided false changes→0.
Settings stays2/5raw correct,3false changes; DTM012abstains on one changed pair.
Original training unseen axis2%paired76/96→89/96,axis6%65/96→79/96,
diagonal75/96→62/96. No independent evaluation or production improvement established.

Duplicated original training inputs still yield18/48raw change predictions; Settings
10/10. Added negative duplicates improve8/16→0/16raw change. These are zero-visual-
difference probes, not genuine no-op action labels. Memorization is not temporal
generalization. No unchanged second run, threshold adjustment or promotion occurred.

## Efficiency and integration

- Cold prepared inputs26.991s; verified warm loading0.214s,160variants.
- Actual run wrapper13.501s: intake0.386s,fit/setup12.971s,checkpoint0.007s,score0.137s.
  Initial CLI preflight excluded; cold preparation is reported separately, not hidden.
- One batched two-model evaluation:1,218shift scores,20rejected pair-condition cells,
  148duplicated probes.25.509s including2.953sPNG decoding. Both models reuse each
  decoded pair. No full native intake repeated for comparison or one-pair CLI parity.
- Exact expanded gate reconstructs the historical29record corpus and checks its hash,
  original admission, full-fit evidence and exact eight-pair decision. Original-gate
  behavior retained. Real altered/missing/extra/new-label cases all rejected.

## Evidence

Protocol `f81aeae70a200516dcdee265c0aeea1aaea3960507f76a3eb44f93c111059aa4`.
Checkpoint `ea23627ad8c42d851dcc4ed4ae935479d0469c53bbe8429aa2e7e8182271c447`.
Candidate: `NativeUITrainer/focus_ring_runs/data67-dtm012/{result.json,last.pt}`.
Protocol/approval/gate: `reports/work/DATA-67/ready/`; approximately3.7MB run output.
`comparison.json` preserves per-case predictions, groups, counterfactuals and timing.
All37reference baseline predictions and5candidate development predictions match
retained records. `negative-gates.json` and `cli-parity.json` verify real boundaries.

Commands, all exit0:
- `scripts/prepare_data67.py` (resident Python, project-local cache).
- `scripts/train_focus_ring_detector.py --experiment-protocol
  reports/work/DATA-67/ready/protocol.json --experiment-approval
  reports/work/DATA-67/ready/approval.json --experiment-arm transition-direct-pixels
  --name data67-dtm012 --preflight`; then same arguments with
  `--experiment-id DTM012 --execute` instead of preflight, after experiment logging.
- `scripts/evaluate_data67.py --candidate
  NativeUITrainer/focus_ring_runs/data67-dtm012/result.json --output
  reports/work/DATA-67/comparison.json`.
- `scripts/qualify_context57.py --base reports/work/DATA-67 --protocol
  reports/work/DATA-67/ready/protocol.json --runs data67-dtm012`.

78focused Python tests pass3.119s. Required offline Swift build/test passed,
14XCTest+120Swift Testing; unchanged Swift evidence reused after the final Python-only
CLI selection optimization. Logs `.build/data67-*`; `git diff --check` passes.
Preserved prior dirty work and failed test evidence. No Git writes or data deletion.

## Independent outcomes and next work

Software verified;32training/5development roles remain approved, no final holdout.
Offline trainer/prediction integration qualified; live TTR not exercised. Model
production gates not passed. No capture, runtime operations, download/export or
promotion. SMB not applicable: no producer contract or next action changed.

Next TEMPORAL-68: one explicitly scoped temporal change-head experiment at the same
32pair/600epoch budget, preserving geometry architecture and legacy loading. Batch
the same diagnostics. In parallel within that tranche, plan a retained-evidence-first
capture matrix for genuine no-scroll positives and missing styles, with session reuse
and separately authorized runtime execution. More unchanged epochs are not the next
step. The overall model goal remains incomplete.
