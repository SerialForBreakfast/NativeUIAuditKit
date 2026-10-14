# REVIEW305: source and notice preparation

**Superseded model archive:** use REVIEW306 for public distribution.
The final privacy scan finds personal information in REVIEW305's embedded Core ML data.
The source archives remain usable. The rebuilt model removes the detected information and preserves retained-image parity.
The public files are in `reports/work/RELEASE-305/public306/`.
The model ZIP has SHA-256 `c2f7b8e7d60a17f4859e4f00ce93ccf03f2ddf0bc6c06aa64ec5ed7ab30c0954`.
Do not publish REVIEW304 or REVIEW305 model ZIPs.

Owner: Maximum-mini-NUIAK. Date: 2026-10-09.

## Completed work

The replacement model archive contains the full AGPL text, MIT notice, and attribution.
The model weights and runtime contract remain unchanged.
REVIEW304 and its GitHub draft remain unchanged.

The exact replacement archive passes compilation, installation, and public-provider loading.
It returns the same 25 detections as the shipped model.
This result verifies local integration, not new model accuracy or TTR execution.

The separate source archive contains 746 files.
It includes the historical trainer, exporter, generator, category map, and 25 tvOS templates.
It also includes resident Ultralytics source for training and export, configuration, and notices.
The archive excludes datasets, checkpoints, images, caches, credentials, and dependency binaries.
Configuration uses relative paths. Original configuration remains unchanged.

## Source audit

The historical NUIAK commit is `dd7b4a7fd6dd187504b2f2c1aea2ad534d67c6ec`.
All 354 selected files from Ultralytics 8.4.153 match their resident package records.
Of 353 selected files from Ultralytics 8.4.124, 2 differ from their package records:

- `ultralytics/data/base.py`
- `ultralytics/utils/patches.py`

The experiment log records image-read fallback changes on 2026-09-09 in these files.
The archive preserves the current modified files. The audit records their hashes and original package hashes.
This evidence does not prove that these exact bytes ran during Run 012.
Package records also do not independently authenticate upstream source.

## Exact artifacts

Outputs remain in `reports/work/RELEASE-305/`.

| Artifact | SHA-256 |
| --- | --- |
| `nativeui-tvos-v3.0-review305.zip` | `80361d6b5eba1d33446eb1130f97b09da4a7b6f9a50021af6f30ae06106d7d2b` |
| `nativeui-tvos-source-review305.zip` | `519f674e6d54f5fe42ec96035b6de15f0057ac4c7d3bb43d07cab1104b430db3` |
| `catalog-review.json` | `58e6464ab3c227263fe63a93a9d7b3a5ddc4979f2f5c04fcd4abeba003e3494d` |

`source-audit.json` records every source member and package comparison.
`verified/review-receipt.json` records the exact model archive and 25 matching detections.
`SHA256SUMS` records the archive, catalog, and audit hashes.

## Verification

The final focused Python suite passes 24 tests.
The offline Swift build succeeds. All 173 Swift tests pass.
The final REVIEW306 archive passes the native test with 25 matching detections.
The final scan finds no current personal identifier, `/Users/` path, or `/home/` path in that model archive.
Logs remain in the REVIEW305 output directory.
No Git write, model training, public upload, or release publication occurs.
The coordinator stores the correction under `nuiak-release306-source-complete-privacy-fix-01`.
No forwarding or TTR acknowledgment is verified at handoff.

## Remaining publication requirements

The [publication review](ModelPublicationReview305.md) now includes completed editable-source preparation and exact manual GitHub steps.
The sanitized checkpoint removes 5 personal paths without changing any of 503 tensor storage files.
The historical exporter succeeds. Native replay matches all 25 detections with 0 mismatches.
The source supplement includes instructions, dated changes, notices, and both verification receipts.
Its hash is `36318403371b09265049c1a7a91ac85d17399672aa16b67bcc732de3b8031cbd`.
Do not upload the original checkpoint.
Historical scripts can contain old paths and assumptions. This work does not verify reproduction of training.
Sillycon-TTR must identify its application distribution terms, source access, and third-party restrictions for its own release.
NUIAK can complete its model release review independently. This does not clear TTR's application distribution.
No repository-wide license change occurs here.

Do not publish `models-review304` as the final licensed release.
Do not overwrite its uploaded assets.
The maintainer reviews the 7-asset preview inventory and runs the supplied GitHub commands.
Do not use the reserved REVIEW305 URL before its release exists.

## Next substantial tranche

Publish the reviewed NUIAK source and model archives through a new GitHub preview release.
Keep TTR's application distribution review separate.
Verify anonymous download, hashes, TTR import, offline reload, and failure handling.
Keep navigation authority disabled during this integration test.
