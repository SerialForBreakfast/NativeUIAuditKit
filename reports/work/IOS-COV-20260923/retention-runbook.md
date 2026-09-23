# DATA-RET: preserved iOS prefix inventory and recovery procedure

Scope: `.build/debug-output/p0c-resume/r6-verified-prefix`, containing14,340 accepted
image/annotation pairs plus complete-prefix rejected-trial evidence and manifests.
Do not clean `.build` as if this tree were disposable. The prefix, original r4/r5
failed evidence, source/runtime pins and P0-C reports are retained dependencies.
Current coverage does not include every other corpus/model in this repository.

`scripts/corpus_retention.py` provides `inventory`, `verify`, `restore`. All new
inventory/restore outputs must be inside the package and must not exist. No delete,
overwrite, external-copy or source-cleanup mode exists. Symlinks and unknown members
fail. The explicit Finder option records `.DS_Store` exclusions; no corpus content
is excluded. Do not hand-edit a sealed inventory to accept changed bytes.

## Observed failure retained

The initial strict inventory included32,833 files/8,904,050,065 bytes. Strict restore
reported `copy_hash_mismatch:.DS_Store`; the destination exists, so this was not a
pre-output rejection. Preserve it as a failed drill, not a verified recovery. The
first receipt lacks stage attribution; the tool now labels preflight/postflight
failures explicitly. Strict inventory and restore.log are retained. A second content inventory explicitly
excludes only Finder metadata; original source is unchanged and metadata not deleted.
This is a changed-source finding, not permission to skip hashes on images/annotations.

## Recovery procedure

1. Preserve the approved content inventory, raw corpus, manifests/annotations, native
   recipe/source/runtime pins and qualification reports together. Raw images and
   sidecars are authoritative dependencies; regeneration on another runtime is not
   a promise of identical pixels.
2. Maintainer selects an independent destination and retention owner. This remains
   unassigned; an additional folder on this same volume is not a backup. Allow at
   least the content inventory's totalBytes plus filesystem overhead, and another
   copy's capacity for a full restore test. Current dataset content is about8.9GB.
3. Under separately scoped copy authority, copy into a new destination, preserving
   all declared relative paths. Do not mirror/delete or overwrite a prior backup.
4. Run `verify --inventory CONTENT_INVENTORY --copy EXACT_BACKUP_ROOT`. It verifies
   complete membership, bytes and hashes read-only. Record destination/media identity
   separately; the tool intentionally does not infer independent storage from a path.
5. Run `restore --inventory CONTENT_INVENTORY --copy EXACT_BACKUP_ROOT --output
   NEW_PROJECT_LOCAL_DIRECTORY`; exclusive copies retain partial failures. Verify
   restored membership and qualification reports before replacing any dependency.
6. Reverify after copying, storage migration or reported corruption and before a
   destructive cleanup. No scheduled task or automatic deletion was created.

The local full-prefix drill in this tranche tests the copy/recovery mechanism only.
`restore-content.log` records success:32,832 files/8,904,043,917 bytes, inventory seal
`8bff6257de9ad5a2a67059b39c6cabe7f1d7c1f9653f3866b69564e265735415`, restored to
`.build/debug-output/ios-retention-20260923/restored-content-v2`. The earlier failed
`restored-prefix` directory remains preserved; no cleanup was performed.
It cannot establish external backup availability, final16,940 membership, annotation
semantic truth or model eligibility. All historical originals and failed trials remain.
