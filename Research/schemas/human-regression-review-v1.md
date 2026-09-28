# Low-friction regression preparation and completeness

2026-09-28. Assigned FOCUS-REVIEW-PREP-01: checklist, diverse batch preparation,
duplicate handling, explicit completeness and coverage report; rectangle double-click
opens the existing label dialog. No capture, inference, training or transport adapter.

Keep v1 diagnostic manifests and historical revisions unchanged. A separate sealed
`human-regression-queue-v1` binds one validated batch, optional frame coverage metadata
(app, layout, interaction family, optional preparer-observed focusTreatment), ordered selected IDs, batches of8, and every
unselected/blocked/exact-duplicate disposition. Exact decoded-pixel groups choose one
canonical frame only within the same screen/context; conflicting proposals/native
observations block reuse. Timeline/event rows remain in the original batch. Do not
copy confirmed labels onto different pixels or auto-drop near duplicates. Metadata
is supplied once per screen/layout by the preparer, not repeatedly by the annotator.
Distinct layout counts remain descriptions, not source-independence claims.

The editor may open a hash-checked queue/batch slice. Its file list and Finish review
ready set must use the same exact frame membership. Saving/canceling/pending frames
retains existing behavior. Finish review offers one unchecked optional assertion:
all visible focusable controls are included in each Ready frame. This creates a new
`human-review-completeness-v1` receipt bound to the immutable revision, snapshots,
human reviewer and covered frame IDs. It does not modify completeFrameCandidates
on old v1 manifests. Software-test reviewers never attest real completeness.
Changed pixels/boxes/revision invalidate a receipt; absent assertion stays unknown.
This enables future admission for full-frame metrics, not automatic scoring now.

A `human-regression-coverage-v1` report distinguishes selected, reviewed, complete,
blocked and unrepresented interaction families; positive/negative support by family
and class stays explicit. Separate retained smoke set from the future real-world
benchmark. No hidden missing members, quota-based qualification or training admission.

Double-click uses normal canvas coordinates and the topmost visible rectangle,
then the stock edit-label dialog. Empty-space/right/drawing clicks are unchanged;
cancel preserves annotations. No vendor-package modifications or new annotation app.
