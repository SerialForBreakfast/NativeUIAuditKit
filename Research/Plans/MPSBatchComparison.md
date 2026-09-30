# TRAIN-MPS-COMPARE-14

User continuation assigns the next bounded batch8/16MPS comparison. Four isolated
trials in8,16,16,8order; same512train/64validation membership, local yolo11m.pt,
640long-side rectangular preprocessing,seed42,2epochs, existing trainer/OHEM and
warmup. Use the existing diagnostic supervisor with an aggregate1800s deadline;
each trial retains8GiB launch /3GiB runtime available RAM,10GiB disk reserve,
2GiB output cap. No automatic retry after blocked/failed/stopped trial. Four trial
outputs bound overall artifacts to8GiB. All weights diagnostic-only.

Refresh source pins explicitly under a new versioned plan, preserving old plans
and receipts. v1diagnostic remains batch8only; v2supports only8or16. The comparison
runner must verify identical membership/taxonomy/initialization/runtime/settings
apart from batch. Actual MPS backend, workers, AMP, batch and complete epoch/batch
counts must match before publishing a comparison. Aggregate supervisor deadline
also includes staging time and is checked before child launch.

Primary: first-epoch training wall (batch intervals plus inter-batch gaps), seconds
and512images/second, both repetitions and median/range. Epoch1uses identical source
membership before OHEM replacements; padding groups and optimizer warmup schedules
can differ with batch size. Epoch2membership can diverge via batch-loss OHEM.
Report epoch2and whole-trial time separately, not as identical-input pure GPU speed.
No extra synchronization, steady-state, causal bottleneck or quality-equivalence
claim. No automatic new default or full training. Stop for actual resource failures.

Deliver tested real supervisor/worker integration, frozen plans, receipts, bounded
runtime results/partial disposition, timing comparison and one adoption decision.
Offline focused Python and required Swift checks precede launch. No TTR action changes.
