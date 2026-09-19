# NativeUIAuditKit — Phase Map

**As of:** 2026-09-19
**Open work:** [`../Tasks.md`](../Tasks.md)  
**Archive:** [`../CompletedTasks.md`](../CompletedTasks.md)

Production phase gates remain binding. Within Phase 6a, software slices are independently acceptable; missing hardware/data blocks qualification, not all development. [IterationRoadmap.md](IterationRoadmap.md) defines lanes and [ImplementationPlans.md](ImplementationPlans.md) defines slice contracts. Historical task write-ups live in the archive, not in Tasks.md.

Full-backlog dispatch uses revision-4 packets and the maintainer-approved DeliveryDecisions.
First: H1, P1-A, P0-A, P4-A, P5-A. Hardware priority: small compatibility batch → FocusRing →
real tvOS holdout → larger fixture collection. After DS-G8 prioritize macOS; badge specification
is independent but its 42-class candidate follows the 41-class milestone. Crop/unified work has
lower priority and keeps its own gates. ScreenAuditKit fake-backed integration is independently
assignable in its own repository. Release of qualified 41-class weights does not wait for all branches.

```
Phases 0–5b ✅
  └─ Phase 6 (5-class iOS YOLO11n) ✅  nativeui-ios-v2.0
       ├─ Phase 6-gate (Foundation Models) ✅ skipped — no image-input API
       ├─ Phase 6d (NativeUIDetectionRequest v2) ✅
       ├─ Phase 7 OCR + audit rules ✅
       ├─ Phase 8 device/OS inference ✅
       └─ Phase 9-1 NativeUIRecognizing ✅
            └─ Phase 9-2/9-3 ScreenAuditKit contract + CLI  ← remaining, other repo

Phase 6a (41-class iOS) — in progress, 41-class weights not shipped
  Run 009 holdout mAP@0.5 = 0.586 (DS-G8 fail)
  ├─ Evaluation software: P1-A, P2-A, P3-A      independent of missing pixels
  ├─ Harvest compatibility: H1, P4-A, P4-B     offline producer/consumer cases
  ├─ Dataset recovery: P0-A → reviewed P0-B    independent recovery lane
  ├─ Training preparation: P5-A               no-training preflight
  ├─ Real baseline/suite: P1-B/P2-B/P3-B       needs eligible recovered/rebuilt test corpus
  └─ TASK-6a-10: full fixture retraining      needs eligible synthetic + fixture corpora
       └─ TASK-6a-12: partial-crop fork         after 6a-10 baseline

Phase 6b tvOS ✅ v3.0 shipped
  ├─ 6b-S / T / WP1 / E ✅
  ├─ 6b-R-2 / R-3 ✅ hardware qualification
  ├─ 6b-R-1 scale to ≥500 real held-out frames  [~]
  ├─ 6b-FD FocusRing v0.1 ✅
  │    └─ FOCUS-DET-05 6,000 pairs + hard-neg   [ ]
  └─ 6b-U unified iOS+tvOS model                [ ]

Phase 6c macOS                                      [ ]
Later badge model: BADGE-A → BADGE-B (after 41-class milestone)
```

Independent of shipping new 41-class weights (each retains its own prerequisites):

- FOCUS-DET-05 (needs Office live harvest, `light`/`highContrast`)
- TASK-6b-R-1 scale-out (needs hardware)
- Track 3: PROVENANCE history-rewrite decision; next git tag blocked on 6a-10
- TVTestRig producer identity/contract tests and application integration with already shipped models (owned in TVTestRig)

Phase 6c is **not independent**: it remains blocked on DS-G8. The partial-crop fork remains blocked on 6a-10. No software-slice completion substitutes for either gate.

The original synthetic test corpus currently has zero resolvable pixels; historical metrics survive but are not a runnable corpus. Live fixture qualification separately awaits identity attestation, available/authorized Office hardware, and a compliant export path. These blockers converge only at real evaluation/training; they do not serialize all software work.

Generator layout rules from Phase 1 live in [`CoordinateSpike.md`](CoordinateSpike.md) and [`BestPractices.md`](BestPractices.md) (BP-01–BP-04), not in `Tasks.md`.
