# Keyboard focus training and OS evolution

2026-09-29. User requested comprehensive Fixture accommodation, without per-letter
human annotation. Producer requirements/acceptance contract; not a claim of current
implementation or permission for installation, device input, settings changes or training.

## Current evidence

Max Fixture ComponentShowcaseView has Username and Search TextFields and field-level
focus snapshots. This does not establish OS keyboard key identity/geometry exports.
TTR CLI source exposes remote text insert/clear; current Office behavior is untested.
NUIAK has tabItem/otherFocusable review roles, not keyboardKey. Existing ocr_helper
uses hardcoded1920×1080 point output, not complete glyph or control rectangles;
do not reuse it as an annotation geometry authority.

## Two complementary lanes

1. **Instrumented custom keyboard:** Fixture-owned configurable native-focusable
   key controls, deterministic layout/style/content, actual focus callbacks and
   per-state measured bounds. Supplies volume and hard negatives. Label explicitly
   fixture_custom, never native_system merely because it runs on tvOS.
2. **Genuine system keyboard:** Fixture opens a non-sensitive local text/search
   field using supported platform APIs. Discover whether the actual OS exposes key
   IDs, focus and geometry through the available native test/observation path.
   App field focus callbacks do not imply access to OS-owned key focus. If unavailable,
   report unsupported telemetry and retain diagnostics; OCR/intent cannot replace
   native truth. Use small human-reviewed transfer samples, not manually box every key.

Do not block the custom lane on unavailable system telemetry; do not claim system
transfer from the custom lane. Simulator/device outcomes stay separate.

## Coverage matrix and semantics

One proposed focus-only keyboardKey role; character/action is metadata, not a
detector class per letter. Adding the role/schema remains a separate implementation
with compatibility tests, not a silent taxonomy or model-head change.

- Field, keyboard container, individual keys, suggestion candidates and result cards
  are distinct. Use explicit parent/scope metadata where observed. Selected mode/tab
  is not active focus; selected-but-unfocused controls are hard negatives.
- Key identity is stable within a declared layout, separate from displayed text.
  Represent key action (insert, space, delete, shift, mode/language switch, submit,
  dismiss or unknown) separately from Unicode grapheme/string value.
- Cover alphabetic/case, numbers, symbols, space/delete, alternate modes and supported
  languages/scripts/directions. Multi-character labels, combining characters and
  repeated glyphs cannot be identified by OCR string alone.
- Cover sparse/dense layouts, field-to-keyboard/results transitions, boundary no-ops,
  disabled keys, selected-but-unfocused modes, held/repeat inputs and visible
  competitors where supported. Dictation/suggestions are explicit optional strata;
  no microphone, account use or network-backed content is assumed.
- Track theme/contrast/motion/font/locale/runtime combinations as supported, unavailable
  or untested. Never mutate global settings simply to fill the matrix.

Use constrained representative combinations, not a Cartesian explosion. Initial
targets are one alphabetic layout, one numeric/symbol mode, and language/case changes
where supported. Quantities are collection targets, not new qualification thresholds.

## Capture, export and automatic annotation

Freeze expected eligible keys, actual visible membership and exclusion reasons.
Capture each eligible focused state, pair the same key with its unfocused state
while another eligible key is focused. Use each frame's own geometry, not identical
boxes across scaled states. Retain surrounding competitors and original frames.
Keep legacy reference-baseline pairing labeled separately. Missing/clipped/ambiguous
keys are rejected or unavailable, never fabricated or silently dropped.

Require versioned examples before consumer integration: source kind, OS version and
build, runtime/device class, Fixture build, keyboard/layout identity, locale/mode,
recipe/seed/style/asset hashes, observed state and actual geometry, pixel dimensions,
timestamped frame/native brackets, and complete target accounting. Unknown OS-internal
layout IDs remain unknown; do not invent an authenticated identifier from a hash.

Direct text insertion and directional key selection are separate action modes.
Record actual TTR command IDs, down/up/repeat if supported, dispatch/completion,
before/after frames, settle times and observed text changes. An input receipt does
not prove text appeared. No retained state-change evidence means no transition label.
Use approved dummy text only; exclude secrets/autofill/account data. Verify clear
and dismiss behavior without submitting network searches unless separately approved.

OCR proposes text/glyph positions, not native focus or key hit bounds. Use actual
image dimensions and explicit coordinate conversion. Allow one keyboard-region
selection and bulk editable proposals, then reusable dimension/layout-bound presets.
Never reuse a preset across an unknown layout/version without review. Native bounds
take priority when verified; suggestions remain unconfirmed. Human work is initial
layout review, sampled transfer and exceptions—not every character in every image.

## OS evolution and regression

Pin exact OS build with every capture. Maintain a supported-version matrix; new OS,
locale or keyboard mode is unknown until checked, not implicitly covered by native
styling. Preserve old data/expected behavior rather than rewriting labels to match
the newest release. Test missing/reordered/renamed keys, changed geometry, appearance
and focus cues, unsupported modes, stale telemetry and source-version mismatches.

Separate layout membership and geometry drift from purely visual variation. On drift,
invalidate affected templates, preserve diagnostics and request a small new reviewed
sample. Do not silently downgrade label authority or continue unattended generation.
Requalify on available supported runtimes; future OS releases cannot be pre-certified.

Group sibling layouts/seeds/sessions across splits; related screenshots are not
independent. Reserve real-system/version transfer data before training. Development
regression may be iterated against, but then is not untouched final evaluation.

## Deliverables and acceptance

Producer: capability matrix; schema/examples; custom keyboard scene and native-key
probe; bounded sweep/accounting; text insert/clear and directional-sequence evidence;
tests for failure, limits/cancel and cleanup. Extend existing Fixture/campaign paths.

Consumer: compatible keyboard role/text metadata, native-label intake, OCR proposal
adapter and preset review, production16%/256 crop QA, split/lineage and coverage report.
Retain unmatched/unsupported cases as unavailable. No model or taxonomy promotion.

Acceptance requires source-pinned positive/negative software tests, actual original
frame-to-key geometry verification, exactly accounted native eligible members, one
true focused key per settled ordinary state, matched hard negatives, failed-input
accounting and postflight health. A small genuine-system holdout checks transfer;
report focus recall/false positives and complete-frame selection by version/layout.
Do not declare production coverage based on custom synthetic volume alone.

Priority: (1) schema/capability probe and configurable custom lane; (2) verified
native-system transfer sample plus automatic proposals; (3) version-drift regression
and bounded scale. Current real-screen crop QA remains independently unblocked.
