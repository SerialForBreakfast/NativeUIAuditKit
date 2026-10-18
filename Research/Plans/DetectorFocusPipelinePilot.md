# Detector boxes to focus selection

Owner: Maximum-mini-NUIAK. Approved priority: 2026-10-17.
Tasks.md owns task status. This plan defines the pilot and its immediate follow-up.

## Question

Can existing control detections feed the improved crop classifier and produce useful full-screen focus selection?
The latest native-control candidate gets 42/48 correct selections with known boxes.
The tested mapped ring path supplies no useful selections on those native controls.
Do not infer that the general detector also misses every case.

## Existing parts and missing connection

T55 prepares development labels. T56 runs the detector and records original-image pixel boxes.
T42 evaluates class-aware and class-free detection. T37 uses production cropping and fixed focus selection.
T37 currently expects ring proposals, capture ordering, geometry records, and a ring-to-body mapping.
The new connection must accept detector body boxes without ring-specific corrections.
Reuse production crop preparation, resident models, and existing outcome definitions.
Do not build another runner, trainer, or evaluation framework.

## Pilot contract

Freeze both crop checkpoints, detector identity, image hashes, frame membership, groups, thresholds, and crop helper identity.
Use retained native development cases with verified observed focus and body geometry.
Keep Standard and HCF results separate. Preserve identical-pixel profile events without counting them as independent groups.
Use known boxes only as a diagnostic reference, never as a deployable proposal source.

Compare these sources using both the retained and latest crop models:

1. Known control boxes.
2. General detector boxes, without filtering by the true class or focus label.
3. General detector boxes plus qualified HCF ring boxes.

Enable the ring addition only for explicit HCF inputs.
Freeze duplicate handling before scoring. Record removed duplicates and their source identities.
Do not use ground truth to select, rank, correct, or merge runtime proposals.
Keep ring mapping separate from detector geometry. Reject unknown coordinate conventions.
Retain original boxes and record every conversion.

Reuse compatible cached detector outputs when their pixels, model, settings, and dimensions match.
Otherwise add bounded detector inference jobs using the existing template.
No new training or capture belongs to the first pilot.

## Software qualification

Run positive and negative cases through the actual compiler and an isolated queue.
Label generated software-test fixtures separately from scientific evidence.

- Verify top-left pixel coordinates and explicitly supported conversions.
- Verify original-resolution crop hashes and unchanged scores against the existing path.
- Reject altered input hashes, unsupported versions, duplicate frame IDs, and mismatched membership.
- Reject nonfinite, empty, or unsupported out-of-frame geometry under a declared clipping policy.
- Accept a valid empty proposal list without inventing a control.
- Keep multiple overlapping proposals visible unless the frozen merge rule removes them.
- Distinguish no-focus truth, unknown truth, absent proposals, and selection abstention.
- Reject missing comparison outputs instead of declaring improvement.
- Preserve completed attempts across interruption and explicit successor submission.

Qualification does not prove model accuracy. Native comparisons follow only after software checks pass.

## Results and decisions

Report per frame, family, profile, and source:

- Focused-control proposal recall before crop scoring.
- Correct selections, wrong selections, misses, and abstentions.
- Verified no-focus false selections and correct abstentions.
- Box overlap, score margins, candidate counts, and duplicate counts.
- Gained cases and previous successes lost against the same-input baseline.
- Independent group support and unavailable conditions.
- Preparation, inference, crop, scoring, and reporting time.

If proposals miss the focused control, prioritize proposal repair.
If boxes exist but overlap poorly, prioritize geometry or realistic box-error training.
If adequate boxes receive wrong scores, prioritize the classifier or selection rule.
If local results differ from TTR, diagnose preprocessing and integration before more training.
No result grants navigation authority or automatic model promotion.

## Highest-priority follow-up after the pilot

Reuse B405-188 for class-versus-geometry analysis where the inputs match.
Use B405-193 and B405-196 for the tall-control regression and realistic proposal errors.
Reuse B405-182 and B405-194 for no-focus states and competing selected controls.
Do not recreate already answered questions under new IDs.

Inventory retained no-focus, border, and competing-control captures before requesting new images.
If a condition lacks qualified evidence, name the missing observation and prepare a producer dependency.
Unknown focus is not a negative label.

Prepare an observation-only handoff with exact models, input images, expected boxes, crops, scores, and tolerances.
Confirm the receiving TTR owner and supported interface before dispatch.
TTR unavailability blocks receiver verification only, not local comparisons.
Preserve existing Standard defaults and keep the HCF path optional.

## Admission and budgets

Use 800 s and 100 MB per diagnostic job.
Pin complete graphs and approve exact immutable IDs under the assigned scope.
Submit batches of 5–10 where useful; do not split reports merely to increase job count.
Keep active worker code unchanged. Integrate shared changes at an idle boundary.
The detached runner executes jobs. Chat reviews batch findings and selects the next correction.

Estimate: 2–4 h for pilot implementation and qualification.
Estimate: 4–8 h total for local pilot and follow-up preparation.
Assumptions: retained inputs qualify, resident tools work, and shared integration has an idle boundary.
New capture, training, background scoring, and TTR execution are outside these estimates.
Record measured execution duration before claiming ready hours.

## Completion

The pilot completes when qualified jobs produce a matched full-path report, not when the adapter compiles.
The follow-up completes when each failure category has evidence and a concrete next action.
Keep unsupported conditions explicit. Do not delay useful local branches for missing receiver evidence.

## Implementation and first qualification — 2026-10-17

T57 runs the matched comparison. T58 combines button, row, and tab reports.
The existing batch compiler registers and approves exact job identities. No new runner is introduced.

The first queue test finds detector boxes entirely below the image.
The corrected adapter records invalid boxes and excludes them from scoring. It does not move them into the image.
Detector-first overlap suppression uses IoU 0.5. Every removed box remains in the result.
HCF mapping applies only to ring boxes. Standard never receives ring additions.

Software checks pass 27 tests. The isolated queue accepts retained button inputs and rejects an unsupported scorecard version.
The integrated offline Swift build and serial tests pass without changing production code.
The successful button attempt takes 14.94 s, including queue overhead.
The original known-box scores agree within 0.0001. Both model comparisons use identical box lists.

On each profile's 8 button frames, detector boxes support 7 focused controls.
The candidate selects 7 correctly; the baseline selects 2. Neither model makes a wrong selection in this slice.
The candidate loses no baseline successes in this slice. Known boxes give the candidate 8 correct selections.
These profiles share pixels and 2 development groups. They are not independent demonstrations of HCF benefit.
The slice has no no-focus frames. It does not qualify abstention on real no-focus scenes.

The 3 registered jobs are `focus-pilot-row`, `focus-pilot-tab`, and `focus-pilot-report`.
The report reuses `focus-pilot-button-qualified-v2` from the isolated queue.
Each job retains the 800 s and 100 MB limits. The runner starts the row comparison without a restart.
This is a short diagnostic batch, not an overnight workload. Further work follows the failure evidence.

Local evidence resides under `reports/work/FOCUS-PIPELINE-PILOT/`.
Keep the failed attempt, successful successor, negative test, and pinned batch descriptions.
