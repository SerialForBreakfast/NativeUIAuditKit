# FOCUS-VISUAL-05 — input × learnable-vision comparison

Assigned October 1, 2026 by “ok continue and perform the next tranche,” following
the proposed four-cell matrix. Owner: Codex. This explicit four-run assignment
supersedes the default three-run count for this tranche only. No export/promotion,
capture, download, protected-test use, split changes or source annotation edits.

Status: completed October1,2026. All four runs executed, all39 retained evaluations
replayed; no eligible checkpoint. FDR021 unchanged. Specific appearance-coverage
finding and next decision: [handoff](../../reports/work/FOCUS-VISUAL-05/handoff.md).

## Input evidence before model execution

Reuse the exact FDR023 corpus (1550 train,315 development,18 retention), weights,
original images, actual rendered bounds and production detail crops. Build numbered
comparison sheets with original context, detail, aspect-fit diagnostic and a
candidate-centered square context window of side0.6×max(frame width,height).
This window is fixed for a given screenshot resolution, not proportional to the
candidate. Pad outside the viewport; never expand object labels to include shadow.
Inspect representative growth pairs, artwork, rows, tabs and clipped controls.
Measure target pixel dimensions/coverage and growth retention before dispatch.
The context stream complements, rather than replaces, the high-resolution detail
stream; wide/clipped controls retain their full detail input. Diagnostic aspect-fit
images do not silently replace production detail crops.

## Four matched arms

FDR027: detail only, frozen backbone. FDR028: detail+context, frozen backbone.
FDR029: detail only, trainable final backbone blocks. FDR030: detail+context,
trainable final backbone blocks. The context stream carries a label-free candidate
mask (rendered body plus16%context) for spatial pooling, so a focused neighbor is
not treated as the target. Shared resident ImageNet MobileNetV3-small;
freeze features[:9], train features[9:] only in the last two arms. Freeze all batch
normalization statistics and affine parameters in every arm. Shared weights across
streams. Head1152→64→1, second-stream columns initialized zero; disabled stream
zeroed, same seed42 and initial head/prefix/tail weights. No geometry features,
augmentation, temporal references or labels in image inputs.

Cache only frozen prefix activations for both inputs, float32 and exact ordered
membership. This is still partial-backbone training: the remaining visual blocks
receive gradients. Validate cache identity and unchanged prefix; no stale final
feature cache may substitute for the trainable blocks.

Use the existing trainer, weighted full-fit objective, AdamW and evaluation.
Accumulate exact whole-corpus weighted gradients in32-control microbatches to bound
memory; one optimizer step per complete corpus pass. Headlr.01, taillr.0001,
weightDecay.01.100updates max, evaluate every10updates plus terminal. No stop on
training-fit success. Fixed0.85 and existing checkpoint eligibility/minimum-loss
selection; strict FDR021 comparison unchanged. Compare matched update numbers if
time caps differ; insufficient optimization is an explicit limitation, not proof
an architecture fails. Never select an alternate checkpoint after seeing results.

## Budget and completion

At most four trained candidates,300seconds each,1800seconds cumulative execution,
2GiB outputs; one bounded prefix encoding pass≤300seconds, cache≤512MiB. Decode
one original frame at a time within existing pixel limits.32×256×256 per-stream
encoding/microbatch. Use project-local artifacts and resident MPS. Generated-tensor
tests precede retained execution; failed zero-update startup recovery counts toward
the same budget. No extra scientific retries. Record timings and exact metadata.

Verify actual CLI dispatch, invalid inputs/changed hashes/protected roles, input
scale/edge behavior, gradient accumulation equivalence, frozen prefix/BN versus
changed tail, deterministic sampling, cache membership and no train-fit stopping.
Run focused Python tests and offline Swift build/test. Replay all retained metrics.
Deliver one Markdown report with comparison sheets, four outcomes, limitations,
next decision and reconciled Tasks/CurrentState/ExperimentLog. TTR coordination
not applicable unless a finding changes its next action.
