# FOCUS342 — training balance and preservation

> Historical research record. Results retain their stated scope and limits.
> Host names are public aliases. Local evidence and execution records remain private.
> This publication does not revalidate earlier results or approve a model.

Owner: research-host-NUIAK. Both 30-epoch runs and all 3 diagnostic jobs complete.
Keep FOCUS329 as the retained control. Neither candidate qualifies as its replacement. No shipped model changes.

## Measured outcomes

Counts below show correct decisions. Abstentions do not count as correct.

| Set | FOCUS329 | FOCUS341 content | Rotation | Rotation and preservation |
| --- | ---: | ---: | ---: | ---: |
| Matched content changes, 192 training cases | 27 | 152 | 152 | 151 |
| Matched focus movement, 192 training cases | 146 | 151 | 154 | 151 |
| Previous authored examples, 1200 cases | 978 | 886 | 841 | 955 |
| Native-derived examples, 640 mixed-role cases | 592 | 600 | 600 | 594 |
| Reserved native-derived examples, 52 cases | 52 | 50 | 50 | 52 |
| Retained replay, 668 cases | 660 | 658 | 658 | 663 |

Preservation reduces lost authored successes from 166 under rotation to 35. FOCUS341 content loses 115.
Preservation keeps all previous correct forward native-derived decisions and adds 2 development successes.
It also keeps all previous correct forward replay decisions and adds 3 successes.
These are useful gains, but aggregate correctness hides errors.

- Matched content: rotation has 0 false changes and 40 abstentions. Preservation has 24 false changes and 17 abstentions.
- Matched movement: rotation loses 3 previous successes. Preservation loses 0, but still misses 2 changes.
- Native-derived cases: preservation changes 4 training abstentions into false changes. Rotation misses 2 reserved changes.
- Reversed native cases: preservation loses 2 successes and gains 2. Rotation loses 9 and gains 23.
- Reversed replay: preservation loses 3 successes and gains 5. It misses 5 changes, versus 2 under FOCUS329.
- Center distractions: preservation loses 5 successes and gains 9. It has 116 false changes among 226 cases.
- Left distractions: preservation loses 0 successes and gains 4. It still has 59 false changes among 226 cases.
- Global lighting changes: both candidates preserve all 226 correct decisions.
- Tiny controls: both retain 8 correct decisions and miss all 8 positive cases. They show no improvement.
- Headless arrival and movement: preservation retains all decisions. Rotation loses 2 arrival successes and creates 2 missed movements.

The 4 new native-derived false changes cross from approximately 0.824–0.826 to 0.855–0.856.
The positive threshold stays at 0.85. Protecting confident successes alone does not protect abstentions from becoming errors.
All 35 authored losses under preservation occur in 2 artwork groups: 16 in `r1-s0` and 19 in `r1-s2`.
Do not change thresholds or select another checkpoint from these results.

## Audit

The old replacement schedule excludes 368 authored negative examples: 232 artwork changes and 136 identical pairs.
Those missing examples account for 43 of the 115 lost authored successes. The other 72 losses occur on retained examples.
Missing coverage therefore explains only part of the measured conflict.

Both new runs use the same 1820 primary examples, 1820 auxiliary assignments, and 114 updates per epoch.
Both retain the original crops and use the same initialization, learning rate, thresholds, and 30-epoch budget.
Rotation restores coverage of all 736 old negatives across training. It does not restore their original total weight.
Old negatives receive 12,734.14 weight units, versus 25,498.28 under the original schedule, before the common auxiliary coefficient.
New negatives receive 12,764.14 units. Rotation and fixed replacement have equal total weights.

The second run protects confident, correct training predictions from the frozen baseline.
It does not use reserved examples as preservation targets. Its recorded primary loss includes the preservation penalty.
Compare decisions across these objectives, not their raw loss values.

## Evidence limits

Matched content changes are authored training examples from 3 related groups.
They change a central background panel. They do not establish native performance or inside-control content coverage.
Native-derived results separate 548 training, 52 reserved, and 40 development cases.
Reserved cases already guide research. They are not untouched final evaluation.
Reversed pairs and related frames do not establish independent trials.

The received 200 triplets remain outside training. Their positive role means control identity, not focused state.
Their archive lacks full-screen pixels and complete source crop rectangles.

## Queue and efficiency

The refreshed dashboard runs the 3 new diagnostic jobs. All pass within 800 s and 100 MB.
The queue now has 92 completed jobs and 43 blocked jobs. Automatic mode remains enabled with no ready job.
The blocked jobs include 25 placeholder jobs and 18 broader investigations. Completion does not imply measured model improvement.

The authored A3 comparison reuses 384 predictions from 192 matched pairs.
Maximum relative magnitude mismatch is 0.001888, or approximately 0.189%.
Both causes receive correct decisions in 27 pairs under FOCUS329, 30 under added detail, and 137 under FOCUS341 content.
These are training-only results across 3 groups. The original native A3 investigation remains open.

The triplet audit verifies 600 crops and finds 81 distinct decoded images.
Shared pixels connect the 200 cases into 14 groups. Reported frame ancestry produces the same 14 groups.
This does not establish independence or training eligibility.

The frozen-branch timing test uses 8 training examples, 5 repeats, and 2 CPU threads.
Cached calculations match direct predictions and gradients exactly in this test.
Median calculation time falls from 77.7 ms to 30.7 ms, a measured ratio of 2.53.
Cache preparation takes 52.6 ms. This is not an established full-run speedup.
The separate rotation report spends 86.4 s preparing images and 12.9 s on inference for 1584 examples.
Therefore, cache prepared crops as well as frozen outputs when exact input identities permit reuse.

## Verification, preservation, and next work

All 124 focused tests pass. The offline Swift build and 187 Swift tests pass.
No original crop, shipped model, threshold, or existing data role changes.
Both queue attempts pass output integrity checks. Their weights, schedules, predictions, and failed acceptance evidence remain unchanged.
Each model has 364,813 parameters, including 24,449 parameters in the added branch.
Rotation takes 1599.77 s. Preservation takes 1520.49 s. Both stay below 1800 s and 2 GiB.
The 3 diagnostic jobs take 2.15 s, 6.10 s, and 0.23 s.
Full authored reports take 101.75 s and 87.03 s. The first report overlaps the second run's final evaluation.
Use the [machine-readable summary](../reports/work/FOCUS-342/summary.json) and its linked reports for exact case comparisons.
Use the [audit](../reports/work/FOCUS-342/audit.json) and [weighted exposure](../reports/work/FOCUS-342/weighted-exposure.json) for schedule evidence.

The next batch should combine cached execution, artwork exchange, identical neighbors, and training-only analysis of the remaining errors.
Test both lost correct decisions and newly wrong decisions from prior abstentions. Do not use aggregate accuracy as the sole gate.
Use current TTR artwork inputs before requesting new rendering controls.
The [queue review](Focus342QueueReview.md) separates executable authored work from missing native controls.
No worker host run or new TTR capture is required to complete this tranche.
The coordinator stores and returns the exact final update at cursor 308. Recipient forwarding and acknowledgment remain pending.
The full tranche takes approximately 65 min, against the initial 90–120 min estimate.
Training attempts account for 52.0 min. No external wait blocks local execution.
