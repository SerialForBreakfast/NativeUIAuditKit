# FOCUS-FIT-01 — learning diagnosis completed

2026-09-30. Owner: Codex. One authorized diagnostic, FDR019; no release candidate.

## What we learned

The existing frozen features and linear head can learn the selected balanced examples.
The earlier runs also performed poorly on their own training data, so it was premature
to attribute their failures solely to synthetic-to-real transfer or insufficient diversity.
This does not prove a single cause: the diagnostic changes subset, loss, learning rate
and schedule. It tests learnability, not which individual change improves production.

| Measure | FDR017 terminal | FDR018 terminal | FDR019 diagnostic |
|---|---:|---:|---:|
| Native training focused hits at0.85 |32/395|27/395|16/16 selected|
| Human training focused hits at0.85 |not trained|0/8|8/8 selected|
| Development focused hits at0.85 |1/27|0/27|17/27|
| Development false positives |5/288|15/288|38/288|
| Complete-frame unique correct |1/14|0/14|7/14|
| Retention correct |9/18|9/18|18/18|

Same development members and evaluator, but different training protocols: this is
context, not an isolated intervention comparison or independent qualification.
At0.5 the prior heads classify646/790 and626/790 native training crops correctly;
the issue is not merely that all training decisions are correct below0.85.
Original heads replay their stored development scores with maximum error0.0.

## Execution and diagnostic result

- Fixed48 admitted training crops:24positive/24negative,16genuine native/Fixture
  pairs across buttons/tabs/artwork/rows plus8human positives/8negatives.
- Exact cached576-dimensional ImageNet MobileNetV3-small features; fresh577-parameter
  head, seed42, fullbatch48, AdamW0.01, plain BCE. No encoder execution or new crops.
- Training-only stop at update162 after five consecutive48/48confident checks:
  positives>=0.85, negatives<=0.15, BCE0.038574. Finite gradients, changed weights.
- PID34480;18:33:56–18:35:04UTC;68.756s including input preflight,1.726s model loop.
  MPS, exit0, no timeout. Maximum1000updates/300model-seconds/600external-seconds.
- Development315controls plus18retention measured initially, every50updates and
  terminally. No development-driven stopping, threshold sweep or checkpoint selection.
- Complete frames:7unique correct,5multiple focus,1wrong,1no focus. Another18frames
  remain unavailable for complete-frame selection because annotations are incomplete.
- Artwork:3/12focused hits and31/181false positives. Rows:7/7hits,1/64false positives.
  Tabs:3/3hits,4/21false positives. Buttons:3/3hits,2/3false positives. Other:1/2hits,
  0/19false positives. Small support and repeated development exposure limit conclusions.

The diagnostic has63%focused recall but only31%precision. It is not safe autonomous
focus selection and cannot be promoted despite the fit and retention successes.

## Acceptance and evidence

- Research-first contract: `Research/Plans/FocusFitDiagnostic.md`.
- Frozen membership/runtime/code references: `frozen-ready/protocol.json`, seal
  `c818c7ab4e98f1a6fa1781273761b2fb15bf303a138fc3894163f4f56759bdaa`.
- Actual CLI preflight: `preflight.json`; MPS verification: `backend.json`;
  bounded execution receipt: `execution.json`.
- Actual trainer artifacts: `NativeUITrainer/focus_ring_runs/fdr019-balanced-fit/`.
  `weights/last.pt` is diagnostic-only. No `best.pt` exists.
- `report.py` replays saved predictions with the production metric implementation,
  checks BCE, stopping, weight change and all pinned source/crop hashes;
  `diagnosis.json` accounts for7,824training and1,665development/retention predictions.
- `prior_fit.py` scores retained FDR017/018 heads on their exact original cache,
  validates cache identities and reproduces development outputs; no optimizer.
  Evidence: `prior-training-fit.json`, `prior-fit.log`.
-42focused/legacy Python tests; offline Swift build and123tests pass. Detailed
  commands/results and negative-case coverage: `verification.md` and retained logs.

## Outcomes and next assignment

**Software:** integrated diagnostic adapter and real trainer path verified; legacy
tests pass. **Data:** no new admission, relabeling or split movement;48selected from
already admitted training members,315development/18retention preserved.
**Integration:** no TTR runtime needed; shared coordination not applicable because
this result changes our model diagnosis, not the producer's current next action.
**Model gate:** training-fit diagnostic passed; release remains unqualified, shipped
weights unchanged. No export, capture or additional training run.

Recommended next model assignment: prepare one full-admitted-corpus fitting experiment
with explicit per-source/class loss accounting and training-fit trajectories. Preserve
the fixed development/retention gates and select only eligible checkpoints. Establish
whether the existing features can fit the full corpus before changing representation.
Use existing data; no further annotation request is needed for this step. Exact new
schedule and execution require separate approval; do not silently reuse this tiny-set
learning rate or promote its terminal weights.

In parallel, receive the already published TTR artwork proof/crop audit through the
verified receipt flow and inspect production crop context. That is a targeted evidence
check, not a prerequisite for the optimization proposal or proof of the failure cause.
