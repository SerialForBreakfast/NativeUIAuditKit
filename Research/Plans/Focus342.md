# FOCUS342 — preserve gains during content-change training

> Historical research record. Results retain their stated scope and limits.
> Host names are public aliases. Local evidence and execution records remain private.
> This publication does not revalidate earlier results or approve a model.

Owner: research-host-NUIAK. Complete. [Results](../Focus342Results.md) reject both candidates as replacements.

The fixed replacement removes 368 old negatives. The candidate also loses 72 successes among retained authored examples.
Test rotating coverage and training-only margin preservation separately. Neither diagnosis establishes causation before comparison.
The weighted audit confirms equal weight totals for fixed replacement and rotation.
Across 30 epochs, old negatives receive 12,734.14 weight units and new negatives receive 12,764.14 units before the common coefficient.
The original schedule gives old negatives 25,498.28 units. Rotation restores coverage, not the original total negative weight.

## Outcome

Test whether changed training coverage causes the FOCUS341 regressions.
Keep both original crops, original data roles, fixed thresholds, and previous results.
Do not use reserved failures as training labels or preservation targets.

## Batch of 5 jobs

1. Audit the old and new auxiliary schedules. Measure group coverage and training-only margins from cached predictions.
2. Audit the received triplets. Check duplicate groups, crop mapping, and label meaning before any admission.
3. If job 1 supports lost coverage, compare a balanced schedule with the retained FOCUS341 control.
4. If training-only evidence supports it, test a preservation loss against the balanced schedule.
5. Compare all fixed candidates against FOCUS329 and both FOCUS341 runs. Report each previous success lost.

Jobs 1 and 2 use separate inputs and can proceed independently.
Job 2 does not block jobs 3 and 4, which use already admitted inputs.
Job 4 remains conditional. Do not run an unsupported candidate to fill the batch.

The queue review also includes a bounded timing check for frozen-branch reuse.
Use 8 admitted training examples, 5 measured repeats, 2 CPU threads, and no optimizer updates.
Require prediction and gradient agreement within 0.000001. Report the measured batch cost, not an end-to-end speedup.
This check does not change either fixed training run. It identifies whether a later cache can reduce repeated work.

## Fixed requirements

Use the existing queue, crop function, trainer, and reports.
Freeze complete input hashes, group membership, initialization, schedule, and decision rules before execution.
Compare equal update budgets. Report old-negative exposure and matched-negative exposure separately.
Use training-only cases for any preservation targets. Keep related artwork and reversed pairs together.
Keep thresholds at 0.15 and 0.85. Do not choose checkpoints from reserved results.
For the preservation arm, the recorded primary loss includes its preservation penalty. Compare decisions, not raw losses across objectives.
Limit diagnostics to 800 s and 100 MB each.
Limit each of at most 2 candidates to 30 epochs, 1800 s, and 2 GiB.
Do not retry failed runs automatically. Preserve partial evidence.

## Acceptance

Require an improvement on the target failure without losing retained previous successes.
Report false changes, missed changes, abstentions, role support, and margins separately.
Include authored, native-derived, distraction, tiny-control, headless, and reversed comparisons.
Keep training fit separate from reserved performance. Report unsupported themes and layouts explicitly.
Keep the previous model if either candidate fails. An inconclusive diagnostic does not justify training.

## Dependencies and estimate

Retained-data work needs no new TTR capture or worker host execution.
Archive admission needs TTR's crop mapping and label explanation.
Allow 20–40 min for audits and preparation, plus about 50 min for 2 candidates.
The training estimate uses FOCUS341's measured 24.6–24.9 min per run.
Report build and review time separately. No new architecture, navigation authority, or release enters this batch.
