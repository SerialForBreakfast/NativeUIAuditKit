# FDR-015: better ranking, not a deployable focus model

One approved experiment completed30/30epochs. No eligible checkpoint; no export,
promotion, threshold change or automatic rerun. Official ImageNet weight download
is10,306,551bytes; SHA256 is recorded in the reset's weight receipt.

## Identical-input comparison

Both runs use363training pairs,9retention pairs,453real selection crops,64excluded
real labels, unchanged sampling and selection rules. `input-comparison.json`
checks exact objects, not just counts. Neither run is an independent test.

| Fixed snapshot | Focus ranked first /13 | Crop AUROC | Winner at0.85: correct/wrong/none | Retention /18 |
|---|---:|---:|---:|---:|
| FDR014 initial warm model | 8 | .654 | 2/1/10 | 18 |
| FDR014 epoch1 | 11 | .685 | 2/2/9 | 18 |
| FDR014 epoch30 | 5 | .601 | 2/1/10 | 18 |
| FDR015 initial random head | 5 | .473 | 0/0/13 | 9 |
| FDR015 epoch1 | 7 | .538 | 0/0/13 | 9 |
| FDR015 epoch30 | 11 | .726 | 0/0/13 | 9 |

These are predefined diagnostic snapshots, not selected checkpoints. FDR015's
final11/13 exceeds FDR014's final5/13 and the largest-box baseline8/13, but only
matches the earlier run's epoch1 ranking. Random choice expects1.398/13. The
13frames include eight Settings-related, three App Store tabs and two Home frames;
27other frame policies remain unavailable for complete-selection measurement.
Runtime-style outcomes use reviewed boxes, not detector proposals/CoreML inference.

At0.85 FDR015 finds0/35real positives and produces1/418false positives (artwork,
outside the13complete frames). Every epoch retains9/18, not the required18/18.
No epoch passes all guards. Lower training loss is not qualification.

## What improved and what remains broken

Final ranking is correct on all eight Settings-related and all three tab frames.
It fails both Home artwork frames:

- `batch02:recorded-12:new-15` (Computers): ranked2, margin−0.02241 versus
  `new-11` (Photos). `diagnostics/005.png` shows the reviewed target and competitor.
- `batch02:recorded-249:new-8` (HotPotatoTV): ranked8, margin−0.13668 versus
  `new-14`. `diagnostics/006.png` shows similarly bright white artwork in both crops.

Visual observations, not new labels: full frames retain relative enlargement,
shadows and title context; resizing individual boxes reduces relative-size cues.
This is evidence to test target/context representation and matched artwork
contrasts, not proof of a crop bug or cause. Original geometry/labels remain intact.

Final positive scores range0.2083–0.8302; negative scores0.1312–0.8537. This shows
score overlap and fixed-cutoff failure, not a demonstrated calibration remedy.
Monotonic calibration cannot repair the two incorrect within-frame rankings.
Do not simply lower0.85 or label the11/13 result production accuracy.

## Execution and reproducibility

`protocol-ready.json` is authoritative (contentSHA256
`353205a204ce39c4b3c6519dea11fdd9544cccf1822d9a1e015551cc17e4432e`).
Earlier `protocol.json` is an unused pre-execution assembly retaining stale
initialization wording; preserved, never used for training. Assembly initially
rejected the venv interpreter symlink; repaired metadata handling, without any
dataset/output containment exception. No model had started during those repairs.

Frozen MobileNetV3-Small features,576dimensions;577parameter linear head,
30epochs,batch64,AdamW0.0003,seed42; unchanged appearance-balanced draws. Whole
256production crop and ImageNet RGB normalization; no default224center crop.
Actual process75348:23:10:26–23:12:00UTC,94.55s overall including preflight;
trainer feature extraction+training+evaluation5.49s. PyTorch2.13.0,
torchvision0.28.0,MPS. Exit2 means no eligible checkpoint, not a crash/timeout.
No speedup claim: feature caching, frozen backbone, architecture and runtime differ.

`pretrained-features.json` and `artifact-verification.json` verify unchanged
encoder/BN, ordered726train/471validation vectors, exact hashes and a head-only
`last.pt`. There is no `best.pt`; last is diagnostic, not a substitute selection.
All14,601stored scores reproduce the existing selector.488real image/crop files
verified. `diagnostics/report.json` pins inputs and records every epoch/frame.
Reproduction: run the cached-only `scripts/focus_reset_diagnostics.py` with this
protocol/result and a fresh output directory; `compare.py` compares frozen reports
and refuses to overwrite `comparison.json`. No further inference is needed.

## Next decision

Keep pretrained features as the promising research direction, not a release
candidate. Next assignment: audit existing native100/canvas-v2 matched artwork
contrasts and their geometry/context against these two failures; use existing
assets before asking for more human annotation. Freeze a grouped development and
calibration split from eligible training sources, separate from the reused real
selection set. Propose one targeted ranking/target-context experiment with fixed
retention and real guards. Calibrating confidence is a separate measured step,
not a way to erase ranking errors. Additional training requires a new assignment.
Do not scale unchanged synthetic recipes or repeat the old full-backbone run.
