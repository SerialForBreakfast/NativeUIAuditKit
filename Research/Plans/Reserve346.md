# FOCUS346 — 25 ready tests for focus changes

> Historical research record. Results retain their stated scope and limits.
> Host names are public aliases. Local evidence and execution records remain private.
> This publication does not revalidate earlier results or approve a model.

## Purpose and scope

Owner: research-host-NUIAK. The maintainer requests 25 useful, unblocked experiments.
The chat defines tests and reviews results. The existing dashboard runs fixed jobs without chat supervision.
This batch diagnoses errors. It does not train, capture, promote, or change production thresholds.

FOCUS343 finds 8 native movement misses and 8 correct stable decisions.
FOCUS344 finds strong negative whole-frame contributions despite positive detail contributions.
Changing crop size does not recover those misses. Keep the original crops.

## Fixed inputs and measurements

Use the FOCUS329 checkpoint and 1,408 retained pairs.
The sources contain 240 FOCUS319 pairs, 960 independent FOCUS326 pairs, 192 matched content pairs, and 16 native pairs.
Here, “independent” names the existing corpus partition. It does not establish statistical independence.
Keep existing roles, groups, exclusions, labels, and original identifiers when present.
Native pairs remain development-only. Their app/build match remains unresolved.
Do not use these inspected cases for final evaluation.

Prepare original-resolution detail crops once with the existing preprocessing.
Store 44 compressed chunks with hashes, baseline predictions, source references, and the model hash.
Preparation takes 67 s and stores 98,400,171 bytes on this machine.
The cache preserves original encoded values. Tests change copies only.

Each job changes 1 factor and compares all cases against the same baseline.
Report correct decisions, false changes, missed changes, abstentions, gains, and lost successes by source, condition, and group.
Retain every score and label for later paired comparisons. Related pairs do not count as independent trials.
Keep the existing decision limits: stable at 0.15 or below; changed at 0.85 or above; otherwise abstain.
Missing theme coverage and unavailable native qualification remain explicit.
These tests do not cover all 7 archetypes or 3 themes.

## Priority and decisions

Run each numbered group as 1 cycle of 5 jobs.

| Jobs | Controlled tests | Decision |
|---|---|---|
| 01–05 | Whole-score floor; maximum detail features; no edge channels; first crop only; second crop only | Identify suppression or harmful detail combinations before another fit. |
| 06–10 | Shared brightness; contrast; gamma; grayscale; saturation | Identify appearance dependence and useful training variations. |
| 11–15 | Blur; shared noise; color precision; half resolution; block averages | Identify required image detail and capture tolerance. |
| 16–20 | Horizontal reflection; vertical reflection; context translation; padding; unchanged pixels | Identify position, orientation, padding, and background dependence. |
| 21–25 | Partial change; stale first crop; stale second crop; exposure flicker; frame jitter | Identify false confidence from incomplete or inconsistent inputs. |

The immutable specifications contain exact parameters and a separate hypothesis for each job.
Encoded-view changes are controlled diagnostics, not claims of native rendering.
Reflection preserves pair labels but does not move crops through the original proposal algorithm.
Stale detail tests deliberately break view consistency. They do not create valid training examples.
Partial-change tests do not establish animation or settling labels.
Block averages do not simulate a specific image codec.
Removing visible evidence can invalidate recognition. Report comparison with original labels, not new ground truth.

## Execution and acceptance

Use the existing queue, interpreter, CPU model, and dashboard.
Use 2 CPU threads, 800 s, 100 MB, and 1 attempt per job.
The maintainer's explicit diagnostic limit replaces the older 300 s and 10 MB defaults for this tranche.
Check every input hash before execution. Reject missing or changed inputs.
Report actual completed pairs during execution. Preserve partial output after failure.
Do not repeat successful jobs or retry failed jobs automatically.

Before dispatch, verify 25 pending jobs with no missing requirements and valid input hashes.
Complete focused tests and the required offline Swift checks.
Refresh the detached runner's fixed job set after registration.
Use `scripts/reserve346.py review` to compare completed results without rerunning inference.

A useful correction recovers target errors without losing retained successes.
Diagnostic gains alone do not justify promotion. Distorted-input results can only justify a subsequent controlled experiment.
Keep native capture work active in its separate queue. Cached tests do not replace Simulator or real-app evidence.

## Replenishment

At each research review, count ready jobs separately from blocked proposals and completed jobs.
When fewer than 10 useful jobs remain, prepare the next evidence-backed reserve toward 25.
Prioritize native size matching, matched content negatives, and a justified branch correction after this batch.
Do not add arbitrary parameter sweeps to meet the count.
The runner cannot invent valid experiments. A finite reserve can finish before the next research review.
Report depletion explicitly. Do not claim perpetual work or background chat monitoring.

## Verification

All 25 jobs pass specification and input hash checks before dispatch.
The readiness receipt is `reports/work/FOCUS-346/ready.json`.
Twelve focused tests pass, including all 25 interventions against the actual checkpoint.
The offline Swift build and 187 serial Swift tests pass.
The dashboard accepts the refreshed batch through authenticated controls.
The model workflow skill keeps model identity, preprocessing, and data roles fixed.

The first job completes through the detached runner in 10.6 s. The second job starts without chat execution.
Limiting whole-frame suppression gains 91 authored decisions but loses 272 prior successes.
It recovers no native movement decisions. Reject this direct correction.
The remaining jobs continue independently. These fast tests do not constitute an overnight workload.
