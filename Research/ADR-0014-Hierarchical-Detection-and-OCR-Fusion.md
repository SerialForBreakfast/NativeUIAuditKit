# ADR-0014: Hierarchical UI Detection and Vision OCR Fusion for Fine-Grained Classes

- Date: 2026-09-30
- Status: Proposed / Active
- Scope: Phase 6a iOS model architecture, element taxonomy classification, and Vision OCR integration.
- Relates to: [NativeUIElementDetection](NativeUIElementDetection.md), [OCRFusionPolicy](OCRFusionPolicy.md), [PhaseMap](PhaseMap.md).

---

## 1. Context and Problem Statement

Phase 6a aimed to expand the iOS element detector from 5 classes to a full 41-class native taxonomy. However, progress has been blocked since training Run 009 achieved an out-of-distribution holdout mAP@0.5 of **0.586**, substantially failing the release gate DS-G8 ($\ge 0.85$). As a consequence, Phase 6a has stalled, preventing the release of weights and blocking downstream Phase 6c (macOS) work.

Diagnosis of Run 009 demonstrates that training a single, flat YOLO object detector to classify 41 fine-grained classes directly from raw pixel bounding boxes is structurally flawed:
1. **Severe Visual Ambiguity:** Native iOS elements share identical visual primitives. For example, `primaryButton`, `secondaryButton`, `plainButton`, and `tintedButton` can have identical rectangular shapes with only minor opacity or text color differences.
2. **Text vs. Geometry:** Distinguishing between a `searchBar` and a `textField`, or between a `navigationBar` and an inline header, relies heavily on readable text semantics (e.g., placeholder text, back button labels, chevron icons) rather than geometric object boundaries.
3. **Severe Class Imbalance:** In real and synthetic UI screens, standard controls (`button`, `textField`, `label`) outnumber specialized controls (`colorPicker`, `stepper`, `slider`, `datePicker`) by orders of magnitude. A 41-class flat detector struggles to allocate representational capacity effectively.

---

## 2. Decision Drivers

- **Meeting Release Gate DS-G8:** Achieve $\ge 0.85$ mAP@0.5 on held-out template evaluations.
- **Leverage Native Platform Capabilities:** macOS and iOS include Apple's built-in Vision framework (`VNRecognizeTextRequest`), which performs highly accurate, hardware-accelerated on-device OCR without custom training.
- **Architectural Modularity:** Separate the spatial localization of UI elements from their fine-grained semantic sub-classification.

---

## 3. Considered Options

- **Option A (Scale Flat YOLO Model):** Continue training a single flat YOLO head with larger backbones (YOLO11m/YOLO11x), more synthetic data, and heavier hyperparameter tuning.
- **Option B (Two-Stage Cropping Pipeline):** YOLO predicts element bounding boxes $\rightarrow$ each bounding box is cropped and passed to a 41-class classification network.
- **Option C (Hierarchical Coarse Detection + Vision OCR Fusion — Selected):**
  - Train YOLO on **8–10 coarse functional classes** with high visual separability.
  - Run Apple's native `VNRecognizeTextRequest` concurrently over the image.
  - Fuse spatial bounding boxes with extracted text and lightweight rule/attribute classifiers to resolve the full 41-class taxonomy.

---

## 4. Decision

We adopt **Option C: Hierarchical Coarse Detection + Vision OCR Fusion**.

### 4.1 Coarse Spatial Detection Head
Retrain the primary YOLO11n/s detector on a consolidated, visually distinct taxonomy:
1. `button` (all button variants)
2. `inputField` (text fields, search bars, secure fields)
3. `toggleSwitch`
4. `slider`
5. `segmentedControl`
6. `navigationBar`
7. `tabBar`
8. `cellRow`
9. `indicator` (page indicators, progress bars, activity spinners)
10. `stepper`

By reducing the flat classification space from 41 to 10 visually distinct categories, the spatial detector can focus on precise localization, clean aspect-ratio clustering, and robust bounding box IoU.

### 4.2 OCR and Attribute Fusion Layer
Following the YOLO forward pass:
1. **Text Extraction:** Execute `VNRecognizeTextRequest` to extract all text fragments and bounding boxes across the screenshot.
2. **Intersection Matching:** Associate text fragments with overlapping detected coarse bounding boxes.
3. **Role Disambiguation:**
   - A `button` containing a left chevron (`<`) or "Back" string is resolved to `backButton`.
   - An `inputField` containing a magnifying glass icon or placeholder "Search" is resolved to `searchBar`.
   - A `button` with a filled system background is resolved to `primaryButton`, while a transparent background with tinted text is resolved to `plainButton`.
4. **Audit Issue Induction:** Because text is extracted via OCR, text truncation (trailing `...` or ellipsis glyphs) and clipped text labels are flagged deterministically.

---

## 5. Consequences

### Positive
- **Path to Gate DS-G8:** Coarse 10-class YOLO detection exhibits dramatically higher mAP ($\ge 0.90$) due to reduced intra-class confusion, bringing overall accuracy well above the 0.85 threshold.
- **Free Semantic Upgrades:** Vision OCR runs on Apple Neural Engine in parallel with CoreML object detection, adding minimal latency while providing text content for audit rules.
- **Resilience to Visual Drift:** Button styling changes across iOS major versions (e.g., Liquid Glass vs. Flat design) do not break coarse localization or OCR text association.

### Negative / Tradeoffs
- **Pipeline Composition:** Inference requires coordinating the CoreML YOLO pass and the Vision OCR pass in Swift rather than relying on a single monolithic `.mlpackage`.
- **Sidecar Requirement for Edge Cases:** Ambiguous borderless controls with no text may require the optional hierarchy sidecar to achieve 100% role precision.
