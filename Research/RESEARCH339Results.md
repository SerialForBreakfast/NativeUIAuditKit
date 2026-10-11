# RESEARCH339 — queued training replay

Date: 2026-10-11 (UTC).
Design: [ADR-0026](ADR-0026-Queued-Research-Experiments.md). Plan: [RESEARCH339](Plans/RESEARCH339.md).
Experiment log: `RESEARCH339-R1`, registered before execution.

## Decision

The research queue reproduces the finished FOCUS329 30-epoch training run exactly.
The replayed weights file `last.pt` is byte-identical to the recorded file.
The queue is qualified for `training` jobs on local hardware. Capture, export, and promotion jobs remain refused.

## Delivered

- `scripts/research_queue.py` permits the `training` authority class. A training spec must carry these fields:
  - Experiment-log run ID. The entry must exist before submission and before each attempt.
  - Membership and initialization, each pinned by SHA-256 and checked before each attempt.
  - Epochs, storage budget, acceptance evidence, and resume mode.
- The queue checks free disk space against the storage budget plus 1 GiB.
- Resume mode is `restart` only. The trainers save weights only at the end, so an interrupted run restarts from epoch 0.
- Replay comparison adds these features:
  - Nested output names, such as `run/fit.json`.
  - An output folder name.
  - Ignore rules for each list entry, such as `history[].seconds`.
  - A numeric tolerance for each file.
  - SHA-256 comparison for binary files.
- Each ignore rule records how many fields it removed from the recorded file and from the replayed file.
- Each JSON file reports `matched` (within tolerance) and `exactlyEqual` (no tolerance) separately.
- `attempt.json` no longer records the host name.
- `scripts/test_research_queue.py`: 20 focused tests. The 6 new tests cover training fields, the log-entry check,
  the storage check, training pin changes, nested names, list-entry ignores, tolerances, and SHA-256 comparison.

## Replay result

| Measure | Recorded run | Queued replay |
| --- | ---: | ---: |
| Data preparation | 124.96 s | 128.46 s |
| 30 epochs (epoch-30 `seconds`) | 851.54 s | 837.49 s |
| Training and preparation (`fit.json`) | 996.95 s | 986.13 s |
| Full run with evaluation and report | 1,165.89 s | 1,152.44 s |
| Queue attempt wall time | not applicable | 1,154.7 s |
| Peak memory (`peakBytes`) | 5.73 GB | 7.73 GB |

All 12 compared files match. The tolerance of 1e-6 was not needed: every compared field is exactly equal.

| File | Result |
| --- | --- |
| `preparation.json` | Exactly equal after `seconds` and `peakBytes` are removed. |
| `run/registration.json` | Exactly equal after path mapping. |
| `run/epoch-0001.json` to `run/epoch-0030.json` (4 files) | Exactly equal after `seconds` and `peakBytes` are removed. |
| `run/fit.json` | Exactly equal. The ignore rules remove 30 epoch times and 4 epoch memory peaks from each file. |
| `run/training.json`, `run/evaluation.json` | Byte-identical. |
| `report.json` | Exactly equal after path mapping. |
| `run/completion.json` | Exactly equal, including the `last.pt` hash. |
| `run/last.pt` | Byte-identical. |

The process imports 139 repository modules. The result records the hash of each module.
The environment is Python 3.13.2, NumPy 2.3.5, PyTorch 2.13.0, and Pillow 12.3.0, on CPU with 2 threads.
The replay writes 4.7 MB. The recorded FOCUS329 files are unchanged; their hashes match the spec after the run.

## Findings

- CPU training with a fixed seed and 2 threads is bit-for-bit reproducible here. Exact weight comparison is a usable check.
- Peak memory is not reproducible. The replay peak is 7.73 GB, against 5.73 GB in the recorded run.
  The peak occurs during data preparation, before training. The script stops at 8 GiB, so the replay had about 0.86 GB of headroom.
  The cause is not measured. [BP-116](BestPractices.md) records this lesson.
- The queue cannot check that a step trains for the declared number of epochs. The epoch-file comparison checks this for a replay.
  A new training job that is not a replay needs its own epoch check in its decision rule.

## Limits and next work

- Epoch-level resume needs a trainer that saves and restores weights, optimizer state, and the random state after each epoch.
- A replay proves reproducibility for 1 run on 1 host. A second host can differ in floating-point results.
- The next queue features, in order:
  1. A `screen` extractor that records 1 primary metric per job, so `summarize` can rank ideas by effect, interval, and cost.
  2. A memory headroom report in each result, with the peak and the limit.
  3. An epoch checkpoint in the shared trainer, if runs longer than about 1 h enter the queue.

This replay produced no new candidate. No promotion, export, capture, device use, or data-role change occurred.
