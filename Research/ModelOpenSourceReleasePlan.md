# Open-source model release checklist

Owner: Maximum-mini-NUIAK. Selected path: free distribution with applicable AGPL obligations.
The maintainer approves this path after the REVIEW304 license review.
No commercial license purchase is planned. No repository-wide relicensing occurs in this step.
The existing GitHub draft remains unpublished until the checklist is complete.

## Source evidence found

Run 012's source commit is `dd7b4a7fd6dd187504b2f2c1aea2ad534d67c6ec`.
The commit identifies the 25-family tvOS detector and includes these source files:

- `scripts/generate_tvos_dataset.swift`
- `scripts/export_tvos_coco.py`
- `scripts/train_tvos_model.py`
- `scripts/export_yolo_coreml.py`
- 25 Swift templates under `NativeUIDatasetGenerator/Templates/tvOS/`

The exporter at that commit has SHA-256 `8dcf2bbbeb67c7b0fff97021f5a9799922e9910a28f8419ea0d9cb9d1970f6ef`.
The recorded export uses Python 3.12 in `.venv-coreml`.
That resident environment contains Ultralytics 8.4.153, matching model metadata.
Its license text matches `Licenses/AGPL-3.0.txt` byte for byte.
This evidence removes the unexplained version mismatch. It does not prove every historical dependency or modification.

One history query reports an older missing Git object.
The exact Run 012 commit and inspected source objects remain readable. Do not repair or rewrite Git history for this review.

## Finish the source package

[REVIEW305 results](Release305Results.md) record completed packaging, the source audit, and exact-archive parity.
Source completeness and TTR distribution scope remain publication requirements.
Update: the editable supplement and tested export procedure are complete.
Use [REVIEW306 publication steps](ModelPublicationReview305.md). Do not publish the older model archives after the final privacy finding.
The maintainer reviews NUIAK's exact preview inventory. TTR reviews its application distribution separately.

Maximum-mini-NUIAK performs these steps:

1. Inventory relevant files from the exact Run 012 commit, including template dependencies and export patches.
2. Compare the resident export code with its package records and identify modifications.
3. Record checkpoint, initialization, source-package, and tool identities separately.
4. Create sanitized configuration copies without personal paths. Preserve the originals privately.
5. Review source access and the material required for the selected distribution under the applicable terms.
6. Prepare a bounded source archive with hashes and durable source links.

Do not include unrelated datasets, screenshots, credentials, caches, or compiled Python files.
Do not claim the current trainer is the exact historical trainer merely because its filename matches.
Do not claim that retraining is necessary solely because historical provenance needs review.

## Finish notices and model packaging

Keep the model weights unchanged.
Include attribution, dated modification information, warranty terms, and the full applicable license text.
Preserve MIT copyright and permission notices for included original code.
Use the packer's existing notice-file boundary unless a tested extension is needed.
Do not overwrite REVIEW304's uploaded archive. New archive bytes receive a new identity and checksum.
Run the exact archive through compilation, public-provider loading, and the retained parity check.

## Coordinate TTR's distribution

Sillycon-TTR identifies its intended application distribution, source access, and any incompatible third-party conditions.
Maximum-mini-NUIAK provides the model terms and source package references.
The maintainer reviews the combined distribution scope before changing either project's declared license.
Public hosting and optional downloads do not resolve this scope by themselves.
If the scope is unclear, request qualified advice rather than inventing an exemption.

## Publish and verify

The maintainer reviews the exact release inventory and publishes through GitHub Releases.
Maximum-mini-NUIAK verifies anonymous downloads, archive hashes, source links, and catalog identity.
Sillycon-TTR returns its actual download, import, offline-reload, and failure-test results.
Keep model quality, integration results, and licensing review as separate records.
The final handoff names remaining host limits and does not grant navigation authority.
