# FOCUS364–365 results

> Historical research record. Results retain their stated scope and limits.
> Host names are public aliases. Local evidence and execution records remain private.
> This publication does not revalidate earlier results or approve a model.

Date: 2026-10-13. Owner: research-host-NUIAK.
Plan: [matched scenes and graph decisions](Plans/FocusGraphs364.md).

## Decision

The graph produces useful failure evidence without changing model weights or thresholds.
Do not replace the original model from these results.
The appearance-trained models lose 1 correct corner movement on the new layouts.
The next correction should address notification changes while preserving matched movement decisions.
Keep native HCF training blocked until TTR repairs observation checks and recovery passes.

## Measured results

All models use the same 392 authored pairs and the existing crop path.
The 2 artwork families come from existing training material. These pairs are development diagnostics, not independent final evaluation.
Reversed pairs remain related. Counts do not establish a deployment error bound.

| Model | Correct | Wrong change | Missed movement | Abstained | Gains against original | Lost successes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| FOCUS329 | 308 | 33 | 4 | 47 | 0 | 0 |
| gamma348 | 324 | 24 | 4 | 40 | 17 | 1 |
| movement349 | 323 | 24 | 4 | 41 | 16 | 1 |

The first 4 layouts supply 224 pairs.
The newer Settings, dialog, and corner layouts supply 168 pairs.
All 7 layouts run under the renderer's default appearance. Other themes remain unsupported.

The first batch shows 11 gained successes and no lost successes for gamma348.
The newer layouts expose the lost success. This result demonstrates why wider controlled coverage matters.

## What the failures mean

- Settings banner changes cause 8 false changes in 8 gamma348 cases.
- Dialog banner changes cause 8 false changes in 8 gamma348 cases.
- Toast changes cause another 8 false changes across those 2 layouts.
- All 4 confident movement misses occur beneath the banner over navigation tabs.
- The banner covers both annotated tab boxes. Some pixel differences remain because the banner is translucent.
- One dimmed corner movement changes from 0.99263 under FOCUS329 to 0.79253 under gamma348.

The last case is `artwork-s1-focus_maze-005`.
The threshold remains 0.85. The candidate abstains instead of retaining the original correct change decision.
Do not lower that threshold to remove this failure without a separate calibration experiment.

The banner result needs interruption handling and visibility labels.
It does not justify forcing a confident answer when the screen covers the useful cue.
The Settings and dialog results justify matched notification negatives with movement-preservation controls.

## Execution and efficiency

The queue completes 29 jobs across the initial, repaired, and extended graphs.
Two initial producers exceed the 100 MB limit. Their failed outputs remain available.
Three obsolete consumers remain blocked on those failed producers. Successor consumers replace them without changing their specifications.
The repaired graph reuses completed renderer, grid, navigation, and native-review results.
It does not regenerate successful inputs.

Recorded worker time totals 112.46 s, including the 2 failed producers.
Retained outputs total 807,251,631 bytes at review time.
These measurements exclude implementation, queue waiting, and software tests. They are not an end-to-end speedup claim.
Per-job limits remain 800 s and 100 MB. The dispatcher runs at most 5 jobs per cycle.

The continuous dispatcher remains enabled. It does not rerun completed jobs to fill idle time.
The next model correction needs a frozen hypothesis and retained-success comparison before training starts.

## Software verification

- 38 queue and initial graph tests pass.
- 68 dashboard tests pass with required loopback access.
- 18 final graph and description tests pass.
- 173 Swift tests pass with serial offline execution.

Test groups overlap. Do not add these counts into a unique test total.
The graph tests exercise a contradicted condition through the real queue.
The conditional consumer remains blocked while an independent job completes.
Other tests cover altered evidence, unknown versions, unbound conditions, arbitrary expressions, and repeated case IDs.

Initial dashboard and Swift checks encounter sandbox restrictions. Scoped host checks pass without changing system permissions.
No NUIAK Git write, model installation, native setting change, training run, or promotion occurs.
The authorized research-host-TTR pull reports that its checkout is already current.

## Evidence

- FOCUS364 decision: `reports/work/research-queue/jobs/focus364-r2-90-decision/attempts/1/out/decision.json`.
- Visibility check: `reports/work/research-queue/jobs/focus364-r2-91-visibility/attempts/1/out/visibility.json`.
- FOCUS365 decision: `reports/work/research-queue/jobs/focus365-90-decision/attempts/1/out/decision.json`.
- Failed and successful attempts remain under their original queue IDs.
- Test logs and the pinned TTR source remain under `reports/work/FOCUS364/`.

Each decision links the exact comparison reports. Those reports link original images, annotations, labels, probabilities, and model hashes.
