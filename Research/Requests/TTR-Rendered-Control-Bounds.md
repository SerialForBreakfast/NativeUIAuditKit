# TTR request: rendered control-body bounds for focus growth

Request ID: `nuiak-20261001-rendered-control-bounds`
Priority: high — blocks affected synthetic training admission.

**2026-10-01 consumer update:** image-card repair received and integrated under
SYN-06-BODY:231members verified,8scenes/21pairs,150body crops pass. Representative
native/custom growth overlays align by reviewer observation. Native button/row/dialog
bodies remain unavailable; selected tab parent stays distinct from focused artwork
child. Request remains open for those unsupported families and broader proof;
human/corpus admission is not implied. See `reports/work/SYN-06-BODY/handoff.md`.
Requested by maintainer,2026-09-30 PDT. Follow-up to
`nuiak-20261001-semantic-export-fixture-v1` and SYN-03 acceptance.

## Reproducible discrepancy

Delivery: `ttr-emitted-native-acceptance-20261001-r1.tar.gz`.
Member: `image/splits/validation/image/synth-0_unfocused.png`.
SHA-256: `382ac4c194c552bd28959b1e1c5781ed57311dcc9598b37e738ba6cb60a477f7`.
Adjacent `synth-0_metadata.json`, baseline scene, control `grid_cell_0_1`.
The filename's unfocused role concerns the pair target; this competitor is focused.

All four exported wrappers are440×420pixels. The focused second tile has bounds
`[824,280,440,420]`, yet its solid rendered body visibly extends past all four
edges of that rectangle. The user verified this with the native proposals displayed
in the annotator. This is enlargement, not just diffuse shadow/glow. Existing manual
annotations follow the enlarged visible control body on each frame.

Current contract honestly calls these measured view/layout rectangles, not effect
segmentation. Thus this is a missing geometry capability/consumer contract mismatch,
not evidence that the current exporter violates its stated wrapper semantics.

## Requested change

1. Export separately identified **rendered control-body bounds** in original-image,
   top-left pixels, accounting for the actual focus transform at capture. Include
   solid-body enlargement; exclude diffuse shadows/glow and unrelated external
   captions. Rounded controls still use an axis-aligned enclosing rectangle.
2. Preserve existing wrapper/layout and artwork-content geometry. Do not silently
   change old fields or relabel layout bounds as rendered bounds. Propose exact
   additive/versioned fields, geometry-source identity and capability availability.
3. Determine whether native presentation/view geometry can expose the transformed
   body reliably, including UIKit-managed internal focus effects. Do not guess a
   fixed scale, copy recipe intent, or substitute OCR/vision estimates as native
   truth. If unavailable for a renderer, explicitly export unavailable/reason.
4. Bind rendered geometry to the same scene/generation/image and capture brackets;
   retain full versus clipped visible bounds and coordinate conventions. Settling
   must cover presentation geometry, not merely requested focus identity. Flag
   unsupported perspective/animation cases rather than silently using layout bounds.

## Acceptance and delivery

- Real growth-on pair: same control's body box changes with visible size and aligns
  with the image. Supply full-frame overlays and raw before/after geometry.
- No-growth control: stable geometry remains valid; do not force all focus to grow.
- Selected-but-unfocused parent stays distinct from focused child.
- Verify clipping and non-square controls; negative tests cover stale geometry,
  wrong identity, invalid/out-of-frame coordinates and unavailable measurements.
- Provide a small representative corrected versioned bundle and source/runtime
  identities through the existing receipt flow. Keep prior originals unchanged.
  Reuse retained evidence where valid; no recapture solely for a new filename.
- NUIAK will map the explicit rendered-body role into annotation proposals, keep
  provenance, and rerun image-overlay and production16%-expanded256×256crop QA.
  We will not silently change production preprocessing or existing reviewed labels.

Do not ask the human to repair an entire synthetic corpus. A small human spot-check
should verify the exporter, not compensate for systematically wrong geometry.

## Correction to prior acceptance

SYN-03's5pair intake and60/60crop-generation checks still prove schema/hash/crop
execution, **not visual body-bound alignment or training eligibility**. Affected
growth samples remain diagnostic-only and held from training pending this repair.
Do not generalize that all non-growing controls are wrong. No model has changed.
This request authorizes coordination; runtime trials follow TTR's own authorized
scope. Please acknowledge this ID and return feasibility, concrete schema and a
bounded proof plan before claiming the production corpus is ready.
