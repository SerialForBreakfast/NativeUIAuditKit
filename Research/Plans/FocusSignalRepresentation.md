# Focus signal: distinguish lost detail from distracting content

Owner: Maximum-mini-NUIAK.

## Scope

Measure the active native pairs. Run 1 justified representation comparison. Review independent evaluation support and complete relevant peer receipts.
Do not repeat capture, train extra candidates, change data roles, or promote a model.

## Diagnostic

Use the existing encoder at 192 × 128. Require exact equality with each saved input.
Verify image and metadata hashes. Use observed focus identity and visible body bounds.
Expand diagnostic regions by 20% around the body center. These regions never enter prediction.
Compare absolute differences before resizing with absolute differences after resizing.
Report differences inside and outside observed focus regions. Keep uncertain decisions separate from wrong decisions.
These measurements describe image changes. They do not identify which changes cause focus.
Use cached DTM078 and DTM079 predictions. Do not repeat inference for this audit.

## Fixed candidate

DTM080 replaces absolute image differences with local residual differences.
Subtract a reflected 9 × 9 mean from the signed RGB difference.
Take the absolute value and clip it to the existing 0–1 range.
Keep the 6 original RGB channels. Keep the existing 9-channel network and its parameters.
Use the existing trainer, DTM067 initialization, and exactly matched DTM078 membership and weights.
Train for 120 epochs with seed 42, batch 16, and Adam at 0.0001.
Use 2 CPU threads and a 64 MiB output limit. Apply the standing no-wall-time-limit approval.
Pin hashes before execution. Preserve failed output and the shipped model.

## Acceptance

Verify restored-checkpoint scores. Evaluate every previous condition, both frame orders, and all disturbance strengths.
Compare individual decisions against DTM078 and DTM067. Reject replacement if previous correct decisions regress.
Do not select thresholds or epochs from reserved examples. All inspected checks remain development evidence.
Record the representation with the weights. The ordinary model loader alone does not recreate this candidate's preprocessing.
No Core ML export or navigation authority follows from this experiment.

## Next comparison: TRANSITION287

DTM080 reduces several disturbance errors but loses artwork and replay decisions.
Test an added local-residual input instead of replacing the original difference input.
Keep the original 9 channels in their original order. Append 3 residual channels.
Copy the original first-layer weights. Set the 3 new channel weights to zero.
Require initial score agreement within 0.000001 and identical decisions on the pinned sanity set.
Stop before training if this check fails.
Reuse DTM067, the exact 1,660 rows, existing weights, and DTM078's fixed configuration.
Run 1 candidate for 120 epochs. Keep the 64 MiB output limit and 2 CPU threads.
Reuse DTM078 control results. Do not start a parameter sweep.
Use the same full evaluation and individual regression rules as DTM080.
Preserve the representation identifier with the weights. Test restored-checkpoint parity.
An improved aggregate score cannot override newly wrong or uncertain cases without an explicit separate decision.
Maximum-mini-NUIAK owns admission and acceptance. BigDog-NUIAK receives only exact, ready inputs if it owns execution.
Do not dispatch a fit while another worker owns it.

## TRANSITION287 result and next diagnostic

DTM081 completes. The added inputs preserve forward replay but leave center distractions almost unchanged.
The candidate fails individual regression checks. Keep existing models.
Use saved DTM078, DTM080, and DTM081 results to select exact failed cases.
Suppress only the residual channels during DTM081 inference to measure their effect.
Compare matched scores, uncertainty, reverse order, and existing observed focus regions.
This intervention tests input use, not generalization. Do not replace ordinary evaluation with intervention scores.
Pin selected membership and model hashes. Use resident inputs, 2 CPU threads, and at most 64 MiB of reports.
Do not train during this diagnostic. Stop on missing model identity or incompatible preprocessing.
Acceptance requires case-linked results and 1 justified next experiment, or an explicit decision against another fit.
Keep independent real-app evaluation separate from these repeatedly inspected Fixture checks.

### Bounded route check after residual suppression

Residual suppression changes 100 native decisions but only 3 center-disturbance decisions.
Use 2 further inference conditions: suppress the original absolute difference, then suppress both difference inputs.
Preserve RGB frames, model weights, labels, and thresholds. Reuse cached ordinary scores after verified parity.
Run each condition once on the same 7 input sets. Do not fit weights or select a new threshold.
These interventions can create unfamiliar inputs. Use them to choose a hypothesis, not to qualify a replacement model.

## Next experiment: matched focus and content across positions

Do not add another input channel or change thresholds from these results.
DTM081 uses residual inputs on native content groups but keeps almost the same center-disturbance failures.
Suppressing absolute differences removes every positive prediction. This is not a usable correction.
The earlier position audit excludes TRANSITION265 replacements. Its missing-position claim does not describe current training.
The current audit finds content comparisons in 8 cells. Focus-only changes occupy 4 cells and remain mostly left-sided.
Balance positions within each condition before claiming balanced coverage. Count unique frames and related groups separately from repeated endpoints.

Use Maximum-mini-TTR first. Check its actual recipe controls before freezing a campaign.
Select 2 training-only recipe families and 3 supported position bands, including missing top regions where available.
Use 2 approved artwork treatments per combination. Preserve all calibration and final exclusions.
For each combination, capture 4 observed states: focus A/content A, focus B/content A, focus A/content B, focus B/content B.
This bounds the proposal at 12 recipe combinations and 48 frames before rejected captures.
Derive comparisons for focus-only changes, content-only changes, both changes, and neither change.
Keep related frames and reverse comparisons in the same group. Do not count them as independent trials.
Record unsupported positions as gaps. Do not substitute different seeds for actual position changes.
Reuse available qualified states before capture. Confirm endpoint labels and geometry after each native batch.

After admission, register 1 matched control/candidate comparison with exact membership, weights, hashes, and source versions.
Keep DTM081's representation and DTM067 initialization fixed. Use 120 epochs, seed 42, batch 16, and Adam at 0.0001.
Match total updates and group influence. Replay old examples in the control where the candidate uses new examples.
This avoids attributing extra optimization steps to better data. Record the resulting complete schedule before launch.
Use 2 CPU threads and at most 256 MiB of new model outputs. Keep raw captures under the verified storage policy.
No training starts until the matched schedule and data admission pass.
Report all prior native, replay, reverse, and disturbance checks. Do not select checkpoints from reserved results.
Accept improvement only under the existing individual regression rules. A failed candidate remains evidence, not a replacement.
The separate EVAL90 contract supplies real-app evaluation; these Fixture results cannot replace it.

### TRANSITION290 execution: reuse approved layouts first

Fresh Maximum-mini-TTR checks pass for the exact simulator and Fixture endpoint.
Do not repeat its retained captures merely to fill an outdated coverage report.
Use `coverage290.py` to verify actual frame hashes, focus observations, dimensions, and visible body centers.
Report original and replacement positions by condition, unique frames, related groups, and existing training weights.

DTM082 tests alternating approved original and shifted layouts across epochs.
Odd epochs use DTM081's replacement corpus. Even epochs use the original approved corpus.
Only 276 rows change between these corpora. All 1,660 labels and weights stay fixed.
This changes layout exposure, not the number of updates. It does not make the corpus position-balanced.
Use DTM067 initialization, DTM081 preprocessing, seed 42, batch 16, Adam 0.0001, and 120 epochs.
Keep 12,480 updates, 2 CPU threads, fixed-last selection, and the 256 MiB output cap.
Reuse the verified DTM081 control. Test unchanged trainer behavior when alternate inputs equal ordinary inputs.
Compare every existing condition, frame order, and strength against DTM067, DTM078, and DTM081.
Do not promote if required previous successes regress.

The independent companion scores 24 retained native table cases with DTM078, DTM081, and DTM082.
Verify all inventory files and run the existing consumer checks first.
Keep these cases calibration-inspection-only. Report agreement with producer observations, not verified accuracy.
The capture-version evidence remains unresolved. Parser success does not resolve that evidence.
Cache exact model, preprocessing, image, and tensor hashes for later reuse.
No new capture, label role, threshold, export, or deployment authority follows from this comparison.

### TRANSITION291: fill the measured condition gap

Owner: Maximum-mini-NUIAK. This is the next bounded model comparison, not an automatic retry of DTM082.
DTM082 fails broader regression checks. Do not use its weights as the new initializer.

Use TRANSITION290's 48 focus-only state comparisons and 32 identity controls.
Verify their image hashes, observed identities, recipe equality, parent admission, and exact training groups.
Keep their existing exclusions. Do not add the unresolved native table cases.
These state comparisons do not supply action labels or temporal-settling labels.

Create 2 registered schedules before training:

- Control: the existing 1,660-row corpus plus 80 matched old training rows and their reverses.
- Candidate: the same corpus plus the 80 prepared comparisons and their reverses.
- Match each added control row by training group and binary label.
- Select control rows by sorted source ID. Stop if the named group lacks the required support.
- Preserve each original group/label total weight after adding rows.
- Require identical label and weight vectors across the 2 schedules.
- Keep all unrelated replay rows and weights unchanged.

Both schedules contain 1,820 rows and 13,680 updates at batch 16 over 120 epochs.
Use DTM067 initialization, DTM081 preprocessing, seed 42, Adam 0.0001, and 2 CPU threads.
Select the last epoch. Keep thresholds 0.15 and 0.85.
Allow at most 256 MiB of model outputs. Use the existing no-wall-time-limit approval.
Run the control and candidate serially on Maximum-mini-NUIAK. Do not duplicate them on BigDog-NUIAK.
Do not reuse DTM081 as an equal-update control because this schedule has more updates.

Test schedule accounting, reverse labels, group weights, conflicting metadata, protected overlap, and saved-model score parity.
Evaluate all prior conditions, both frame orders, and every fixed disturbance strength.
Report the 80 added comparisons as training fit, never independent evaluation.
Report the retained table pack separately as inspection while its capture evidence remains unresolved.
Accept only under existing regression rules. Preserve both failed and successful weights without replacing deployed models.

The expected handoff includes both schedules, exact hashes, full regression results, and the next evidence-backed decision.
No capture, installation, new architecture, threshold search, or worker transfer is needed for this comparison.

### Interpretation limits

The comparison tests the complete 80-example addition. It does not isolate the effect of the 48 focus-change examples.
The candidate adds identical-image negatives. The control repeats older unchanged-focus examples from the same groups.
Each group keeps its total label weight, but the mix of negative conditions changes.
Report any loss on content changes separately. Do not claim that more positive examples alone cause the result.
The 80 comparisons reuse training frames. They cannot establish independent generalization.
The reserved Fixture checks have also been inspected repeatedly. Keep them separate from an untouched final audit.

### TRANSITION292: separate positive and negative additions

Owner: Maximum-mini-NUIAK. Use the standing training authority within this fixed comparison.
DTM084 fits all added states but loses native and artwork answers. Do not repeat the combined treatment.

Complete the 2 missing combinations:

- Positive-only addition: use the new 48 positive pairs and the control's 32 negative examples.
- Negative-only addition: use the control's 48 positive examples and the new 32 identical-image pairs.
- Append the corresponding reverse pairs in the same order.
- Reuse DTM083 as the old-positive/old-negative result.
- Reuse DTM084 as the new-positive/new-negative result.

Use TRANSITION291's exact registration, control indices, admitted frames, label vector, and weight vector.
Verify all source hashes and the common 1,660-row prefix before execution.
Do not add data, change roles, change the negative weight, or search thresholds.
Start both runs from DTM067 with DTM081 preprocessing.
Keep 120 epochs, seed 42, batch 16, Adam 0.0001, 1,820 rows, and 13,680 updates.
Use 2 CPU threads, serial execution, fixed-last selection, and a combined 256 MiB output cap.
Record both schedules before either launch. Stop on incompatible retained inputs or another owner running the same assignment.

Test that each schedule changes only the intended added label class.
Require identical labels, weights, prefix pixels, reverse order, and total updates across all 4 combinations.
Use the existing trainer and evaluation entrypoints. Cache unchanged reference predictions with exact model/input/preprocessing identities where supported.
Report every previous condition, individual gain/loss, uncertain answer, and fixed disturbance strength.
Compare the positive effect under both negative choices. Compare the negative effect under both positive choices.
Report interactions instead of attributing the combined change to one component.
Do not treat a single-seed comparison as proof that an improvement repeats.

Acceptance requires both complete runs, saved-checkpoint agreement, full regression evidence, and an evidence-backed model decision.
Keep all previously inspected data in development roles. Independent real-app qualification remains separate.
If neither treatment preserves prior successes, stop this data-mix branch and investigate spatially selected evidence before another fit.
No new capture, installation, transfer, provider, export, or deployment follows from this contract.

### TRANSITION297: test spatial evidence before another fit

Owner: Maximum-mini-NUIAK. This follows TRANSITION292's failed regression checks, not another data-mixture attempt.
Use retained images, observed geometry, and cached scores. No new capture, training, threshold search, or deployment occurs.
Keep all existing data roles. Do not use repeatedly inspected Fixture cases as final qualification.

Freeze the selected IDs before scoring interventions. Use up to 640 native pairs and the existing 226-pair distraction sets.
Include focus moves, content-only changes, identical frames, and each supported position region.
Keep unchanged originals as the baseline. Verify model, image, encoding, membership, and geometry hashes.
Use fixed DTM083 and DTM085 weights. Require agreement with cached ordinary predictions before new inference.

Compare 3 region choices:

- Observed before/after focus regions, expanded by 20%. These use truth and are diagnostic-only.
- Image-only regions from the existing change-region tool. Do not give this tool observed focus labels.
- Equal-area control regions with a fixed seed. Record overlaps with known regions rather than hiding them.

Measure how each region retains relevant changes and nuisance changes. Separate proposal coverage from model decisions.
Use bounded interventions that remove differences inside or outside each region. Preserve original images and record the exact transformation.
These transformed images may no longer have the original semantic label. Report score shifts, not invented accuracy on transformed images.
Keep original-pair errors and uncertainty separate. Report direction, position, content type, and related group support.
Do not claim that an observed-region advantage proves deployable accuracy. It identifies what an image-only proposal method still needs.

Use the existing encoder, model loader, and scorer with 2 CPU threads and at most 128 MiB of new reports.
Cache unchanged predictions. Run each fixed intervention once; do not search masks or thresholds against evaluation answers.
Test coordinate transforms, clipping, equal-area controls, empty proposals, cache identity, and missing geometry.
Stop on conflicting observations. Exclude unsupported cases with exact reasons and counts.

Acceptance requires a case-linked diagnosis and one bounded next experiment, or an evidence-backed decision against another fit.
If relevant information disappears during resizing, test resolution next. If region proposals fail, prioritize proposals instead of more epochs.
If known regions help but image-only regions do not, do not train with truth regions as if deployment supplies them.
Keep independent real-app evaluation and TTR receiver work separate from this local diagnostic.

### TRANSITION299: check weak visual evidence

Owner: Maximum-mini-NUIAK. Inputs are retained, eligible native pairs and TRANSITION297's fixed proposals and model scores.
No training, threshold search, capture, or deployment occurs in this diagnostic.
Record input hashes, original roles, independent groups, and the fixed threshold of 24 before scoring additional retained cases.
Reuse compatible cached proposals. Check direction, position, small controls, clipping, and low-contrast focus effects separately.
Report unsupported conditions instead of synthesizing labels. Keep authored disturbance results separate from native efficacy.
Compare the unchanged model with a diagnostic rule that abstains when no proposal exists.
Do not change empty proposals to an unchanged-focus label. Report lost correct decisions, caught errors, abstentions, and coverage.
Test empty support, missing labels, stale caches, coordinate transforms, and duplicated groups.
Use 2 CPU threads and at most 128 MiB of new outputs. Stop on conflicting observations or output collisions.
Acceptance requires exact per-condition counts and one evidence-backed decision about a later prospective test.
If weak-effect support is missing, identify the exact capture requirement. Continue package work without waiting for new data.
Keep final-audit membership untouched. The diagnostic does not establish a deployment threshold.

## Coordination

Verify the r47 transfer and publish exact receipts. Keep sender cleanup separate from receipt.
Accept CHAT285's existing reconnect evidence. Do not repeat delivered provider requests.
BigDog-Coordinator owns expiry and cleanup. Do not renew its expired grant.
Keep BigDog-NUIAK's independent reviews active. Do not duplicate this short local fit remotely.
