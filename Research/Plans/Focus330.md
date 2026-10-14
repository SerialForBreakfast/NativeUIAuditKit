# FOCUS330 — control-centered regions

Maximum-mini-NUIAK owns this approved experiment. Use retained images and resident models only.

## Measurement

Run the existing tvOS detector on unique native training frames. Use confidence 0.25 and no OCR.
Pin the executable, loaded model, settings, images, and coordinate convention.
Compare detector boxes with every measured control. Do not use focused identity to select controls.
Measure control recall, boundary coverage, and artwork inside selected windows.
Compare the existing 2 windows with 2 control-centered windows at the same pixel budget.
Rank proposed controls by image change, not labels. Keep missing detections explicit.
Known boxes serve as diagnostic references only. They cannot enter candidate inputs.

## Conditional training

If training evidence supports the new regions, register 1 matched 30-epoch candidate.
Keep original whole-frame views, labels, weights, schedule, thresholds, and evaluation roles.
Use original-resolution crops through the existing cropper. Use image-only fallback when source proposals are unavailable.
Initialize from FOCUS325-average. Train detail filters and correction weights only.
Use seed 42, batch 16, learning rate 0.0001, and auxiliary weight 0.25.
Use 2 CPU threads, at most 8 GiB memory, and at most 2 GiB new output.
Use fixed-last selection. The standing approval removes the wall-time limit.

## Acceptance

Test all previous-success sets. Report correct decisions, false changes, missed changes, abstentions, gains, and losses.
Require useful native gains without lost previous successes or increased missed changes.
If detector coverage does not support the change, preserve the diagnosis and do not start unsupported training.
Test coordinates, clipping, missing detections, altered hashes, and forbidden label use.
Run focused tests and the integrated offline Swift checks after code changes.
Keep current TTR models unchanged unless a separate qualified promotion passes its requirements.
