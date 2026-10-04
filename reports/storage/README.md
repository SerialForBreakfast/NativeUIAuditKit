# Local SSD artifact storage

`locations.json` is an ignored machine-local registry, not a dataset/eligibility
manifest. Canonical references and hashes remain repo-relative and unchanged.
Supported input readers resolve registered prefixes to the verified local SSD.
No symlinks: source, environments, caches and new outputs stay local; registered
prefixes are read-only to output helpers.

Resolve an input for a shell tool or visual inspection:

```sh
.venv-yolo/bin/python scripts/artifact_storage.py reports/work/FOCUS-CAMPAIGN-09/artifacts/settings-review/raw/recorded-299.png
```

Mount must be local APFS at `/Volumes/training-drive`; registry currently pins
`/dev/disk7s1` after the October4 OS update (previously `/dev/disk25s1`). Verified
USB/APFS volume UUID `FD8D8E36-FAAC-4205-87ED-86134C3582B1`; archived campaign
receipt matches the local SHA256 `33e7e41bfdd0aa53648a1b97f0d0f0eee55953fecf3fc86f535a2208ec706742`.
Device numbers can change after reconnect/reboot: inspect the actual
mount and confirm the intended SSD before explicitly rebinding the registry. Do not
accept any device or create a substitute folder when disconnected. No automatic
mounting, fallback to stale local copies or remote access is implemented.

Only integrated readers support mapped inputs. Arbitrary shell commands and older
tools do not automatically resolve old paths. Use the resolver above or qualify
the tool before moving its inputs. YOLO symlink exports, training caches and other
unmigrated dataset trees remain local.

For new migrations: choose exact bulk prefixes; copy with
`migrate_artifact_storage.py copy`, activate a nonoverlapping registry entry,
verify real consumers/immutable identities, then run `reclaim`. Reclaim preserves
Git-tracked files and verifies both copies before removal. No model execution is
authorized by migration. Interrupted copies/partial reclamation require receipt
inspection, not blind retries/overwrites; this is not an automatic synchronizer.

Tracked review documents remain in Git; external copies keep evidence self-contained.
Edit tracked prose locally, not through mapped reader paths. Open the resolved SSD
path to review archived HTML with its image siblings.

Recovery: receipts in `reports/work/STORAGE-LIVE-01/` list membership and SHA256.
A registry/receipt copy is also at SSD `data/NUIAK/live/storage-state-20261003/`.
Verify external files, restore missing originals without overwriting tracked changes,
verify the reconstructed tree, then remove its registry mapping. Never alter sealed
manifests for relocation. One SSD copy is not redundant backup; the live tree is not
disposable cold-archive data.

The inactive r5 prefix is also mapped under `live/.build/debug-output/p0c-resume/`.
Its complete receipt is `reports/work/STORAGE-LIVE-02/r5-copy.json`; October3 second
registry snapshot and receipt are retained under `live/storage-state-20261003-02/`.
It is retained historical evidence, not newly qualified training data. The current
r6 prefix and r7/r8 YOLO paths have not moved. Resolve the r5 path explicitly for
inspection; older tools without storage support require verified restoration first.

## iOS exports after STORAGE-LIVE-03

The r7, r8 and addon corpus roots have registered SSD copies. r7's original local
copy remains because its old YOLO export is tracked; do not delete it yet. r8's
untracked image links have a sealed old-target inventory in
`reports/work/STORAGE-LIVE-03/links.json`. Restore source bytes before restoring those
original link texts. No corpus-root symlink has been introduced.

Use `NativeUITrainer/yolo_dataset_r7_ssd03_frozen/dataset.yaml` for the qualified
replacement export. `yolo_dataset_r7_ssd03` is the preserved failed directory-scan
trial and must NOT be used for training. Always pass `--manifest-members-only` when
exporting this frozen corpus: its directory contains unmanifested duplicate-named
files. New training still needs its own configuration/data-role approval.

Maintainer-only cleanup (not executed by agents): inspect the staged changes first,
then remove only the old generated export from Git tracking while keeping local files:

```sh
git rm -r --cached -- NativeUITrainer/yolo_dataset_41class_r7
git diff --cached --stat
```

The ignore rule is present. This stages removals, not physical deletion; it does not
authorize a commit or rewrite history. Once reviewed, a follow-up storage pass can
inventory/rebind those now-untracked links and reclaim the retained local r7 source.
Do not run `reclaim` on r7 before that dependency step.
