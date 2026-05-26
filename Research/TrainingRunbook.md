# NativeUIAuditKit — Model Training Runbook

Step-by-step procedure for training, evaluating, and diagnosing the 5-class iOS CoreML model.
Written to be followed by an agent or engineer who has no memory of prior sessions.

Last updated: 2026-05-25

---

## Prerequisites

Before starting any training run, confirm:

1. `swift build` passes in the package root — zero errors
2. Dataset is at the expected path (check `NativeUITrainer/Sources/main.swift` `Args.parse()` for the `--dataset` flag target)
3. `NativeUIAuditKitModels/Sources/NativeUIAuditKitModels/` is the output directory
4. There is no active training run: `ps aux | grep NativeUITrainer | grep -v grep`

---

## Step 0 — Disk Space Pre-Flight (New — Required After Run 003)

**Root cause discovered during Run 003:** Create ML writes ~23 GB of UUID-named training checkpoint files to `/var/folders/.../T/CreateMLModels/` during a 25,000-iteration run. These are NOT automatically cleaned up after a failed run. Combined with accumulated compiled-model caches (`.mlmodelc` files from `eval_map.swift` runs), this consumed all available headroom at the moment of the final `write(to:)` — causing the "No space left on device" crash even with nominally 144 GB free.

### Before every training run:

```bash
# 1. Check free space — need > 50 GB free AFTER accounting for CreateMLModels growth
df -h /System/Volumes/Data

# 2. Check for stale CreateMLModels checkpoints from a prior failed run
du -sh /var/folders/*/b*/T/CreateMLModels/ 2>/dev/null

# 3. If previous run failed: delete its stale checkpoints (safe — not used by new run)
# (replace path with actual path from step 2)
rm -rf /var/folders/4w/b85wbq0d43vdx6rpgpc2jxhm0000gn/T/CreateMLModels/

# 4. Delete accumulated compiled eval caches (re-created on next eval_map.swift run)
find /var/folders/*/b*/T/ -maxdepth 1 -name "*.mlmodelc" -type d -print0 | xargs -0 rm -rf

# 5. Delete any 0-byte stub from a prior failed model write
ls -la NativeUIAuditKitModels/Sources/NativeUIAuditKitModels/NativeUIDetector_v1.mlpackage.mlmodel 2>/dev/null
# If it exists and is 0 bytes, delete it:
# rm -f NativeUIAuditKitModels/Sources/NativeUIAuditKitModels/NativeUIDetector_v1.mlpackage.mlmodel
```

**Minimum safe free space before training:** 50 GB (model write is ~7 MB; training temp files peak at ~23 GB).

---

## Step 1 — Pre-Flight Checks (Do Not Skip)

Skipping pre-flight cost two 45-minute training runs. Run every check.

### 1a. Verify annotation coordinates are normalized

Sample 5 annotation entries from the training split. All `cx`, `cy`, `w`, `h` values must be in `[0, 1]`. If any value is > 1.0, the annotations are in pixels — fix `CreateMLExporter.swift` before training.

```bash
# Quick sanity check: look at the annotation file in the createml_export directory
# (if it already exists from a prior export)
head -1 <dataset-path>/createml_export/train/annotations.json | python3 -c \
  "import sys,json; a=json.load(sys.stdin); \
   c=a[0]['annotation'][0]['coordinates']; \
   print(c); assert c['x']<=1.0 and c['y']<=1.0"
```

### 1b. Verify Vision → Create ML coordinate conversion

For a navigationBar annotation (which has `boundsVisionNormalized.y ≈ 0.89` because it's near the top of the image when measured from Vision's bottom-left origin), the Create ML cy should be close to 0.07 (near the top when measured from Create ML's top-left origin):

`cy = 1.0 - vn.y - vn.h/2`  
If `vn.y = 0.89`, `vn.h = 0.063`: `cy = 1.0 - 0.89 - 0.0315 = 0.0785` ✓

### 1c. Run a 50-iteration smoke test

Before a full run, temporarily set `maxIterations: 50` in `TrainingConfig.swift`, run training, and confirm:
- Training completes without error
- `swift scripts/test_model_predictions.swift` returns at least one prediction (even at low confidence) on a known test image

Reset `maxIterations` to the intended value (default: 25,000) before the full run.

### 1d. Check existing log for a prior run

```bash
tail -50 NativeUITrainer/training.log
ps aux | grep NativeUITrainer | grep -v grep
```

If a training process is running, do not start another.

---

## Step 2 — Launch Training

Training runs for ~90 minutes (25,000 iterations on 18,563 records with strip tiling). Use `nohup` so it survives terminal closure.

```bash
# From NativeUIAuditKit package root:
nohup swift run NativeUITrainer \
  --dataset <path-to-NativeUIAuditKit-Dataset> \
  --output  NativeUIAuditKitModels/Sources/NativeUIAuditKitModels \
  >> NativeUITrainer/training.log 2>&1 &
echo "PID: $!"
```

Record the PID. Add an entry to `Research/ExperimentLog.md` with the configuration before walking away.

**Log the PID, date, and config in ExperimentLog.md right now — before you do anything else.**

### What normal output looks like

Create ML does NOT print per-iteration progress from a CLI. The log will look like:

```
── Step 1: Exporting to Create ML format ──
...
  Exported 18563 images to .../createml_export/train
    (4509 full images + 14054 strips)
    alert: 320 instances
    navigationBar: 3709 instances
    ...

── Step 2: Configuring Create ML data sources ──
── Step 3: Training (this takes a while) ──
  Algorithm        : transferLearning(objectPrint revision:1)
  Max iterations   : 25000
  ...

Parsing JSON records from .../annotations.json
Successfully parsed 18563 elements from the JSON file ...
[SILENCE — training is running. This is normal. Wait ~90 min.]
── Step 4: Validation metrics ──
  Validation mAP@0.5  : ...
```

**Do not restart training if the log goes silent after "Successfully parsed N elements."** That silence IS the training run. Check CPU usage to confirm: `ps aux | grep NativeUITrainer` should show high CPU%.

---

## Step 3 — Post-Training Evaluation

After "Done. NativeUIDetector_v1 trained at ..." appears in the log:

### 3a. Update ExperimentLog.md

Record the validation metrics from the training log (Step 4 output) in `Research/ExperimentLog.md` under the current run.

### 3b. Single-image spot check

```bash
swift scripts/test_model_predictions.swift
```

This script runs VNCoreMLRequest on `img_000809.png` (a navigationBar test image) and one alert image. Confirms:
- Model file is found and compiles
- `.scaleFill` is being used (critical — do NOT use `.scaleFit`)
- Alert IoU > 0.9 (sanity check — if this fails, something broke since Run 002)
- NavigationBar: check if any predictions exist at the correct y-location

### 3c. Full evaluation

```bash
swift scripts/eval_map.swift
```

Runtime: ~3 minutes for 1,364 validation images. Reports per-class AP@0.5 and overall mAP.

**Do NOT use `detector.evaluation(on:)`** — it uses `.scaleFit` internally and returns mAP≈0 for portrait images regardless of model quality. This is a known Create ML bug with no API workaround. See `Research/Phase6LessonsLearned.md` §3 for the full explanation.

### 3d. Interpret results — decision tree

```
mAP ≥ 0.70 AND all 5 class APs ≥ 0.50
  → DS-G6 gate passes → proceed to TASK-6-5 formal evaluation → TASK-6-6 device benchmark

mAP in [0.50, 0.70) OR any class AP < 0.50
  → Investigate which classes are failing (see Diagnostics section)
  → Check class imbalance (see §4.1 below)
  → Likely need one more training run with adjusted config

navigationBar or textField AP = 0.00 (same as Run 002)
  → Strip tiling did not help → escalate to YOLO11 investigation
  → Document in ExperimentLog.md and file a new task

mAP < 0.30 with alert AP also degraded
  → Regression — strip tiling broke something
  → Check CreateMLExporter strip coordinate math
  → Verify strip images look correct in NativeUITrainer/strip_smoke_test/
```

---

## Step 4 — Diagnostics When Things Are Wrong

### 4.1 "Zero predictions" for a class

The model produces 0 detections for a class at any confidence threshold.

**Diagnostic steps:**
```bash
swift scripts/inspect_model_outputs.swift   # shows raw YOLO candidates with threshold=0.0
```

- If raw candidates exist but max confidence < 0.01: anchor-assignment failure (see BP-26)
  - Fix: ensure strip tiling is active (check `stripFraction` in training log output)
  - Fix: increase strip fraction to 0.30 if 0.22 wasn't enough
- If NO candidates even with threshold=0.0: model file is corrupt or image preprocessing is wrong
  - Check: is `.scaleFill` being used?
  - Check: did `MLObjectDetector.write(to:)` succeed? (`NativeUIDetector_v1.mlpackage.mlmodel` should exist)

### 4.2 mAP dramatically lower than Run 002 (0.336)

Regression — something broke. Check in this order:
1. Annotation coordinates: are they normalized? (`head -1 annotations.json`)
2. Strip coordinate math: do strips for alert/toggle still have correct coordinates?
   - Run `swift scripts/verify_strip_export.swift` — all aspect ratios should be ≤ 4:1
3. Class counts: are the same training classes present with roughly the same instance counts?
   - Check the "── Step 1" section of `NativeUITrainer/training.log`

### 4.3 Very low alert/toggle AP when those were previously 0.91/0.60

Something changed in how those classes are annotated in the exported strips.

The strip filter uses: `elem.cy >= yTopNorm && elem.cy <= yBotNorm` (center must fall within strip). For alert (which appears in the center of the screen), the center should fall into at least 1–2 strips. For toggle (small items throughout the settings list), centers should appear in multiple strips.

Check: does the strip smoke test show any alert/toggle strips?

### 4.4 "Fatal error: Expecting one JSON file with object annotations, found N"

Multiple `.json` files exist in the export images directory. The `directoryWithImages(at:annotationFile:)` call uses an explicit annotation file path — this error should NOT occur with our pipeline. If it does:
- Check that no stale per-image JSON files from an old pipeline version exist in the export directory
- The export directory is cleaned before each run via `try? FileManager.default.removeItem(at: exportRoot)` — confirm that line is in `CreateMLExporter.swift`

---

## Step 5 — After DS-G6 Gate Passes (mAP ≥ 0.70)

1. Run `scripts/eval_map.swift` one final time on the withheld test set (not validation)
2. Run `TASK-6-5` formal evaluation: confusion matrix, content-agnostic blurred text test
3. Run `TASK-6-6` device benchmark: `XCTest` performance test on physical iPhone
4. Update `Tasks.md`: mark TASK-6-5 and TASK-6-6 as `[x]` complete
5. Update `ModelRegistry.swift`: set `trainingDatasetVersion` from `manifest.json`
6. Update `Research/ExperimentLog.md`: record final metrics and gate status

---

## Reference: File Locations

| File | Purpose |
|---|---|
| `NativeUITrainer/training.log` | Active training log (tail to monitor) |
| `NativeUITrainer/Sources/TrainingConfig.swift` | Training hyperparameters |
| `NativeUITrainer/Sources/CreateMLExporter.swift` | Export logic + strip tiling |
| `NativeUITrainer/Sources/main.swift` | CLI entry point |
| `NativeUIAuditKitModels/Sources/NativeUIAuditKitModels/NativeUIDetector_v1.mlpackage.mlmodel` | Trained model output |
| `NativeUIAuditKitModels/Sources/NativeUIAuditKitModels/training_config.json` | Config written alongside model |
| `scripts/eval_map.swift` | Full mAP evaluation (use this, not `evaluation(on:)`) |
| `scripts/test_model_predictions.swift` | Single-image spot check |
| `scripts/inspect_model_outputs.swift` | Raw YOLO tensor inspection |
| `scripts/verify_strip_export.swift` | Strip dimension and coordinate validation |
| `Research/ExperimentLog.md` | All training runs — read before starting a new one |
| `Research/Phase6LessonsLearned.md` | Detailed technical findings from Phase 6 |
| `Research/BestPractices.md` | All known pitfalls (BP-25: scaleFit bug, BP-26: anchor assignment) |

---

## Quick Command Reference

```bash
# Monitor active training
tail -f NativeUITrainer/training.log
ps aux | grep NativeUITrainer | grep -v grep

# Post-training evaluation
swift scripts/test_model_predictions.swift
swift scripts/eval_map.swift

# Strip validation (run before training to verify strip export is correct)
swift scripts/verify_strip_export.swift

# Raw model output inspection (when getting 0 predictions)
swift scripts/inspect_model_outputs.swift

# Check training log for class instance counts
grep "instances" NativeUITrainer/training.log
```
