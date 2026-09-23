# Repository cleanup — current change set, no deletion

2026-09-23, NUIAK architect. Starting HEAD b3f0546. Preserved all prior worktree
changes. No Git writes, staged paths, filesystem deletion, uploads or history rewrite.

## Result

Before:168 untracked files,27,413,471 bytes;151 report files account for27,287,308
bytes. Added report-specific ignores for generated JSON/tabular output, raw logs,
capture media, archives/result bundles and one-off Python scripts. Also cover local
.venv-* environments, trainer caches and unpromoted checkpoint/export artifacts.
Schemas, source, reusable scripts, deliberate Tests fixtures, Markdown handoffs and
promoted compiled-model resources remain visible.

119 pre-existing generated report artifacts remain unchanged on disk; all119 hashes
in artifacts.sha256 verified. The inventory identifies local retained evidence, not
a backup. Visible untracked payload dropped to roughly0.25MB before this handoff/
commit list. No original artifact is deleted or moved. The .build restoration copy
must not be cleaned before independent backup. Existing historical reports unchanged.

Fixed scripts/test_validate_visual_probe.py: the test now creates its independently
expected catalog through NativeUIDatasetGenerator --plan-visual-addon, under its
owned .build temporary directory, before assembling a separate batch directory.
It no longer requires reports/work/DATA-PROBE-01/catalog-v2.json in a fresh checkout.
Tests require swift build first, as the existing generator CLI tests already do.
The other test reference to reports/work is a temporary-output parent, not a
historical artifact dependency; no untracking of historical test inputs performed.

## Checks

11 Python tests pass: ignore boundaries, real probe intake and real planning CLI.
tests.log records0.696s; all generated test directories removed by their owners.
Read-only shasum verification passes for119 retained artifacts. Offline swift build/
test use existing project-local caches with automatic resolution disabled; logs stay
ignored here. git diff --check passes.
Final Swift result:14 XCTest+109 Swift Testing pass; build exit0,0.20s incremental;
Swift Testing3.321s. No staged paths were present at handoff. The fixed commit list
has94 source/test/schema/documentation paths including this cleanup's evidence index.
Ignore tests assert new artifacts are ignored
while schemas, explicit image/JSON test fixtures, code and compiled model resources
remain eligible for Git.

Software verified; data eligibility unchanged; external integration not applicable;
model gates not assessed. No new package/model release is claimed.

## Maintainer action

commands.md provides explicit read-only review, path-list staging and commit commands.
commit-paths.txt includes the current integrated source/docs/tests and this cleanup,
not just cleanup-only files: the probe test depends on the accompanying uncommitted
generator/intake work. Review the whole list/diff before staging; no blanket git add .
and no force-add of ignored artifacts. A future worker's files are not authorized by
this snapshot; if state changes, stop and refresh the review/list.

There are2,435 already-tracked paths matching current ignore rules. They remain in
the index. This is NOT a de-indexing approval list: includes historical evidence and
possibly intentionally tracked resources. Review dependencies/retention separately
before any git rm --cached; this tranche avoids deleting historical checkout evidence
for other users. New ignores prevent growth but cannot shrink existing history.

Coordination: not applicable; repository hygiene doesn't change TTR's next action.
