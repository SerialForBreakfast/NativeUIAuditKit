# FOCUS-FULL-FIT-03 — FDR020 completed with measurable gains, not release-qualified

2026-09-30. Owner Codex. Approved proposal implemented and single run completed.

| Outcome | Result |
|---|---|
| Software | Versioned adapter integrated with actual trainer;47focused/legacy tests, offline build and123Swift tests pass. |
| Data |928admitted training members,315development and18retention preserved; code/source/crop/cache hashes verified. No new admission. |
| Integration | Actual MPS preflight and bounded execution complete; no TTR/device/export operation. |
| Model | No eligible checkpoint among40snapshots. Strict all-confident training criterion not met, but all928classifications correct at0.5. Shipped weights unchanged. |

## Results at the unchanged0.85decision threshold

| Measure | FDR019 tiny diagnostic | FDR020 full corpus |
|---|---:|---:|
| Development focused hits |17/27|14/27|
| False positives |38/288|3/288|
| Complete-frame unique correct |7/14|9/14|
| Multiple focus |5/14|1/14|
| Wrong focus |1/14|0/14|
| No focus |1/14|4/14|
| Retention correct |18/18|18/18|

Same development membership/evaluator; changed training population/loss/weights/schedule.
This is not a controlled single-variable comparison or an independent test. Another
18frames are incomplete/unresolved and cannot establish complete-frame correctness.
FDR020 improves precision (82.4%) at the cost of recall (51.9%); a high aggregate
crop accuracy must not obscure13missed focused controls.

Training: weighted BCE0.017118;928/928correct at0.5;393/403positive hits and0/525FP
at0.85.901/928meet strict separation (.85positive/.15negative):10native positives
remain below.85 and17native negatives above.15. Human training138/138confident.
Therefore the predefined all-confident five-check stop criterion did not pass;
execution ended at update1000, not a falsely declared fit success.

## What is still failing

| Development stratum | Focused hits | False positives |
|---|---:|---:|
| Buttons |3/3|1/3|
| Tabs |2/3|0/21|
| Artwork |1/12|2/181|
| Rows |6/7|0/64|
| Other |2/2|0/19|

The Photos Welcome all-iCloud button (`photos:frame-004:all-icloud-photos`) is labeled
unfocused but scores0.983845, causing the sole complete-frame multiple-focus result.
The other false positives are `batch03:recorded-536:new-1` (Home top shelf) and
`batch03:recorded-1043:new-9` (App Store search results); those frames are incomplete.
Four complete-frame no-focus cases: Settings303, Home12, Home249, App Store tabs971.
All16terminal crop errors and exact scores/source crop references are retained in
`terminal-errors.json`. Several artwork misses score near zero, so this is not merely
a group of borderline0.85decisions. No label was changed based on a prediction.

The previous underfit is substantially improved. Persistent poor artwork performance
on other screens now establishes a transfer weakness for this representation/recipe;
it does not prove whether appearance coverage, crop context or frozen features cause it.

## Execution and reproducibility

- Proposal seal ef8001be1109177728ecd35ec8fd473bee31a6bf61782c08737070eb84a44537.
- Frozen protocol b650da4919583d57180ca0f29c6577529c2b6984f7582ce0c2c3ab695b5644b7.
- Existing FDR017576feature cache; fresh577parameter head seed42. No encoder loaded.
  Fullbatch928, AdamW0.01/weight_decay0.01, plain weighted BCE, native/human80/20mass,
  50/50label mass. Every example observed every update; no sampling/augmentation.
- MPS/PyTorch2.13.0, PID40455,19:03:08–19:04:40UTC.91.530s including preflight;
  model loop21.342s.1000updates, exit0, no timeout. External600s/model300s caps retained.
- Native duplicate weighting retained; human frame/label/pixel weighting explicitly
  normalized. Exact cache tensor order/labels/shape/hash validated before indexing.
- `scripts/focus_full_fit_experiment.py --output …/frozen` prepared the protocol;
  actual `train_focus_ring_detector.py --experiment-arm full-corpus-fit --preflight`
  passed. `launch.py` performed the single guarded launch with no automatic retries.
- `report.py` replayed928,928training and13,653development/retention predictions,
  training-only stopping and unchanged guarded minimum-loss/earliest-tie selection.
  Pinned code/source/crop identities preserved; finite gradients and changed weights.
- Last checkpoint: `NativeUITrainer/focus_ring_runs/fdr020-full-corpus-fit/weights/last.pt`.
  Diagnostic only. No best.pt exists. Reports/logs are local ignored evidence.

## Verification and completion

Research amendment and ExperimentLog preceded code/run. Tests cover actual trainer
dispatch, approval/configuration rejection, leakage/conflicting duplicate labels,
loss balance, finite/complete predictions, training-only stopping and actual loop
checkpoint behavior. CPU unit fixtures are generated and isolated, not another corpus
run.47Python tests/123Swift tests pass; offline build passes. See `verification.md`.
Prior uncommitted preparation/status work preserved. No Git writes or external mutation.

Assigned implementation, real execution, replay, diagnosis and status are complete.
No background process remains. Coordination is not applicable: TTR's next action
is unchanged, and there is no replacement model to deliver. Prior crop-audit receipt
and correction request remain separate; no stale peer acknowledgment is invented.

## Recommended next substantial tranche

Target artwork and Photos transfer, not a longer unchanged run. Use retained original
frames, reviewed labels, native focus-switch pairs and cached features to test whether
scores follow image content or focus appearance, and inspect context/geometry on the
exact errors and matched counterexamples. Preserve development membership; do not move
failed examples into training or claim a new independent benchmark.

End that diagnosis with one justified intervention: targeted matched training data
if the required focus contrasts are absent, or an explicitly bounded feature-adaptation
experiment if those contrasts exist but the frozen representation fails to transfer.
Do not request another broad human annotation batch or launch another run by default.
No threshold change, new capture, additional training, export or promotion is authorized
by this completed assignment.
