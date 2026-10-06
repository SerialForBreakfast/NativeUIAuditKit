# ADR-0020 — test prompt-rendered UI against deterministic focus composition

Date: October 5, 2026 (Pacific). Status: approved bounded worker spike;
feasibility results pending. No training admission or native parity established.
Priority refinement: this is now a stretch/nonblocking spike behind
[artwork-backed native delivery](Plans/ArtworkModelImprovement204.md). Its published
bounded request remains valid; local planning does not cancel or interrupt peer work.
Related: [ADR-0019](ADR-0019-Batched-Renderer-and-Asset-Pipeline.md),
[RENDER-202](../reports/work/RENDER-202/handoff.md).

## Question and decision

Can Big Dog produce repeatable, configurable, fully annotated UI frames from Swift-like
descriptions and rules, without the Apple rendering stack? Test two approaches on the
same explicit scenes, not on unrelated attractive examples:

1. **Prompt-only:** describe the layout, coordinates and focus state, including a compact
   SwiftUI-like declaration, to the installed text-to-image model. Requested geometry
   is a hypothesis, not an annotation. Independently review actual visible elements.
2. **Deterministic compositor:** reuse generated artwork, rasterize controls and effects
   from a small typed scene graph, and export geometry/masks from the actual draw commands.
   These are trustworthy procedural labels when raster alignment passes, not native labels.

Prefer option2 as the engineering hypothesis; retain option1 as a falsifiable experiment.
Do not invest in arbitrary Swift parsing, a new rendering framework, diffusion training
or a new model download for this test. Big Dog uses its existing approved environment.
An independently assigned worker may implement the tiny renderer in its own checkout.

## Why Swift text is not a renderer

A text-to-image model does not execute SwiftUI layout, font metrics, clipping or the
tvOS focus engine. Even a syntactically correct view description does not establish
the final pixels or boxes. Native Swift source also depends on runtime environment,
safe areas, dynamic type and view state; source inspection alone cannot label its raster.
Convert selected declarative concepts into an explicit restricted scene graph instead
of pretending arbitrary `.swift` files can be faithfully interpreted by diffusion.

The installed SDXL-Lightning model uses a fixed few-step pipeline; its model card gives
matching checkpoint/scheduler settings, not a bounding-box compliance guarantee.
[Primary source](https://huggingface.co/ByteDance/SDXL-Lightning).
ControlNet demonstrates spatially conditioned generation, but that requires a compatible
additional model/configuration and still needs output validation. It is a possible
later arm, not assumed installed or authorized here.
[Primary source](https://github.com/lllyasviel/ControlNet).

## Frozen experiment: FOCUS-RENDER-203

Canvas1024×576, integer top-left pixels. Three layouts with two content seeds203001
and203002. Layout has stable IDs, explicit class, z-order, artwork hash, clip rectangle,
font identity/size where used, and role-labelled geometry. Six independent *scene
configurations*, not six independent evaluation families. Related assets and all
derivatives stay development-only and out of final evaluation.

Layouts (x,y,width,height):
- poster shelf: A(96,160,160,240), B(304,160,160,240), C(512,160,160,240).
- settings-like list: A(160,120,704,72), B(160,220,704,72), C(160,320,704,72).
- dialog: body(192,112,640,352), A(256,340,208,64), B(560,340,208,64).

Four states per scene: reference/no focus, focusA, focusB, and content-only change
while A remains focused. Compare reference→A, A→B and A→content-change. The latter
must change artwork inside B (or a labelled decorative patch for rows/dialog), not
focus/geometry. No invented all-unfocused native-screen claim: it is a procedural state.

Primary samples:24frames per arm. Repeat two fixed outputs per arm unchanged once,
giving26per arm/52total. Log exact PRNG algorithm, model RNG/backend, seeds, software,
model/asset/font hashes and settings. Repeats measure same-host determinism; same seed
does not promise cross-hardware bit identity. Freeze prompts before running; no cherry
picking, retries for appearance, threshold tuning or silent missing-cell omission.

### Effect profiles — synthetic, not calibrated tvOS constants

- Shelf: uniform center-pivot scale1.10, 3px white outline, shadow offset(0,6),
  blur radius8, opacity0.35. Fixed z-order: focused item above siblings.
- List: scale1.03, white rounded background, dark text, no external ring;
  corner radius12. Bright unselected content remains possible.
- Dialog: scale1.06, 3px white outline, shadow as shelf; body remains unchanged.

Reference scale1.0; highlight alpha0. All values, interpolation policy and clipping
must be configuration, not hidden code. Freeze these profiles for the initial matrix.
Do not call them Apple's exact growth/glow/parallax. Animated settling, perspective,
parallax and material/shader fidelity are out of scope; return those as native gaps.

Annotation convention: original layout rect; transformed control-body rect; clipped
visible body bounds; independent body mask; separate ring/shadow/effect extent. For
scale s about center c, x'=cx-s*w/2, y'=cy-s*h/2, w'=s*w,h'=s*h. Raster rounding is
recorded. Do not inflate body annotations to include shadows. Textured asset edges
do not redefine the enclosing control. Alpha/masks come from composition, not guessed
from artwork. Image hashes bind every record; unsupported classes remain unsupported.

### Prompt-only template

"Render a flat front-facing fictional television UI screenshot, exactly1024by576,
no perspective or device frame. Background dark neutral. Declarative layout:
{Swift-like ZStack and frame/position declarations generated from frozen scene graph}.
Top-left pixel rectangles: {IDs and rectangles}. Current state: {state}.
Only {focusedID or none} has {complete effect profile}; all other controls retain
their size and styling. Preserve exactly {N} controls. No extra buttons, no painted
coordinate labels. Artwork theme {seed-bound description}."

Include transformed target body rectangles explicitly for focus states. Use the same
model seed for a scene's state variants to attempt content continuity; do not assume
it succeeds. Save exact prompts and generated images. Prompt-only cannot claim exact
reuse of a particular artwork hash without an actual image-conditioning mechanism.
Record this mismatch when comparing arms, rather than claiming perfect paired control.

## Measurement and acceptance

- Account for all planned frames, failed cases, repeats, duration, peak memory and bytes.
- Compositor: independently test formula results and raster masks within1pixel after
  declared rounding; identity state, clipping, overlap/z-order and degenerate geometry
  negative cases. Same-pinned-environment repeats should have identical decoded pixels.
  Compare before/after pixels outside the declared effect/content-change union: zero
  unexpected differences for this static deterministic arm.
- Prompt-only: independent reviewer marks actual visible control-body boxes and focus
  ID, absent/extra/ambiguous elements. Do not use requested boxes, NUIAK predictions or
  the generator's own prose as observed truth. Unreviewed samples get unavailable metrics.
  Report per-element IoU, center/edge error, expected-count agreement, correct-focus rate
  and outside-target pixel drift with denominators and abstentions. Rendering quality
  and annotation alignment are distinct. Human refinement of review boxes stays possible.
- Exploratory screen: target IoU>=0.90 for each unambiguous body and correct focused-ID
  for all primary focus states; report every failure. This is not a training or native
  gate. Passing six scene configurations cannot establish general annotation reliability.
- Report achieved, not theoretical, accepted annotated pairs/hour and review effort.
  Comparing these runtimes with native capture needs matching output/evidence scope.

Decision: if prompt-only misses geometry/state continuity, restrict it to artwork and
references. If compositor meets raster invariants, consider a separately reviewed
procedural augmentation corpus; it still needs matched native transfer evaluation.
If neither passes, preserve evidence and diagnose; do not scale or retrain automatically.

## Execution, transfer and next step

Worker budget: one finite run, up to2GPU hours,2CPU hours,1GiB outputs,26diffusion calls
maximum. No installation/download, paid API, extra server, Apple runtime, real-device
operation, detector training or model promotion. Reuse original24artwork pixels;
flagged assets may be explicit diagnostic challenges, never silently clean-admitted.
Do not interrupt another job. OOM/unsupported resolution is a reported case, not
authority to download alternatives or change the frozen matrix.

Return compact metrics, review overlays/contact sheets, source/config/test evidence
and exact original PNGs through one regular-file-only immutable SMB archive capped
at128MiB compressed/256MiB expanded; if larger, report inventory before transfer.
Sender retains originals; exact size/hash receipt precedes cleanup. Artwork review,
procedural label integrity, native fidelity and model utility are independent outcomes.

No local rendering implementation or images produced by this ADR. Big Dog execution
is requested; NUIAK independently reviews its results. Next, if procedural invariants
pass, compare matched procedural/native scenes and evaluate a bounded augmentation
experiment without changing final holdouts or promoting on synthetic scores alone.
