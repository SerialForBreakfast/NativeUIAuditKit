# Model release preparation contract v1

Tool: `scripts/model_release.py`. This is offline maintainer tooling, not an application downloader or installer.
The trusted catalog comes from a reviewed code release. Do not trust a catalog merely because its archive contains matching hashes.

## Catalog

The root has exactly `schemaVersion: 1` and a nonempty `models` array.
Each entry has these required fields:

- `modelID`, `artifactVersion`, `task`, and `screenshotDomain` identify one exact supported model.
- `modelRoot` names one top-level source `.mlpackage` directory.
- `files` lists each relative path, byte count, and SHA-256.
- `expandedBytes`, `archiveBytes`, and `archiveSHA256` identify exact payload and archive bytes.
- `url` pins an HTTPS GitHub release asset. Credentials, mutable tags, queries, and fragments are rejected.
- `hosts` lists platform, minimum version, and evidence. Screenshot domain is not the execution host.
- `runtimeContract` is `nuiak-model-v1`.
- `preprocessing` records the exact preprocessing version.
- `tensorContractSHA256` matches `contract.json` in the inventory.
- `licensePath` identifies a nonempty notice file outside the source model directory.
- `qualification` describes the permitted use and known limits.
- `sourceRevision` records the producer or export revision.
- `releaseStatus` is `review-only` or `approved`.
- `approvalReference` links the maintainer's exact decision when publication is requested.

Unknown fields, unknown versions, duplicate artifact identities, invalid hashes, and ambiguous task mappings fail validation.
The tool validates structure and declared identity. It cannot prove truthful labels, legal rights, minimum-host support, or model quality.
No production catalog is approved yet. Tests create artificial packages; those packages are not trained models.

## Limits and format

Use at most 32 MiB per archive, 64 MiB expanded, 256 files, and 512 UTF-8 bytes per relative path.
FocusRing source packages additionally retain the existing 5,000,000-byte gate.
Use stored ZIP entries with fixed timestamps and regular-file modes. Model weights already dominate these small packages.
Do not include executable files, links, absolute paths, traversal, case collisions, or undeclared members.
The verifier reads archive members without extracting them. It verifies the trusted archive hash first.
The optional `native-probe` uses those verified bytes with macOS `ditto` in a new private directory.
It checks every extracted file and leaves a receipt only after verification. It does not install or activate models.
Actual application extraction, compilation, activation, cancellation, and rollback remain separate implementation requirements.

The internal Swift `ModelArchive` reader now enforces the stored ZIP subset before native extraction.
The internal `NativeModelInstaller` preserves failed attempts and atomically finishes a validated local installation.
It remains a prototype, not a public downloader or complete model manager.
The [digest contract](ModelDigestContract.md) distinguishes archive, source, and compiled identities.
Compilation uses a hash-pinned helper. Receipt version 2 permits verified reuse on the same host version and architecture.
Interrupted claims require explicit review. The installer does not select or remove active models.
See [Sillycon-TTR handoff](TTRModelHandoff.md) for actual parity results and remaining lifecycle checks.
The [internal downloader](ModelDownloadContract.md) now transfers a trusted selected entry and reuses this verified installation path.
It does not replace the full catalog validator or approve a release.

## Commands

```sh
.venv-yolo/bin/python scripts/model_release.py audit --output reports/work/RELEASE-300/new-audit.json
.venv-yolo/bin/python scripts/model_release.py validate path/to/catalog.json --publication
.venv-yolo/bin/python scripts/model_release.py pack path/to/reviewed-payload path/to/inventory.json path/to/new.zip
.venv-yolo/bin/python scripts/model_release.py verify path/to/entry.json path/to/new.zip --publication
.venv-yolo/bin/python scripts/model_release.py native-probe path/to/entry.json path/to/new.zip reports/work/RELEASE-300/new-probe
```

Use a new project-local output path. The tool rejects overwriting an archive or placing it inside its source directory.
Preserve interrupted output as failed evidence. Do not treat successful packing as publication approval.
Keep catalogs and checksums outside the archive to avoid circular hashes.
The archive contains the source model, `contract.json`, and its declared notice file only.
Review filesystem space and the approved source inventory before packing actual model artifacts.
