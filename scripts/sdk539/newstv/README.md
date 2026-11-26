# NewsTV integration for SDK539 and REAL543

This integration targets source revision `95aa870210a5db57b84317353ed9999ad8bcb81d`.
It changes data and instrumentation. It retains the application's existing views.
The integration builds and passes an authenticated SDK metadata trial.
It is not benchmark-qualified. The SDK reports interruption and unknown focus.
The trial returns 23 rectangles. Pixel alignment and complete labels remain unverified.
Direct diagnostics compare SwiftUI phase, application state, window scene state, and native focus availability.
All 3 scene observations report inactivity. The integration does not override this evidence.

## Reproduction

1. Use the pinned NewsTV Git checkout.
2. Run `git apply --check` with `instrumentation.patch` before applying it.
3. Apply the patch inside that checkout.
4. Run `FixSourcePath.swift` against `NewsTV.xcodeproj/project.pbxproj`.
5. Place the complete TTRDiagnostics package in `Vendor/TTRDiagnostics`.
6. Preserve the TTR license and record every vendored file hash.
7. Run `LinkSDK.swift` against the project file.
8. Build the NewsTV scheme for a generic tvOS Simulator.

Use project-local Swift caches and build outputs.
The current private SDK snapshot includes source modifications beyond its Git revision.
Its receipt is `reports/work/REAL543/newstv-sdk-vendor.json` in the NUIAK checkout.
A clean, published SDK revision remains a portability qualification requirement.
The linking tool rejects an already linked package. It preserves existing project objects.

## Observation contract

SDK launch configuration controls instrumentation. Release builds disable SDK activation.
The signed query endpoint requires enrollment and a Simulator identity. It accepts no navigation input.
The endpoint expires after 800 s. It does not print the enrollment key.

Explicit hooks register main tabs, category tabs, and article buttons.
They measure layout rectangles in window points before each SDK response.
Reused views replace the old identity. Disappearing views unregister their identity.
The app does not report complete coverage, clipping, occlusion, or native focus.
Focus remains unknown. Selection styling is not focus evidence.
The reviewer must inspect all visible controls before false-positive scoring.

## Controlled content

The DEBUG-only argument `--real543-controlled-content` supplies 18 original text articles across 3 categories.
It disables live RSS fetching and the unrelated Nova listener during this mode.
It skips local-news fetching during initial setup. Article ages use a fixed reference time.
It skips the notification permission request (REALAPP554 RA554-01). That system alert makes the app scene inactive.
No external images are supplied. Existing app layout and controls remain in use.
This does not establish network isolation for every application feature.
The first pilot restricts navigation to the planned news, technology, and science flows.

Installation, launch, capture, and benchmark admission require their applicable authority and checks.
No screenshots or model predictions accompany this patch.

## Controlled-content repairs for capture — B405-298 (Joe: "Patch NewsTV", 2026-11-25)

Apply after `instrumentation.patch`. Both change behavior only where the unmodified build cannot be captured. Rendered layouts stay the same.

| Patch | SHA-256 | Change |
|---|---|---|
| `foryou-render-loop.patch` | `5a10ebb7be0bd93d1bb3718c627a1aca9b97e634ec8c284a50566905ff525561` | `PersonalizationEngine.personalizedFeed` returns the sorted list without writing `@Published personalizedArticles`. `ForYouView` called it from `body`, so every render re-published and the app never became idle. Nothing else reads that property. |
| `watchlater-icloud-guard.patch` | `ae68816ffa99757c432c6dee47452397fe4da21541c19cf2898955ad5ff0dbd3` | Cloud sync, save and delete return early without an iCloud account (`ubiquityIdentityToken == nil`). The unsigned Simulator build has no iCloud entitlement, and `CKContainer(identifier:)` trapped when Watch Later opened. |

Build: same command as RA554 (`-derivedDataPath .build/sdk539-newstv-derived`, `CODE_SIGNING_ALLOWED=NO`). `NewsTV.debug.dylib` SHA-256 `eecd3e7678490bd70a7b22e761b5399e7f7d7af19ce1b69050f94568b427b415`.
Previous app kept for rollback in `.build/sdk539-newstv-pre-b405298/`.
