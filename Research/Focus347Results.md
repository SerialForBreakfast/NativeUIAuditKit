# FOCUS347 — appearance failures confirmed

> Historical research record. Results retain their stated scope and limits.
> Host names are public aliases. Local evidence and execution records remain private.
> This publication does not revalidate earlier results or approve a model.

## Fixed correction against previous successes

Maximum detail pooling replaces the mean of 2 detail vectors with their elementwise maximum.
The test changes no weights, crops, labels, or thresholds. It does not train another model.
Fresh baseline predictions match the retained results exactly on all 7 sets.

| Retained set | Baseline correct | Correction correct | Gains | Previous successes lost |
|---|---:|---:|---:|---:|
| Native-derived, forward | 592/640 | 498/640 | 26 | 120 |
| Native-derived, reversed | 592/640 | 497/640 | 25 | 120 |
| Replay, forward | 660/668 | 639/668 | 1 | 22 |
| Replay, reversed | 650/668 | 638/668 | 1 | 13 |
| Global disturbance | 226/226 | 226/226 | 0 | 0 |
| Left disturbance | 155/226 | 169/226 | 14 | 0 |
| Center disturbance | 85/226 | 146/226 | 61 | 0 |

Reject the correction. Better distraction results do not justify losing native and replay successes.
FOCUS346 also records 41 authored losses. No model qualifies for replacement.
Reversed pairs remain related to their forward pairs. Do not add these counts as independent trials.
These inspected sets measure regressions, not untouched final evaluation.

## Remaining batch

All 20 appearance tests complete through the existing detached runner.
They separate whole-frame content, detail content, geometric padding, and source-image preprocessing.
The specifications preserve exact inputs, prior predictions, source groups, and decision rules.
Each job has an 800 s and 100 MB limit. Failed jobs do not retry automatically.
The raw reports remain under `reports/work/research-queue/jobs/focus347-*`.

## Verification and decision

Sixteen focused tests pass. The offline Swift build and 187 serial Swift tests pass.
All 25 new specifications pass input checks before dispatch.
The first 5 jobs complete through the actual detached runner. Their saved reports preserve every score and label.
The agent instructions now require geometric padding checks, regression checks, useful decisions, and queue-duration reporting.

FOCUS348 uses these results for one equal-budget augmentation comparison with original-example replay.
Keep the matched native size campaign separate. None of FOCUS346's tests repairs the native corner misses.

## Runner repair

The seventh job reaches its final progress event, but live size counting races with an atomic progress-file rename.
The controller stops without a completion receipt. Do not count that attempt as complete.
The size check now tolerates a file that disappears during inspection. It still rejects links and permission errors.
Final output hashing remains strict. The tests cover the missing-file race and rejected unsafe states.
research-host-NUIAK restarts only its idle dashboard to load the repair.
The original attempt remains preserved. An explicit `-r2` job uses the same inputs and scientific settings.
Remaining jobs resume. Reload the dashboard page if the previous launch token expires.
The replacement completes successfully. The next queued job also completes after the repair.
All 98 focused queue, dashboard, and experiment tests pass. The earlier offline Swift checks remain valid.

## Appearance results

The unchanged authored baseline gets 1,005/1,392 decisions correct.
The table reports source-image transformations before standard resizing and crop selection.

| Transformation | Correct | Gains | Lost successes | Changed crop selections |
|---|---:|---:|---:|---:|
| Brightness +0.1 | 923 | 190 | 272 | 234 |
| Contrast ×0.65 | 908 | 233 | 330 | 210 |
| Gamma 1.5 | 569 | 83 | 519 | 412 |
| Grayscale | 779 | 23 | 249 | 304 |
| Saturation ×0.5 | 822 | 17 | 200 | 284 |

Gamma also loses 495 successes when only detail content changes.
Its source result confirms that encoded padding does not explain the entire failure.
The source test also changes quantization and crop selection. It does not isolate gamma from those pipeline effects.
Every appearance condition retains 8/16 native development decisions. No condition correctly detects a native movement.
The 8 correct native decisions are stable pairs. Gamma converts some native misses into abstentions, not correct detections.

Select gamma augmentation with original-view replay for FOCUS348.
Compare it with unchanged-image training at the same budget.
Do not infer native improvement from authored training accuracy.
