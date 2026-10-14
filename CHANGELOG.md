# Changelog

All notable changes to this project are documented here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning follows
[Semantic Versioning](https://semver.org/).

## Unreleased — preparation for TTR 0.4.3 RC

TTR 0.4.3 RC is a downstream version. The NUIAK release version remains subject to review.

### Fixed

- Missing optional focus now produces receipts that the existing decoder accepts.
- The standalone models package now includes the current iOS, tvOS, and FocusRing resources and detector manifests.
- The standalone verification command tests that package directly and loads all 3 models.
- Licensing guidance now reflects the actual bundled dependency and unresolved distribution requirements.
- The provenance table no longer repeats personal values from an earlier privacy incident.

### Added

- Offline release catalog, deterministic ZIP, and archive verification tools.
- A verified native macOS ZIP extraction probe using `ditto`, without a new dependency.
- A repository audit and a manual release checklist with separate artifact, privacy, integration, and model gates.
- A resource-free runtime product with explicit local models and typed missing-model errors.
- Bundled compatibility adapters that reuse the same inference code.
- Internal native archive and installation tests, including a real tvOS source comparison.
- A fixed compiler helper, verified restart checks, exclusive installation claims, and a shared digest test vector.
- Internal active-model selection, rollback, protected calls, and recoverable removal with one writer per storage root.

No model weights, inference thresholds, or navigation policy change.
Optional downloads and the complete installation lifecycle remain unfinished. These entries do not claim public release approval.

## [2.0.0] — 2026-08-23

First release where the package works end-to-end as a resolvable SPM dependency with a
working trained model included. `1.0.0` predated the model-shipping work entirely — this is
a major bump because the package's fundamental capability (ship a usable detector) did not
exist before this release.

### Added
- `NativeUIAuditKitModels` is now a real SPM target (previously existed on disk but was not
  wired into `Package.swift` at all).
- Trained YOLO11n model (`NativeUIDetector_v2.mlmodelc`, precompiled) bundled as a package
  resource — mAP@0.5 = 0.935 on 1,394 held-out validation images, ~7.5ms on-device inference.
- `NativeUIModelAsset` — zero-config model accessor: `loadModel()`, `defaultModelURL`,
  `metadata`, `makeConfiguration(computeUnits:allowLowPrecision:)`.
- `ModelMetadata` — tensor-level contract (input size, class label order, NMS/confidence
  thresholds) shipped alongside the model asset, so consumers read these values instead of
  hardcoding constants that can silently drift from a future model update.
- `NativeUIAuditKitModels` product split from `NativeUIAuditKit` — consumers who bring their
  own inference code (e.g. ViewLens) can depend on just the model, without the Vision
  framework wrapper, dataset generator, or trainer.
- Platform support expanded from macOS-only to `.macOS(.v15)`, `.iOS(.v17)`,
  `.macCatalyst(.v17)`, `.visionOS(.v1)`.
- DocC catalogs for both `NativeUIAuditKit` and `NativeUIAuditKitModels` targets;
  `swift-docc-plugin` dependency added.
- `ModelRegistry.v2Metadata` and `ModelRegistry.iOS` now point at the YOLO11n model by
  default; the superseded Create ML descriptor is preserved as `ModelRegistry.iOS_v1`.
- `NativeUIAuditKitModelsTests` target with smoke tests confirming the bundled model
  resource resolves and loads via `MLModel`.
- `NativeUIDetectionRequest` (the `NativeUIAuditKit` product's higher-level API) migrated to
  the YOLO11n model — single-pass letterboxed inference ported from
  `scripts/eval_yolo_map.swift`, replacing the superseded v1 model's 3-pass Vision-framework
  pipeline (full-image + SAHI tiling + horizontal strips). No Vision framework dependency
  remains in this target. `minimumConfidence` now passes directly as the model's
  `confidenceThreshold` input.
- Two new tests (`detectionRequestFindsRealElements`,
  `detectionRequestRespectsMinimumConfidence`) against a real fixture,
  `Tests/NativeUIAuditKitTests/Fixtures/kitchen_sink_screen.png`.

### Changed
- `.gitignore` no longer blocks the packaged model resource or its training config — only
  raw/unpromoted training-run artifacts remain ignored.

### Removed
- `NativeUIDetectionError.modelUnavailable` — unreachable now that `NativeUIModelAsset`
  always resolves a bundled model; the case and the test asserting it were removed together.
- The old `detectionRequestThrowsModelUnavailable` test, which asserted a throw that no
  longer happens and whose dev-fallback path (compiling the stale raw v1 model on the fly)
  was found to genuinely hang — confirmed by a `swift test` run stuck at 10+ minutes CPU
  time before being killed.

## [1.0.0] — 2026-05-03

Initial tagged version. Predates the trained-model-shipping work in this changelog —
package built but had no way to distribute a working model to a dependent.
