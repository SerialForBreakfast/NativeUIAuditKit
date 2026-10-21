# REHEARSAL482 — Broader rehearsal and completed no-focus review

## Completed findings

All 31 IOS480 jobs, 9 NOFOCUS481 jobs, and 4 native fallback comparisons complete.
No model qualifies for replacement.

| Mixed IOS480 comparison | Gained detections | Lost detections |
|---|---:|---:|
| Against matched original-data control | 25 | 56 |
| Against native-only candidate | 70 | 52 |
| Against Run013 | 19 | 57 |

The original-data control gains 40 detections and loses 47 against Run013.
Both small training arms regress. Native mixing alone does not solve the problem.
These comparisons use the same 6 retained development conditions. They do not establish release accuracy.
Case identities remain in the terminal report at `ios480-matched-decision/attempts/1/out/decision.json` under the local queue.

The no-focus review and all 8 dependent comparisons complete without recapture.
Both crop models abstain correctly with both detector confidence tiers and both profiles.
The profiles share identical pixels. This is 1 scene, not independent evidence from 2 scenes.

B405-256 finds no Standard fallback gain across 4 new native groups.
The candidate detector path gains 1 HCF decoration selection without losses or new wrong selections.
Do not extend that narrow result to Standard or deployment.

## Next correction

Test broader original-data coverage with existing preparation and training adapters.
The control uses 128 original training images. The mixed arm uses 112 shared original images plus the same 16 native images.
Both memberships pass actual trainer preparation. Preserve training roles, label checks, group exclusions, and original source hashes.
Keep Run013 initialization, seed 371, 30 epochs, fixed-last selection, and all scoring settings unchanged.
Each fit retains the 1,800 s and 2 GiB limits.
Corpus growth also changes native proportion and optimizer steps. Do not attribute cross-size changes to one mechanism.

The 31-job graph includes 2 fits, 12 scores, 2 decisions, 12 conditional diagnoses, and 3 matched reports.
Reject replacement if any Run013 success is lost. The graph does not promote models or start further training automatically.
B405-257 independently checks fallback abstention using the completed no-focus reports through T66.

## Execution and queue duration

All 32 new jobs receive exact approval. The runner starts `ios482-control-train` without a restart.
At this check, 1 job runs, 2 jobs are pending, and 29 await dependencies or conditions.
The previous fits take 542 s and 569 s. Estimate 35–40 min for both larger fits, plus scoring and reports.
This batch is not an overnight reserve. Conditional diagnostics do not count as independently ready work.
The queue was empty because the previous graph finished without another qualified training batch behind it.

## Grooming decisions

- Close the no-focus validator repair. Preserve its failed attempts and completed successors.
- Reject both IOS480 candidates as replacements. Preserve all case-linked losses.
- Stop unchanged fallback tests on button, row, and tab groups. They add no gains.
- Check no-focus fallback once with the completed evidence. Do not repeat capture.
- Run the larger matched rehearsal before changing the trainer or adding a model architecture.
- Keep a lower-learning-rate or frozen-backbone comparison as preparation work until a qualified adapter supports it.
- Do not reuse the novel adapter claims as proof of a working detector trainer.

## Evidence

- `reports/work/REHEARSAL482/membership/qualification.json`
- `reports/work/REHEARSAL482/trainer-check-control/dataset/dataset.yaml`
- `reports/work/REHEARSAL482/trainer-check-mixed/dataset/dataset.yaml`
- `reports/work/REHEARSAL482/preflight.json`
- `reports/work/REHEARSAL482/compiled.json`
- `reports/work/REHEARSAL482/admission.json`
- `Research/Experiments/results/B405-256.json`
- `Research/Experiments/batches/B405-257.json`

Standard behavior, shipped models, original captures, and previous successes remain unchanged.
