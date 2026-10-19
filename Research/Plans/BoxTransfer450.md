# BOXTRANSFER450 — Test measured-box training on retained detector boxes

Owner: Maximum-mini-NUIAK. Date: 2026-10-18.

All 12 GEOMETRY449 jobs complete. Six Standard misses lack matching proposals.
Two additional misses have usable overlap but fail crop selection.
Neighbor-spacing item 0 has IoU 0.788 and height ratio 1.169. Its retained score falls from 1.0 to 0.717.
Shelf item 3 has IoU 0.808 and height ratio 1.141. Its score falls from 1.0 to 0.842.
The fixed threshold remains 0.85. These observations suggest geometry sensitivity but do not establish causality.

## Controlled comparison

Use T57 for 6 conditions: dark background, grid, large controls, neighbor spacing, no focus, and shelf.
Compare the retained mixed model against `offset421-train-measured` on identical retained detector boxes.
Reuse completed predictions and known-box scores. Do not repeat capture, detector inference, or training.
The pinned batch and exact source references reside in `reports/work/BOXTRANSFER450/batch.json`.

Report gains, lost successes, new wrong selections, and no-focus outcomes for each profile.
The primary decision concerns Standard. HCF remains an optional separate slice.
Use COVERAGE447 membership for original groups. Preserve development roles and previous results.

## Decision and limits

If the existing correction recovers detector-box selections, retain it as evidence for a later matched training design.
If it loses successes or adds wrong selections, reject replacement and retain the failure cases.
The original consumer crop set still has a lost positive. This batch cannot override that regression or qualify a release.
Do not lower thresholds or train on inspected development offsets.
Missing proposals need separate complete training-only annotations, not crop jitter.

All 6 jobs pass preflight and receive exact approvals. All 17 focused adapter and compiler tests pass.
Each job permits 800 s, 100 MB, and 1 attempt. These limits are not runtime estimates.
The existing background runner executes the batch without a restart.
No source changes occur. Prior integrated Swift evidence remains applicable.
