# NativeUIAuditKitModels

This package distributes pre-trained CoreML models and runtime descriptors for use with **NativeUIAuditKit**.

---

## Bundled Models & Provenance

### 1. `NativeUIModel_iOS.mlmodelc` (`nativeui-ios-v2.0`)
- **Architecture**: YOLO11n (anchor-free, single-stage detector).
- **Target Platform**: iOS and iPadOS.
- **Trained Classes (5)**: `alert`, `navigationBar`, `primaryButton`, `textField`, `toggle`.
- **Performance**: mAP@0.5 = 0.935 on 1,394 held-out validation images.
- **License**: **AGPL-3.0 License** (derived from Ultralytics YOLO11 training framework).
- **Manifest**: [`model_manifest_ios_v2.json`](Sources/NativeUIAuditKitModels/Resources/model_manifest_ios_v2.json).

### 2. `NativeUIModel_tvOS.mlmodelc` (`nativeui-tvos-v1.0`)
- **Architecture**: YOLO11n (anchor-free, single-stage detector).
- **Target Platform**: tvOS (Apple TV 1080p and 4K displays).
- **Trained Classes (10 with active instances, 41-class mapped head)**:
  `alert`, `cancelAction`, `collectionItem`, `imageView`, `label`, `listRow`, `navigationBar`, `primaryButton`, `tabBar`, `toggle`.
- **Performance**: mAP@0.5 = 0.995 on held-out test suite; 100% focus resolution accuracy on synthetic test screens.
- **License**: **AGPL-3.0 License** (derived from Ultralytics YOLO11 training framework).
- **Manifest**: [`model_manifest_tvos_v1.json`](Sources/NativeUIAuditKitModels/Resources/model_manifest_tvos_v1.json).

---

## Licensing Terms & Compliance

The Swift code in this package is licensed under the **MIT License**.

The pre-trained weights (`.mlmodelc` directories) carry the **AGPL-3.0 License** declared in their CoreML metadata (`MLModelLicenseKey`).

- **Internal Use**: Internal test harnesses, CI pipelines, and QA automation rigs (such as TVTestRig) may use these models without restriction.
- **Commercial Distribution**: For public or commercial distribution in proprietary apps, obtain an enterprise license from Ultralytics or retrain using a permissive framework (e.g. Apple Create ML). See [`Research/LicensingArchitecture.md`](../Research/LicensingArchitecture.md) for details.
