# INFERENCE412 — T43 detector-inference template

Owner: research-host-NUIAK. Date: 2026-10-15.

## Purpose

tvOS detector questions stalled because the stored real-screen scorecard (REAL-MODEL-SCORECARD-36) holds only predictions at confidence 0.50 and 640 px.
T43 runs pinned detector weights on the pinned reviewed frames. Then it compares the result with the pinned baseline scorecard through T42 matching.
One job answers one arm. `backlog_pipeline.py review` reads its `benchmark_summary.json`.

## Contract

- Template: T43, adapter `scripts/detector_inference412.py`.
- Inputs: `labels` (the scorecard frame list), `baseline` (a scorecard on the same labels), and `model`.
- Parameters: `engine`, `confidence` (0.01–0.95), `imageSize`, and `slice` (class, position, or screen).
- `engine: production` runs the package CLI (`nativeui-audit scan --min-confidence`) with its bundled Core ML model. The image size is fixed. The bundled model tree hash must equal the baseline detector hash.
- `engine: pytorch` runs the source weights through ultralytics at 640, 960, or 1280 px, with NMS IoU 0.45.
- Outputs: `scorecard.json` with raw per-frame predictions (T42-readable), and `benchmark_summary.json`.
- Seven reviewed frames were moved to `/Volumes/training-drive/data/NUIAK/live` by STORAGE-LIVE-01. The adapter finds them there by hash.
  The CLI refuses inputs outside its root. The adapter copies these frames into `.build/debug-output/inference412/`, verifies the copy, and removes it after the scan.

## Qualification

- On 3 frames, including 1 archived frame, the production arm at 0.50 reproduces the stored scorecard exactly. A changed weights file fails before output.
- On all 46 frames, the production control `b405-023-c050` reproduces the stored scorecard exactly: 273 detected, 811 unmatched, 0 gains, 0 losses.
- The PyTorch engine does not reproduce production at 640 px: it detects 247 controls instead of 273. FP16 Core ML export and NMS differences are possible causes; this check did not isolate the cause.
  Use the PyTorch engine only for comparisons between PyTorch arms. Do not compare it directly with production results.

## Limits

Diagnostic limits are 800 s and 100 MB per job. A 46-frame job takes 4–8 s. Frames are development-only reviewed frames. No model is accepted.
