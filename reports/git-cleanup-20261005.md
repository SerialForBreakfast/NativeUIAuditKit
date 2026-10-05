# Git cleanup and commit review — 2026-10-05

## Completed cleanup

- Added `/reports/work/**/artifacts/` to `.gitignore`, preserving existing rules and edits. All 36,119 previously visible generated artifact paths are excluded. Source, tests, plans and top-level handoffs remain visible.
- Updated `Research/ArtifactRetention.md` to explain the stable directory rule. No blanket JSON/TXT/YAML exclusion was introduced.
- Confirmed the Git index is empty. No staging, unstaging, de-indexing or commits were necessary or performed. Existing tracked artifacts remain tracked pending an exact reviewed removal list.
- Verified USB mount `/dev/disk7s1`, local APFS, volume UUID `FD8D8E36-FAAC-4205-87ED-86134C3582B1`, approximately 1.9 TB available.
- Archived the inactive Apple source-research ZIP below, verified destination and unchanged source hashes, then removed only its local copy. No dataset, model, capture, active input or pending-transfer artifact was removed.

### Archive receipt and recovery

Original: `reports/work/UI-SOURCE-177/artifacts/apple-media-catalog.zip`

Retained archive: `/Volumes/training-drive/data/NUIAK/archive-20261005-git-cleanup/apple-media-catalog.zip`

Bytes: **39,806,690**. SHA256: `b234e9bb4a15a29a6b0cd254243750e5872ff753ae3a88acaa76c9ec85b134e9`.

To restore, verify this hash and copy to the original path only if absent; do not overwrite a newer file. This is a single archived copy, not redundant backup. No automatic resolver mapping or symlink was introduced.

### Deliberately preserved

The 36k labels/artifacts are ignored but remain usable at their existing paths. The larger corpus trees have path-bound consumers; moving them wholesale would risk pending Run020 evaluation and earlier replay workflows. Local process inspection was sandbox-denied, so inactivity was not inferred for training inputs. The source ZIP has no script or transfer-transaction reference and belongs to the completed read-only source spike.

The existing migration helper hardcodes `/dev/disk25s1`, while the verified current device is `/dev/disk7s1`. It was not executed or modified. Qualify a current-volume-aware migration before additional live-input moves. The already documented r7 de-indexing prerequisite also remains unresolved.

Two pre-existing canonical script deletions and identical ` 2.py` copies remain untouched; reconcile those filenames before committing. See [audit](git-audit-20261005.md).

## Commit summary for maintainer review

Suggested cleanup-only subject: **Ignore generated experiment trees and record verified USB archival**

Suggested body:

> Exclude all report artifact directories independent of packet ID or extension, preventing generated labels, caches and extracted reports from entering Git. Document retention boundaries and the verified archival/recovery location of the inactive Apple sample-source ZIP. Audit the pending work without removing tracked historical evidence or changing active dataset paths.

Cleanup-only review paths:

```text
.gitignore
Research/ArtifactRetention.md
reports/git-audit-20261005.md
reports/git-cleanup-20261005.md
```

The `.gitignore` diff also contains six pre-existing packet exclusions; they are preserved and now redundant with the broader artifact-directory rule. Review the entire diff before staging.

Maintainer commands (not executed by agent):

```sh
git diff -- .gitignore Research/ArtifactRetention.md
git add -- .gitignore Research/ArtifactRetention.md reports/git-audit-20261005.md reports/git-cleanup-20261005.md
git diff --cached --stat
git diff --cached --check
git diff --cached
```

Do not broadly stage the checkout. Other pending changes should be reviewed as separate groups: iOS renderer/capture tests; iOS training/evaluation experiments; focus-transition/worker experiments; SMB transfer infrastructure; research/task/evidence updates; artwork/UI-source handoff plans. The audit describes these groups; this cleanup does not certify their implementation or model results.

## Verification and next step

After the ignore edit: **zero staged paths, zero untracked artifact paths**, 150 remaining untracked candidates before adding this handoff. Explicit checks confirmed `scripts/fit175.py`, `Research/Plans/UIComponentIntake.md` and the UI-SOURCE-177 handoff remain visible. `git diff --check` passed. Documentation/ignore-only changes did not require a build or training run. SMB coordination not applicable.

Next storage tranche: produce the exact historical-artifact de-indexing inventory, check replay/test consumers, repair and test volume binding in the migration helper, then qualify additional USB input mappings before reclamation. The current change solves accidental Git inclusion, not the full disk-space problem.
