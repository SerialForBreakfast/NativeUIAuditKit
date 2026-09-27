# ADR-0011: Measure training efficiency before changing the experiment

- Date: 2026-09-24
- Status: planning decision recorded at maintainer request; execution changes require separate approval.
- Scope: local YOLO training, initially Run 013; applicable measurement principles also inform FocusRing.
- Supersedes: unsupported performance assumptions in [ADR-0006](ADR-0006-Training-Iteration-Efficiency.md), not its historical experiment records.
- Delivery: [TrainingEfficiency](Plans/TrainingEfficiency.md); ownership/status only in [Tasks](../Tasks.md).

## Context and observed evidence

Run 013 makes a long feedback loop concrete: its saved results showed epoch durations
of 39.07, 36.95 and 35.98 minutes. At roughly 37 minutes/epoch, 150 epochs cost about
92.5 hours in total if throughput stays constant and early stopping does not fire.
“35%” within epoch 3 is not 35% of the run. Neither convergence at epoch 75 nor a
specific early-stop date can be inferred from three improving epochs.

This is a read-only September 24 snapshot, not a fresh process-health assertion.
Evidence is retained locally in `NativeUITrainer/yolo_runs/phase6a_r013/args.yaml`,
`results.csv`, `NativeUITrainer/training_6a13.log`, and the Run 013 entry in
[ExperimentLog](ExperimentLog.md). Installed source examined was Ultralytics
8.4.124 under `.venv-yolo/lib/python3.13/site-packages/ultralytics/`.
The live process interpreter must still be reconciled with that installation.
Process/hardware inspection was sandbox-denied; total memory, GPU utilization and
actual stage costs were not established. No benchmark or job modification occurred.

| Finding | Meaning and limitation |
|---|---|
| Saved configuration: YOLO11m, 640 pixels, batch 8, 14,540 training images, 150 epochs, AdamW, cosine schedule, patience 15 | A useful baseline, not proof these settings are optimal. The r7 corpus differs from the older r6 corpus. |
| Generic local `weights/yolo11m.pt`; startup transferred 643/649 items | Pretrained initialization, not random scratch. Reconcile departure from the earlier Run 009 UI-weight plan with the run owner; do not restart on assumption. |
| Installed trainer forces workers to 0 for MPS/CPU; AMP check returns false there | Saved `workers: 4` and `amp: true` do not establish effective workers or mixed precision. Saved arguments precede some runtime overrides. |
| Installed dataset disables mosaic when rectangular batching is enabled | `rect: true` plus `mosaic: 1.0` is not evidence mosaic ran. Audit effective augmentation before comparing experiments. |
| Installed detection fitness weights mAP@0.5:0.95 | Patience is not simply “15 epochs without improved mAP@0.5.” Record the actual stopping/checkpoint criterion. |
| OHEM callback assigns each image a batch-loss proxy and calls `.detach().cpu()` | Not true per-image loss mining; possible synchronization cost, not yet a measured bottleneck. |
| OHEM rebuilds dataset image/cache lists | Blindly enabling RAM cache may not retain its benefit. Rectangular batch metadata after resampling also needs a correctness test, not an assumed defect. |
| `last.prev.pt` callback copies `last.pt` after save | A mirror is not a proven previous-generation or atomic recovery guarantee. `save_period=-1` still permits last/best writes. |

Local implementation references: `scripts/train_ios_model.py`,
`scripts/ohem_callback.py`, and installed `engine/trainer.py`, `utils/checks.py`,
`utils/metrics.py`, `data/dataset.py`. These findings require a pinned audit receipt
before implementation; an untracked dependency upgrade could change their meaning.

## Decision

Optimize **wall-clock time to a qualified model**, with repeatable measurements and
unchanged data/evaluation integrity. Epoch speed alone, low allocated MPS memory,
or improving early validation scores do not establish compute efficiency or quality.

1. Preserve Run 013, its owner, checkpoints and outputs. Read-only audit and offline
   tooling may proceed; no concurrent MPS benchmark, inference or profiler. Pausing,
   resuming, replacing a run or changing its training semantics needs approval.
2. Produce a requested-versus-effective configuration receipt, then a bounded
   performance benchmark. Measure loading/augmentation, training, validation, OHEM
   and checkpoint costs separately; report unattributed/overlapping time honestly.
3. Test batch size first at the same model, resolution and data ordering. Inspect
   gradient accumulation, effective batch, weight decay and warmup before calling
   any batch change semantically equivalent. Test cache/OHEM only after compatibility
   checks. Do not assume larger batches, more workers, AMP or caching will help.
4. Compare compatible UI-checkpoint initialization against generic initialization
   only in a separately authorized learning experiment. A smaller architecture is
   an optional screening experiment, not a substitute for the accepted model gates.
5. Freeze evaluation membership and metric implementation. Use development/validation
   data for tuning; untouched final tests are not benchmark input or repeated tuning
   feedback. Unsupported classes remain unavailable, not zero. New corpus versions
   do not retroactively make historical mAP comparable or satisfy DS-G8.
6. Adopt measured improvements through an explicit continue/resume/new-experiment
   decision. A resume preserves experiment state; new initialization, changed sampling
   or other semantic changes require an independently identified experiment.

No automatic epoch reduction, lower input resolution, disabled validation, patience
reduction, mixed-precision forcing, data dropping, service reset, application shutdown,
cloud transfer or hardware purchase follows from this ADR. Keep 640-pixel detail in
the first throughput comparison. Failed pilots yield diagnosis, not retraining loops.

## Alternatives and consequences

- **Leave everything unchanged indefinitely:** preserves comparability but leaves a
  multi-day cost unaudited. Keep the current run, investigate the next configuration.
- **Change several knobs now:** risks losing the current experiment and prevents
  attributing a gain. Rejected without controlled evidence and execution approval.
- **Immediately switch hardware or architecture:** potentially useful, but performance,
  cost and quality benefits are unmeasured. Keep outside this initial tranche.

Measurement consumes some compute, so cap the benchmark and stop expanding the matrix
once a useful decision is supported. Prefer a few meaningful comparisons over a broad
hyperparameter search. Preserve recovery writes until a tested replacement exists.
No speedup percentage is promised. No new model gate is passed by faster training.

## Primary references

Public documentation provides context; the pinned installed implementation governs
an individual run. These sources can evolve independently of Ultralytics 8.4.124:

- [Ultralytics training settings](https://docs.ultralytics.com/modes/train/): batch, caching and loader controls.
- [Trainer implementation reference](https://docs.ultralytics.com/reference/engine/trainer/): runtime setup and training behavior.
- [AMP checks](https://docs.ultralytics.com/reference/utils/checks/#ultralytics.utils.checks.check_amp): backend-dependent enablement.
- [PyTorch MPS profiler](https://docs.pytorch.org/docs/main/generated/torch.mps.profiler.profile.html): optional bounded profiling, not an assumed diagnosis.

## Revisit condition

Review after TRAIN-EFF-B measurements and TRAIN-EFF-C's authorized learning pilot, or
after a dependency/backend upgrade. Keep software verification, data eligibility,
runtime integration and model qualification independently reported.
