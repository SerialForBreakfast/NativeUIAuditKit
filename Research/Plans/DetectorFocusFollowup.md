# Complete-path focus checks after the native pilot

Owner: Maximum-mini-NUIAK. Date: 2026-10-17.
Keep Standard unchanged. Keep HCF optional. The detached runner owns execution.

## What the pilot answers

The combined pilot covers 48 capture events from 6 development groups and 24 unique images.
Standard and HCF counterparts share pixels. Their equal scores do not establish an HCF advantage.

| Source | Baseline correct per profile | Candidate correct per profile | Candidate wrong per profile |
| --- | ---: | ---: | ---: |
| Known control boxes | 1/24 | 21/24 | 0 |
| General detector boxes | 4/24 | 16/24 | 1 |
| Detector boxes plus HCF rings | 4/24 | 16/24 | 1 |

The candidate loses no baseline successes within this pilot. The wider tall-control regression remains unresolved.
Detector proposals cover 20/24 focused controls per profile. Rings add no useful controls in this set.

The 8 candidate failures per profile separate into:

- 4 cases without a sufficiently overlapping box: 1 button and 3 rows.
- 3 cases with multiple scores above 0.85: 1 row and 2 tabs.
- 1 tab with adequate overlap but no score above 0.85.

The wrong row selection occurs when the focused control lacks a good proposal.
Known boxes fix the ambiguous row and the below-threshold tab. They do not fix the other 2 ambiguous tabs.
These results separate proposal errors from score competition. They do not justify lowering the selection threshold.

## Registered follow-up graph

B405-199 prepares retained captures through T59. B405-200 runs the pinned detector through T56.
B405-201 compares the matched training control and mixed model through T57.
This baseline differs from the retained delivery baseline in the first pilot. Report these comparisons separately.

| Case set | What does it test? | What will it decide? |
| --- | --- | --- |
| No-focus scenes | General boxes can appear when no Fixture control has focus. | Whether either classifier makes a false selection despite correct ring abstention. |
| Tall controls | The mixed model previously loses a raw-box success. | Whether general detector boxes preserve or repeat that regression. |
| Small decoration | Small decorative details can resemble focus cues. | Whether detector proposals introduce false selections or competing scores. |
| Diamond decoration | Strong decorative borders can attract proposals and scores. | Whether the complete path needs better negative examples or abstention. |
| Edge clearance | Crops and control bounds interact near image edges. | Whether proposal geometry removes otherwise correct selections. |

The corrected graph contains 13 jobs: 4 preparation jobs, 4 detector jobs, and 5 selection comparisons.
It reuses the qualified no-focus detector output. It does not repeat captures or training.
Every job retains the 800 s and 100 MB diagnostic limits.
Producer dependencies make later stages wait for verified outputs, not another chat instruction.

## Acceptance

Compare both crop models on identical proposals, thresholds, and source images within each case set.
Require zero lost previous successes and zero new false selections before advancing a correction.
Keep known-box, detector, and detector-plus-ring results separate.
Preserve all failed and exhausted attempts. Use explicit successors for changed inputs.
Do not interpret unmatched detector boxes as false positives when annotations are incomplete.
No-focus means verified absence of Fixture control focus, not proof about every external app.

## Reusable preparation

T59 converts verified development captures into the existing detector input format.
It checks native observations before and after capture, geometry, taxonomy, roles, image hashes, and dimensions.
It rejects unknown focus through the existing native observation checks.
Identical images share one payload only when labels, geometry, and groups agree.
Every original event remains recorded. Conflicting duplicates fail.

Software verification: 30 focused tests pass. The real isolated queue accepts 6 no-focus events with 3 unique images.
A negative queue test rejects a training-eligible artifact with `capture_role`.
Integrated offline Swift checks pass. No production Swift code changes.

The first integrated batch exposes an unsupported `labelReview` value after detector inference.
The producer now sets review status to `unknown` and records native observation separately as the label source.
The actual producer-to-detector queue test passes with this correction.
The corrected jobs use `pipeline-followup-*-v2-*` IDs. Original specifications and failed attempts remain unchanged.
Withdrawn approvals prevent obsolete blocked comparisons from running later.
The dashboard marks replaced failures as superseded only after their successors complete.

## Next decisions and remaining preparation

If no-focus cases produce false selections, preserve those cases before changing thresholds or training.
If adequate boxes create competing scores, prepare within-screen ranking comparisons from B405-180.
If box geometry causes the losses, prioritize B405-193 and the measured-error preparation in B405-196.
Derive any training error distribution from training groups, not these inspected development cases.
TTR observation-only verification still needs exact model export, receiver identity, and compatible proposal input.
This graph does not qualify TTR consumption, independent audit performance, or physical-device accuracy.

The batch is short diagnostic work, not a claim of overnight capacity.
Longer training remains conditional on a justified correction and complete matched inputs.
Do not fill idle time with repeated completed runs or arbitrary model variants.

Evidence: `reports/work/FOCUS-PIPELINE-FOLLOWUP/` and the immutable `pipeline-followup-*` queue attempts.
