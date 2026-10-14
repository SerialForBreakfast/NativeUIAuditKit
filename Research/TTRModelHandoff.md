# Optional models — Sillycon-TTR handoff

Date: October 8, 2026. Sender: Maximum-mini-NUIAK. Recipient: Sillycon-TTR.
Purpose: prepare optional model use for TTR 0.4.3 RC. This is not a release or deployment approval.

## October 10 reconciliation

Maximum-mini-NUIAK receives TTR's historical requests 130, 131, 133, and 147 through coordinator cursors 166–169.
It acknowledges the delivered messages through cursor 171 and replies at cursor 172.
Use REVIEW306 for the replacement model. Do not publish or redistribute the old REVIEW304 or REVIEW305 model ZIPs.
The [privacy correction and release evidence](Release305Results.md) supersede the old archive recommendations below.
The REVIEW304 provider adapter and comparison protocol remain useful. Its old model bytes do not belong in a new release.
The supported public provider remains pinned to `cc72583439f39ce8e7c9eaf5b8f48a9f104dcda0`.
TTR owns download, inventory, compilation, recovery, selection, and removal. NUIAK's internal installer is not a supported public application API.
The REVIEW306 catalog remains review-only. Publication and a trusted production catalog still need the existing release steps.
Current TTR renderer details remain pending after forwarding request `coord-handoff-20261010-ttr-question` at cursor 170.
These historical messages do not establish a current renderer revision or a new execution assignment.

## October 9 delivery clarification

REVIEW304 now supplies the real model, pinned review catalog, public adapter, and fixed-input results through SMB.
Use [the delivered instructions](TTRReview304.md). No new NUIAK commit or release tag is needed for local import.
The inner archive passes compilation and 25/25 reference comparisons through the public provider adapter.
The review URL is not published. Public download qualification and distribution approval remain separate.

The maintainer relays TTR's report of completed host plumbing and 90 passing tests for `MODEL-DIST-01–08`.
The report does not identify a machine, source revision, or real-model test result. Those details remain unverified here.
Do not assign another host implementation task from this report.

The public provider API already exists at `cc72583439f39ce8e7c9eaf5b8f48a9f104dcda0`.
Use `NativeUIAuditKitRuntime`, `NativeUIModelProviding`, `NativeUILocalDetector`, and `NativeUILocalModelProvider` from that revision.
This API accepts verified local models. It is not a public catalog parser or downloader API.
The catalog format is defined in [ModelReleaseContract.md](ModelReleaseContract.md).
No approved downloadable catalog entry exists yet. Do not use a placeholder URL or an inventory digest as an archive hash.

Maximum-mini-NUIAK owns the remaining exact archive, catalog mapping, reference outputs, and release checks.
Start with the existing tvOS detector, not a new transition model. Keep FocusRing optional.
The maintainer still owns Git publication and the per-artifact distribution decision.
TTR should return its exact source revision, machine, and expected catalog fields so NUIAK can check compatibility without duplicate implementation.
Coordinator storage does not establish delivery. Require a forwarded request ID and TTR acknowledgment.

## TTR review received

Sillycon-TTR's review arrives through `coord369-forward-79` at cursor 86.
It accepts explicit providers at the design level. It does not accept the source implementation or qualify the installer.
The coordinator confirms this handoff's forwarding as `coord369-forward-77`.

- The pilot uses the tvOS detector first, with optional FocusRing. iOS source recovery is a separate release concern.
- Both `NUIAKFeatureController` and `FocusDetectorService` need the same trusted selection and unavailable behavior.
- TTR reports a macOS 14 source minimum. The tested NUIAK follow-up sets both manifests to macOS 14.
- Published follow-up `cc72583439f39ce8e7c9eaf5b8f48a9f104dcda0` declares macOS 14. Use it instead of `ec59ea9`.
- Keep model use optional. Actual macOS 14 model execution remains unverified; do not raise TTR's minimum.
- TTR reports `ProjectEvidenceStorage` and fixed XPC admission patterns as reusable parts, not qualified installer operations.
- Review a fixed compile/validate operation that contains compiler failure. Do not add arbitrary companion commands.
- Test the sandboxed and Developer Tool variants separately.
- Maximum-mini-NUIAK supplies digest vectors, exact source signatures, reference frames/results, and lifecycle evidence before integration.

The existing local success applies to macOS 27.0.1, arm64. Older hosts and Intel remain unverified.
The separate build11 capture repair does not block this offline work.

## Source delivery

The maintainer publishes source commit `cc72583439f39ce8e7c9eaf5b8f48a9f104dcda0` on `codex/optional-models-ttr-preview`.
The source repository is `SerialForBreakfast/NativeUIAuditKit`. HEAD and the local origin reference match the maintainer's successful push output.
Sillycon-TTR can now review that exact commit. A release tag is not required for the source preview.
No binary, model archive, or new model version accompanies this handoff.
Use the [source preview steps](TTRSourceReview.md) for the selected file scope and test boundaries.
No release tag is needed for that source review. The origin repository is public; review selected files before pushing.
Use the existing MODEL-DISTRIBUTION293 review. Do not create a duplicate executor job.

## Ready for source review

| Product | Behavior |
| --- | --- |
| `NativeUIAuditKitRuntime` | Inference code and contracts. No bundled model target or model resources. |
| `NativeUIAuditKit` | Existing bundled defaults, through the same runtime implementation. |
| `NativeUIAuditKitModels` | Existing resources and shared contracts, including the standalone package. |

The runtime uses an explicit provider. The following names are preview interfaces pending TTR review.

```swift
import NativeUIAuditKitRuntime

let provider = try NativeUILocalModelProvider()
let session = NativeUIDetectionSession(modelProvider: provider)
// warm() throws NativeUIModelAvailabilityError.unavailable when no detector is selected.
```

For a verified detector, create `NativeUILocalDetector` with its URL, expected digest, manifest, and metadata.
Set that detector in the provider's `iOS` or `tvOS` field.
The digest uses `compiled-tree-sha256-v1`. It is not a ZIP hash or the Python inventory hash.
Use a trusted installation receipt for the expected digest. A self-reported hash from an unknown download does not establish trust.

For FocusRing, supply both `focusURL` and `focusDigest`.
The provider rejects a missing identity or changed bytes.
The provider checks detector identity, screenshot domain, and the supported preprocessing version.
The loader checks image dimensions and output ranks against the model manifest.
The model cache includes artifact, manifest, metadata, and preprocessing identity.
Keep each provider's selection fixed. Create a new session when the selected model changes.
Existing operations retain their loaded model.

Missing optional FocusRing produces an unavailable receipt. It does not silently select the heuristic.
Set `allowsHeuristicFocusFallback` only when the host explicitly requests that behavior.
The compatibility product keeps the existing heuristic policy.
Both paths keep the existing letterbox and FocusRing crop code.

## Verified evidence

- The integrated offline build passes on macOS 27.0.1, build 26A434, arm64.
- All 161 Swift tests pass after the selection and rollback changes.
- Explicit local models and bundled defaults give matching results on the retained iOS and tvOS images.
- A dependency-free consumer builds exact copies of the runtime sources and contains no model directories.
- The root runtime target depends only on `NativeUIModelContracts`.
- A native local installation compiles the resident Run 012 tvOS source and loads it through the real request.
- That source matches all 25 detections on the retained tvOS image.
- The stale source in the models directory differs on all 25 ordered detections.
- The parity check rejects that stale source before installation completes.
- Failure checks cover changed bytes, malformed archives, unsafe paths, case collisions, missing files, links, and missing models.
- Tests preserve failed attempts and reject destination collisions.

These results establish software behavior and limited numerical parity. They do not establish model accuracy or all supported hosts.
No training data, model weights, thresholds, or navigation policy change.

## Native installation limits

The Swift installer remains internal. Do not call it as an approved application interface.
It accepts a trusted inventory, checks a bounded stored ZIP, and uses `/usr/bin/ditto`.
It checks extracted bytes, compiles the source, runs the supplied validation, and moves completed output atomically.
It does not download models. The separate internal selection store now manages active and previous installations.

A malformed package manifest caused Core ML to abort during a negative test.
The installer now rejects that malformed structure before compilation.
This check does not prove that Core ML can safely compile every arbitrary package in the application process.
Only reviewed, hash-pinned source models belong in the supported input contract.
Compilation and the initial load now run in the internal `ModelCompileWorker` executable.
The host pins the helper hash. The helper accepts only a source path and its expected digest.
Timeout and cancellation stop only the owned child. This process boundary is not a security sandbox.
Signed TTR variants still need separate tests. The application still loads reviewed models for inference.
Receipt version 2 records the helper, source, compiled output, and host identities.
Restart checks reject changed output, unfinished receipts, unknown versions, and a different host.
An exclusive directory claim prevents duplicate installation across installer instances.
The installer does not reclaim an interrupted claim automatically.

See [digest contract and test vector](ModelDigestContract.md) for the exact tree hash.
Missing optional focus now produces receipts that pass the existing decoder rules.
The dependency-free probe targets macOS 14. Its executable records `minos 14.0`.
The probe runs on macOS 27, not macOS 14. The actual package now also builds and passes tests targeting macOS 14.
See [minimum host support](MinimumHostSupport.md). The manifest follow-up is published in `cc72583`.

The following checks remain before application installation or release:

- Test full host interruption and recovery of interrupted claims in both signed TTR variants.
- Qualify the implemented activation, rollback, and protected-call behavior inside the TTR host.
- Define host cleanup for recovery folders. Removal currently preserves bytes instead of deleting them.
- Qualify extraction and compilation inside the actual TTR sandbox.
- Finish trusted catalog integration and explicit bounded downloads.
- Verify exact iOS source exports and the FocusRing size requirement.
- Review artifact rights, public source scope, minimum hosts, and the final NUIAK version.

Do not use the similarly named tvOS source in the models directory for this release.
Use the resident `NativeUITrainer/yolo_runs/phase6b_tvos_v3/weights/best.mlpackage` as the next parity candidate.
Its source weights hash is `f0f9533f97453ef236631999a4e22fd8b397acb8590cb872b46da1e4688feeea`.
Its model specification hash is `253e7c677ce43749ea4ce7f5671c4b636075e0b3ffb00912281e0e25c2ce6e00`.
The 1-image comparison does not replace the full release comparison.

## Requested Sillycon-TTR response

1. Confirm receipt of this handoff and identify its request ID.
2. Name the current owner of optional NUIAK integration.
3. Review the preview provider interface against existing optional modules.
4. Confirm required model choices and supported Mac hosts.
5. Identify existing folder access, archive, download, and helper-process code that can serve this workflow.
6. Report whether the sandbox permits the native extraction and compilation path.
7. Review missing-model, fallback, version selection, and rollback behavior.
8. Return exact required changes before the integration test.

Sillycon-TTR owns any changes in its repository. Maximum-mini-NUIAK does not edit that repository.
After source delivery, Maximum-mini-TTR can test the consuming build under its existing authority.
No installation, signing change, dependency download, capture, or service restart is requested here.

## Integration test after source delivery

- Select only `NativeUIAuditKitRuntime` in the optional module.
- Verify that the TTR application contains no bundled model directories through that dependency.
- Start without selected models and without network access.
- Check the typed unavailable result and the disabled interface state.
- Select approved local artifacts with verified identities.
- Compare fixed frames with the existing bundled reference.
- Record actual detector and focus identities, settings, failures, and timings.
- Keep model output in observer mode. Do not use it to authorize navigation.

New diagnostic capture or transfer still follows [ADR-0024](ADR-0024-Opt-In-Model-Feedback.md).
Consensus is a review signal, not a training label.
Send compact successful-run summaries. Send images only through approved, case-linked transfers.

## Delivery states

Source preparation, coordinator storage, forwarding, recipient acknowledgment, and integration acceptance are separate states.
The coordinator must identify Sillycon-TTR and the exact forwarded request ID.
The task queue records current delivery status. This document does not claim recipient acceptance.

Next NUIAK tranche: connect a trusted catalog to bounded downloads, then qualify the same installation path in TTR.
Keep public publication behind the maintainer's source, rights, hosting, and version decisions.
