# ADR-0018 — retain Settings tracking; keep the Swift pixel-rule port

Date: October 2, 2026. Status: experimental recommendation, not runtime promotion.
Scope: SETTINGS-SWIFT-SPIKE-25, bundled with accessibility review29.

## Decision

Keep the current OpenCV tracker for this diagnostic. The new offline Swift pixel
implementation is parity-qualified on this development set; the tested Vision tracker
is not a suitable drop-in replacement. TTR can consider the arithmetic implementation
as an optional future supporting signal, with qualified tracking and ordinary Settings
context supplied separately. No calibrated confidence percentage or navigation authority
is implied by pixel agreement.

## Evidence

Same five reviewed Settings screen pairs, 50 controls, 48 semantically scorable;
two page-change pairs excluded. Only two genuine focus moves. Human after-state and
geometry enter scoring, not tracking. Retained-data result and source/tool pins:
[comparison](../reports/work/SETTINGS-SWIFT-SPIKE-25/retained-host/result.json).

| Pipeline | Correct | Wrong | Undecided /48 |
| --- | ---: | ---: | ---: |
| Existing OpenCV + Python rule | 33 | 0 | 15 |
| Same tracking/crops + Swift rule | 33 | 0 | 15 |
| Vision tracking + Swift rule | 2 | 0 | 46 |

All45matched production-crop arithmetic comparisons make the same decision; maximum
absolute difference in the four stability measurements is3.21e-13. This separates a
correct arithmetic port from a poorer correspondence candidate. Vision has34accepted
tracking outputs, but only32match the semantic target at IoU>=.5, versus45for OpenCV.
Nine Vision controls fail reciprocal/scale checks and seven fail confidence. Of the
remaining scored controls,30are too different to call stable; the four real arrival/
departure controls are unavailable. This candidate's alignment/availability fails
before the brightness rule can help; thresholds were not loosened to improve the score.

The14generated stress cases give12exact expected outcomes for Python and5for Vision.
Python's two remaining outcomes safely abstain instead of the expected unknown.
The Vision candidate also abstains rather than making a wrong focus selection, but
loses valid movement/unchanged detections. Preserve duplicate/content/illumination and
external-outline cases; body-only comparison remains rejected.

Retained replay27.77s; generated replay3.60s. Vision's first measured control67.15ms,
subsequent-control median35.39ms, includes file loading and reciprocal tracking.
These are observed first/subsequent calls, not a controlled cold-cache benchmark.
Driver timings label their stages; Python track/crop and Vision track/crop/rule totals
have different scope, so do not claim a relative pipeline speedup. No performance
optimization is justified while decision coverage regresses this much.

## Implementation and boundaries

### Follow-up30: why Vision fails

[Source-bound diagnosis](../reports/work/ACCESSIBILITY-TRACKING-30/retained-verified/result.json)
replays saved positions rather than rerunning or tuning tracking. Integer displacement
rounding remains2correct/0wrong/46abstained. Translating the unchanged before-sized crop
to the reviewed after-center yields36correct/0wrong/12abstained, including both real
switches. This last arm consumes reviewed geometry: it is an oracle diagnostic, not
an improved deployed detector or independent accuracy claim. Existing OpenCV remains
33/0/15, only three fewer correct decisions.

Among48scorable controls, Vision has15unavailable tracks, one track on the wrong row,
30pixel-rule abstentions and two correct unchanged decisions. Across33tracks with
reviewed matches, median center error is3.11source pixels and maximum69.50. The wrong
row visually follows “AirPlay and Apple Home” after “Notifications” loses focus.
High overlap can still be insufficient alignment for pixel stability. Rounding does
not repair this; the problem is not merely fractional coordinates. Twelve unchanged
controls remain uncertain even with reviewed centers, consistent with the existing
context/scroll diagnosis and annotation precision limits. Reviewed centers are not
exact pixel-registration ground truth.

On14generated cases, raw/rounded tracking each achieve5exact outcomes; controlled
geometry achieves13, with neighbor-only still uncertain. All three make zero wrong
decisive calls; duplicate identity is explicitly withheld from the oracle. Thresholds
are unchanged. Retain OpenCV correspondence and the parity-qualified Swift arithmetic.
A future native matcher should match translation/ambiguity behavior, not tune away
safety checks to rescue VNTrackObjectRequest. Broader qualification needs new moves.

`SettingsProbeTool` is an offline executable, not a public library API. Its measurement
mode accepts exact RGB bytes from the existing production cropper. It implements
edge-growth, central brightness, border illumination, full-crop absolute stability
and four-quadrant highlight checks. Tracking mode uses `VNTrackObjectRequest` revision1,
accurate level, reciprocal checking, confidence>=.55 and scale deviation<=.06;
accepted windows retain the original scale. `settings_swift_spike.py` applies the
existing equal-context support/cropper and scoring contracts. Reports retain hashes,
membership, thresholds, exclusions, timing and unknown outcomes.

This deliberately small diagnostic does not make Vision tracking universally unsuitable.
Future work may investigate registration error or a different tracker, on explicit
counterexamples before threshold changes. Broader deployment also needs more than two
reviewed real focus moves and complete endpoint inventories. High Contrast/assistive
profiles need their own qualification; this Settings rule is not a universal outline
detector. TTR continues to own context, freshness, actions and recovery.
