# NativeUIAuditKit — Current State

**As of:** 2026-09-18  
**Audience:** maintainers and agents  
**Open work:** [`Tasks.md`](../Tasks.md)  
**Finished work:** [`CompletedTasks.md`](../CompletedTasks.md)

This page is the living snapshot. If it disagrees with `AGENTS.md` or `README.md`, fix those to match this file.

---

## Shipped

| Artifact | ID | Notes |
|---|---|---|
| iOS 5-class detector | `nativeui-ios-v2.0` | YOLO11n, mAP@0.5 = 0.935 CoreML / 0.968 `.pt`. Latency ~7.5 ms/image. |
| tvOS OS UI detector | `nativeui-tvos-v3.0` | YOLO11n, 25 trained classes, mAP@0.5 = 0.9822. Bundled as `NativeUIModel_tvOS.mlmodelc`. |
| Stage 2 focus classifier | `focus-ring-detector-v1.0` | MobileNetV4-Conv-Small, FDR-001. FP16 4.80 MB. Bundled as `FocusRingDetector.mlmodelc`. Torch test 270/270. Hard-neg n=0. |
| Detection API | `NativeUIDetectionRequest` | YOLO letterbox inference, OCR fusion, audit rules, device inference, optional FocusRing Stage 2. |
| Perception primitives | Frame similarity, change-ROI, text-anchor verify | Track 4, for TVTestRig to consume. |

Phases **0–5b**, **6** (5-class), **6d**, **6-gate (skipped)**, **6b-S / WP1 / E**, **6b-R-2 / R-3**, **6b-FD-01–04**, **7**, **8**, **9-1**, Track 4, extraction checklist: **complete.** See [`CompletedTasks.md`](../CompletedTasks.md).

---

## Not shipped

| Item | Why |
|---|---|
| 41-class iOS YOLO11m | Run 009 withheld-template holdout mAP@0.5 = **0.586** (DS-G8 ≥ 0.850). In-family val 0.991. |
| FocusRing v1.0 | Need ≥6,000 pairs and non-vacuous `light`/`highContrast` hard-neg (FOCUS-DET-05). |
| macOS detector | Phase 6c not started. |
| Unified iOS+tvOS model | Phase 6b-U not started. Keep separate models until every gate passes. |
| ScreenAuditKit contract/CLI | TASK-9-2 / 9-3 live in ScreenAuditKit, not this repo's remaining core path. |

---

## Current bottleneck

**TASK-6a-10** — full-frame fixture retraining for 41-class iOS. Ingest scripts are written and unit-tested. Live `aatv fixture batch` is blocked on TVTestRig coordinator IPC (`serviceUnavailable`) and on an authorized Office hardware run. Do not retrain on empty sidecars or the model's own `*_result.json` predictions.

FocusRing v0.1 is independent of that bottleneck and is already bundled.

---

## Train / eval pointers

- Run log: [`ExperimentLog.md`](ExperimentLog.md)
- Doc index: [`README.md`](README.md)
- Fixture ingest format: [`FixtureBatchIngest.md`](FixtureBatchIngest.md)
- Phase streams: [`PhaseMap.md`](PhaseMap.md)
- FocusRing: [`FocusRingDetectorSpec.md`](FocusRingDetectorSpec.md)
- Provenance: [`../PROVENANCE.md`](../PROVENANCE.md)
