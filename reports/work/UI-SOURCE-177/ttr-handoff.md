# ART-HANDOFF-178 — proposed producer ownership

Maintainer requested2026-10-05: send the generated poster sheet and transfer artwork
generation/UI collection considerations to TTR for future best practices. Low priority;
do not displace current source publication, compatibility or capture repairs.

## Proposed scope split (please acknowledge/adapt under TTR instructions)

TTR owns: artwork catalog/generation practice, prompts and generation budgets;
deterministic slicing/import/caching; native scene adapters and third-party code/asset
license review; theming/layout/animation/observed focus/visible geometry; producer
recipes and capture/export. Adopt or consolidate ART producer work and UI-IMPORT
adapter work into TTR's queue; do not create a second NUIAK renderer or asset service.

NUIAK owns: consumer schemas and validation, crop/preprocessing parity, training
admission, source/asset/journey split constraints, evaluation, model experiments and
quality/promotion decisions. Jointly agree only the asset/recipe provenance and
measured-label contract. Producer compatibility is not automatic data admission.

## Included snapshot

- poster-sheet001.png: original single built-in generation output, twelve fictional
  artworks; user says visual direction looks good. Review-only, not training data.
- poster-sheet001-prompt.txt: exact expanded prompt; no private reference images.
- GeneratedMediaAssets.md: prompts, sheet geometry/budgets, rich-screen requirements,
  proposed manifest, lineage and QA. Planning recommendations, not TTR API claims.
- UIComponentIntake.md: source-pinned code/dependency/license spike and adapter ranking.
- DiverseNativeUICorpus.md: source/layout ancestry and broader corpus contract.
- This document: ownership proposal and requested response.

Links inside copied plans refer to the NUIAK source tree and may not resolve in this
flat snapshot. External source URLs/pins are preserved. Snapshot plans carry earlier
NUIAK ownership wording; this handoff explicitly proposes relocating producer work.
No Apple archive, upstream source, weights, captures, credentials or personal data
included. No new generation, source installation, capture or training requested now.

## Concrete image lesson for TTR best practices

Requested1920×1080, returned1672×941RGB. PNG SHA256
4bcd52a7f65bd58c1b025f70415af2f6dffb016bd4b25da1aa4d1497742430f1.
Six columns/two rows are visible, but top padding is approximately37px rather than
the53px prescribed by the actual-size exact2:3grid (278×417cells, offset2,53).
No crops extracted or accepted. Do not blindly trust prompt dimensions or grid seams;
review explicit per-cell rectangles, reject bleed and avoid anisotropic stretching.
Some style briefs were only approximate. Generator model/seed/cost are unknown.
Preserve original sheet/prompt, hashes, derived crop mapping and one ancestry group.
Keep generated art separate from native controls, focus effects and annotation truth.
Use procedural/native gradients, text, badges and geometry; reserve generation for
semantic art. Render-size and model-input-size detail both matter. Scene composition
and animation remain distinct coverage from artwork diversity.

## Requested response

1. Verify/copy bundle and publish exact size/hash receiver receipt; no deletion by age.
2. Acknowledge ownership proposal, give TTR task IDs or reasons for scope changes.
3. Incorporate the observed sheet-geometry failure into future asset workflow guidance.
4. Rank Apple media sample, SwiftUI-Kit, ParallaxView then richer isolated adapters;
   use the detailed spike rather than redoing discovery or importing whole Swiftfin.
5. State the actual supported local asset interface and any consumer contract needs.

No live proof, model gain or source-license clearance is implied. NUIAK retains the
original and only cleans its exact SMB copy after a matching verified receiver receipt.
