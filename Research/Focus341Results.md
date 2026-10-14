# FOCUS341 — overnight results

> Historical research record. Results retain their stated scope and limits.
> Host names are public aliases. Local evidence and execution records remain private.
> This publication does not revalidate earlier results or approve a model.

Owner: research-host-NUIAK. Review date: 2026-10-12.

Both 30-epoch runs finish. Neither meets the requirement to preserve previous successes.
The baseline and original crops remain unchanged. No model promotion occurs.

| Set | FOCUS329 correct | Added detail correct | Detail and content correct |
| --- | ---: | ---: | ---: |
| Matched content, 192 training cases | 27 | 30 | 152 |
| Matched movement, 192 cases | 146 | 149 | 151 |
| Retained authored, 1200 cases | 978 | 985 | 886 |
| Native-derived, 640 mixed-role cases | 592 | 599 | 600 |
| Left distraction, 226 cases | 155 | 153 | 161 |
| Center distraction, 226 cases | 85 | 89 | 97 |
| Global distraction, 226 cases | 226 | 226 | 226 |

## Gains and losses

Matched content false alarms fall from 89 to 74 with detail, then to 0 with content training.
The final arm still abstains on 40 matched content cases. These gains concern training examples from only 3 related groups.
They do not establish performance on unseen apps.

Added detail loses 10 previous authored successes and gains 17. The content arm loses 115 and gains 23.
Added detail loses 6 previous native-derived successes and gains 13. The content arm loses 13 and gains 21.
The 640 native-derived cases include 548 training cases, 52 reserved cases, and 40 development cases.
The content arm misses 2 changes in the reserved 52 cases. Added detail gets all 52 correct.
Repeated review means these reserved cases are not untouched final evaluation.

The reversed replay exposes 8 missed changes with content training, compared with 2 for the baseline.
Related and reversed cases are not independent trials. Do not combine their counts into a statistical safety claim.

## Evidence and time

Added detail takes 1490.94 s. Detail with content takes 1476.40 s.
Both finish within their 1800 s limits. Combined training takes 49.46 min.
The review verifies all 15 output files for each job against their recorded sizes and hashes.
Raw reports remain under `reports/work/FOCUS-341` and the existing queue attempt folders.
The summary is `reports/work/FOCUS-341/unattended-summary.json`.

## Queue and received data

The queue contains 130 jobs: 87 complete and 43 blocked. No job is ready.
The blocked jobs include 25 placeholders and 18 measured investigations. Completion does not establish scientific validity.
Missing controls include separate effects, clipping, positions, no-focus scenes, timed frames, and matched native rendering.
Some authored matched-change evidence now exists. It does not silently change frozen specifications.

The received TTR archive contains 200 triplets and 600 verified PNG crops.
Only 81 decoded images are distinct. No identical pixels carry conflicting supplied focus labels.
All 200 positive crops have `is_focused: false`. Their positive role concerns control identity, not focus state.
The archive remains outside training. TTR still needs to explain crop mapping and observed labels.
Its SHA-256 matches the offer, but the offered size is wrong: 50,474,809 versus 50,138,372 actual bytes.
The first transfer rejects that mismatch. A separate record uses the observed size and unchanged offered hash.

## Decision

Keep FOCUS329 as the comparison baseline. Do not replace shipped models.
FOCUS342 tests whether the new negative schedule removes useful training coverage.
This is a hypothesis, not an established cause. Run the coverage audit before another candidate.
