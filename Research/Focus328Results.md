# FOCUS328: growth versus content contrast

## Decision

Reject the candidate as a replacement. Keep the current TTR model.
The experiment completes diagnosis, 1 matched 30-epoch candidate, full regression checks, and the case-level report.
It improves authored training and some distraction checks. It loses native-derived successes and introduces missed focus changes.
No export, promotion, capture, or data-role change occurs.

## Matched comparison

The [plan](Plans/Focus328.md) fixes inputs, initialization, training schedule, thresholds, and output limits before fitting.
FOCUS328 normalizes each detail frame before its learned filters. FOCUS327 uses raw detail frames.
Both start from FOCUS325-average and train the same detail filters and correction layer.
Whole-frame and geometry weights remain unchanged. Both use the original 1,820 views and 1,200 auxiliary rows.
Raw images and original-resolution crops remain unchanged. Their hashes and cached feature agreement pass exactly.

| Check | FOCUS327 | FOCUS328 |
| --- | ---: | ---: |
| Authored training correct /960 | 736 | 893 |
| Authored false changes | 3 | 0 |
| Authored missed changes | 6 | 2 |
| Authored abstentions | 215 | 65 |
| Native-derived correct /640 | 592 | 546 |
| Native false changes /219 unchanged pairs | 4 | 0 |
| Native missed changes /421 changed pairs | 0 | 11 |
| Native abstentions | 44 | 83 |
| Reversed native correct /640 | 590 | 544 |
| Replay correct /668 | 660 | 644 |
| Reversed replay correct /668 | 651 | 643 |
| Global lighting correct /226 | 226 | 226 |
| Left distraction correct /226 | 155 | 186 |
| Left distraction false changes | 64 | 32 |
| Center distraction correct /226 | 83 | 74 |
| Center distraction false changes | 136 | 128 |
| Tiny native changes correct /4 | 0 | 0 |
| Tiny reversed changes correct /4 | 0 | 0 |
| Tiny identical pairs correct /8 | 8 | 8 |
| Placeholder movements correct /8 | 6 | 8 |
| Placeholder arrivals correct /16 | 14 | 14 |

FOCUS328 loses 60 native-derived successes and gains 14 against FOCUS327.
The lost cases belong to `234:recipe-02` and `training234-family0/1`.
Against the earlier FOCUS326-independent control, it loses 56 native successes and gains 13.
All earlier model comparisons remain in the report. Do not select only the favorable comparisons.

## Where contrast helps and hurts

The training content-contrast set contains changed artwork and backgrounds. It is not solely a brightness adjustment.
Report both labels separately.

| Training condition | FOCUS327 correct | FOCUS328 correct |
| --- | ---: | ---: |
| Focus stays unchanged /69 | 42 | 53 |
| Focus changes /210 | 192 | 137 |

The correction helps unchanged-focus cases but harms changed-focus cases under the fixed training budget.
Blanket normalization is not a safe correction. The result does not prove that every normalized representation will fail.
It also does not establish that a longer run would fix the losses.

Training-only perturbations cover 24 factor cells from 1 artwork family.
The average feature shift falls from 22.92 to 17.96 in arbitrary activation units.
For movement crops, it falls from 25.57 to 0.86. For artwork-only crops, it falls from 25.66 to 0.40.
For identical full-frame fallbacks, it rises from 17.55 to 52.61.
The fixed perturbation covers crop content but only the central region of a full-frame fallback.
That last condition is a regional contrast change, not a global contrast change. The aggregate hides this important difference.
These measurements explain sensitivity. They are not accuracy estimates or independent trials.

The boundary diagnostic uses authored boxes, not model proposals.
It measures a 35-pixel band around the union of the two control bodies, excluding their shared interior.
In 8 selected movement cases, that band contains 70.2%–90.2% of change energy, averaging 83.4%.
In 8 artwork-only cases, the band contains no change energy. All 8 identical cases have no change energy.
This supports testing boundary-specific information. It does not establish a native effect formula or a usable image-only detector.

## Data roles and limits

| Role | Rows | Groups | FOCUS327 correct | FOCUS328 correct |
| --- | ---: | ---: | ---: | ---: |
| Training | 548 | 17 | 503 | 456 |
| Development | 40 | 10 | 37 | 38 |
| Previously inspected reserved groups | 52 | 2 | 52 | 52 |

All 40 development pairs have unchanged focus. They cannot measure missed focus changes.
The reserved groups already have repeated inspection. They are not untouched final evaluation.
Native-derived totals include retained captures and derived pairs. They do not measure general real-app or physical-device accuracy.
No threshold, membership, or label changes occur. The fixed last checkpoint supplies all reported candidate results.

## Software and execution

The first preparation stops before an epoch to correct full-frame fallback handling. Its source and partial evidence remain preserved.
The corrected normalization preserves full-frame side pixels and existing black crop margins.
The candidate changes only 10 detail and correction tensors. Checkpoint reload gives exact predictions.

- Focused checks: 89 pass in 1.84 s.
- Offline native SwiftPM build: passes in 4.28 s.
- XCTest: 14 pass.
- Serial Swift Testing: 173 pass in 54.50 s.
- Corrected preparation: 122.44 s.
- Training: 752.58 s for 30 epochs and 3,420 updates.
- Training and full evaluation: 1,050.40 s, excluding the stopped preparation and later report analysis.
- Peak memory: 5,977,391,104 bytes, below 8 GiB.
- Retained output at report time: about 8 MiB, below 2 GiB.

Ignored evidence is in `reports/work/FOCUS-328/`.
`inputs.json`, `preparation.json`, `diagnostic.json`, `comparison.json`, and `report.json` link inputs, measurements, and case changes.
Exact sources, failed checks, the stopped preparation, and the checkpoint remain available.
Candidate SHA-256: `9a71b6da09355c8baa7e54340be37fb2ccf2c6564627c053dc3e1d3d872be022`.
FOCUS327 control SHA-256: `d6328fe53e30478fb6bcdda44d50ce4d382f41bc9ee6d44b1f1de1c0d17f89df`.

- Software verification: passed.
- Data eligibility: unchanged retained training roles; no new admission.
- TTR integration qualification: not assessed.
- Model requirements: failed. Preserve the candidate for diagnosis only.

## TTR coordination

The coordinator stores the result at cursor 164. It does not confirm forwarding or recipient acknowledgment.
The SMB fallback publishes `nuiak/responses/nuiak-focus328-result-01.json` with verified bytes, hash, and parsed readback.
The message tells Sillycon-TTR to keep the current model. It creates no capture, build, or worker assignment.
The inspected Maximum-mini-TTR checkout remains `d06a64bd8840c5ada053fd90841c56cef2a9dd58`.
History after cursor 163 contains no new TTR messages. The earlier request for the reported feature updates remains open.
No new relevant artifact offer or cleanup receipt appears in the checked reports. The historical EVS transfer already has completed cleanup.
Missing chat delivery does not block this completed local experiment.

## Next substantial tranche

Proposed FOCUS329 tests boundary information while preserving raw appearance.
Maximum-mini-NUIAK owns the comparison. New producer work still requires human approval.

1. Measure boundary and interior changes on retained training captures with verified per-frame body bounds.
2. Compare those known-box measurements with existing image-only region proposals.
3. Keep known-box results separate from deployable inputs. Report missing or clipped bounds instead of guessing them.
4. If native training evidence supports the method, register 1 additive boundary/detail correction that keeps raw appearance available.
5. Train 1 fixed 30-epoch candidate with unchanged membership, thresholds, original views, and previous-success checks.
6. Report changed-focus and unchanged-focus errors separately. Reject losses in previous successes.

Use the existing trainer, crop extraction, scorer, and retained controls. Keep the 2-thread, 8 GiB memory, and 2 GiB output limits.
Do not repeat blanket normalization, lower thresholds to pass the 4 tiny cases, or start more volume without a measured gap.
If known native boundaries do not distinguish the failures, deliver that finding before another fit.
TTR can help with independently controlled geometry and artwork, but the local diagnostic needs no new capture or renderer.
