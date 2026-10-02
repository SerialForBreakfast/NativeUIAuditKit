# Accessibility-assisted real focus annotation — 29

Planning review, October 2, 2026. Owner: NUIAK/Codex. Execution queue: Tasks.md.
Purpose: turn TTR's accessibility observations into better ordinary-appearance real
training and evaluation examples, especially the reference pairs missing from Native28.
This plan assigns consumer work; live capture, data admission and model execution retain
their applicable authorization boundaries.

## Evidence reviewed

Published TTR source **45c84b69459743e60570117edc46be65402a8d9e** (19:34:47Z),
not the adjacent dirty local checkout at 46dce7b. Source inspection does not identify
the installed running build. Primary reports, pinned to that revision:

- [Physical accessibility comparison](https://github.com/SerialForBreakfast/TVTestRig/blob/45c84b69459743e60570117edc46be65402a8d9e/Docs/Testing/2026-10-02-office-accessibility-comparison.md).
- [Appearance throughput and annotation mapping](https://github.com/SerialForBreakfast/TVTestRig/blob/45c84b69459743e60570117edc46be65402a8d9e/Docs/Testing/2026-10-02-appearance-throughput-annotation-mapping.md).
- [Implemented perception and runner reuse](https://github.com/SerialForBreakfast/TVTestRig/blob/45c84b69459743e60570117edc46be65402a8d9e/Docs/Testing/2026-10-02-campaign-reuse-accessibility.md).
- [Mapping acceptance plan](https://github.com/SerialForBreakfast/TVTestRig/blob/45c84b69459743e60570117edc46be65402a8d9e/Docs/Plans/2026-10-02-accessibility-annotation-mapping.md),
  [ADR 0048](https://github.com/SerialForBreakfast/TVTestRig/blob/45c84b69459743e60570117edc46be65402a8d9e/Docs/Decisions/0048-accessibility-assisted-annotation-templates.md), and
  [local navigation plan](https://github.com/SerialForBreakfast/TVTestRig/blob/45c84b69459743e60570117edc46be65402a8d9e/Docs/Plans/2026-10-02-local-navigation-verification.md).

Later producer status at 19:55:36Z reports acquisition stopped on a correspondence
mismatch and settings/session cleanup completed. That is a producer report, not a
consumer replay or current device availability. Request its sanitized failure analysis
before repeating the mapping trial.

| Capability | Observed result | Useful to NUIAK / remaining limit |
| --- | --- | --- |
| High Contrast | Home outlined focus; Settings retained filled highlighting | Additional focus-location evidence, not universal detection or ordinary body geometry |
| Cross-profile geometry | One Home icon: assisted outline 286px wide versus ordinary body about 306px; IoU .930 | Outline was about 10px **inside each horizontal edge**. Direct copying clips the normal focused body; no universal padding correction |
| Hover Text CLI/MCP | 5/6 retained banner-on cases proposed; 0/2 off controls; 106–218ms ROI analysis | Optional semantic hints. One heading case missed; actionability remains unknown |
| Hover Text navigation | Physical banner rendered; noninteractive heading stops, context, clipping and clock contamination observed | Banner text is not necessarily an actionable control or ordinary input focus |
| Simulator Hover Text | Enabled state without banner in retained trial | Invocation/runtime feasibility unresolved; do not call universally unsupported |
| Reduce Transparency / Motion | Transparency reduced measured Settings contrast; settled growth persisted with reduced motion | Do not enable these as assumed training improvements; timing comparisons were confounded |
| Native accessibility | Fixture instrumentation remains the strongest structured truth | No qualified generic physical third-party accessibility text feed; passive Settings logs yielded no events in six moves |
| Appearance throughput | Matched 12 recipes 145.944→113.737s, 22.1% reduction | Useful next capture optimization, not a reason to repeat unchanged training |
| Transition runner reuse | 48-pair CLI/MCP/resume path tested | Transition-only option; do not infer appearance or multi-Simulator qualification |

Physical evidence is Apple TV HD; exact OS marketing-version correspondence was
unresolved. Home/Settings observations do not establish third-party app-interior,
locale, hardware or OS-wide reliability. Small retained counts are development results.
Apple documents configurable Hover Text placement and appearance, reinforcing that
the tested top-160px ROI must not become a universal assumption:
[Apple TV Hover Text](https://support.apple.com/en-nz/guide/tv/atvb8f832e2e/tvos).

## Decision: an annotation assistant, not a replacement ground truth source

### Priority refinement: High Contrast first; Hover Text optional

Maintainer direction, October2: prioritize High Contrast focus over Hover Text.
Make profile provenance first-class, not a mandatory Hover Text provider. The core
annotation path must work without banners, OCR text or Hover Text availability.
High Contrast is the leading qualification candidate, not yet proven more accurate
across arbitrary apps. Use three distinct purposes: focus evidence, capture stability,
and model robustness. A setting helpful for one purpose may harm another.

Apple's current [contrast guide](https://support.apple.com/en-gb/guide/tv/atvb81aeaf3f/tvos)
lists Reduce Transparency, Increase Contrast and Focus Style separately. Discover
actual settings on the selected OS/device rather than collapsing these into a single
"high_contrast" boolean or assuming the latest guide matches the installed OS.

| Priority / option | Proposed TTR use | Proposed NUIAK use / qualification question |
| --- | --- | --- |
| P0: Focus Style High Contrast | Outline-assisted local focus verification, scoped by app/control family | Identify ordinary-frame focus via verified correspondence; measure false outlines, abstentions and body-edge differences |
| P0: profile receipts and restoration | Inspect actual state, apply named supported changes, verify, restore original state | Every capture records settings and evidence strength; prevent accidental profile mixing |
| P1: Increase Contrast | Test foreground/background separation independently of Focus Style | Does it improve focus/box proposals or change all controls equally? Preserve ordinary counterparts |
| P1: Reduce Transparency | Test whether simpler backgrounds improve tracking/OCR | Existing Settings contrast decreased; measure corrections/errors, not perceived legibility alone |
| P1: Auto-Play Video Previews off | Test reduced background motion in supported apps | Cleaner correspondence pairs; preserve separate ordinary-motion test examples |
| P1: Reduce Motion | Test settling variance and tracking success | May alter the native cue being learned; compare settled growth, shadow and shading before adopting for collection |
| P1 enabler: Accessibility Shortcut | Qualify state-preserving profile switching, where the feature is actually listed | Fewer Settings round trips could reduce identity loss; verify same screen/focus and restoration |
| P2: Differentiate Without Color | Observe alternative visual cues in supporting apps | Test whether shape/symbol cues improve detection; may change content/layout, so recapture boxes |
| P2: Color Filters, Reduce White Point, Light Sensitivity | Controlled display-profile stress cases | Test color/brightness dependence; not additional focus truth. Verify the effect reaches the capture transport |
| P2: Bold Text / available text-size controls | OCR/legibility and layout stress | Test truncation, row geometry and box robustness; measure fresh bounds after reflow |
| P2: Hover Text | Optional label/context lookup when needed | Existing provider remains usable; banner/heading/occlusion uncertainty cannot block core focus workflow |
| P2 bounded spike: Switch Control | Candidate accessible-item/group discovery | Compare scan coverage with fixture inventory; scan highlight is not ordinary input focus or exact body bounds |
| P3: VoiceOver navigation / speech | Semantic traversal and label checking where qualified | Accessibility completeness and labels, with assistive/input focus separately attributed; no generic utterance export established |
| P3: Zoom / Follow Focus | Candidate magnified inspection | Changed viewport/transform/occlusion makes ordinary box mapping expensive; use only for a specific unresolved case |
| P3: Siri / Type to Siri, remote navigation accommodations | Potential setup/recovery route where supported | Operational convenience, not annotation truth; evaluate separately from perception accuracy |
| Deferred: captions, audio descriptions, hearing controls, braille | Targeted accessibility-testing scenarios | Not priority sources of focus labels; captions may become distractors in later robustness work |

Primary platform references: [motion and preview controls](https://support.apple.com/en-gb/guide/tv/atvb1f949820/tvos),
[light/color options](https://support.apple.com/en-gb/guide/tv/atvbf413b243/tvos),
[Switch Control](https://support.apple.com/guide/tv/get-started-with-switch-control-atvbc96e032c/tvos),
[shortcuts](https://support.apple.com/en-gb/guide/tv/atvb0a315d10/tvos),
[Zoom](https://support.apple.com/guide/tv/use-zoom-to-magnify-atvb4dc7fb7e/27/tvos/27).
These document platform features, not TTR transport or Simulator qualification.

### Implement the common support, then qualify one feature at a time

TTR request: extend existing profile/observation work with a capability table per
target/runtime and transport: present, readable, controllable, visually effective in
capture, restorable, qualified scope, or unknown. Preserve separate values for focus
style, increased contrast, transparency, motion, preview autoplay, color/filter
intensity, text settings and assistive-navigation mode. Store original and verified
applied values, action receipts and cleanup outcome. Implement only supported routes;
publish explicit unavailable reasons rather than guessing private settings APIs.

Use baseline → single changed setting → restored baseline comparisons on the same
scene. Begin with fixture truth across artwork, rows, tabs and buttons, then qualify
real-app use. Pairing needs verified identity after every profile transition; changing
a setting may leave the app, move focus or change layout. Capture-path qualification
must distinguish a visible display effect from an effect actually present in captured
pixels. Compare latency/settling p50/p95, failed correspondence, false focus decisions,
abstentions, coverage and human corrections. Alternate trial order to reduce timing
drift. Test combinations only after individual benefits are measured, rather than
launching a combinatorial capture sweep.

For navigation, keep ordinary directional focus as the baseline. Switch scanning,
VoiceOver exploration and ordinary navigation can enumerate different items. Preserve
group-versus-leaf identity, discovered/not-reached coverage and separate focus channels.
TTR ADR0044's broad claims of complete enumeration/exact boxes are explicitly
unqualified by its feasibility amendment; do not turn those into consumer guarantees.
Qualify a working exit before enabling a mode that changes input interpretation.

Shortcut qualification is a useful enabler, not an assumed implementation. Apple
documents Back/Menu triple-press; TV-button hold opens Control Centre. One enabled
shortcut toggles directly; multiple choices show a menu. Discover whether the desired
feature is listed—High Contrast shortcut eligibility is not established here. TTR's
three serialized Back calls took1.578s and navigated Home; they did not implement the
gesture. Request a supported transport-level gesture if available, with state checking
and unknown-completion handling; do not repeat that macro or claim zero state loss.
See TTR [feasibility evidence](https://github.com/SerialForBreakfast/TVTestRig/blob/45c84b69459743e60570117edc46be65402a8d9e/Docs/Testing/2026-10-01-accessibility-feasibility-spikes.md)
and proposed ADR0044/0045 with their qualification caveats.

NUIAK implementation priority: optional typed profile evidence and High Contrast
focus proposals first; ordinary rendered-body proposals and grouped review next;
then profile-stratified evaluation. Keep assisted-only runtime navigation useful in
its own right, while reporting ordinary-profile transfer separately. Offline grayscale
or brightness augmentation may test hypotheses cheaply, but is not proof of an OS
filter's behavior. Keep related profile variants in one split, not extra independent
samples. Broader accessibility-mode training gets an explicit dataset purpose and
measured default-profile retention, rather than silently replacing the ordinary model.

Use TTR's existing ACC-PERCEPT-01, ACC-MAP-01 and NAV-VERIFY-01 work. NUIAK owns
candidate intake, annotation review, crop checks, corpus roles and model evaluation;
TTR owns capture, settings receipts, navigation and restoration.

1. Retain the ordinary screen and independently identified focus state.
2. Observe the same control with High Contrast and optionally Hover Text, retaining
   separate profile receipts and evidence. A heading, duplicate label or changed
   viewport is a reason to withhold correspondence, not guess it.
3. Restore ordinary appearance and verify control identity, screen/viewport and settled
   focus again. Capture an ordinary unfocused reference for paired model use.
4. Propose boxes from **ordinary rendered bodies**, supported by native measurements
   where available and visual proposals otherwise. Keep assisted outlines separate.
5. Review prefilled ordinary frames in one grouped annotation batch. Retain a random
   sample plus a distinct disagreement/failure sample; report both denominators.

An assisted frame is useful evidence of identity/focus, not a fabricated ordinary
frame. Do not erase the banner, recolor the image, infer an unfocused body from a growth
ratio, or normalize away enlargement. For FDR036, reliable ordinary unfocused-reference
bounds are still required; an assisted outline alone does not unblock real replay.

## Consumer contract to align with TTR

Extend/reuse the existing observation envelope; no competing dispatcher or mandatory
new provider. Preserve raw field meanings and version additions compatibly.

- Capture/frame ID and hash, target/runtime/app and known OS identity; action and
  sequence IDs, timestamps/clock domain, freshness and settled evidence.
- Accessibility profile **per frame**, distinguishing caller-declared from verified
  settings receipts; unknown stays unknown. Input focus, assistive focus, banner text,
  selected tab and requested focus are distinct observations.
- Coordinate dimensions/origin/units and transform provenance. Separately typed
  layout, rendered body, artwork, outline, shadow/context and banner bounds.
- Semantic label/context, actionability (including unknown/heading), source/provider,
  clipping/occlusion/coverage, screen/viewport identity and evidence references.
- Cross-frame correspondence source, competing candidates, rejection reasons and
  profile-restoration evidence; absence is not an implicit exact match.
- Outcomes: verified-for-stated-predicate, ambiguous, stale, unsupported, interrupted.
  Missing banner means unavailable evidence, never unfocused. Conflicting sources
  trigger review; correlated confidences are not multiplied into a probability.

Consumer acceptance measures identity errors, false focus decisions, abstentions,
coverage, manual correction time and ordinary-body per-edge pixel errors as well as
IoU. Report both source-pixel and crop-scaled edge errors, clipping and occlusion.
No auto-admission threshold is qualified yet: consumer review calibrates geometry
tolerance by control family. A known wrong identity or clipped body cannot be accepted
because average IoU is high. The retained 10px discrepancy is a failure example, not
a requested blanket 10px correction. Initial calibration compares independent human
boxes against proposals and a plain-Vision baseline.

## Prioritized substantial tranches

### P0 — local consumer and retained-evidence qualification

- Reconcile the producer's later correspondence-mismatch report with its pinned source;
  inventory eligible retained ordinary/assisted/reference pairs and explicit gaps.
- Implement optional observation/provenance import into the existing review flow,
  preserving supplied boxes as proposals. Add negative tests for duplicate labels,
  headings, profile changes, stale observations, scroll/overlays and missing references.
- Produce one grouped review queue with normal frames, assisted evidence links, reason
  codes, random samples and disagreement samples. Benchmark reviewer effort and box
  corrections against ordinary Vision/OCR proposals.
- In parallel, finish SETTINGS-SWIFT-SPIKE-25's offline arithmetic/tracking comparison;
  this remains useful independent of physical capture availability.

Acceptance: actual import/review caller and realistic failure cases tested; evidence
report identifies precisely which pairs can be considered for admission. Captured
private content stays local. New real capture is a separately scoped next dependency,
not a prerequisite for local importer tests.

### P1 — fill real coverage gaps, then test transfer

Use ACC-MAP-01's bounded profile-matching trial when appropriately authorized, with
Home/Settings controls first and separately identified third-party app-interior coverage.
Resolve the reported mismatch before expanding. Include duplicates, focus unchanged,
focus moves, scrolling, overlays and absent/unhelpful contrast outlines. Review ordinary
focus and rendered-body bounds; choose corpus role explicitly before admission.
Then replay the frozen FDR036 on qualified ordinary pairs and compare with the existing
baseline. Report settings versus artwork separately. Further training is justified by
the observed error pattern, not the mere availability of more assisted images.

### P2 — scale useful generation and optional runtime integration

Qualify published appearance optimization locally for the next justified capture;
qualify transition runner reuse only for transition campaigns. Keep single-Simulator
baseline timing before considering parallelism. Reuse fixture native truth for synthetic
generation. Optional TTR observer integration follows measured real-data performance;
braille, generic VoiceOver extraction and unqualified accessibility variants remain
lower priority than this direct path to ordinary real-app labels.

## Dataset maintenance

Ordinary-style models train/evaluate on ordinary pixels. Assisted images may provide
review evidence; any assisted-profile model dataset has an explicit separate purpose.
Group ordinary/assisted captures, paired endpoints, scene variants and traversal ancestry
in the same split. A changed accessibility profile is not an independent test scene.
Preserve profile/OS/app/renderer provenance under ADR-0017. Keep a held-out ordinary
real-app benchmark separate from annotation-rule and threshold development. Privacy
withholding applies equally to OCR strings, banners and screenshots.

## Planning outcome

### Assigned implementation, October2

The consumer adapter accepts a hash-bound existing review batch plus optional
accessibility evidence, and creates a new immutable proposal batch using the same
editor/Finish review/crop QA callers. Evidence must bind ordinary frame hash, target,
screen/viewport, profile receipt and explicit correspondence. Outlines never replace
ordinary boxes. Missing or conflicting evidence is flagged in the grouped review;
original proposals and evidence remain intact. A deterministic random sample is
reported separately from flagged frames; both sets open in a single editor directory.
The adapter is a consumer evidence contract, not a claim TTR exports this exact schema.
Real FDR036 replay requires reviewed ordinary pairs; missing evidence is reported
before loading weights. Settings25 runs its approved retained-data comparison independently.

Consumer implementation and offline verification are complete; see the
[integrated handoff](../../reports/work/ACCESSIBILITY-ASSISTED-29/handoff.md).
Real transfer awaits qualified ordinary reference pairs and producer correspondence
evidence. No model gain is attributed to accessibility yet. The measurable next
win is fewer manual labels with verified ordinary-frame focus and bounds, followed by
a real paired-model result—not another synthetic-only accuracy claim.
