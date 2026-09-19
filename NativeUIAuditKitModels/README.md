# NativeUIAuditKitModels

This package distributes pre-trained CoreML models and runtime descriptors for use with **NativeUIAuditKit**. Snapshot: [`Research/CurrentState.md`](../Research/CurrentState.md). Provenance: [`PROVENANCE.md`](../PROVENANCE.md).

---

## Bundled Models & Provenance

### 1. `NativeUIModel_iOS.mlmodelc` (`nativeui-ios-v2.0`)
- **Architecture**: YOLO11n (anchor-free, single-stage detector).
- **Target Platform**: iOS and iPadOS.
- **Trained Classes (5)**: `alert`, `navigationBar`, `primaryButton`, `textField`, `toggle`.
- **Performance**: mAP@0.5 = 0.935 on 1,394 held-out validation images.
- **License**: **AGPL-3.0 License** (derived from Ultralytics YOLO11 training framework).
- **Manifest**: [`model_manifest_ios_v2.json`](Sources/NativeUIAuditKitModels/Resources/model_manifest_ios_v2.json).

### 2. `NativeUIModel_tvOS.mlmodelc` (`nativeui-tvos-v3.0`)
- **Architecture**: YOLO11n (anchor-free, single-stage detector).
- **Target Platform**: tvOS (Apple TV 1080p and 4K displays).
- **Trained Classes (25 active; 41-class mapped head)**:
  `activityIndicator`, `alert`, `cancelAction`, `collectionItem`, `contextMenu`, `destructiveButton`, `imageView`, `label`, `link`, `listRow`, `navigationBar`, `popover`, `primaryButton`, `progressView`, `searchField`, `secondaryButton`, `secureField`, `segmentedControl`, `sheet`, `sidebar`, `slider`, `stepperControl`, `tabBar`, `toggle`, `toolbar`.
- **Performance**: mAP@0.5 = 0.9822 on held-out test; hardware-qualified on Office Apple TV 4K.
- **License**: **AGPL-3.0 License** (derived from Ultralytics YOLO11 training framework).
- **Manifest**: [`model_manifest_tvos_v1.json`](Sources/NativeUIAuditKitModels/Resources/model_manifest_tvos_v1.json) (`modelId` is `nativeui-tvos-v3.0`).
- **Superseded**: `nativeui-tvos-v1.0` (10-class prototype), `nativeui-tvos-v2.0` (21-class).

### 3. `FocusRingDetector.mlmodelc` (`focus-ring-detector-v1.0`)
- **Architecture**: MobileNetV4-Conv-Small (vendored `scripts/focus_ring_backbone.py`; trained from scratch, not Ultralytics YOLO).
- **Target Platform**: tvOS Stage 2 focus classification on 256×256 YOLO crops.
- **Outputs**: `is_focused_prob`, `confidence` (metadata `focusThreshold=0.85`, `ambiguityThreshold=0.70`).
- **Performance**: FDR-001 held-out 270/270; package 4.80 MB FP16. Hard-negative `light`/`highContrast` split is empty (FOCUS-DET-05).
- **License**: Not AGPL-3.0. From-scratch weights; no `MLModelLicenseKey` in CoreML metadata. See [`Research/LicensingArchitecture.md`](../Research/LicensingArchitecture.md).
- **Run**: [FDR-001](../Research/ExperimentLog.md).

---

## Licensing Terms & Compliance

The Swift code in this package is licensed under the **MIT License**.

YOLO compiled weights (`NativeUIDetector_v2.mlmodelc`, `NativeUIModel_tvOS.mlmodelc`) carry the **AGPL-3.0 License** declared in their CoreML metadata (`MLModelLicenseKey`). `FocusRingDetector.mlmodelc` is a from-scratch MobileNetV4 classifier and does not embed that key.

- **Internal Use**: Internal test harnesses, CI pipelines, and QA automation rigs (such as TVTestRig) may use these models without restriction.
- **Commercial Distribution**: For public or commercial distribution in proprietary apps, obtain an enterprise license from Ultralytics or retrain using a permissive framework (e.g. Apple Create ML). See [`Research/LicensingArchitecture.md`](../Research/LicensingArchitecture.md) for details.
