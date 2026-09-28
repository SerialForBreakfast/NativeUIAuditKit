# Local Simulator Fixture visual review

Reviewer: NUIAK agent, 2026-09-27 local. This is agent visual QA of independently
observed Fixture labels, not human Photos annotation or training approval.

Reviewed all24 production crops (focused/unfocused for each of four controls in
each bundle), all five distinct artwork full frames, and representative focused
full frames for bright and dock. All12 pairs are accepted for development review;
none are accepted for training or qualification. Native v2 brackets, image hashes,
per-state geometry and all annotations pass the existing strict consumer validator.
Reported source is not authenticated pixel attestation.

| Number | Bundle / exact pair IDs | Observed cue and context | Disposition |
|---|---|---|---|
| 01–04 | smoke / synth-0, synth-1, synth-2, synth-3 | Colored stripes/mountains; thin white outline only in focused crop. Partial neighboring tiles retained. | 4 development pairs |
| 05–08 | bright / synth-0, synth-1, synth-2, synth-3 | Cream/yellow artwork remains bright in both states; focused white outline survives resize. Brightness alone is not the label. | 4 development pairs |
| 09–12 | dock / synth-0, synth-1, synth-2, synth-3 | Blue/green landscape icons in one row; focused outline plus blue glow, unfocused artwork unchanged. | 4 development pairs |

Original bundles: `dataset/tvos_captures/sim-focus-dev-01-{smoke,bright,dock}`.
Production crop QA: `dataset/focus_ring/sim-focus-dev-01-{smoke,bright,dock}-qa`.
The manifest in each directory binds numbered pair IDs to exact image/crop hashes,
measured boxes and observed focus IDs. Never merge the three local `synth-N` ID
namespaces without their corpus ID. This report is immutable once hash-bound into
reviewed manifests; amendments require a new report and new derived output.

Per-pair actual crop filenames are identical across corpora because they derive
from local pair IDs; their parent corpus and hashes distinguish different pixels.
All focused crops visibly enclose the intended tile; no empty/black crops found.
The lower standard-grid row moves vertically when focused. Production crops use
each state's measured bounds, not copied baseline coordinates. Whole frames also
contain Fixture chrome outside the four annotated corpus controls. The baseline
focus is on Reference frame, not absence of focus throughout the screen; these
pairs do not establish complete-frame unique-selection accuracy.

All three recipes use one seed, runtime and source group. Differences in palette,
artwork, layout and glow demonstrate supported rendered diversity, not independent
data or native Photos coverage. Artwork is simple procedural imagery, not a proven
custom photograph/Top Shelf asset pipeline. No model ran. Protect all these
development-exposed members from later untouched-challenge claims.
