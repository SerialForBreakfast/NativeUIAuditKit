# Reviewed Office focus comparison

2026-09-28. One approved run, fixed0.85 threshold, original boxes and production
16%/256×256 crops. Eight correlated frames,113 controls:8 focused/105 unfocused.
**FDR-009 regresses on this development set; do not promote it.** This is not a
generalization estimate or proof that one training change caused the regression.

| Measure | Shipped CoreML CPU | FDR-009 epoch3 PyTorch CPU |
|---|---:|---:|
| Predictions / expected |113/113|113/113|
| Correctly detected focused controls |4/8|1/8|
| Misses |4|7|
| False positives |11/105|15/105|
| Recall |50.0%|12.5%|
| Precision |26.7%|6.25%|
| Accuracy (negative-heavy, not headline quality) |86.73%|80.53%|
| Explicit Photos pairs, both states correct |2/2|0/2|

Candidate-minus-shipped: recall−37.5 percentage points; false positives+4;
misses+3; accuracy−6.19 percentage points. These deltas compare identical members
and metrics, but different deployment backends. No export/latency-parity claim.

| Screen / control | Focused / unfocused support | Shipped TP / FN / FP | FDR-009 TP / FN / FP |
|---|---:|---:|---:|
| Home / collectionItem |4 /92|1 /3 /11|1 /3 /15|
| Photos Welcome / primaryButton |3 /3|3 /0 /0|0 /3 /0|
| Settings / listRow |1 /10|0 /1 /0|0 /1 /0|

Photos has two distinct reviewed pairs plus a separately retained repeat state;
three positive crops are not three independent button families. Both models detect
the single focused Music Home crop; neither detects the three focused Photos Home
crops. General is the only positive Settings row here, so its miss is narrow evidence.
Zero positive predictions makes precision unavailable for those affected subgroups,
not a measured zero. JSON metrics preserve nulls.

## Explicit Photos pairs

| Reviewed control | Shipped focused / unfocused score | FDR-009 focused / unfocused score |
|---|---:|---:|
| View All iCloud Photos |0.984375 /0.000060|0.005036 /0.001197|
| View Only Shared Albums |0.997070 /0.000105|0.003774 /0.000662|

Both candidate paired score differences are positive but far below0.85. That does
not justify threshold tuning; Home already has15 false positives, several near1.0.
No new Home pairs were inferred from copied annotation IDs.

## Numbered evidence and interpretation

All37 model-specific errors have original-frame context, a marked box, the actual
production crop, sample ID and score in [error-sheets/index.json](error-sheets/index.json).
Representative agent-reviewed sheets (visual observations, not new human labels):

- [001: General missed by shipped](error-sheets/001-shipped.png), also missed by FDR-009.
- [002: Focused Photos Home tile missed](error-sheets/002-shipped.png), both models.
- [005: Unfocused Pluto debug artwork falsely focused](error-sheets/005-shipped.png), shipped.
- [017: Shared Albums white focused button missed](error-sheets/017-fdr009.png), candidate.
- [023: Unfocused red artwork](error-sheets/023-fdr009.png), candidate≈0.99995.
- [027: Unfocused Music](error-sheets/027-fdr009.png), candidate≈0.99979.
- [030: Unfocused orange artwork](error-sheets/030-fdr009.png), candidate≈0.99898.
- [034: Unfocused Podcasts](error-sheets/034-fdr009.png), candidate≈0.95971.

Appearance shortcuts and insufficient matched negatives are hypotheses supported
by repeated high-scoring unfocused artwork. Counterexample: the shipped model's
strongest false positives are different artwork. Native-white-control transfer is
another hypothesis; shipped succeeds on Photos buttons while both miss General.
The required next observation is the same reviewed control in both states across
separate layouts/background contexts, not another repeated screenshot or a lowered
cutoff. Wide controls are visibly stretched by production preprocessing; this is
expected behavior, not evidence of corrupt crops or a reason to relabel boxes.

## Repetition and provenance

Full113-sample counts remain primary. Keeping one representative per exact crop
pixel group gives111 crops: unchanged TP/FN/FP for both models, two fewer TN.
Shipped accuracy86.49%, candidate80.18%; recall/precision unchanged. This sensitivity
does not establish111 independent examples. Near-duplicate full frames stay retained.

Actual hashed indexes checked:564 training/retention crops (546+18),1344 reserved
rows (1248 development competition/pair rows and96 challenge pair rows),20 historical
protected/visual rows. No exact byte/retained-pixel-hash matches with the Office batch.
Eight historical visual rows have frame references only, no crop references in that
index. Source sessions/layout ancestry and exhaustive shipped training history remain
unknown. Protected rows were metadata/hash-compared only, never scored or displayed.

Complete-frame candidate coverage is unknown: no unique-selection accuracy,
detector recall, transition accuracy or autonomous navigation qualification is reported.
Training eligibility remains false. Model/release gate remains unassessed.

## Recommendation

Request the targeted additional data in [next-assignment.md](next-assignment.md).
Keep this reviewed session fixed as a regression set. Do not train on it, retrain
automatically, change preprocessing/thresholds, export or replace shipped weights.
