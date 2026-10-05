# Repository artifacts and cleanup policy

## October 5 — stable experiment-artifact exclusion

All `reports/work/**/artifacts/` directories are ignored regardless of packet ID
or file extension. This closes the TXT-label/cache/HTML gaps in extension-only
rules. Keep reviewable summaries and reusable source outside those directories.
Ignoring does not move files or remove already tracked members. USB archival
remains a separate hash-verified operation; active path-bound inputs stay local.

## Live SSD readers — STORAGE-LIVE-01

Seven bulk report trees now use explicit read-only mappings, not symlinks. See
[storage operations](../reports/storage/README.md) and
[migration evidence](../reports/work/STORAGE-LIVE-01/handoff.md). Shared input/ref
helpers preserve logical identities; local output helpers reject mapped prefixes.
Do not move other corpus trees without verifying their actual consumers, especially
YOLO symlink exports. Prior experiment code pins remain historical; new execution
protocols must pin the updated readers. No training occurred during migration.

## October 3 — local archive migration authorized

Additional explicit maintainer approval covers the inactive Xcode DerivedData
folders `TVTestRig-bfjtodidumtdyagsgxcmwrmheuxr` and
`JoesProxy-dxemdjtrbsmajlcxomqjmywpxhsk`, plus GeneratorRunner's `Documents/dataset`
and `Documents/reconstruction` in iOS simulator
`F3EF9DB8-0B0F-4757-B653-D1628269F6FF`, app container
`C8AB9407-5AEE-427B-8350-B4B6C6B31A46`. This is a one-off exact-target cleanup,
not blanket Library/Simulator deletion authority. Preserve the running TTR build
`TVTestRig-fssavpzkujakgqggjglqjvvrtyoo`, app installations and other simulator data.
Delete only verified generated-data duplicates; archive unique bytes first.

Maintainer now designates `/Volumes/training-drive/data/NUIAK` for inactive repo
artifacts to reclaim internal space. This supersedes the prior cancellation for
local storage only, not SMB/SSH/service changes or new model/device execution.
Verify the mounted local volume before writing. Keep source, environments, current
build caches and active path-bound model inputs local. Archive inactive scratch and
recovery outputs to a new dated directory, recording exact original paths, membership,
SHA256 hashes and restore instructions. Verify complete copies and unchanged source
before removing exact local members; never delete an unverified original. Do not
create symlink replacements that bypass strict consumer path checks. Archived sealed
evidence can require restoration to its original path before replay; moving it is
not a new data admission. One external copy is an archive, not redundant backup.
Inventory and migration evidence: `reports/work/STORAGE-20261003/`.

## October 2 amendment — synthetic corpus lifecycle

[ADR-0017](ADR-0017-Corpus-Lifecycle-and-OS-Support.md) supersedes blanket preservation
or independent-backup prerequisites for replaceable synthetic bulk data. Keep recipes,
assets/licenses, versions, manifests and small historical references; preserve private
device captures and human corrections. Exact cleanup still requires assigned scope.
The maintainer authorizes local USB corpus/scratch storage for the native-focus spike
at `/Volumes/training-drive/data/NUIAK/NATIVE-FOCUS-EFFECT-SPIKE-26`, after mount
verification. The cancelled shared-drive/SSH investigation below remains cancelled.

Source control retains source, reusable tests, schemas, canonical plans, concise
reviewed result/decision handoffs and compact artifact hash indexes. It is not the
dataset or execution-log store. Artifact retention and model gates remain unchanged.

## New work

### Authorized external training storage — 2026-09-29 local date

**Cancelled2026-09-30:** this designation and migration/access plans are inactive.
Use project-local artifact storage and existing verified SharedStatusFile receipt
flow. No external-drive/SSH/SFTP/rsync retries, mounts, migrations or service changes.
External storage is not a prerequisite. Historical observations below are retained,
not current setup instructions. See DATA-EXTERNAL-01 closure for user-reported later
APFS reformat and failed permission repair; neither established filesystem/privacy
causation. Do not advise reformatting or broader access from those hypotheses.

Status amendment2026-09-30 09:05PDT: the same verified volume UUID and partition
UUID are now mounted at `/Volumes/training`; the existing folder is
`/Volumes/training/data_training`. Max's SMB share remains named `data_training`
and targets the new path. The old `/Volumes/Crucial X9` path is absent. This is an
observed rename, not a migration by this agent. No pipeline paths changed or writes
performed; preserve this identity binding when implementing future storage routing.
Remote authentication/write access remains unverified; coordination share absent.

Maintainer designated `/Volumes/Crucial X9/data_training` for large training data,
captures and checkpoints shared between machines, including Sillycon. This is a
specific exception to the project-only output boundary, not permission for arbitrary
external writes, capture, training, migration or deletion. Repository source, scripts,
environments, build caches and compact evidence/receipt indexes remain project-local.

Observed locally: existing directory on `/dev/disk6s2`, mounted exFAT at
`/Volumes/Crucial X9`, approximately1.8TiB available/45GiB used. Filesystem observation
does not prove Sillycon sharing, remote write access or an independent backup.
Initial restricted DiskManagement query failed; subsequent authorized read verified
volume UUID `F673FB8B-97D3-39F6-AF8A-AEA44CC42ED9` and disk/partition UUID
`6E1B6421-621C-4E34-B729-577503A66D84`. Verify identity again before automated writes.
Never create a replacement mount directory on the internal drive when absent.

Use separate producer-owned and consumer-owned dataset/run directories, immutable
versioned deliveries, file hashes and verified receipts. Avoid concurrent writers to
the same artifact. Treat exFAT as bulk-file storage, not a POSIX environment; do not
depend on symlinks, ownership or Unix executable permissions there. A single shared
drive is not an independent backup, and missing/disconnected storage must fail closed.

Existing manifests bind repository-local paths. Migration therefore needs a scoped
copy/hash verification, consumer path-resolution check and explicit cleanup decision;
do not move trees or replace them with symlinks blindly. No files moved/deleted by
this designation. Max's published SMB name `data_training` and local target were
verified; attempted endpoint `smb://192.168.1.21/data_training` has not qualified.
Latest user-supplied remote share-listing attempt fails authentication. Exact current
SMB account enablement/credentials remain operator checks; no password retained.
exFAT/FSKit incompatibility is a hypothesis, not an established cause. Do not enable
sharing, change permissions or assume the local path is remotely valid.

Coordination: designation published under packets.DATA-EXTERNAL-01 in verified
`/Volumes/SharedStatusFile/nuiak/status.yaml` at2026-09-30T04:04:49Z; schema/unique-key
validation and readback passed. Request nuiak-20260930-external-training-storage asks
for the existing remote endpoint only, not configuration changes or active-job
redirection. Peer acknowledgment pending.

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

The following describes September23 historical policy. October3 authorized cleanup
above supersedes its blanket no-move/no-delete wording; verified redundant recovery
drills were deleted and failed-capture evidence archived. See STORAGE-20261003.

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
