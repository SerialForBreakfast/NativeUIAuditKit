# Diverse native UI corpus — deferred implementation plan

Date: 2026-10-01. Planning owner: NUIAK Codex. Execution owners unassigned.
Priority: deferred behind current focus experiment; Tasks.md is the execution queue.
Update2026-10-05: [UI-SOURCE177](UIComponentIntake.md) completed source/dependency/
license inspection and ranks actual adapter candidates. This supersedes the original
uninspected candidate ordering, not the source-specific import/qualification gates.
This assignment records research and actionable work only. No code acquisition,
capture, training, model replacement or TTR implementation is dispatched here.

## Outcome and limits

Build a reusable library of genuinely different native tvOS screen structures,
with rights-reviewed code/content, configurable data and appearance, and measured
per-frame annotations. Reuse TTR's existing Fixture renderer/export and NUIAK's
intake, sampled review, crop QA and training interfaces. Do not build a parallel
capture or annotation system. This extends the existing
[semantic export request](../Requests/TTR-Semantic-Export-and-Fixture-Ground-Truth.md).

Success means better detection and focus selection on unseen layout families and
separate real-app screenshots, not a larger dataset or a higher same-template score.
Code-derived annotations are verifiable ground-truth candidates, not automatically
perfect labels. Appearance randomization encourages invariance; it cannot guarantee
that a model learns focus rather than an accidental shortcut.

## Candidate sources to investigate, not approved imports

| Candidate | Useful contribution | Required check before reuse |
| --- | --- | --- |
| [Apple TVUIKit full-screen layout](https://developer.apple.com/documentation/tvuikit/creating-immersive-experiences-using-a-full-screen-layout) | UIKit collection layout and native focus behavior | Exact downloaded sample license, bundled assets, current SDK/build compatibility |
| [Apple SwiftUI media catalog](https://developer.apple.com/documentation/swiftui/creating-a-tvos-media-catalog-app-in-swiftui) | Shelves, lockups, detail/product screens | Sample-specific terms and asset rights; not presumed MIT |
| [PGSSoft ParallaxView](https://github.com/PGSSoft/ParallaxView) | MIT-described tvOS parallax controls and collection cells | Pin revision, inspect license and example assets, assess older API compatibility; component diversity is not independent app diversity |
| [Jellyfin Swiftfin](https://github.com/jellyfin/Swiftfin) | Complex native tvOS media UI and navigation | MPL-2.0 obligations, dependencies/build cost; replace unlicensed server/media content with owned assets |
| [Ferret-UI 2](https://arxiv.org/abs/2410.18967) | Research describes Apple TV screenshots with human annotations | Verify actual dataset release, exact terms, annotation coverage and permitted use; no downloadable tvOS source-paired corpus established |

Sources inspected online on 2026-10-01; no candidate was downloaded, built or
qualified. Prefer a small number of independent, useful implementations over
indiscriminate repository harvesting. Related forks share ancestry.

## Tranche A — rights and coverage inventory

**NUIAK:** Produce a source register with URL, pinned revision, upstream family,
code license/notice, asset/font/icon licenses, dependencies, modification obligations,
permitted intended uses and unresolved restrictions. Preserve required attribution.
Separate permission to use code from permission to use photographs, logos, movie
posters or remotely fetched content. The [MIT license](https://choosealicense.com/licenses/mit/)
requires retaining its copyright and permission notice; a repository badge is not
an asset-by-asset rights determination. Do not treat fair use as a blanket approval;
unresolved rights require permission/review or replacement with owned content.

Build a coverage matrix for browsing shelves, mixed-size grids, detail pages,
search/keyboards, settings rows, dialogs/overlays and playback controls. Record native
versus custom controls, focus effects, selected parents, clipping and nesting.
Initial planning target: three independently sourced implementations spanning at
least six screen families; this is a collection target, not a qualification gate.

**Acceptance:** A go/no-go decision per candidate, exact allowed files/content and
obligations, diversity/ancestry inventory, and a ranked first integration choice.
No bulk import until this review is complete.

## Tranche B — reusable TTR scene adapters and annotation contract

**TTR request, deferred:** Add adapters within the existing Fixture mechanism for
approved UIKit/SwiftUI components. Keep upstream provenance/notice and adapter
version. Recipes specify source/layout family, seed, data, styling, asset IDs,
ordering, scroll position and requested focus. Avoid requiring production servers,
accounts or network content; inject local deterministic data.

Export through the existing versioned handoff: original screenshot/hash, runtime
and OS version, recipe identity, source/asset ancestry, actual observed focus,
selected state separately, stable scoped element IDs, hierarchy, semantic roles,
layout bounds, transformed visible body bounds, clipping/visibility, viewport
transform, settling evidence and screenshot/observation correlation. Report
unsupported fields explicitly. Preserve temporal action evidence when captured;
do not infer successful movement from requested focus.

**NUIAK:** Agree exact schema examples and map roles without silently changing public
detector classes. Reuse existing importer; unsupported roles remain diagnostic.
Cross-check geometry on growth, parallax, clipped cards, nested controls and overlays.
Native accessibility group bounds must not substitute for visible control bounds.

**Acceptance:** One approved screen adapter emits reproducible real rendered pairs
accepted by existing intake/crop tooling, including negative and incomplete cases.
Measured boxes match visible enlarged bodies. Simulator and physical-device support
are reported separately; physical qualification is not a prerequisite to local work.

## Tranche C — controlled variation and paired generation

**TTR:** Support two explicit variation modes:

- Appearance-only: change owned artwork, text where layout stays constrained,
  colors, gradients, background patterns and shading; assert geometry invariance.
- Structural: vary shelf order, card sizes/aspect ratios, spacing, density, captions,
  scrolling, panels and overlays; recompute all geometry after layout settles.

For each recipe/content seed, traverse eligible controls and retain focused and
unfocused observations of the same target with visible competitors. Match content,
layout and background within a pair; record legitimate focus-induced geometry changes.
Balance assets and styles across both labels; never make a certain poster, color,
label string, position or background occur only when focused. Include selected-but-
unfocused parents, bright unfocused tiles, dark focused tiles and no-focus cases
where native observations establish them. Do not force one focus label on ambiguous
or transient frames. Keep exaggerated stress patterns separate from realistic data.

**NUIAK:** Audit balance, missing competitors, duplicate images/crops and family
counts. Thousands of recolorings do not count as thousands of independent layouts.
Measure invariance across matched content substitutions without assuming causality.

**Acceptance:** Replayable bounded pilot across the selected families; complete
annotations and actual label transitions; appearance-only geometry checks pass;
structural variants have fresh measured boxes, not copied template coordinates.

## Tranche D — automatic QA and efficient sampled human verification

**NUIAK:** Reuse prefilled annotation queues. Automatically validate membership,
hashes, coordinate conversion, visibility/clipping, focus consistency, completeness
and production crops on every frame. Use optional OCR/rectangle disagreement only
to flag review candidates, never to overwrite native truth automatically.

Separate a seeded random audit from targeted high-risk review. Stratify by source,
layout, native/custom renderer, control type, focus effect, label and OS/runtime.
Show full-screen overlays and paired focus states, not only isolated crops. Human
edits flag an adapter/recipe defect for correction and re-generation rather than
quietly masking systematic errors through thousands of manual edits.

Choose sample size from a declared acceptable defect rate and confidence level,
not a fixed percentage. For illustration, zero defects in 299 independent random
units gives a one-sided 95% upper bound near 1% under a binomial assumption
(1 - 0.05^(1/299)); correlated template variants do not satisfy that independence
assumption. Define the audit unit/defect, report per-stratum support and clustered
sampling limits, and avoid calling an aggregate bound proof for every class.
Requalify affected families after renderer/OS/layout changes. Sample approval is not
permanent verification of future boxes. Uncertain cases stay excluded/diagnostic.

**Acceptance:** Reproducible random and targeted queues with denominators, reviewed
defects/uncertainty, and a scoped admit/repair decision. No manual redraw requirement
for every character/card; no invented high-confidence or perfect-label claim.

## Tranche E — honest comparison, then scale

**NUIAK:** Assign source/app/layout ancestry groups to training, development and
protected testing before generation. Keep forks, derived layouts, matched pairs,
sequences and cosmetic variants in one group. Track asset overlap separately;
include an asset-disjoint check where claiming unseen-artwork performance.
Keep reviewed real-app evaluation separate; failure-mined examples remain
development-exposed. Do not recycle current development failures as a fresh exam.

Compare baseline against a candidate with the diverse data, preserving the
evaluation set and source-weight budget. First isolate data changes; a full-screen
focus detector is a separate architecture experiment, not bundled into this one.
Report element localization/class errors separately from focus errors, full-frame
wrong/multiple/no-selection counts, family-level support and retention. Check
whether improvement holds on withheld families and real screens, not merely crops.

**Acceptance:** Explicit keep/reject decision against criteria fixed before the run;
scale generation only after annotation quality and useful diversity are demonstrated.
Training/export/release require their assigned experiment scope and existing gates.

## Ownership and coordination

NUIAK owns rights/admission records, coverage/splits, review, evaluation and model
decisions. TTR owns source-adapter implementation, native rendering/control,
correlated capture and producer exports. Both agree examples and field semantics
before implementation. No new transport or annotation application is requested.

This is a locally recorded future request, not a published TTR assignment or
acknowledged capability. When prioritized, publish the B/C producer scope as an
addendum to the existing semantic/Fixture request, asking for owner, supported
adapters, exact export example and bounded pilot proposal. Keep current artwork
repair/model work first; this backlog introduces no new blocker for it.
