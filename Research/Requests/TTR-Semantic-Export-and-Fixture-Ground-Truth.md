# TTR implementation request: native semantics, Hover Text and Fixture ground truth

Request ID: `nuiak-20261001-semantic-export-fixture-v1`  
Priority: High — focus corpus and efficient annotation  
Requested by: NUIAK maintainer, 2026-09-30 PDT  
Owners: TTR observation/runtime and Fixture maintainers; NUIAK importer reviewer  
Status: Requested; not implemented or qualified by this document

Operational acceptance: [producer/consumer addendum](TTR-Synthetic-Pipeline-Acceptance.md)
specifies replay-safe jobs, finalization, portable bundles, corrections, feedback and
the schema/examples needed before build delivery. It extends this same request.
Canonical work-package names are TTR-A through TTR-F in the joint pipeline plan;
the A/B/C sections below are capability groupings, not competing task IDs.

## Outcome

Deliver screenshots with synchronized, source-attributed semantic and geometric
annotations through TTR's existing capture/export and CLI/MCP workflow. Fixture
should generate complex, varied screens with automatically verified ground truth;
humans review representative recipes and exceptions, not draw every rectangle.

Provide three distinct capabilities:
1. Native accessibility export from the existing runner where accessible.
2. Optional Hover Text observation with local OCR, explicitly a weaker fallback.
3. Fixture-owned render/semantic instrumentation for reproducible synthetic data.

"Perfect annotations" is the engineering objective for controlled Fixture scenes:
complete, correctly correlated, measured and mechanically checked. Do not claim
perfect real-app accessibility metadata, OCR, or production model accuracy.
Export success alone does not establish annotation correctness or training admission.

This request expands the implementation needs behind
`nuiak-20261001-corpus-source-layout-contract`; retain that request's ancestry and
keyboard/selected-parent questions rather than dispatch duplicate work. Braille
ADR0041 remains separate research, not a dependency or part of this implementation.

## 1. Native accessibility snapshot/export — first delivery

Reuse the current native runner and coordinator. Inventory fields already captured
before introducing a second runner or framework. Export the strongest available
observations, with explicit unsupported/unavailable/partial states. Qualify Fixture,
Simulator system apps, physical system apps and third-party apps separately;
success in one does not establish access to another. Do not require VoiceOver to be
enabled just to obtain an accessibility tree when the existing runner can read it.

For each accessible element, export when supplied:
- Provider-local element identity, app-supplied identifier, parent and child
  relationships, and identifier stability scope. Labels are not unique identifiers.
- Label, value, hint, element type/traits, enabled/selected state, focusability
  where available, and bounds. Preserve raw role values plus any documented mapping.
- Navigation/input focus and assistive focus separately, with evidence source and
  unknown state. Selected tabs/parents must not become a second focused control.
- Coordinate space, viewport origin, orientation and point-to-pixel transform;
  distinguish accessibility grouping bounds from measured visible control bounds.
- Field provenance and completeness. Do not manufacture missing descriptions,
  focusability or focus from OCR, command intent, visible brightness or labels.

Capture native snapshots before and after the image within a bounded interval.
Verify matching target, session/generation and stable relevant layout/focus; return
ambiguous or unsettled when they differ. Do not invent atomic frame identities.
If native support is unavailable, preserve the image and say why; no silent fallback
from native fields to inferred fields under the same provider identity.

## 2. Hover Text provider — optional and independently useful

Add a default-off observation option using already enabled/configured tvOS Hover
Text and TTR's existing capture plus local Vision OCR. Detect/qualify the overlay
region or allow a reviewed region configuration; return its pixel bounds, raw OCR
text/confidence, language, scrolling/truncation/completeness and capture reference.
Keep this provider named and attributed as Hover Text OCR, not native accessibility.

No silent settings mutation: preflight reports whether the capability is usable,
requires user setup or is unsupported/unknown. Settings changes need the separately
approved session scope, recorded original values and verified restoration if changed.
Do not add per-frame prompts once a bounded session has been approved.

Account for absent overlays, animated/scrolled text, stale repeated text, duplicate
labels, dialogs and occlusion. Do not treat matching text as proof an input succeeded.
Hover Text is an assistive rendering: record its enabled state and overlay region.
Never crop/erase/inpaint the overlay and call the result an original clean frame.
Clean visual-only examples require a separate verified capture; bind observations
only when the relevant scene/target is unchanged. Uncertain correspondence stays
diagnostic. Native export and Fixture generation must not wait for this provider.

## 3. Fixture instrumentation and complex-screen generation — core training deliverable

Expose observed state from the actual rendered Fixture, not just requested recipe
coordinates/focus. Use native focus callbacks and post-layout geometry with a
layout generation and settling evidence. Keep accessibility semantics and visible
geometry separately attributed, even when Fixture supplies both.

Required scene families and state combinations:
- Sparse/dense artwork grids and shelves; mixed card aspect ratios, imagery,
  placeholders, captions, bright/dark backgrounds and nearby focused competitors.
- Native buttons, wide buttons, dialogs and settings-like rows with accessories.
- Tabs with selected-but-unfocused parents and a focused descendant; nested groups,
  scrolling/clipping, overlays and transitions. Preserve focus-scope relationships.
- Keyboard characters, space/delete/mode keys and layout changes. Distinguish a
  native OS keyboard from a custom Fixture imitation; identify OS/build and locale.
  Unsupported native key telemetry remains an explicit capability gap.
- Long/localized labels, repeated labels, dynamic text sizes and changed layout
  structures. Requested variation must be demonstrated in rendered pixels.

For every generated frame, export a full scene inventory, not just the requested
target. Include visibility, clipping/occlusion and inclusion/exclusion reasons.
For every applicable item retain:
- Stable recipe-local control ID, parent/focus scope, semantic role, label/value.
- Measured control-wrapper bounds; artwork-body and label bounds separately when
  applicable; visible/clipped bounds and presentation-effect bounds when measurable.
  Missing/inapplicable/estimated are distinct. Native buttons do not require a
  nonexistent artwork-body rectangle. Do not substitute nominal layout for measured
  scaled/parallax geometry without labeling the limitation.
- Requested target, observed navigation target, observed assistive target, selected
  state, interaction mode and relevant timestamps as separate fields.

Provide bounded native traversal of eligible controls using the existing action
mechanism. Record same-control focused/unfocused pairs with visible competitors,
preserving genuine switch/no-op events and action receipts. Prefer actual peer-focus
negatives; identify reference-focus negatives explicitly. If exactly-one focus is
expected, validate it within the declared scope; report multi/unknown focus instead
of repairing labels. Detect dead ends and unreachable targets; never loop forever.

Generation must be resumable and bounded by recipe/target count, duration, retained
bytes and free-space floor. Account for every planned target: accepted, rejected,
excluded, blocked or unattempted, with reason. Do not repeat completed captures to
recover an export failure. Keep deterministic seeds, asset hashes, recipe/renderer
versions, OS/runtime, source/layout ancestry and observed variation in provenance.

## 4. Shared delivery contract and NUIAK integration

Propose one additive, versioned semantic sidecar, reusing existing capture/receipt
identities. These are required semantics, not prescribed wire field names. Supply
an example and compatibility tests before NUIAK binds its adapter. Preserve current
imports; no silent breaking sidecar or taxonomy change.

The sidecar binds: image hash/dimensions; target/app/runtime; capture and native
observation intervals/clock domains; action IDs; provider version; session/generation
and sequence; locale/assistive mode; complete/partial state; per-element records;
raw evidence references; and explicit uncertainty/withholding reasons. Time after
an action is correlation, not proof of causality. Fence reconnects and report loss
or overflow; require a fresh baseline after gaps.

Expose capability discovery, snapshot and batch export through existing app-owned
CLI/MCP access and ownership controls. Return compact results plus artifact
descriptors; no embedded full-image payloads by default or new parallel control
channel. A batch should run without chat between presses. Preserve originals and
verified receiver receipts. Keep private content out of logs/shared metadata and
withhold sensitive frames/text before export; hashes are not privacy protection.

NUIAK owns consumer normalization, provenance-aware box/label proposals, review,
production crop QA and training/evaluation admission. Focus crops remain16% expansion
and256×256 via the existing production cropper; TTR should supply original images
and geometry rather than replace that contract. Native labels should reduce work to
accept/correct exceptions; OCR proposals stay optional. Labels may supervise a
visual-only model, but semantic sidecars must not enter that model's inference
inputs. Report accessibility-assisted runtime evaluation separately.

Reserve source/layout/asset-related groups before generation. Keep existing
development, retention and protected challenge memberships intact. Different seeds,
sessions or colors do not establish independent sources. Do not repurpose the
matched24validation campaign. Existing production coverage gates remain unchanged.

## Delivery tranches and acceptance

**A — Native export end to end.** Deliver a capability matrix and one actual
image/sidecar/export/receiver-import example through existing callers. Test missing
fields, duplicate labels, selected versus focused, invalid bounds, target/generation
mismatch, stale snapshots, changed hashes, partial trees and unavailable providers.
Reuse current runner; no hardware purchase or braille prerequisite.

**B — Fixture corpus automation.** Deliver a source/layout-bound recipe manifest,
bounded generator, full inventories, same-control pairs, resumable accounting and
recipe-level review sheets. Demonstrate grids, rows, tabs/nested selected parents,
buttons and keyboard capability or an exact unsupported case. Check native focus
against frame brackets, geometry against rendering and requested diversity against
pixels. Deliver positive and intentionally invalid examples; no exhaustive manual
annotation of generated rectangles. Do not block supported families on keyboard work.

**C — Optional Hover Text end to end.** Demonstrate actual overlay capture/OCR and
attribution on a separately approved target. Test absence, scrolling, truncation,
duplicates, occlusion, reconnect and disagreement with native evidence. Measure
annotation effort and observation latency; no accuracy/token-saving claims without
comparison. This tranche can proceed independently of B.

Complete offline parser/contract tests first, then actual producer-to-consumer proof
under approved target/session scope. Report software, data eligibility, integration
and model-gate outcomes separately. This request commissions an implementation
proposal/work item; it does not itself dispatch device operations, install runners,
change accessibility settings, buy hardware, train or promote models.

## Requested TTR response

Return the implementation owner and order, existing/reusable versus missing fields,
proposed sidecar/example, platform/app coverage limits, exact first live-proof scope,
and estimated effort. Answer explicitly:
1. Which labels/values/bounds/focus fields can the current native runner already export?
2. Which Fixture measurements are observed versus nominal, especially artwork effects?
3. Can native keyboard keys and selected-parent states be exported, and on which runtimes?
4. Can Hover Text use current capture/OCR without new permissions or a new control path?
5. Which source/layout groups and generation budgets are proposed for new training data?

Please acknowledge this request ID; implementation, live compatibility and NUIAK
admission are separate later receipts, not implied by acknowledgment.

## Research references

- Apple: [XCUIElementAttributes](https://developer.apple.com/documentation/xcuiautomation/xcuielementattributes).
- Appium reference, not a required dependency: [element attributes](https://appium.github.io/appium-xcuitest-driver/latest/reference/element-attributes/).
- Apple: [Hover Text](https://support.apple.com/guide/tv/use-hover-text-to-see-enlarged-text-atvb8f832e2e/tvos), [VoiceOver modes](https://support.apple.com/en-euro/guide/tv/atvbfa4ff6cd/tvos).
- NUIAK: [focus/VoiceOver separation](../ADR-0007-VoiceOver-Navigation-Focus-Alignment.md), [corpus collection needs](../../reports/work/FOCUS-CORPUS-03/collection.md).
