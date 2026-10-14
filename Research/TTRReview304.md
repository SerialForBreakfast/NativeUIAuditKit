# TTR real-model integration pack — REVIEW304

Owner: Maximum-mini-NUIAK. Recipient: Sillycon-TTR.
This pack supplies the existing tvOS detector for local integration tests.
It does not publish a model release or approve navigation use.

## Published delivery

The verified share contains `nuiak/nuiak-tvos-review304-handoff.zip` with 5,816,443 bytes.
Its SHA-256 is `8ee3c41acb7fc96d8c1707cc1b37eb4775389865dd314457a1087b889e60d1ab`.
The receipt ID is `nuiak-tvos-review304-handoff`.
Coordinator request `nuiak-release304-real-model-delivery-01` is stored at cursor 125 with exact-ID verification.
Forwarding, TTR receipt, and signed integration remain unconfirmed.
The native offline build, 173 Swift tests, and 16 focused Python tests pass.
The separate exact-archive test compiles and matches all 25 reference detections.
The first reference test fails because its installation directory is absent. The corrected attempt uses a new directory.
Both attempts remain available under `reports/work/RELEASE-304` and `reports/work/RELEASE-303`.

## Use the pack

1. Verify the outer archive size and SHA-256 against the coordinator message.
2. Extract the archive into a new approved folder with bounded, safe extraction.
3. Read `catalog-review.json` and `entry.json` as a pinned review contract.
4. Do not fetch the entry's URL. It reserves a proposed release path and is not published.
5. Check the inner archive against `archiveBytes`, `archiveSHA256`, and every `files` record.
6. Compile `model.mlpackage` through TTR's approved compiler path.
7. Validate the model against `contract.json` before selection.
8. Record the source digest, compiled digest, compiler identity, host version, and architecture.
9. Use the public provider adapter with that verified compiled digest.
10. Run the reference image with OCR and FocusRing disabled.
11. Compare labels, scores, and pixel boxes with `reference-results.json`.
12. Return an exact transfer receipt and a separate integration report.

The source API pin is `cc72583439f39ce8e7c9eaf5b8f48a9f104dcda0` in `SerialForBreakfast/NativeUIAuditKit`.
Use the `NativeUIAuditKitRuntime` product. It does not bundle model resources.
`TTRReviewAdapter.swift` contains the public adapter and a small compile test.
Remove the `Testing` import and test function when copying the adapter into application code.
Decode `contract.json` as `TTRReviewContract`, then call `provider(compiledURL:expectedCompiledDigest:)`.
Create `NativeUIDetectionSession(modelProvider: provider)` or the existing request with that provider.
The host owns download, extraction, compilation, selection, and folder permissions.
Do not call NUIAK's internal installer types as public APIs.

## Compare results

The local reference has 25 detections. Its input is the existing `tvos_home_screen.png` test fixture.
Use tvOS configuration, confidence 0.25, and the existing letterbox preprocessing.
For the same runtime, compare confidence within 0.00001 and each pixel box value within 0.01.
Ignore generated observation IDs. Preserve the ordered labels and report any order difference separately.
Different compute backends can differ. Report those differences rather than silently increasing tolerances.
Reference agreement checks integration, not detector accuracy or real-app generalization.

The package declares macOS 14. NUIAK verifies this execution on macOS 27.0.1 arm64 only.
TTR must report actual older-host results separately.
FocusRing is absent from this pack. Missing focus remains unavailable, not a heuristic score.
No transition model or new trained weights belong to this pack.

## Remaining public release steps

The catalog has `releaseStatus: review-only`. Publication validation deliberately rejects it.
The maintainer reviews model rights and chooses the release repository, tag, and exact publication scope.
NUIAK then prepares the approved catalog and verifies downloaded release bytes.
This local review does not need a new Git tag or a public upload.
Preserve the share copy until Maximum-mini-NUIAK verifies TTR's matching receipt.
