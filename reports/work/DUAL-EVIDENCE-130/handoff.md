# DUAL130 — cached dual-evidence experiment, DTM032 rejected

Software verified. Original source roles/ancestry preserved; monotonic contrast
variants training-only as explicitly scoped. Producer integration unassessed.
Model retention gate failed; no export, deployment or promotion.

## Experiment outcome

DTM031frozen raw logit plus1152new correction weights over raw and affine-normalized
residual features. One600epoch Adam0.01 seed42 CPU2threads fixed-last fit. Existing
gradient loop factored into reusable `fit_change_features`; tests prove identical
weights/history versus pixel entrypoint, with frozen parameters preserved.

Training:207originals+2×433one-sided contrast views, plus226original identity pairs.
No translated/cropped view admitted. Features are a research contract, not deployed
CoreML inputs. Thresholds remain0.15/0.85. Every original/10stress baseline replay
is bit-exact before fitting.

| Measure | DTM031 | DTM032 |
|---|---:|---:|
| Original transitions |207/207|201/207|
| Original identities |226/226|226/226|
| Before-contrast identity negatives |0/226|211/226|
| After-contrast identity negatives |0/226|209/226|
| Before-dim original transitions |172/207|93/207|
| After-dim original transitions |169/207|102/207|

Lost originals:3,7,17,21,23,25; five confidently wrong, one abstention. New correction
does not separate nuisance changes from useful evidence adequately. Reject it; do
not trade away original retention for negative recovery or fit more unchanged epochs.
All values are exposed-data/constructed-view diagnostics, not independent accuracy.

## Evidence / efficiency

- Protocol/cache: `artifacts/ready03/protocol.json` and11feature arrays, all hashed.
- Result/checkpoint: `NativeUITrainer/focus_ring_runs/dual130-dtm032/`.
  Checkpoint SHA256 `842eafe22ba9638e052c843794436ffe9b843e412113b7cd2f2e276b5de5748f`.
- Valid prepare48.673s; fit0.603s; execution including checkpoint/evaluation1.120s.
  Source decoding/normalization dominates; fit does not reload pixels or regenerate
  features. These timings exclude the two preserved failed preparations.
- Both actual CLI modes exit0; PID18943. Checkpoint replay and identity probability
  preservation exact. Output budget2GiB, actual small feature/cache artifacts ignored.
- 14focused Python tests and offline Swift build/139tests pass. Logs `.build/dual130-*`.
  `git diff --check` passes. Existing source/data/weights and dirty changes preserved.

First preparation failed historical batch replay; second isolated strided-cache
sigmoid differences≤3.73e-9. Contiguous logits with original424+9batch boundaries
restore bit-exact baseline without relaxing tolerances. Both failures occurred
before optimizer updates; their directories/logs are retained. Regression tests
cover the layout effect and feature-trainer parity.

## Next substantial tranche

Test a narrowly scoped nuisance indicator using full-frame affine residuals and
spatial residual support, comparing abstention rather than forced unchanged output.
Measure how many original positives it would suppress before adopting any guard.
Use cached outcomes to choose cases; reserve actual TTR feedback as separate
integration evidence. No assumption that synthetic affine equivalence proves native
focus identity. Keep shipped/current passive artifacts unchanged.
