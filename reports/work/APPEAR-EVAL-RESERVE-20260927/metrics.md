# Frozen surface validation — no replacement recommended

2026-09-27. Threshold0.85, base boxes only, production16%/256 crops. Two
validation groups,48 pairs/96 paired crops,48 focused frames×24 controls=1,152
competition crops. All1,248 predictions/model completed:3,744 total, zero failures.
The other48 pairs are reserved final challenge and have zero model predictions.

Native callbacks/capture brackets and pixel integrity pass; renderer/journey
independence is not established. Treat these as scoped diagnostics, not a release
holdout. Repeated frames, neighbors and shared layouts are correlated observations.
Oracle native boxes isolate focus classification; YOLO localization is not evaluated.

## Primary outcome: focus selection

| Model | Unique correct | Wrong | No focus | Multiple focus |
| --- | ---: | ---: | ---: | ---: |
| Shipped FocusRing |0/48|0|0|48|
| FDR-007 |1/48|22|0|25|
| FDR-008 |1/48|22|24|1|

Shipped and007 produce multiple focus on all24 cinema_rows frames;008 selects
none on all24. On album_grid, both candidates produce22 wrong,1 correct and1
multiple. The sole unique-correct frame for both is `album_grid:synth-6`.
Shipped produces multiple focus on all24 album_grid frames.

## Paired target classification

| Model | TP | FN | FP | TN | Recall | False-positive rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Shipped |38|10|44|4|79.17%|91.67%|
| FDR-007 |2|46|14|34|4.17%|29.17%|
| FDR-008 |2|46|1|47|4.17%|2.08%|

Each stratum below reports **TP/positive support; FP/negative support** on the
same paired inputs, not independent statistical trials.

| Stratum | Shipped | FDR-007 | FDR-008 |
| --- | --- | --- | --- |
| Dense dark media |15/16;14/16|0/16;8/16|0/16;0/16|
| Bright artwork |3/8;6/8|0/8;4/8|0/8;0/8|
| Gray/blank placeholders |6/8;8/8|0/8;0/8|0/8;0/8|
| Dock neighbors |10/12;12/12|0/12;0/12|0/12;0/12|
| Fixture detail-action buttons |4/4;4/4|2/4;2/4|2/4;1/4|
| Actual Photos buttons |unavailable|unavailable|unavailable|

All supplied samples are dark theme. Light/highContrast support is unavailable.
Fixture detail-action buttons do not close the Photos-button coverage requirement.

## Complete-frame competition and deltas

| Model | TP /48 | FN /48 | FP /1,104 | TN /1,104 | Crop accuracy |
| --- | ---: | ---: | ---: | ---: | ---: |
| Shipped |38|10|988|116|13.37%|
| FDR-007 |2|46|299|805|70.05%|
| FDR-008 |2|46|23|1,081|94.01%|

An always-unfocused classifier scores95.83% on these competition crops. FDR-008's
94.01% therefore cannot establish useful focus selection. Compared with007, it
removes276 false positives and24 multiple-focus outcomes but gains **zero** focus
hits or unique-correct frames. The24 changed frames become no-focus. Compared
with shipped, both candidates lose36/48 true focus hits (75 percentage points of
recall). These are same-input deltas; no historical-corpus numerical delta is used.

## Error analysis and priorities

1. **Recover appearance recall while retaining negative discrimination.** Both
   candidates miss every positive in the four main non-button strata (44/44).
   Existing training fit has not transferred. Do not infer that more epochs or
   a lower threshold will fix this; these data remain validation, never training.
2. **Context-dependent wrong button selections.** FDR-008's23 competition false
   positives are all Fixture detail-action controls, despite only1/48 false
   positives in the paired baseline-negative set. Full-frame competition is
   essential; paired target accuracy alone misses this failure.
3. **Shipped false-focus saturation.**988/1,104 competitors cross0.85, including
   all276 dock negatives,179/184 placeholders and127/184 bright-artwork negatives.
   This warrants hard-negative appearance coverage in a future training-only
   collection, not threshold tuning on the final challenge.
4. **Qualify missing source independence and coverage before a launch.** No exact
   pixel leakage was found against3,789 prior images or across reserved roles,
   but source/asset/journey ancestry remains unreviewed. Photos and non-dark
   appearance support remain explicit gaps.

Representative paired misses include `cinema_rows:synth-16:pair:1` (FDR-007
~0.000029; FDR-008~0.000004). Shipped labels `cinema_rows:synth-0:pair:0` at1.0;
FDR-007 labels `cinema_rows:synth-2:pair:0` at~0.994655. Both candidates falsely
label `album_grid:synth-6:pair:0` (~0.97248/~0.971356). Full per-member scores,
miss/false-positive inventories, per-group/control/theme metrics and selected IDs
are retained in `comparison/{shipped,fdr007,fdr008}.json` and `comparison.json`.

## Runtime scope

Pinned runtime: Python3.12.9, Torch2.7.0, NumPy1.26.4, Pillow11.3.0, macOS26.4.1 arm64.
Shipped uses CoreML CPU;007/008 use PyTorch CPU with2threads/batches32. Shipped
median per-item inference1.30ms; median per-process model load14.45ms. Candidate
amortized batch inference19.53/19.82ms per crop. These differently scoped backend
timings exclude different overheads and are **not** export parity, device latency
or evidence that one backend is intrinsically faster. Model-stage totals69.81,
25.30 and25.56seconds include additional work.

Protocol seal: `d6fd77c74fc5de7bf672e71b252a54173e387ea54f94c5919eb06a3d95a3c460`.
Exact model hashes, source/runtime/implementation references, membership and settings
are in `protocol.json`; separate reports preserve the shipped and two candidate IDs.
No model, threshold, crop margin, training data, exported package or release changed.
