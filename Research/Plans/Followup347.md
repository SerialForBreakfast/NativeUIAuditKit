# FOCUS347 — isolate appearance failures and test a correction

> Historical research record. Results retain their stated scope and limits.
> Host names are public aliases. Local evidence and execution records remain private.
> This publication does not revalidate earlier results or approve a model.

Owner: research-host-NUIAK. Use the existing detached queue.

## Evidence and decision

FOCUS346 completes 25 jobs across 1,408 retained pairs.
The jobs use 319 s of worker time and produce 62 MB of outputs.
Shared preparation uses 67 s and 98 MB. These figures exclude chat analysis and queue gaps.
No tested intervention recovers a native corner movement decision.
Every intervention loses authored successes. Do not promote any intervention.

Maximum detail pooling gains 94 authored decisions and loses 41.
This result justifies measuring broader regressions, not training or promotion.
Shared brightness loses 301 authored successes. Reduced contrast loses 337. Gamma loses 510.
Those interventions also change encoded padding or image statistics after resizing.
Changing padding alone gains 97 decisions and loses 29. Padding is a demonstrated model input, not harmless storage.

## Next batch: 25 ready experiments

Jobs 01–05 test maximum detail pooling on retained native, replay, global, left, and center sets.
The native and replay jobs include both frame orders.
Keep weights, original detail preparation, and thresholds fixed.
Require fresh baseline predictions to match retained predictions within 1e-6.
Report every lost success. The correction already fails authored acceptance; broader results do not erase that failure.

Jobs 06–25 test 5 appearance factors with 4 controlled paths each.
The factors are brightness, contrast, gamma, grayscale, and saturation.
Use the same factor settings as FOCUS346. Do not add a parameter sweep.

| Path | Fixed elements | Question |
|---|---|---|
| Whole-frame content | Detail crops and padding | Does context cause the appearance sensitivity? |
| Detail content | Whole frame and padding | Does local detail cause the sensitivity? |
| All content | Geometric padding and crop positions | Does the failure persist without changing padding? |
| Original source images | Model and standard preprocessing | Does the failure persist through actual resizing and crop selection? |

Use geometry to identify padding. Preserve black image content.
For unchanged pairs, detail views use the existing whole-frame fallback.
For changed pairs, use the existing crop mapping to identify valid source support.
The source-image path includes quantization, resizing, and crop selection. Do not attribute its result to only one stage.
Record how many source pairs change their selected crop positions.

## Execution contract

Reuse FOCUS346's pinned model, 1,408 rows, and compressed original views.
Reuse the pinned regression arrays and existing label membership for jobs 01–05.
Keep native app/build uncertainty explicit. Do not admit native development images for training.
Preserve related groups and final evaluation exclusions.
Do not claim all-theme or all-archetype coverage.

Use 2 CPU threads, 800 s, 100 MB, and 1 attempt per job.
Run 5 jobs per cycle. Reject changed inputs before execution.
Preserve completed attempts and failed evidence. Do not retry automatically.
The runner reports completed pairs, not time-derived percentages.
The source-image paths take longer than cached paths. Measure their actual cost before estimating an overnight reserve.

## Acceptance and next decision

Require focused geometry, immutability, transformation, and preprocessing tests.
Run the required offline Swift checks once after integration.
Verify 25 pending specifications and input hashes before dispatch.
Check actual detached execution and complete the 5 regression comparisons during this tranche.
Let remaining diagnostics continue without chat supervision.

If source-level variations confirm an appearance weakness, define one equal-budget augmentation comparison with original-example replay.
Do not remove original examples or choose thresholds from the native development cases.
If only encoded changes fail, fix the experimental method before adding training data.
Keep the matched native size campaign as a separate priority. These tests do not replace native coverage.

## Process improvements

Evaluate the loop on resolved questions and retained gains, not completed jobs.
Track queue duration as well as count. A 25-job reserve can still finish in minutes.
Keep review reports compact. Preserve raw predictions once, with hashes.
Use rejected corrections to stop unnecessary fits. Do not call rejected corrections model improvements.
Keep training and model promotion separate from automatic execution.

## Verified checkpoint

All 25 specifications pass input checks. The detached runner completes the first 5 jobs.
Maximum detail pooling loses 120 previous successes per native frame order. Reject the correction.
See [the results](../Focus347Results.md) for all 7 sets and exact baseline parity.
Sixteen focused tests, the offline Swift build, and 187 Swift tests pass.
The remaining appearance experiments run independently of this chat.
