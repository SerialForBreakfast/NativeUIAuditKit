# ``NativeUIAuditKit``

Detect native Apple platform UI elements in screenshots using an on-device CoreML model —
no cloud calls, no image tokens spent on a multimodal LLM.

## Overview

This is the higher-level detection API — a request/observation ergonomic (similar shape to
Apple's own Vision framework requests), built on the `NativeUIAuditKitModels` product's
YOLO11n model with a single-pass letterboxed inference pipeline (no Vision framework
dependency itself). If you only need the trained model and want to roll your own inference
— as [ViewLens](https://github.com/SerialForBreakfast/ViewLens) does — depend on
`NativeUIAuditKitModels` directly instead; see its own documentation catalog.

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
