# CHECKPOINT404 — restore training without changing its result

## Scope

research-host-NUIAK extends the existing crop trainer and queue.
Standard models, crop preprocessing, thresholds, and retained successes remain unchanged.
This work does not promote a model or qualify detector restoration.

## Measured restoration

The comparison uses the retained TEMPLATE395 membership and a pinned HCF crop initializer.
One process completes 30 epochs without interruption.
A second process stops after epoch 12 and writes all training state.
A third process restores that checkpoint and completes epoch 30.

The first comparison finds exact agreement in these values:

- Model tensors and final model bytes.
- Optimizer and scheduler state.
- Python, NumPy, Torch, and MPS random state.
- Training loss history.

The comparison takes 17.4 s on the tested MPS runtime.
This small test qualifies its exact configuration, not arbitrary models or data sizes.
The original queue attempt fails its input-read receipt check after producing the comparison.
The explicit successor completes after repairing that check without changing the trainer or comparison settings.
Preserve both attempts.
The queued restore adapter then completes in 5.2 s and produces identical final model bytes.
All 154 focused checks and the offline Swift checks pass.
The Swift run contains 14 XCTest checks and 174 Swift Testing checks.

## Rejected restoration

The background test rejects a missing optimizer, a changed seed, and changed row order.
Each rejection occurs before a new checkpoint appears.
The original checkpoint stays unchanged.

## Queue admission

Use `checkpoint-v1` only with `checkpoint_restore404.run`.
Pin the checkpoint, qualification report, membership, and initializer.
Require the tested training contract and the same 30-epoch endpoint.
Keep each continuation within 800 s and its cumulative approved storage and time limits.
Use a new immutable successor and output directory.
Do not repeat a completed experiment to occupy the worker.

The only retained timeout already has a successful 30-epoch successor.
It does not need continuation.
Capture failures for small and wide controls need valid native geometry, not more training time.

## Native selection comparisons

Nine background jobs compare known boxes, raw outline proposals, and fixed inset mapping.
They use 74 retained frames from 10 named groups.
These inspected groups are development evidence, not an independent final audit.

| Profile | Known boxes | Raw proposals | Mapped proposals |
| --- | --- | --- | --- |
| Standard | 36 correct, 1 correct abstention | 36 misses, 1 correct abstention | Unchanged from raw |
| HCF | 35 correct, 1 miss, 1 correct abstention | 3 correct, 33 misses, 1 correct abstention | 5 correct, 31 misses, 1 correct abstention |

The mapping loses 1 previous raw-proposal success on a tall control.
Do not advance it as a replacement despite its net gain.
The limited no-focus pair produces no false selection in any arm.
This pair does not establish broad no-focus performance.
Known boxes remain a diagnostic upper bound.

## Next decisions

Prioritize proposal coverage and the tall-control mapping failure before more crop training.
Test any correction against the same retained successes without changing thresholds.
Qualify detector restoration separately only when an unfinished useful detector run needs it.
Keep future continuations below ordinary approved work.
