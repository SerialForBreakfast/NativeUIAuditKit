# Attempt02 — completed on Apple M4 / MPS

2026-09-30. User explicitly resumed after closing applications. The unchanged
plan passed all pins and resource guards. Child PID85595 exited0 after189.832s
(3m10s), below1800s. Two epochs,128training batches,512training/64validation
members; original checkpoint, images, labels and source pins reverified afterward.

## Measured host-wall costs

| Interval | Epoch1 seconds | Epoch2 seconds | Total seconds |
|---|---:|---:|---:|
| Training batch intervals |67.651|66.107|133.759|
| Between-batch gaps |9.826|9.617|19.443|
| Validation |5.371|4.264|9.635|
| Checkpoint save |2.114|0.578|2.692|
| Checkpoint mirror |0.045|0.242|0.287|
| Epoch total |85.423|81.210|166.633|

Batch intervals account for80.3%of recorded epoch wall time. Nested within them:
preprocess0.228s, optimizer13.192s and OHEM batch-loss recording0.039s total.
OHEM epoch replacement adds0.022s total. Do not add nested measurements again.
The remaining23.2s of supervisor elapsed time includes startup/final evaluation/
cleanup, not a separately measured stage. No GPU synchronization was injected;
these are host-wall costs, not isolated GPU kernel or pure loader times.

OHEM epoch1 requested102replacements, fulfilled94, skipped8incompatible slots.
Epoch2 requested83, fulfilled75, skipped8. Its second request count is based on
the distinct images actually seen after first-epoch replacement, not all original
512images. Both callbacks and subsequent training batches completed without
geometry/alignment errors. This verifies execution, not OHEM's quality benefit.

Actual runtime: MPS/Apple M4,workers0,AMPfalse,recttrue,batch8. Accumulation was8
at setup/end; warmup caused19optimizer steps in epoch1 and8in epoch2. Timing is
therefore early-training diagnostic evidence, not a steady-state comparison.
PyTorch warned that some MPS operations lack deterministic implementations with
warn-only determinism enabled. Seed42does not establish bitwise reproducibility.

## Resource and artifact accounting

94supervisor samples: minimum available RAM6.376GiB (>3GiB guard), minimum free
disk45.683GiB (>10GiB), maximum sampled artifact footprint724.407MiB (<2GiB).
These are sampled extrema, not proof of every transient. Final footprint493.994MiB
after the trainer's normal optimizer stripping; no agent cleanup/deletion occurred.
Launch available RAM12.946GiB passed8GiB guard. No resource stop or download occurred.

The generated best/last/mirror weights remain diagnostic-only in attempt02.
Shipped weights are unchanged; no export, promotion or model qualification claim.

Paths below are relative to `generated/attempt-02/`:

| Artifact | SHA256 |
|---|---|
|receipt.json|4a531f073829411be2f24aba7efdbcb470467ddbc997304128fa00897d9aa14a|
|runs/diagnostic-only/host-timing-31588d4ae18d49cf826151e80d19c6da.jsonl|30e1b56b099f56c86a601768dabce1062bcc46fa5918b7ff8c9ee61e4b46f401|
|runs/diagnostic-only/results.csv|147266b46a8aa3f62da514dfc9df5307a056d9dbe7aa262888e804e9ab41a99f|
|runs/diagnostic-only/weights/best.pt|315a55dff1b7de8eefa7f4e4f6292be96c436fae3f6983036f93d5f08c2d7ed3|
|runs/diagnostic-only/weights/last.pt|0e04df63c697d32897d3a6f5c5648763249c749a64a45a4e725bf101b0ecc560|
|runs/diagnostic-only/weights/last.prev.pt|175a5cd1470bb7866532fe55337815c0a2912854493ffae1ec18188330283cce|

## Decision

OHEM callback and checkpoint costs are not the dominant measured bottleneck in
this trial. Focus the next efficiency experiment on the training batch path:
propose a bounded matched batch8/16MPS comparison, preserving source initialization,
data, input-size and memory safeguards and reporting warmup/accumulation effects.
No comparative speedup or quality equivalence is established yet; do not launch
another full run or rewrite the trainer on these timings alone. The separate
tvOS focus data/transfer issues are not resolved by this iOS efficiency diagnostic.

No code changed in this continuation. Prior30Python/123Swift passes remain
applicable; fresh verification covers actual execution, terminal receipt,128batch
accounting, frozen576input/source pins and artifact hashes. TTR coordination not
applicable. No process remains running from this diagnostic.
