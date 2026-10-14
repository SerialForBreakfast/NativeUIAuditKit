# FOCUS325: small controls and detail pooling

## Decision

Reject both candidates. Neither preserves previous successes or detects the 4 tiny native changes.
The mixed candidate learns more authored examples, but that improvement does not transfer to the native checks.
Keep the current TTR model. No export, promotion, or navigation change occurs.

## Matched experiment

Maximum-mini-NUIAK creates 432 authored pairs from approved FOCUS319 renders.
Control widths are 3, 6, and 12 pixels after whole-frame encoding. Separation is independently 32 or 96 pixels.
The generator covers 4 corners, 3 artwork families, 3 conditions, and both frame orders.
Conditions are focus movement, artwork changes without focus movement, and identical frames.
There are 360 distinct ordered pairs. Reversals and repeated identical pairs do not provide independent trials.
All 432 pairs retain training ancestry. They do not become native evidence or final evaluation data.
The validator checks every image, hash, changed region, transformed body box, and recorded focus state.
The review includes 9 representative views. All 72 coverage cells contain 6 scheduled rows.

Both candidates start from FOCUS319 and use the same 1,820 original examples plus 672 authored examples.
The authored examples include the previous 240 pairs. Original views, weights, detail crops, and exclusions remain unchanged.
Each run uses 30 epochs, seed 42, batch size 16, learning rate 0.0001, and authored loss weight 0.25.
Decision thresholds remain 0.15 and 0.85. No threshold changes follow evaluation.
Only the detail projection and correction layers train. All 30 other tensors remain unchanged.

The control retains adaptive average pooling into a 4 × 6 grid.
The correction uses a fixed 50/50 blend of average and maximum pooling into the same grid.
This is not a comparison against a single global average. Earlier planning language overstated that limitation.
Frozen convolution outputs are cached once. Tests check cache/image parity and checkpoint reload.
The candidate comparison isolates pooling. Comparison with FOCUS319 also includes further training and changed authored exposure.

## Results

Counts show correct decisions. False changes appear separately. Abstentions do not count as correct.

| Check | FOCUS319 | Average | Mixed |
| --- | ---: | ---: | ---: |
| Native, 640 pairs | 581 | 588 | 577 |
| Reversed native, 640 pairs | 579 | 580 | 562 |
| Replay, 668 pairs | 646 | 649 | 649 |
| Reversed replay, 668 pairs | 644 | 643 | 649 |
| Global changes, 226 pairs | 226 | 226 | 226 |
| Left distractions, 226 pairs | 160 | 155 | 165 |
| Left false changes | 53 | 64 | 57 |
| Center distractions, 226 pairs | 85 | 81 | 69 |
| Center false changes | 136 | 140 | 147 |
| Tiny native changes, 4 pairs | 0 | 0 | 0 |
| New authored training, 432 pairs | 204 | 225 | 260 |

Average pooling loses 7 previously correct native decisions and gains 14. Mixed pooling loses 31 and gains 27.
The mixed candidate introduces 2 native false changes. The average candidate introduces none.
Both candidates preserve 8/8 placeholder movements and 8/8 identical tiny negatives.
Both retain 14/16 placeholder arrival decisions. These previously inspected checks are not an untouched final audit.
Native totals include training and previously inspected evaluation groups. They do not measure independent deployment accuracy.
Raw reports retain each changed decision, group, and data role.

Mixed pooling detects 10/48 authored movements at width 3. Average pooling detects 0/48.
However, both candidates abstain on all 48 width-3 artwork changes.
This is a partial training improvement, not reliable small-control recognition.

## Additional diagnosis

The companion audit measures changed pixels after the unchanged whole-frame encoding.
For width-3 authored movements, 66–70 pixels exceed a mean RGB difference of 1/255.
The 4 tiny native movements affect 269–280 pixels at that threshold.
Their maximum mean RGB difference is 0.554–0.571, versus 0.098–0.150 for width-3 authored movements.
Width-6 authored movements affect 180–190 pixels, with maximum difference 0.158–0.254.
Thus control size alone does not match the native effect's area and contrast.
Resizing an entire patch also shrinks its shadow and highlight. The generator cannot vary those independently.
These measurements identify a coverage gap. They do not prove its causal effect on model errors.
The audit runs after training. It changes no weights, thresholds, labels, or membership.

## Verification and efficiency

All 70 focused tests pass. The offline Swift build passes.
All 14 XCTest tests and 173 serial Swift Testing tests pass.
Shared preparation takes 109.57 s. The training loops take 1.48 s and 1.55 s.
Each complete candidate run, including evaluation, takes about 158 s.
These timings show that preparation and evaluation dominate this frozen-feature experiment.
They do not establish the same speed for full encoder training.
No new capture, dependency download, external computation, or Core ML qualification occurs.

Evidence stays under `reports/work/FOCUS-325/` outside Git.
The corpus hash is `3baa6887965b4039043448201ee9edc5046eff44a276f5390cb2bdadb2442d5b`.
The average checkpoint hash is `1882c4458a9c583ee8745ae2bbaf012661463fce415c9dd61287de2338310d5e`.
The mixed checkpoint hash is `8a0bcbfd6e77dc148d4fc0e6a9b23b66b8ed4bfdb22daf9c6a31c26a4d83355a`.
`inputs.json` pins training inputs, code, review, and initialization.
`training-comparison.json`, both candidate reports, and `effect-audit.json` retain detailed evidence.

- Software verification: passed.
- Data eligibility: approved authored training only; original evaluation roles remain unchanged.
- TTR integration: not tested by this experiment.
- Model requirements: failed; no promotion.

The coordinator stores the result at cursor 158 without confirmed forwarding.
The approved SMB fallback publishes `nuiak/responses/nuiak-focus325-result-01.json` with verified size, hash, and readback.
Sillycon-TTR acknowledgment remains unconfirmed. The update tells Sillycon-TTR to keep its current model.

## Next substantial tranche

FOCUS326 should test effect coverage before another architecture change.
First, qualify independent control-body size, effect width, and contrast using existing local renderer capabilities.
Preserve size, separation, artwork, and position balance. Add matching artwork-only changes as negatives.
Then freeze a matched 2-run comparison against FOCUS325-average with equal optimizer updates and unchanged evaluation roles.
Use native development measurements to define broad coverage, not to copy protected native frames into training.
Record whether each effect is authored or measured. Do not claim native equivalence from a similar pixel difference.
Acceptance requires native gains without lost previous successes or increased false changes.
If existing tools cannot vary the effect independently, record the exact missing control before requesting producer changes.
Do not launch more volume or another pooling sweep without this evidence.
