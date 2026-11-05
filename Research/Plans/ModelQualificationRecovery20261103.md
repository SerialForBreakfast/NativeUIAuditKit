# Model qualification recovery checklist — November 3, 2026

Owner: Maximum-mini-NUIAK.
Purpose: establish whether R5 and WSP improve consumer results without losing previous successes.
Tasks.md remains the task authority. This checklist defines follow-up work; it does not record completed implementation or admit jobs.
Keep shipped Standard models unchanged. Keep HCF optional and iOS independent.

## 1. Verify current source and evidence — P0

Owner: Maximum-mini-NUIAK.

- [x] Record the active branch, revision, dirty files, and available main revision.
- [x] Check remote changes through the approved Git workflow. Preserve uncommitted work before any integration.
- [x] Re-audit current label generation, scoring, thresholds, and model identities.
- [x] Record whether newer changes fix each audited defect. Do not assume main contains a correction.

Gate: every finding names the inspected revision and exact evidence. No claim that a pull or merge occurred without a receipt.

## 2. Correct claims and task status — P0

Owner: Maximum-mini-NUIAK. Depends on step 1.

- [x] Mark the RC561 100% score as invalid independent accuracy evidence if the circular evaluation remains.
- [x] Preserve original reports, predictions, labels, captures, and failure evidence.
- [x] Reopen incomplete RA554-13 and RC561-05 qualification work.
- [x] Correct README, current status, experiment records, dashboard claims, and promotion summaries where affected.
- [x] Describe 10/10 NewsTV scores above 0.01 as a diagnostic, not recall at the 0.85 acceptance threshold.

Gate: displayed claims identify their evaluation scope, threshold, data role, numerator, and denominator.
Historical claims remain traceable with explicit corrections. No candidate gains promotion status from this correction.

## 3. Test evaluator independence and reporting — P0

Owner: Maximum-mini-NUIAK. Reuse existing evaluators, manifests, templates, and consumer diagnostics.

- [x] Reject candidate predictions presented as independent reference labels.
- [x] Require reference provenance, review completeness, and frozen membership for qualification.
- [x] Test exact matches, wrong classes, duplicates, localization failures, empty predictions, and failed inference.
- [x] Test known no-focus, unknown focus, unresolved classes, and incomplete annotations.
- [x] Verify coordinate conversion, orientation, taxonomy mapping, crop hashes, and loaded-model identity.
- [x] Reject membership changes and cross-partition duplicates.
- [x] Cross-check detection scoring with the official COCO evaluator on identical inputs.

Gate: positive and negative tests pass through the real evaluation entrypoint.
Candidate-derived drafts remain distinct from independently reviewed references.
No filename, hash, or automatic accepted flag substitutes for independent review.

## 4. Independently label retained screens — P1

Owners: Maximum-mini-NUIAK prepares evidence; the maintainer or designated human reviewer confirms labels.
Reuse SDK539-APPS and RC561. Do not create another application-integration project.

- [x] Prepare authenticated SDK drafts without candidate predictions in the review interface.
- [ ] Review complete visible control coverage, including controls absent from SDK registration. (Human reviewer)
- [ ] Record visible bounds, clipping, occlusion, control identity, and provenance. (Human reviewer)
- [ ] Keep ambiguous classes unresolved. Distinguish focused, known no-focus, and unknown focus. (Human reviewer)
- [x] Audit training exposure, application ancestry, duplicate images, and related flows.
- [x] Preserve the manifest of captured, rejected, missing, and reviewed cases.

Gate: every scored case has independently reviewed labels. Precision uses only complete annotations.
The existing 8 screens are development evidence after diagnostic use, not a fresh independent holdout.
Retain the planned 50-screen pilot and subsequent 200-screen benchmark across 5 qualified apps.
If fewer apps qualify, report actual coverage. Do not count related frames as independent evidence.

## 5. Compare shipped Standard and R5 — P1

Owner: Maximum-mini-NUIAK defines the graph. The detached runner executes approved jobs.
Depends on steps 3 and 4.

- [ ] Freeze models, hashes, preprocessing, taxonomy, thresholds, labels, and membership before inference.
- [ ] Use full screenshots through the actual TTR consumer path. Keep SDK labels outside model inputs.
- [ ] Score shipped Standard first. Score the predeclared candidate on identical inputs.
- [ ] Report per-class recall, precision, misses, unmatched detections, AP50, AP75, and AP50–95.
- [ ] Report correct selections, wrong selections, abstentions, unknown references, no-focus false selections, latency, and execution failures.
- [ ] Report recovered cases, lost successes, and new wrong selections.
- [ ] Report each application and an equal-application summary. Preserve flow groups for exploratory uncertainty estimates.

Gate: every frozen case has predictions or an explicit execution failure. Failed inference cannot disappear from the denominator.
Report a selected test population, not deployment-wide accuracy. Keep the historical custom AP definition separately named.

## 6. Qualify WSP FocusRing at the actual threshold — P1

Owner: Maximum-mini-NUIAK; detached runner executes approved comparisons.

- [ ] Freeze the candidate and shipped baseline, with the 0.85 threshold unchanged.
- [ ] Reproduce legacy retention and per-case backend decisions.
- [ ] Report supplied-box scores separately from full-screen TTR selection.
- [ ] Measure existing FOCUS556 gates and remaining retention checks.
- [ ] Test no-focus scenes and hard negatives through the consumer path.

Existing development gates: D1 >=12/21; D2 <=8/21; D3 >=5/21; legacy retention 270/270.
The audited WSP receipt reports D1=3/21, D2=16/21, D3=1/21, and legacy retention 270/270.
Those results fail development acceptance. Do not lower thresholds or gates to declare success.
Keep R2, R3, and fresh qualification requirements from FOCUS556 explicit.

## 7. Keep independent work moving — P1

Owner: Maximum-mini-NUIAK.

- [x] Prepare approved FOCUS556 training-only crops and groups while independent labels await review.
- [x] Keep real-app development and qualification images outside that training corpus.
- [ ] Review iOS retention losses separately and select a correction supported by those failures.
- [ ] Reuse completed comparisons and existing templates. Do not repeat rejected fits unchanged.
- [ ] Register exact jobs only after inputs, conditions, budgets, and approvals qualify.
- [ ] Report ready duration separately from job counts and dependent work.

Missing real-app labels block qualification, not unrelated valid experiments.
The runner owns execution. This checklist does not start training, capture, or services.

## Decisions and finish line

- Supported: candidate passes existing gates; prepare a separate promotion decision with rollback artifacts.
- Contradicted: preserve the result and identify the specific training or consumer correction.
- Inconclusive: name missing coverage or uncertain references; continue independent work.

Finish: reproducible comparisons establish gains, losses, and limitations without circular labels or misleading thresholds.
Static screenshots cannot establish tracking quality. Keep the temporal benchmark separate.

## Evidence inspected in the preceding audit

- [RC561 label generation](../../scripts/rc561_build_holdout.py)
- [WSP parity report](../../reports/work/WSP/wsp-parity-report.json)
- [Focus diagnostic definitions](../../scripts/focus_candidates556.py)
- [FOCUS556 acceptance gates](FocusRealApp556.md)
- [Existing independent benchmark plan](RealApp554.md)

These references describe the audited files. Step 1 must check subsequent changes before implementation.
