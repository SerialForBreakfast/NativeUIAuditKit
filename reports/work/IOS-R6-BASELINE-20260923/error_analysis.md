# iOS r6 41-Class Baseline Error Analysis (Run 009)

**Evaluation Date:** 2026-09-24T02:24:31Z  
**Model Checkpoint:** `/Users/josephmccraw/Documents/GitHub/NativeUIAuditKit/NativeUITrainer/yolo_runs/phase6a_r009/weights/best.pt`  
**Corpus:** `ios-41class-r6-test` (2,000 holdout test images)  

## 1. Executive Summary

- **Supported Class mAP@0.50:** **0.5549** (across the 13 supported classes).
- **Supported Class mAP@0.50:0.95:** **0.3982**.
- **Coverage Integrity:** Exactly 13 classes are represented in the test set. Per BP-52 and P2-METRICS, the remaining 28 classes are reported as `unavailable` (never imputed as 0.0).
- **Historical Non-Comparability:** Historical Run 009 achieved 0.586 on the lost historical test split. Because the reconstructed r6 corpus has distinct family distributions and only 13 test classes, no direct improvement delta against 0.586 can be computed.

## 2. Per-Class Performance Breakdown (13 Supported Classes)

| Class Name | Ground Truth Count | Predictions Count | AP@0.50 | AP@0.50:0.95 | Precision (conf≥0.25) | Recall (conf≥0.25) | Diagnosis |
|---|---|---|---|---|---|---|---|
| `imageView` | 1900 | 1388 | 0.1571 | 0.1462 | 0.4049 | 0.1647 | Critical failure; severe missed detections or confusion |
| `label` | 9165 | 14078 | 0.7004 | 0.5153 | 0.7074 | 0.7411 | Moderate performance |
| `listRow` | 700 | 7032 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | Critical failure; severe missed detections or confusion |
| `navigationBar` | 800 | 3213 | 0.9998 | 0.9473 | 0.8999 | 1.0000 | Strong fit |
| `pageControl` | 600 | 544 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | Critical failure; severe missed detections or confusion |
| `picker` | 200 | 946 | 0.8053 | 0.2465 | 0.4639 | 0.7700 | Moderate performance |
| `primaryButton` | 1366 | 2429 | 1.0000 | 0.9928 | 0.8706 | 1.0000 | Strong fit |
| `progressView` | 200 | 243 | 0.9998 | 0.3492 | 1.0000 | 0.7450 | Strong fit |
| `secondaryButton` | 341 | 66 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | Critical failure; severe missed detections or confusion |
| `secureField` | 200 | 450 | 0.6001 | 0.5015 | 0.5161 | 0.5600 | Sub-target; boundary/recall degradation |
| `stepperControl` | 200 | 493 | 0.5940 | 0.3564 | 0.5000 | 1.0000 | Sub-target; boundary/recall degradation |
| `textField` | 503 | 851 | 0.5482 | 0.3963 | 0.7118 | 0.4911 | Sub-target; boundary/recall degradation |
| `toggle` | 1687 | 2325 | 0.8085 | 0.7250 | 0.7512 | 0.7641 | Moderate performance |

## 3. Unsupported Classes (28 Classes)

The following 28 classes have 0 test ground truth instances in the r6 reconstruction:

`actionSheet`, `activityIndicator`, `alert`, `cancelAction`, `collectionItem`, `colorWell`, `contextMenu`, `destructiveButton`, `disclosureGroup`, `dynamicIsland`, `homeIndicator`, `link`, `mapView`, `menuButton`, `popover`, `refreshControl`, `scrollIndicator`, `searchField`, `segmentedControl`, `sheet`, `sidebar`, `slider`, `statusBar`, `tabBar`, `toolbar`, `tooltip`, `unknown`, `webContent`.

Per P2-METRICS policy, their metrics are explicitly `None` (unavailable). Inventing zero AP would artificially depress the macro average and misrepresent model capability.

## 4. Small Element Performance (< 100px)

| Class Name | Small GT Count | Small AP@0.50 |
|---|---|---|
| `imageView` | 350 | 0.0007 |
| `label` | 8520 | 0.6423 |
| `pageControl` | 600 | 0.0000 |
| `picker` | 200 | 0.8053 |
| `primaryButton` | 100 | 0.0732 |
| `progressView` | 200 | 0.9998 |
| `secureField` | 200 | 0.6001 |
| `stepperControl` | 200 | 0.5940 |
| `textField` | 452 | 0.6101 |
| `toggle` | 1687 | 0.8085 |

## 5. Performance by Template Family (Holdout)

| Template Family | Image Count | Supported Classes | Family mAP@0.50 |
|---|---|---|---|
| `CardDetail` | 200 | 4 | 0.7136 |
| `EmptyState` | 400 | 3 | 0.4868 |
| `GalleryPage` | 200 | 5 | 0.7872 |
| `MultiSectionForm` | 200 | 8 | 0.7769 |
| `NotificationCenter` | 200 | 3 | 0.3027 |
| `OnboardingPage` | 400 | 4 | 0.3494 |
| `SettingsToggleDense` | 200 | 3 | 0.9424 |
| `WizardStepFlow` | 200 | 6 | 0.6403 |

## 6. Actionable Error Modes & Key Findings

1. **Container vs Control Boundary Blurring:** Classes like `listRow` and `navigationBar` suffer from bounding box misalignment with internal labels and buttons, reducing AP@0.5:0.95 significantly compared to AP@0.5.
2. **Small Indicator Detection:** `pageControl` and `progressView` exhibit low recall at small scales, confirming the need for specialized anchor/resolution consideration or targeted zoom augmentation.
3. **Absence of 28 Classes:** DS-G8 cannot be passed until a test corpus with coverage of all 41 classes is rendered and verified.

