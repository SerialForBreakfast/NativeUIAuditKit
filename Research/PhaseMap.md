# NativeUIAuditKit — Phase Map

**As of:** 2026-09-18  
**Open work:** [`../Tasks.md`](../Tasks.md)  
**Archive:** [`../CompletedTasks.md`](../CompletedTasks.md)

Dependency order is still binding: do not start Phase N+1 until Phase N's gate is documented. Historical task write-ups live in the archive, not in `Tasks.md`.

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
  └─ TASK-6a-10: fixture retraining          [!] data/IPC blocked
       ├─ TASK-6a-11: multi-corpus eval      [~] 1 of 4 corpora exist
       └─ TASK-6a-12: partial-crop fork      [ ] after 6a-10 baseline

Phase 6b tvOS ✅ v3.0 shipped
  ├─ 6b-S / T / WP1 / E ✅
  ├─ 6b-R-2 / R-3 ✅ hardware qualification
  ├─ 6b-R-1 scale to ≥500 real held-out frames  [~]
  ├─ 6b-FD FocusRing v0.1 ✅
  │    └─ FOCUS-DET-05 6,000 pairs + hard-neg   [ ]
  └─ 6b-U unified iOS+tvOS model                [ ]

Phase 6c macOS                                      [ ]
```

Independent of 6a (can proceed without shipping 41-class weights):

- FOCUS-DET-05 (needs Office live harvest, `light`/`highContrast`)
- TASK-6b-R-1 scale-out (needs hardware)
- Track 3: PROVENANCE history-rewrite decision; next git tag blocked on 6a-10
- Phase 6c (spec says it requires the 6a gate; do not start until that is explicit)

Generator layout rules from Phase 1 live in [`CoordinateSpike.md`](CoordinateSpike.md) and [`BestPractices.md`](BestPractices.md) (BP-01–BP-04), not in `Tasks.md`.
