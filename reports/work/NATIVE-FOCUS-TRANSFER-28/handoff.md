# Native focus transfer28 — cue diagnosis and offline caller

October2,2026. Base commit69b507d, clean at entry. User assigned the next substantial
tranche after the successful native-effect experiment.

| Outcome | Evidence |
|---|---|
|Software verified|64Python checks; offline Swift build and134tests; actual advisory CLI|
|Data eligible|Same500synthetic evaluation controls, original split/labels preserved|
|Integration qualified|Offline experimental caller, native crop and model parity; live integration pending|
|Model gate|Real transfer blocked by missing compatible reviewed reference pairs|

## What changed our understanding

Frozen FDR036, identical500controls, fixed0.85threshold:

| Input | Correct | False focused | Missed focused |
|---|---:|---:|---:|
| Original fixed reference window |500|0|0|
| Equal-size body crops |398|0|102|
| Body replaced with midgray; size and outside pixels retained |250|0|250|

Resizing away enlargement loses102focused detections,88on dark backgrounds and14on
light. At0.5it loses64. Hiding interior appearance loses every focused detection at
both thresholds. **The model is sensitive to both scale and body appearance.**
Size/outside pixels alone were insufficient under this artificial mask. We cannot
attribute success specifically to shading: masking is out-of-distribution and also
removes rounded corners; equal-size recropping alters context/resampling too.

The common-input replay matches saved scores within1.03e-8. All cue probes completed
in41.60s. [Exact predictions, input and model hashes](probes/results.json).
Original USB source images/annotations remain unchanged; only12diagnostic thumbnails
and compact results are project-local.

### Negative stress

All250unfocused evaluation examples remain unfocused under the fixed low-score rule
(score<=0.15) after
0.8or1.2global RGB gain. No false focus or uncertain outputs. Runtime1.39s.
246same-configuration/background content-variant pair compositions and250identical
no-ops also remain unfocused. These are constructed negatives using saved scores,
not independently captured actions or proof against scrolling/animation.
[Stress evidence](stress.json).

## Real transfer: precise missing evidence

Recomputed the existing recorded-action audit against immutable human revisions and
all pinned source files:166actions,14timing-ready,7with reviewed endpoints. Those
seven are Settings-row screens, not qualified native-artwork transitions. Native
effect applicability and persistent identity remain unverified. Separately the315
representative static controls have no pairID/sourceElementID. Proximity is not a
substitute for correspondence or an unfocused reference.

[Audited sources and per-action gaps](real-audit.json). This covers the existing
action ledger, not an assertion that no useful image exists anywhere in storage.
Resume real scoring when retained or newly reviewed native-artwork pairs establish
unfocused reference bounds, same-control correspondence and settled context.

## Offline caller delivered

`scripts/native_focus_transfer.py advisory --request <project-local.json> --output <fresh.json>`

Request: image/reference file hashes, reference bounds, size, known-unfocused evidence,
same-screen/correspondence/native-effect/settled/unoccluded/clear-context attestations,
and observation ages<=5s. Unknown prerequisites return unavailable before loading
weights. Inputs outside project/approved USB are rejected; clipping/invalid geometry,
changed hashes and output collisions fail closed. Attribution remains caller-supplied:
this is not authenticated TTR telemetry or automatic reference discovery.

Actual production Swift crop + frozen-prefix/FDR036 execution on the accepted fixture
example returns focused with score1.0. [Request](advisory-example.json),
[actual reply](advisory-result.json). Ages in this example are offline replay-relative,
not a claim that these retained files are currently fresh observations. Scores are
uncalibrated advisory evidence, never navigation permission or a release decision.

## Verification

- [64focused Python tests](python-tests.log): prerequisite rejection before inference,
  nonfinite/stale ages, clipped/invalid bounds, mask support, hash tampering, actual CLI
  unavailable/collision, existing corpus/trainer/runtime checks.
- [Offline Swift build](swift-build-host.log), [134Swift tests](swift-test.log).
  Initial restricted build failed at nested manifest sandbox; scoped host build passed.
- Actual500-example inference replay and accepted-fixture advisory CLI passed.
- Existing model weights unchanged; no new fit or evaluation-based threshold choice.

## Next substantial tranche, in priority order

1. Obtain an inventory of retained real native-artwork transition evidence from TTR,
   then prepare one combined review batch for missing reference/correspondence labels.
   If retained evidence is absent, agree on physical app/target capture scope.
2. Evaluate FDR036 on those pairs, including wrong-reference, no-op, content change,
   scroll and stale-reference cases. Score coverage and wrong decisions separately;
   retain the existing broad detector as the comparison.
3. If real transfer passes, implement reference lifecycle/tracking in the advisory
   consumer and perform a matched CoreML parity/export tranche. Otherwise diagnose
   actual real errors before further synthetic generation or fitting.

Local diagnostics and caller are complete for review. Real transfer/live integration
are the concrete remaining evidence boundary; another unchanged synthetic run does
not resolve it. TTR handoff asks for retained evidence inventory, not a new build.
[Shared publication and request](coordination.md) verified; peer acknowledgment pending.
