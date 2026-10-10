# ADR-0023 — Optional downloads for Core ML models

- Date: October 7, 2026.
- Status: Proposed. TTR feedback and implementation remain pending.
- Owner: Maximum-mini-NUIAK owns the package and model contracts. TTR owns its download interface and application policy.
- Scope: Deliver selected models without bundling every model in TTR.

The maintainer requests implementation tasks on October 7. [Canonical plan](Plans/OptionalModelDistribution.md) defines tasks 293-A through 293-F.
The design remains proposed pending TTR review. Task creation does not authorize publication or mark the interface accepted.

## Decision

Use SPM for inference code and small model descriptions. Use GitHub Releases for separate, versioned model archives.
TTR explicitly requests a model. NUIAK verifies, compiles, and loads that model from local storage.
Keep model selection optional. A missing model does not prevent TTR from starting or using its other tools.
Do not download during package resolution, application startup, or a build script.
Do not use Git LFS or raw Git files as the application download interface.

Prefer a dedicated model-release repository after the maintainer approves its name, visibility, and distribution rights.
Keep only manifests, release tooling, and documentation in that repository's Git history.
Attach each model archive to an exact release tag. Do not select production models through a mutable `latest` URL.
Enable release immutability before the first publication, where the repository supports it.
Create a draft, attach all verified files, then publish. Corrections require a new version.
GitHub documents this release sequence and its asset protections. [Release management](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository).

## Initial code requires separation

October 8 implementation adds the resource-free runtime and bundled adapters described below.
The installer remains internal. [Sillycon-TTR handoff](TTRModelHandoff.md) records verified behavior and remaining release requirements.
The following paragraphs describe the initial package structure.

The root `Package.swift` defines both the inference and model products.
The inference target requires `NativeUIAuditKitModels`, which copies 3 compiled model directories into resources.
The default detector and session call bundled loaders in `NativeUIModelAsset.swift`.
The session currently caches detectors by platform. Downloaded versions need a more precise cache identity.
The focus classifier accepts an `MLModel` internally, but its ordinary loading path still uses bundled resources.

A downloader alone does not remove these resources from TTR.
Separate model contracts from model bytes. Do not make the optional runtime product depend on the bundled asset target.

Proposed package boundaries:

| Component | Contents | Model bytes |
| --- | --- | --- |
| Contracts | Descriptions, taxonomy, preprocessing contracts, validation | None |
| Runtime | Existing inference with an injected model provider | None |
| Downloads | Explicit download, verification, compilation, local storage | Only after a request |
| Bundled adapter | Compatibility path for existing clients and offline deployments | Explicitly selected resources |

These names describe boundaries, not approved public API names.
Keep the existing product as a compatibility adapter initially. Add a resource-free product for TTR.
Avoid duplicate inference implementations. Both adapters use the same inference code.
Moving weights out of current Git files does not remove old Git history. History cleanup remains a separate maintainer decision.

## Model catalog

Create one catalog entry per exact artifact version. Give different tasks distinct model IDs.
Start with the iOS detector, tvOS detector, and FocusRing classifier only after their release checks pass.
Do not publish an experimental transition checkpoint as a qualified Core ML model.
Transition models need their own conversion, preprocessing, and parity evidence before catalog admission.
An existing bundled model is not automatically approved for public redistribution.

Each entry contains:

- Schema version, model ID, artifact version, and task.
- Exact release URL, archive bytes, expanded bytes, and SHA-256.
- Internal file inventory with hashes and one declared model root.
- Minimum host OS, supported host platforms, model format, and compatible runtime contract versions.
- Screenshot domain, separately from the host that executes Core ML.
- Input/output descriptions, taxonomy mapping, preprocessing version, and decision settings.
- Qualification scope, evidence reference, source/export versions, and license notices.
- Optional dependencies and their exact versions, if the selected pipeline needs more than one model.

For example, a tvOS screenshot detector can execute on a macOS host. Do not confuse screenshot domain with runtime support.
Reject unknown schemas, unsupported contracts, missing required fields, and mismatched tensor definitions.
Do not map a requested old model ID silently to different weights.

## Artifact format and compilation

Prefer a ZIP containing the qualified source `.mlpackage`, its contract, file inventory, and license notices.
Allow `.mlmodel` for models that use that format.
Compile on the consuming host with the supported asynchronous Core ML API. Keep compilation off the main thread.
Apple documents downloading models, local compilation, and loading the compiled result. [Apple guidance](https://developer.apple.com/documentation/coreml/downloading-and-compiling-a-model-on-the-user-s-device).
The existing exports require a spike to verify package compilation across the declared minimum OS versions.
Do not assume today's compiled `.mlmodelc` directories work on every future host or OS.
If a source export is missing, stop that model's release until an exact export and parity check exist.

Treat compiled output as a local derivative, not the canonical release identity.
Record the source archive hash and local compiled inventory separately.
Key compiled caches by source hash, host OS/build, architecture, and relevant runtime configuration.
Recompile after incompatible runtime changes. Retain the previous working version until replacement passes checks.

## Trust and safe installation

For the first version, ship a small pinned catalog with the code package.
The catalog fixes archive hashes and allowed release URLs. HTTPS protects transport.
A hash from the same untrusted download does not authenticate the model. The trusted catalog supplies the expected hash.
This first version requires a code update to authorize new artifact versions, but does not bundle model bytes.
If independent catalog updates become necessary, add signed catalogs with pinned verification keys and explicit key rotation.
Define expiry, revocation, and rollback behavior before enabling remote catalog updates. Do not accept unsigned mutable catalogs.

The loader performs these steps:

1. Check explicit host consent, model compatibility, and available space.
2. Download to an operation-owned staging location with byte and time limits.
3. Validate HTTPS redirects against an explicit delivery policy. Never forward credentials to another host.
4. Check archive size and SHA-256 before extraction.
5. Reject traversal, absolute paths, links, duplicate names, unexpected members, and expanded-size violations.
6. Check every extracted file against the trusted inventory.
7. Compile the declared model and validate its actual input/output contract.
8. Run a bounded load and inference check with approved nonprivate test inputs.
9. Install the complete result atomically and record its identity.
10. Activate the version only under the host's selection policy.

Do not execute downloaded scripts, plugins, or build hooks.
Concurrent requests share one operation per artifact. Cancellation and interruption leave the active model intact.
Resume only when the partial file still matches the exact artifact; otherwise start a new staging file.
Keep previous working models for rollback. Do not replace a model during an active capture or comparison.
Reset session caches when the selected model changes. Key loaded models by artifact identity, not only platform.

## Storage and TTR behavior

Use the application's permitted storage for installed models. Keep disposable staging and compiled caches separate.
Exclude re-downloadable model files from backups where platform rules permit.
Support a user-selected external directory only through the host's normal folder-access workflow.
Do not depend on another app's container or inherit its folder permission.
TTR owns sandbox entitlements, folder selection, and access repair. NUIAK receives an approved destination.

Show each model's purpose, version, download size, expanded space estimate, qualification limits, and installation state.
Offer explicit download, cancel, select version, rollback, and remove actions.
If no compatible model exists, report unavailable. Do not silently substitute a different model or heuristic.
An explicit host fallback remains possible, but its output must identify the method actually used.
Once installed, inference works offline. Network failure does not break the last verified installation.
Record model and preprocessing identities with every evaluation or shadow result.
Model installation grants no navigation authority and does not change TTR's action permissions.

## Hosting choices

| Option | Decision | Reason |
| --- | --- | --- |
| GitHub Releases | Preferred first host | Separate binary downloads with exact versions; no weight history in Git |
| SPM resource bundle | Keep as explicit legacy option | Good for offline installation, but resources remain in the application |
| SPM binary target | Do not use as runtime download mechanism | Resolves build dependencies, not user-selected model installation |
| Git LFS or raw files | Do not use for application delivery | Adds repository and tooling coupling without a model lifecycle |
| Object storage/CDN | Later alternative | Useful when delivery needs exceed release hosting; keep the same catalog contract |
| Private GitHub Releases | Separate authentication design | Do not embed a shared GitHub token in an application |

SwiftPM documents target resources and binary dependencies separately. Neither is an application model manager.
[SwiftPM package description](https://docs.swift.org/package-manager/PackageDescription/PackageDescription.html).
GitHub currently documents a limit of 1,000 assets per release and less than 2 GiB per asset.
These models do not require a large hosting system solely because several models exist.
[GitHub release limits](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases).
Release hosting has no application uptime guarantee in this design. Preserve offline operation and exact artifact mirrors if later required.

## Implementation sequence and acceptance

1. Inventory exact release candidates, source exports, contracts, licenses, and artifact sizes.
2. Add a resource-free runtime path while preserving bundled behavior and existing tests.
3. Implement the pinned catalog, local import, safe extraction, and compilation with offline fixtures.
4. Add explicit downloads and test interrupted transfers against a controlled test server.
5. Integrate TTR's optional model interface under its own assignment.
6. Publish only after maintainer repository approval and each artifact's qualification checks.

Acceptance includes a TTR build with no bundled model directories and no network access during build or startup.
Test 2 independent model installations, offline reload, cancellation, low space, corrupt bytes, incompatible contracts, and rollback.
Test denied folder access, revoked external access, concurrent requests, stale session caches, and failed compilation.
Require identical decisions and accepted numerical parity against each qualified bundled model on fixed inputs.
Measure installed size, first-load time, compilation time, and warm inference latency.
Run focused tests and the required offline Swift build/test pass when implementation occurs.
This ADR changes no code, package dependency, release, repository visibility, or model qualification.

## Feedback requested from TTR

- Which models should users select independently, and which tasks need a complete model set?
- What runtime/provider interface fits TTR's current optional NUIAK modules?
- Which host OS versions and distribution channels require support?
- Should pinned versions or independent signed catalog updates be available first?
- Where should models live, and how should TTR show external-folder failures?
- Which fallback, update, cancellation, and rollback behaviors should the interface expose?
- Does TTR already have a verified downloader or archive reader that we should reuse?

Maximum-mini-NUIAK requests review through BigDog-Coordinator. Sillycon-TTR can review source design; Maximum-mini-TTR later qualifies the consuming build.
Repository publication, signing-key setup, and public asset uploads require separate explicit authority.
