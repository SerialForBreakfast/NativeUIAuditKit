# NativeUIAuditKit — Current State

**As of:** 2026-09-19
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
| Badge/42-class expansion | Approved later milestone; 41-class release remains first. No enum/map/model change has shipped. |
| ScreenAuditKit contract/CLI | TASK-9-2 / 9-3 live in ScreenAuditKit, not this repo's remaining core path. |

---

## Current bottleneck

**TASK-6a-10** — full-frame fixture retraining for 41-class iOS. Ingest scripts are written and unit-tested. Coordinator IPC was resolved on 2026-09-18; the later live batch gate is `identity_preflight` / `identityUnavailable` until TVTestRig's adapters attest a shared HarvestIdentity. Office is occupied as of 2026-09-19; an authorized hardware run is a separate prerequisite. See [the recorded evidence](../reports/tvtestrig_feedback_2026-09-18.md). Do not retrain on empty sidecars or the model's own `*_result.json` predictions.

Office-independent work is defined in [ImplementationPlans.md](ImplementationPlans.md); dispatch state lives only in Tasks.md.

**Accepted offline foundation (2026-09-19):** H1 and the NUIAK software scopes of
P1-A, P2-A, P3-A, P4-A, P4-B, P5-A, and FR-A are accepted. This establishes fail-closed
consumer, evaluation, assembly, preflight, and FocusRing-alignment interfaces only.
It does not establish eligible pixels, a genuine producer bundle, live capture behavior,
or a candidate-model gate; those remain separately blocked in `Tasks.md`.

For the explicit iOS five-class → 41-class path, use the
[iOS platform tasks](../Tasks.md#ios-platform-tasks) and
[five-tranche delivery plan](Plans/iOSPlatform.md). Corpus recovery, offline toolchain
acceptance, and eligible synthetic baseline evaluation do not require Office. Live
fixture qualification is a separate input to the planned mixed-data candidate.

The [iteration roadmap](IterationRoadmap.md) separates software acceptance from data/model qualification. H1 producer-contract work, export/selector/preflight software, and recovery assessment are independently dispatchable. TVTestRig has a documented offline bundle-validator lane at inspected revision `586050e`; consumer compatibility remains to be implemented/verified, and passing offline integrity is not trusted capture evidence.

The accepted full backlog is defined as independent revision-4 [worker packets](ImplementationPlans.md),
including later models and separately owned consumer work. [DeliveryDecisions.md](DeliveryDecisions.md)
keeps 41-class first, moves badge to a versioned later model, prioritizes FocusRing then macOS
after DS-G8, and separates software/data/integration/model outcomes. Publishing these plans
does not mark any worker implementation, experiment or quality gate complete.

**New independent blocker — TASK-DATA-01 (2026-09-19):** Manifest-based inspection found all 2,000 synthetic test links broken, plus 10,543/11,984 training and 2,696/3,056 validation entries with broken image links; corresponding labels survive. The historical Run 009 mAP50=0.585669 report remains intact, but cannot currently be reproduced from this corpus. Missing files do not establish deletion cause. The native-only P0-C replacement path retired its failed WKWebView route and passed UIKit validation, but its fresh generator launcher was externally terminated with exit 137 before progress or output; no replacement corpus exists. [Evidence](../reports/dataset_availability_2026-09-19.md); [P0 recovery plan](DatasetRecoveryPlan.md); [P0-C record](../reports/work/P0-C/web-content-blocker.md). Baseline inference, frozen-suite acceptance, and full training depend on verified corpus readiness; offline tooling and ingest tests can proceed.

FocusRing v0.1 is independent of that bottleneck and is already bundled.

---

## Train / eval pointers

- Run log: [`ExperimentLog.md`](ExperimentLog.md)
- Doc index: [`README.md`](README.md)
- Fixture ingest format: [`FixtureBatchIngest.md`](FixtureBatchIngest.md)
- Phase streams: [`PhaseMap.md`](PhaseMap.md)
- FocusRing: [`FocusRingDetectorSpec.md`](FocusRingDetectorSpec.md)
- Provenance: [`../PROVENANCE.md`](../PROVENANCE.md)
