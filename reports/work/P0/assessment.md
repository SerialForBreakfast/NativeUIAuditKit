# P0-A Dataset Recovery Assessment

Generated: 2026-09-19T18:41:56Z  
Git HEAD: `325e7cf5882c7070829a6696b0a4d498f1d8ed01`

## Decision

The original Phase 6a image corpus was not recovered in the bounded search. The
assessment is **not evidence that the originals are destroyed**; it records only
that no exact source was found at the documented paths searched here. The next
safe action is to obtain a specific backup/archive location from the maintainer,
or to obtain approval for a separately versioned replacement-corpus proposal.

Do not relink the historical export, rerun `export_coco.py` over the old output,
pair regenerated pixels with surviving labels, or report the historical 0.585669
mAP50 as currently reproducible.

## Manifest inventory

The complete machine-readable inventory is
[`manifest_inventory.jsonl`](manifest_inventory.jsonl). It contains one record
per manifest entry, including link target, image/label existence, label size,
available image hash/dimensions, and stable repository-relative paths where
possible. Per-file label content hashes were not read during this bounded pass;
the surviving per-split `labels.cache` identity hashes are recorded instead.

| Split | Entries | Resolvable images | Broken symlinks | Other missing images | Labels |
|---|---:|---:|---:|---:|---:|
| train | 11984 | 1441 | 10543 | 0 | 11984 |
| val | 3056 | 360 | 2696 | 0 | 3056 |
| test | 2000 | 0 | 2000 | 0 | 2000 |

Total entries: **17040**  
Unique manifest paths: **17040**  
Unique source target paths: **15239**  
Duplicate manifest paths: **False**

The surviving labels and historical report are preserved. The label and manifest
hashes, plus the Run 009 checkpoint hash when present, are recorded in
[`assessment_data.json`](assessment_data.json).

The per-file label hash field is intentionally `null` with an explicit status:
the label corpus is evidence to preserve, but opening the large surviving label
directories caused repeated multi-minute filesystem stalls during this
read-only assessment. The existing Ultralytics cache hashes provide a surviving
split-level identity signal; they are not substitutes for per-file content
hashes and do not qualify image recovery.

## Bounded source lookup

The lookup checked only exact paths documented by `export_coco.py`, provenance
records, and the recovery plan. It did not recursively scan the home directory,
mount volumes, install recovery tools, or mutate any source.

| Candidate | Path | Root exists | Present expected source files | Root manifest |
|---|---|---:|---:|---:|
| `export_report.source` | `dataset/dataset` | yes | 0/15239 | no |
| `in_repo_dataset_parent` | `dataset` | yes | 0/15239 | no |
| `trainer_source_dataset` | `NativeUITrainer/source_dataset` | no | 0/15239 | no |
| `documented_sibling_dataset` | `/Users/josephmccraw/Documents/GitHub/NativeUIAuditKit-Dataset` | no | 0/15239 | no |
| `documented_home_dataset` | `/Users/josephmccraw/NativeUIAuditKit-Dataset` | no | 0/15239 | no |

Full candidate details are in
[`candidate_sources.json`](candidate_sources.json). No candidate met the
identity threshold for original-corpus recovery.

## Surviving derived artifacts

- `reports/blurred_eval_images/` contains 200 blurred images from the historical
  evaluation pass. They are derived outputs, not original holdout pixels.
- `NativeUITrainer/yolo_runs/phase6a_r009_test_pred/labels/` contains 2,000
  historical prediction label files. They do not restore image bytes, image
  hashes, or source provenance.

These artifacts are catalogued in `assessment_data.json` and were not modified.

## Provenance and recovery limits

The bounded checked-in evidence search found 124 matching lines;
details are in [`provenance_search.json`](provenance_search.json). The repository
records the synthetic dataset as an external `NativeUIAuditKit-Dataset` store,
but that documented store was not present at the searched sibling or home path.
Git does not contain the ignored PNG corpus.

## Acceptance evidence

| Criterion | Result | Evidence |
|---|---|---|
| Account for all 17,040 entries | PASS | `manifest_inventory.jsonl`, `assessment_data.json` |
| Account for every label and preserve hash evidence | PARTIAL | All 17,040 labels exist; per-split `labels.cache` identity hashes recorded; per-file content hashes deferred |
| Preserve existing artifacts | PASS | No dataset links, labels, weights, or historical reports changed |
| Identify documented source locations | PASS | `candidate_sources.json`, `provenance_search.json` |
| Establish exact original recovery | NOT ESTABLISHED | No candidate source had matching files |
| Recommend next action without inventing provenance | PASS | Request specific backup/archive or review a new corpus version |

## Handoff status

P0-A is **review-ready**, not accepted. The per-file label hash field is the one
known evidence limitation in this assessment; the surviving cache identities and
label sizes are recorded, but they are not equivalent to per-file content hashes.
P0-B must not begin until a specific
source is supplied and the architect reviews whether its identity is verified,
uncertain, or a new corpus. The independent training-corpus readiness remains
unresolved even if the 2,000-image test holdout is recovered.
