# NativeUIAuditKit — Current State

**As of:** 2026-09-21 (local; latest handoff 2026-09-22 UTC)
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

**2026-09-22 parallel acquisition:** direct HTTP/simctl runner, development-only
v1.4 consumer and existing runtime-crop/baseline integration delivered;38 Python
and92 Swift tests pass. Matching installed Fixture launched and reference PNG
captured/visually checked. First focused target fails `non_view/unmapped_item`;
independent TTR job fails the same native-identity prerequisite. Fixture responsive,
ownership clear. Zero eligible pairs;42-recipe pilot and genuine baseline not run.
This supersedes the endpoint-unavailable and screenshot-only bottlenecks below.
[Handoff and producer request](../reports/work/TVGEN/handoff.md).

**2026-09-22 05:49 UTC diagnostic:** updated local TTR responds; exact-target
infrastructure readiness passes and ownership is clear. Repaired companion source
matches the producer receipt, but prior Fixture endpoint8080 refuses connection.
Capture/export/intake were not run; screenshot repair is locally unqualified, not
newly failed. [Diagnostic feedback](../reports/work/SIM-DATA-01-02/readiness-20260922-0548/handoff.md).

**2026-09-22 01:39 UTC smoke:** native reference focus now resolves and settles,
but screenshot output fails Cocoa513/EPERM writing frame.png in TTR's app-managed
capture directory. Zero accepted rows; no export/intake or training. Postflight
Fixture responsive and ownership clear. This supersedes readiness-only status below.
[Failure and producer request](../reports/work/SIM-DATA-01-02/smoke-20260922-0140/handoff.md).

**2026-09-22 01:34 UTC runtime check:** updated TTR/Fixture and repair checkout
fd50a80 are present; all infrastructure readiness checks pass with ownership clear.
Idle Fixture has no native sample yet. A new bounded smoke is ready to be authorized,
but capture/intake and training readiness are not established.
[Evidence](../reports/work/SIM-DATA-01-02/readiness-20260922-0134/handoff.md).

**Offline perception acceptance (2026-09-22):** PER-01 evidence inventory and
PER-02/04/05/06 offline scopes are accepted after integrated review/corrections.
[Acceptance](../reports/work/PERCEPTION-ACCEPTANCE/handoff.md). All 44 supplied
screenshots were visually triaged; no real gold-label benchmark or training corpus
was qualified. Screenshot output access remains the last observed producer blocker,
not the previously resolved native-reference focus failure. No new training or promotion.

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

**Parallel path approved, 2026-09-22:** [ADR-0009](ADR-0009-Direct-tvOS-Simulator-Generation.md)
defines direct native tvOS Fixture/OS generation independent of TTR capture/export.
Direct software and runtime inventory are now delivered for review; no corpus is
qualified. Both acquisition adapters currently share the Fixture native-focus
identity defect. TTR desktop acquisition remains independent; iOS reconstruction
is unchanged. See [current evidence](../reports/work/TVGEN/handoff.md).

**Legacy FocusRing reuse warning (2026-09-21):** the 1,500-pair crop corpus is
byte-decodable but not requalified. An audit found 84 identical-pixel groups crossing
partitions despite zero shared seeds; all examples are dark and frame-bound label
evidence is absent. Historical 270/270 and empty-hard-negative passes are not clean
qualification evidence. Preserve shipped weights; no automatic replacement follows.
[Audit and corrections](../reports/work/EVIDENCE-AUDIT/handoff.md).

**2026-09-21 FocusRing update:** local simulator runtime/storage readiness passed,
but the clean two-element smoke failed `native_focus_or_geometry_unavailable:
sceneNotSettled`; no eligible pilot exists. Broad simulator collection remains
paused. [Smoke evidence](../reports/work/SIM-DATA-01-02/smoke-20260921/executed-smoke.md).
**2026-09-22 00:35 UTC follow-up:** the newly authorized updated-build smoke also
failed, now narrowed to `unresolved_focus`: both buttons measured, no missing IDs,
36 native samples but no resolved focus. Inline recipe import succeeded after
file import incorrectly surfaced `serviceUnavailable`. Postflight Fixture responds
and ownership is clear; no completed bundle or training data. TTR diagnosis/fix
requested; no automatic retry. [Latest evidence](../reports/work/SIM-DATA-01-02/smoke-20260922-0031/handoff.md).
Offline [launch preparation](Plans/FocusRingLaunchPreparation.md) is delivered for
review: runtime-exact crops, actual CoreML baseline adapter and frozen capture
planning. A tested crop-origin correction changes inference preprocessing, not
shipped weights; historical runtime metrics cannot establish its quality. No
training or promotion occurred. The older operational snapshot below is historical,
not a fresh Office/producer readiness check.

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

**Independent corpus blocker — TASK-DATA-01 (updated 2026-09-22 UTC):** All 2,000 historical synthetic test links remain broken, plus 10,543/11,984 training and 2,696/3,056 validation image links; labels and historical Run 009 mAP50=0.585669 remain intact. Missing files do not establish deletion cause. P0-C is executing a separately authorized native-only replacement, not historical recovery. Failed attempts exposed writer/schema drift, native-navigation geometry defects and repeated pixels; evidence is preserved. Corrected-source preflight passes eight native tests and independent validation of 346 sample pairs. The [r5 continuation](../reports/work/P0-C/reconstruction-configuration-r5.md) retains 7,500 verified completed r4 captures with explicit build lineage and collects 9,440 remaining slots toward the unchanged 16,940 target. Full capture/audit remains in progress, not eligible training data yet. `webContent` remains uncovered. [Historical availability evidence](../reports/dataset_availability_2026-09-19.md); [recovery plan](DatasetRecoveryPlan.md); [resumption evidence](../reports/work/P0-C/resumption-20260922.md). Baseline inference, frozen-suite acceptance and training still depend on completed corpus qualification; offline work is independent.

FocusRing v0.1 is independent of that bottleneck and is already bundled.

---

## Train / eval pointers

- Run log: [`ExperimentLog.md`](ExperimentLog.md)
- Doc index: [`README.md`](README.md)
- Fixture ingest format: [`FixtureBatchIngest.md`](FixtureBatchIngest.md)
- Phase streams: [`PhaseMap.md`](PhaseMap.md)
- FocusRing: [`FocusRingDetectorSpec.md`](FocusRingDetectorSpec.md)
- Provenance: [`../PROVENANCE.md`](../PROVENANCE.md)
