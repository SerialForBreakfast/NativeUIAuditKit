# SDK529 — Adopt native UI and timeline evidence

October 25, 2026. Owner: Maximum-mini-NUIAK.

## Audit result

The Developer TTR source exposes more information than current NUIAK preparation uses.
Source inspection confirms capabilities. It does not prove instrumentation exists in every app or retained capture.
Keep current experiments running. Add these connections to existing packet, preparation, and comparison templates.

| Evidence | Current NUIAK use | Next use |
|---|---|---|
| ID, lifetime, revision | Packet rows retain identity. Transition classification compares only focus ID strings. | Track control lifetime across frames. Distinguish replacement, movement, revision, and reappearance. |
| Parent IDs and native classes | Crop metadata retains these fields. | Review semantic class mappings and associate text with its owning control. |
| Accessibility traits and reviewed public accessibility fields | SDK supplies optional fields. Packet review does not retain these fields in normalized rows. | Preserve optional evidence and provenance for semantic labels and confusion slices. |
| Measured bounds, clipping, transforms, viewport | Packet review validates screen-pixel bounds. Layout diagnostics contain additional geometry. | Measure localization errors, clipped controls, scrolling, and coordinate transforms. |
| Native focus and focus decisions | Endpoint focus and basic arrival/departure are used. | Separate actual focus, requested focus, rejected changes, accessibility focus, and selected state. |
| Sequence numbers, input correlation, lifecycle and presentation | Existing action-pair checks enforce ordering. No complete sequence-based training product exists. | Build capture episodes for dismissals, redirects, temporary no-focus, and focus return. |
| Playback and controls visibility | TTR inquiry exposes retained playback events. NUIAK preparation does not consume them. | Test auto-hide, player dismissal, interruption, and return to app content. |
| Geometry stability and history coverage | SDK exposes bounded stability and history-gap evidence. | Compare capture timing policies and reject unsupported temporal conclusions. |

## Reusable experiment graph

A short scenario request should produce one episode with frame hashes, native snapshots, and bounded event references.
Normalize this evidence once. Branch into geometry, semantics, focus, and temporal analyses independently.
Use separate eligibility results for each product. Missing playback events must not block static geometry analysis.
Missing observed Focus Style must not block general diagnostics. Existing profile-specific training gates remain unchanged.
Do not treat incomplete registered controls as complete detector labels.

The graph should support these initial scenarios:

1. A focused control moves while its content changes.
2. A list recycles a control ID for a new lifetime.
3. Playback controls hide while the video continues.
4. A modal closes and focus returns to its previous control.
5. Playback ends and the app redirects to its own home screen.
6. Focus becomes temporarily absent during a transition.

App home and tvOS Home are different destinations. An app SDK cannot alone establish focus after another app becomes foreground.
Require independent foreground evidence for that boundary. Unknown observations remain unknown.

## Implementation tasks and acceptance

### SDK529-01 — Preserve semantic fields and identity. Priority P1.

Extend sdk_packet502 and sdk_training513 normalized outputs with optional native semantic fields and their source references.
Preserve full identity, parent, accessibility traits, reviewed public text, native class, layout revision, and observed visibility.
Replace string-only transition matching with an explicit lifetime-aware comparison in the supported pair path.
A revision change alone must not invent a new control. A lifetime change must not silently become unchanged focus.
Acceptance: retained packets remain compatible; missing fields stay unavailable; recycled IDs, changed lifetimes, and parent changes pass positive and negative tests.
Prove reuse with 2 scenarios through configuration. Do not alter sources while their queued consumers run.

### SDK529-02 — Qualify class and geometry annotations. Priority P1.

Use existing class-review tools to combine native class, semantic role, traits, parent structure, and measured bounds.
A UIView subclass name alone does not define a detector class. Preserve ambiguous mappings for review.
Qualify complete-label coverage separately from registered-control crop eligibility.
Acceptance: coordinate transforms, clipped bounds, duplicate labels, unknown classes, and incomplete inventories have deterministic results.
Compare matched detector errors before and after reviewed annotation corrections. Preserve previous successes and data exclusions.

### SDK529-03 — Add an episode intake product. Priority P1.

Extend existing pair intake to retain event sequences, clock domains, lifecycle, presentation, playback, and action references.
Keep caller-asserted input correlation distinct from native callback observations.
Detect missing events, history eviction, producer loss, out-of-order events, and producer restarts.
Acceptance: a complete episode joins exact frame evidence; incomplete history permits eligible static analysis but rejects unsupported causal labels.
Split by episode ancestry. Adjacent frames must not cross training and evaluation groups.

### SDK529-04 — Compare capture timing policies. Priority P1.

Compare the existing fixed-delay policy against observed focus plus registered-geometry stability on identical scenarios.
Measure label/frame disagreement, transition frames, missed transient states, capture latency, and output volume.
Moving video must not force indefinite waiting. Stable control geometry does not imply stable video pixels or complete animation settling.
Define a fixed maximum wait and sample budget before capture. Include deliberately unstable and timeout cases.
Acceptance: improve alignment without losing transient-event coverage or exceeding the approved budget.

### SDK529-05 — Qualify dismissal and focus-return sequences. Priority P1.

Use deterministic Fixture or instrumented sample scenes for auto-hide, modal close, and playback-to-home return.
Record pre-transition, transition, and settled endpoints with actual focus and presentation identity.
Measure wrong retained selections, false no-focus, stale-control selection, and time to correct reacquisition.
Keep visual-focus accuracy separate from navigation correctness. A correct screen transition does not prove correct focus selection.
Acceptance: all prior successes stay preserved; no stale selection survives dismissal; missing final focus remains an explicit failure.

### SDK529-06 — Use episode evidence for data selection. Priority P2.

Cluster failures by independent episode, control family, transition, and error type.
Compare diverse failure selection with a deterministic random sample at equal annotation and training budgets.
Avoid oversampling adjacent frames or repeating the same application layout.
Acceptance: compare distinct recovered errors, retained losses, data diversity, and preparation cost through existing training graphs.

## TTR requests, only where qualification shows a gap

- Frame-to-event references with capture intervals, clock-domain mappings, and uncertainty where available.
- Explicit lifecycle or presentation completion evidence for dismissals, without inferring it from elapsed time.
- Reliable lifetime and reuse reporting for recycled controls.
- Coverage metadata that distinguishes registered inventory, truncation, clipping, and unavailable occlusion.
- Exported episode manifests that preserve event gaps, app build, runtime, and instrumentation capabilities.

First inspect existing inquiry, layout, playback, and export contracts. Request only fields missing from the usable export path.
These are proposed requirements. This document does not claim they are missing SDK APIs or sent feature requests.

## Boundaries

Native geometry does not establish screenshot alignment without its coordinate transform and capture bracket.
UIKit hidden and alpha observations do not prove occlusion by another view.
Accessibility focus, preferred focus, selected state, and actual tvOS input focus remain separate labels.
SDK visual contrast does not establish HCF Focus Style. Current SDKVisualContext explicitly leaves HCF unknown.
Use approved public or synthetic text. Do not turn arbitrary account text into training labels.
Use SDK metadata as supervision for screenshot-only models. Do not silently give evaluation models privileged metadata.
Evaluate an SDK-assisted model as a separate product if that becomes an explicit goal.

## Inspected source

TTR revision: e4c693c5237b8498a23e60d51c104ee5f7600a16.
Sources: UIRecorder.swift, AppleUIHooks.swift, UILayoutDiagnostics.swift, VisualContext.swift, PlaybackEvidence.swift, CausalSummary.swift, Inquiry.swift.
NUIAK sources: sdk_packet502.py, sdk_campaign508.py, sdk_training513.py.
The initial audit changed no runtime sources. The implementation status below records subsequent changes.


## Implementation status — October 25, 2026

The work remains incomplete. No model or capture policy is promoted.

- `sdk_semantics529.py` preserves optional semantics and compares full control identities.
- `sdk_episode529.py` joins pinned frames with authenticated event history and clock brackets.
- `sdk_timing529.py` compares capture policies on retained frames. It does not measure live capture speed.
- Unsettled frames remain eligible for supported temporal analysis. They do not become stable image labels.
- Missing temporal evidence does not block qualified static diagnostics.
- 25 focused Python tests pass. Two configurations pass through an isolated queue.
- 29 TTR SDK tests pass. The first run lacked the required test output environment; the corrected run passes.
- The source-built TTR candidate passes package verification. Compilation takes 104 seconds.
- The candidate adds bounded event history and clock brackets to capture observations.
- The candidate preserves packet errors instead of masking them as `invalidArgument`.
- The new CLI envelope regression test is written but not executed yet.

The isolated queue tests use synthetic software fixtures. They do not establish native capture accuracy.
The capture adapter correction activates under the runner lock after both iOS fits complete.
The runner receives the bounded native capture and retained-recovery jobs listed below.

### Remaining execution and integration

1. Qualify reviewed class mappings and complete-label coverage from native evidence.
2. Collect complete matched timing and dismissal episodes through the runner.
3. Compare diverse and random training selections through existing training graphs.

Candidate activation, sample enrollment, and packet/crop/pair integration are complete.
The integrated suite passes 65 tests. Native sequence qualification remains incomplete.

TTR reply 1469 identifies an existing Focus Style collector and explicit profile attachments.
It requires an owned session already positioned on the Focus Style screen.
The SDK packet does not collect that profile or construct a continuity ledger.
Contrast remains separate from HCF evidence. General geometry analysis does not require an HCF claim.

Local evidence: `reports/work/SDK529/software-tests.log` and `reports/work/SDK529/coordinator-receipt.json`.
The TTR package log and signed candidate receipt remain in its ignored `.local-work/sdk529` paths.
The coordination correction is stored at cursor 1470. Forwarding is not yet confirmed.


### Native execution update

The maintainer approves candidate activation and sample relaunch. Both operations complete.
The candidate passes passive preflight. Fresh SDK inquiry supplies native focus, geometry, and bounded timeline evidence.
The sample reports historical queue loss. That history does not qualify complete transitions.

The first native packet contains a 3840 × 2160 image and has no packet issues.
It reports observed no-focus. It does not establish focused-control performance or a model improvement.
Publication fails because the expanded reply exceeds the previous 256 KB limit.
The adapter now accepts bounded replies up to 8 MiB. Existing job output budgets remain unchanged.
The original capture and failed attempt remain preserved.

- `sdk529-native-packet-01`: capture succeeds; queue publication fails.
- `sdk529-native-packet-01-recovery`: approved diagnostic intake of verified existing bytes; no recapture.
- `sdk529-native-packet-02`: revoked before execution because its dependency references failed publication.
- `sdk529-native-packet-02-r2`: approved remaining frame, dependent on retained recovery.

The 2 capture specifications allocate 700 seconds and 100 MB combined.
The runner owns execution. No model, data role, settings, or physical device changes occur.
Further work includes complete event retention, existing crop-path integration, native sequence qualification, and matched training selection.
These tasks remain open. Software tests and packet recovery do not close the full SDK529 goal.

### Verified recovery and episode results

The approved capture-root correction is active. No submitted specification changes. No running job is cancelled.
Both native packet recovery jobs complete. Their output hashes match their result receipts.
The second capture needs receipt recovery because publication does not record its dependency read.
The adapter now reads dependency receipts before capture. Both original attempts remain preserved.

The native episode intake and timing replay also complete with verified outputs.
The episode has aligned frames and permits static diagnostics. Missing events prevent temporal review.
The timing replay reports `episode_event_gap`. It does not establish a better capture policy.
Both frames show no focus and have identical image hashes. They are not independent examples.
No model improvement, training admission, or Standard change follows from these results.

Next, repair bounded event retention and collect a complete transition episode.
In parallel, qualify semantic class mappings before using native controls as detector labels.
A native UIButton class alone does not distinguish primary buttons from collection items.
The runner remains active. At this check, it waits for approved work that passes readiness checks.

Evidence: `reports/work/research-queue/jobs/sdk529-native-packet-02-recovery/attempts/1/result.json`.
Timing result: `reports/work/research-queue/jobs/sdk529-native-timing-replay/attempts/1/out/benchmark_summary.json`.

### Event-retention correction and independent preparation

SDK529-01 is complete at the packet, crop, and pair integration boundary.
The remaining P1 and P2 tasks are incomplete.

The sample alternates window-point and screen-pixel registrations on each callback.
That creates false geometry events and exhausts the pending event buffer.
The corrected UIKit hook registers one observation in the requested coordinate space.
Unchanged registration refreshes observation time without adding a change event.
Real geometry changes remain recorded. Existing callers retain window points by default.
The corrected sample builds from source. Installation and bounded native comparison approval are pending.
The active sample and TTR app remain unchanged during this source work.

Validation:

- 3 timeline tests pass, including the overflow reproduction and corrected stable observations.
- 34 related XCTest checks pass. One receiver-process test skips because its binary path is not supplied.
- All 10 host envelope tests pass. The initial test build finds an incorrect test error-code type; the corrected test passes.
- 28 Python checks pass across annotation, episode selection, episode intake, and timing.
- Annotation mappings now require pinned review evidence during production evaluation.
- The episode selector uses verified comparison outcomes and preserves original data roles.
- Diverse and random selection use equal frame and annotation budgets from the same group pool.
- Unequal costs and shared episode ancestry fail explicitly. No difficult group is silently removed.

The selector is software-tested. It has no completed native selection or matched training comparison yet.
Reviewed semantic labels and eligible training episodes still block those results.
The retained sample uses generic action controls. A native class name alone does not establish primary versus secondary action semantics.
Do not convert layout names or model predictions into ground-truth classes.

Sillycon-TTR confirms overlapping optional capture mapping and saved-history query work.
Maximum-mini-NUIAK sends the exact changed contracts through BigDog-Coordinator at cursor 1474.
The message is stored. Forwarding is not yet verified.

Next execution order: install the approved corrected sample, qualify complete focus episodes, then compare capture policies and dismissal behavior.
Prepare matched training selection only after episode roles and labels pass qualification.
Standard, shipped models, previous captures, and failed attempts remain preserved.

The episode selector also passes 2 configurations through an isolated queue.
The fixture uses synthetic verified model receipts. No live training or capture runs in this test.
The 8-test selector suite includes unequal costs, repeated ancestry, deterministic ordering, and preserved evaluation roles.
Evidence: `reports/work/SDK529/selection-queue-tests.log`.

### Continuation boundary

SDK529-01 is complete. SDK529-02 through SDK529-06 remain open.
The corrected sample requires installation and launch approval before native qualification.
The requested comparison is limited to 6 frames, 800 seconds, and 100 MB on the intended tvOS Simulator.
That comparison does not close auto-hide, modal dismissal, playback return, or equal-budget training requirements.
Those remain explicit parts of the original goal.
Neither the active TTR application nor the background runner is restarted in this tranche.

### Matched focus episode reports

`sdk_focus_episode529.py` now consumes verified endpoint scores and pinned native episodes.
It recomputes outcomes from boxes and scores instead of trusting recorded outcome labels.
The report separates false no-focus, wrong selection, and selection at a departed control location.
A reused location does not establish stale internal identity.
The report preserves previous successes and lists every new wrong selection.

Reacquisition intervals use sampled native focus observations and explicit clock uncertainty.
They do not measure action-to-response latency or unobserved transient states.
Missing timeline history disables timing claims but preserves supported frame comparisons.
Unknown or unaligned frames do not become ground truth.

All 8 focused tests pass. Two configurations execute through an isolated queue with synthetic model receipts.
Changed source bytes fail verification. Evidence: `reports/work/SDK529/focus-episode-queue-tests.log`.
This completes the comparison software connection, not native dismissal qualification.
No new live experiment or training job is admitted from these software tests.
The requested Simulator sample deployment approval is still pending.

### Completion audit — native execution dependency

The P1 and P2 goal is not complete. The capture-root approval is already applied.
This approval does not cover the separate corrected-sample installation and launch request.

| Task | Verified result | Required result still missing |
| --- | --- | --- |
| SDK529-01 | Packet, crop, and pair integration preserves semantic evidence and lifetime identity. | None for this software integration task. |
| SDK529-02 | Annotation checks and pinned review rules pass software tests. | Reviewed native class mappings and matched detector comparisons on those annotations. |
| SDK529-03 | Both retained packet receipts verify. Episode intake completes. | A complete native transition episode without missing events. |
| SDK529-04 | Retained replay reports the event gap correctly. | Prospective fixed-delay and stability trials, latency, transient coverage, moving backgrounds, and timeout results. |
| SDK529-05 | Matched focus reporting passes isolated queue tests. | Native auto-hide, modal dismissal, playback return, and temporary no-focus comparisons. |
| SDK529-06 | Equal-cost selection passes configuration reuse tests. | Qualified native failure groups, actual matched training, and retained-success comparisons. |

The 2 retained frames are identical no-focus observations. Repeating their analysis does not qualify transitions or independent coverage.
The timing adapter currently replays retained frames. Live policy execution still needs a producer connection and native qualification.
The completion audit does not classify that connection as implemented.

TTR source includes FixturePlaybackSession with a real AVPlayerViewController and a seeded loopback HLS source.
Its source path is TVTestRig/TVTestRigFixture/Views/FixturePlaybackView.swift in the Developer checkout.
This is a reusable capability, not evidence that the player or media source currently runs.
The SDK playback setup document explicitly leaves native auto-hide and timing qualification open.
Use this existing capability before building another playback scene.

The next native step requires the pending corrected NavigationConsumer installation and launch approval.
The requested scope is the intended tvOS Simulator, at most 6 frames, 800 s, and 100 MB.
No settings changes or physical devices are included. Preserve the existing app and source receipts.
After deployment, refresh enrollment and queue the bounded transition comparison through the detached runner.
Use its real event output to finish the prospective timing connection and qualify the remaining scenarios.
Do not infer detector classes from UIButton names or use unknown labels for training.

BigDog-Coordinator stores source handoff request nuiak-sdk529-source-reconcile-20261025-v1 at cursor 1482.
The latest read contains no destination forwarding receipt or Sillycon-TTR acceptance.
Preserve the shared source archive until its exact receipt arrives.
No active job is interrupted. Standard and shipped models remain unchanged.

### Approved sample deployment and queued transition comparison

The maintainer approves corrected sample installation and launch, with at most 6 frames, 800 s, and 100 MB.
Maximum-mini-NUIAK installs the source-built NavigationConsumer on the intended tvOS Simulator.
A setup wrapper fails while reading an empty startup log. The sample launch itself succeeds.
After verifying that launch, the wrapper relaunches the sample with recoverable private enrollment. No capture repeats.
The fresh authenticated snapshot reports native no-focus, 4 retained events, and zero dropped events.
This confirms the registration correction avoids the previous immediate event flood at this observation.
It does not qualify transitions or model accuracy.

The existing capture adapter now supports a fixed arrival/departure sequence.
It uses 3 frames and 2 playPause inputs within the sample app.
Each input requires fresh native observations. Uncertain input outcomes stop without retry.
The adapter preserves partial frames, records input intent before dispatch, and closes its own remote session.
Missing event history rejects temporal qualification while retaining captured evidence.
Four new sequence cases pass. The test command also runs 9 inherited capture contract checks.
The focused suite contains 13 distinct checks.

Job sdk529-native-arrival-departure-r3 is submitted and approved. Fresh-process readiness reports ready with no blockers.
The detached service remains active but has not started an attempt at the dispatch check.
Service dispatch diagnosis remains open. No service restart occurs in this step.
Evidence: reports/work/SDK529/sequence-tests.log, sequence-spec-r3.json, and sequence-admission-r3.json.
Native deployment evidence is in Developer/TVTestRig/.local-work/sdk529-native-r3/activation.json.
Standard, submitted specifications, and prior results remain unchanged.

The active service rejects the exact approved specification with sdk_capture_identity.
Fresh-process validation and readiness pass for the same specification.
The service retains the old adapter in memory. A single idle restart now awaits separate approval.
The request does not cancel jobs or change submitted specifications.
Evidence: reports/work/SDK529/sequence-service-admission-r3.json.

### Approved restart and verified dispatch

The maintainer approves 1 idle dashboard restart. The qualified restart tool completes without cancelling a job.
The new service process is 52283. It resumes the existing queue and priority settings.
The first sequence attempt fails before capture because the sample's 30-minute SDK listener has expired.
The retained response reports live_evidence_unavailable. No image or input intent exists in that attempt.
The adapter reports sdk_sequence_identity because the unavailable response contains no authenticated identity.
Preserve that failure; it is not a model failure or a capture result.

The approved sample session is relaunched with fresh enrollment.
Immutable successor sdk529-native-arrival-departure-r4 receives the remaining 795 s and 99,970,300 bytes.
The original failed attempt consumes 5 rounded seconds and 29,700 output bytes.
The cumulative scope remains at most 6 frames, 800 s, and 100 MB. This successor plans 3 frames and 2 inputs.
The background runner starts the successor. The dispatch snapshot reports running with no runner error.
No native comparison result is available at this handoff. No repeated job polling follows.
Standard and previous results remain unchanged.
Evidence: sequence-idle-restart.log, sequence-budget-r4.json, sequence-admission-r4.json, and sequence-dispatch-r4.json under reports/work/SDK529.

### Strategy correction after disabled-focus persistence

The native trial retains left focus after both controls become disabled. The original no-focus expectation is unsupported.
The adapter now captures unexpected endpoints and reports supported, contradicted, or inconclusive separately from execution status.
All 14 focused tests pass. Successor sdk529-native-observed-focus-r5 is approved within the remaining original budget.
See [the evidence, Apple references, and revised strategy](SDK529FocusStateStrategy.md).
This change does not qualify native departure, visual labels, or a model replacement.

The corrected comparison completes in 31.978 s with verified output hashes.
It retains a full 11-event native history and reports arrival followed by unchanged focus.
The final focused control is disabled. The departure hypothesis is contradicted; its image label stays unknown.
The remote session closes successfully. The runner remains healthy and becomes idle.
No model, profile, data role, or previous success changes.
