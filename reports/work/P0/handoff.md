# P0-A Handoff

Status: **review**  
Packet: `P0-A`  
Evidence: [`assessment.md`](assessment.md)

P0-A completed a bounded, read-only recovery assessment. The full 17,040-entry
inventory is in `manifest_inventory.jsonl`; source candidates and provenance
matches are in `candidate_sources.json` and `provenance_search.json`.

## Outcome and changed paths

- Base revision inspected: `325e7cf5882c7070829a6696b0a4d498f1d8ed01`.
- The working tree already contained unrelated research/task changes; those were
  preserved. This packet added `scripts/assess_dataset_recovery.py`, generated
  `reports/work/P0/*`, and updated the P0-A queue row in `Tasks.md` to `review`.
- No source files, links, labels, checkpoints, or historical reports were changed.

## Acceptance evidence

| Criterion | Result | Evidence |
|---|---|---|
| Inventory all 17,040 entries | PASS | `manifest_inventory.jsonl` |
| Test pixels available | FAIL / blocked | 0 of 2,000 test images resolve |
| Train/validation original pixels available | PARTIAL | 1,441 train and 360 validation batch images resolve; original synthetic links remain broken |
| Documented candidate roots checked | PASS | `candidate_sources.json` — 0/15,239 expected original source files found |
| Exact original recovery established | NOT ESTABLISHED | No candidate source matched |
| Per-file label content hashes | DEFERRED | Label existence/size and surviving cache identity hashes recorded; no label bytes were rewritten |

## Verification commands

- `PYTHONDONTWRITEBYTECODE=1 .venv-yolo/bin/python scripts/assess_dataset_recovery.py` — exit 0.
- Focused inventory assertions — passed: 17,040 rows, all labels present, split counts verified, five candidate roots with zero matching source files.
- `git diff --check` — exit 0.
- `swift build` — passed on the bounded retry with in-project compiler cache.
- `swift test` — passed on the bounded retry: 14 XCTest cases and 90 Swift Testing tests, 0 failures.

No source files, links, labels, checkpoints, or historical reports were changed.
No recovery, regeneration, inference, training, or external write was attempted.

All 17,040 labels were accounted for by manifest-relative existence and size.
Per-file label content hashes were not collected because the large surviving
label directories caused repeated filesystem stalls; surviving per-split cache
identity hashes are recorded in `assessment_data.json` and the inventory marks
this limitation explicitly.

## Remaining risks and resume condition

The historical Run 009 aggregate report remains historical and non-reproducible
until usable test pixels are recovered or a new corpus is explicitly versioned.
The surviving `batch_6a8` images are separate fixture artifacts and must not be
treated as recovered synthetic holdout pixels. No P0-B staging, reconstruction,
inference, or training is authorized by this handoff.

The resume condition is a maintainer-supplied, bounded backup/archive location or
an architect-reviewed replacement-corpus decision. P0-B must stage into a new
in-project corpus directory and verify every image before any data-dependent
evaluation or training.

No new BestPractices entry was added: the observed failure is already covered by
BP-52, with the concrete evidence recorded here.
