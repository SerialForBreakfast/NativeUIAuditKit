# Simulator expansion: native-label visual review

Reviewer: NUIAK agent, 2026-09-27 local / 2026-09-28 UTC. This is agent visual
QA of independently observed Fixture labels under the maintainer's explicit
Simulator training-data assignment, not human Photos annotation.

Reviewed all 13 numbered sheets and all 104 production crops. Inventory:
`review-sheets/inventory.json`, seal
`e187576a08c5ab1af7e310b1feb7e9a251b12397b1d6312bb7487c6e805eb7e9`.
Numbers below use this inventory (not the older smoke report's numbering).
Every listed corpus contains exactly `synth-0` through `synth-3`. Exact frame,
crop and manifest hashes, per-frame bounds and control IDs are in the inventory.

| Numbers | Corpus suffix | Reviewer observation | Visual disposition |
|---|---|---|---|
| 001–004 | dev-01-bright | Cream/yellow artwork in both states; focused white outline. | accept 4 |
| 005–008 | dev-01-dock | Landscape imagery, white outline/blue glow only when focused. | accept 4 |
| 009–012 | dev-01-smoke | Colored artwork, thin white focused outline. | accept 4 |
| 013–016 | expansion-r01 | New seed's colored stripes/moons; focused white outline. | accept 4 |
| 017–020 | expansion-r03 | Bright cream/yellow stripes/moons; brightness alone is not focus. | accept 4 |
| 021–024 | expansion-r05 | Gray placeholder with dash; focused white outline. | accept 4 |
| 025–028 | expansion-r07 | Blank gray placeholder; focused white outline. | accept 4 |
| 029–032 | expansion-r09 | Yellow/black artwork in both states; added outer yellow rim/glow distinguishes focus. | accept 4 |
| 033–036 | expansion-r11 | Landscape icons in grid; focused white outline/blue glow. | accept 4 |
| 037–040 | expansion-r13 | Media shelf with colored moons; thin focused outline, neighboring cards retained. | accept 4 |
| 041–044 | expansion-r14 | Bright cream/yellow media cards; thin focused outline. | accept 4 |
| 045–048 | expansion-r15 | Gray media placeholders/dashes; focused white outline. | accept 4 |
| 049–052 | expansion-r16 | Landscape media cards; focused outline and blue glow. | accept 4 |

All intended controls are present and fully retained in their crops; no black or
empty target crops. Neighbors and Fixture chrome sometimes enter the expanded
crop; that is preserved production context, not an annotation of all controls.
Media cards are aspect-stretched by the existing 256×256 production path; no
new preprocessing is introduced. Each state's measured geometry is retained.
The native v2 brackets, not these visual observations or remote-button intent,
provide the labels. Baseline Reference-frame focus is outside the paired target
set; these examples do not establish complete-screen unique-selection accuracy.

Visual acceptance does not bypass hash, duplicate, overlap or lineage admission.
52 pairs have 104 frame files, 65 distinct frame pixels and 102 distinct crop
pixels. The extension assembly must account for every pair and all exact pixel
duplicates separately. The failed nine-control r02 job is excluded; five matching
geometry recipes were not attempted. See `expansion-amendment.md`.

All corpora are conservatively related as `fixture-procedural-development`.
They can contribute training examples but cannot become untouched challenge or
independent validation. Existing development-purpose manifests remain unchanged;
new explicit source reviews and a training-only extension bind the admission.
Simple procedural artwork is not a custom photograph/Top Shelf pipeline and is
not native Photos coverage. This report is immutable once hash-bound.
