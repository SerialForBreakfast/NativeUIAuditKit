# FOCUS341 — added boundary detail and matched content changes

> Historical research record. Results retain their stated scope and limits.
> Host names are public aliases. Local evidence and execution records remain private.
> This publication does not revalidate earlier results or approve a model.

Owner: research-host-NUIAK. Date: 2026-10-12.

## Fixed comparison

Keep FOCUS329 weights and both original crops as the control.
Add 1 image-selected boundary crop from the original-resolution image.
Start its correction at 0. Freeze the existing branches during training.
Do not average the new crop into the original crop features.

Generate content-only negatives from the admitted FOCUS326 training families.
Keep focus identity, control bodies, and effect pixels unchanged.
First try the existing artwork change. Record cases that cannot match its magnitude.
For those cases, change a background patch outside both control patches.
Match mean absolute RGB change within 10%, after integer pixel rounding.
Record the changed region and method. These remain authored training examples, not native observations.

## Execution

Run the crop audit and negative generation before training.
Reject changed originals, labels, hashes, or protected group membership.
Use the existing crop function and trainer.
Run at most 2 candidates with fixed initialization, seed 42, 30 epochs, and learning rate 0.0001.
Each candidate has a 30 min limit and a 2 GiB output limit.
Compare added detail alone with added detail plus matched negatives, if generation qualifies.
Keep the original training views and update count unchanged.
Use the fixed last checkpoint. Do not tune thresholds from evaluation results.

## Acceptance

Require exact original crop preservation and initial prediction agreement.
Report boundary coverage, extra input cost, supported matches, and unmatched cases.
Compare native, reversed, distraction, and tiny-control results against retained predictions.
Report each previous success lost. A replacement needs improvement without lost previous successes.
Keep inspected evaluation cases in their current roles. Do not call them untouched evaluation.
Missing native labels block native qualification, not authored diagnostics.

research-host-TTR supplies retained rendering and artwork where available.
Its current source has 4 fixed layouts, but no independent effect or magnitude controls.
Keep original renderer source and all previous output unchanged.
