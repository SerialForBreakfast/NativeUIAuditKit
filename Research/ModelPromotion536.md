# MODEL536 — Next model promotion paths

Real-app accuracy is not independently established. Dataset scores do not measure the percentage of screenshots understood.
See [REAL543](RealAppValidation543.md) for the independent benchmark and historical metric audit.

Owner: Maximum-mini-NUIAK. Reviewed October 31, 2026.

## Common decision

Keep shipped models and Standard unchanged until each candidate passes its existing release gates.
Separate model weights, inference policies, and consumer integrations. Each can improve without changing the other two.
Use exact matched inputs and pinned weights. Preserve prior successes and report every new wrong selection.
Related frames count as observations, not independent examples. Trainer validation does not establish held-out accuracy.
Freeze thresholds before independent qualification. Keep inspected development groups out of the final holdout.
Require consumer preprocessing, conversion, model identity, latency, and output-size checks before release.
Use existing release requirements. This plan does not lower DS-G8 or authorize a 41-class release.

## 1. iOS detector: shipped 5-class model and Run013 expansion

Run013 achieves matched withheld generated-family custom mAP50 0.6322 versus Run009 0.5549 on 13 supported classes.
Native adaptations still lose retained detections. The 5-class release remains the consumer baseline.
ROW545 annotations are corrected. Frozen, wider-data, and lower-rate candidates still lose retained detections.
The next controlled factor is classification preservation on original training images.

1. Reuse the completed ROW545 control fit and its 7 scoring sets.
2. Train IOS551-PRESERVE with the same 157 images, initialization, seed, learning rates, and 30 epochs.
3. Apply a frozen Run013 teacher only to the 125 original training members.
4. Compare every candidate score with ROW545, Run013, and the earlier native control.
5. If previous successes regress, run the predefined class-versus-geometry diagnoses.
6. If retention and native gains pass, prepare independent qualification. Do not promote from these development results.

The fixed fit permits 1,800 s and 2 GiB. Teacher overhead remains unmeasured.
The graph includes 1 fit, 7 scores, 1 decision, 3 retention reports, and 7 conditional diagnoses.
These 19 nodes represent 1 investigation. They are not 19 independent experiments.

## 2. tvOS detector: general model and scoped proposal candidates

The general detector covers 112/120 registered controls on the SDK review set. Scoped coverage is 9/120 there.
A different native set favors the scoped detector. Neither result supports wholesale replacement across domains.
Lower confidence recovers 3 registered controls but adds 46 proposals.
Its downstream focus comparison adds no gain and loses 1 success. Close that correction.

1. Preserve the existing domain-specific proposal baselines.
2. Use retained geometry reports to name missing or malformed boxes by control type and scene group.
3. Produce complete training-only inventories for those failures. Partial registered controls cannot establish detector precision.
4. Run one matched detector fit with existing T89 and full detector and focus comparisons.
5. Reject recovery that increases wrong focus selections or loses retained detections.

Acceptance: improve targeted coverage without lost prior successes; pass complete-inventory false-positive and consumer focus checks.
Blocker: qualified independent native training groups and complete detector annotations.
Resolve semantic roles from app evidence. Native UIButton alone does not establish primary versus secondary roles.
Do not block binary focus training on these detector-role requirements.
Budget: use the existing training envelope only after exact membership and configuration are recorded.

## 3. Standard single-frame focus: crop model and full-screen policy

The fixed resolution fallback improves 13/43 to 28/43 retained selections across 13 recorded groups.
It loses no success and adds no wrong selection. It retains 2 existing wrong selections and 10 misses.
This is the nearest measured pipeline candidate, not a released model.
New SDK scenes expose a separate crop limitation: TEACHER496 selects only 1/40 focused endpoints correctly.

1. Complete TVOS515-CONSUMER with the exact scoped detector, teacher496 weights, and resolution rule.
2. Compare TTR outputs with saved references on identical images and crops. Keep navigation disabled.
3. Measure end-to-end latency, including proposals and both resolutions when used.
4. Qualify separate native groups containing visible unfocused controls and no-focus scenes.
5. In parallel, prepare native crop training from observed focus and bounds after profile acquisition passes.

Acceptance: preserve the retained 15 gains, prior successes, and no-focus outcomes through the actual consumer path.
Independent qualification must satisfy existing release gates. The retained score alone does not authorize Standard replacement.
Blocker: exact consumer path differs from the active optional observer; native crop groups lack qualified profile continuity.
Reuse the existing endpoint scorer and batch comparisons. Do not train merely to resolve consumer parity.

## 4. Optional HCF crop model and observer

The active optional observer passes retained TTR parity on 38 observations and 264 crop hashes.
Maximum score error is below 0.000003. This supports the bounded observer integration already qualified.
It does not establish independent application accuracy or navigation authority.

1. Freeze the active model hashes, thresholds, proposal rule, and input preprocessing.
2. Qualify separate native groups with observed HCF profile, focus identity, and control bounds.
3. Compare full screenshots and supplied-box diagnostics separately.
4. Include light backgrounds, decorative borders, small controls, visible no-focus distractors, and transitions.
5. Verify the exact TTR observer path on at least one independent qualified app before broadening its claim.

Acceptance: preserve current successes and no-focus outcomes; add supported coverage without new wrong selections.
If proposals fail but supplied-box scoring passes, correct proposals before retraining the crop model.
Blocker: profile producer and independent app groups. Existing review captures remain available for diagnostics.
Keep HCF optional. Its data acquisition must not block independent iOS work.

## 5. Mixed focus crop model

The mixed model has content-sensitive false positives. Existing geometry corrections do not resolve them.
It must qualify separately from HCF; HCF success does not certify mixed behavior.

1. Use independent observed-focus crops with unfocused selected controls, bright artwork, and decorative borders.
2. Compare a matched original-data rehearsal control against one added hard-negative training arm.
3. Use existing crop training and retention templates. Preserve original group roles and fixed thresholds.
4. Evaluate full-screen selections and visible-distractor no-focus cases through TTR.

Acceptance: reduce the named false positives without lost focused successes or new wrong selections.
If the training data is unavailable, keep the existing observer bounded; do not rerun failed inference recipes.
Blocker: independent eligible native crops with observed profile continuity.

## 6. Temporal focus model

Both retained candidate seeds recover historical development cases. Native departure remains a known failure.
Grayscale and symmetric temporal scoring introduce regressions. Do not repeat those rejected corrections.

1. Produce independent before/after groups for arrival, departure, movement, and unchanged focus with moving content.
2. Include auto-hide, modal dismissal, and return to content. Use observed states rather than expected input outcomes.
3. Use existing episode intake and T47 preparation. Require frame alignment and complete event history for temporal claims.
4. Run matched T49 training with retained rehearsal, then compare against both the baseline and a single-frame ablation.
5. Verify event timing, no-focus behavior, and recovery through the consumer path before release.

Acceptance: recover departure without mistaking background motion for focus changes; preserve retained successes.
Blocker: independent eligible temporal groups with profile and timeline evidence.
Budget: T49 retains its existing 10-epoch contract. Record exact time and storage bounds before admission.

## Shared blocker and execution order

The producer now exists. Its current source accepts only test-role tvOS cases.
Maximum-mini-NUIAK must not relabel those captures as training data.
Sillycon-TTR must support new training and validation groups with explicit ancestry and observed profile evidence.
The request is stored at coordinator cursor 1836. Forwarding and acceptance remain unconfirmed.

Maximum-mini-NUIAK now compiles static crops and temporal products independently through sdk_training513.
Missing action timing blocks temporal training without blocking qualified static crops.
Detector taxonomy and full inventory remain separate requirements. Binary focus crops do not inherit them.
Two software campaigns exercise the same compiler with different configurations.
This proves software reuse. It does not establish native training eligibility.

Priority order:

1. Qualify retained Standard replay through published TTR revision ac85177b.
2. Execute the matched iOS preservation graph through the detached runner after qualification.
3. Review complete real-app labels independently of TTR provenance work.
4. Release each native product when its own evidence and producer role pass.
5. Qualify exact HCF checkpoint restoration before any approved continuation.
6. Prepare independent temporal groups before training a departure correction.

Unknown labels remain unknown. Missing observations cannot be reconstructed from expected actions.
Standard remains first. HCF stays optional. Inspected evidence remains development evidence.

## Execution status and evidence

See Tasks.md for current admissions and exact blockers.
See reports/work/PARALLEL551 for implementation tests and frozen experiment specifications.
TTR candidate activation still needs the separately requested authorization.
Executed crop identity remains unavailable in the published runtime contract.
Real-app accuracy remains unestablished. No result in this plan changes a shipped model.
