# FOCUS311 — smaller training controls

Maximum-mini-NUIAK completes 1 fixed 30-epoch candidate and all retained regression checks.
The candidate does not repair tiny native changes. Do not promote it.

## Method

The candidate uses FOCUS310's original-detail architecture and DTM085 initialization.
It preserves all 1,820 schedule entries, labels, weights, and connected groups.
It uses batch 16, seed 42, learning rate 0.0001, and thresholds 0.15/0.85.
The completed FOCUS310 candidate supplies the matched control. No control training repeats.

Image hashes assign each native training pair to 1 scale without reading its label.
Both frames receive the same resize and centered placement on black pixels.
Training geometry sets the scale. Inference still selects detail from image differences, not labels.
Original-resolution detail remains available for the transformed native images.

| Training entries | Count |
| --- | ---: |
| Native controls near 3 encoded pixels | 270 |
| Native controls near 6 encoded pixels | 274 |
| Native controls near 12 encoded pixels | 282 |
| Native controls at original size | 326 |
| Unchanged older encoded entries | 668 |

Measured minimum sizes now reach 2.997 pixels. The tiny native checks measure 2.93 pixels.
These images are authored derivatives, not new native captures.
Shrinking a whole scene also changes its background and spacing. This experiment does not isolate control size perfectly.
Repeated and reversed pairs do not add independent evidence.

The runner rejects protected groups, changed images that become identical, and exact matches with protected frames.
Native and tiny evaluation views match FOCUS310's hashes exactly.
No evaluation image enters training. No data role changes.

## Results

Counts show correct decisions unless a row explicitly names false changes.

| Cases | DTM085 | FOCUS310 | FOCUS311 |
| --- | ---: | ---: | ---: |
| Native training groups, 548 | 505 | 528 | 495 |
| Native development, 40 | 33 | 34 | 28 |
| Reserved native, 52 | 51 | 49 | 52 |
| Native total, 640 | 589 | 611 | 575 |
| Forward replay, 668 | 667 | 668 | 665 |
| Reversed native, 640 | 582 | 608 | 581 |
| Reversed replay, 668 | 666 | 667 | 661 |
| Global lighting, 226 | 226 | 226 | 226 |
| Left disturbances, 226 | 144 | 141 | 137 |
| Center disturbances, 226 | 80 | 94 | 82 |
| Center false changes, 226 | 121 | 108 | 119 |
| Tiny forward changes, 4 | 0 | 0 | 0 |
| Tiny reversed changes, 4 | 0 | 0 | 0 |
| Tiny identical comparisons, 8 | 8 | 8 | 8 |

Compared with DTM085, the candidate gains 8 correct native decisions and loses 22.
It has fewer correct decisions in 8 of 24 strength/order checks.
All tiny changed scores remain below 0.012, far below the fixed 0.85 threshold.
Previously inspected reserved cases are regression checks, not untouched final evaluation.

## Training diagnostic

The diagnostic selects 32 unique image pairs per assigned scale, ordered by hashes.
It checks 128 training pairs with both models, using original and scaled views.
All reconstructed scaled tensors and detail views match the training hashes.

| Changed training examples | FOCUS310 scaled view | FOCUS311 scaled view |
| --- | ---: | ---: |
| Near 3 pixels, 24 | 0 | 14 |
| Near 6 pixels, 28 | 7 | 26 |
| Near 12 pixels, 24 | 15 | 18 |

The candidate learns some small synthetic changes. It still cannot transfer that improvement to the 4 tiny native changes.
The 3-pixel training sample also retains 10 abstentions. Training fit itself remains incomplete.
This sample does not establish an independent accuracy estimate.

The test replaces most original native views with scaled views. It does not preserve original-view exposure.
Thus, unchanged label weights do not guarantee unchanged exposure to original images.
Next, preserve original-view exposure and compare measured native effect strength with the scaled derivatives before another fit.
Check effect contrast, changed area, and crop coverage on training groups first.
Use local native generation only for missing training cases. Keep tiny development images and their related groups excluded.
Do not respond with more epochs, another threshold, or a larger synthetic batch without that diagnosis.

## Verification and limits

- All 34 focused Python tests pass.
- The offline Swift build passes in 2.67 s.
- All 173 Swift tests pass in 53.137 s. XCTest also passes.
- Checkpoint reload produces identical scores.
- All registered code and input hashes still match after execution.
- Training takes 260.80 s. Preparation, training, and evaluation take 457.60 s.
- Completion records 3,189,702 output bytes before the later diagnostic and handoff files.
- Sampled memory reaches 3,510,304 KiB. These samples do not establish peak memory.

Software verification passes. Training derivatives pass the declared checks.
Native data qualification does not change. Model acceptance fails.
No capture, export, deployment change, or Git write occurs.

Raw evidence stays under `reports/work/FOCUS-311/`.
The directory preserves registration, scale records, checkpoints, predictions, and case-linked losses.
The coordinator stores the result at cursor 141. The approved SMB fallback passes exact readback.
Sillycon-TTR acknowledgment remains pending. Message storage does not establish peer delivery.
