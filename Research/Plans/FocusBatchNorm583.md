# FOCUS583 — Restore baseline BatchNorm state

Owner: Maximum-mini-NUIAK. All model results remain provisional for Joe's review.
Standard, shipped models, operating thresholds, and the optional observer stay unchanged.

## Question and motivating evidence

Does restoring baseline BatchNorm state remove native donor retention losses while keeping its native selection?
FOCUS581 classifier and head edits keep 270 legacy crop decisions but lose the native selection.
That selection uses 1 distinct positive input across 3 related frames.
The full native donor keeps it but loses 2 legacy crop decisions.
Those comparisons change trained parameters and BatchNorm state together.

## Fixed comparison

Keep every trained parameter from the exact recovered native donor.
Restore only FDR-001 BatchNorm running means, variances, and counters.
Copy tensors exactly. Do not interpolate, train, recalibrate, tune thresholds, or export.
All 138 resident model buffers belong to BatchNorm. All 138 differ between the retained checkpoints.
Reject unsupported buffers, changed ancestry, incompatible tensors, or non-finite state.
Keep the original checkpoints immutable.

Reuse the retained FDR-001, full native donor, classifier, and head results.
Compare the new model against both FDR-001 and the full native donor on identical native inputs.
Score the complete retained suite with its existing reviewed references and ancillary sets.
SDK-observed focus labels remain separate from model predictions.

## Inputs and scope

Reuse the exact production crop path, 16% expansion, and 256 by 256 model inputs.
Use focus threshold 0.85 and ambiguity threshold 0.70 without tuning.
Preserve all pixels, bounds, labels, roles, exclusions, groups, and model input hashes.
The native set has 24 crop presentations, 11 distinct model inputs, and 3 construction groups.
It has 3 distinct positive inputs and 8 distinct negative inputs.
Native roles remain review-only. Observed profiles remain unknown. Do not admit these cases for training.
Static repeated frames do not establish movement, settling, or independent scene coverage.
Full-screen consumer behavior, independent-app accuracy, and profile qualification remain unmeasured.

## Graph and decisions

Use T94 for one producer, T95 for one retained score, and T63 for four native cohort scores.
Use T96 for a retained comparison with cached controls.
Use the existing native comparison adapter for two reports: baseline versus correction and donor versus correction.
These 9 nodes answer 1 question. They do not represent 9 independent investigations.
Each node permits 800 s and 100 MB. The graph ceiling is 7200 s and 900 MB.
Estimate useful duration from the matching completed jobs. Ceilings do not estimate duration.
No capture, training, export, or model activation occurs.

A supported mechanism preserves the donor native selection and all previous correct decisions without new wrong selections.
Require all 270 legacy crop decisions and retained correct abstentions. Report every failed existing quality gate.
If the mechanism is supported, prepare fresh profile-qualified consumer tests after Joe reviews the evidence.
If the native selection is lost, reject this correction and stop buffer-only variations without new causal evidence.
If legacy losses remain, inspect those exact inputs before another correction. Do not start a coefficient sweep.
If execution or identity checks fail, preserve the attempt and fix the exact defect through a successor.
Missing independent labels, profiles, or consumer receipts keep model qualification inconclusive.
No result authorizes a headline metric update or model promotion.

## Independent iOS work

IOS582 continues under the unchanged active source pins and fixed 30-epoch comparison.
The control fit is complete. The teacher fit runs when this tranche begins.
Its dependent scoring and retention reports are already admitted.
Review the complete pair together. Do not infer model quality from fit completion or training loss.
Do not add another unchanged preservation fit while this question remains unanswered.

Private configurations, exact manifests, test logs, and admission evidence are in reports/work/FOCUS583.
