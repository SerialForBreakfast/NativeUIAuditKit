# Repository artifacts and cleanup policy

Source control retains source, reusable tests, schemas, canonical plans, concise
reviewed result/decision handoffs and compact artifact hash indexes. It is not the
dataset or execution-log store. Artifact retention and model gates remain unchanged.

## New work

- Put reusable code in scripts/ or the appropriate source target, not reports/work.
- Tests generate their inputs under an owned .build directory or use deliberately
  reviewed fixtures under Tests/Fixtures. Never depend on a previous worker's output.
- reports/work keeps concise Markdown handoffs. Generated JSON, logs, screenshots,
  videos, result bundles and one-off scripts remain local by default. A genuinely
  necessary compact JSON record can be reviewed into an explicitly allowed path;
  do not force-add large outputs to bypass policy.
- A handoff states commands, result counts, source/model/corpus identities, unresolved
  limitations and artifact paths/hashes. Links to ignored local evidence are not a
  claim that a fresh checkout includes it. Document recovery location/owner when
  available; missing independent backup stays a blocker, not an implied success.
- Do not ignore all JSON, all media or all reports globally: schemas, models package
  resources and deliberate test fixtures remain versioned in their own directories.

## This cleanup

No files are deleted or moved, no Git index/history is changed, and no data is uploaded.
Current generated artifacts are retained at their existing locations and fingerprinted
in reports/work/REPO-CLEANUP-20260923/artifacts.sha256. The .build restoration drill
and dataset/ trees must not be cleaned: no independent backup was established.

New ignore rules prevent adding matching untracked outputs. They do not remove
already tracked files. The existing report history requires a separate reviewed
de-indexing list, with reference/test dependencies and retained recovery copies checked
before the maintainer runs git rm --cached. Do not run a broad git rm -r --cached .,
git clean, history rewrite or filesystem deletion as part of this tranche.

The accompanying commit path list is a snapshot, not future authorization: review
git diff before staging and review git diff --cached afterward. The maintainer owns
all Git writes. Ignoring files saves future Git growth; it does not shrink old history.
