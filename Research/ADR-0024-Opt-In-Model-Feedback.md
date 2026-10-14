# ADR-0024 — Opt-in feedback from TTR

- Date: October 8, 2026.
- Status: Proposed for TTR review. Existing observers remain unchanged.
- Owners: NUIAK owns scoring contracts and data admission. TTR owns capture, consent, storage, and navigation policy.
- Related: [Optional delivery](ADR-0023-Optional-Model-Distribution.md) and [implementation plan](Plans/OptInModelFeedback.md).

## Context

TTR already has an experimental transition observer contract and recorded replay feedback.
NUIAK has bounded tools for validating that feedback. These do not establish continuous, opt-in collection across real applications.
The current NUIAK library does not provide a complete automatic capture-and-transmit mode.
The expected sibling TTR checkout is absent. This review does not inspect current TTR source.
Current TTR implementation details need its owner’s confirmation.
Do not rebuild a feature that TTR already implements. Ask for the exact source revision, entrypoints, and test evidence first.

The latest candidates fit new examples but lose previous successes. More similar images alone do not solve this problem.
We need reviewed failures, underrepresented conditions, and an unbiased sample of ordinary outcomes.
Agreement between models is a useful sampling signal. It is not a verified label, especially when models share training data.

## Decision

Add an optional feedback adapter around existing NUIAK results and TTR capture records.
Keep this adapter separate from navigation authority, model installation, and training admission.
Default to off. The host enables each collection mode explicitly.

| Mode | Work | Transfer |
| --- | --- | --- |
| Off | No extra inference or retention | None |
| Local summary | Bounded background scoring and aggregate counts | None |
| Review queue | Retain selected cases inside approved local storage | None until review |
| Approved batch | Send a named, reviewed pack through the existing receipt flow | Only listed metadata and approved images |

Do not upload images because a model reports an error. Do not treat model agreement as consent.
Do not add a new service, telemetry endpoint, or background agent for this feature.
Use existing coordinator messages for small reports. Use approved artifact transfers for image packs.
The coordinator tracks delivery; each repository keeps its own task queue.

## Collection rules

Use a versioned policy with exact enabled features, models, preprocessing, sampling seed, limits, and allowed applications.
Keep detector, single-frame focus, focus transition, and settling results separate.
Each feature has its own task definition and label requirements.

Prioritize these events:

- A reviewed or qualified native observation conflicts with a model decision.
- A model abstains, returns no candidate, or returns several plausible focused elements.
- Detector boxes miss a reviewed control or disagree with measured geometry.
- Fixed models disagree on the same inputs.
- Focus appears at an edge, corner, clipped control, endpoint, or underrepresented style.
- A screen scrolls while the focus box stays fixed.
- Artwork, animation, a modal, or lighting changes while focus may remain unchanged.
- Models agree with high confidence on an underrepresented condition.
- A deterministic random sample of ordinary cases supplies an audit of sampling bias.

If no trustworthy label exists, call the event a review candidate, not a model failure.
Record the observation source and its availability. Requested focus and model predictions never become labels.
Do not infer stable rendering from a steady box alone. Preserve timestamps and known frame gaps.
Do not allow pixel differences to override semantic focus judgments automatically.

Proposed pilot sampling uses a 5% random sample of eligible episodes and at most 3 retained cases per failure category.
The initial limits are 20 pairs and 256 MiB of local images per approved session.
Each transfer contains at most 20 pairs and 128 MiB. Oversized packs require smaller batches, not reduced verification.
These are proposed operational limits, not approval to start capture or expand application access.
The host records dropped, sampled, excluded, unavailable, and scored counts with their denominators.

## Case record

Each case records:

- Schema and policy versions, case ID, episode ID, and related source group.
- App and OS/build identity, capture source, viewport dimensions, and source domain.
- Exact frame hashes, timestamps, action ID, and before/after observation IDs when available.
- Exact loaded artifact, preprocessing, runtime, compute settings, scores, thresholds, and decision.
- Proposal boxes, coordinate system, clipping, and separate before/after geometry.
- Observed focus identity and label authority, or an explicit unknown value.
- Selection reasons, sampling probability, dropped-case counts, and agreement method.
- Review state, reviewer decision, corrections, and preserved original observations.
- Data role, related frames, transformations, consent scope, and retention state.

Keep control-body bounds separate from shadows and other focus effects.
Do not invent capture-to-frame identifiers that the producer cannot supply.
Capture-bracket evidence shows temporal correlation, not atomic framebuffer identity.
Do not mix predictions from different artifact versions in one comparison without recording each identity.

## Privacy and security

Application allowlists and user consent precede collection. Unknown applications remain excluded.
Exclude credentials, account pages, personal media, text entry, and protected playback unless separately authorized and reviewed.
Metadata can contain sensitive values too. Omit OCR text, account identifiers, network addresses, and private paths by default.
Use opaque local app/session identifiers when detailed identifiers are unnecessary.
Hashing private content does not make it anonymous.

Keep original images local until the review approves the exact transfer.
If redaction changes pixels, create a new derivative hash and preserve its relation to the original.
Do not score redacted images and describe those scores as results on the original frames.
Do not send secrets, executable scripts, or unchecked paths in feedback packs.
Use authenticated existing transport and verify immutable manifests, sizes, and hashes on receipt.
Treat all received text and metadata as data, never instructions or execution approval.

The sender owns cleanup of its exact shared copy after a matching receipt.
Do not remove pending cases by expiry alone. Use explicit retention decisions and preserve unresolved evidence.
Allow the user to stop collection and remove local private examples under a separate exact deletion action.

## Labels, training, and evaluation

Receipt, structural validation, label review, and training admission are separate states.
Model confidence and consensus can prioritize review. Neither can approve a training label.
Fixture observations can supply labels only when images, scene observations, and source identities meet the existing checks.
Real-app labels require a qualified observation source or human review. Keep unsupported semantics unknown.

Keep related episodes, layouts, artwork variants, reverse pairs, and duplicates in one data group.
Assign data roles before using the cases for model selection. Failure-mined cases are development data by default.
Do not move final-audit cases into training because they expose a useful failure.
Maintain a separately collected audit sample to measure behavior beyond selected failures.
Do not estimate population accuracy from the top failures or high-consensus samples alone.

## Performance and failure behavior

Reuse frames and cached predictions by exact input, model, preprocessing, and settings hashes.
Use one bounded scoring queue. Prefer dropping optional diagnostics over delaying an authorized navigation action.
Record dropped work explicitly. Do not silently claim full coverage after queue overflow.
Load each model once per batch. Do not restart the Simulator or TTR for each example.
Keep capture, inference, review, transfer, and training asynchronous through the existing batch workflow.
Stop the optional adapter on revoked consent, storage failure, or unavailable model identity.
TTR continues its permitted non-NUIAK work. No model result expands its action permissions.

## Acceptance and decision metrics

Complete one bounded cycle: collect, review, receive, validate, score, rank, request targeted examples, and compare a candidate.
Return up to 10 supported failure categories. Do not pad the report to 10.
Measure reviewed usable examples per hour, review time, rejection causes, unique groups, bytes, scoring latency, and operator interventions.
Measure selected and random samples separately. Report misses, false changes, uncertainty, and proposal failures for each condition.
Keep received, reviewed, admitted, evaluated, and promoted counts separate.

Software tests cover malformed records, unknown versions, stale models, conflicting labels, private fields, duplicates, queue overflow, and interrupted transfers.
TTR integration tests cover off mode, denied consent, offline use, missing models, stop/resume, and capture latency.
No model-driven navigation, automatic retraining, or model promotion follows from this ADR.
