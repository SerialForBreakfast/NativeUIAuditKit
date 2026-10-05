# Generated media artwork library

Planning date: 2026-10-05. Low-priority, opportunistic work; Tasks.md owns status.
Ownership update ART-HANDOFF178: producer generation/prompts/crop-import/rendering
is proposed for TTR ownership at maintainer request; acknowledgment pending. Earlier
NUIAK producer assignments below are retained design context, not local dispatch.
NUIAK keeps consumer admission/validation/splits/evaluation. See
[minimal transfer memo](../../reports/work/UI-SOURCE-177/ttr-minimal-handoff.md).
Pilot update: [UI-SOURCE177](UIComponentIntake.md#poster-sheet-pilot-outcome) executed
one requested review sheet. It is visually useful but not crop-qualified: actual
dimensions and visible padding differ from the prompt. ART-A remains open; validate
explicit rectangles against actual seams before any extraction/admission.
This assignment creates the plan, not images, paid jobs, captures or training.
Use existing image-generation tooling/skill when a generation packet is dispatched.
Do not displace model evaluation, qualified data intake or producer unblock work.

## Goal and boundary

Produce reusable fictional posters, episode thumbnails, backdrops and avatars for
realistic native media screens. Generated artwork adds semantic/texture diversity
that flat colors and procedural shapes do not readily supply. It complements those
cheap, controllable assets; it is not proven to improve model quality yet.

Generate artwork only. Fixture renders navigation, titles, synopsis text, buttons,
focus effects, shadows and clipping using native controls and measured telemetry.
Do not generate a finished screen and treat painted buttons or painted focus as
ground truth. Fake show/detail pages are deterministic Fixture compositions of
artwork plus local metadata, not image-generated screenshots or new UI classes.
No Jellyfin import, brand imitation, recognizable franchise, celebrity likeness,
real account content, external fetch or producer-repository modification is included.

## ART-A — freeze catalog, geometry and tiny crop/import contract

Owner: NUIAK. Inputs: existing artwork contracts, this plan, current TTR source.
Implementation: inspect actual artwork import/path/format limits read-only, select
one supported role, create the versioned manifest and planning-only catalog, and
implement one deterministic sheet slicer/validator using resident image tooling.
Do not invent a TTR API; missing import capability is a scoped producer proposal.
Cropping is an explicitly requested mechanical asset operation, not generative
image editing. It is unrelated to FocusRing's production 16%/256px inference crop.

Planning canvas is **1920×1080**, not an assertion that a generator outputs it.
Check actual provider dimensions before spending a request. For any returned W×H,
calculate the largest centered exact-aspect integer-cell grid that fits; persist
the resolved rectangles before extraction. No guessing from a resized preview,
anisotropic resizing, invented exact resolution or automatic super-resolution.

| Role | Grid | Cell pixels on 1920×1080 | Outer padding | Assets/request | Intended use |
|---|---|---|---|---:|---|
| Poster, 2:3 | 6 columns × 2 rows | 320×480 | top/bottom 60 | 12 | Default shelf artwork |
| Poster, compact 2:3 | 8×3 | 240×360 | none | 24 | Optional after pilot; smaller detail budget |
| Episode/landscape, 16:9 | 4×4 | 480×270 | none | 16 | Cards and episode rows |
| Landscape, higher detail | 3×3 | 640×360 | none | 9 | Alternative, not an additional quota |
| Avatar, square | 8×4 | 240×240 | top/bottom 60 | 32 | Profiles; native UI supplies circular mask |
| Hero/backdrop, 16:9 | 1×1 | 1920×1080 | none | 1 | Full-screen/detail background |

Examples for the default canvas: poster(row,col) = (320col,60+480row,320,480);
thumbnail = (480col,270row,480,270); avatar = (240col,60+240row,240,240).
Row/column indexing starts at zero, top left; rectangles are half-open integer
pixel bounds. These are asset crop rectangles, never training annotation boxes.
For aspect p:q and C×R grid, k=floor(min(W/(C p),H/(R q))), cell=(kp,kq),
center the grid with integer floor offsets and record any one-pixel padding asymmetry.

The prompt asks for exact panels, but a generated grid is not mechanically reliable.
Accept only after every cell is checked for seam crossing, cut-off subjects and
wrong composition. Rejected cells remain rejected; no automatic recentering or
content-based cropping that changes the declared mapping. A contact sheet should
be displayed once for review, not dozens of redundant full-resolution images.

Manifest `generated-media-assets-v1` fields:

- library/sheet/asset IDs; source PNG SHA-256, decoded-pixel hash, actual dimensions;
- generator/provider/model/version as reported (unknown if absent), UTC, request ID,
  exact prompt and prompt hash, parameters/seed if supported (never invented);
- columns/rows, aspect, each [x,y,width,height], original cell index, output hash,
  genre/style/composition labels, intended role, inspection result and rejection reason;
- common `ancestryGroup` for the entire sheet and all crops/variants/retries/derivatives;
  franchise/content-family links where characters/artwork recur across sheets;
- preassigned training/development/reserved role, rights/provenance limitations,
  retention source and reported cost/time, with unknown cost recorded as unknown.

Output is opaque RGB PNG, orientation normalized, defined sRGB conversion recorded;
retain original provider file. No baked circular masks, rounded corners or selection
borders. Use safe IDs such as poster-sheet001-r00-c00, never titles as filesystem paths.
Use verified USB bulk storage under `/Volumes/training-drive/data/NUIAK/generated-media/`
with original/sheets, derived/assets and manifests; never create an unmounted lookalike.
Compact plans/prompts/receipts stay local. No raw rasters in Git or metadata-only SMB.

Tests: exact crop hashes on a synthetic coordinate-colored sheet; non-1920 dimensions;
odd padding, unsupported aspect, out-of-bounds/overlapping rectangles, duplicate IDs,
corrupt PNG, missing source/hash, output collision, role/ancestry leakage. Wire the
actual importer when supported; otherwise deliver an explicit unsupported contract.
Acceptance: deterministic real CLI, self-contained tests, required offline Swift
checks after code changes, no lossy stretching, no silent missing cells. Next ART-B.

## ART-B — small generated pilot, inspect before expansion

Owner: NUIAK generation worker. Depends on ART-A; record budget before execution.
Initial ceiling: **7 requests**, yielding at most **64 accepted assets**:
12 posters + 16 episode thumbnails + 32 avatars + 4 individually generated backdrops.
These are inventory targets, not guaranteed yield; no automatic retry on failed cells.
One sheet/request is a resumable unit. Review first poster sheet before spending the
rest. If precise grids fail, compare fewer/larger panels or individual generation;
report accepted assets/request and human review time before changing the budget.

Pilot is development-only, including all related variants. Use four fictional
show metadata records to demonstrate compositions; generate names/synopses as text,
with no network content. Do not require identity-consistent characters across sheets
unless separately tested; semantic plausibility is sufficient for this pilot.

Coverage is a designed mixture, not an estimate of real app prevalence:
animation/family adventure, drama, comedy, non-graphic horror, science fiction,
documentary/nature. Vary bright/dark, warm/cool, low/high contrast, faces/no faces,
simple/busy, photographic/illustrated/graphic styles and subject placement.
Include varied fictional adult skin tones, ages and presentation in portrait assets.
Keep extreme stress artwork separately tagged from plausible entertainment art.
Balance bright artwork in focused AND unfocused states later; no label-specific assets.

Acceptance: every cell accepted/rejected with reason; manifest and hashes valid;
all source sheets retained; one compact visual review per sheet plus flagged cells;
actual time/cost/yield reported. No training benefit or independent holdout claim.
Next: ART-C pilot import, not automatic bulk generation.

## Reusable generation prompts

Replace bracketed fields from the frozen catalog; save the full expanded prompt.
Do not put UI instructions, bounding-box labels or cell numbers inside artwork.
Generator layout errors are caught by ART-A/B, not assumed away by strong wording.

### Poster sheet (default, 12 cells)

> Create an original fictional entertainment-art contact sheet on a landscape canvas,
> requested size 1920 by 1080. The centered artwork region is six columns by two rows
> of equal 2:3 portrait panels; at the requested size each is 320 by 480 pixels with
> 60 pixels of neutral gray padding above and below, no internal gutters. Each panel
> is its own complete edge-to-edge composition. No object, face, lettering or artwork
> crosses a panel boundary. No divider strokes, frames, shadows, rounded corners,
> screen UI, focus glow, watermark, existing logo or recognizable franchise.
> No lettering; titles will be rendered separately. Twelve clearly different original
> fictional movie/series artworks in row-major order: [CELL_BRIEFS]. Use convincing
> entertainment-poster composition, a deliberate mix of realistic photography,
> illustration and graphic design as specified. Keep key subjects safely inside their
> own panel. No graphic violence or sexual content. Diversity in palette, brightness,
> visual complexity and subject position is important; do not repeat one template.

Pilot CELL_BRIEFS, row-major:
1. warm hand-painted woodland adventure; 2. cool photographic adult family drama;
3. bright graphic workplace comedy; 4. dark non-graphic haunted lighthouse;
5. luminous science-fiction desert observatory; 6. quiet nature documentary coast;
7. cool stylized underwater animation; 8. warm intimate stage-performer drama;
9. dark deadpan illustrated mystery comedy; 10. pale foggy suspense mansion;
11. bold geometric orbital exploration; 12. saturated macro botanical documentary.

### Episode/landscape sheet (16 cells)

> Create sixteen distinct original fictional episode-still artworks in an exact
> four-column, four-row edge-to-edge grid, requested total 1920 by 1080. Every panel
> is 16:9, 480 by 270 at that size. No gutters, borders, text, timecodes, logos,
> playback controls or selection decoration. Nothing spans panels. Use [CELL_BRIEFS]
> in row-major order. Mix close-up, medium and wide compositions, interiors and
> exteriors, people and scenery, light and dark scenes, plausible photographic and
> explicitly illustrated content. All characters and productions are fictional.
> Preserve a complete readable composition within each rectangle. No graphic violence.

Catalog briefs are the Cartesian sample of four genres (animation, drama, comedy,
suspense) and four scene types (interior conversation, exterior journey, object/detail,
wide establishing shot), assigned varied palettes rather than one palette per genre.

### Avatar sheet (32 cells)

> Create an exact eight-column by four-row grid of thirty-two different square profile
> artworks, requested canvas 1920 by 1080. At that size panels are 240 by 240 with
> neutral gray 60-pixel top and bottom padding. No gutters, labels, circle masks,
> rings, badges, shadows or UI. Each subject stays inside its square. Row one:
> eight fictional adult portraits with varied age, skin tone and gender presentation.
> Row two: eight distinct illustrated animals. Row three: eight abstract geometric
> identities. Row four: eight playful original robots or fantasy creatures. Vary
> palette and brightness within every row. No real people or recognizable characters.
> Keep face/identity details legible at small display sizes and retain square artwork.

### Individual background (one each)

> Create one original fictional [GENRE] entertainment backdrop, landscape 16:9,
> requested 1920 by 1080. Scene: [SCENE]. Palette: [PALETTE]. Complexity: [LEVEL].
> Composition: [SUBJECT_POSITION]. No text, logo, controls, panels, borders or focus
> effects. Use believable visual depth and lighting. All subjects are fictional.
> [TEXT_SAFE_REGION] has lower visual detail but is not an empty painted UI rectangle.

Pilot: warm animated hillside village / cool dramatic city dusk / bright comic
coastal cafe / dark non-graphic science-fiction station. Alternate text-safe left
and right; do not make one subject position correlate with future focus position.
Full-screen backdrops are single images because four 960×540 crops cannot provide
the same source detail. No claim that upscaling restores missing detail.

### Text-only show metadata prompt

> Produce strict JSON containing four wholly fictional shows. For each return stable
> ID, invented title, genre, short synopsis, three invented episode titles/descriptions,
> and references ONLY to the supplied accepted asset IDs: [ASSET_IDS]. No URLs,
> real franchises, ratings claims or personal data. Titles under 50 characters,
> synopsis under 240; episode descriptions under 140. Do not invent asset IDs.

Validate JSON/schema/references. Fixture controls line wrapping and localization
tests; generated typography is not a rendering-quality claim. Add native-rendered
title overlays later as a separate variation, keeping clean underlying assets.

## ART-C — one native media composition and controlled pilot

### Complexity and detail coverage

Use fictional streaming/video-app compositions inspired by common interface patterns,
not pixel-for-pixel YouTube/Paramount replicas or claims of their measured fidelity.
Build the following coverage incrementally; the first two screens are a pilot, not
completion of this matrix:

| Screen family | Competing visual evidence | Native components/observations needed |
|---|---|---|
| Media home | Full-bleed hero art, colorful gradient/scrim, multiple poster shelves | Header/sidebar, shelf title, selected tab distinct from focus, clipped adjacent cards |
| Video browsing/search | Dense landscape thumbnails, faces, busy baked thumbnail lettering | Search field, channel avatar, title/metadata, native duration/live badges, filter chips |
| Show/episode detail | Large backdrop, logo-like native title, synopsis, episode imagery | Primary/secondary buttons, tabs, episode rows, progress indicators |
| Playback overlay | Moving imagery beneath translucent panels, bright highlights | Timeline/thumb, transport buttons, subtitles, speed/audio menu, settling evidence |
| Profile/account chooser | Colorful avatars and strong selected-state decoration | Native circle masks, labels, edit action, selected-but-unfocused state |
| Dialog over media | Dimmed but visually busy underlying screen | Modal buttons, stacked hierarchy, native focus, noninteractive backdrop |

Cheap **native/procedural** controls should provide gradients, scrims, text, badges,
progress bars, masks, borders and layout. Reserve costly generation for semantic
imagery: faces, artwork, photographic scenes, rich illustration. Thumbnail-like text
can be composited deterministically into the asset later as a declared derivative;
it is picture content, not a new actionable control or OCR ground truth from the model.
Add local-only fictional channel identities and distinct plain app logos through
native/vector drawing rather than spending an image request per icon.

Vary brightness, saturation, contrast and visual detail independently from focus.
Include bright edges inside artwork that resemble focus rings, dark focused controls,
small white text against busy backgrounds, similar adjacent posters, colorful
unfocused neighbors and focus growth against tight spacing. Do not bake actual
selection effects into the generated source. Some dramatic stress variants may be
unrealistic; tag them separately and retain a plausible baseline.

Separate these transition populations explicitly: focus-only change; stationary
focus plus changing background; scrolling with/without focus identity change;
overlay appearance; loading-to-artwork replacement; stable no-op. A still artwork
library cannot establish temporal realism. Use existing supported deterministic
crossfades/pans or native animation only when observation binding is qualified;
actual video acquisition/generation is outside this asset budget.

**Resolution gate:** for each layout record source cell size, largest rendered
pixel rectangle (including native focus enlargement), fit/fill transform and final
model-input size. Prefer source dimensions at least as large as the sampled display
region; explicitly flag upscaling instead of claiming high detail. A320×480poster
is appropriate only where the display budget supports it. Detail-page hero imagery
uses individual higher-resolution generation; thumbnails shown larger than480×270
use the9-cell or individual option. Requests may return other sizes; actual dimensions
govern. Review both full-resolution composition and exact inference-resolution view:
beautiful1920×1080art can disappear when the model downsamples the screen.

### Token-efficient generation and Fixture handoff

Keep one reusable base prompt per role plus a short row-major cell-brief list. Supply
only the selected sheet's briefs, not the entire corpus or repository history. Record
the expanded prompt once; later handoffs reference its hash. Start with one contact
sheet review and flagged crops; do not repeatedly send unchanged full-size images.
No promised token savings without measurement. Record request count, actual image
dimensions, available usage/cost and review effort; visual tokens depend on provider.

The Fixture handoff has two small machine-readable files: the asset manifest defined
above and a source-versioned scene binding mapping supported recipe fields to asset
IDs, fit modes and metadata IDs. Fixture resolves IDs to validated local files beneath
one approved asset root; reject traversal, links escaping the root, unknown IDs,
missing hashes, oversized decode budgets and unsupported fields before mutation.
Do not embed base64 images or long prompts in recipes/status. Import raw artwork
once, cache by content hash and reuse across scenes. Preserve placeholder tests as
explicit cases; a silent placeholder cannot count as successful asset import.

Acceptance includes deterministic mapping of each cropped asset into its intended
native element, no cross-cell bleed, bounded decode/cache memory, correct fit/fill
and focus enlargement, and reproduction using only the frozen catalog/local files.
NUIAK owns the proposed interchange; verify TTR's real supported fields before
calling it an implemented importer. Missing support gets one bounded producer task,
not another capture/transport stack. Send only the relevant API gap when selected.

Ownership: TTR implements any missing asset adapter under its own assignment;
NUIAK owns catalog/export review and intake. Input: accepted ART-B library and
source-pinned supported import contract. A proposal is not a producer edit authority.
Publish a low-priority request only when this packet is selected, reusing the
existing artwork/semantic request; no duplicate coordinator or import service.

Compose one media browsing screen and one detail/episode screen using existing
native Fixture capabilities: header/sidebar, multiple shelves, posters/landscape
cards, native text, backdrop and avatar. If missing, report supported subset and
exact API gap. Keep asset fit mode (aspect-fit/fill), clipping, placeholder/loading
state and source IDs explicit. Use local assets only, bounded decoded image memory
and cached decoding; oversized files fail before rendering. Verify rendered content
uses the requested hash, not a default or silent placeholder.

Capture only when runtime/scope is assigned. Use existing jobs, observed focus and
before/after geometry. Compare the same controls/transitions under procedural versus
generated artwork without changing geometry; separately compare simple versus rich
layout, because these are different hypotheses. Include no-op/content-only changes,
bright unfocused artwork and selected-but-unfocused parents. Preserve seed/asset
and scene lineage. Background changes must not become accidental focus labels.

Acceptance: genuine import/render/intake proof, focus and annotation validation,
complete accounting, matched baseline diagnostics and memory/timing evidence.
Report resemblance qualitatively; no Jellyfin fidelity or real-world accuracy claim.
Next ART-D only if assets work and reveal useful coverage, not merely look attractive.

## ART-D — incremental library expansion and utility evaluation

Provisional full-library ceiling: 96 posters (8 sheets), 128 thumbnails (8 sheets),
128 avatars (4 sheets), 16 backdrops (16 requests): **368 assets / 36 requests total**,
including pilot. Counts assume zero rejects; not a minimum to train or a mandate
to exhaust generation. Extra retries require a revised recorded request budget.
No dollar estimate without current provider/account pricing; no paid API assumption.

Select one catalogued sheet per spare tranche, not automatic recurring jobs. Stop
at the packet budget, leave failures visible, and continue other approved work.
Before expansion, assign whole sheet/content-family connected groups to roles.
Pilot stays development. Reserve new asset families AND layout families before
failure-driven selection; generated-asset holdout is not independent real-app evidence.
Near-duplicate checks supplement exact hashes; never treat cosmetic variants as new
independent samples. Do not break related focus pairs to inflate diversity.

Run one separately logged data-only comparison with fixed model/budget/splits and
procedural baseline. Measure focus localization, wrong/no-focus decisions, nuisance
false changes and retention by layout/style; reviewed external screens stay separate.
Record assets accepted/request, generation/review/import time, GPU/CPU memory and
accepted useful training examples/hour. More assets do not imply better performance.
Gate further spending on a useful matched result or a clearly diagnosed coverage gap.

## Reporting and efficient handoff

Each packet carries manifest/version, exact hashes, accepted/rejected inventory,
tests and observed runtime results. Report software verified, data eligible,
integration qualified and model gates separately. Artwork acceptance is not capture
label verification or training admission. Reuse unchanged evidence, run full offline
checks once per integrated code change, and retain one concise tranche handoff.
Local asset generation has no SMB status requirement. Publish only a concrete TTR
import/interface request or qualified intake result; artifact transfers use receipts.
