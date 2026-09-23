# TEMP-FOCUS-DEV — temporal focus localization diagnostic

2026-09-23. NUIAK architect. Assigned development precursor complete for review;
TEMP-LIVE genuine-journey/interruption qualification remains open. Prior iOS and
appearance changes preserved; no capture, new model inference, training or promotion.

| Outcome | Evidence |
|---|---|
| Software verified | Actual replay CLI/TransitionTool;51 combined regression tests and required offline Swift checks |
| Data eligible | Prior reviewed development frames only; no new training or independent evaluation admission |
| Integration qualified | Offline production primitive boundary; no TTR live action integration |
| Model gate passed | Not assessed; no weights changed |

## Frozen experiment and results

Protocol9f7ecc0731564af97d3797ef083c1519285f65fc80cf74ced6a5c9cb6bcd29fb:
three retained appearance families, each with three observed focused frames.
Nine reference arrivals,18 constructed directed focus switches,9 identical-frame
controls. All are source-related development membership, not36 independent samples.
All control boxes are native current-frame oracle proposals. Source/recipe/focus
claims, image hashes, cached scores, candidate completeness and truth binding checked.

Fixed policy before measurements: shipped threshold0.85; production luma noise24;
changed-region bounding-box overlap≥0.01 and lead≥0.10 for a unique diff candidate.
Combined policy intersects eligible model and change candidates; unchanged frames
fall back to the single-frame decision. No diff boxes become element boxes or labels.

| Case kind | Shipped single-frame correct/wrong/abstain | Diff-only correct/wrong/abstain | Shipped+diff correct/wrong/abstain |
|---|---|---|---|
| Reference→focus,9 cases |0/2/7|9/0/0|6/0/3|
| Constructed A→B switch,18 cases |0/4/14|2/2/14|0/1/17|
| Identical-frame control,9 cases |0/2/7|0/0/9|0/2/7|

FDR-007 and008 abstain on every single-frame and combined case at0.85; diff-only
has no model input and therefore its identical results across model rows must not
be counted as additional trials. Their underlying appearance misses remain unresolved.

**Interpretation:** temporal localization can remove persistent bright-art false
candidates on baseline arrivals. It does not yet solve determining which control
gained rather than lost focus. The combined policy reduces some wrong decisions
by abstaining, not by making focus switches correct. Keep single-frame initial
observations and uncertainty; no production integration recommendation yet.

Latency: final36 calls total10,612ms process time,10,172ms primitive time (~283ms/pair),
including image loading and both Vision feature distance/change localization. Not
diff-only kernel timing, end-to-end TTR latency, physical-device latency or cold/warm
model inference. This path would need targeted latency measurement before live use.

## Implementation and verification

- `scripts/temporal_focus_replay.py`: freezes caller policy by exact contract;
  verifies hash-bound prior artifacts, scene membership, complete current candidates,
  native labels and scores. Production measurement through existing TransitionTool.
  Truth joins after each policy decision; no model or image processing replacement.
  New-only report, bounded cases/regions/timeouts, partial failure retention, no retry.
- `scripts/test_temporal_focus_replay.py`: truth independence, old/new ambiguity,
  moving background, no-change fallback, low model scores, invalid/corrupt/missing
  inputs, mismatched native focus, incomplete candidates, output collision and real CLI.
- `prepare.py` froze actual protocol before measuring; result.json retains first run.
  Final result-final.json includes helper-identity check. Both36/36 complete, no errors;
  decisions and summaries identical; final evaluator hash matches source. No policy
  change or threshold tuning between them. Do not rerun model inference for cached scores.
- Restricted integration test failed Vision CVPixelBufferPool creation; preserved
  tests.log. Identical approved host tests pass. Final combined suite51 tests/8.666s
  includes temporal, transition, retention and reconstruction tests.
- Offline Swift build/test run on integrated source; logs retained. No dependency
  downloads, device use or external outputs beyond approved platform runtime caches.

## Next substantial assignment

Use actual ordered Fixture/native journeys with settled before/action/after evidence,
including no-op boundaries, scrolling, animations/background motion and unexpected
context. Bind actual observed previous/current focus and geometry, action identity,
source timestamps and hashes. Do not call these constructed pairs button-press traces.
Compare single-frame, temporal and combined paths with current-frame detector boxes;
retain native oracle boxes only for error attribution. Test whether reliable prior
focus helps distinguish departure/arrival, and measure genuine latency. No new temporal
model until this comparison isolates a learnable gap and training is separately approved.
Native truth scores results; it must not secretly choose the visual arm's target.

All offline assigned criteria complete. Remaining live/model work needs eligible
ordered traces and explicit scope; independent model evaluation groups remain a
different data dependency. Coordination contains only the cross-project findings.
Skills: worker execution/model workflow preserved existing tools, source roles,
change-scoped testing and separate integration/model qualification.
