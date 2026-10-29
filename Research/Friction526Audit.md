# FRICTION526 — Remove avoidable capture and preparation restrictions

October 25, 2026. Owner: Maximum-mini-NUIAK.

## Decision

The maintainer removes the blanket prohibition on repeated captures.
Use bounded Simulator captures when they supply missing evidence for an approved experiment.
Preserve originals and evaluation exclusions. Reconcile uncertain operations before retrying.
The background runner continues to own execution.

## Completed correction

The SDK preparation adapter now accepts a selected product list.
Use `products: ["crops"]` for single-frame crops. Use `["temporal"]` for temporal pairs.
Omitting the field retains both products.
Missing action timing no longer blocks otherwise valid single-frame crops.
Unknown focus profiles, invalid geometry, and split leakage still block crop training.
Aggregate eligibility now reflects eligible output rows, rather than the requested training role alone.

All 30 focused tests pass in 32.131 s.
The tests include two isolated queue campaigns that use the same adapter without new scripts.
Negative tests preserve temporal timing requirements and crop profile requirements.
Evidence: `reports/work/FRICTION526/preparation-tests-r3.log`.
No live capture or training job starts during this audit.

## Rules and implementation audit

| Restriction | Decision | Reason and next action |
|---|---|---|
| Never repeat captures | Remove | Missing historical observations can require a new capture. The maintainer authorizes this correction. |
| Require action timing for crop preparation | Fixed | Single-frame classification does not consume inter-frame timing. Temporal preparation still requires it. |
| Require complete screen labels for registered-control crops | Do not apply | Crop truth needs observed focus and valid registered bounds. Complete detector evaluation needs complete labels. |
| Couple source intake to Simulator qualification | Keep separate | Portable source tests can pass while runtime acquisition remains incomplete. |
| Hardcode campaign successor IDs in queue validation | Replace through a scoped implementation task | Exact approval remains necessary. Campaign names should not require repeated validator edits and service restarts. |
| Require both Standard and HCF in native coverage production | Scope by requested profile | Standard acquisition must not wait for optional HCF coverage. Existing T45 requires both. |
| Require 20 percent free storage in an older capture adapter | Replace with measured storage requirements | This rule is not a present blocker. The verified USB has approximately 1.6 TiB free. |
| Require observed labels and profile evidence | Retain where consumed | Expected focus and contrast settings do not establish actual focus or native Focus Style. |
| Require target ownership and recovery reconciliation | Retain | These checks prevent conflicting actions and duplicate execution after uncertain outcomes. |

The audit does not lower model acceptance criteria or change shipped behavior.
No new service, automatic schedule, or dependency is installed.

## Capture path: exact remaining work

Maximum-mini-TTR reports the intended tvOS Simulator ready, with clear ownership.
The Fixture environment endpoint responds.
These checks do not prove SDK enrollment or native profile acquisition.
No current usable SDK enrollment was found in the inspected local setup.

The source provides `aatv sdk packet` and a native NavigationConsumer example.
A complete queue producer must connect enrollment, native observations, profile evidence, and packet export.
The existing session-reuse adapter has campaign-specific identifiers and validation-only roles.
It cannot be treated as a general training-data producer without qualification.

Start with one layout and at most 2 frames, within 800 s and 100 MB.
Use observed focus, visible bounds, profile evidence, and original group exclusions.
Require action timing only if the requested product includes temporal pairs.
Qualify this small acquisition before expanding to the requested training groups.
A source rebuild can supply missing executable code. It cannot reconstruct absent historical observations.

Coordinator message 1464 records the changed capture authority and requests the supported acquisition entrypoint.
It requests routing to Sillycon-TTR. Storage is confirmed; forwarding is not yet confirmed.
It explicitly prevents a remote duplicate while Maximum-mini-NUIAK prepares local execution.
Sillycon-TTR host recovery problems do not make Maximum-mini-TTR unavailable.

## Independent detector result

The matched SDK525 comparison recovers 3 registered controls without losing any of 112 previous detections.
Coverage changes from 112/120 to 115/120.
Proposal count changes from 329 to 375.
These are development geometry results, not full-screen focus accuracy or a promoted model.
Evidence: `reports/work/FRICTION526/geometry-result.json` and the verified SDK525 report receipt.

Next compare focus decisions on the two sets of retained proposals with identical crop weights.
Measure correct selections, abstentions, lost successes, and new wrong selections.
The existing T57 adapter assumes older 3840 by 2160 capture records and cannot consume these SDK packets directly.
Extend the existing SDK endpoint adapter for pinned proposal inputs instead of recapturing these frames.
This follow-up is an implementation task, not an admitted experiment.

## Completion boundary

The policy correction and preparation adapter are implemented and tested.
The 48 retained pairs still lack observed profile evidence. None becomes training data through this change.
No new live jobs are admitted by this audit. The queue is not reported as unblocked.
Next delivery requires the bounded SDK acquisition and the retained-proposal focus comparison.
Preserve Standard, previous successes, and all original evidence.
