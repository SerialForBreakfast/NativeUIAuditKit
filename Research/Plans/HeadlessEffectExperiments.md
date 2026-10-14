# Headless focus effects: controlled training tests

Owner: Maximum-mini-NUIAK. Producer request: Sillycon-TTR. The plan includes configurable effects and bounded tests with existing controls.
FOCUS319 has [measured results](../Focus319Results.md). FOCUS320 tests the resulting training conflict.

Request `nuiak-focus314-authored-effects-01` is stored at coordinator cursor 144.
SMB fallback: `nuiak/requests/nuiak-focus314-authored-effects-01.json`, 2,407 bytes.
SHA-256: `444b02041a501d18bb6fd4579c110b011394f81cfcd857542890ae6c94d54c02`.
Exact readback passes. Forwarding, peer acknowledgment, and producer acceptance remain unconfirmed.

## Decision and evidence

### FOCUS325 — small controls and pooled detail

Owner: Maximum-mini-NUIAK. The user approves the corpus review and 2 matched experiments.
Use existing reviewed FOCUS319 shelf renders. No producer service or new capture is needed.
Make 432 authored pairs from 3 approved artwork families, 3 control sizes, 2 separations, and 4 corner regions.
Use movement, fixed-focus artwork changes, identical pairs, and both frame orders.
Keep patch limits explicit. Transformed patches are not exact native effects or independently observed focus.
Verify source hashes, transformed geometry, changes inside permitted patches, and ancestry exclusions.
Review representative images before training. Preserve all original source images and all evaluation roles.

Both candidates start from FOCUS319. They keep all 1,820 original training views and the 240 prior authored pairs.
Add the new corpus to the auxiliary pool. Cycle within each label and require exposure of every auxiliary row.
Keep original row weights and auxiliary coefficient 0.25. Match exact exposure between candidates.
Freeze convolution filters, whole-frame weights, and geometry. Train the detail dense layer and correction layer only.
The first candidate keeps adaptive average pooling on a 4 × 6 grid.
The second uses a fixed 50/50 average/max blend on the same grid. No threshold search occurs.
Cache both pooled representations from the same convolution pass. Do not cache labels as model inputs.
Verify cache/image parity, checkpoint reload, and unchanged frozen weights.
Use the existing trainer for 30 epochs, batch 16, learning rate 0.0001, and seed 42.
Select the final checkpoint in both runs. Keep thresholds at 0.15 and 0.85.
The matched comparison isolates pooling under this training scope. Comparison with FOCUS319 also includes further training and changed auxiliary exposure.

Use the existing evaluation tools for native, reversed, replay, nuisance, placeholder, and tiny-change cases.
Report development and previously inspected reserved groups separately. Do not call either a new final audit.
Acceptance requires useful native gains without losing previous successes or increasing false changes.
If either candidate fails, preserve its evidence and stop that experiment. Do not tune on the resulting failures.
Use 2 CPU threads, 8 GiB memory, and at most 2 GiB new output. The standing time override applies.
Finish focused tests, the offline Swift build/tests, results, and a verified update for Sillycon-TTR.

### FOCUS324 — detail features before scalar compression

Complete. Native gains do not offset the distraction regression. Reject the candidate. [Results](../Focus324Results.md).

Owner: Maximum-mini-NUIAK. The user approves the feature audit and 1 justified correction.
Use the frozen FOCUS319 branches, FOCUS321 membership, and original-resolution views from FOCUS313.
Extract the 32 context features and 32 mean-pooled detail features before scalar compression.
Keep both selected windows and their shared before/after coordinates unchanged.
Use the original 1,820 training views and 240 approved authored pairs. Preserve every role and input hash.
Compute normalization from those training features only. Use a minimum standard deviation of 0.001.
Compare constrained separation using detail alone and context plus detail. These are training diagnostics, not an evaluation leaderboard.
If combined features lower weighted margin shortfall by more than 0.0001, use that solution for 1 candidate.
Fit 65 residual coefficients with the existing solver and coefficient bounds [-1, 1].
Keep the original logits as the starting score. Protect correct training decisions with the FOCUS323 margin rule.
Keep original row weights and authored exposure with coefficient 0.25. Thresholds remain 0.15 and 0.85.
Report support by training group, measured body size, authored layout, and condition. Do not infer unavailable native effect strengths.
Check float32 constraints, cached/image parity, restored weights, and unchanged feature branches.
Use the existing evaluator for every native, reversed, replay, nuisance, placeholder, and tiny-change check.
Compare previous models on identical membership. Previously inspected groups remain development evidence.
Acceptance requires a useful gain without failing previous-success requirements. Otherwise, reject the candidate and explain the failure.
Run focused tests and 1 offline Swift build/test pass. Send the measured result to Sillycon-TTR.
Use 2 CPU threads, an 8 GiB memory budget, and a 256 MiB output cap.
No new capture, dependencies, data roles, exports, promotion, or peer assignment occurs.

### FOCUS323 — direct constrained output fit

Complete. The candidate adds no correct native focus changes. [Results](../Focus323Results.md).

Owner: Maximum-mini-NUIAK. The user approves 1 direct output fit and the complete comparison.
Use the FOCUS321 score cache and the initial FOCUS322 hidden features, normalization, and seed.
Reproduce the pinned feature hash before fitting. Keep all input roles unchanged.
Use the existing constrained feature routine with the resident HiGHS solver and 2 threads.
Fit 9 coefficients within [-1, 1] to minimize weighted linear margin shortfall.
Keep training-success constraints, target margin, original weights, and authored coefficient 0.25 unchanged.
This is a direct solve, not a second 30-epoch run. Its loss differs from FOCUS322's squared loss.
Do not claim that this comparison isolates the solver from the loss.
Check double-precision constraints and float32 constraints before image evaluation.
Allow at most 0.00002 numerical logit error, but permit no lost protected training decision.
Stop if the solver, input hashes, frozen tensors, or parity checks fail. Preserve failed evidence.
Use the existing image evaluator for native, reversed, replay, nuisance, authored, and tiny-change sets.
Compare FOCUS319, FOCUS322, FOCUS313, FOCUS321, and DTM085 without evaluation-based selection.
Acceptance requires a useful improvement without failing existing model requirements. Otherwise, reject the candidate.
Keep outputs below 256 MiB and working memory below 8 GiB. No wall-time limit applies.
No new capture, dependencies, export, promotion, or worker assignment occurs.
Finish focused tests, one offline Swift build/test pass, case-linked results, and the TTR update.

### FOCUS322 — score separation and margin guard

Complete. The candidate preserves FOCUS319 but adds no correct decisions. [Results](../Focus322Results.md).

Owner: Maximum-mini-NUIAK. The user approves the audit and 1 justified correction.
Use the pinned FOCUS321 scores, FOCUS319 image branches, and unchanged original and authored training roles.
First, test positive and unrestricted linear separation with the resident SciPy solver.
Then minimize weighted margin shortfall while protecting existing training successes.
The audit reports infeasibility and no available linear improvement under those constraints.
This result justifies 1 nonlinear correction instead of another scalar fit.

Add a residual network with 2 inputs, 8 tanh units, and 1 output. It has 33 parameters.
Set its output weights to zero at initialization. Preserve the whole-frame and detail branches.
Use training-only means and scales. No evaluation labels or scores enter fitting or normalization.
Use the existing trainer with squared margin loss, original row weights, and auxiliary coefficient 0.25.
Keep 30 epochs, seed 42, batch 16, and fixed last-checkpoint selection. Set learning rate 0.001.
The target logit margin is `log(0.85/0.15) + 0.25`. Deployment thresholds remain unchanged.
Protect each existing training success at its original margin, capped at that target.
After each update, test all protected training scores.
If an update violates a constraint, halve it at most 12 times. If it still fails, restore the previous parameters.
This training guard does not promise success on unseen images.

Use 2 CPU threads, less than 8 GiB memory, and less than 256 MiB new output.
The standing time override applies. No downloads, capture, export, or production change occurs.
Verify input hashes, unchanged tensors, cache/image parity, and restored checkpoint scores.
Test native, reversed, replay, nuisance, tiny-change, and authored examples with the existing evaluation tools.
Keep FOCUS313, FOCUS319, FOCUS320, FOCUS321, and DTM085 comparisons separate.
Reject any candidate that fails existing model requirements. Do not tune it against the resulting evaluation report.
Acceptance includes the separation result, fixed candidate comparison, focused tests, offline Swift tests, and the TTR update.

Use authored effects to teach visual changes across controlled scenes. Do not require an exact Apple shader before testing this hypothesis.
Keep authored effects separate from observed native focus. Strong synthetic scores do not establish native accuracy.
More examples can increase the same bias. Measure useful variation and native transfer before increasing volume.

Maximum-mini-TTR source `538a1119a9edbf25651e768bf5a2a61ec137bc10` provides a standalone AppKit renderer.
`Scripts/render-headless-screen.swift` supports shelf, grid, hero detail, and navigation layouts at 1080p or 4K.
Its command interface selects layout, assets, output, resolution, and focused item.
Its fixed scales range from 1.08 to 1.15. Its shadow uses opacity 0.75, blur 28, and vertical offset -18.
Shadow distances scale with output resolution. These values describe this renderer, not verified Apple constants.
The interface does not expose effect strength, arbitrary positions, or independent before/after focus identities.
FOCUS313 verifies a useful workaround: render 2 focus IDs separately, then pair their focused images.
Matching unfocused-image hashes verify unchanged base pixels across those renders. This supports authored A-to-B diagnostics now.
An explicit pair command is a convenience, not a prerequisite for those bounded tests.
The renderer uses AppKit. BigDog-NUIAK can score its output but cannot run this Swift script directly on Linux.

[FOCUS312](../Focus312Results.md) supplies the immediate reason for this work.
One detail window contains about 50% of the tiny native difference, versus at least 90.8% of the smallest training derivatives.
Shrinking whole scenes changes control size and separation together. The next renderer tests vary them independently.
Preserving original training views alone does not preserve previous correct decisions.

## Ranked tests

### FOCUS321 — decision margins and score combination

See the next [FOCUS322 contract](#focus322--score-separation-and-margin-guard).

Complete. The candidate fails previous-success checks. [Measured results](../Focus321Results.md) record rejection and the next proposed test.

The user approves margin measurement and 1 score-combination experiment. Maximum-mini-NUIAK owns this work.
Use FOCUS319's retained image branches because they already learn authored effects. Preserve its failed status as the unchanged control.
Measure whole-frame logits, added detail logits, and distance from the fixed decision threshold on training data only.
Use all 1,820 original views and 240 reviewed authored pairs. Preserve original hashes and exact auxiliary exposure.
Cache the 2 branch scores once. Bind them to source, model, preprocessing, membership, and input hashes.
If useful detail scores oppose excessive context scores, fit a positive weighted sum plus bias.
Train only these 3 parameters. Freeze both image branches and geometry. Start with weights 1/1 and bias 0.
This preserves the initial decisions. It does not preserve them after training; the regression checks decide acceptance.
Use the existing trainer with explicit cached-score inputs. Do not create another training loop.
Use 30 epochs, seed 42, batch 16, learning rate 0.01, and 2 CPU threads.
The larger learning rate applies only to 3 scalar parameters. Keep auxiliary coefficient 0.25 and all original sample weights.
Use 3,420 updates and the fixed last checkpoint. Keep thresholds 0.15/0.85.
This adapts a retained checkpoint. It is not an equal-compute comparison with the earlier full CNN runs.
Require cached-score versus image-path parity before evaluation. Reject stale caches and invalid score shapes.
Compare FOCUS313, FOCUS319, FOCUS320, and DTM085 using existing evaluation tools.
Acceptance needs useful gains without lost previous successes or increased false changes. Otherwise preserve failure evidence and stop this fit sequence.
Keep outputs below 256 MiB and memory below 8 GiB. No wall-time limit applies.
No capture, download, export, data-role change, or production change occurs. Keep inspected reserved data outside training.
Run focused tests and integrated offline Swift checks. Send TTR a measured result without requesting new worker execution.

### FOCUS320 — conflicting training signals

The user approves this follow-up after FOCUS319. Maximum-mini-NUIAK owns the complete experiment.
Use the retained 1,820 original views and 240 reviewed authored pairs. Do not generate more images.
Measure weighted gradients by training group and label. Measure authored movement, artwork-only, and identical conditions separately.
Check fresh initialization, the original-only control, and the rejected authored candidate. Do not use evaluation labels for gradient selection.
Report gradient direction, norm, and opposing components. These are local measurements, not proof of the full training history.
If opposing gradients occur, test one-sided projection of the authored gradient against the original gradient.
Keep the original gradient unchanged. Remove only its opposing component from the authored gradient.
The audit also finds excessive authored magnitude. Cap its remaining norm at the original norm before applying coefficient 0.25.
This is 1 combined correction, not an isolated estimate of either component's benefit.
This controls raw gradients, not Adam's complete update. It does not guarantee preserved decisions.
Select and record the correction from the diagnostic before fitting. Stop if the diagnostic does not justify this correction.
Use the existing trainer, fresh DTM085 initialization, 30 epochs, batch 16, seed 42, and learning rate 0.0001.
Keep 2 CPU threads, 3,420 updates, auxiliary coefficient 0.25, and fixed thresholds 0.15/0.85.
Keep the model structure and original-resolution detail unchanged. Preserve original input, label, weight, and detail hashes.
Use the fixed last checkpoint. Keep outputs below 2 GiB and memory below 8 GiB. No wall-time limit applies.
Reuse completed FOCUS313 and FOCUS319 controls. Compare native cases, reversals, replay, distractions, tiny changes, and authored conditions.
Acceptance needs a meaningful gain without lost previous successes or increased false changes. Otherwise, reject with measured causes.
Report inspected reserved cases as inspected evidence, not an untouched final audit. No export or production change occurs.
Run focused tests and one integrated offline Swift pass. Send TTR the measured result under the existing renderer request.

### Approved supported-subset test: FOCUS319

The maintainer approves this test on October 10. It uses existing controls while effect configuration remains unavailable.
Use 10 reviewed training assets from ARTWORK204 families r1-s0 through r1-s4. Preserve all reserved artwork roles.
Render 4 layouts, 2 artwork assignments, and 2 focus states per family: 80 renders and 240 ordered pairs.
Pair types are 80 focus movements, 80 artwork changes with fixed focus, and 80 identical pairs.
Check every PNG, sidecar, base-image match, and decoded pair for conflicting labels. Inspect representative images before training.
These labels describe authored focus states. They do not describe observed native callbacks.

Keep the FOCUS313 architecture and original 1,820 views, labels, weights, and update count unchanged.
Add a label-matched auxiliary loss with weight 0.25. Cycle through authored pairs deterministically and report their actual exposure.
Use 30 epochs, seed 42, batch 16, 2 CPU threads, and the fixed final checkpoint.
Keep the whole-frame branch frozen. Reuse the completed original-only control and measure the added computation.
Limit new output to 2 GiB. Use the existing 8 GiB memory target and no-wall-time-limit training approval.
Check native cases, reversals, nuisance conditions, tiny controls, and previous successes with fixed thresholds 0.15 and 0.85.
Do not claim independent layout generalization from the previously inspected placeholder cases.
Accept only target gains without lost previous successes or more false changes. Preserve a failed result without another automatic fit.
This subset does not complete FOCUS314–316's configurable-effect requirements.

| Priority | Test | Controlled comparison | Required evidence |
| --- | --- | --- | --- |
| P0 | FOCUS314: qualify authored pairs | Known transforms, missing assets, interrupted batches, and invalid geometry | Correct pixels, annotations, failures, and reproducible output |
| P1 | FOCUS315: isolate visible effects | Growth only, shadow only, tint/ring only, and combined effects | Error by effect, strength, position, and source domain |
| P1 | FOCUS316: test transfer | Native-only control versus mixed synthetic training versus strong-to-weak training | Native gains, previous successes, false changes, abstentions, and cost |
| P2 | FOCUS317: test variety and volume | Independent artwork/layout variation, then a bounded volume comparison | Benefit from diversity versus benefit from repeated examples |

### FOCUS314: smallest useful producer contract

Inputs: pinned renderer source, licensed artwork manifest, fixed recipe list, and existing admission checks.
Ask Sillycon-TTR to extend the existing headless308 repair request. Do not create a second renderer or native calibration requirement.
Maximum-mini-NUIAK checks the returned source and runs generation locally after software qualification.

Require these controls:

- Select before and after focus IDs independently, including unchanged focus and no focus.
- Set control size and distance between controls independently of canvas size.
- Set growth scale, anchor, shadow opacity/blur/offset, and ring/tint strength independently.
- Set explicit positions, clipping, and draw order. Support edges and corners without silent relocation.
- Record resolved parameters, random seed algorithm, source revision, asset hashes, dimensions, and PNG hashes.
- Record per-frame body bounds and visible bounds. Record authored focus IDs separately from effect geometry.
- Return an error for missing required artwork, invalid IDs, invalid geometry, output collisions, and incomplete batches.
- Preserve partial output. Publish completion only after every planned pair passes checks.

Optional masks show body coverage and effect coverage separately. Define an opacity cutoff for shadow coverage.
Keep masks out of model inputs unless an experiment explicitly tests predicted masks.
Do not create synthetic native callbacks or claim that authored geometry proves native parity.

Acceptance: replay identical recipes with identical decoded pixels on the pinned runtime.
Check expected transforms against pixels and annotations. Include an interrupted batch and a failed asset read.
Record unavailable controls explicitly. A supported subset can start a narrower test without waiting for every optional feature.
Next action: freeze FOCUS315 membership from the supported subset.

### FOCUS315: effect visibility and shortcut tests

Start with 216 matched comparisons: 9 screen regions × 3 effect strengths × 4 effect families × 2 semantic conditions.
Use the same base scene for each matched positive and negative comparison.
The positive changes focus between 2 controls. The negative retains focus while a different control changes appearance.
Include unchanged pairs separately. Keep all derivatives from each base scene in one data role.
Use growth-only, shadow-only, tint/ring-only, and combined families. No family represents every native control.
Set strengths from measured native ranges where available, then add clearly marked stronger settings.
Do not infer strength from parameter values alone. Measure visible contrast, changed area, and effect footprint after preprocessing.
Use bounded fractional coverage when effects reach a screen edge. Do not move clipped items into the center.

Score existing models first through existing entrypoints. Preserve original-resolution images and aligned before/after views.
Report misses, false changes, abstentions, and regional coverage. Separate localization from change classification.
An authored no-op with a zoom provides a hard negative only when other visible context distinguishes it.
If identical visible evidence receives conflicting semantic labels, mark the case ambiguous. Do not force a learnable distinction.
Zero-strength invisible focus changes belong in ambiguity tests, not ordinary visually labeled positives.

Acceptance: complete counts and case-linked failures across all supported cells, with no hidden missing cells.
This diagnostic selects a training hypothesis. It does not select a production threshold or create untouched final evaluation.
Next action: freeze a separate training catalog and native regression protocol for FOCUS316.

### FOCUS316: matched training comparison

Prerequisites: FOCUS314 checks pass; FOCUS315 identifies relevant effects; eligible training and evaluation groups remain separate.
Use the architecture selected from FOCUS313. Do not mix an architecture change into the synthetic-data comparison.
Use 3 fresh runs from identical initialization:

1. Use original training inputs only.
2. Use original inputs plus a fixed mixture of measured and exaggerated effects.
3. Use the same synthetic examples, ordered from stronger to weaker effects.

Keep optimizer updates, original-input exposure, synthetic loss budget, and condition weights matched between runs 2 and 3.
Record the extra compute relative to run 1. Do not describe added forward passes as free training.
Start with at most 1,024 unique synthetic training pairs. Freeze exact hashes and ancestry before execution.
Use the existing 30-epoch baseline, seed 42, fixed final checkpoint, and existing thresholds.
Set 2 CPU threads, an 8 GiB memory limit, and a 2 GiB output limit for local execution.
The standing no-wall-time-limit override applies. Register the exact batch configuration before launch.
BigDog-NUIAK may run an equivalent finite assignment after receiving named portable inputs and environment requirements.

Use all previous native successes, tiny development cases, reversals, and nuisance tests without changing their roles.
Report training, development, and previously inspected reserved groups separately. None becomes a new untouched audit.
Acceptance requires more correct target cases without losing previous successes or increasing false changes at fixed thresholds.
If the synthetic test improves but native decisions do not, reject the transfer claim.
Do not respond with an automatic larger run. Diagnose effects, proposals, and context separately.
Next action: choose FOCUS317 only if a candidate passes these development requirements.

### FOCUS317: diversity before volume

Cross artwork and background choices with labels. Do not let a filename, texture, or placeholder predict focus.
Add dense scenes, overlapping cards, varied aspect ratios, mixed control types, and shadows already present in artwork.
Keep focus movement distance independent from control size. Include fixed-box focus changes and scrolling with unchanged focus.
Reserve separate layout and artwork families before generation. Group related assets, derivatives, and recipe variants together.
Compare 1,024 versus 4,096 pairs with equal optimizer updates and recorded exposure differences.
Do not claim an independent sample for each effect strength from the same scene.
Report accepted pairs per minute, rejection causes, rendering time, scoring time, training time, and storage.
Acceptance requires native gains and no regression under the unchanged FOCUS316 protocol.
Next action: request a separate deployment-domain audit before promotion.

## Useful producer additions, in order

First, expose existing effect constants and explicit pair states through a versioned recipe.
Second, add independent size, separation, clipping, and seeded placement controls.
Third, add reusable artwork pools, dense layouts, and independent nuisance changes.
Later, add explicit animation timestamps and causal sequences for settling tests.
Static generated pairs cannot establish temporal settling or real native parallax behavior.

## Ownership and verification

Sillycon-TTR owns producer changes and confirms its accepted scope. Maximum-mini-NUIAK owns admission, experiment design, and native evaluation.
BigDog-NUIAK receives immutable portable inputs for scoring or training. Do not require Apple runtime access.
Reuse existing trainers, evaluators, crop routines, transfer receipts, and cached predictions.
Run focused tests for changed code and one integrated offline Swift build/test pass.
For this planning update, check links and the diff only. No code, generation, or model execution changes.
Report software checks, data eligibility, native integration, and model outcomes separately.
## FOCUS325 outcome

The matched comparison and effect audit complete. See [results](../Focus325Results.md).
Both candidates fail previous-success requirements. Preserve their evidence, but do not promote their weights.
FOCUS326 proposes independent control-size, effect-width, and contrast coverage before another encoder change.

