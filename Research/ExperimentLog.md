# NativeUIAuditKit — Experiment Log

Chronological record of every training run and major technical decision in Phase 6. Written so that any future agent or engineer can reconstruct what was tried, why, and what the outcome was — without reading the full conversation history.

Last updated: 2026-05-24

---

## How to Read This Log

Each entry has:
- **Run ID**: sequential, used in reports and cross-references
- **Date / wall time**: calendar date and approximate elapsed training time
- **Configuration**: key parameters that differed from default
- **Outcome**: actual metrics, errors, or observations
- **Diagnosis**: what we think happened and why
- **Action taken**: what changed as a result

---

## Run 001 — First Full Training Run (Pixel-Coordinate Bug)

**Date:** 2026-05-22  
**Elapsed:** ~45 min (10,000 iterations)  
**Configuration:**
- Algorithm: transferLearning(objectPrint revision:1)
- Max iterations: 10,000
- Batch size: 32
- Dataset: 4,509 training images (full images only, no strip tiling)
- Annotation format: **PIXEL coordinates** (bug — should be normalized [0,1])

**Outcome:**
- Training completed without error
- `detector.evaluation(on:)` → mAP@0.5 ≈ 0.001
- All class APs ≈ 0.000

**Diagnosis:**
- Root cause: annotation coordinates were in PIXELS, not normalized [0,1] as `MLObjectDetector.AnnotationType.boundingBox(units: .normalized, ...)` expects. The model received wildly large cx/cy/w/h values (e.g. cx=550 instead of 0.47) and could not learn any meaningful geometry.
- Secondary confusion: the `evaluation(on:)` result would have been near-zero anyway due to a separate `.scaleFit` bug (see Run 002), but the pixel-coordinate issue was the primary failure here.

**Action taken:**
- Fixed `CreateMLExporter.swift` to convert `boundsVisionNormalized` → Create ML normalized coords (cx, cy, w, h all in [0,1])
- Formula: `cx = vn.x + vn.w/2`, `cy = 1.0 - vn.y - vn.h/2`
- Documented in `Research/BestPractices.md` — check before every future run

---

## Run 002 — Second Full Training Run (Normalization Fixed, scaleFit Evaluation Bug Discovered)

**Date:** 2026-05-23  
**Elapsed:** ~45 min (10,000 iterations)  
**Configuration:**
- Algorithm: transferLearning(objectPrint revision:1)
- Max iterations: 10,000
- Batch size: 32
- Dataset: 4,509 training images (full images, no strip tiling)
- Annotation format: **NORMALIZED [0,1]** ← fixed from Run 001

**Outcome (via `detector.evaluation(on:)`):**
- mAP@0.5 ≈ 0.001 (same as Run 001 — appeared unchanged)
- All class APs ≈ 0.000

**Outcome (via custom `scripts/eval_map.swift` with `.scaleFill`):**
| Class | AP@0.5 |
|---|---|
| alert | 0.909 |
| toggle | 0.605 |
| primaryButton | 0.165 |
| navigationBar | 0.000 |
| textField | 0.000 |
| **mAP** | **0.336** |

**Diagnosis (scaleFit evaluation bug — BP-25):**
`MLObjectDetector.evaluation(on:)` runs `VNCoreMLRequest` internally with `.scaleFit` (letterboxing). Create ML trains objectPrint by scale-filling to 299×299. For 1179×2556 portrait images:
- `.scaleFit` shrinks the image to fit 299×299 with black padding (image is only 138px wide in the 299-wide input)
- A predicted box at cx=0.687, w=0.687 (correct in training space) remaps to w≈1.49 in original image space
- IoU(1.49-wide pred, 0.687-wide GT) ≈ 0.457 — just below the 0.5 threshold
- Result: every correct prediction registers as a FP; mAP = 0

**Fix:** Always use `.scaleFill` in custom inference and evaluation. Built-in `evaluation(on:)` cannot be fixed — use `scripts/eval_map.swift` instead.

**Diagnosis (navigationBar/textField AP=0 — BP-26):**
Actual mAP of 0.336 revealed that alert and toggle ARE being detected, but navigationBar and textField have AP=0 despite having the most training instances (3,709 and 2,000 respectively). Investigation:
- `scripts/inspect_model_outputs.swift` with `confidenceThreshold=0.0` confirmed the model produces 14,661 YOLO candidates on a navigationBar test image
- Best candidate at the correct y-position had max confidence 0.0024 (for class "toggle", not "navigationBar")
- The navigationBar bounding box has aspect ratio 16:1 (w=1.0, h=0.063). Even a generous anchor of (0.5, 0.5) gives center-IoU ≈ 0.11 with a 16:1 box. Assignment threshold is ~0.4–0.5. **No anchor is ever matched to navigationBar during training → zero gradient → model never learns the class.**

**Action taken:**
- Documented scaleFit bug as BP-25 in `Research/BestPractices.md`
- Documented anchor assignment failure as BP-26
- Created `scripts/eval_map.swift` — correct custom evaluation using `.scaleFill`
- Created `scripts/test_model_predictions.swift` — single-image diagnostic
- Created `scripts/inspect_model_outputs.swift` — raw tensor inspector bypassing VNCoreMLRequest
- Decided to fix the anchor-assignment problem before Run 003 (see Run 003 configuration)

---

## Run 003 — Strip-Tiled Training (In Progress as of 2026-05-24)

**Date:** 2026-05-24 (started ~23:48)  
**Status:** IN PROGRESS — PID 7107, ~10 min elapsed at last check  
**Expected duration:** ~90 min (25,000 iterations on 18,563 records)

**Configuration:**
- Algorithm: transferLearning(objectPrint revision:1)
- Max iterations: **25,000** (increased from 10,000 — more data, more iterations needed)
- Batch size: 32
- Training records: **18,563** (4,509 full images + 14,054 horizontal strip images)
- Validation: **1,364 full images** (strips are training-only augmentation)
- Strip configuration: 22% of image height per strip, 50% overlap (stride = stripH/2)

**Strip tiling rationale (fix for BP-26):**
A 22%-height horizontal strip of a 2556px-tall iPhone screenshot is 562px tall, 1179px wide → roughly 1179×562 in the strip. At 299×299 training input after scale-fill:
- navigationBar occupies width=1179, height=~160px within the strip → height fraction ≈ 160/562 = 0.285 of strip height
- Strip-space aspect ratio: 1.0 / 0.285 ≈ **3.5:1** (down from 16:1 in full image)
- textField strip-space aspect ratio: **~2.5:1** (down from 21:1)
- primaryButton: **~2.0:1** (down from ~6:1)

Verified by `scripts/verify_strip_export.swift`:
- navigationBar strip AR: 1.83:1 ✓ (< 4:1 threshold)
- textField strip AR: 2.46:1 ✓
- primaryButton strip AR: 1.96:1 ✓
- alert strip AR: 0.87:1 ✓
- toggle strip AR: 0.65:1 ✓

**Training counts (after strip generation):**
- Train: 18,563 records (4,509 full + 14,054 strips)
- Per-class full-image counts: alert=320, navigationBar=3709, primaryButton=3120, textField=2000, toggle=2740

**Log location:** `NativeUITrainer/training.log`

**Expected outcome (based on anchor IoU analysis):**
- navigationBar: aspect ratio 3.5:1 in strip space → anchor IoU > 0.5 achievable → expect AP > 0.00, target > 0.50
- textField: aspect ratio 2.5:1 → expect AP > 0.00, target > 0.40
- primaryButton: already had some detections (AP=0.165); strip training may improve recall
- alert, toggle: unaffected (square-ish objects, already worked in Run 002)
- Target overall mAP: > 0.60 (approaching DS-G6 gate of 0.70)

**Follow-up evaluation (to run after training completes):**
```bash
# After training completes, run:
swift scripts/test_model_predictions.swift   # verify alert IoU > 0.9, check if navBar appears
swift scripts/eval_map.swift                 # full per-class mAP on 1,364 validation images
```

---

## Key Lessons Learned (Summary across all runs)

| Lesson | Impact | Reference |
|---|---|---|
| Annotation coordinates must be normalized [0,1], not pixels | Run 001 wasted | BP, Section 2 |
| `MLObjectDetector.evaluation(on:)` uses `.scaleFit` → mAP≈0 for portrait images | Run 002 appeared to fail | BP-25, LessonsLearned §3 |
| Always use `.scaleFill` for VNCoreMLRequest on portrait images | Every inference and eval | BP-25 |
| YOLO anchor assignment fails for 16:1 boxes → zero gradient | navBar/textField AP=0 | BP-26, LessonsLearned §4 |
| Training log must go inside the project: `NativeUITrainer/training.log` | Files lost outside project | AGENTS.md |
| Run 50-iteration smoke test before full training | Would have caught Run 001 bug in <30s | LessonsLearned §10.1 |
| Custom eval loop is required — do not trust `evaluation(on:)` | Mis-diagnosed two runs | LessonsLearned §9 |

---

## Pending Runs (Planned After Run 003)

### Run 004 — Post-strip evaluation & possible class-balance fix
**Trigger:** Run 003 completes  
**Decision tree:**
- If navigationBar AP > 0.50 and textField AP > 0.30 → proceed to DS-G6 gate check (mAP ≥ 0.70)
- If mAP < 0.50 → investigate class imbalance: alert has only 320 training instances vs navigationBar 3,709 (11.6:1 ratio — exceeds 5:1 plan cap). Reduce navigation bar cap to 1,600 and retrain.
- If navigationBar still AP=0 → the anchor hypothesis is confirmed but insufficient; consider YOLO11 migration (Phase 6a path)

### Run 005 (if needed) — Class-balanced retrain  
**Trigger:** Run 004 mAP < 0.50 or alert/toggle regression  
**Configuration change:** Reduce `subsamplingCapPerClass` to 800 (to enforce 5:1 max given alert=320 minimum), or boost alert instances by adding more alert-focused templates to the generator
