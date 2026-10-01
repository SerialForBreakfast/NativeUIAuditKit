# ADR-0015: Context-Aware and Unified tvOS Focus Detection Architecture

- Date: 2026-09-30
- Status: Proposed comparative experiments; FDR021 baseline retained.
- Contract: [Local-first delivery tranches 3–5](Plans/LocalFirstDelivery.md).

## Corrected evidence

FDR021 uses frozen MobileNetV3-small features and a 577-parameter head with
986 training, 315 development and 18 retention crops. It achieves 12/14 unique-
correct complete frames, 16/27 positive hits, 3/288 false positives and 18/18
retention classifications. Artwork remains weak at 2/12 positive hits.
[Execution evidence](../reports/work/FOCUS-REVIEW-CONTINUE-16/execution-handoff.md).

Not all earlier FDR runs used this probe. The encoder is nonlinear; insufficient
focus representation is a hypothesis, not a mathematical consequence of a linear
head. The small repeatedly inspected development set limits generalization claims.

Alpha/straight-RGB repair corrected a genuine deployment error (maximum score
difference 0.418649). Production parity now passes 333/333 crops, maximum error
about 0.0000341, with no tested threshold flips. Keep automated parity.
[Evidence](../reports/work/FDR021-PIXEL-PARITY/handoff.md).

## Experiment direction

1. Build coverage-driven data before repeating unchanged training. Include buttons,
   tabs, artwork, rows and supported keyboard controls, selected-but-unfocused
   parents, hard negatives and visible competitors. A proposed 5,000+ pair collection
   target does not replace existing production coverage/independence requirements.
2. Native labels require observed focus and frame-correlated actual geometry,
   settling and duplicate checks. Review recipes and exceptions; metadata variation
   does not prove pixel diversity.
3. Group sources/layouts before splitting and generation. Preserve real development/
   retention data and untouched tests. Failure-mined development cannot silently
   become training or untouched challenge data.
4. In separately approved runs, compare improved data with the current representation
   first; then isolate context changes and upper-backbone fine-tuning. Do not change
   data, crop, optimizer and backbone simultaneously and attribute improvement to one.
5. Production stays at 16% expansion and 256×256. A 35% or dual-stream arm needs
   versioned preprocessing and export compatibility tests. Wider context may help
   neighbors/shadows but reduce target detail at fixed resolution.
6. Predefine improvement and retention criteria; report full-frame wrong/no/multiple
   focus, misses/FP, stratum support, timing and memory. No automatic failed-run sweep.

## Deferred unified detector

A joint focus attribute could remove crop-stage errors but needs the same full-screen
comparison. Do not double public classes speculatively. A 1080p source is letterboxed
to model input; global field of view does not guarantee subtle cue preservation.
Halved compute, lower latency and better generalization are not established.

## Delivery boundary

Retain FDR021 and shipped weights. A new selected candidate needs production CoreML
parity, explicit artifact selection/rollback and TTR loaded-identity proof before
observer testing. Promotion and autonomous navigation remain separate. No capture
or training is authorized by this ADR or a corpus-size target.
