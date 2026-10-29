# SDK529 — Separate focus state from interaction state

Owner: Maximum-mini-NUIAK. Date: October 25, 2026.

## Observed failure

The original sequence expects no focus, focus arrival, then no focus after disabling the controls.
The first 2 captures succeed. Both playPause inputs report delivery.
The final SDK inquiries report left as focused while both controls report enabled=false.
The remote session closes successfully. No final screenshot exists in that failed attempt.
This evidence does not establish whether a visible focus effect remains on the disabled control.
It also does not establish a general UIKit defect or a TTR transport failure.

The failed attempt is sdk529-native-arrival-departure-r4, attempt 1.
Its last SDK inquiry and input receipts remain under reports/work/research-queue/jobs.
Preserve its 2 frames and raw native observations.

## Documentation and interpretation

Apple describes isEnabled as interaction state. It does not promise that disabling clears existing focus.
Source: [UIControl.isEnabled](https://developer.apple.com/documentation/uikit/uicontrol/isenabled).

UIFocusSystem.focusedItem reports current focus. An app requests focus updates; the focus engine decides the result.
Source: [UIFocusSystem](https://developer.apple.com/documentation/uikit/uifocussystem).

setNeedsFocusUpdate requests a reset through preferred focus. The request does not establish a nil focused item.
Source: [setNeedsFocusUpdate](https://developer.apple.com/documentation/uikit/uifocusenvironment/setneedsfocusupdate()).

Apple lists removal from the view hierarchy as a trigger for automatic focus updates.
Removal can move focus to another control. It does not guarantee an empty focus result.
Source: [tvOS focus guide](https://developer.apple.com/library/archive/documentation/General/Conceptual/AppleTV_PG/WorkingwiththeAppleTVRemote.html).

Our original test therefore contains an unsupported expectation. The observed contradiction is useful research evidence.
Do not change reported focus to satisfy that expectation. Do not infer no-focus from enabled=false.

## Corrected executable strategy

Keep the same source-built sample and the same 2 bounded inputs.
Require fresh authenticated identity and a valid control session before input.
Capture each endpoint even when actual focus differs from the expected result.
Preserve enabled state, native focus, geometry, and frame-alignment findings separately.
Retain image labels as unknown when the current visual-label checks fail.
Do not weaken production crop admission or convert disabled controls into negative focus labels.

Report execution and scientific acceptance separately:

| Outcome | Execution result | Research result |
| --- | --- | --- |
| Valid captures support the original sequence | Complete | Supported; native departure qualified only with complete history |
| Valid captures contradict the expected sequence | Complete | Contradicted; no departure qualification |
| Captures lack sufficient temporal evidence | Complete | Inconclusive; retain eligible static analysis |
| Transport, identity, input delivery, or cleanup fails | Failed | Preserve partial evidence; diagnose the exact operation |

The original departure criterion remains no-focus, focused, no-focus with complete event history.
The correction does not lower that criterion. It stops discarding observations that fail it.
An uncertain input is never replayed automatically.

## Implemented comparison

The existing sdk_capture527 adapter now records expectedNativeStates, observedNativeStates, and nativeFocusOnDisabledControl.
It also records alignedImageStates, hypothesisOutcome, and departureQualified.
The hypothesisOutcome field evaluates the original departure expectation, not model accuracy.
No model or training data is accepted automatically.

All 14 focused tests pass. They include disabled-focus persistence, missing events, uncertain input, and incorrect launch identity.
The disabled-focus test captures all 3 endpoints and reports contradicted rather than timing out.
The SDK listener-unavailable error now names missing live evidence instead of a generic identity mismatch.

Successor sdk529-native-observed-focus-r5 is approved through the existing runner.
It uses 3 new frames. The prior attempt captured 2 frames, so the cumulative plan uses 5 of 6 authorized frames.
The remaining execution budget is 739 s and 98,436,382 bytes.
No new TTR build, installation, settings change, dashboard restart, or model replacement is required.

## Next scenario comparisons

1. Keep disabled-but-focused as a separate robustness condition. Compare visible evidence before assigning image labels.
2. Test removal and restoration of the focused view. Record its actual replacement focus or verified no-focus state.
3. Test modal dismissal and return to app content. Preserve presentation identity and previous successes.
4. Test playback controls disappearing while content moves. Separate native focus, visible focus effects, and annotation eligibility.

These scenarios need their own bounded specifications and actual producer evidence.
Do not repeat the disabled-state sequence until it returns the desired answer.
Keep Standard and the optional observer unchanged until matched model comparisons justify a change.

## Verified native result

Successor sdk529-native-observed-focus-r5 completes in 31.978 s. All recorded output hashes verify.
The 3 native states are no_focus, focused, and focused. The final focused control reports enabled=false.
The original departure hypothesis is contradicted. departureQualified remains false.
The image-label states are no_focus, focused, and unknown. No disabled-control image becomes an automatic negative label.

The episode includes all 11 events in sequence interval 6–17. Temporal review is eligible with no reported history gap.
The identity-based transitions are arrival followed by unchanged. The control lifetime remains the same.
The remote session closes with cleanup stopped and controlBusy=false.
This proves the corrected experiment can retain a negative result through the real runner.
It does not prove visible focus appearance, native departure, playback behavior, or model improvement.

The background runner is healthy and idle after this completed comparison.
No additional capture is queued to repeat the contradicted assumption.
The next useful producer change is a separate removal/restoration scenario, with its own bounded specification.
Independent annotation review remains useful without another native capture.

## Retained scoring and removal candidate

The existing endpoint adapter now accepts pinned episode requests through `sdk-endpoint-episode-v1`.
It scores visible registered controls even when they are disabled.
Unknown image labels remain unknown. They do not count as gains, losses, or no-focus successes.
All image and evidence files enter the queue specification as pinned inputs.
The original endpoint request and its admission rules remain unchanged.

The native scoring job `sdk529-retained-native-crop-scores` completes through the detached runner.
TEACHER495 and TEACHER496 each score both controls above 0.998 on all 3 frames.
Both models miss the known focused frame because multiple scores exceed the fixed 0.85 threshold.
Both abstain on the no-focus frame because selection is ambiguous.
This correct abstention does not prove that either model recognizes no-focus.
The disabled-focus frame remains unknown. Neither model gains or loses a known selection in this comparison.
These are 3 related frames from 1 scene, not independent accuracy trials.

The next queued comparison uses PROFILE425 against TEACHER496 on these same retained frames.
It asks whether pre-adaptation weights separate the controls better.
The existing episode report also consumes verified completed scores without another inference run.
Both jobs use existing templates. Each permits 800 s and 100 MB.
These are short diagnostics, not an overnight workload.
Do not train or change thresholds from this single scene alone.

Maximum-mini-TTR has a source-built removal candidate in `.local-work/sdk529-removal`.
Its `--sample-removal-scene` option starts with enabled controls.
Two playPause inputs remove both views, then restore the same objects and identities.
The sample records app-declared hierarchy changes separately from actual UIKit focus.
It unregisters removed controls instead of inventing offscreen boxes.
The capture adapter supports `sdk-removal-restoration-request-v1` with the same bounded execution path.
It observes 3 endpoints and tests focused, no-focus, focused as a hypothesis.
A different native result remains evidence. It does not trigger repeated inputs.

The candidate builds successfully. Configuration checks reject 9 conflicting or duplicate options.
All 15 capture-adapter tests and 13 endpoint tests pass.
The new scenario needs installation, launch, capture authorization, and one idle validator reload.
An approval request specifies 3 frames, 2 inputs, 800 s, and 100 MB.
No new native capture is admitted before approval and fresh enrollment.
Standard, previous successes, and shipped models remain unchanged.

## Completed comparison decision

All 3 new jobs complete. Their reports match completed output receipts.
PROFILE425 also misses the focused frame, but it does not show the adapted models' saturation.
Its no-focus scores are 0.0465 and 0.0321. Its focused-frame scores are 0.000015 and 0.4331.
The native focused control is the first control. The other control has the higher score.
Thus adaptation changes score calibration, but this scene also exposes a pre-existing focus discrimination error.
Neither a lower threshold nor forced maximum selection fixes this focused frame safely.
Do not select another threshold or training run from this scene alone.

The native episode report verifies complete temporal history and preserves the unknown final image label.
The next useful correction is representative native focus supervision, with controlled removal and restoration as an independent diagnostic.
The next training batch needs independent qualified scene groups and the retained-success comparison.
The built sample and adapter are ready for the pending bounded native authorization.
No additional model job remains queued from this tranche. The 3 jobs are short diagnostics and have already finished.

## Approved native removal trial

The maintainer approves the sample trial and one idle dashboard restart.
The restart refuses active work and completes with the queue preserved.
Maximum-mini-TTR verifies the source candidate hash and clear Simulator ownership.
The removal sample installs and launches with fresh private enrollment.

Job `sdk529-native-removal-restoration-r1` is submitted and approved for the detached runner.
Its limits are 3 frames, 2 playPause inputs, 800 s, and 100 MB.
It shares the original scene group to prevent treating this variant as independent evidence.
The trial records actual focus after removal and restoration. Contradictory results remain valid observations.
No settings, physical devices, Standard models, or prior evidence change.
Native execution and scientific acceptance remain pending at admission.

## Removal results and independent follow-ups

The removal trial completes in 32.642 s. All 47 output hashes verify.
Native focus follows focused, no-focus, focused. All 12 history events are present.
The remote session closes and reports controlBusy=false.
The before and restored screenshots have identical hashes. They are repeated observations, not independent examples.
The middle frame reports registered_geometry_not_stable. It remains an unknown image label.
Native departure qualifies; the full image sequence does not qualify.

Source inspection identifies a sample defect. The empty inventory produces an empty geometry signature.
The SDK stability helper correctly treats an empty signature as unavailable.
The sample now includes the registered control count in its signature.
This distinguishes an observed empty inventory from unavailable geometry without changing SDK validation.
The corrected sample builds. Its configuration tests include empty and nonempty signatures.
A new bounded trial requires the pending installation and launch approval.
No existing packet, label, or result is rewritten.

Two removal scoring jobs complete through the runner.
TEACHER495, TEACHER496, and PROFILE425 miss both known focused endpoints.
The middle frame remains unknown for every model. No model gain or replacement follows.
Training still needs representative native focus groups with verified roles and observed profile evidence.

The independent SDK528 review verifies 5 coverage gains and 21 losses at 960 pixels across 8 retained groups.
Reject standalone replacement of 1280-pixel inference.
Six new comparisons preserve every baseline box and add only non-overlapping cached 960-pixel proposals.
Groups 4 and 6 add no boxes. They are not rerun.
The existing endpoint adapter supports this comparison through proposalMode=resolution-supplement.
Weights, crop preprocessing, confidence, and selection threshold remain fixed.
All 25 focused comparison tests pass, including unchanged confidence-comparison behavior.

Nine jobs are admitted: 6 supplemental groups, 1 aggregate, and 2 removal scoring jobs.
At the batch review, both removal jobs and supplemental groups 1–3 complete with verified receipts.
The first 3 supplemental groups have no gains, losses, or new wrong selections.
Groups 5, 7, and 8 remain pending. The aggregate waits for their dependencies.
These are short diagnostics. They do not provide overnight work.
The detached runner retains execution ownership.

Both IOS527 retention decisions remain contradicted because they lose previous detections.
Do not promote either model or repeat the same training settings merely to fill the queue.
The next training decision needs a case-linked retention correction and the complete matched regression set.
Standard and shipped models remain unchanged.

Evidence: reports/work/SDK529/removal-followup-review.json and supplement-tests.log.
The build receipt is in Developer/TVTestRig/.local-work/sdk529-removal-r2/build-receipt.json.

## Corrected trial admission

The maintainer approves the corrected sample trial.
Maximum-mini-TTR verifies the candidate hash and clear Simulator ownership before installation.
The corrected source-built sample installs and launches with fresh private enrollment.
Job `sdk529-native-removal-restoration-r2` is submitted and approved for the detached runner.
Its scope is 3 frames and 2 playPause inputs within 800 s and 100 MB.
The job preserves the original scene group, first trial, models, and previous successes.
No dashboard restart occurs. Native results remain pending at admission.

## Qualified sequence and next research decision

The corrected removal trial completes with focused, no-focus, focused image labels.
Native departure and the full image sequence both qualify. Output hashes verify.
The new screenshots exactly match the previous trial's pixels.
Two temporal reports therefore reuse existing model scores without another crop inference run.
All tested crop models miss the 2 focused observations and abstain on the empty scene.
The 2 focused observations share identical pixels. This is 1 scene, not independent accuracy evidence.
Empty-scene abstention does not test visible distractors.

A separate frozen-detector comparison uses only the 2 unique screenshots.
The general detector covers both registered controls. DETECTOR469R covers neither.
Retain the general detector. Geometry and focus classification remain separate correction needs.
The annotation audit finds valid geometry but unresolved semantic roles for left and right.
UIButton and a button accessibility trait do not establish primaryButton versus secondaryButton.
The audit keeps both labels unmapped. No detector training data is admitted.

All 6 supplemental-resolution groups finish without a focus gain, lost success, or new wrong selection.
Their 42 retained frames include 2 correct focused selections, 28 misses, 8 correct abstentions, and 4 false selections per arm.
The additional proposals do not change these outcomes. Close this branch without changing runtime behavior.

The independent iOS comparison isolates the existing additive-data recipe from its original-only control.
Initialization and optimizer settings match. The 144-image recipe includes extra exposure compared with the 128-image control.
It gains 12 detections and loses 13 against that control.
It gains 20 and loses 14 against Run013. Reject model replacement.
Matched gains are 6 labels, 4 list rows, and 2 home indicators.
Matched losses are 6 labels, 3 list rows, 2 progress views, 1 home indicator, and 1 navigation bar.
These are development label outcomes. They are not independent app accuracy or equal-compute data-effect estimates.

Six T42 jobs now compare the same cached iOS outputs without class matching.
They distinguish class changes from missing or displaced boxes across all 6 comparison partitions.
No training, inference, capture, or label changes occur in these jobs.
The runner owns execution. These short diagnostics do not fill an overnight window.

## Next substantial tranche

1. Review the 6 matched geometry reports and identify exact retained failures before another iOS fit.
2. Review the sample's semantic control roles and record explicit mappings for left and right.
3. Connect current observed Focus Style evidence before profile-specific native crop training.
4. Use qualified independent native scene groups for the next training comparison, with the complete retained-success suite.

The current removal group stays review-only and excluded from training.
Do not increase its frame count and describe repeated frames as broader training coverage.
Standard, shipped models, prior successful cases, and original captures remain unchanged.
