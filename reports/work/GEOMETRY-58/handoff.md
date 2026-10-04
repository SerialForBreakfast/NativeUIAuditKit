# GEOMETRY-58 — completed for review

October3,2026. Starting commit24964ec, clean checkout. Assigned geometry experiment,
retained-source coverage inventory and low-risk technical-debt cleanup completed.

| Outcome | Evidence |
|---|---|
| Software verified |34Python tests, offline Swift build and134tests pass |
| Data eligible | Existing24Fixture/train and5Settings/development admission unchanged; no new data admitted |
| Integration qualified | Actual trainer/evaluator/prediction CLI and four-checkpoint parity pass; no new TTR runtime claim |
| Model gate passed | Failed:2/4paired boxes, required4/4; conditional candidate correctly refused |

## Experiment

DTM005 changes only geometry supervision to BCE-with-logits on the existing fractional
coordinate targets. Same881,819parameter context model, same four training IDs,
96×64,120epochs,Adam0.001,batch8,seed42,fixed-last. CPU2threads. No augmentation,
data-role changes, threshold tuning, capture, export, promotion or Git writes.

| Fitted-subset metric | DTM004 | DTM005 |
|---|---:|---:|
| Correct cells |8/8|8/8|
| Correct raw change |4/4|4/4|
| Both endpoint IoUs≥0.5 |0/4|2/4|
| Mean geometry L1 |0.08116|0.03843|
| Mean cell CE |0.08753|0.03967|

Both light pairs pass. Dark before-frame IoUs0.4458/0.4766 remain below0.5;
predicted heights0.140/0.129 versus0.06328truth. Heights no longer collapse to zero,
but extent errors persist. Different training objectives make total loss incomparable.
Actual candidate preparation exits1 `memorization_gate_failed`; noDTM006directory/run.

All24train-role pairs rescored, only4fitted: paired9/24, raw change17/24. Settings5:
paired0/5,raw change5/5,all5emit decisions. Change confidence still does not qualify
box accuracy. Not usable navigation localization or independent evaluation evidence.

Protocol `f311d1fcbe9f70a0843568783f5e04c444103085cb6b9a8d3e61b84679714a7b`.
Checkpoint `ba278dff323048098c16226572074b394b24b6c824843527132eae6beda54e0b`.
Corpus `9735108bf5ae011dfb17c07f7d49c4b42dfba4c9e1e027459a2b377047f589aa`.
PID15007 exited0;120updates,20.219s including intake/fit/development scoring,
3,549,047run bytes under2GiB. No running process remains. CPU warm median4.453ms,
p954.779ms over20samples, excludes PNG load; no controlled performance comparison.

## Independent source inventory

`source-inventory-reviewed.json` is the final inventory. All24Fixture pairs have
native per-container offsets stable within each capture bracket and different across
endpoints:12changed/12unchanged, all scrolling. The five Settings records have
completed action events and reviewed focus relations but unknown scrolling and no
bound cleanup receipt in the inspected chain. No-scroll training coverage is absent.

Fixture receipts distinguish12navigation actions from24observed scroll mutations;
all24contain verified cleanup. Embedded evidence pointers remain in original files,
not fabricated standalone receipts. `source-inventory.json` is retained intermediate
evidence; its unconditional action pointer was corrected for mutation-only cases.
No source edits, new admission or automatic capture. Shared status not applicable:
local findings and proposed acquisition scope do not instruct TTR to act yet.

## Technical debt and verification

- Reused `prepare_context57.py --geometry` with strict config-specific diagnostic gate;
  no copied experiment runner. Candidate cannot use the wrong diagnostic family.
- Parameterized parity runner `--base/--runs`; actual image-only prediction matches
  savedDTM005/004/003/002outputs. `cli-parity.json` pins all four checkpoints.
- Centralized allowed spatial/diagnostic configurations; removed hardcoded384-cell
  loss reshape. Existing configuration values and old inference remain unchanged.
- Added PID to future execution/results; diagnosis now checks checkpoint version/config.
- Analytical tests prove finite correcting gradients at saturated geometry logits,
  exact unchanged initial architecture, serialization, gate failures and native-scroll
  unknown handling.34focused Python tests pass2.391s.
- Offline Swift build and134tests pass using approved host execution with project-local
  caches/temp/logs. No repeated sandbox denial, services or permission changes.
- Actual preparation/trainer/evaluator/diagnosis/inventory/parity entrypoints exit0;
  conditional candidate rejection is expected exit1. `git diff --check` passes.

Logs `.build/geometry58-{prepare,dtm005,eval,diagnosis,inventory,inventory-reviewed,
candidate-gate,parity,tests-final,swift-build,swift-test}.log`. Full diagnostics and
frozen protocol/approval remain under this directory; raw weights stay gitignored.
External wait and capture time zero. No TTR request publication or peer acknowledgment
claimed. Tasks, canonical plan, roadmap, state, experiment log and observed lesson updated.

Next substantial tranche: proposed GEOMETRY-59, overlap-aware extent supervision on
the now-working context/cell/logit model, same diagnostic gate and conditional candidate,
plus a bounded no-scroll acquisition specification. New experiment assignment required;
no automatic extra fit follows this failure. Actual acquisition retains separate authority.
