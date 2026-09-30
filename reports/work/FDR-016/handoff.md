# FDR016 — complete, not qualified

One approved run completed30epochs on MPS,PID82133,23:44:27–23:45:58UTC,
90.83seconds including preflight. No timeout. No encoder loaded;577-parameter
fresh head reused FDR015's726training/471validation feature vectors.
Identical corpus, initial predictions and selection rules verified.

| Final diagnostic | FDR015 | FDR016 |
|---|---:|---:|
| First-choice ranking, complete frames |11/13|11/13|
| Fixed0.85correct frame decisions |0/13|2/13|
| Fixed0.85no-focus decisions |13/13|11/13|
| Retention correct |9/18|12/18|
| Real positives detected |0/35|3/35|
| Real false positives |1/418|16/418|
| Real crop AUROC |0.7261|0.7070|
| Eligible epochs |0|0|

Home ranks remain2and8; margins worsen from−0.0224/−0.1367to−0.0834/−0.1870.
The exploratory target—fix one Home case while preserving11/13ranking—failed.
No best.pt selected. Last.pt is diagnostic-only; no export or promotion.
All14,601stored predictions replayed through unchanged metrics. [Comparison](comparison.json)
includes31snapshots and nine retention-pair probability/logit margins each. Training
pair predictions were not retained; no new inference manufactured those diagnostics.
13complete frames/27unavailable; reused development screens are not independent
testing or end-to-end detector/CoreML qualification. Paired batches also change
batch correlation; this is not a pure loss-only causal comparison.

## Decision and next assignment

Do not repeat this unchanged corpus/loss approach. Prioritize crop/data alignment:
distinguish detector/icon-body from caption-inclusive wrapper geometry; prepare
matched native artwork positives and bright unfocused competitors with different
sizes/density, then separately approve a data-informed experiment. Do not lower
thresholds to call this a pass. Encoder fine-tuning remains an experiment, not an
assumed remedy. Newly received native112 data did not enter this run.

## Outcomes

- Software: paired adapter integrated; cache/order/approval/legacy rejection tests
  and offline Swift build/test pass (tests-final.log and native112 Swift logs).
- Data: frozen363training+9retention pairs and453real selection crops preserved.
- Integration: cached features used without encoder inference; native112 production
  crop QA complete separately, with receipt/geometry response for TTR.
- Model: zero eligible checkpoints; shipped model unchanged.

The model-workflow skill kept preprocessing, one-run scope and gates fixed.
