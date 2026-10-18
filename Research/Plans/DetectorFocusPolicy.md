# Test fixed corrections before more training

Owner: Maximum-mini-NUIAK. Date: 2026-10-17.
Standard remains the primary path. HCF stays optional.

## Measured findings

All corrected B405-199 through B405-201 jobs complete.
No execution failure remains in that graph. Historical failed attempts remain available.

- Both models abstain on 6 no-focus events from 3 groups.
- The candidate loses 1 Standard diamond-decoration success when using detector boxes.
- Known boxes preserve that success. The detector-box score is 0.585, below the frozen 0.85 threshold.
- General detector boxes cover 11/16 Standard focused controls and 0/16 HCF focused controls in these hard-case sets.
- Mapped rings add coverage for all 16 HCF focused controls. The candidate selects 15 correctly through the combined proposal path.
- The small-decoration miss has competing proposals. The Standard regression instead has a low score.

These are development results. They do not establish generalization across physical devices or external apps.
The native pilot uses the retained delivery baseline. The hard-case follow-up uses the matched training control.
Do not combine these baseline comparisons into one claimed model improvement.

## Chosen corrections

### B405-202 — prefer ring candidates only in HCF mode

If retained mapped-ring candidates exist in HCF mode, score the selection from those candidates alone.
Otherwise keep the existing candidate list. Standard retains the identical list and scores.
Keep the original score threshold, model, and geometry.

This tests whether general-detector candidates create avoidable competition with qualified ring candidates.
It uses only ring candidates retained by the original merge. It does not restore suppressed proposals.
The isolated small-decoration test improves from 3/4 to 4/4 HCF selections, with no changes to Standard.
The 7 queued case sets test transfer and preservation. Reuse the isolated result instead of repeating it.

### B405-203 — older-model fallback after candidate abstention

If the candidate does not produce exactly 1 score above threshold, check the older model on the identical boxes.
If the older model produces exactly 1 score above threshold, use that selection for this experiment.
Otherwise keep the candidate's abstention.

This tests recovery of the observed Standard loss. It can also restore older wrong selections.
Test that risk explicitly across all 8 retained case sets. Do not implement this fallback in TTR without qualification.
Truth labels evaluate the choice but never choose the model or proposal.

## Gates and next actions

Require gains without lost candidate successes or new wrong selections within each case set.
Report any remaining older-model successes lost. A policy does not remove that release blocker by ignoring it.
Preserve all no-focus abstentions. Keep profile and group counts separate.
Do not tune thresholds on these cases. Do not train on these development captures.

If ring preference passes, prepare independent HCF-only verification and an observation-only integration proposal.
If fallback restores wrong selections, reject it and prioritize geometry-aware training inputs or preservation training.
If neither resolves the Standard regression, prepare B405-196 from training-group proposal errors, not evaluation errors.
The next training comparison needs a pinned training-error sampler, matched exposure, and the complete retained regression suite.

## Execution and evidence

T60 consumes a completed T57 report and its receipt. It verifies source hashes and replays both original decisions first.
It reuses saved scores. It performs no inference, capture, training, export, or runtime update.
Successful and invalid-policy paths pass through an isolated queue. The invalid policy fails with `focus_policy_unknown`.
Software qualification passes 34 focused tests.
The integrated offline Swift tests pass with the existing scratch build.
The 15 queued jobs retain 800 s and 100 MB limits. They are short cached diagnostics, not overnight work.
The background runner owns execution. Review results as a batch rather than polling individual jobs.

Local evidence: `reports/work/FOCUS-PIPELINE-POLICY/` and the `focus-policy-*` queue attempts.

## Completed batch decision

All 15 background jobs complete. No new execution failure remains in this batch.
The ring policy adds no losses or wrong selections across the 7 transfer sets.
Together with the isolated small-decoration result, it recovers 1 HCF selection while preserving tested Standard decisions.
The candidate still loses the older model's Standard diamond selection. The broad replacement gate therefore fails.
Keep ring preference as an HCF-only candidate for independent verification, not a released correction.

Reject the older-model fallback. It recovers the Standard diamond selection but adds 3 wrong selections.
Those errors occur on Standard small decoration and both profiles of the native row case.
Neither policy changes the 6 no-focus abstentions.

The next Standard correction is B405-196: train with measured proposal errors instead of arbitrary crop changes.
Maximum-mini-NUIAK must first pin training-only proposal/body matches and qualify the deterministic sampler.
The current T41 adapter consumes T37 reports, not T57 detector proposals. Do not pass incompatible reports through it.
Extend that adapter with a verified unchanged replay before defining geometry interventions on this new path.
Keep the inspected failures in development. Do not use their offsets to generate training examples.
Compare realistic errors with generic jitter at equal exposure, then run the complete retained preservation suite.
This preparation is not an executable training job yet. No ready-duration estimate exists for it.

## Next admitted batch: B405-204

T61 measures box size, center error, overlap, and paired score changes from verified T57 reports.
It marks cases where multiple controls match the same proposal. Those matches do not become reliable training labels.
The 8 approved jobs cover no-focus, tall controls, small decoration, diamond decoration, edge clearance, rows, tabs, and buttons.
Each job retains the 800 s and 100 MB diagnostic limits. These limits are not runtime estimates.
The adapter passes 37 focused tests with the related templates, including invalid scores and duplicate rows.
An isolated queue run completes before production admission. The detached runner handles the admitted batch.
Use these reports to choose which errors need a training-only sampler. They cannot prove that retraining improves selection.
