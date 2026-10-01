# INTAKE-AUDIT-01 — consumer audit and contract readiness

Consumer software completed for review; new producer contract acceptance pending.
Repository worker-execution guidance shaped actual caller tests and explicit outcome
accounting, not additional per-frame paperwork.

## Delivered

- `scripts/human_intake_audit.py`: seeded sampling without replacement from eligible
  imported frames; exact original aliases/unresolved native entries excluded and
  accounted; separate bounded exception queue with deferred counts.
- Structural findings: missing boxes, unknown/conflicting/multiple focus, reviewer
  flags and overlapping boxes (which may be legitimate). No Vision/model execution
  or claim that a flag proves an error.
- Fresh isolated editor workspace, prefilled from immutable review snapshots or
  original proposals, never mutable editor work. Approval flags reset; focus labels
  preserved. Existing editor `--queue` and eight-frame `--batch-index` work directly.
- Existing Finish review, immutable revision and production crop QA remain authority.
  Correction summary separately counts random/exception completion and changes;
  overlapping frames are shown once. Changes are not automatically adjudicated defects.
- Recovery: existing evidence stays untouched; output collision fails rather than
  overwriting progress. Reopen the same workspace to continue. Source/hash/queue
  changes reject replay. No new capture-job retry semantics are invented.

## Use

From repository root, prepare an existing supported batch (omit `--revision` to use
original proposals):

```sh
PYTHONDONTWRITEBYTECODE=1 .venv-review/bin/python scripts/human_intake_audit.py prepare BATCH_JSON NEW_PROJECT_OUTPUT --revision REVISION_JSON --seed 42 --count 8 --exception-limit 8
PYTHONDONTWRITEBYTECODE=1 .venv-review/bin/python scripts/human_review_editor.py NEW_PROJECT_OUTPUT/review/batch.json --queue NEW_PROJECT_OUTPUT/combined-queue.json --batch-index 1 --runtime NEW_PROJECT_OUTPUT/runtime
PYTHONDONTWRITEBYTECODE=1 .venv-review/bin/python scripts/human_intake_audit.py summary NEW_PROJECT_OUTPUT/combined-queue.json NEW_REVIEW_REVISION_JSON NEW_PROJECT_OUTPUT/summary.json
```

Random and exceptions each have separate queue files; combined avoids duplicate
human effort. Zero selected frames is an accounted empty result, not a review task.
No need for the user to reannotate the retained smoke sample below.

## Acceptance evidence

| Check | Result / evidence |
| --- | --- |
| Human-review suite including 12 new audit tests | 135 passed, `python-tests-review.log` |
| Existing producer/import validators | 41 passed, `harvest-tests.log` |
| Installed Labelme UI | `artifacts/ui-proof/ui-result.json`: filtered list, prefilled rectangle, approval reset and clean load passed |
| Retained real images | 4 of 8 eligible selected deterministically; 18 source/editor files unchanged, `retained-proof.json` |
| Existing native contract/crop replay | 3 pairs, 6 production crops; `native-replay.json`, `artifacts/native-replay/` |
| Actual Finish + crop integration | Generated corrections accepted through existing callers and production crops in audit tests; software-only review does not count as human completion |
| Rejection/recovery | Changed hashes, duplicate IDs, bad bounds, protected partition, altered baseline/selection, wrong revision, empty population, deferred exceptions, output collisions and 8/8/1 slicing tested |
| Swift build | Passed without warnings, `swift-build-local.log` |
| Full offline Swift tests | 120 Swift Testing +14 XCTest passed, `swift-test-verified.log` |

Initial broad Python attempt used the model environment without Labelme; rerun in
`.venv-review` passed. Restricted Swift attempts failed macOS platform access, not
new Python assertions. Final test used scoped service access, CFFIXED_USER_HOME,
TMPDIR and Swift caches inside `.build`; no networking or device operations.

## Independent outcomes and remaining dependency

**Software:** ready for review; deterministic local workflow integrated, no new app.
**Data:** retained proof only, no new labels approved, training admission or source
independence claimed. Random sample represents the eligible subset, not all sources.
**Integration:** legacy replay passed. TTR's r1 is explicitly illustrative/unemitted;
new-format acceptance cannot pass until named valid/partial/corrupt examples arrive.
Detailed [producer response](producer-feedback.md) specifies exact resume inputs.
**Model:** unchanged; no training, model inference, new Vision proposal execution,
threshold change or promotion. Required Swift tests exercise existing platform tests.

Next substantive work: bind actual emitted semantic examples into existing intake,
replay partial/corrupt cases, then prepare a fresh producer audit—not another manual
review of these already reviewed real screens. Optional OCR/box discrepancy scoring
is not implemented here and must remain advisory when assigned.

## Coordination

Published/read back `nuiak/requests/nuiak-20261001-intake-audit-r1.md` and own
`packets.INTAKE-AUDIT-01` in verified SharedStatusFile. YAML parses; unrelated packet
entries preserved. Producer plan copied with verified 8587-byte/SHA256 receipt
(see producer-feedback). Peer acknowledgment not yet observed; does not block local work.
