# Measured crop errors and refinement review

Owner: Maximum-mini-NUIAK. Date: 2026-10-18.

## Current comparison

Question: do measured detector boxes improve focus selection compared with generic jitter at equal training exposure?

Use the admitted NCTRL417 mixture, initialization, row order, labels, and 30-epoch fixed-last trainer.
Keep existing jitter variants and all development rows unchanged.
Change only original-body training crops with unique detector correspondences and IoU of at least 0.5.
The earlier IoU 0.1 correspondence test was diagnostic. It does not establish suitable crop labels.

The matched arms are:

1. Retained original crops. Regenerate supported originals and require decoded-pixel parity before reusing the retained control model.
2. Generic jitter of up to 8 px per edge, using seed 371 and the existing jitter function.
3. Actual detector boxes from the same training images and controls.

These arms match row count, class exposure, initialization, and updates. They do not match perturbation magnitude.
This is a conditional comparison on supported controls. It does not solve missing proposals or establish broad generalization.
Do not invent offsets for excluded controls. Do not transfer offsets from development cases.

T91 prepares the crops with `FocusRingClassifier.makeCrop` through the existing Swift helper.
T06 trains each changed arm using the resident trainer. No STN, copula, or new backbone enters this comparison.
Use T37 for the retained native and artwork suites. Use T63 for the matched TTR consumer failure set.
Preserve the fixed threshold and report Standard and HCF separately.
Reject a replacement with any lost retained success or new wrong selection.
The completed preparation proves data integrity, not model acceptance.

The first preparation attempts fail because the original mixture already contains jittered crops.
Corrected `-r2` jobs preserve those variants instead of composing two changes. Original attempts remain immutable.

## Detector label qualification

T92 verifies source image hashes, observed focus, exported body geometry, taxonomy, group roles, and duplicate consistency.
Its scope is the Fixture's focusable controls. Scene coverage does not establish complete labels for all UI classes.
The retained admission has training and development groups, but no calibration groups.
Do not move inspected development cases into calibration or final audit.

For T89, freeze the detector target scope before setting `labelsComplete`.
A focusable-control-only detector and the general UI detector require different label claims and regression comparisons.
The current T89 contract requires separate calibration groups. It cannot consume the current membership unchanged.
Fixed-last training does not inherently require calibration-based checkpoint selection.
A future train-only qualification can disable validation or label it as training diagnostics, but it needs an explicit tested contract.
Do not create a calibration blocker merely to select a fixed last checkpoint.

## Audit of the supplied remediation plan

The plan correctly removes preset curves, label-derived feature defaults, estimated size gates, and false no-focus claims.
Adopt those requirements. Keep prototype qualification separate from scientific admission.

| Area | Recommendation |
| --- | --- |
| T78 support gates | Do not adopt 2 groups, 16 matches, 10% ambiguity, and 15% misses as established scientific limits. They lack a stated validation basis. |
| Partial correspondence | Exclude ambiguous matches individually. High ambiguity limits coverage; it does not automatically invalidate every unique match. Report the conditional scope. |
| Offset training | Start with actual source-image recrops. Warping an already resized crop can lose context and alter the signal under test. |
| Copula and STN | Defer both until the simpler measured-box comparison supports them. Adding both would combine data and architecture changes. |
| Shared crop trainer | Reuse the resident trainer and production cropper. Add bounded hooks only when required. Do not introduce a second full training loop. |
| Feature dimensions | The resident backbone uses `conv_head`, `norm_head`, and 1280 head channels. The proposed `head_conv` and fixed 960-dimensional path are incorrect. Inspect actual tensors. |
| T67 loss injection | Verify criterion creation, coordinate units, normalization, and loss weighting against the installed trainer. A proposed callback is not verified integration. |
| T81 pooling hooks | Registered modules must enter the optimizer and checkpoint before training. Python hooks alone do not establish saved or exportable architecture. |
| Unchanged controls | Test disabled extensions against the actual resident outputs and gradients. Matching a final metric alone is insufficient. |
| T73 sliced inference | Useful next. Pin tile geometry and recover coordinates. Measure proposal recall, full-path selection, false positives, and latency. |
| T85 containment rule | Useful bounded rule comparison. Inspect the actual retained schema instead of assuming every report contains boxes and scores. Report every lost success. |
| T72 recipes | Use actual TTR and T46 schemas. The supplied iOS recipe version does not match the resident `t46-recipe-v2` contract. No capture authority follows from recipe generation. |
| T74 compression | Use the qualified exporter environment and real package size. Keep export parity separate from measured Apple runtime parity. |
| T75 motion | Connect frame pixels to measured motion. Keep supplied motion as an explicit control. Reject weak or ambiguous correlation estimates. |
| T76 consensus | Different checkpoint hashes do not establish independent errors or out-of-fold evidence. Require training-group provenance before making those claims. |
| T79 checkpoint selection | Use calibration or explicitly designated development selection groups. Never select against the final audit or conceal repeated selection against retained tests. |
| T80 conformal output | Empty proposals mean unknown or abstained. Use identical calibration and evaluation transformations. Do not claim risk control without its sampling assumptions. |
| T84 subset selection | Preserve whole groups and explicit family support. Reject fabricated feature defaults. Define the response when the budget cannot cover every family. |
| T86 model merging | Verify compatible architectures and initialization. Measure full-checkpoint reload and actual BatchNorm recalibration. Do not infer improvement from vector arithmetic. |

The supplied plan is a proposed design, not evidence that these implementations now exist.
Do not approve all 20 templates together. Qualify each bounded integration on real inputs and explicit failures.

## Next decisions

- If measured boxes improve deployment selection without losses, repeat on new native groups before considering a more complex sampler.
- If known-box success improves but deployment does not, prioritize proposal coverage and localization.
- If either arm loses Standard or retained artwork successes, reject that replacement and record the failing cases.
- If detector label scope remains unresolved, keep its training blocked while crop comparisons run independently.

## DETECTOR422 — annotation scope and independent next comparison

The requested review occurs while OFFSET421 training still runs. No completed matched result supports another crop correction yet.
Do not infer gains from training loss. Leave the approved crop comparisons running.

The retained Fixture recipes enumerate every button, row, and tab body in these scenes.
The new preparation checks recipe items against observed elements, planned focus IDs, taxonomy, and measured presentation-layer bodies.
Unknown component kinds, missing elements, hidden controls, changed geometry, and unverified focus fail qualification.
Reuse the verified T87 image links. Do not duplicate the bulk image payloads.

This qualifies a separate 3-class proposal detector, not exhaustive annotations for the general UI detector.
Its target classes are primaryButton, listRow, and menuButton. Text inside those controls and containers are not separate targets.
Keep the shipped general detector and Standard behavior unchanged.

The first proposed split reserves b405-027-tab-group-2 for calibration. A further ancestry check finds shared layouts across all 3 tab groups.
Revoke the unstarted fit and its dependent branches. Preserve their specifications. Reuse the 16 independent baseline jobs.
The v2 successor keeps all 21 unique training images across 5 source groups and 3 layouts together.
All 6 development groups remain excluded from training. No calibration partition exists.
Use the fixed last checkpoint with patience 0. Resident validation runs on training images and reports training diagnostics only.
Do not call these metrics held-out accuracy. Separate development jobs decide whether the candidate helps.
These data support a feasibility test. They do not establish broad deployment coverage.

Use T89 with retained tvOS weights, seed 371, 30 epochs, batch 8, AdamW, and 640 px images.
The queue permits 1800 s and 2 GiB. Preserve a timeout as failure; do not reinterpret it as completed training.
The output head changes to 3 classes. This comparison does not isolate architecture from training data.

The batch contains 1 training job and 40 diagnostic jobs across 8 conditions.
Conditions cover buttons, rows, tabs, diamond decoration, edge clearance, small decoration, tall controls, and no-focus scenes.
For each condition, compare both detectors through PyTorch at confidence 0.5, image size 640, and NMS IoU 0.45.
T56 reports class-aware gains and losses. T42 separates localization from class errors.
T57 checks complete focus selection with both fixed crop models and retained HCF ring support.
Do not compare PyTorch results directly against production Core ML results as a training-effect measurement.

If proposals improve without lost selections or new wrong selections, test supplemental proposal use before considering any detector replacement.
If native gains lose artwork or no-focus behavior, reject global replacement and retain case-linked failures.
If the small dataset fails, inspect proposal coverage and group support before increasing training volume.
No model promotion follows from completed jobs.
