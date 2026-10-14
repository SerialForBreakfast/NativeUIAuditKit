# FOCUS312 — effect coverage and original-view retention

Maximum-mini-NUIAK measures existing images before testing 1 fixed candidate.
The audit, 30-epoch candidate, full regression check, and diagnostics complete.
The candidate improves some native decisions but fails acceptance. Do not promote it.

## What the audit establishes

The audit checks 511 unique training image pairs and all 16 tiny development comparisons.
Unique image pairs do not establish independent source groups.
It verifies the exact FOCUS311 derivatives against their retained hashes.
It uses observed labels already approved for each data role. Image differences do not create labels.

These measurements use the model's 192 × 128 encoded images.
Changed area means mean absolute RGB difference above 1/255.
The numbers include all image changes, not only focus shading or growth.

| Changed pairs | Count | Changed pixels, minimum / median / maximum | Peak RGB difference, median |
| --- | ---: | --- | ---: |
| Tiny native forward checks | 4 | 269 / 274.5 / 280 | 0.563 |
| Training derivatives near 3 pixels | 84 | 33 / 71 / 252 | 0.629 |
| Training derivatives near 6 pixels | 100 | 108 / 232.5 / 984 | 0.432 |

Matching the control size does not match its complete effect footprint.
The tiny native footprint overlaps the 6-pixel derivatives more than the 3-pixel derivatives on these area measurements.
This is a limited comparison, not proof that a different scale alone will repair the model.

The current detail selector chooses one 32 × 32 window from image differences.
That window contains 49.5%–50.4% of the tiny native difference energy.
It contains 90.8%–100% of the 3-pixel changed training derivatives.
Shrinking the complete scene brings separate changed regions into one window.
The tiny native cases keep those regions far apart.

A second image-selected window covers essentially 100% of the difference energy in all 4 tiny native pairs.
Both frame orders use the same image-only rule. Identical pairs produce no proposed window.
This checks pixel coverage only. It does not change model decisions or establish focus accuracy.
Body bounds support coverage measurements only. They do not select windows.

## Registered training comparison

The candidate starts from DTM085 with FOCUS310's original-detail architecture.
Every epoch includes all 1,820 original views and original detail views.
Their hashes, labels, row weights, and source groups remain unchanged.
Each optimizer step adds the exact FOCUS311 scaled views through an auxiliary objective.

`loss = original weighted BCE + 0.25 × scaled weighted BCE`

The original objective keeps coefficient 1. Its total row weight remains 1,660.
The auxiliary objective adds 415 uniformly across the same rows.
Group and condition proportions remain unchanged. Total loss weight increases by 25%; this is explicit, not hidden normalization.
The auxiliary view approximately doubles forward/backward work. It adds no optimizer steps or independent examples.

- Initialization: DTM085.
- Control: completed FOCUS310 original-detail run.
- Epochs: 30, fixed last checkpoint.
- Batch: 16.
- Learning rate: 0.0001.
- Seed: 42.
- Updates: 114 per epoch, 3,420 total.
- Thresholds: 0.15 and 0.85.
- Limits: 2 CPU threads, 8 GiB working memory, 128 MiB output.

The existing trainer gains an optional auxiliary input. Its default objective stays unchanged.
A numerical test checks the combined update against a direct Adam calculation.
Tests check invalid auxiliary inputs, original-image preservation, effect measurements, and window coverage.
No reserved image, tiny development image, or related group enters training.
Native and tiny evaluation views match FOCUS310's hashes exactly.

## Model results

Counts show correct decisions unless a row names false changes.

| Cases | DTM085 | FOCUS310 | FOCUS311 | FOCUS312 |
| --- | ---: | ---: | ---: | ---: |
| Native training groups, 548 | 505 | 528 | 495 | 529 |
| Native development, 40 | 33 | 34 | 28 | 29 |
| Reserved native, 52 | 51 | 49 | 52 | 52 |
| Native total, 640 | 589 | 611 | 575 | 610 |
| Forward replay, 668 | 667 | 668 | 665 | 666 |
| Reversed native, 640 | 582 | 608 | 581 | 598 |
| Reversed replay, 668 | 666 | 667 | 661 | 663 |
| Global lighting, 226 | 226 | 226 | 226 | 226 |
| Left disturbances, 226 | 144 | 141 | 137 | 37 |
| Center disturbances, 226 | 80 | 94 | 82 | 62 |
| Left false changes, 226 | 81 | 81 | 87 | 185 |
| Center false changes, 226 | 121 | 108 | 119 | 136 |
| Tiny forward changes, 4 | 0 | 0 | 0 | 0 |
| Tiny reversed changes, 4 | 0 | 0 | 0 | 0 |
| Tiny identical comparisons, 8 | 8 | 8 | 8 | 8 |

Against DTM085, FOCUS312 gains 25 correct native decisions and loses 4.
It loses 107 previous correct left-disturbance decisions and 20 center-disturbance decisions.
It has fewer correct decisions in 13 of 24 strength/order checks.
All tiny changed scores remain below 0.0036. No threshold changes follow these results.
Reserved examples remain excluded from training, but prior inspection prevents an untouched final-evaluation claim.

The fixed 128-pair training diagnostic reuses old scores and checks only the new model.
FOCUS312 gets 12/24 scaled 3-pixel changes correct, versus FOCUS311's 14/24 and FOCUS310's 0/24.
It gets 23/28 scaled 6-pixel changes correct, versus 26/28 and 7/28 respectively.
Retaining original views improves some original-size results but does not solve tiny native transfer.
This experiment changes the original/scaled objective balance. It does not isolate a universal benefit from either loss alone.

An inference-only diagnostic removes the added correction without saving changed weights.
Left false changes fall from 185 to 87, but abstentions rise from 4 to 98.
Correct left decisions rise only from 37 to 41. The adapted whole-frame branch still differs from DTM085.
Center false changes fall from 136 to 87, with 110 correct decisions instead of 62.
Lighting remains 226/226. This diagnostic does not select another model.

## Decision and next test

Reject this candidate. Original-image exposure does not guarantee preservation of previous decisions.
Do not expand the scaled corpus or repeat this fit with more epochs.
Next, test one versus two image-selected windows while keeping the original whole-frame branch frozen.
Use shared detail weights and matched settings. This separates crop coverage from changes to the existing whole-frame classifier.
Check all disturbance conditions and previous successes before any promotion claim.
No TTR renderer repair blocks that retained-data comparison.
For later native generation, vary control size and separation independently. Do not shrink the whole screen to simulate small controls.

## Verification

All 39 focused Python tests pass in 0.822 s.
The offline Swift build passes in 2.75 s.
All 173 Swift tests pass in 53.111 s. XCTest also passes.
The native Swift build option emits its existing deprecation warning.
Sampled memory is 5,109,968 KiB. The sample does not establish peak memory.
Training takes 534.10 s. Checkpoint verification brings the fit stage to 537.09 s.
Preparation through regression evaluation takes 778.75 s. The initial audit and later diagnostics are separate work.
The runner verifies all 3,420 updates and exact checkpoint reload scores.
All registered source and input hashes still match after execution.

Software verification passes. The declared training-input checks pass.
Native integration qualification does not change. Model acceptance fails.

Evidence remains under `reports/work/FOCUS-312/`.
It includes the effect audit, proposal diagnostic, registered settings, and input identities.
No capture, installation, export, public API change, or Git write occurs.
The coordinator stores the result at cursor 143. The approved SMB fallback passes exact readback.
Sillycon-TTR acknowledgment remains pending. Neither publication proves peer acceptance.
