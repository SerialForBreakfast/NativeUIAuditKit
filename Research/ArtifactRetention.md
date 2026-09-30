# Repository artifacts and cleanup policy

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
