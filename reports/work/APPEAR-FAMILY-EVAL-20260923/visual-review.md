# Nine-pair visual review

Reviewer: NUIAK architect, 2026-09-23. Reviewed high-contrast-frames.png,
photos-like-dock-frames.png, blank-placeholder-frames.png and all-crops.png against
the strict native-bound metadata. Each bundle has reference plus three focused
targets (grid_cell_0_0, grid_cell_1_0, grid_cell_1_1); disabled grid_cell_0_1 is
outside the focus sweep. All nine focus targets and18 production crops accepted
for simulator development diagnostics, not independent evaluation or training.

High contrast shows distinct yellow outline/white halo only on the observed target.
Photos-like dock shows white border/blue glow on that target; it is vector landscape
art on collectionItem controls, NOT Photos primary/secondary buttons. Blank gray
cards have a visible white rounded focus border, absent on the reference. Full-frame
overlays agree with control geometry; focused scaling and label/context are retained
by the production16% expansion/256 crop. Some neighbor content appears within the
expanded crop by design; no target focus boundary is visibly clipped. Original
unannotated pixels, not overlays, supply crops and inference.

All native bracket/recipe/hash checks pass on the unchanged source bytes. Visual
review corroborates labels, never replaces callbacks with requested focus/model
predictions. These three dark/regular/seed7 renderer variants have related lineage;
do not claim untouched final evaluation, theme diversity, physical rendering,
navigation success, or Photos-button coverage. All inspected rendering effects are
real here, unlike the earlier catalog's dark/high_contrast pixel alias.
