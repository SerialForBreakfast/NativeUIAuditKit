# ``NativeUIAuditKitModels``

The trained CoreML model + versioned metadata, with no Vision framework dependency.

## Overview

This is the lightweight product to depend on if you bring your own inference pipeline and
just need the trained weights — this is what
[ViewLens](https://github.com/SerialForBreakfast/ViewLens) depends on.

```swift
import NativeUIAuditKitModels

let model = try await NativeUIModelAsset.loadModel()
let metadata = NativeUIModelAsset.metadata   // input size, class order, thresholds
```

The bundled model is `nativeui-ios-v2.0` (YOLO11n), mAP@0.5 = 0.935 on a 1,394-image
held-out validation set, ~7.5ms on-device inference. See ``ModelRegistry`` for the full
descriptor and ``ModelMetadata`` for the tensor-level contract (input size, class label
order, recommended thresholds) — read these instead of hardcoding constants, so a future
model update can't silently break your bounding-box math.

The superseded Create ML v1 model's descriptor remains available as `ModelRegistry.iOS_v1`
for anyone pinned to it, though its binary asset is not bundled as a package resource.

## Topics

### Model Asset

- ``NativeUIModelAsset``
- ``ModelMetadata``

### Registry

- ``ModelRegistry``
- ``ModelDescriptor``
- ``OSVersionRange``
