# Changelog

All notable changes to this project are documented here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning follows
[Semantic Versioning](https://semver.org/).

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
