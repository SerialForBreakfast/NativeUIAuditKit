# FOCUS310 — original detail and control sizes

Maximum-mini-NUIAK completes 2 matched 30-epoch runs and the full retained regression check.
Original detail reduces some distraction errors. It does not repair tiny focus changes or preserve all previous successes.
Do not promote either model. Existing models remain unchanged.

## Measured size gap

The audit follows the actual DTM085 schedule, including replacement images and reversed pairs.
It checks 1,820 entries with unchanged labels, roles, and weights.

| Schedule entries | Count | Measured minimum dimension after encoding |
| --- | ---: | --- |
| Native pairs and their derivatives | 1,152 | 15.06–27.02 pixels |
| Older encoded-only pairs | 668 | Original body measurements unavailable |
| Tiny development comparisons | 16 | 2.93 pixels |

All 2,304 endpoints of the native training entries have measured visible body bounds.
Those entries belong to 14 training groups. Repeated rows and reversed pairs are not independent evidence.
No measured native training entry has a focused body below 15 pixels across.
This does not prove that the 668 older entries lack small controls. Their original measurements remain unavailable.

The image-selected window contains a focused body's center in all 8 tiny changed comparisons.
It contains at least half that body in all 8 comparisons.
Among 806 changed native training entries, those counts are 578 and 224 respectively.
Thus, the size and visible body fraction differ between the training views and the tiny checks.
Geometry supports this diagnosis only. It does not select model inputs.

## Matched method

Both models start from DTM085 and retain full-frame context.
Both models have 339,932 parameters and a zero-initialized added correction.
Both use seed 42, batch 16, learning rate 0.0001, and 2 CPU threads.
Both use the fixed last checkpoint and thresholds 0.15/0.85.

Image differences select one aligned 32 × 32 window. Labels do not select it.
The control enlarges encoded pixels. The candidate uses original pixels where verified source images exist.
Both preserve aspect ratio and padding at frame edges. Encoded-only examples use the same fallback in both runs.
The existing trainer accepts an optional detail input. Its default path remains unchanged.
The existing evaluator accepts an optional input transform. Reference models retain their original inputs.

The first attempt stops after epoch 1 because its source crop removes padding retained by the control.
The corrected attempt uses a new directory. A new edge-padding test passes.
The failed attempt and its source remain preserved. No failed result enters model selection.

## Results

These counts show correct decisions, except the explicitly marked false-change row.

| Cases | DTM085 | Encoded control | Original detail |
| --- | ---: | ---: | ---: |
| Native training groups, 548 | 505 | 526 | 528 |
| Native development, 40 | 33 | 34 | 34 |
| Reserved native, 52 | 51 | 49 | 49 |
| Native total, 640 | 589 | 609 | 611 |
| Forward replay, 668 | 667 | 668 | 668 |
| Reversed native, 640 | 582 | 608 | 608 |
| Reversed replay, 668 | 666 | 665 | 667 |
| Global lighting, 226 | 226 | 226 | 226 |
| Left disturbances, 226 | 144 | 139 | 141 |
| Center disturbances, 226 | 80 | 90 | 94 |
| Center false changes, 226 | 121 | 119 | 108 |
| Tiny forward changes, 4 | 0 | 0 | 0 |
| Tiny reversed changes, 4 | 0 | 0 | 0 |
| Tiny identical-image comparisons, 8 | 8 | 8 | 8 |

Compared with DTM085, the candidate gains 27 correct native decisions and loses 5.
It gains 15 correct center decisions and loses 1. Aggregate gains therefore do not mean complete preservation.
The 2 reserved losses come from recipe-06. Both become abstentions, in both frame orders.
The matched control loses the same reserved cases. Original pixels alone do not explain these losses.
The candidate also has fewer correct decisions in 3 of 24 strength/order checks than DTM085.

Replacing original tiny detail with encoded detail does not change any tiny decision.
Both versions remain far below the fixed change threshold.
This rejects original detail alone as the current repair. It does not reject detail inputs in a scale-matched training set.

## Verification and limits

- 53 focused Python tests pass. A final 7-test check also passes.
- The offline Swift build passes. All 173 Swift Testing tests pass in serial mode.
- Source hashes and exact encoding parity pass for every native row used here.
- Checkpoint reload produces identical scores on the registered sanity inputs.
- The corrected preparation, fits, and regression checks take 944.58 s.
- The control fit takes 264.20 s. The original-detail fit takes 319.51 s.
- No capture, export, Git write, data-role change, or promotion occurs.

Previously inspected reserved cases remain regression evidence, not an untouched final audit.
These results concern the focus-transition model, not the shipped single-frame FocusRing model.
They do not establish real-app or physical-device performance.

## Next bounded correction

First, prepare small-control examples from training-only groups at approximately 3, 6, 12, and 24 encoded pixels.
Keep the existing tiny development pairs and all related evaluation exclusions unchanged.
Use local native generation where ready. Mark any scaled image derivatives as authored data, not new native observations.
Preserve negative-condition weights and include unrelated highlights, artwork changes, and unchanged focus.
Measure both control size and visible body fraction inside each detail view.
Then compare 1 scale-matched candidate against the same prior-success suite.
Do not repeat unchanged 30-epoch fits or lower the decision threshold.

Raw evidence: `reports/work/FOCUS-310/`.
The comparison SHA-256 is `0aada1cea00f0181fb51d2a097a2af04b0882d1e9b11e1973f8fcf9249b54cc4`.
The completion SHA-256 is `8ac681d7578cdd606e3193ce8d05f457f5bada0a48b3b19fcfa463791257feab`.

Software verification passes. Existing data roles remain valid. No new live integration or production model gate passes.
