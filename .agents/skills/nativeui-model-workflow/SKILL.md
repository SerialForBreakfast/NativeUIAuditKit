---
name: nativeui-model-workflow
description: Train, evaluate, export or diagnose NativeUIAuditKit YOLO11 and FocusRing/CoreML models with pinned data, preprocessing and evidence. Requires separately assigned model execution.
---

# NativeUIAuditKit model workflow

Read [CurrentState](../../../Research/CurrentState.md), your packet in
[Tasks](../../../Tasks.md), relevant BestPractices and the
[operational lessons](../../../Research/WorkerExecution/references/operational-lessons.md#dataset-and-evaluation-invariants).
A plan, available corpus or passing software test does not authorize a run.
Preserve shipped models; no automatic candidate loop or promotion.

## Runtime and preflight

Use the packet's approved pinned interpreter/environment. The ordinary repository
environment is `.venv-yolo/bin/python`, but the recorded CoreML export lane uses a
separately approved resident environment; do not silently switch back in subprocesses.
Diagnose imports/optimizer/trace/conversion/load independently using the
[residency procedure](../../../Research/WorkerExecution/references/operational-lessons.md#coreml-and-dependency-residency).
No automatic downloads, dependency reinstall or external environment creation.

Keep configured YOLO_CONFIG_DIR, MPLCONFIGDIR, TORCH_HOME, Python bytecode/temp,
Swift caches, logs and isolated output directories project-local. Set cache
environment before library imports. Do not repurpose HOME/CODEX_HOME or assume
these settings contain Apple-managed runtime writes; those need explicit scope.

Before model execution:
1. Inspect the existing script's actual interface/side effects. A flag called
   dry-run may still import/load/write; validation-only must never train/download.
2. Pin local checkpoint, dependency versions, model/category map, corpus membership,
   preprocessing, metric implementation, thresholds and new output destination.
3. Verify every required pixel/annotation and split eligibility. Original broken
   symlinks, labels, old metrics and caches are not a usable corpus. Reconstructed
   pixels create a new baseline; missing classes stay unavailable, not AP0.
4. Keep fresh checkpoint initialization, interrupted-run resume and evaluation-only
   modes distinct. Log each authorized training experiment before launch.
5. Inspect startup and bounded progress; preserve failed output. New run/resume,
   export, physical comparison and promotion each retain their assigned scope.

Use existing exporter, assembly, trainer, evaluator and cropper, not a parallel
implementation. Read current help/source before forming commands; historical default
paths/weights are not an approved launch configuration.

## Preprocessing and labels

- Shipped YOLO detectors use their established single-pass letterbox and CoreML NMS
  path. Preserve original-image coordinate recovery. Do not apply historical blanket
  `.scaleFill` advice to YOLO or replace its evaluator with Create ML's.
- BP-25 `.scaleFill` / custom Vision evaluation concerns historical Create ML
  objectPrint models; `MLObjectDetector.evaluation(on:)` is not the portrait evaluator.
  Use that historical path only for an explicitly assigned compatible model.
- Vision boxes are normalized bottom-left; YOLO centers are top-left:
  `cx=x+w/2; cy=1-y-h/2`. Identify the input coordinate convention before conversion;
  do not flip already top-left sidecars.
- FocusRing uses production `FocusRingClassifier.makeCrop`,16% expansion,256×256,
  per-frame top-left pixel bounds. Never substitute `CGImage.cropping(to:)`.
  Compare source-pinned actual scoring crops, including fractional/clipped boxes.
- Fixture requested focus and prediction files are not labels. Retain observed
  callbacks, scene brackets, actual geometry and raw-to-crop hashes. Unavailable
  state remains unknown. Visual focus and VoiceOver alignment are separate tasks.

## Training and evaluation

Freeze source/recipe/journey/duplicate-connected groups before splitting. Different
seeds/adapters do not establish independence. Reserve final evaluation before
failure-driven tuning; bind reservations to actual reviewed membership. Sampling
weights use training partitions only. Distinguish development experiments from
full-corpus and physical qualification. Do not silently relax quotas or class gates.

Report per-class/theme/control support, misses, false positives, abstentions,
frame-level wrong/no/multiple focus and cold/warm latency. High tile accuracy can
hide an unusable focus selector. Temporal differences need genuine focus-switch and
no-op evaluation, not only reference-to-focus arrivals. Compare identical compatible
inputs/settings; unavailable metrics never become zero or fabricated deltas.

Use focused behavioral tests during changes and real caller/CLI contract tests.
Run required offline Swift build/tests once at integrated code handoff. Reuse
unchanged evidence; no model execution or full build for prose-only edits.
Batch inference/crops within both decoded-pixel and item limits, preserving order.

## Export and delivery

FocusRing uses the vendored `scripts/focus_ring_backbone.py`, no timm or ONNX
detour; existing export uses `torch.jit.trace`. The established baseline remains
30epochs unless the assigned experiment explicitly varies it.

Verify PyTorch/CoreML preprocessing, outputs and decisions on frozen inputs; report
same-backend parity separately from CPU/GPU/ANE differences. Weight-only INT8 size
reduction is not a latency or generalization win. FocusRing's5MB limit means
5,000,000 total package bytes, not5MiB or rounded display size. Preserve failed gates.

Record exact loaded artifact identity/backend and scoring completeness, not merely
the bundled model filename. Detailed execution receipts must serialize derived
counts and reject inconsistent wire payloads.

Compiled promoted resources belong in the models package; raw weights, datasets,
unpromoted packages and bulky reports remain gitignored/local. Follow
[ArtifactRetention](../../../Research/ArtifactRetention.md); never clean sole-copy
data or assume ignore rules remove already tracked history. No agent Git writes.

Handoff: commands/exit codes/timing, immutable data/model/config references, supported
and unsupported gates, four separate software/data/integration/model outcomes, and
one next meaningful assignment. A failed candidate yields diagnosis, not auto-retrain.
