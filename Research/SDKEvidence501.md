# Use observed UI evidence in experiments

Owner: Maximum-mini-NUIAK. Date: October 24, 2026.

## Implemented connection

`scripts/fixture_evidence501.py` reads retained campaign exports through existing capture validators.
One small request selects case IDs and either the geometry or transition view.
Both views use the same adapter and queue contract. Neither view captures images or trains a model.

The geometry view preserves observed control identity, parent identity, taxonomy, layout bounds, visible body bounds, and artwork presentation.
It preserves the semantic inventory and screenshot hash with each frame.
The transition view reports observed focus changes and measured scroll-offset changes.
Requested transition conditions remain separate from observed changes.

This implementation consumes verified Fixture metadata. It does not establish that the portable SDK exports an equivalent bundle.
Portable SDK delivery still needs exact source and export qualification.

## Current executable requests

| Job | Question | Decision |
|---|---|---|
| `sdk501-geometry` | Which body, artwork, hierarchy, and class fields are available on the retained 4 cases? | Reuse verified fields in detector diagnosis. Request incomplete annotation coverage explicitly. |
| `sdk501-transitions` | Do retained focus identities and native scroll offsets distinguish changed and unchanged focus? | Use observed transition labels for diagnostics. Request missing no-focus and content-motion evidence separately. |

Each job uses the original 8 images and calibration ancestry. Each has an 800 s and 100 MB ceiling.
These are short audits. They do not supply overnight training work or establish model improvement.
The detached runner owns execution. No service restart is needed for this new adapter.

Both jobs complete through the background runner. Their output hashes match their execution receipts.
The 8 frames contain 68 measured body observations, 52 artwork measurements, and 4 clipped bodies.
All 4 pairs have native scroll observations. Two pairs change observed focus.
The entire set shares 1 ancestry group. It does not supply independent cross-app evidence.

## Qualification

Four unit tests pass against retained evidence.
Two configuration-only positive cases pass through the isolated queue.
An invalid case ID fails with `sdk_case_unknown` through the same queue.
Changed receipt hashes, duplicate membership, and unsupported views fail validation.
The isolated runner stops after the expected negative. The second positive then passes in its own dispatch.

The first qualified pair contains 18 element observations and 18 measured bodies across 2 frames.
It contains 14 measured artwork observations and observed unchanged focus and scroll.
These counts describe repeated observations, not independent controls or accuracy.

## Data boundaries

- Preserve calibration roles and original ancestry. Do not admit these captures for training.
- Report annotation completeness as unknown until the producer supplies coverage evidence.
- Require observed focus identity. The current validator does not support an explicit no-focus export yet.
- Do not turn absent telemetry into a no-focus label.
- Do not infer decoration, selection, or brightness from recipe names.
- Keep SDK ground truth out of screenshot-only model inputs.
- Do not equate scroll offsets with arbitrary background-motion measurement.

## Next producer requirements

Use the existing P1 dataset investigation and TTR campaign interface. Do not create another renderer or transport.

1. Detector geometry request: export a list and grid with observed bounds, hierarchy, class mapping, and explicit coverage exclusions.
2. Transition request: export focus movement, unchanged focus, content-only movement, and observed no focus with frame-bound identities.
3. Supply source revision, app and Fixture versions, recipe identity, pixel hashes, coordinate units, and group ancestry.
4. Reject stale frame identity and missing required observations with stable error codes.
5. Preserve partial results and recovery receipts. Resume only unattempted cases within approved budgets.
6. Prove the second request changes configuration only, through the same producer and consumer interface.

Maximum-mini-NUIAK owns intake and experiments. Sillycon-TTR owns proposed SDK additions through BigDog-Coordinator.
Current TTR endpoint refusal blocks new local production. Retained audits remain independent.
The 4 existing session comparisons do not authorize extra dataset captures.

TTR reply 1331 reports dynamic recovery qualification against implementation `ae310e08`.
Its qualification documents remain uncommitted. This is peer evidence, not local NUIAK qualification.
Contract request `nuiak-sdk501-producer-contract-20261024-v1` is stored at coordinator cursor 1332.
Forwarding and acceptance remain unconfirmed. The request asks for existing interfaces before new implementation.
It also corrects the prior IMPORT500 message, whose unsupported status value required coordinator review.

## How findings advance models

Detector experiments compare predicted boxes with observed visible bodies and preserve original class labels.
Hierarchy identifies parent-child relationships for diagnostic slicing. It does not automatically remove child predictions.
Transition experiments compare screenshot-only predictions with observed before-and-after focus.
Ground-truth-assisted comparisons remain diagnostic upper bounds, separate from deployed behavior.

Training follows only after complete labels, training-only groups, and matched retention comparisons are ready.
See [SDK requirements and acceptance checks](TTRSDKTrainingRequirements.md) for the missing producer fields.

## Local evidence

- [Geometry request](../reports/work/SDK501/sdk501-geometry.json)
- [Transition request](../reports/work/SDK501/sdk501-transitions.json)
- [Queue qualification](../reports/work/SDK501/qualification.json)
- [Second-view qualification](../reports/work/SDK501/second-view-qualification.json)
- [Completed audit receipts](../reports/work/SDK501/handoff.json)
