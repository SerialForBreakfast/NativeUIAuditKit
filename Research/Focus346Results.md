# FOCUS346 — results and value of the experiment loop

All 25 jobs complete. The shared baseline has 1,005 correct authored decisions among 1,392 pairs.
It correctly rejects all 8 native stable pairs and misses all 8 native movements.
No tested intervention recovers a native movement decision.

| Intervention | Authored gains | Previous authored successes lost | Decision |
|---|---:|---:|---|
| Limit whole-frame suppression | 91 | 272 | Reject direct correction. |
| Maximum detail pooling | 94 | 41 | Reject replacement; measure broader regressions. |
| First detail only | 118 | 48 | Keep both original views. |
| Shared brightness | 201 | 301 | Investigate appearance and padding separately. |
| Reduced contrast | 241 | 337 | Investigate appearance and padding separately. |
| Gamma 1.5 | 87 | 510 | Test source-level luminance changes. |
| Gray padding | 97 | 29 | Treat padding as a meaningful model input. |

These are comparisons against original labels, not deployment accuracy estimates.
Interventions can remove visible evidence or break view consistency.
The 1,408 pairs contain 5 authored group names and 1 native scene group.
They do not represent 1,408 independent trials. Native app/build matching remains unresolved.

## Efficiency

The 25 workers use 318.84 s in total. Median job time is 12.59 s; the longest is 14.49 s.
Measured evaluator time totals 289.74 s. Worker startup and completion account for the remaining 29.10 s.
Shared preparation takes 66.61 s. The prepared cache uses 98.40 MB.
Job output folders use 61.98 MB. These figures exclude chat analysis, queue gaps, and ancillary logs.
The workers score 35,200 pair interventions without repeating original crop preparation for each test.
No measured comparison with an uncached full campaign exists. Do not claim a speedup ratio.

## Assessment

The loop reliably produces reproducible evidence and rejects weak corrections at low compute cost.
It does not yet improve native focus detection. No model qualifies for replacement.
The main weakness is experimental interpretation: encoded appearance changes can also change padding and crop consistency.
The next batch separates those effects and checks the most promising pooling change against previous successes.
Do not respond with another broad training sweep.

See [FOCUS347](Plans/Followup347.md) for the next 25 fixed comparisons.
Raw evidence remains under `reports/work/research-queue/jobs/focus346-*`.
