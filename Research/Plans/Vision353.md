# VISION353 — Vision capability investigations

> Historical research record. Results retain their stated scope and limits.
> Host names are public aliases. Local evidence and execution records remain private.
> This publication does not revalidate earlier results or approve a model.

Priority: P3, below focus repairs and qualified HCF comparisons.
Owner: research-host-NUIAK. Tasks.md owns the backlog and execution state.
The user approves preparing and running these investigations through the queue.
The [first execution report](../Vision353Results.md) records 10 completed jobs on retained captures.
Capture, training, and navigation remain outside this Vision batch.

## Goal

Find when Apple Vision tools help NUIAK and TTR, when they fail, and when combining them increases errors.
Test navigation evidence through recorded replay. Do not give these tools authority to send remote commands.
Report measured benefits, limits, and costs. Do not assume agreement between tools means correctness.

## What exists

- `FrameSimilarity.swift` uses image feature prints. Its request currently uses the default revision.
- `NativeUIDetectionRequest.recognizeText` uses accurate OCR, language correction, and English language settings.
- `TextAnchorVerifier` and `ObservationMerger` already provide text and geometry integration points.
- `vision_annotation_probe.swift` and `derive_frame_similarity_threshold.swift` provide existing diagnostic entrypoints.
- `VisionAnnotationComparison.md` and `AccessibilityTracking30.md` contain earlier rectangle and tracking investigations.

Reuse these implementations and compatible retained outputs. Do not repeat their completed comparisons without a new question.
Confirm the actual detector path first. A Vision wrapper and direct Core ML inference can use different preprocessing.
GENERATION352 already supplies the producer-job pattern for missing controlled inputs.
Its failed 160 px capture remains incomplete. Do not treat its partial output as a complete dataset.

## Temperature and settings

The reviewed Vision request APIs do not expose a general sampling-temperature setting.
Do not invent one or treat confidence thresholds as temperature.
OCR exposes recognition level, languages, language correction, custom words, and minimum text height.
Feature prints expose request revision and crop settings. Their distances are not class probabilities.
Tracking exposes tracking level. Rectangle detection exposes geometric constraints and observation limits.
Optical flow exposes computation accuracy. Test availability against the installed SDK and runtime before registering jobs.

Temperature scaling is different: it rescales model logits before probabilities are calculated.
For a binary classifier, the usual form is `sigmoid(logit / T)`, with `T > 0`.
A shared positive temperature preserves multiclass rankings and binary decisions at 0.5.
It can change decisions at other confidence thresholds. It cannot recover missing features or fix localization.
Run this test only where valid logits and separate calibration groups exist.
Do not interpret opaque OCR confidence or feature distance as logits.
If logits are unavailable, report the test as unsupported rather than add a guessed temperature parameter.

## Experiments

All rows use the shared acceptance checks below. Each row names its additional readiness requirement.
Batch A establishes settings and failure limits. Batch B tests temporal evidence. Batch C tests combinations and cost.

| ID | Controlled test | Measurements and decision | Required before execution |
| --- | --- | --- | --- |
| A1 | Inventory used requests, supported revisions, defaults, and available settings. Check a tiny retained input through each supported request. | Record supported, unavailable, and failed requests separately. Select exact settings for later jobs. | Installed SDK inspection and a tested queue adapter. No installation. |
| A2 | Compare whole-frame feature distances with existing pixel and focus-change scores on identical pairs. | Report missed focus movements and nuisance alarms at every frozen operating point. Decide whether similarity can safely skip later analysis. | Qualified pair labels and A1. Reuse DATASET351 endpoints. |
| A3 | Compare OCR fast/accurate modes, then correction on/off with recognition level fixed. | Report text errors, missing labels, wrong text associations, and latency. Choose settings by control size and text type. | Reviewed text and boxes. Include titles, numbers, and repeated labels. |
| A4 | Compare rectangle proposals with existing detector proposals and their union. Use 2 fixed geometric presets. | Measure body-box recall, duplicate proposals, and downstream wrong selections. Decide whether rectangles add useful candidates. | Complete control labels and A1. Preserve earlier rectangle comparisons as controls. |
| A5 | Compare full-frame OCR with the existing region-of-interest path and minimum-height settings. | Measure small-label recall, coordinate errors, and time saved. Reject speed gains that lose retained small labels. | Reviewed small text, edge positions, and conversion fixtures. |
| B1 | Compare feature-print revisions and repeated identical inputs within each supported backend. | Measure distance drift, decision changes, cold/warm time, and repeatability. Decide whether caches require revision-specific separation. | A1 and available resident backends. Never compare incompatible prints directly. |
| B2 | Compare tracking levels on recorded focus movement, identical neighbors, and occlusion. | Count identity switches, lost tracks, box error, and recovery delay. Decide when tracking needs fresh detection. | Qualified ordered sequences and initial boxes. Keep label-supplied boxes separate from deployable proposals. |
| B3 | Compare unchanged frames with translation-aligned frames during scrolling and focus growth. | Measure alignment error and focus evidence removed by alignment. Decide whether registration helps or hides the target change. | Known motion controls plus native sequences. Do not claim global translation models all UI motion. |
| B4 | Compare optical-flow accuracy settings with existing pixel differences on scroll, growth, and animated backgrounds. | Measure motion separation, nuisance responses, memory, and latency. Reject costly settings without a measured benefit. | Same-size qualified frames, A1, and one request at a time. |
| B5 | Replay missing, repeated, delayed, and out-of-order frames through existing similarity and text caches. | Count false stable decisions, stale labels, and recovery steps. Require explicit invalidation on stale or mismatched input. | Timestamped replay fixtures and caller tests. This is a software test, not model accuracy. |
| C1 | Compare detector-only output with detector plus OCR through the existing merger. | Count corrected and newly wrong control identities, unmatched text, and duplicate-label failures. Decide which associations help. | A3/A4 and reviewed text-to-control associations. |
| C2 | Compare the current transition model with fixed combinations of similarity, OCR, tracking, and model evidence. | Report missed movement, false change, abstentions, and errors among emitted stable decisions. Decide when disagreement requires abstention. | Compatible outputs from A2/B2/C1. Freeze at most 3 rules on development groups before separate review. |
| C3 | Fit one temperature against an unchanged-logit baseline on separate calibration groups. | Report negative log loss, Brier score, reliability bins, coverage, and false-stable risk. Decide whether confidence becomes more useful. | Valid logits, qualified labels, and approved calibration membership. No reused final audit groups. |
| C4 | Compare always-running tools with a frozen staged pipeline on recorded navigation episodes. | Measure missed events, actual requests avoided, end-to-end latency, and false readiness. Decide whether conditional execution earns its complexity. | C2 and complete episode labels. Include native boundaries, overlays, and no-movement actions. |
| C5 | Compare supported compute configurations and image orientations using the unchanged production preprocessing. | Measure decision differences, box alignment, memory, and cold/warm latency. Document runtime limits for TTR. | A1, pinned models, and available Apple hardware. Do not claim ANE use without execution evidence. |

## Inputs and labels

Start with retained development captures. Reuse input decoding and predictions where identities match.
Keep procedural images, native Fixture captures, real-app Simulator captures, and physical captures separate.
Retained Office material stays local and keeps its current data role. Unreviewed pairs support observations, not accuracy claims.
DATASET351 has focus labels but does not automatically have reviewed text or object-tracking labels.
HCF comparisons depend on HCF350 delivery and validation. Their absence does not block ordinary-profile investigations.

If coverage is missing, add a generation producer with exact recipes, target, counts, and output requirements.
Consumers depend on verified producer completion. They do not start from partial captures.
Do not duplicate the remote HCF pilot or change OS settings through this plan.

## Queue preparation and budgets

These are backlog tasks, not executable jobs yet. Do not register fake scorers to increase the ready count.
For each batch, prepare 5 immutable specifications through the existing queue.
Each specification names input hashes, labels, source revisions, model hashes, settings, expected outputs, and its decision rule.
Add exact producer dependencies where needed. Mark unsupported combinations explicitly.
The runner owns execution. The chat defines tasks and reviews completed batches.

Limit each diagnostic job to 800 s and 100 MB. Store bulk inputs under the verified storage policy.
Run Apple Vision requests on an available Mac. Serialize optical-flow requests and bound decoded image memory.
worker-host-NUIAK can summarize exported numeric results after a complete assignment. It cannot qualify Apple's runtime.
Stop failed jobs without automatic retries. Do not download models or dependencies for this backlog.

## Shared acceptance and reporting

- Preserve source images, original model crops, settings, and raw observations.
- Keep related scenes, repeated frames, derivatives, and reversed pairs in the same group.
- Separate development, calibration, and final audit groups before fitting any setting.
- Report all 7 archetypes and 3 themes. Mark unsupported cells instead of substituting data.
- Report support by size, position, effect type, HCF mode, and source domain where labels permit it.
- Separate focus selection, focus change, localization, OCR, tracking, and settling metrics.
- Report counts, abstentions, coverage, previous successes lost, and new successes gained.
- Report group counts. Use paired group comparisons without treating related frames as independent evidence.
- Measure cold and warm latency, decoding cost, memory, and total job time.
- Mark unavailable metrics as unavailable. Do not call replay agreement accuracy.

A setting advances only when its intended metric improves without losing retained required successes.
An unchanged class decision after temperature scaling is expected, not a failed implementation.
Inconclusive support produces a coverage request, not a deployment recommendation.
These experiments do not change production thresholds, weights, navigation policy, or promotion gates.

Test coordinate conversion, empty observations, unsupported revisions, stale frames, missing labels, and changed hashes before dispatch.
Test calibration leakage and non-finite logits before C3. Test cache invalidation and disagreement paths before C2/C4.
Reuse existing report contracts and queue tests. Run integrated Swift checks once after code integration, not for this planning edit.

## TTR feedback

Send one compact result per completed batch when it changes TTR's next action.
Include the tool, exact settings, supported conditions, failure counts, runtime cost, and reproduction IDs.
Recommend use, limited use, or no use for the tested condition. Distinguish replay evidence from live qualification.
Do not send Office images or general raw captures through chat.
TTR retains navigation policy. Peer suggestions do not start new assignments without human approval.

## Sources checked

These sources describe APIs and methods, not measured NUIAK gains.

- [Apple OCR request](https://developer.apple.com/documentation/vision/vnrecognizetextrequest): settings and supported languages.
- [Apple Core ML request](https://developer.apple.com/documentation/vision/vncoremlrequest): model wrapper and image scaling.
- [Apple feature prints](https://developer.apple.com/documentation/vision/vngenerateimagefeatureprintrequest): image representations and request configuration.
- [Apple tracking sample](https://developer.apple.com/documentation/vision/tracking-multiple-objects-or-rectangles-in-video): initial observations and tracking levels.
- [Apple image registration](https://developer.apple.com/documentation/vision/vntranslationalimageregistrationrequest): translation alignment.
- [Apple optical flow](https://developer.apple.com/documentation/vision/vngenerateopticalflowrequest): motion vectors, accuracy settings, and resource limits.
- [Guo et al., 2017](https://proceedings.mlr.press/v70/guo17a.html): temperature scaling for confidence calibration.
