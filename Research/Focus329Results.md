# FOCUS329 — native boundaries and added edge channels

The corrected native diagnostic and matched 30-epoch candidate complete.
Reject the candidate as a replacement. Maximum-mini-NUIAK preserves the model for diagnosis only.

## Model result

| Check | FOCUS327 | FOCUS329 |
| --- | ---: | ---: |
| Native-derived correct /640 | 592 | 592 |
| Native false changes /219 unchanged pairs | 4 | 0 |
| Native missed changes /421 changed pairs | 0 | 0 |
| Native abstentions | 44 | 48 |
| Reversed native correct /640 | 590 | 592 |
| Replay correct /668 | 660 | 660 |
| Reversed replay correct /668 | 651 | 650 |
| Lighting correct /226 | 226 | 226 |
| Left distraction correct /226 | 155 | 155 |
| Center distraction correct /226 | 83 | 85 |
| Center false changes /226 | 136 | 132 |
| Tiny forward changes correct /4 | 0 | 0 |
| Tiny reversed changes correct /4 | 0 | 0 |

The candidate turns 4 native false changes into abstentions. It does not add correct forward native decisions.
It loses no forward native successes against FOCUS327. It gains 2 reversed native decisions and 2 center-distraction decisions.
However, reversed replay case 64 changes from correct to abstention. Its probability falls from 0.857709 to 0.818869.
The fixed threshold remains 0.85. Do not lower it for this inspected case.
Compared with the earlier FOCUS313 model, the candidate loses 19 native successes and gains 13.
These results fail the previous-success requirements. They do not support model replacement.

Authored training correctness reaches 755/960, versus FOCUS327's 736/960.
Authored false changes fall from 3 to 0, but missed changes increase from 6 to 8.
Placeholder movement stays 6/8. Placeholder arrival stays 14/16. Tiny identical pairs remain 8/8 correct.

Native training correctness stays 503/548. Development stays 37/40. Previously inspected reserved membership stays 52/52.
The 40 development pairs contain no focus changes. They cannot measure missed changes.
Previously inspected reserved cases are not untouched final evaluation. Native-derived pairs do not prove real-app or physical-device performance.

## What the native images show

The audit checks 548 training pairs across 17 groups at original resolution.
Those pairs reuse 138 source files. Every source image measures 3,840 × 2,160 pixels.
It verifies source hashes, encoded-image agreement, measured bodies, and observed focus identities.
All rows have measured geometry. The audit keeps reported clipping instead of treating visible boxes as complete bodies.
The metadata reports 1,084 partially clipped body entries. Another 3,568 body entries do not report clipping.
These repeated entries are not independent examples.

The audit uses every measured control with the same control IDs in both frames.
It measures a 35 px band around the union of both body positions, excluding their shared interior.
This band is a diagnostic definition, not Apple's focus formula.

| Content-change training check | Unchanged focus | Changed focus |
| --- | ---: | ---: |
| Pairs | 69 | 210 |
| Median share of change in boundary bands | 4.05% | 5.83% |
| Range of that share | 0.40%–4.49% | 4.86%–15.73% |
| Median boundary change strength | 0.5834 | 0.5161 |

Boundary location separates these training cases. Raw boundary strength does not: unchanged-focus cases can have stronger changes.
The content subset contains only 2 related families. Its perfect boundary-fraction ranking is not independent evaluation.
The image-only edge ratio gives weaker ranking scores of 0.690 and 0.683 within those families.
Here, 0.5 means chance ordering and 1 means every positive scores above every negative. This is not classification accuracy.
Existing image-selected windows contain about 42% of each family's boundary-change energy, by median.

## Diagnostic correction

The first audit selects controls from the focused endpoints. That gives changed pairs more regions than unchanged pairs.
Maximum-mini-NUIAK stops preparation before any epoch or checkpoint. The failed audit and partial preparation remain preserved.
The corrected audit uses the same control population. Its result still supports 1 bounded experiment.
The corrected audit takes 163.43 s. The rejected first audit takes 167.71 s.

## Candidate contract

Use the [approved plan](Plans/Focus329.md). Keep the original 12 detail channels and add 6 gradient-magnitude channels.
Initialize from FOCUS325-average. Set new convolution weights to 0. Starting prediction agreement is exact on the registered check.
Train detail filters and correction weights for 30 epochs. Freeze whole-frame and geometry weights.
Keep the original images, detail crops, membership, weights, thresholds, and all previous-success checks.
Correct boxes and observed focus IDs do not enter the candidate.

## Verification and evidence

The 101 focused Python tests pass. The offline native SwiftPM build passes in 4.33 s.
All 14 XCTest tests and 173 serial Swift Testing tests pass. Swift Testing takes 54.38 s.
No Swift source changes follow that integrated pass.
Ignored evidence stays in `reports/work/FOCUS-329/`.
The first preparation has no checkpoint. Its process exits with code 143 after the owned stop.

Preparation takes 124.96 s. Training takes 851.54 s for 3,420 updates.
Preparation, training, and the full comparison take 1,165.89 s. This excludes the audits and stopped preparation.
Peak memory is 5,731,909,632 bytes, below 8 GiB.
Original-view and detail-view hashes match FOCUS327. Cached feature agreement is exact.
Only 10 permitted detail and correction tensors change. Checkpoint reload agreement is exact.
Candidate SHA-256: `b8c1314e1edf622bed86cc763d200b6ba18bcddb5b1ae5229108074e55ef6964`.

- Software verification: passed.
- Data eligibility: existing training roles unchanged; no new admission.
- TTR integration qualification: not assessed.
- Model requirements: failed. No export or promotion occurs.

## Check of the added channels

After training, disable only the 6 added channels. Keep all trained weights and every raw channel unchanged.
Native correctness falls from 592/640 to 572/640. Missed native changes rise from 0 to 11.
The trained network uses the added channels. This does not establish a 20-case gain over the separately trained FOCUS327 control.
The 4 previous false changes remain abstentions with the channels disabled. Their improvement cannot be assigned to edge channels alone.
With edges enabled, their probabilities are about 0.824–0.826, versus 0.857–0.859 for FOCUS327.
These are near-threshold changes in 2 related training families, not broad evidence of reliable rejection.
The first report attempt fails after scoring because a source path has the wrong Python type.
The corrected report completes. A new entrypoint test covers that error. Both logs remain preserved.

## TTR coordination

The coordinator delivers historical TTR messages at cursors 166–169 and a routing receipt at 171.
Maximum-mini-NUIAK acknowledges the messages through cursor 171. This closes the missing historical-message gap.
The current renderer question reaches Sillycon-TTR at cursor 170. Its answer remains pending.
The historical messages do not establish a newer renderer or new execution authority.
Response 172 returns the public provider boundary and the existing REVIEW306 privacy correction.
Sillycon-TTR keeps current models. Authored geometry remains distinct from native visual evidence.
The coordinator stores the final result at cursor 174. Exact-ID readback passes; result forwarding and TTR acknowledgment remain unconfirmed.

## Next substantial tranche

Proposed FOCUS330 tests control-centered regions before another encoder change. Maximum-mini-NUIAK owns the work.

1. Compare known control regions with image-only regions on the existing training captures.
2. Use the resident tvOS detector to propose controls. Pin its model, settings, and coordinate conversion.
3. Measure missing controls, boundary coverage, and included artwork. Keep known-box results separate from usable model inputs.
4. Choose 1 region rule from training evidence only. Keep original-resolution extraction and a fixed pixel budget.
5. If that rule improves boundary coverage without unsupported labels, register 1 matched 30-epoch candidate.
6. Test every previous-success set with unchanged roles and thresholds. Report gains, losses, false changes, misses, and abstentions.

Use existing inference, crop, trainer, and comparison tools. No capture, download, export, or producer implementation is required.
Keep 2 CPU threads for training, an 8 GiB memory limit, and a 2 GiB output limit.
The detector supplies proposed regions, not focus labels. Missing controls remain explicit failures, not invented boxes.
Do not repeat another generic edge-channel fit or assume that larger synthetic datasets solve region selection.
The maintainer has not yet assigned FOCUS330. This proposal does not start another training run.
