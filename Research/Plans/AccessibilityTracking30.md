# Accessibility intake and Settings tracking diagnosis30

Assigned October2,2026. Continue review29/Settings25; preserve their original outputs.

## Producer evidence

Receive only the published sanitized NAV-VERIFY/ACC-MAP report,13271bytes,
SHA2560830baabd5f6faf664ee7795418869b333803f451774aa16b7d686c5c7b2e874.
Ordinary/assisted private pixels were not published. Use the existing recorded
inventory; no recapture or inference from a High Contrast profile comparison to
ordinary focus ground truth. Grouped review and FDR036 scoring require qualified
ordinary artwork/reference evidence, human uncertainty resolution and data-use scope.

## Fixed diagnostic comparisons

Hypothesis: Vision's coarse correspondence can overlap the right row yet misalign
pixels enough to destroy the fixed focus/stability rule. Test the same five recorded
Settings pairs/50controls/48scorable from25, with two screen changes still excluded.
Preserve OpenCV and Vision saved predictions as baselines and verify input hashes.

1. Replay saved Vision windows through unchanged production cropping and fixed rule.
2. Round only Vision dx/dy to the nearest source pixel, preserving before bounds,
   scale, missing-tracking outcomes and every guard. This tests subpixel jitter;
   never select between rounded/raw predictions using truth.
3. Diagnostic oracle: translate the before-sized window to the independently
   reviewed after-body center. Explicitly uses annotation geometry and cannot be
   deployed or reported as model quality; missing semantic correspondence abstains.
   Human box precision limits interpretation. Focus labels enter scoring only.

Report pixel displacement, correct/wrong/abstained, threshold failures and separate
tracking-unavailable/wrong-target/rule-abstention counts. Reuse14retained generated
stress cases with known translations; preserve duplicate identity ambiguity and
outline/content-change negatives. Generate a local Markdown crop gallery for review.
No threshold search, learning, new model or split change. Bound each retained/stress
pass to300seconds,100controls and256MiBnew outputs; total diagnostic budget900seconds.
Explicit output/cache/temp paths are project-local. Existing production cropper
and resident Python environment; existing Swift arithmetic, no fresh Vision tracking
necessary. Run focused tests plus final offline Swift build/test at integrated handoff.

## Completion

Deliver exact producer diagnosis/receipt, evidence eligibility gap, all three
comparisons with provenance and actual caller tests, recommendation in ADR0018,
and one handoff. Independent work completes even if producer pixels stay unavailable.

## Existing-image follow-up within reference qualification

The action-linked audit is not exhaustive of still-image reference opportunities.
Inspection found reviewed Home001/002Photos/Music counterparts. Prepare exact
existing boxes/pixels and20%production windows together; measure every neighbor
intersection before eligibility. Human pair/data-use confirmation remains pending.
Both windows contain the changing adjacent icon, so record difficult-case candidates
separately from clean references. No label regeneration, automatic admission or
model invocation follows from this preparation. Metadata and four crops remain local.
