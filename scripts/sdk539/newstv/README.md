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
No external images are supplied. Existing app layout and controls remain in use.
This does not establish network isolation for every application feature.
The first pilot restricts navigation to the planned news, technology, and science flows.

Installation, launch, capture, and benchmark admission require their applicable authority and checks.
No screenshots or model predictions accompany this patch.
