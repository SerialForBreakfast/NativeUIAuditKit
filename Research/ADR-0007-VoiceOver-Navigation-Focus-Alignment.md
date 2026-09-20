# ADR-0007: Separate visual focus detection from VoiceOver/navigation alignment

**Status:** Accepted design; implementation and capture remain separately assigned.  
**Date:** 2026-09-19  
**Decision owners:** NativeUIAuditKit maintainer

## Context

tvOS exposes more than one meaningful focus concept. Directional remote navigation
can visibly focus one element, while VoiceOver may be reading or exploring another.
That difference can be intentional—for example, during exploration—or it can reveal
an accessibility/navigation defect. A screenshot alone cannot reliably disclose the
active accessibility cursor, the interaction mode, or whether a difference is expected.

The shipped `FocusRingDetector` is a Stage 2 binary crop classifier. Its only job is
to score whether a visible focus treatment appears around a YOLO candidate. It already
includes VoiceOver high-contrast outline appearance in the broader tvOS visual corpus,
but it does not decide semantic accessibility alignment. Treating every visually absent
ring or every VoiceOver caption as an error would create false accessibility findings.

## Decision

Keep one visual focus model. Add a separate, metadata-backed focus-alignment policy.

1. `FocusRingDetector` continues to answer only: **does this candidate crop visibly
   carry the directional or VoiceOver focus treatment?** Its 16%-expanded, 256×256 crop
   contract remains unchanged.
2. Fixture and eventual live-capture metadata must represent two distinct targets when
   known: `navigationFocusElementID` and `voiceOverFocusElementID`. Neither may be
   inferred from pixels or a speech caption.
3. Every alignment example records an explicit `interactionMode`:
   `directionalNavigation`, `voiceOverExploration`, `voiceOverTraversal`, or `unknown`.
   It also records an expected relation: `aligned`, `expectedDecoupled`,
   `unexpectedMismatch`, or `notAssessable`.
4. The policy reports an accessibility mismatch only when source-backed metadata says
   `unexpectedMismatch`. `unknown` and `notAssessable` abstain; a visible ring score
   alone never proves an accessibility defect.
5. Exploration and traversal are first-class expected-decoupling scenarios. They are
   useful synthetic data only when the fixture explicitly supplies both targets and
   mode. The fact that a caption names a different item is not enough evidence.

## Synthetic fixture data

Use deterministic fixtures with at least two simultaneously visible focusable elements.
For each frame, retain a stable screen/seed ID, element IDs/bounds, visual-focus target,
VoiceOver target, interaction mode, expected relation, theme, and accessibility visual
style. Derive, but do not substitute for identity, the normalized center distance and
topological relationship between targets.

The required matrix includes:

| Case | Visual navigation target | VoiceOver target | Expected relation | Use |
|---|---|---|---|---|
| Normal directional navigation | A | A | `aligned` | Positive alignment control |
| VoiceOver exploration | A | B | `expectedDecoupled` | Expected mismatch; must not alert |
| VoiceOver traversal | A or no visual ring, source-defined | B | `expectedDecoupled` or `aligned` | Mode-specific control |
| Intentional fixture fault | A | B | `unexpectedMismatch` | Policy-positive defect case |
| Missing producer state | optional visual A | unknown | `notAssessable` | Abstention control |

For visual-model training, crop labels still describe only visual focus. A non-ring
VoiceOver target is a useful hard negative for the crop classifier, but its semantic
mismatch label belongs solely to the alignment-policy evaluation set. Split by scene
family, theme, mode, and target relationship so near-identical A/B pairs cannot leak
between training and held-out evaluation.

## Consequences

- No new CoreML model, taxonomy class, or public API is introduced by this decision.
- A future alignment rule consumes trusted fixture/live metadata plus the existing visual
  observation; it is not a replacement for the accessibility tree or XCTest assertions.
- The current FocusRing v0.1 model is unchanged. FOCUS-DET-05 must retain its existing
  pair/theme/hard-negative gates and add this matrix only through a separately assigned
  fixture/capture and policy implementation packet.
- Live TVTestRig evidence remains separately qualified. Synthetic fixture success proves
  software/data-contract behavior, not live VoiceOver behavior on hardware.

## Rejected alternatives

**Train a separate mismatch classifier from screenshots.** Rejected because screenshots
do not establish the hidden VoiceOver target or whether decoupling is expected.

**Teach the FocusRing model that every VoiceOver target is visually focused.** Rejected
because it conflates a visual crop label with accessibility semantics and would create
false positives during exploration.

**Flag every unequal target pair.** Rejected because exploration and traversal can make
that relationship intentional.

## Implementation prerequisites

Before capture or policy implementation, define the versioned fixture metadata envelope,
its producer authority, and deterministic contract tests for all five matrix rows. Any
mode/preferences not explicitly represented by trustworthy producer state remain
`notAssessable`; do not fabricate their labels. No hardware operation, training run, or
model promotion follows from this ADR.
