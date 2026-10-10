# Optional model distribution — implementation plan

October 8 preparation: [resident inventory and CLI checks](../../reports/work/MODEL-DISTRIBUTION-293/readiness.md) complete.
Task 293-A remains partial. Catalog validation passes; exact source selection, distribution review, and broad parity remain open.
Use existing baselines for observer testing. Do not describe current experimental transition candidates as release-ready.

Design: [ADR-0023](../ADR-0023-Optional-Model-Distribution.md).
Queue: [Tasks.md](../../Tasks.md#optional-model-distribution).

## Outcome and boundaries

TTR can install selected NUIAK models without including their bytes in its application.
Installed models work offline. Existing bundled clients keep their current behavior.
NUIAK owns model contracts, verification, loading, and inference. TTR owns its interface, storage permission, and selection policy.
Keep one inference implementation for both delivery methods.
The task queue records current status. This document defines contracts, not a second status queue.

Do not change model weights, preprocessing, thresholds, taxonomy, or qualification claims.
Do not train, capture, publish releases, create repositories, or change Git history under these implementation tasks.
Use existing qualified exports. Missing exports block only the affected artifact's release.
Public release and external TTR edits retain separate authority.
The first implementation uses a catalog pinned in code. Independent signed catalog updates remain a later task.

## Delivery tranches

| Tranche | Tasks | Complete outcome |
| --- | --- | --- |
| 1 — Local optional loading | 293-A, 293-B, 293-C | Resource-free consumer installs a local archive, validates it, loads it, and survives failure |
| 2 — Download and TTR use | 293-D, 293-E | Explicit per-model download, offline reuse, rollback, and TTR integration evidence |
| 3 — Release | 293-F | Approved immutable release with exact assets and a verified consumer download |

Start inventory and package separation without waiting for TTR's review.
The resource-free product exposes preview provider interfaces for TTR review. Do not tag them as a stable release before that review.
The native installer remains internal until its lifecycle and host checks pass.
TTR feedback blocks its integration agreement, not offline implementation and tests.
The October 8 review accepts explicit providers, with source delivery and integration tests still required.
Audit the macOS 14 requirement before changing the current macOS 15 package declarations.
Include both TTR's session consumer and its independent `FocusDetectorService` in the integration contract.
Prioritize tvOS detector delivery with optional FocusRing. Do not block that pilot on unrelated iOS source recovery.
Do not stop tranche 1 after a schema or downloader stub. Finish the real consumer path and failure checks.

## 293-A — Inventory and freeze the delivery contract

**Owner:** Maximum-mini-NUIAK. **Dependencies:** ADR-0023 and resident model files.

Inputs include `Package.swift`, `NativeUIModelAsset.swift`, `ModelRegistry.swift`, current manifests, and existing export/parity reports.
Inventory the iOS detector, tvOS detector, and FocusRing model separately.
Record exact source and compiled artifacts, hashes, sizes, licenses, preprocessing, tensor contracts, and supported execution hosts.
Separate the screenshot domain from the host OS.
Record missing exports and missing qualification evidence explicitly. Do not manufacture replacement exports.

Define a versioned catalog with mandatory archive identity, internal inventory, compatibility, task, and qualification fields.
Use exact model IDs and versions. Do not silently resolve historical aliases to different bytes.
Freeze initial limits for archive bytes, expanded bytes, file count, paths, requests, and compilation time before implementation tests.
Derive these limits from actual artifacts and record the chosen values.
Record TTR's requested models, host versions, storage policy, and provider requirements when its reply arrives.

**Tests:** validate catalog examples; reject missing hashes, duplicate IDs, unknown schemas, incompatible hosts, and ambiguous task mappings.
**Acceptance:** one inventory and contract identify every eligible artifact and every blocked artifact without changing model status.
**Evidence:** `reports/work/MODEL-DISTRIBUTION-293/inventory.json` and a compact contract review.
**Next:** give 293-B and 293-C exact contracts. Ask TTR only for unresolved consumer choices.

## 293-B — Separate model bytes from inference code

**Owner:** Maximum-mini-NUIAK. **Dependencies:** current package graph; 293-A supplies final catalog types.

Move shared contracts and validation into a resource-free target.
Add a resource-free inference product with an explicit model provider.
Keep current products as bundled compatibility adapters. Preserve their documented imports and default behavior.
Use forwarding or re-exported types where needed; do not copy inference logic into another target.
Make default detectors, sessions, and focus classification use the provider consistently.
Return a typed unavailable result when the optional provider has no selected compatible model.
Do not crash, download automatically, or silently choose another model.
Key session caches by exact artifact and preprocessing identity, not only platform.
The implemented key also includes the manifest and metadata. Providers keep their selected models fixed within a session.
Pin a loaded version for each active inference operation. Apply version changes to later operations.

**Tests:** compile both consumer paths; check absent models, selected versions, cache changes, and unchanged bundled behavior.
Use a minimal consumer project to inspect linked resources.
Reject a dependency graph that still brings the bundled model target into the optional product.
Distinguish application size from source checkout size. This task does not remove historical Git objects.

**Acceptance:** the optional consumer contains no model directories and builds without model downloads.
Existing bundled callers retain their API behavior and inference decisions.
**Evidence:** dependency graph, consumer resource inventory, compatibility tests, and proposed API notes.
**Next:** connect 293-C's installed-model provider to the real inference entrypoints.

## 293-C — Verify local archives and manage installed models

**Owner:** Maximum-mini-NUIAK. **Dependencies:** 293-A contract and 293-B provider integration.

Start with explicit local archive import. Use resident dependencies and project-local test storage.
Review available archive readers before adding a dependency. Do not implement unsafe shell extraction.
If no resident reader meets the contract, report that exact dependency decision before installation.

October 8: the native macOS `ditto` probe passes with pre-extraction validation and complete output verification.
Use an absolute executable path and argument array, not a shell. No third-party ZIP dependency is needed for this host probe.
Qualify Swift process handling, cancellation, bounded output, and TTR sandbox access before calling this an application installer.
Do not claim iOS installation support from macOS command-line results.

October 8 continuation: compilation and the initial load use a fixed helper process with a pinned hash.
Receipt version 2 checks completed output after restart and rejects changed host or helper identities.
Directory claims prevent duplicate imports across installer instances. Interrupted claims remain for review.
Low-space, timeout, cancellation, changed receipts, and changed output tests cover the local path.
The helper is not a security sandbox. Signed TTR execution remains unqualified.
Activation, removal, rollback, and handling models still in use remain open.
Use the [digest contract](../ModelDigestContract.md) for shared test vectors.

The next continuation adds an internal selection store for one host-owned storage root.
It verifies installations before activation and records the active and previous versions atomically.
The previous version remains protected until the host explicitly releases it.
A protected callback covers loading and inference. Removal rejects models while a callback still uses them.
Removal moves unused installations to a uniquely named recovery folder. Permanent cleanup remains a separate host action.
An OS file lock limits each root to one live store. The OS releases that lock when its process exits.
Tests cover another store, changed lock files, restart, failed writes, rollback, cancellation, and active calls during version changes.
Signed host interruption and abandoned installation claims still require qualification. Do not claim those from actor restart tests.

Verify the trusted archive hash before extraction. Enforce every frozen limit while extracting.
Reject traversal, links, duplicate or case-colliding paths, unexpected files, and paths outside staging.
Verify member hashes and the single declared model root.
Compile the source model asynchronously using Core ML. Validate actual tensor shapes and preprocessing contracts.
Use a bounded test input to check loading before activation.
Record source identity separately from compiled output identity.

Define these states: absent, installing, ready, active, failed, and removing.
Serialize installation for each artifact. Define cancellation behavior for multiple callers sharing one installation.
Use operation-owned staging and atomic completion on the destination volume.
Keep a durable record so interrupted installs cannot appear ready after restart.
Do not remove an active model or the retained rollback version without the host's explicit action.
Keep compiled cache keys sensitive to source, OS/build, architecture, and relevant configuration.
Protect a verified active model when compilation, cleanup, or replacement fails.

**Tests:** corrupt archive, invalid members, low space, interrupted writes, failed compilation, concurrent import, stale cache, removal, and rollback.
Use deterministic test archives for failure tests. Keep offline package tests independent of network and Simulator access.
Run real Core ML compilation and parity checks separately on available supported hosts.
If a host is unavailable, report that support as unverified.

**Acceptance:** one real local model loads through the optional consumer and matches its bundled reference within existing parity tolerances.
Failed installs preserve the active model. Restart restores only verified completed installations.
**Evidence:** installation receipts, parity results, failure reports, and storage inventory.
**Next:** reuse the same installer in 293-D. Do not create a second download-specific validation path.

## 293-D — Add explicit, bounded model downloads

**Owner:** Maximum-mini-NUIAK. **Dependencies:** 293-C; 293-A catalog and delivery policy.

The internal transfer implementation now has a [bounded download contract](../ModelDownloadContract.md).
It consumes a trusted selected entry, not a remote catalog. Full catalog admission remains a separate host integration requirement.
Offline tests use 2 packaging versions of the same tvOS model. Do not count these as 2 independently qualified model families.
Live endpoint and signed TTR checks remain open even when offline transfer tests pass.

Use `URLSession` behind an injectable transport. The host starts each download explicitly.
Enforce HTTPS, allowed destinations, redirect rules, response sizes, request deadlines, and cancellation.
Do not send credentials across redirected hosts. Do not embed GitHub tokens.
Handle missing assets, rate limits, TLS failure, changed server content, and interrupted responses without retry loops.
Use a validated entity identity for resume. If it changes, discard only the owned partial file and restart explicitly.
Keep transfer completion, installation, and activation as separate events.
Report progress and exact failure reasons. Reuse verified installed bytes instead of downloading again.
Do not add a persistent service or perform a network request during package build or application startup.

**Tests:** mocked transport success and failures, truncated responses, changed resume identity, redirects, cancellation, and duplicate requests.
The required Swift suite remains fully offline.
A separate controlled-server test needs an approved endpoint and service scope. Do not start a server implicitly.

**Acceptance:** 2 independently selected model versions complete the same verified installation path.
Both reload with network access disabled. A failed update leaves the selected version usable.
**Evidence:** transfer receipts, size/time measurements, offline reload, and error-path reports.
**Next:** supply a source-level integration contract and exact local test inputs to 293-E.

## 293-E — Qualify optional use in TTR

**Owners:** Sillycon-TTR owns its source changes. Maximum-mini-TTR tests the consuming build under its assignment.
Maximum-mini-NUIAK owns package behavior and parity evidence.
**Dependencies:** 293-B through 293-D and a TTR review of request `nuiak-model-distribution293-ttr-review-01`.

TTR chooses which model or pipeline to install. Show purpose, size, version, qualification limits, progress, and current state.
TTR supplies an approved storage location and its normal folder-access handling.
TTR exposes cancel, remove, version selection, and rollback where supported by the agreed contract.
Missing optional models do not stop TTR's other capabilities.
If TTR uses an explicit fallback, record that method in its output.
Keep shadow evaluation separate from navigation authority.

Test a TTR build with no bundled models and no download during startup.
Install 2 distinct eligible models. Verify offline use, denied access, revoked external access, cancellation, and restart.
Compare loaded identities and fixed-input results against the NUIAK reference.
Check that a model update does not replace the model inside an active comparison.
Record application size, installed size, compilation time, first-load time, and warm latency.

**Acceptance:** TTR returns exact build/artifact identities and completes the agreed positive and failure scenarios.
**Evidence:** source revision, test receipts, parity report, and remaining platform gaps.
**Next:** approve only supported delivery combinations for 293-F. Do not infer artifact release approval from successful integration.

## 293-F — Publish and verify approved model releases

**Owners:** maintainer owns Git and hosting changes; Maximum-mini-NUIAK prepares release evidence and verifies consumption.
**Dependencies:** accepted artifacts, distribution rights, hosting approval, and 293-E integration evidence.

Obtain the exact repository name, visibility, and publication scope before external writes.
Prepare immutable version names, model archives, inventories, license notices, and a pinned catalog update.
Review every artifact's qualification scope and prevent experimental weights from entering a stable catalog.
Provide exact maintainer commands for draft creation, asset upload, verification, and publication.
Do not execute Git writes or public uploads from the preparation task.
The maintainer enables release immutability before publication where available.

After authorized publication, download each named asset through the production path.
Verify its size, hash, model contract, and fixed-input parity.
Test a missing release without disturbing a previously installed model.
Document rollback to an already approved version. New bytes require a new version and catalog entry.

**Acceptance:** published bytes match the approved package; the optional consumer installs them and works offline.
**Evidence:** exact release links, artifact hashes, consumer receipts, and supported-host results.
**Next:** maintain this contract for future qualified model versions. Signed remote catalogs need a separate scoped design.

## Verification and handoff

Run focused tests after each changed mechanism. Run one offline Swift build/test pass after each integrated code tranche.
Reuse unchanged artifact and parity evidence. Do not train a model to test distribution.
Keep large archives under the approved storage policy. Commit source, schemas, test fixtures, and compact summaries only.
Keep publication, readback, peer acknowledgment, installation, and model acceptance as separate facts.
Report software verification, artifact eligibility, TTR integration, and model quality independently.
Distribution work changes no existing model-quality gate.

The current assignment creates the plan and queue entries. It does not claim implementation or release completion.
