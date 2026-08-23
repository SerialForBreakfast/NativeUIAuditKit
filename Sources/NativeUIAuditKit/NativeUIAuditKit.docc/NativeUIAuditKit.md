# ``NativeUIAuditKit``

Detect native Apple platform UI elements in screenshots using an on-device CoreML model —
no cloud calls, no image tokens spent on a multimodal LLM.

## Overview

This is the higher-level Vision-style detection API, built on the `NativeUIAuditKitModels`
product. If you only need the trained model itself (no Vision framework wrapper — for
example if you're rolling your own inference pipeline, as
[ViewLens](https://github.com/SerialForBreakfast/ViewLens) does), depend on
`NativeUIAuditKitModels` directly instead — see its own documentation catalog.

> Important: ``NativeUIDetectionRequest``'s multi-pass pipeline (full-image + SAHI tiling +
> horizontal strips) was built for the superseded Create ML v1 model and has not yet been
> updated for the current YOLO11n model. It is not the recommended entry point right now.
> For working, tested model access, use `NativeUIModelAsset` from `NativeUIAuditKitModels`
> directly. This will be resolved in a future release.

## Getting Started

See <doc:GettingStarted> for the model-loading Quick Start.

## Model Performance

The bundled model (`nativeui-ios-v2.0`, YOLO11n) scores mAP@0.5 = 0.935 on a 1,394-image
held-out validation set, with on-device inference around 7.5ms per image. Full breakdown in
the repository [README](https://github.com/<org>/NativeUIAuditKit#model-performance) and
[`Research/ExperimentLog.md`](https://github.com/<org>/NativeUIAuditKit/blob/main/Research/ExperimentLog.md).

## Topics

### Detection

- ``NativeUIDetectionRequest``
- ``NativeUIDetectionConfiguration``
- ``NativeUIDetectionError``
- ``NativeUIElementObservation``
