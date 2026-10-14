# FOCUS331 — image-only boundary regions

Maximum-mini-NUIAK owns this approved experiment. Use retained training images and existing tools.

## Fixed comparison

Compare 2 image-only rules with the current absolute-change windows.
Smooth each frame with a 5 × 5 mean filter. Measure changes in per-frame gradient magnitudes.
Rank legal 32 × 32 windows by this signal. Select at most 2 nonoverlapping windows.
The first rule selects both windows this way. The second preserves the existing first window and selects only its replacement second window.
Do not use detector boxes, measured geometry, focus identities, or labels to select windows.
Use measured boundaries only for training diagnostics. Retain original-resolution extraction through the existing cropper.

Measure coverage and included artwork on all training rows, each family, and content-change rows.
A supported rule improves mean boundary coverage by at least 0.02 on all nonzero training rows and content rows.
It must not reduce mean boundary purity by more than 0.02 on either subset.
If both pass, choose the rule with the higher mean content boundary coverage. These are experiment criteria, not deployment thresholds.
Do not change these criteria after reading the results.

## Conditional candidate

If a rule passes, register 1 matched 30-epoch candidate before execution.
Keep the FOCUS327 initializer, original images, membership, labels, schedule, weights, and thresholds.
Train existing detail filters and correction weights. Freeze whole-frame and geometry weights.
Use seed 42, batch 16, learning rate 0.0001, auxiliary weight 0.25, and fixed-last selection.
Keep 2 CPU threads, an 8 GiB memory limit, and a 2 GiB output limit. The standing approval removes the wall-time limit.
Use the same region rule during training and evaluation. Keep raw image channels and existing output sizes.
No capture, downloads, TTR edits, or new data admission is needed.

## Completion

Run focused selector, coordinate, parity, role, and checkpoint tests.
Run the integrated offline Swift build and serial tests once.
If training starts, compare every previous-success set. Report false changes, missed changes, abstentions, gains, and losses.
If neither rule passes, preserve the failed measurements and do not start unsupported training.
Update Tasks, results, and coordinator chat. Keep current TTR models unchanged unless all promotion requirements pass.
