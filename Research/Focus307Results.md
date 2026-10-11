# FOCUS307 — Detail and training exposure

Maximum-mini-NUIAK completes 2 related diagnostics without capture, training, or threshold changes.
The tested region-only policy fails its acceptance check. No model changes reach TTR.

## Fixed comparison

The runner compares 1,334 retained pairs with DTM083 and DTM085.
It reuses whole-frame scores and image-only proposals from FOCUS302 and TRANSITION297.
It checks model hashes, source hashes, and native encoding against retained tensors.
Source regions and enlarged low-resolution regions use the same coordinates in both frames.

- Select at most 4 regions by area, with coordinates as the tie breaker.
- Expand each region by 2, with a minimum window of 32 × 32 input pixels.
- Use the existing 192 × 128 transition encoder.
- Use the highest region score as the pair score.
- If no region exists, keep the whole-frame score.
- Keep decision thresholds at 0.15 and 0.85.

This changes experimental transition inputs, not production FocusRing crops.
Region selection never reads focus labels or observed focus boxes.
The report evaluates the complete pair decision. It does not assign pair labels to individual regions.
Authored disturbance sets only have encoded frames. Their source-region and enlargement paths therefore match.

## Results

Counts below show correct decisions. Abstentions do not count as correct decisions.

| Set | Pairs | DTM083 whole | DTM083 regions | DTM085 whole | DTM085 regions |
| --- | ---: | ---: | ---: | ---: | ---: |
| Native, training role | 548 | 505 | 502 | 505 | 502 |
| Native, development role | 40 | 34 | 19 | 33 | 19 |
| Native, reserved role | 52 | 51 | 52 | 51 | 52 |
| Center distractions | 226 | 81 | 57 | 80 | 56 |
| Left distractions | 226 | 152 | 125 | 144 | 123 |
| Global lighting changes | 226 | 226 | 45 | 226 | 47 |
| Tiny controls, forward | 4 | 0 | 0 | 0 | 0 |
| Tiny controls, reverse | 4 | 0 | 0 | 0 | 0 |
| Identical tiny-control frames | 8 | 8 | 8 | 8 | 8 |

Both models change all 8 tiny-control misses into abstentions with source regions.
Neither model correctly declares these focus changes at the fixed thresholds.
DTM085 forward scores rise from below 0.00005 to 0.668–0.780.
This shows useful sensitivity, but not a successful detector.

Regions cause 134 false changes for DTM083 and 153 for DTM085 on global lighting cases.
The whole-frame path has 0 false changes on those 226 cases.
The remaining region errors on that set are abstentions.
Source regions and enlarged encoded regions produce the same native decision counts, despite some different scores.

Reject this fixed region-only policy as a replacement.
Do not lower the threshold to make the 4 tiny-control pairs pass.
The result does not reject every region method or prove that detail is the only cause.
The maximum-score rule and loss of surrounding context can also cause errors.

## Independent companion: actual training weights

The companion reconstructs all 1,820 entries in the retained schedules.
It checks the exact label and weight hashes before reporting contributions.
These percentages describe loss weights, not measured gradients or independent evidence.

| Schedule | Content-contrast weight | New focus-pair weight | New identical-pair weight |
| --- | ---: | ---: | ---: |
| DTM083 control | 26.38% | 0% | 0% |
| DTM084 combined | 20.54% | 3.61% | 2.22% |
| DTM085 positive addition | 22.77% | 3.61% | 0% |
| DTM086 negative addition | 24.15% | 0% | 2.22% |

All schedules assign 40.24% of total loss weight to legacy replay.
This audit does not resolve that replay's independent group ancestry.
Reverse pairs repeat exposure; they do not create new independent examples.

Keeping group totals fixed does not keep condition totals fixed.
New focus comparisons take weight from content-contrast comparisons in this design.
The next comparison must report both totals and keep negative-condition exposure explicit.
These figures do not prove which weights caused an accuracy change.

## Evidence and limits

- [Registered comparison](../reports/work/FOCUS-307/registration.json).
- [Scores and conditional counts](../reports/work/FOCUS-307/result.json).
- [Exposure audit](../reports/work/FOCUS-307/exposure.json).
- [Completion receipt](../reports/work/FOCUS-307/completion.json).
- [Executable comparison](../scripts/detail307.py).
- [Executable exposure audit](../scripts/exposure307.py).

The comparison takes 135.87 s, including input verification and image reads.
The output receipt records 1,301,444 bytes before later documentation and coordination records.
No simulator setup, artifact transfer, model download, or external wait is required for scoring.
Existing roles remain unchanged. Repeatedly inspected reserved cases are not a new untouched audit set.
The 4 tiny-control pairs share existing development ancestry.

Software verification, data eligibility, integration, and model approval remain separate.
All 32 focused Python tests pass. The native offline build and all 173 serial Swift tests pass.
The original parallel test attempt stalls in Apple Vision. The serial attempt completes in 54.00 s.
The output-collision check rejects a duplicate launch before inference.
The software tests do not establish new data eligibility or real-app accuracy.
Native capture evidence comes from the retained runs. This tranche performs no live TTR test.
Neither model qualifies for promotion from this result.

## Next substantial tranche

Test 1 model that sees both whole-frame context and aligned region detail.
Use admitted training groups only. Keep the tiny-control batch outside training.
Compare against a matched whole-frame control with fixed initialization, epochs, and decision thresholds.
Keep lighting, artwork, scrolling, and identical-frame negatives in the comparison.
Report condition weights and every retained gain and loss.
Stop the candidate if improvements require hiding a failed condition or moving evaluation examples into training.

Before fitting, register the exact representation, eligible inputs, parameter count, training budget, and storage limit.
This is a new controlled hypothesis, not permission to launch an open-ended sweep.
