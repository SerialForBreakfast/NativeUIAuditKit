# Dependency residency repair attempt — 2026-09-22 17:51 UTC

Scope: restore existing dependency bytes, verify imports, then resume the isolated
FDR-007 export/parity if ready. No package replacement, training or promotion.

## Newly established evidence

Host-scoped `fileproviderctl evaluate` on the exact `.venv-yolo` folder reports:

- `isRecursivelyDownloaded=0`, `isKeepDownloaded=0`, `isSyncPaused=0`.
- Upload error NSFileProviderErrorDomain/-1003, underlying Cocoa4354: insufficient
  iCloud account quota. This is an **upload** error, not proof of the download cause.
- Documents' provider-domain attribute identifies Apple's
  `com.apple.CloudDocs.iCloudDriveFileProvider`. Provider identity is now established;
  no account credentials or bookmark data are retained in this report.
- Local disk has123GiB available; do not confuse account quota with local capacity.

Exact probe member:
`.venv-yolo/lib/python3.13/site-packages/coremltools/converters/libsvm/_libsvm_converter.py`.
Provider evaluation reports7189 bytes, uploaded1, downloaded0, downloading0,
downloadRequested0, keepDownloaded0, unresolvedConflicts0, trashed0.

## Bounded supported repair and verification

Executed Foundation `FileManager.default.startDownloadingUbiquitousItem(at:)`
for only that exact URL, through host-approved Swift with a60s subprocess bound,
project-local module cache and TMPDIR. It reported `isUbiquitousItem=true`,
accepted the download request and exited0. No provider settings were modified.
Apple describes this API as starting a download, not proving completion:
[API documentation](https://developer.apple.com/documentation/foundation/filemanager/startdownloadingubiquitousitem%28at%3A%29).

Subsequent provider evaluation still reports downloaded0/downloading0/requested0.
A single host-approved byte-read verification with a45s deadline exited1 in0.670s
with OS `TimeoutError: [Errno 60] Operation timed out`. Final metadata remains
`hidden,compressed,dataless`. No bytes/hash were obtained; request acceptance is
not successful materialization. Do not replay it or claim recursive residency.

No full import/export was repeated against this unchanged prerequisite.
`export-01` remains absent. No background diagnostic processes remain; iCloud's
internal request lifecycle is not claimed cancelled. No service resets, evictions,
permission changes, sync disabling, environment deletion or downloads from PyPI.

## Outcome and exact resume

- Software verification: prior exporter/parity evidence unchanged; diagnostic
  commands establish the current file-provider boundary.
- Data eligibility: no changes; existing frozen challenge retained.
- Integration: export/compile/parity blocked on unavailable dependency bytes.
- Model gates: not assessed; no artifact or promotion.

The authorized in-place restore did not materialize the probe file. Next choose:
maintainer restore/keep-download the existing environment through iCloud, or
authorize a separately pinned export environment outside cloud-managed Documents.
The latter requires explicit package-download/install and outside-project runtime
authority (including a skill exception to the normal `.venv-yolo` interpreter).
Proposed isolated location:
`/Users/josephmccraw/Library/Application Support/NativeUIAuditKit/Environments/focus-export-01`.
Keep model outputs/reports/caches in this project; preserve old dependencies and
checkpoints. Before creating it, verify destination absence, pin a compatible
Python/Torch/coremltools set from official sources, and record the changed runtime
as part of the parity evidence. No such installation has been performed.

Local-only result: SMB coordination not applicable. Documentation/diff verification
only; no unnecessary Swift package suite rerun for these diagnosis-only changes.
