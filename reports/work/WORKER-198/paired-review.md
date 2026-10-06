# Worker198 paired report review — 2026-10-06

Transfer accepted; metric report requires correction. Received45,454bytes,
9regular files /1,021,747expanded bytes. Archive SHA256:
`c4fd4af11aa6821dd06c53eac173e99ec1ff85b6ca7edaaba79dcad3eb2f01d2`.
Local evidence: `artifacts/paired-return01/worker198-paired-return01/`.
Report02 SHA256:
`b7c3e6ff1cc822669475a4cd130851fe987faa8f0d84520d76e49b710316fa15`.

Reviewed complete report source/tests. Worker reports four tests and1.836s CPU;
no GPU. Its machine-path-bound full CLI was not rerun locally. Independent helper
reproductions confirm score0.02 correct boxes count as TP at the export floor,
and two identical targets/one matching box incorrectly produce localization_FN.
Per-class sums reconcile.

Corrections: retain export-floor AP but add fixed0.25 operating counts and observable
low-confidence candidates; fix assignment competition; report unsupported AP/deltas
as unavailable, retaining FP counts. Same inputs, CPU600s/20MiB, no new inference.

Raw-floor totals are **not** deployment operating metrics:

| Partition | Support | Control TP/FP/FN | Treatment TP/FP/FN |
|---|---:|---|---|
| Fit |477|453 /3630 /24|454 /3632 /23|
| Page development |37|34 /484 /3|37 /351 /0|
| Combined retained |1524|1081 /14700 /443|1109 /13390 /415|

Worker owns corrected source/report; NUIAK owns independent acceptance. No admission,
model gate or promotion follows. Corrected case-linked operating failures will guide
the next experiment. Publication/readback and acknowledgment are separate; see
[feedback-loop.md](feedback-loop.md).

## Corrected return04 accepted

65,218bytes /9members /1,798,977expanded bytes; archive
`352c9ce779282240091e6c99c112363bbf6749805d7397160c8d11c20db85e39`.
Report `c175552677291d0654e68a8d6e4e306b24d180062dddf808efac3a091ee65589`.
All41per-class operating counts/AP independently match existing NUIAK scorer across
both models and all585windows. Two reviewed correction tests pass locally0.009s,
including deterministic fixture-backed actual report entrypoint; full six are peer evidence.

Operating control→treatment TP/FP/FN: fit420/246/57→422/254/55;
page34/33/3→37/27/0; combined942/1747/582→1080/1597/444.
Accepted as raw-ROI diagnosis, not full-frame qualification. Top-level failure ranking
still uses export-floor counts; use operating case fields for next prioritization.
Low-confidence candidate lists may include targets already matched at operating score.
No new GPU work needed. Exact transfer receipt and acceptance in response05;
acknowledgment and sender cleanup remain separate.
