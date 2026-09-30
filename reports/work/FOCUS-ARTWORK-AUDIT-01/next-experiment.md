# Proposed next experiment — one paired-loss frozen-feature head

Status: decision-ready proposal, **not implemented, launched or allocated a run ID**.
Current audit does not authorize another run. Aim: test a learning objective that
uses the same-control pairs we already have; no new annotation or TTR prerequisite.

## Fixed inputs

- Exact FDR015363training pairs/726crops,9retention pairs,453real selection crops
  and64exclusions. Preserve source-group boundaries; no evaluation-to-training moves.
- Verified FDR015 cached576dimensional ImageNet features, feature/label order,
  encoder SHA and production16%-expanded256crops. Reuse, do not infer again.
- Fresh linear head with the same seed42 initialization; no FDR015-last warm start.
  Same AdamW0.0003,30epochs,64crops per step,1800s limit and fixed0.85 threshold.
- Same25%appearance mass, balanced labels, uniform pairs within each stratum.
  Change sampling unit to32complete pairs per batch; document correlated batches
  as an accompanying change rather than claiming a perfectly isolated loss ablation.

## The one change to test

For each focused/unfocused pair with scores z+ and z−:

`loss = mean(binary_cross_entropy_with_logits(z, label)) + mean(softplus(-(z+ - z−)))`

Fixed ranking coefficient1.0, no search. BCE preserves an absolute-score anchor;
pure pairwise loss alone does not determine a usable confidence offset. The pair
term rewards the same control's focus transition instead of rewarding a static
artwork identity. It can fail, and cannot invent missing Home focus appearances.

Integrate into the existing explicit experiment adapter/trainer, not a second
trainer. Tests must cover pair completeness/identity, label order, no evaluation
sampling, finite scores, frozen features, exact loss and unchanged legacy behavior.
Freeze an approved protocol and log before execution. One attempt, no automatic
extra epochs, architecture sweep, threshold sweep or restart.

## Decision and stopping

Report initial and all30epochs using the same implementation: paired score margins,
real per-stratum recall/FP,13complete-frame ranking and strict/runtime-style outcomes,
and all18retention decisions. Keep all27incomplete/unknown frames unavailable for
unique-selection claims. Compare against FDR015 on identical cases, including its
11/13final ranking and two Home failures; do not hide FDR014's earlier11/13snapshot.

Research target, **not a qualification threshold**: fix at least one of the two
Home rankings without reducing11/13overall ranking. Report endpoint and all epochs;
this target never selects a checkpoint. Existing fixed0.85/retention/real/stratum/
complete-frame guards alone determine eligibility, then the existing minimum
balanced-real-BCE rule chooses among eligible epochs. No eligible epoch means none.
No export/promotion in this experiment, even if a development checkpoint is eligible.

## Calibration and geometry stay separate

Do not fit calibration on the reused real selection screens, nine retention pairs,
or protected challenge. There is no qualified separate calibration set in this
audit. Before a calibration experiment, form source/recipe/asset/journey-connected
groups using eligible training sources, freeze disjoint fitting/calibration/
verification roles, check support by stratum, and keep related variants together.
The five current group names do not prove that split is feasible. Insufficient
support blocks calibration, not the paired-loss experiment above.

No claimed temporal learning: these are same-control state pairs, not verified
ordered input journeys. No geometry-vector augmentation yet: native training box
areas are constant across focus states. Resolve the measurement target with TTR
and inspect already-published native12/native100 before adding that input channel.

Next approval can cover implementation, verification and this single bounded run
together. The independent existing-archive intake should be assigned explicitly;
it does not require a new device session or further human annotation.
