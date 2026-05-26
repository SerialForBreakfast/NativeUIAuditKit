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

## Run 003 — Strip-Tiled Training (Complete 2026-05-26)

**Date:** 2026-05-24 (PID 7107 started ~23:48, crashed disk-full at 05:09); retry PID 10413 started 2026-05-25 ~18:22, completed 2026-05-26 05:18  
**Status:** COMPLETE  
**Actual duration:** ~11 hours (wall clock — Create ML's objectPrint takes far longer than the 90-min estimate when dataset is 4× larger)

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
# After training completes, run in order:
swift scripts/test_model_predictions.swift   # spot check: alert IoU > 0.9? any navBar detections?
swift scripts/eval_map.swift                 # full 3-pass mAP on 1,364 validation images

# For confusion matrix (TASK-6-5):
WRITE_YOLO_PREDS=1 swift scripts/eval_map.swift   # also writes reports/yolo_preds/
swift scripts/export_yolo_gt.swift                 # writes reports/yolo_gt/
python scripts/confusion_matrix.py \
  --gt-dir reports/yolo_gt \
  --pred-dir reports/yolo_preds \
  --version 1
```

**⚠️ Eval pipeline fix applied during training:**
`scripts/eval_map.swift` was updated (2026-05-25) to run all 3 passes (full-image + SAHI + horizontal strips) before Run 003 completed. The previous version ran only a full-image pass and would have reported AP=0 for navigationBar/textField even if the strip-trained model correctly detects them in strips. This is now fixed — the eval script matches the 3-pass inference pipeline in `NativeUIDetectionRequest`.

**Disk-full incident during Run 003:**
PID 7107 (first attempt) crashed at `write(to:)` with "No space left on device" despite 144Gi nominally free. Root cause: 24GB of accumulated compiled eval caches (`*.mlmodelc` in `/var/folders/.../T/`) consumed available headroom. Fixed by deleting stale caches before retry, freeing 170Gi. See `Research/TrainingRunbook.md` Step 0 for the pre-flight disk check protocol added as a result.

**Built-in validation metrics (Create ML's `.scaleFit` eval — unreliable for portrait images, see BP-25):**
- mAP@0.5: 0.0066
- alert: 0.025, navigationBar: 0.000, primaryButton: 0.004, textField: 0.000, toggle: 0.004

**Custom 3-pass eval results (`scripts/eval_map.swift`, IoU@0.5, NMS@0.45):**

| Class | Run 002 AP | Run 003 AP | Change | Notes |
|---|---|---|---|---|
| alert | 0.909 | 0.101 | 📉 regression | Recall=100% (40/40 TP) but 2,999 predictions → massive FP |
| navigationBar | 0.000 | **0.137** | 📈 strip fix ✓ | Recall=100% (1,156/1,156 TP) but 15,591 predictions |
| primaryButton | 0.165 | **0.456** | 📈 improved | 683/731 TP, 3,534 predictions |
| textField | 0.000 | **0.129** | 📈 strip fix ✓ | 259/315 TP, 6,100 predictions |
| toggle | 0.605 | 0.236 | 📉 regression | 785/845 TP (93%), 10,481 predictions |
| **mAP@0.5** | **0.336** | **0.212** | 📉 overall | DS-G5 floor (0.50) not met |

**Spot check (`test_model_predictions.swift`):**
- alert [full pass]: IoU=0.881 ✓ (previously 0.909 — minor regression)
- navigationBar [strip pass]: IoU=0.977 ✓ (previously 0.000 — definitive proof strip fix works)

**Diagnosis — false positive explosion:**
The strip tiling fix definitively solved the anchor-assignment failure for navigationBar and textField (both moved from 0.000 to detectable). However, the model suffers from severe confidence saturation: almost all predictions output confidence ≈ 1.0, and the 3-pass pipeline (8-10 strips per image × many predictions per strip) generates 5-14× more predictions per image than the GT count. After NMS at IoU=0.45, adjacent-strip predictions of the same navBar remain (IoU between adjacent strips ≈ 0.30-0.40, below the merge threshold) → many FPs per true detection.

Root causes (in priority order):
1. **Cross-strip NMS gap**: Adjacent strips (50% overlap) predict the same navBar/textField with IoU ~0.35 — below the NMS threshold of 0.45 — so they are not merged. Lowering NMS threshold to 0.30 for strip pairs, or using class-aware suppression with distance-based merge, would help.
2. **Confidence saturation**: Every prediction is near conf=1.0 regardless of quality. Likely caused by 25,000 iterations being too many for this dataset size (18,563 records × 43 effective epochs) — model overfit and output logits drove to saturation.
3. **Class imbalance**: alert=320 vs navigationBar=3,709 (11.6:1) exceeds the 5:1 cap. The alert class has too few examples relative to other classes; the model deprioritized calibration for it.

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
| Strip training fixes anchor assignment but creates FP explosion via cross-strip duplicates | Run 003 mAP 0.212 despite 100% recall | Lower NMS threshold to 0.30 |
| 25K iterations on large dataset → confidence saturation (all preds ~1.0) | Precision collapses | Cap iterations at 10K |
| Class imbalance >5:1 degrades minority class AP severely | alert: 0.909→0.101 | Enforce 5:1 cap in TrainingConfig |
| `.mlmodelc` eval caches fill `/var/folders/.../T/` — clear before each training run | 24GB consumed → disk full crash | TrainingRunbook Step 0 |
| Create ML training on 18,563 images takes ~11h (not 90 min) | Monitoring cadence needs updating | TrainingRunbook Step 2 |

---

## Key Lessons Learned — New Entries from Run 003

| Lesson | Impact | Reference |
|---|---|---|
| Create ML training takes ~11h for 25K iterations on 18,563-image dataset (not 90 min) | Scheduling / monitoring significantly harder | This entry |
| `.mlmodelc` eval caches accumulate in `/var/folders/.../T/` — 3,445 files = 24GB after 3 runs | "No space left on device" crash at model write | TrainingRunbook Step 0 |
| Create ML's built-in validation metrics use `.scaleFit` — always near-zero, always ignore | Confirmed yet again (mAP=0.0066 on a model with 100% recall) | BP-25 |
| Strip pass detections from adjacent strips have IoU ~0.35 — below NMS 0.45 threshold → not merged | 10-15× FP multiplier for navBar/textField | Run 004 plan |
| 25K iterations on 18,563 records = ~43 effective epochs → confidence saturation (all preds ~1.0) | AP tanked despite good recall | Run 004: reduce iterations |
| Class imbalance 11.6:1 (navBar/alert) exceeds 5:1 plan cap → alert calibration degraded | alert AP: 0.909 → 0.101 | Run 004: cap at 5:1 |

---

## Pending Runs

### Run 004 — FP-suppression + class-balance fix (Next)

**Trigger:** Run 003 complete, mAP=0.212 (below DS-G5 floor of 0.50)

**Three changes for Run 004:**

1. **Lower NMS IoU threshold in `eval_map.swift` from 0.45 → 0.30** (eval-only change, no retraining needed)
   - First, re-evaluate Run 003 model with NMS=0.30 to quantify how much the cross-strip merge gap is responsible
   - If mAP jumps significantly → the Run 003 model may already be good; no new training needed

2. **Reduce max iterations to 10,000** (if retraining is needed)
   - 25K → 10K reduces effective epochs from ~43 to ~17, reducing confidence saturation
   - Run 002 used 10K on 4,509 images and achieved alert=0.909 — validate this still works

3. **Enforce 5:1 class balance cap** (`subsamplingCapPerClass` in `TrainingConfig.swift`)
   - With alert=320 as the minimum, cap other classes at 320×5=1,600 instances
   - Current: navBar=3,709 (11.6:1 ratio); capped: navBar=1,600
   - This will reduce training set from 18,563 to approximately 9,000-10,000 records

**Do step 1 first (eval-only, 10 minutes) before committing to a new training run.**

### Run 005 (if needed) — YOLO11 migration
**Trigger:** Run 004 mAP < 0.50 after both eval and retrain fixes  
**Rationale:** If Create ML's objectPrint algorithm cannot achieve adequate precision with strip training, migrate to YOLOv11 (via ultralytics) which supports custom anchor configurations and better handles thin-box classes natively.
