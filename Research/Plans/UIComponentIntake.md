# Native UI source intake — UI-SOURCE-177 spike and low-priority follow-ons

ART-HANDOFF178: maintainer requests native source adapters and artwork practices be
owned by TTR. Proposal/image delivered, acceptance pending. Producer follow-ons below
are planning inputs for TTR, not authority for duplicate NUIAK renderer work; retain
consumer contracts, admission, lineage and model evaluation in NUIAK.

Date: 2026-10-05. Scope: read-only source/dependency/license inspection and one
generated poster-sheet review. No third-party code executed, installed or vendored;
no simulator, capture, training or producer edits. FFC means feasibility, fidelity
and cost here; cost estimates are relative engineering judgments, not measured hours.
Tasks.md remains the sole queue. This refines DUC-A/B, not a competing corpus plan.

## Strategy and evidence standard

Inspect repository tree, pinned source, project/package manifest, lockfile, license,
representative render/focus code and image-data provenance. Separate native-platform
support from README marketing. Record all declared dependency pins where available;
do not claim complete transitive-license clearance from a root license. Favor the
smallest independently useful source slice. Do not import account/network/player
infrastructure just to render a shelf. Every future adapter requires deterministic
data injection, stable IDs, observed focus and per-frame visible geometry.

Five named implementation candidates, three discovery indexes and two dataset
families were assessed. Apple sample was downloaded into ignored research storage;
GitHub source was read via API/raw URLs. No Git writes or repository clones.
Current remote revisions are audit pins, not promises of compatibility with our SDK.

## Ranked implementation candidates

| Rank | Candidate | Source evidence | FFC judgment / decision |
|---|---|---|---|
| 1 | Apple tvOS media catalog | Actual 39,806,690-byte archive, 207 entries; tvOS18 project, no external package references | Best rich-screen starting point; moderate adapter work, high composition relevance; conditional go |
| 2 | Jordan Singer SwiftUI-Kit | tvOS17 target; small shared native view groups, no external package references found | Cheapest control baseline, limited independent visual style; conditional go |
| 3 | PGSSoft ParallaxView | tvOS9+ Swift5.3 package, empty dependencies; native UIFocusUpdateContext callbacks | Strongest small custom-focus extension; medium geometry/runtime risk; conditional go |
| 4 | Barbara Martina SwiftUI Catalog | Numerous reusable source views, no project/package manifest in inspected tree | Good iOS styles/layouts; not a drop-in tvOS app, shell/platform work needed; iOS-only follow-on |
| 5 | Jellyfin Swiftfin | Real media client, 41 package lock pins, app-specific poster/image/environment types | Highest real-app richness, highest integration/license surface; defer whole-app import, isolate one shelf proposal |

These are source judgments. No candidate has passed a local build, measured geometry
or consumer intake. No model-quality ranking can be inferred from visual richness.

### 1. Apple media catalog: inspectable full-screen baseline

[Official page](https://developer.apple.com/documentation/swiftui/creating-a-tvos-media-catalog-app-in-swiftui)
and [exact archive](https://docs-assets.developer.apple.com/published/4151095c6511/CreatingATvOSMediaCatalogAppInSwiftUI.zip).
Archive SHA256 `b234e9bb4a15a29a6b0cd254243750e5872ff753ae3a88acaa76c9ec85b134e9`.
Retained: `reports/work/UI-SOURCE-177/artifacts/apple-media-catalog.zip`.

Inspected LICENSE.txt, project.pbxproj, MovieShelf.swift, Artwork/Asset.swift,
Artwork/CodeSampleArtwork.swift, HeroBackgroundView.swift and
ViewModifiers/VisibleWhenFocusedModifier.swift. Tree includes CardShelf, StackView,
SearchView, DescriptionView, SidebarContentView, TVMusicShelf and ButtonsView.
MovieShelf uses native Button, LazyHStack, borderless styling and disabled scroll
clipping; native behavior must be measured after focus growth, not assumed from layout.
Hero uses a gradient mask over a bundled landscape image. VisibleWhenFocused reads
the SwiftUI isFocused environment. Asset is a local 15-item enum with named portrait/
landscape images and keyword search—no server needed for these inspected paths.
CodeSampleArtwork uses `randomElement()`: replace with seeded/catalogued selection
before calling captures reproducible. Sample minimum tvOS18; not built here.

LICENSE.txt grants broad use/modification/distribution with copyright/permission
notice retention and warranty disclaimer (MIT-form text, Apple2024 copyright).
That supports a code-slice proposal, not an assertion that every artwork subject,
mark or third-party asset has been independently cleared for our corpus. First adapter
uses our own reviewed artwork and retains the sample notice. No external package
references were found in the inspected project; Apple SDKs are still dependencies.

### 2. SwiftUI-Kit: useful, but tvOS does not include every advertised control

Pin `1211aa6b1aee07a3860e4f45d5cd5efcfec64509` (master).
[Source](https://github.com/jordansinger/SwiftUI-Kit/tree/1211aa6b1aee07a3860e4f45d5cd5efcfec64509),
[license](https://github.com/jordansinger/SwiftUI-Kit/blob/1211aa6b1aee07a3860e4f45d5cd5efcfec64509/LICENSE).
Read Shared/ContentView.swift, Groupings/ControlsGroup.swift and project.pbxproj.
Shared source has buttons/colors/controls/fonts/images/indicators/shapes/text/map
groups. tvOS target declares17.0, Swift5.0. No SPM references or lockfile found.
ControlsGroup explicitly excludes sliders on tvOS and limits stepper/date/color
pickers to other platforms. Do not report those as new tvOS coverage.
Date() state and map examples are not suitable deterministic defaults; select a
small offline button/toggle/picker slice with fixed state and no map/network use.
Native focus observation/geometry hooks are not a supplied annotation exporter.
MIT copyright Jordan Singer2020 verified in full. Keep notice; replace brand assets
and any unclear media. Easiest integration is selected views, not the entire app.

### 3. ParallaxView: real focus hook, more than nominal-frame labels

Pin `a4165b0edd9c9c923a1d6e3e4c9a807302a1a475` (master).
[Package](https://github.com/PGSSoft/ParallaxView/blob/a4165b0edd9c9c923a1d6e3e4c9a807302a1a475/Package.swift),
[focus view](https://github.com/PGSSoft/ParallaxView/blob/a4165b0edd9c9c923a1d6e3e4c9a807302a1a475/Sources/Views/ParallaxView.swift).
Package has zero external dependencies and processes Sources/Resources. The view
is always focusable, observes next/previous native focused views, dispatches become/
resign callbacks, and supports configurable effects and press animations. Uses UIKit.
MIT PGS Software2019 full text inspected; source also carries original author notice.
Retain both. Resource-level review is still needed; avoid example images.
Qualification must measure transformed visible body, glow separately, clipping and
settling. Simulator success cannot prove remote-driven physical parallax realism.
Choose one card/cell with original artwork; no wholesale example import.

### 4. SwiftUI Catalog: broad iOS source library, incomplete build packaging

Pin `56ba26829a9cb06facec9b8fb1dff1962cf77b4f` (main).
[Source](https://github.com/barbaramartina/swiftuicatalog/tree/56ba26829a9cb06facec9b8fb1dff1962cf77b4f).
Recursive tree contains SwiftUICatalogApp, ContentView, compositional cards, grids,
tags/circle/columns layouts, custom styles, accessibility, UIKit PageControl bridge,
WebView, StoreKit, Charts and Metal examples. No .pbxproj, Package.swift, lockfile,
Podfile or Cartfile found in that tree. Therefore whole-project dependencies/build
closure cannot be declared resolved. Selected ImageWithOverlayView and
MyOwnButtonStyle import SwiftUI/Foundation and use local images/native controls.
MIT Barbara Martina Rodeker2021 full text verified. Select those isolated views first,
replace preview media and avoid WebView/StoreKit/Metal routes. Build a scoped native
shell later; do not classify touch/pressed styles as observed tvOS focus effects.

### 5. Swiftfin: source richness is real; cheap extraction is not established

Pin `81c0a2e0afec74414b928aa1371357eae6aaafd1` (main).
[PosterButton](https://github.com/jellyfin/Swiftfin/blob/81c0a2e0afec74414b928aa1371357eae6aaafd1/Shared/Components/PosterButton.swift),
[PosterImage](https://github.com/jellyfin/Swiftfin/blob/81c0a2e0afec74414b928aa1371357eae6aaafd1/Shared/Components/PosterImage.swift),
[dependency lock](https://github.com/jellyfin/Swiftfin/blob/81c0a2e0afec74414b928aa1371357eae6aaafd1/Swiftfin.xcodeproj/project.xcworkspace/xcshareddata/swiftpm/Package.resolved),
[license](https://github.com/jellyfin/Swiftfin/blob/81c0a2e0afec74414b928aa1371357eae6aaafd1/LICENSE.md).
PosterButton uses Poster protocol, environment viewContext, poster styles/context
menus, matched transitions, tvOS focusedValue and size tracking. PosterImage imports
BlurHashKit/Nuke, resolves sources through environment and uses placeholders/failure
paths. This is not a standalone Image/Button file. Replace network image sources and
server DTOs with deterministic local models without claiming unchanged app fidelity.

41 lock entries (direct + transitive, not 41 direct UI dependencies): BlurHashKit,
CocoaLumberjack, CollectionHStack, CollectionVGrid, CoreStore, Defaults, DifferenceKit,
Engine, Factory, Files, Get, jellyfin-sdk-swift, KeychainSwift, LNPopupController,
LNPopupUI, LNSwiftUIUtils, Mantis, MediaAccessibilityKit, MPVUI, Nuke, Pulse,
PulseLogHandler, StatefulMacro, SVGKit, swift-algorithms, argument-parser, atomics,
case-paths, collections, identified-collections, log, nio, nio-transport-services,
numerics, syntax, system, SwiftUI-Introspect, SwiftVLC, Transmission, TVOSPicker,
xctest-dynamic-overlay. Nested PreferencesView/SwiftfinMacros have their own manifests.
Playback/storage/macros/logging are avoidable costs for a shelf adapter; no automatic
dependency resolution or binary download. Full transitive licensing NOT cleared.

Root/file licenses are MPL2.0. A distribution plan must preserve notices and meet
covered-source obligations; this does not mean all unrelated NUIAK files must be
MPL. Server movie posters/logos/media do not become licensed by a code license.
Legal validity of third-party assets remains unresolved; use owned/generated content.

Useful discovered alternatives to importing the whole client:

- CollectionHStack pin5824801d31b67f89a125013d642cce7d284143c2 and CollectionVGrid
  pin7e4c4d8f20c8534cc5736e46f06265cd3686c944: Swift6 package tools, tvOS18/iOS18,
  MIT headers/licenses; each declares DifferenceKit1.3+. DifferenceKit's pinned
  license identifies Apache2.0. Inspect full selected dependency/license closure
  and renderer source before admission; no build performed.
- TVOSPicker pin90806460f3b3e7564344647241c157aeb0b27a71: Swift5.7 tools, tvOS13,
  no external package dependencies, Apache2.0 license identified. Candidate for a
  useful narrow picker, not proof of broad media-screen diversity.

These are follow-up candidates discovered from a real lockfile, not approved imports.

## Discovery indexes and datasets

[Awesome tvOS](https://github.com/mbcrump/awesome-tvos),
[Awesome iOS](https://github.com/vsouza/awesome-ios),
[Awesome SwiftUI](https://github.com/onmyway133/awesome-swiftui): discovery only.
Do not inherit a list's license or platform claims for linked packages. This spike
covers the named shortlist, not every link in those large indexes. Further searches
must fill a named coverage gap, avoiding endless repository collection.

[RICO](https://www.interactionmining.org/archive/rico): original page describes
Android screenshots, hierarchy and interaction data, with66k+screens. Not native
tvOS source or a focus-before/after label contract. No dataset license text was
located on the inspected landing page; require exact downloadable artifact terms,
privacy review, class mapping and duplicates/ancestry review. Hold import.

[Ferret-UI README](https://github.com/apple-aiml-research/ml-ferret/blob/main/ferretui/README.md)
documents research-only use and noncommercial dataset restrictions; released model
checkpoints/sample data are not a confirmed full AppleTV focus corpus.
[Ferret-UI2 paper](https://arxiv.org/abs/2410.18967) includes AppleTV in research but
does not itself qualify availability/rights/labels for this lane. Do not mix restricted
data into a potentially shipped model. Research-isolated investigation only if later
assigned. Neither dataset is presently ranked ahead of native source adapters.

## Independently dispatchable follow-ons (all low priority)

Common authority: NUIAK owns research/intake; TTR adapter changes require its own
assignment. Runtime build/install/capture must use current authorized target/context.
No new service, Git write, automatic downloads or production API/model changes.

### UI-IMPORT-A — Apple screen and SwiftUI-Kit component feasibility

Input: exact pins above, selected code/notice inventory, reviewed local artwork.
First qualify Apple MovieShelf+Hero+Description and one SwiftUI-Kit toggle/picker
group in isolated renderer targets. Freeze data instead of randomElement/Date.
Exclude network/map and proprietary logos. Budget one screen family and one control
group; stop dependency expansion and report the exact missing library/API if needed.
Test cold launch, offline asset resolution, stable IDs, focus callbacks, clipping,
enlargement, repeated seed determinism, changed theme and missing-asset failure.
Evidence: source/file hashes, notices, build logs, actual screenshots/overlays,
complete capture counts and successful existing NUIAK intake. Not just a preview.
Acceptance: same scene replayable with observed labels; no network dependency;
report software/data/integration/model outcomes separately. Next UI-IMPORT-D.

### UI-IMPORT-B — one custom parallax cell

Input: pinned ParallaxView/resources and notice inventory; accepted baseline adapter.
Integrate one cell using existing adapter interface, local art and known focus options.
Test focused/unfocused/pressed states, growth/glow distinction, clipping, settled
observations and failure on unknown geometry. Preserve physical-device qualification
as unavailable. Acceptance: bounded measured native pairs through existing intake,
not copied nominal rectangles. Next include this family in UI-IMPORT-D.

### UI-IMPORT-C — richer sources without whole-app coupling

Input: above Swiftfin dependency/source inventory and Catalog selected views.
First produce an exact minimal file/dependency/license closure for one Swiftfin shelf
OR independent CollectionHStack/TVOSPicker; select based on new coverage, not stars.
Keep model protocols local/offline and preserve MPL files/notices if chosen. Reject
any proposal requiring player/account/server stack just for static rendering.
Separately select two iOS Catalog styles/layouts not already in our generator; build
only in an iOS target and preserve current generator memberships.
Acceptance: closure and notices complete, no unresolved bundled media rights, isolated
offline build and one renderer/intake proof per selected platform. If closure remains
large, report no-go rather than ship a disguised partial import. Next UI-IMPORT-D.

### UI-IMPORT-D — source-diverse batch and utility decision

Inputs: accepted adapters, ART asset manifest, family/source ancestry and existing
evaluation protocol. Reserve source/layout/content groups before capture. Do not count
forks/recolors as independent apps. Create a bounded campaign covering simple/rich
layouts, focus-only/content-only/no-op/scroll cases, with one prepared runtime and
existing resume/intake tooling. Reuse exact geometry/crop validators.
Acceptance: all planned/rejected cases accounted for, deterministic offline tests,
native observation alignment, zero cross-role lineage leaks; one fixed data-only
comparison versus procedural baseline with retention gates and separate real-app
results. Candidate training logged under standing authority when selected, not now.
Scale only after useful coverage or measured model gain, not asset count alone.

## Poster-sheet pilot outcome

One built-in generation request, exact prompt in
`reports/work/UI-SOURCE-177/poster-sheet001-prompt.txt`.
Saved original at `reports/work/UI-SOURCE-177/artifacts/poster-sheet001.png`.
File SHA256 `4bcd52a7f65bd58c1b025f70415af2f6dffb016bd4b25da1aa4d1497742430f1`;
decoded RGB SHA256 `6e8fa3b03436e682d51e923cfc472c83968108ea88d153255c525e1b594829d7`.
Actual1672×941 RGB, not requested1920×1080. Twelve visually distinct panels present;
no visible text/UI focus decoration. Workplace comedy is photographic rather than
requested graphic style, orbital panel illustrative rather than strongly geometric.
Visual result useful for human review, not exact prompt compliance.

Critical finding: visible top padding is approximately37px, not the53px implied by
our largest centered exact2:3 grid at actual size (278×417cells, origin2,53).
Thus prompt geometry is not reliable enough for blind crop admission. No crops
extracted/admitted, no manual hidden recentering, no extra paid retry. ART-A remains
open. Proposed next workflow: accept/reject a versioned explicit per-cell rectangle
map after seam review, with intentional safe insets documented; or request larger/
fewer panels. Do not stretch cells to force aspect. User review decides visual
direction; automated geometry/hash checks still gate ingestion.

Generator model/version/seed/cost not exposed by tool: unknown, not invented.
Whole sheet is one development ancestry group. Local source/crop QA is not Fixture
import qualification, training eligibility or independent evaluation evidence.
