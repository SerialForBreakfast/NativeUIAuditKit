# Storage cleanup — October 3, 2026

**Later expanded cleanup:** internal free space now39GiB after explicitly approved
inactive DerivedData and redundant GeneratorRunner output cleanup. See
[expanded handoff](generator-handoff.md); original results below retain their timestamps.

Maintainer authorized local external storage and deletion of unnecessary artifacts.
Completed without Git writes, model changes, simulator operations or service changes.

## Result and preservation

- Deleted two redundant recovery-drill copies without archiving:17,808,087,834
  content bytes (~16.6GiB). Both matched the surviving r6 prefix inventory:
  32,832files each; only `.DS_Store` excluded. Original prefix stays local.
- Archived three failed-capture trees:59,151content files/17,171,979,071bytes
  (~16.0GiB), then removed verified local duplicates.
- Archived four compressed transfer files:2,961,018,782bytes (~2.76GiB), then
  removed verified local copies. Extracted images, annotations and receipts stay local.
- Internal free space increased from5.9GiB to16GiB at final observation. Logical
  removed content is35.3GiB; this is not a promise of equal physical reclamation
  on APFS with shared blocks/snapshots or concurrent system activity. No snapshots
  were removed. `.build` footprint fell51GiB→19GiB; reports29GiB→26GiB.
- Source, environments, current build caches, shipped models, checkpoints, reviewed
  labels, accepted corpora and current transition evidence remain local. Exact
  29pair corpus revalidated with unchanged hash
  `9735108bf5ae011dfb17c07f7d49c4b42dfba4c9e1e027459a2b377047f589aa`.

## Archive location and mappings

Mounted local APFS volume observed as `/dev/disk25s1`, at
`/Volumes/training-drive` (1.8TiB capacity). Archive root:
`/Volumes/training-drive/data/NUIAK/archive-20261003`.
Device numbers may change on remount; verify the actual volume again before use.

| Original repo path | Archive-relative path |
|---|---|
| `.build/debug-output/p0c-resume/rejected-r2-capture` | `rejected-r2-capture` |
| `.build/debug-output/p0c-resume/rejected-r4-evidence` | `rejected-r4-evidence` |
| `.build/debug-output/p0c-resume/rejected-r5-evidence` | `rejected-r5-evidence` |
| `reports/work/FOCUS-APPEARANCE-06/artifacts/received/ttr-composition-d1-20261001-r1.tar.gz` | `transfers/ttr-composition-d1-20261001-r1.tar.gz` |
| `reports/work/FOCUS-RECORDED-STRUCTURAL-22/artifacts/ttr-structural-data64-20261002-r1.tar.gz` | `transfers/ttr-structural-data64-20261002-r1.tar.gz` |
| `reports/work/FOCUS-ARTWORK-08/artifacts/received/ttr-owned-white-artwork-20261001-r2.tar.gz` | `transfers/ttr-owned-white-artwork-20261001-r2.tar.gz` |
| `reports/work/FOCUS-APPEARANCE-06/artifacts/contract-received/ttr-composition-audit-20261001-r1.tar.gz` | `transfers/ttr-composition-audit-20261001-r1.tar.gz` |

Deleted redundant roots were `.build/debug-output/ios-retention-20260923/` children
`restored-content-v2` and `restored-prefix`. No independent unique pixels were lost;
both can be recreated from `.build/debug-output/p0c-resume/r6-verified-prefix`.
Historical failed-drill logs/strict inventory remain; failure concerned Finder metadata.

## Verification and recovery

Existing `scripts/corpus_retention.py` inventoried and SHA256-verified every corpus
file at destination and source before exact local deletion. Three content inventory
seals, respectively:

- r2: `27a91f0e7a18d9344e587de9b9367845f378e3b65859a3a1f89ac865d0674ba0`
- r4: `120a448faf940cd688c27996ce9d791a40adb29323fdfc6acca0d27d56eb1138`
- r5: `be3b10c1d2c9bcb354f75957991da6f10e3c3672e7e6364bc7ce38e6ace83fbe`

Local `*-content-inventory.json` files and archive `<name>-inventory.json` copies
contain full membership/hashes. `*-source-verification.json` and
`*-content-copy-verification.json` retain successful receipts. Initial r2 strict
copy verification failed because Finder changed `.DS_Store`; original was preserved,
failure retained, and the existing explicit metadata-exclusion mode verified all
content. No corpus/image/annotation exclusions were introduced.

Transfer packages passed SHA256 plus byte-for-byte `cmp`; complete mappings/hashes
are in `transfers.log`, also copied into the archive. Operational command scripts
remain `.build/storage-20261003.sh` and `.build/storage-transfers-20261003.sh`;
they are executed one-off journals, not rerunnable/resumable services.
Process inspection found no active train/capture/build job.75,361symlinks checked,
no incoming dependencies into the three rejected trees or two recovery-drill roots.
No tracked file was archived/deleted. No replacement symlinks were created.

To restore a corpus, first verify mount/free space and ensure original destination
does not exist. Example from repo root:

```sh
.venv-yolo/bin/python scripts/corpus_retention.py restore \
  --inventory reports/work/STORAGE-20261003/rejected-r2-capture-content-inventory.json \
  --copy /Volumes/training-drive/data/NUIAK/archive-20261003/rejected-r2-capture \
  --output .build/debug-output/p0c-resume/rejected-r2-capture
```

Restore other trees using their exact mappings. Restore a transfer package to its
original path only when absent; verify against `transfers.log` before use. Historical
path-bound replay may require restoration; copying paths into sealed manifests or
using symlinks is not a valid migration. Archive is a single retained copy, **not a
redundant backup**. Keep the drive available; no remote accessibility claim is made.

No code behavior changed; verification was content hashes, byte comparison, active
corpus validation and documentation diff review—not an unnecessary full model/build run.
Prior model/code edits preserved. Shared status is not applicable to local storage.

## Remaining cleanup recommendations

1. Add explicit storage-root resolution/migration checks for the remaining26GiB
   report evidence and12GiB reconstructed corpora before moving them. Current strict
   validators resolve paths inside the repo; blind moves would block experiments.
2. Retain environments (~2.7GiB), current Swift caches and model weights: deleting
   these saves little versus the rebuild/download/reproducibility cost. Remove only
   obsolete per-task build caches when their owners confirm they are inactive.
3. Store future inactive/raw bulk on the designated drive with compact local indexes;
   keep one working set internally. Recreate temporary recovery drills on demand,
   not as permanent duplicate datasets. Archive transfer packages after intake.
4. `.git` is only650MiB. Do not rewrite history or broadly clean ignored files;
   most valuable recovery images and checkpoints are intentionally ignored.
5. Maintain a second backup for irreplaceable captures/human corrections before
   eventually making the external drive their sole home. This cleanup does not
   authorize or configure a backup service or delete OS/Simulator storage.
