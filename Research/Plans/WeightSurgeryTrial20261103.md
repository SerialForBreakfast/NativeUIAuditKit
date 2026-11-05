# Weight surgery trial — November 3, 2026

Owner: Maximum-mini-NUIAK. Parent: ADR-0033. Task authority: Tasks.md.
Status: planned; no jobs admitted by this document. FocusRing runs first; detector preparation proceeds independently.

## Research question and limits

Can bounded weight edits improve focus selection, or improve detector initialization, while preserving previous successes?
Separate checkpoint interpolation, taxonomy projection, and reasoning-guided surgery in reports. They are different interventions.
The cited WSP research motivates testing. It does not establish results for these architectures.
No promotion belongs to this trial. Preserve Standard, shipped artifacts, original captures, and prior evidence.

## Verified preparation findings

- FDR-003 trained from random initialization. It is not a fine-tuned descendant of FDR-001.
- FDR-006 warm-stretch records strict FDR-001 initialization. Verify checkpoint hashes and preprocessing before use.
- Existing WSP blending edits floating state entries. Explicit parameter allowlists must exclude BatchNorm statistics and other buffers.
- Existing T86 runs on numeric arrays and an isolated BatchNorm module. It does not yet load and qualify full perception models.
- Existing projection defaults include an unimplemented max_pooling name. Reject unsupported modes instead of silently summing.
- ROLES559 includes context-dependent key mappings and button-text ownership. A fixed class matrix cannot implement those rules alone.
- FOCUS556 F1/F2 reports now identify unauthorized scratch execution. Preserve those outputs as exploratory evidence, not qualified queue results.

## A. Common evidence and execution contract

1. Inspect current main, active revision, dirty work, and recent audit corrections before implementation. Preserve other workers' edits.
2. Pin source checkpoints, architecture, taxonomy, preprocessing, input groups, software revision, and thresholds.
3. Reuse existing independent-label validators and queue comparison templates. Reject predictions-as-reference-labels.
4. Preserve 21-frame focus development and 270-crop legacy sets as repeatedly inspected development/regression evidence.
5. Reserve fresh application flows for qualification. Do not train on real-app evaluation images or select edits using qualification outcomes.
6. Each candidate gets an immutable checkpoint, parent hashes, edit recipe, changed-tensor inventory, and per-case predictions.
7. The detached runner owns execution. No live adapter changes while a job uses that source.

No public model API changes. Add internal receipts for edit identity, allowed tensors, unchanged buffers, and grouped outcome counts.
Use existing template admission. Add a bounded adapter extension only where real checkpoints cannot pass existing interfaces.
Diagnostic jobs retain 800 s and 100 MB limits. Candidate checkpoint production reserves 2 GiB and requires an explicit artifact budget before admission.
Training uses fixed 30 epochs, 2 GiB per fit, and the repository's 43,200 s hung-job guard.
Record expected duration from matching previous jobs; a guard is not an estimated runtime.

## B. FocusRing comparison: compatible weight edits

Question: does editing a small output subnetwork improve focus discrimination beyond a global score shift?
Use FDR-001 as the anchor. Use FDR-006 only after its initialization and crop contract pass verification.
If ancestry or preprocessing cannot be established, block this merge branch and continue the detector track.
Do not substitute FDR-003 merely because its tensor shapes match.

Freeze these arms before scoring:

| Arm | Change |
| --- | --- |
| F0 | Unchanged FDR-001; serialize and reload once to test no-op parity |
| F1 | FDR-001 classifier bias plus 0.5; fixed calibration diagnostic |
| F2 | Baseline plus 0.5 of the FDR-006 parameter delta, classifier parameters only |
| F3 | The same coefficient, conv_head and classifier parameters only |

Use exact named parameters, not substring matching. Keep all remaining parameters and buffers byte-identical to FDR-001.
The same-initialization condition supports testing; it does not guarantee compatible intermediate representations or successful merging.
Keep inference threshold 0.85. Report F1 as an effective calibration change, not evidence of improved features.
Do not search additional coefficients after inspecting these results within this tranche.

Measure D1 focused reference boxes above threshold, D2 ambiguous frames, D3 runtime-equivalent selections, and legacy retention.
Also report negative false-high counts, per-app outcomes, and every gained or lost case.
Acceptance retains FOCUS556: D1 >=12/21, D2 <=8/21, D3 >=5/21, R1=270/270, R2>=14/16, and R3>=3/8.
A candidate must add no wrong full-screen selections relative to the matched baseline.
Supplied-box results remain separate from actual full-screen TTR execution.

Select at most one passing candidate: highest D3, then lowest false-high count, then fewest changed parameters, then arm order.
If no arm passes, reject this bounded interpolation hypothesis. Do not call preserved legacy accuracy a solved focus problem.
If an edit only matches the bias control, record calibration as the sufficient explanation.
If a candidate passes, queue Core ML parity and retained TTR replay, then fresh independent qualification.
Require identical threshold decisions per crop for backend parity; any mismatch requires diagnosis before further qualification.

## C. Detector comparison: projected head initialization

Question: does role projection improve convergence or final detection compared with a random 13-role output head?
Use the same pinned tvOS 41-class source checkpoint in both arms, rather than mixing iOS Run013 with a tvOS control.
Use the existing ROLES559 880-row membership with its exact role rules, groups, and exclusions.
Preserve the same non-output weights, regression branches, optimizer, seed 42, batch size, preprocessing, and learning rate 0.0001.
Resolve the batch size from the pinned original T89 configuration; record it before admission. Do not auto-tune it differently per arm.

| Arm | Initialization and execution |
| --- | --- |
| D0 | Original source predictions mapped to roles; retained inference control |
| D1 | Random 13-role classification output layers; 30 epochs through T89 |
| D2 | Mean projection of corresponding source classification weights and biases; identical 30 epochs through T89 |

Only D1 versus D2 tests initialization. D0 supplies context, not a matched training comparison.
Preserve detector class priors using the same initializer for D1 across both recorded seeds.
For roles without source channels, copy the matching random initialization into D2 and disclose the unsupported projection rows.
Use the full role-label converter for key identities and button-text rules. Do not claim the projection matrix performs those conversions.
Verify device, dtype, module mode, class order, and all three YOLO scales after editing.
Evaluate zero-step predictions diagnostically. They do not establish a valid class-probability merge.

Score checkpoints at epochs 5, 10, 20, and 30 using fixed development inputs. Compare fixed-last models for acceptance.
Use AP50, AP75, AP50–95, per-role precision and recall, misses, false detections, and prior successes lost.
Cross-check with official COCO scoring. The circular RC561 labels are prohibited.
Supported: final AP50 improves by >=0.01 absolute, no role loses >0.02 AP50, and no previous full-screen success is lost.
Contradicted: lost full-screen successes or any role regression exceeds the limit. Other outcomes are inconclusive.
Early-checkpoint gains with no final gain support a convergence observation only, not promotion.
If supported, repeat D1/D2 at seed 43 before qualification. Admit those two fits only after the first comparison passes.
If contradicted or inconclusive, stop this projection variant. Record the affected classes rather than expanding a sweep.

## D. Conditional reasoning-guided surgery

This is a separate follow-up, not another name for F2/F3 blending.
If focus edits fail, inspect training-only activations for a specific artwork-versus-focus confusion.
Produce a diagnosis naming the proposed tensor, expected effect, affected examples, and a falsifiable prediction.
A later bounded trial compares one proposed patch against the unchanged model and the bias control.
Freeze that patch before seeing evaluation results. Require unchanged non-target tensors and fresh qualification after development selection.
Do not claim that a texture channel is causal from large weight magnitude or correlation alone.
Do not admit an unspecified patch or automatic open-ended search from this plan.

## E. Tests and delivery

- No-op editing preserves predictions; changed tensors exactly match the allowlist.
- Missing keys, shape mismatches, nonfinite weights, incompatible ancestry, and unsupported projection modes fail clearly.
- BatchNorm buffers and counters remain unchanged for the focus arms.
- A synthetic two-class example proves that averaged logits are not max or union probabilities.
- Reference provenance tests reject circular labels; incomplete annotations do not generate complete precision claims.
- Queue integration tests cover immutable inputs, explicit failures, conditional successors, and preserved original attempts.
- Reports distinguish execution completion, development acceptance, backend parity, and independent qualification.

Deliver one comparison report per track with exact hashes, conditions, outcomes, and the next selected branch.
Independent iOS work remains available; no iOS model replacement is implied by either experiment.

Sources: [ADR-0033](../ADR-0033-Weight-Space-Programming-for-Perception-Models.md),
[FOCUS556](FocusRealApp556.md), [ROLES559](Roles559.md),
[qualification recovery](ModelQualificationRecovery20261103.md), and
[experiment ancestry](../ExperimentLog.md).

## Implementation checkpoint — November 4, 2026

The bounded edit helper and checkpoint inspection CLI are implemented in `scripts/weight_surgery.py`.
Three focused tests pass: non-target preservation, exact no-op, and invalid edit rejection.
The actual FDR-001 and FDR-006 best checkpoints pass key, shape, dtype, and finite-value checks.
The head edit changes exactly classifier.weight, classifier.bias, and conv_head.weight in memory.
Base SHA-256: `08158ebc78689f0549511b26f744f9e39e0250d56cbae311da3c83cf9c4ce1e5`.
Donor SHA-256: `00359cc9bd547f2821b244b45ce64374465f6e5a30e92070dd520af2cafb2fa3`.
Ancestry remains a separate evidence check. Tensor compatibility does not establish it.
Remaining: immutable candidate production, queue adapter integration, matched scoring, and detector initialization comparison.
No candidate is saved, admitted, scored, exported, or promoted by this inspection.

## SURGERY562 admission preparation — November 4, 2026

Ancestry verification passes against exact FDR-001 and FDR-006 hashes, retained preflight, and completion records.
This verifies the historical initialization record; it does not claim an execution attestation.
The reusable queue templates are T94 candidate creation, T95 scoring, T96 comparison, T97 crop preparation, and T98 detector initialization.
The frozen request is `reports/work/SURGERY562/batch.json`. It defines 11 jobs with no training or export.
Focus references cover 21 blinded, human-reviewed development frames from 2 applications.
Retained checks cover 270 legacy crops, 16 reserved procedural crops, and 8 poster-calibration crops.
Legacy and repeatedly inspected references are development/regression evidence, not fresh qualification.
Each job retains an 800 s guard and 100 MB output limit. Total reservation: 8,800 s and 1,100 MB.
This is a short diagnostic graph, not an overnight workload. Execution estimates remain unmeasured for this adapter.
Admission occurs in 2 cycles: 6 preparation/producer jobs, then 5 dependent score/report jobs.
The report cannot promote a model. Full-screen TTR replay and fresh qualification remain separate requirements.
The detector job creates matched random/projected 13-role initializations from the same tvOS checkpoint.
Detector fits remain pending because T89 fixes seed 371 and does not verify exact initializer preservation after trainer reconstruction.
A bounded T89 extension must expose the planned seed and verify all starting tensors before the first optimizer step.
The extension must preserve existing defaults, then qualify seed-42 random/projected fits with batch 8 and 30 fixed epochs.

Verification before admission: 9 surgery tests, 3 projection tests, 10 template tests, 9 batch tests, and 46 benchmark tests pass.
An isolated offline Swift build passes 3 model-asset tests and 7 FocusRing tests.
The no-op producer passes an actual isolated queue run with exact tensor roundtrip.
