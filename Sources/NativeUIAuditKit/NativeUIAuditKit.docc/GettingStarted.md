# Getting Started

Add NativeUIAuditKit as a dependency and load the trained model in a few lines.

## Add the Dependency

```swift
// Package.swift
dependencies: [
    .package(url: "https://github.com/<org>/NativeUIAuditKit.git", from: "2.0.0")
]
```

Then add `NativeUIAuditKitModels` to your target — this is the lightweight product
containing just the trained model and its metadata, with no Vision framework dependency:

```swift
.target(
    name: "YourTarget",
    dependencies: [
        .product(name: "NativeUIAuditKitModels", package: "NativeUIAuditKit")
    ]
)
```

## Load the Model

```swift
import NativeUIAuditKitModels
import CoreML

let model = try await NativeUIModelAsset.loadModel()

// Tensor-level contract — read these instead of hardcoding them, so a future
// model update (different input size, reordered classes) can't silently break you.
let metadata = NativeUIModelAsset.metadata
print(metadata.inputWidth, metadata.inputHeight)     // 640, 640
print(metadata.classLabels)                          // ["alert", "navigationBar", ...]
print(metadata.recommendedNMSIoUThreshold)            // 0.30
```

`NativeUIModelAsset.loadModel()` uses `MLModelConfiguration` with `computeUnits = .all` by
default (Apple Neural Engine + GPU). Override with `makeConfiguration(computeUnits:)` if
you need CPU-only inference for testing.

## Running Inference

The model expects a 640×640 letterboxed input (aspect-ratio-preserving resize with gray
fill, matching standard YOLO preprocessing) and returns predictions with NMS already baked
into the CoreML graph — no separate NMS pass needed. For a complete, tested reference
implementation of the letterbox → predict → parse pipeline (including the stride-based
`MLMultiArray` output parsing), see
[`scripts/eval_yolo_map.swift`](https://github.com/<org>/NativeUIAuditKit/blob/main/scripts/eval_yolo_map.swift)
in the repository — this is the exact logic validated against the 0.935 mAP@0.5 figure.

> Note: `NativeUIDetectionRequest` (the `NativeUIAuditKit` product's higher-level Vision-style
> wrapper) has not yet been updated to this preprocessing and is not the recommended path
> today — see the module overview for details.
