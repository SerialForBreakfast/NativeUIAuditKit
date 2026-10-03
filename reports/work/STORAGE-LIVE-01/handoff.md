# STORAGE-LIVE-01 — live SSD evidence

Completed October3. Seven report trees now load directly from the local SSD.
Software verified; data roles unchanged; real input integration qualified for the
29pair transition workflow. Model gates not assessed; no training/inference/capture.

## Migration

`/Volumes/training-drive/data/NUIAK/live/` mirrors these logical prefixes:

- `reports/work/FOCUS-APPEARANCE-06/artifacts`
- `reports/work/FOCUS-ARTWORK-08/artifacts`
- `reports/work/FOCUS-RECORDED-STRUCTURAL-22/artifacts`
- `reports/work/FOCUS-CAMPAIGN-09/artifacts`
- `reports/work/FOCUS-INTAKE-13/artifacts`
- `reports/work/SYN-07-READINESS/artifacts`
- `reports/work/NATIVE112-INTAKE-01/received`

Copied/verified22,954files,15,858,982,349content bytes. Reclaimed15,858,730,636bytes
(14.77GiB) internally;56Git-tracked files preserved. `.DS_Store` alone is excluded
from content hashes and left local if present. No symlink replacements or Git writes.
Receipts `<packet>-copy.json` contain complete source membership/hashes; copy and
reclaim verified both sides using existing corpus-retention checks. All commands exit0.

Internal free space was37GiB at migration preflight and29GiB at final observation,
despite successful local reclamation; do not equate logical deletion with disk-wide
free-space change. `/System/Volumes/Update` currently occupies14GiB and was untouched;
its change over this interval was not measured. Other APFS/system activity remains
unattributed. Reports footprint fell26GiB→12GiB. Unmigrated datasets remain local.

## Integration and verification

- `artifact_storage.py` maps exact prefixes using ignored local
  `reports/storage/locations.json`, pinned to the observed local APFS mount
  `/dev/disk25s1` at `/Volumes/training-drive`. Mount/root/path/overlap checks fail
  closed. No fallback or new output routing; `fresh` rejects mapped outputs.
- Shared member/ref readers, human-review editor bindings and reconstructed-corpus
  validation use explicit input resolution. Logical paths and sealed documents
  remain unchanged. Future direct-model protocols now pin the storage/reader code.
  Historical execution protocols are not silently rebound after source changes.
- First actual input test exposed an external editor snapshot's `relative_to(ROOT)`
  assumption; fixed with reverse logical mapping and a dedicated regression test.
  Failure retained in `.build/storage-live-consumer.log`.
- Corrected real input check:29pairs, exact corpus hash
  `9735108bf5ae011dfb17c07f7d49c4b42dfba4c9e1e027459a2b377047f589aa`,15.43s for
  hashing, label reconstruction and image checks. This mixed CPU/I/O validation is
  not a cold-storage benchmark or proof of training-throughput equivalence.
- After reclaim, actual CLI `focus_direct_transition.py --sources
  reports/work/DIRECT-TRANSITION-53/sources.json --output
  reports/work/STORAGE-LIVE-01/post-migration-inventory` exits0:29pairs,0exclusions,
  same hash and groups (Fixture12changed/12unchanged; Settings2changed/3unchanged).
  Generated protocol/admission proposal remains unapproved; no new roles assigned.
- 115focused Python tests pass4.711s; coverage includes absent/wrong mount, traversal,
  overlaps, symlinks, unknown external paths, source/output isolation, identity,
  archive corruption/collision, tracked-file preservation and reader compatibility.
  `.build/storage-live-tests-final.log`.
- Offline Swift build2.91s/test build2.59s,14XCTest+120SwiftTesting tests pass.
  Existing resident dependencies/local caches; scoped compiler sandbox escalation.
  `.build/storage-live-swift-{build,test}.log`. Final diff check passes.

Registry SHA256:
`55f0f45ba69ef3d7b0cd0632a97a5d0167d8ee82720b6c9f9f4715986be319e1`.
Registry and receipts also copied/verified to
`/Volumes/training-drive/data/NUIAK/live/storage-state-20261003/`.
See [operations and recovery](../../storage/README.md). Device numbers can change
after reconnect; verify the intended volume before explicitly rebinding. A single
SSD copy is live storage, not redundant backup. Shell tools require a resolved path;
not every historical consumer has been qualified. Tracked prose remains editable
locally; mapped readers use the preserved external evidence copy.

## Scope and next tranche

New reusable source: storage resolver/migrator and tests. Updated shared readers,
human-editor paths, iOS validator entrypoint, direct protocol code pins, plans/queue
and operational docs. All previous dirty model/code/doc work preserved. No external
repository, SMB or device action. Do not modify/delete SSD live data as a cache.

Next substantial storage tranche: qualify YOLO exports/symlink dependencies and
full dataset-loader behavior, migrate the remaining large iOS/tvOS datasets with
the same content checks, and benchmark representative training input loading without
launching a new model run. Current integration does not authorize blind whole-repo
movement. Model development can resume now with the SSD mounted and newly pinned
execution protocols; no need to restore these migrated report trees first.
