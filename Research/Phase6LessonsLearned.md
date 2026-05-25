# Phase 6 — Training Lessons Learned

This document captures every concrete thing we learned while building and debugging the first 5-class Create ML object-detection model for NativeUIAuditKit. It is written so that whoever trains the next model — even with no memory of this session — can avoid every mistake we made and understand why things behaved the way they did.

---

## 1. Create ML API — What's Real vs. What the Docs Imply

### 1.1 `MLObjectDetector.DataSource` — there is no `annotatedFiles` case

The Create ML documentation and older samples reference a case called `.annotatedFiles`. **It does not exist in the current SDK.** The real cases are:

| Case | Description |
|---|---|
| `.directoryWithImagesAndJsonAnnotation(at:)` | Points to a directory. Create ML scans it for a **single** `.json` file and uses ALL images in the directory. Fails with `Fatal error: Expecting one JSON file with object annotations, found N` if there are multiple JSON files (e.g., one per image). |
| `.directoryWithImages(at:annotationFile:)` | Points to an images directory and an explicit annotation file URL. This is the right case when you control the annotation layout. |

**Use `.directoryWithImages(at:annotationFile:)` for all custom pipelines.** The annotation file must be a single JSON array:
```json
[
  {"imagefilename": "img001.png", "annotation": [{"label": "toggle", "coordinates": {...}}]},
  ...
]
```

### 1.2 Feature extractor for object detection: `objectPrint`, NOT `scenePrint`

`MLImageClassifier` uses `.scenePrint(revision:)`. `MLObjectDetector` uses `.objectPrint(revision:)`. These are different extractors for different tasks. If you specify scenePrint for an object detector the compiler will reject it, but older code samples mix these up.

### 1.3 `MLObjectDetector.ModelParameters` init signature

The correct macOS 11+ init is:
```swift
MLObjectDetector.ModelParameters(
    validation: .dataSource(valSource),
    batchSize: 32,
    maxIterations: 10000,
    gridSize: CGSize(width: 13, height: 13),
    algorithm: .transferLearning(.objectPrint(revision: 1))
)
```

`gridSize` and `algorithm` are separate named parameters. Do not pass `algorithm` via `validation:`.

### 1.4 `MLObjectDetector.ModelParameters.AnnotationType`

```swift
let annotationType = MLObjectDetector.AnnotationType
    .boundingBox(units: .normalized, origin: .topLeft, anchor: .center)
```

Pass this as the `annotationType:` argument to `MLObjectDetector.init(trainingData:parameters:annotationType:)`. Units can be `.pixel` or `.normalized`. **Critically: this parameter only controls how Create ML interprets training annotations. It does NOT affect `evaluation(on:)`, which has its own (undocumented) interpretation — see Section 3.**

### 1.5 `MLObjectDetectorMetrics.meanAveragePrecision` is a tuple

```swift
valMetrics.meanAveragePrecision.IoU50      // mAP at IoU threshold 0.5
valMetrics.meanAveragePrecision.variedIoU  // COCO-style mAP at varied IoU thresholds
```

It is NOT a plain `Double`. Treating it as one crashes at compile time.

### 1.6 `detector.write(to:)` appends `.mlmodel` — you will get `.mlpackage.mlmodel`

If you call:
```swift
let url = outputDir.appending(path: "NativeUIDetector_v1.mlpackage")
try detector.write(to: url)
```

The output is `NativeUIDetector_v1.mlpackage.mlmodel` — a flat `.mlmodel` file, not a proper `.mlpackage` directory. This is valid CoreML and compiles correctly, but it's not the package format. Factor this into resource declarations in `Package.swift`.

---

## 2. Coordinate Systems — The Complete Map

This was the single biggest source of bugs. There are four coordinate systems involved and they are all different.

### 2.1 The four systems

| System | Origin | Y direction | Unit | Used by |
|---|---|---|---|---|
| **Pixel (top-left)** | Top-left | Down | Pixels | PNG, UIKit frames |
| **Points (top-left)** | Top-left | Down | Points (px / scale) | UIKit layout |
| **Vision normalized** | Bottom-left | Up | 0–1 fraction of image size | `VNImageRequestHandler`, `VNRecognizedObjectObservation.boundingBox` |
| **Create ML normalized** | Top-left | Down | 0–1 fraction of image size | annotation JSON passed to `MLObjectDetector` |

### 2.2 The conversion: Vision → Create ML normalized

Our source annotation format stores `boundsVisionNormalized` (Vision bottom-left origin). Convert to Create ML top-left center-anchored:

```swift
let vn = elem.boundsVisionNormalized
// vn.x = left edge from left, [0,1]
// vn.y = bottom edge from BOTTOM of image, [0,1]
// vn.width, vn.height = [0,1] fractions

let cx = vn.x + vn.width  / 2          // horizontal center
let cy = 1.0 - vn.y - vn.height / 2   // flip y-axis: bottom-left → top-left
let w  = vn.width
let h  = vn.height
```

**Do not compute normalized coordinates from pixel values + image dimensions.** That requires reading PNG dimensions for every image and introduces floating-point error. Always use `boundsVisionNormalized` (which is already clamped to `[0,1]`).

### 2.3 The Vision y-axis flip — the most common mistake

Vision says `y = 0.3` means "the box bottom edge is 30% up from the BOTTOM of the image." Create ML says `y = 0.3` means "the box center is 30% down from the TOP." If you forget the flip, all boxes appear reflected vertically and the model learns inverted geometry.

---

## 3. The `evaluation(on:)` Bug — mAP≈0 Despite Correct Predictions

This cost us two full training runs (each ~45 minutes). Document it permanently.

### 3.1 What happened

After training with normalized annotation coordinates, `detector.evaluation(on:)` returned mAP@0.5 ≈ 0.001. We ran a direct inference test and the model predicted the alert bounding box with IoU = 0.992 against ground truth — a near-perfect prediction. Yet mAP was 0.

### 3.2 Root cause: `evaluation(on:)` uses `.scaleFit` internally

`MLObjectDetector.evaluation(on:)` runs `VNCoreMLRequest` internally with `imageCropAndScaleOption = .scaleFit` (letterboxing). Create ML trains objectPrint models by **scale-filling** (stretching) images to 299×299 — the opposite of letterboxing.

For a portrait iPhone screenshot (1179×2556, aspect ratio ≈ 0.46):
- `.scaleFit` letterboxes it: the image occupies only 138px of the 299-wide input (padding 80px each side)
- The model learned to predict a box that is 0.687 wide (= 0.687 of the 299px training space)
- After `.scaleFit` unmapping: 0.687 × (299/138) ≈ **1.49 wide** in original image space
- Ground truth box is 0.687 wide
- IoU(predicted 1.49-wide box, GT 0.687-wide box) ≈ 0.457 — just below the 0.5 threshold

**Every detection registers as a false positive. mAP@0.5 = 0 even though the model is actually good.**

### 3.3 The fix

For any custom evaluation or inference: always use `.scaleFill`:
```swift
let req = VNCoreMLRequest(model: vnModel)
req.imageCropAndScaleOption = .scaleFill   // matches Create ML training preprocessing
```

For SAHI tiles (square 640×640): `.scaleFit` and `.scaleFill` are equivalent (no aspect ratio difference) — but use `.scaleFill` by default for consistency.

**`MLObjectDetector.evaluation(on:)` cannot be fixed** — there is no API to override its crop/scale option. Write your own evaluation loop (see `scripts/eval_map.swift`).

### 3.4 Actual mAP after correct evaluation

| Class | AP@0.5 (correct, scaleFill) | AP@0.5 (broken, MLObjectDetector.evaluation) |
|---|---|---|
| alert | 0.9091 | 0.0000 |
| toggle | 0.6051 | 0.0039 |
| primaryButton | 0.1649 | 0.0018 |
| navigationBar | 0.0000 | 0.0000 |
| textField | 0.0000 | 0.0000 |
| **mAP** | **0.336** | **0.0011** |

The "correct" mAP is still not good enough for the DS-G6 gate (needs ≥0.70), but the direction of the problem is completely different from what the built-in evaluation reported.

---

## 4. Why NavigationBar and TextField Have AP=0 — What We Think Is Wrong and Why

### 4.1 The observed facts

- `navigationBar` has **3,709 training instances** — more than any other class.
- After 10,000 iterations, the model produces **0 navigationBar predictions** at any confidence threshold.
- With `confidenceThreshold=0.0` passed directly to MLModel, we get 14,661 raw YOLO candidates, but the **maximum confidence across all classes on a pure-navigationBar validation image is 0.0024**.
- The candidates ARE clustered at the right vertical location (cy ≈ 0.101 vs. GT cy = 0.104).
- The detected width at that location is ≈ 0.15, not 1.0.
- The class assigned to these weak predictions is "toggle" (class 4), not "navigationBar".

### 4.2 The working hypothesis: YOLO anchor assignment failure

In YOLO, during training, each ground-truth box is matched to an anchor box based on IoU. **Only the anchor with the highest IoU is responsible for predicting that ground-truth box.** If no anchor achieves sufficient IoU, the box is never assigned and the network never receives a learning signal for it.

For `navigationBar` (w≈1.0, h≈0.063, aspect ratio ≈ 16:1):
- Even a generous anchor of (0.5, 0.5) gives center-IoU ≈ 0.11 with a 16:1 box
- YOLO assignment typically requires IoU > ~0.4–0.5
- **If no anchor has IoU > 0.4 with the navigationBar shape, no anchor is ever assigned to it during training, and the network never adjusts its weights to detect it**

For `toggle` (w≈0.05, h≈0.03, aspect ratio ≈ 3.6:1): a small, roughly-square anchor would give high IoU → assignment succeeds → model learns.

For `alert` (w≈0.69, h≈0.25, aspect ratio ≈ 2.7:1): a medium anchor gives high IoU → assignment succeeds → model learns.

### 4.3 Why the user challenged this framing — and they were right to

The framing "YOLO can't regress 16:1 boxes" is imprecise. YOLO CAN in principle regress any width — the regression target is `exp(tw)` where `tw` can be any real number. The regression doesn't fail; the **anchor assignment** fails first. The model never reaches regression for navigationBar because no anchor is ever matched to it, so the loss gradient for that class is never propagated.

This matters because the fix is specific:
- **Wrong fix**: "make regression easier by reducing the aspect ratio to regress"
- **Right fix**: "ensure at least one anchor has sufficient IoU overlap with the navigationBar box shape"

The only way to do that with objectPrint (whose anchors are fixed and not publicly documented) is to **transform the training images so that navigationBar no longer has a 16:1 aspect ratio in the model's 299×299 input space**. See Section 6 for the fix.

### 4.4 Alternative hypotheses not yet ruled out

- **Feature extractor saturation**: objectPrint's ResNet-based backbone may have been pre-trained on object recognition tasks where full-width, thin strips don't appear, so it produces near-zero activations for that spatial configuration.
- **Class confusion**: the model may be predicting "toggle" or another class at the navigationBar location (we observed toggle=class 4 getting the highest confidence at the navigationBar's y-position). This suggests the anchor closest to navBar's shape is the one also used for toggle, creating competition.
- **Data quality**: the navigationBar annotations may have some coordinate issue we haven't found yet. Worth spot-checking 10 annotations manually.

---

## 5. Training Process — What to Check Before a Full Run

45 minutes of GPU time is expensive. Validate everything before starting.

### 5.1 Pre-flight checklist (run in this order)

1. **Verify annotation coordinates are normalized [0,1]** — not pixels. Sample 5 annotation JSON entries manually and confirm cx, cy, w, h are all < 1.0.

2. **Verify Vision → Create ML coordinate conversion** — for at least one image with a known GT position, confirm `cy = 1.0 - vn.y - vn.h/2` produces a value near the top of the image for navigationBar.

3. **Verify image-annotation pairing** — each image in the export `images/` directory must have a matching `imagefilename` in `annotations.json`. Spot-check 5 pairs.

4. **Verify the annotation JSON is a single file** — `ls *.json` inside the export directory should return exactly `annotations.json`. Any other JSON files (e.g., per-image JSON from a previous pipeline) will cause `Fatal error: Expecting one JSON file`.

5. **Run a 1-iteration training test** — modify TrainingConfig to `maxIterations: 1` and run. Confirms the pipeline compiles, the data source is valid, and the output writes without errors. A 1-iteration training that crashes tells you the same thing as a 10,000-iteration training — in < 5 seconds.

6. **After training, immediately run `scripts/eval_map.swift`** (not `evaluation(on:)`). The built-in evaluation has a known `.scaleFit` bug that will always report mAP ≈ 0 for portrait images.

### 5.2 The nohup pattern for long training runs

Create ML training runs via `swift run` are killed when the terminal session ends. Use:
```bash
nohup swift run NativeUITrainer \
  --dataset <dataset-path> \
  --output  <output-path> \
  >> NativeUITrainer/training.log 2>&1 &
echo "PID: $!"
```

**The log file is inside the project directory** (`NativeUITrainer/training.log`). Do not write to `/tmp` — it's outside the project and gets lost between sessions.

Check progress:
```bash
tail -30 NativeUITrainer/training.log
```

Check if still running:
```bash
ps aux | grep NativeUITrainer
```

### 5.3 Training progress output

Create ML does NOT print iteration-by-iteration progress when running from a CLI (only in the Create ML app GUI). The output jumps from "Successfully parsed N elements" directly to the validation metrics step after training completes. Silence between those two lines is NORMAL — the training is running, not hung.

---

## 6. The Fix for NavigationBar/TextField: Square-Crop Training

### 6.1 Why square crops work

Instead of training on the full 1179×2556 portrait screenshot, split each image into overlapping square tiles:
- **Tile 0 (top)**: rows 0–1178 → 1179×1179 square
- **Tile 1 (middle)**: rows 688–1867 → 1179×1179 (50% overlap)
- **Tile 2 (bottom)**: rows 1377–2555 → 1179×1179

For navigationBar (full image width, top of screen) in Tile 0:
- Width in tile: 1179/1179 = 1.0 (still full width of the TILE)
- Height in tile: (0.063 × 2556) / 1179 ≈ 0.137

Aspect ratio: 1.0 / 0.137 = **7.3:1** instead of **16:1**. For a "good" anchor around (0.5, 0.1):
- Center-IoU with (1.0, 0.137): intersection = 0.5×0.1=0.05, union = 1.0×0.137 + 0.5×0.1 - 0.05 = 0.187, IoU = **0.27** — closer but still below typical threshold.

For a targeted "wide, thin" anchor like (0.8, 0.12): IoU with (1.0, 0.137) ≈ 0.58. **Assignment succeeds.**

The key insight: by making the image square-crop, the navigationBar height becomes ~13.7% of the tile height rather than 6.3% of the full image height. This doubles the anchor-matching IoU and brings it into the range where assignment occurs.

### 6.2 Implementation in CreateMLExporter

Add a `tilesToSquare: Bool` option. When true:
1. For each source image, generate 3 square tiles (top/middle/bottom)
2. For each tile, filter annotations to those whose center falls within the tile
3. Translate + normalize annotation coordinates to tile space
4. Export each tile as a separate PNG (or via CGContext composition without writing to disk)

At inference time, SAHI already generates square 640×640 tiles from a 2× scaled image — this is structurally the same crop operation. When the model is trained on square crops, inference on SAHI's square tiles is a clean match.

### 6.3 Expected post-fix metrics

Based on the anchor IoU analysis:
- navigationBar (7.3:1 in square tile): likely learnable, expect AP > 0.70
- textField (5.4:1): likely learnable, expect AP > 0.50
- primaryButton (6.2:1): likely learnable, may exceed current 0.16
- alert, toggle: unaffected (roughly square objects, already work well)

Target mAP post-fix: > 0.70 (DS-G6 gate).

---

## 7. What the Current Model Can and Cannot Do

**As of the 10,000-iteration run on 2026-05-24:**

### Works well
- **`alert`**: AP@0.5 = 0.91. Centered, bounded box with a clear aspect ratio (2.7:1). 39 of 40 GT instances correctly detected.
- **`toggle`**: AP@0.5 = 0.60. Small, roughly square (3.6:1). 596/845 GT instances detected.

### Partially works
- **`primaryButton`**: AP@0.5 = 0.16. 139 total predictions, 96 TPs against 731 GT instances. The model IS detecting some buttons but recall is only 13%. Possible causes: slight aspect ratio challenge (6:1), multiple buttons per screen with some missed, visual similarity to textField confusing classification.

### Does not work
- **`navigationBar`**: AP@0.5 = 0.00. Zero predictions at any confidence. **Not a data quantity problem (3,709 training instances)** — an anchor shape mismatch problem.
- **`textField`**: AP@0.5 = 0.00. Zero predictions. Same root cause.

---

## 8. Dataset Quality Lessons

### 8.1 Class imbalance ceiling matters more than minimum

We had navigationBar=3,709 vs alert=320 (11.6:1 ratio). Alert got AP=0.91; navigationBar got AP=0.00. The training plan specified a 5:1 maximum imbalance ratio. We violated it. **Cap dominant classes to 5× the smallest class count before training.** The `subsamplingCapPerClass` in TrainingConfig exists for this — it was set to 2,000, which should have capped navigationBar, but alert's training count was 320 (which is below the 5× threshold of 1,600 max given 320 minimum). Need to also impose a LOWER bound: if any class has < 400 training instances, do not train until that class reaches 400.

### 8.2 `datasetVersion` reporting "unknown"

The `manifest.json` in the dataset root didn't have a `datasetVersion` key at the path the trainer expected. The training_config.json records `"datasetVersion": "unknown"`. Fix: ensure manifest.json is written with the exact key name `datasetVersion` (camelCase) before any training run.

### 8.3 Simulator state bias (not yet tested)

We generated all training data in a relatively small number of sessions. The time shown in the status bar is constant within each session. This is a known bias source (see BP-25 in the training plan). For the first retrain, add at least 4 different generation runs on different calendar days and use `xcrun simctl status_bar override` to sweep the clock.

---

## 9. The Evaluation Workflow — What Actually Works

### 9.1 `MLObjectDetector.evaluation(on:)` — do not use for portrait images

It's broken for non-square images due to the `.scaleFit` issue. Use `scripts/eval_map.swift` instead.

### 9.2 `scripts/eval_map.swift` — the real evaluation pipeline

- Loads all 1,364 validation images
- Runs `VNCoreMLRequest` with `.scaleFill`
- Converts Vision bottom-left coords to Create ML top-left for IoU matching against annotation JSON
- Computes per-class AP using 11-point interpolation
- Reports DS-G5 (mAP≥0.50 all classes) and DS-G6 (mAP≥0.70) gate status
- Runtime: ~3 minutes for 1,364 images on M2 MacBook Air

### 9.3 Minimum diagnostic after any training run

1. Run `eval_map.swift` — get per-class AP numbers
2. Run `test_model_predictions.swift` on a known image (img_000409 = alert image) — verify IoU > 0.9 for alert
3. Run `test_model_predictions.swift` on img_000809 (navigationBar image) — check if any predictions exist
4. Run `inspect_model_outputs.swift` with `confidenceThreshold=0.0` to see raw YOLO candidates when step 3 shows 0 detections

---

## 10. Process Lessons — How to Run This Project Better

### 10.1 Validate the API before a 10K-iteration training run

We ran a 10,000-iteration training run with pixel coordinates in the annotation JSON (should have been normalized), then ran another full run after fixing the coordinates, only to find out the built-in evaluation was broken. **Total wasted training time: ~90 minutes.** 

Next time: run a **50-iteration smoke test first**. Check that predictions are in the right ballpark before committing to a full run. Add a `--maxIterations 50` flag path to NativeUITrainer for this purpose.

### 10.2 Keep all output files inside the project directory

Log files, test scripts, scratch Swift files — all go inside the project directory. `/tmp` files are invisible to git, invisible to other team members, and get lost between sessions. Recommended locations:
- Training logs: `NativeUITrainer/training.log`  
- Diagnostic scripts: `scripts/`
- Reports: `reports/`

### 10.3 Document coordinate system decisions at the data layer, not just at the model layer

The confusion between Vision coords and Create ML coords cost two full training runs. A simple diagram at the top of `CreateMLExporter.swift` stating "input: Vision bottom-left normalized, output: Create ML top-left normalized" would have caught the bug in code review instead of at inference time.

### 10.4 Verify one prediction manually before running evaluation

After every training run, before running full evaluation:
1. Pick one validation image with a clear, centered element (the alert images work well)
2. Run `test_model_predictions.swift` on it
3. Confirm IoU > 0.5 for the expected class
4. If IoU is wrong, fix the inference code before running 1,364-image evaluation

This 30-second check caught the `.scaleFit` bug immediately after the second training run.

### 10.5 The "YOLO outputs 0 predictions" diagnostic path

If `VNCoreMLRequest` returns 0 detections:
1. Check if model file exists and compiles
2. Lower `confidenceThreshold` in `VNCoreMLRequest` to 0.01 — do results appear?
3. Pass `confidenceThreshold: 0.0` directly to MLModel (bypassing VNCoreMLRequest's threshold) — do raw YOLO candidates appear?
4. If raw candidates exist but confidence < 0.01: the model learned the wrong location/class, or the anchor-assignment failed during training
5. If NO candidates even with threshold=0.0: the model file is corrupt or the input image preprocessing is wrong

---

## 11. Architecture Decisions That Held Up

- **Single consolidated `annotations.json` per split** (not per-image JSON): correct and required by Create ML
- **`boundsVisionNormalized` as the source of truth** for annotation coordinates: correct — it's pre-clamped and doesn't require reading PNG dimensions
- **`scaleFill` for all non-square inference**: correct
- **Custom eval loop instead of `evaluation(on:)`**: necessary and correct
- **SAHI for inference**: still the right approach; square training tiles will complement SAHI's square crop geometry

---

## 12. What to Do Differently in the Next Training Run

1. **Pre-flight**: run 50-iteration smoke test → confirm non-zero predictions on a known image
2. **Square crop tiling**: implement in `CreateMLExporter` before generating the export
3. **Class balance**: enforce 5:1 max ratio AND 400-instance minimum per class before training
4. **Evaluation**: run `scripts/eval_map.swift` immediately after training — not `evaluation(on:)`
5. **Log location**: `NativeUITrainer/training.log` (in-project)
6. **Simulator state sweep**: run at least 4 separate generation sessions with different clock overrides
7. **Spot-check**: manually verify 5 annotations per class in the training set before committing to a 10K-iteration run
8. **Validate manifest**: ensure `manifest.json` has `datasetVersion` key before training so the training_config.json records the real version
