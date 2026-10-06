# Run027 CUDA proposal-stage diagnostic

CPU-only evaluation on October6, exit0. No new model inference or threshold tuning.
Strictly validated worker predictions merged using existing `roi197_compare.merge`
and scored with existing `eval_run013.score`. Original frozen proposal records and
cached Run022 first-pass predictions unchanged. This is a **hybrid** pipeline:
retained Mac first pass plus resident8.4.173/CUDA Run027 second pass. It is not the
registered all-MPS comparison, independent new qualification, or a treatment result.

Custom all-point AP, not official COCO/Ultralytics AP; operating TP/FP at confidence
0.25/IoU0.5. All non-page class metric rows asserted identical to cached first pass.

| Population | Images / page support | First-pass TP/FP | With027 TP/FP | Page AP50 before → after |
|---|---:|---:|---:|---:|
| Fit diagnostics |216 /216|185 /38|202 /38|0.856008 →0.920804|
| Page development |96 /96|58 /14|72 /16|0.619261 →0.738180|
| Combined retained |2400 /600|249 /24|533 /24|0.858402 →0.931957|

Combined page AP50:95 rises0.494261→0.617944. Page development AP50:95
0.321576→0.433172. Fit diagnostic AP50:95 0.474462→0.545466. Do not interpret
fit improvements as generalization or omit the two added development false positives.

Accounting preserves every full-frame case, including no proposal:

- Fit:17added,122duplicate-operating,69no-unique-donor,8absent.
- Page:16added,23duplicate-operating,5no-unique-donor,52absent.
- Combined:284added,105duplicate-operating,103no-unique-donor,1908absent.

Checkpoint `0cd43172ba947576e30d48007b1da939dee51c713b63dd40cb1cb9828d323243`.
Returned prediction hashes and original input-content hashes remain recorded in
`artifacts/eval027-return01/worker198-eval027-return01/reports/work/WORKER198/EVAL027/terminal01.json`.
Canonical frozen mapping: `reports/work/IOS-PROPOSAL-197/artifacts/comparison01/protocol.json`.
This read-only diagnostic creates no replacement official report or altered seal.

Interpretation: the worker can return usable prediction artifacts for the existing
proposal mechanism. It does not isolate benefits of STYLE210's new examples, establish
CUDA/MPS parity, pass all model gates or authorize promotion. Next: same worker
inputs/environment with verified Run028checkpoint, then compare matched outcomes;
complete registered MPS scoring and fixed-sample backend checks after local training.
