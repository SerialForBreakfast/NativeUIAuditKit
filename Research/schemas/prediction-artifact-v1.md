# Prediction artifact v1

**Status:** Draft interface implemented by P1-A; it proves serializer and
preflight software only. A synthetic artifact has no real inference metrics,
corpus eligibility, integration qualification, or model-gate result.

`prediction-artifact-v1` is a complete, per-image output of the same PyTorch
YOLO prediction settings used by `scripts/eval_phase6a.py`. Boxes are measured
on the original decoded image, not its letterboxed 640-pixel inference canvas.
They use top-left-origin pixel `[x1, y1, x2, y2]` coordinates with `x2 > x1`
and `y2 > y1`. Integer `classID` values are frozen IDs from the referenced
`category_map.json`; scores are finite values in `[0, 1]`.

## Input manifest

The explicit input manifest avoids scanning a dataset directory. It is JSON:

```json
{
  "formatVersion": "prediction-input-manifest-v1",
  "corpusID": "example-toy-corpus-v1",
  "images": [
    {
      "imageID": "fixtures/rectangular.png",
      "imagePath": "images/rectangular.png",
      "labelPath": "labels/rectangular.txt"
    }
  ]
}
```

`imageID` is a unique corpus-relative POSIX identifier, never an absolute host
path. `imagePath` and `labelPath` are resolved relative to the manifest file.
Every member is required: the exporter resolves a symlink target, decodes the
image, validates every YOLO label row against the frozen class count and
normalized `cx cy width height` bounds, and hashes image and label bytes before
any model import/inference. Missing, dangling, duplicate, corrupt, or invalid
members fail readiness; the requested set is never reduced.

## Output document

The exporter writes a new JSON file only after preflight succeeds and refuses
to overwrite an existing output path. Its stable top-level fields are:

| Field | Meaning |
|---|---|
| `formatVersion` | Exactly `prediction-artifact-v1`. |
| `evaluatorVersion` | Versioned exporter identifier. |
| `corpus` | Input corpus ID, input-manifest SHA-256, and content SHA-256 over ordered image/label identities and bytes. |
| `model` | Explicit checkpoint relative path where possible and SHA-256. |
| `categoryMap` | Frozen map version and SHA-256. |
| `settings` / `settingsSHA256` | Effective model, image-size, confidence, NMS, and output-coordinate settings. |
| `completeness` | Requested IDs/count, result IDs/count, missing IDs, duplicate IDs, and whether one record exists for every requested member. |
| `results` | Exactly one record for each requested `imageID`, in manifest order. |

Each result contains `imageID`, decoded `width`/`height`, image and label
SHA-256 values, `status`, and `detections`. `status` is `ok` for one or more
detections, `empty` for a successful prediction with none, or `failed` for a
post-preflight inference failure. A failed record has an error code/message and
no detections. A document can be complete while containing failed records; a
consumer must not use failed results for numerical comparison.

Each detection is:

```json
{
  "classID": 33,
  "score": 0.91,
  "xyxyPixels": [14.0, 8.0, 98.0, 42.0]
}
```

The serializer rejects invalid class IDs, scores, non-finite coordinates,
reversed boxes, and boxes outside the original image instead of clipping or
silently dropping them.

## Inference equivalence

The export mode and normal evaluator use the shared effective settings:

```json
{
  "engine": "ultralytics-yolo",
  "imgsz": 640,
  "confidence": 0.001,
  "iou": 0.7,
  "maxDetections": 300,
  "augment": false,
  "agnosticNMS": false,
  "coordinateSpace": "original-image-top-left-pixel-xyxy"
}
```

The export mode consumes the explicit manifest one decoded image at a time;
it does not reuse `save_txt` labels from a prior run. This prevents stale label
reuse and permits explicit empty results. CoreML, blur, quantization, and
latency paths do not run in this mode.

## Synthetic reviewed example

`P1-A-example-rect-empty` is a deterministic 320×180 non-user rectangle case
with a valid empty label file and no detections. Its expected output is one
`empty` record, matching source dimensions, no missing IDs, and
`complete == true`. The P1-A test constructs it under `.build/debug-output/`;
it is not a corpus, not a prediction metric, and not evidence for Run 009.

## Compatibility policy

Consumers must reject an unknown format version, a changed coordinate space,
missing required hashes, incomplete result set, duplicate image ID, unsupported
class ID, or failed result when a complete numerical comparison is requested.
Additive fields may be ignored only if the required v1 meanings remain
unchanged. A new required semantic requires a new format version and matching
contract tests.

## P2 comparison compatibility

P2-A compares the nested `corpus.contentSHA256`, `categoryMap.sha256`,
`completeness`, per-image pixel/label identities, and `settingsSHA256` fields
from this envelope. It rejects failed records before any numerical comparison.
The per-image artifact does not itself calculate evaluation metrics; a caller may
attach a separate numeric `metrics` object for a controlled comparison. If either
artifact lacks that object, the comparison reports `metricAvailability:
"unavailable"` and no deltas. It must never interpret missing metrics as zero.
