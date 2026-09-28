# FOCUS-REVIEW-PREP-01

Offline review preparation. Owner: current NUIAK review-tool worker. No capture,
model inference, training, transport adapter or vendor-package changes.

[Operator checklist](operator-checklist.md) ·
[Contract](../../../Research/schemas/human-regression-review-v1.md)

## CLI

Run from the repository root; all output paths must be new project-local files.
Optional metadata is a sealed `human-regression-coverage-metadata-v1` document with
the existing diagnostic FLAGS and `screens: {screenID: {app, layout, family}}`.
Optional `focusTreatment` records a preparer's visual description once per screen;
omission stays unknown, not inferred from labels or model scores.
Accepted families: artwork-grid, shelf-card, native-list, button-detail,
navigation-toolbar, overlay-search-player, unknown. Omitted metadata stays unknown.
Use existing `human_annotation_review.write(path, document, sealed=True)` to seal it.

```sh
PYTHONPATH=scripts .venv-yolo/bin/python scripts/human_regression_review.py prepare \
  path/to/batch.json path/to/new-queue.json --metadata path/to/metadata.json
reports/work/HUMAN-REVIEW-01/runtime/venv/bin/python scripts/human_review_editor.py \
  path/to/batch.json --queue path/to/new-queue.json --batch-index 1
PYTHONPATH=scripts .venv-yolo/bin/python scripts/human_regression_review.py coverage \
  path/to/new-queue.json path/to/new-coverage.json \
  --revision path/to/revision/revision.json --completeness path/to/completeness.json
```

Omit revision/completeness when not yet reviewed. Omit completeness when not
explicitly asserted. Existing editor invocation without a queue still works.
Queue mode fixes membership: directory changes/search/drop cannot add hidden images;
relaunch with another queue slice for the next batch. Bounds/focus are never inferred.

The completeness receipt binds a revision and its actual annotation/pixel snapshots.
Editing later creates a new revision; it cannot inherit old completeness. Old v1
`completeFrameCandidates` stays false. A future metric adapter must explicitly
validate this receipt before using full-frame selection metrics. Nothing here admits
data to training or independent evaluation.

All original rows are accounted for: selected, deferred, exact-duplicate or blocked.
Compatible exact repeats refer to a canonical row; no labels are copied and no raw
events are deleted. Conflicting proposals block the whole exact group. Unknown
source independence is not resolved by a layout name or another recording session.
