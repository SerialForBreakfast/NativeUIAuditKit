# FDR-012: small synthetic gain, worse real-screen transfer

Decision: **do not export or promote this checkpoint, and do not repeat this run
unchanged.** The approved development success criterion failed: real recall fell
and false positives increased. Shipped weights remain unchanged.

## Execution and selection

All30epochs completed on MPS in90.70seconds;396.55seconds including full preflight.
PID54962 exited0. Same-process MPS assertion passed before existing trainer execution.
325training pairs/650crops and9retention pairs/18crops; fresh FDR007 initialization,
AdamW,batch64,lr0.0003,seed42,50/50 native-Fixture,no augmentation,1,800second cap.
No partial FDR-011 weights reused.

Replayed all30epochs through existing retention metrics; all were eligible.
Epoch29 has minimum retention BCE2.8957965862683084e-8 and18/18correct at0.85.
Checkpoint SHA256 `b079f4c756af52889b055cda2a3a87d4310be9fe518703a1d28704b49dbd044c`.
Selection was frozen before benchmark inference. No alternative epoch was scored.

## Real development screens

All517scores completed across40frames.453settled candidate crops enter this table:
35focused,418unfocused.64auxiliary/disputed/unsettled entries remain accounted for
in each benchmark and comparison-summary.json, not silently removed. These are
repeatedly used, correlated development examples, not an independent production exam.

| Model | Focused found /35 | Recall | False positives /418 |
|---|---:|---:|---:|
| Shipped |18|51.4%|140|
| FDR-010 |3|8.6%|9|
| FDR-012 |1|2.9%|15|

FDR-012 versus FDR-010:2 fewer focused controls,6 more false positives,
recall -5.71percentage points, FPR +1.44points. Neither candidate is a release pass.
Overall negative-dominated accuracy is not the decision criterion.

| Stratum | Focused / unfocused support | Shipped TP / FP | FDR-010 TP / FP | FDR-012 TP / FP |
|---|---:|---:|---:|---:|
| Buttons |3 /7|3 /3|0 /0|0 /0|
| Tabs |3 /21|1 /10|0 /0|0 /0|
| Artwork |18 /255|10 /81|1 /9|0 /15|
| Rows |9 /116|3 /46|2 /0|1 /0|
| Other |2 /19|1 /0|0 /0|0 /0|

Complete-frame selection is supported for13 of the first24frames. FDR-010:
2unique-correct,11no-focus,0wrong,0multiple. FDR-012:1unique-correct,11no-focus,
1wrong,0multiple. Shipped:3unique-correct,5no-focus,0wrong,5multiple.
The other27real frames do not establish complete-frame selection; do not divide
these successes by40 or infer completeness from a single annotated positive.

Preserved benchmark-level FDR-010 → FDR-012 TP/FP:

- Batch1:1/0 →1/0 (5positive support).
- Batch2:0/0 →0/1 (8positive support).
- Batch3:2/3 →0/1 (6positive support).
- Prior Home/Photos/Settings eight-frame set:0/4 →0/13 (8positive support).
- Supplemental eight-frame set:0/2 →0/0 (8positive support).

## Related synthetic diagnostics — separate population

All312scores completed:100paired-target crops and212competitor crops. These
correlated subsets are not312independent focus states.50complete frames.

| Model | Focused targets /50 | Paired-negative FP /50 | Unique-correct frames /50 |
|---|---:|---:|---:|
| Shipped |7|2|7|
| FDR-010 |18|0|18|
| FDR-012 |20|0|20|

FDR-012 preserves4/4buttons,10/10tabs,4/4rows and improves artwork0/32 →2/32.
All paired-negative strata remain0FP. Complete frames:20unique-correct,30no-focus,
0wrong,0multiple. The two newly correct positives are texture-export synth-0 and
synth-3, scores0.8844 and0.8920. Thirty artwork positives still fail. A shared
renderer/motif result is interpolation evidence, not independent generalization.

## Failure diagnosis and next assignment

There are18changed real decisions:5improvements and13regressions. Two regressions
are lost positives: batch3 `recorded-306:new-7` (row,0.9970→0.3131) and
`recorded-1043:new-7` (artwork,0.9370→0.0414). Eleven new false positives minus
five resolved false positives account for the net+6FP. Nine new false positives
are in the prior Home/Photos/Settings set, concentrated in repeated new-5/new-19
controls across several frames. These repeated errors are not nine independent
source failures. Every changed decision and candidate error binds original
sample/image/crop/bounds in real-errors.json.

Evidence supports inadequate representative transfer/selection, not a proved
single visual cause: tiny familiar retention loss remained excellent while real
artwork/rows regressed. Added12pairs did not produce the intended transfer gain.
One stochastic training comparison cannot establish that related synthetic data
is generally harmful, or isolate content, focus effects, geometry and context.

**Next bounded assignment: intake the already-published44pairs, audit them against
these failure slices, and freeze a representative selection proposal before any
new training.** TTR's21:11:59Z status reports44pairs/11scenes complete and published;
this tranche has not downloaded or admitted them. Avoid duplicate capture/redraw.

1. NUIAK: verify the named44-pair artifact, native labels/geometry, production crops,
   pixel conflicts and exact protected-member exclusions. Keep admitted variants
   related-source development training; do not invent source independence.
2. TTR: map existing44 and proposed100 recipes to matched native-image/native-button
   content, explicit light/dark backgrounds, geometry and visible bright unfocused
   competitors. Identify unsupported cells rather than enlarging an easy grid.
   Retain selected-unfocused tab parents and genuine row context as nonregression
   slices. Ask for source IDs/recipe hashes, not individual human box drawing.
3. NUIAK: propose representative selection with buttons,tabs,artwork,rows balanced
   across declared source groups, keeping18/18retention as a floor. The current
   benchmarks stay development-exposed; any use for selection must be explicit,
   and a disjoint genuine-source qualification set must remain separate. This is
   a proposal for separate approval, not permission to choose another FDR-012 epoch.
4. Fill measured gaps before scale. Existing96-pair matched-contrast and30real-state
   targets remain planning targets, not new gates. First count what44already supply.

No new capture or next100 runtime is authorized here. Software, native capture
integrity, model transfer and release qualification remain independent outcomes.

## Verification and limitations

Existing production16%/256crops, threshold0.85; frozen inputs/hash checks before
and after scoring.829/829candidate predictions,0failed/invalid/missing. Baselines
reused only after exact metric replay and identity validation.33focused tests pass.
No implementation code changed; no new Swift build needed. Comparison summary
and errors reproduce from retained predictions without another inference run.

Shipped inference is CoreML CPU; candidates use PyTorch CPU. No export-parity or
direct latency comparison claimed. MPS was used for training only. No independent
qualification, temporal policy, confidence calibration, export or promotion tested.
