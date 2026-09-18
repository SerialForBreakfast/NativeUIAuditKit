# Licensing & Distribution Architecture

This document defines the licensing architecture, intellectual property boundaries, and distribution options for **NativeUIAuditKit** and its optional companion package **NativeUIAuditKitModels**.

---

## 1. Summary of Licenses

| Component | Repository / Location | License | Terms & Permissibility |
|---|---|---|---|
| **NativeUIAuditKit** (Codebase) | `Sources/NativeUIAuditKit/` | **MIT License** | Fully permissive. Free commercial, proprietary, and open-source use with standard disclaimer. |
| **NativeUIAuditKitModels** (Swift Glue) | `NativeUIAuditKitModels/Sources/` | **MIT License** | Fully permissive Swift bindings and protocol definitions. |
| **Bundled CoreML Weights** | `NativeUIAuditKitModels/Resources/*.mlmodelc` | **AGPL-3.0** (Ultralytics) | Derived from Ultralytics YOLO11 pre-trained backbones. Subject to AGPL-3.0 copyleft terms upon distribution unless commercially licensed. |

---

## 2. IP Boundary & Package Decoupling

NativeUIAuditKit was intentionally architected as two separate packages:

1. **`NativeUIAuditKit` (Core Engine — Pure MIT)**:
   - Contains all heuristic audits, geometry processing, safe area rules, Vision OCR text fusion, session management, and `NativeUIRecognizing` abstractions.
   - Contains **zero** model weights, zero YOLO dependencies, and zero AGPL code.
   - Can be embedded directly into proprietary, commercial, or enterprise closed-source products without any copyleft obligations.

2. **`NativeUIAuditKitModels` (Optional Pre-Trained Weights)**:
   - Provides out-of-the-box YOLO11n weights (`nativeui-ios-v2.0` and `nativeui-tvos-v1.0`).
   - The compiled model artifacts embed `MLModelLicenseKey: "AGPL-3.0 License"` in their CoreML metadata (`metadata.json`), reflecting their origin from the Ultralytics YOLO11 framework.

---

## 3. Considerations for Downstream Consumers

### 3.1 Internal Testing, QA, and Automation (e.g. TVTestRig)
- **Status**: Allowed under AGPL-3.0.
- Running NativeUIAuditKit and bundled weights within internal CI/CD pipelines, local development rigs, test benches (like TVTestRig), and offline automated testing environments does **not** constitute external conveyance or network service distribution under AGPL-3.0.

### 3.2 External Commercial Distribution
If a consumer intends to ship an end-user application (e.g. on the App Store) containing bundled weights, two distinct unencumbered paths are available:

#### Path A: Ultralytics Enterprise Commercial License
- Purchase a commercial distribution license directly from Ultralytics Inc.
- Allows proprietary distribution of YOLO11 weights without AGPL-3.0 source-disclosure requirements.

#### Path B: Permissive Clean Retrain (Zero Third-Party Licensing)
- Retrain the detector using a permissively licensed framework:
  1. **Apple Create ML**: Built into macOS. Produces native `.mlpackage` models with zero third-party licensing encumbrances.
  2. **TorchVision (BSD 3-Clause / Apache 2.0)**: Train standard object detection architectures (e.g. Faster R-CNN, SSD-MobileNet, RetinaNet) and export via `coremltools`.
- Because `NativeUIDetectionRequest` accepts any conforming `ModelManifest` and CoreML tensor contract, swapping in a clean-room retrained model requires zero code changes to the core library.

---

## 4. Metadata Verification

Every bundled CoreML model artifact contains explicit provenance and licensing metadata verified at runtime and test time:

- `license`: `"AGPL-3.0 License (https://ultralytics.com/license)"`
- `author`: Ultralytics YOLO11 export
- `description`: Platform-specific UI element detection model for iOS or tvOS.

---

## 5. Training Data Provenance

See [`PROVENANCE.md`](../PROVENANCE.md) for the training hardware, exact hyperparameters, and
source datasets behind every shipped model, plus an explicit audit for personal identifiers or
proprietary third-party assets in training data.
