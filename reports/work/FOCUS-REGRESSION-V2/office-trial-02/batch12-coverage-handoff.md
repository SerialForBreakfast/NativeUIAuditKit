# Completed-batch coverage audit and next assignment

## Outcomes

- Software: existing revision/completeness/audit mechanisms executed successfully;
  no implementation edits, model loading or new tests/build required.
- Data:16 reviewed frames/171 production crops revalidated. Diagnostic-only;
  no formally declared or newly admitted training pairs.
- Integration: immutable source, snapshot and crop bindings verified. Open batch03
  untouched; no TTR operation or peer next-action change, coordination not applicable.
- Model gate:unassessed. No inference/training/export/promotion.

Evidence: `batch12-coverage-proposal.json` binds the two revisions, completeness
receipts and crop reports by hash, enumerates154 proposed candidates,16 auxiliary
annotations and1 unresolved clock/avatar, and records14 proposed pair mappings.
Existing `checked_revision`, `checked_completeness` and `human_review_audit.audit`
ran on both exact revisions; each has8 completeness assertions and zero hard issues.
All input references were checked again after report generation. Source files and
human labels were not edited. Selection context images were visually inspected;
visual findings are preparer observations, not native ground truth.

## What is covered—and what is not

Seven Settings frames contribute69 proposed candidates/7 focused; three Home
frames49/3; six empty-content App Store tab screens36/6. These are related views
from one session, not16 independent environments. There are no focused native
dialog buttons, populated shelves/search results, player overlays, Control Center,
or observed no-focus/multiple-focus cases in these two completed batches. Batch03
may add populated cards/search once reviewed; it contributes zero accepted support
now. Appearance strata such as theme/contrast are not formally annotated.

The current data is useful for a development baseline, not a broad training corpus.
There are16 focused crops versus155 unfocused crops; aggregate accuracy would be
misleading. Classifier evaluation with human boxes does not measure detector misses.
All formal pair arrays are empty. Nine visual same-control proposals, plus five
qualified/uncertain matches, must not be advertised as14 validated training pairs.

Specific findings: Update Apps changes On→Off between456/488; VoiceOver changes
On→Off and removes its Help row between349/386. These are not clean focus-only
changes. Local ordinal IDs differ for Install Apps. Computers is clipped in249;
blank HotPotatoTV counterpart cannot be identified from appearance alone. Frame605
has an unresolved clock/avatar and unboxed partial tiles at the bottom; retain
its human completeness receipt but flag the conflict for frame-level admission.

## Prioritized next collection (proposal, not capture authority)

1. **Finish existing batch03 first.** Its populated artwork cards and search results
   address a real coverage gap without another capture session. Reuse presets and
   copy/paste, then verify per-frame geometry/focus. No request for descriptions on
   every box; semantic pair identity can be reviewed in a small grouped sheet.
2. **Native buttons/Photos:** initial target6 matched pairs from approved safe
   screens, both states of the same visible button plus competitors. Receive the
   existing Photos originals first if available; do not repeat capture merely to
   fill a quota. Preserve the earlier diagnostic-only approval; new training-use
   permission and trustworthy image/session/hash/bounds evidence are still needed.
3. **Artwork/Home/card transfer:** initial target12 matched pairs with varied
   backgrounds, positions and visible competitors; avoid placeholder-only artwork.
   Keep clear full-control pairs separate from intentionally clipped diagnostics.
4. **Settings rows:** initial target6 matched pairs produced by moving focus only,
   with values unchanged. No setting toggles needed. Include lookalike unfocused
   rows and exact control correspondence, not ordinal matching.
5. **Tabs:** initial target8–12 pairs across different approved layouts/apps, not
   additional snapshots of this one six-tab strip. Preserve tabItem role without
   pretending it is a detector class or relabeling the whole bar as focused.

These32–36 pairs are initial collection targets, not qualification thresholds or
guarantees of improvement. Priorities reflect coverage gaps, not newly measured
model failures (no predictions run). Reserve sources/roles before collection:
keep this entire trial02 development-exposed session out of training and untouched
challenge. A separate session alone does not prove different source ancestry;
track app/layout/recipe relationships and qualify independent validation separately.
Training needs its own human-label admission decision and execution approval.
Broader safe Control Center/player/overlay collection is a later coverage tranche,
not a reason to stall the current baseline. No new6000-pair quota is imposed on
this development step; existing qualification gates remain unchanged.

## Low-friction next handoff

The updated `Research/Plans/Trial02DevelopmentAdmission.md` is the concrete
admission/implementation plan. Bundle its few unresolved decisions after annotation;
do not interrupt the annotator per image. Existing tooling is reused.

When batch03 Finish review supplies a revision path: verify its seal/snapshots and
matching completeness receipt with `human_regression_review`; run existing
`human_annotation_review.crop_qa` into a **fresh** project-local QA directory;
then `human_review_audit.py REVISION CROP-QA NEW-AUDIT-DIR`. Count every frame and
control, verify crop hashes/production preprocessing, inspect duplicate warnings
for real focus changes, preserve pending exclusions, and update combined coverage.
Do not read mutable open editor JSON as confirmed labels or alter batch03 now.

Completion: coverage and exact proposal delivered; next is admission decisions
and separately assigned role-aware evaluation, not another open-ended training run.
