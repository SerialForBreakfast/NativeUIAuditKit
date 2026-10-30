# MODEL536 — Next model promotion paths

Real-app accuracy is not independently established. Dataset scores do not measure the percentage of screenshots understood.
See [REAL543](RealAppValidation543.md) for the independent benchmark and historical metric audit.

Owner: Maximum-mini-NUIAK. Reviewed October 25, 2026.

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
The immediate candidate is annotation-quarantine training, not another resolution sweep.

1. Consume the existing IOS534 control and additive graphs. Do not submit duplicate fits.
2. Review their matched IOS527 and Run013 reports, including class-aware and class-agnostic losses.
3. Review row535-native-bounds. Require measured row extent and preserved text bounds across all 4 frames.
4. If row geometry passes, prepare corrected training-only groups using T46 and existing membership preparation.
5. Change only the justified training factor. Use T89 and detector_training_batch478 for train, score, compare, and retention.
6. If retention passes, qualify independent native groups and the exact Core ML consumer path.

Acceptance: retain prior successes, improve the targeted native cases, and pass existing class and release gates.
If quarantine fails, diagnose the remaining 8 missing-box cases before another fit.
Do not erase the 5 competing evaluation labels from historical acceptance reports.
Status: control training completes. Additive training and comparison completion are not established in this review.
The row capture is approved but has no result yet. No new fit is admitted by this plan.
Budgets: reuse the submitted 30-epoch, 1,800 s, 2 GiB fit specifications. New membership requires a new immutable specification.

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

Sillycon-TTR must supply the supported profile producer command and exact source revision.
Existing collectors and verifiers do not construct the complete campaign ledger.
BigDog-Coordinator request 1506 asks for routing. Forwarding and acceptance remain unverified.
This is an implementation dependency, not a request for repeated capture permission.
Maximum-mini-NUIAK owns producer integration, qualification, and automatic intake after that interface is available.

Priority order:

1. Finish existing IOS534 and row535 graphs. They have executable jobs already admitted.
2. Qualify the measured Standard fallback through the exact TTR consumer path.
3. Connect native profile acquisition once, then release separate Standard, HCF, mixed, and temporal data products.
4. Run matched native correction fits after each product passes its own admission checks.
5. Perform independent release qualification and preserve rollback artifacts.

Do not require complete detector inventory for crop-only products.
Do not require temporal history for single-frame crops.
Do not require optional HCF groups for Standard acquisition.
Unknown labels remain unknown. Missing observations cannot be reconstructed from expectations.

## Execution status and evidence

This document defines conditional execution plans. It does not claim missing-input branches are runnable jobs.
No new training, capture, model promotion, or runner restart occurs during this review.
Existing evidence: CurrentState.md, Stream515Qualification.md, SDK530NativeLabelsAndIOS.md, and Review535RowsAndQueue.md.
Queue review confirms ios534-control-train attempt 1 completes. Final comparisons and row capture results are absent.
