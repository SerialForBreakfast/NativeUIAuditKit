# RECONCILE407 — successor review and useful comparisons

Owner: Maximum-mini-NUIAK. Date: 2026-10-14.

## Decisions

Withdraw 22 obsolete execution requests. Reuse 14 completed successors.
Keep every specification and attempt unchanged.
The [mapping](../Experiments/reconciliation407.json) identifies every old job and its replacement.
The generated evidence is `reports/work/RECONCILE407/reconciliation.json`.
It verifies result identities and every recorded output hash.
Tasks.md owns closure. Preserved queue records can still display as blocked.

| Original group | Old jobs | Completed replacements | Finding |
| --- | ---: | ---: | --- |
| HCF375D | 3 | 1 | HCF388 completes the fixed 30-epoch detector |
| HCF376 | 9 | 3 | Migrated controls complete each original comparison |
| HCF402 | 6 | 6 | Corrected reports reuse the same captures and mapping |
| TEMPLATE395 | 4 | 4 | Qualified successors replace stale contracts |

Training initialization, membership, and epochs match in all 12 training records.
The 6 HCF402 comparisons retain identical template inputs and parameters.
Two TEMPLATE395 inputs change paths. Their content hashes remain identical.
The other template inputs match exactly.
These facts establish replacement coverage. They do not establish model acceptance.

## Approved control comparison

Reuse these existing immutable jobs:

1. `program384-d1-train43-v2`.
2. `program384-d1-train44-v2`.
3. `program384-d1-evaluate43-v2`.
4. `program384-d1-evaluate44-v2`.
5. `program384-d1-report-v2`.

The maintainer approves both controls on 2026-10-14.
Fresh approval checks pass. Older approval records had stale code hashes and are replaced through explicit revocation and approval.
The downstream comparisons also pass preparation checks and receive scoped approval.
No duplicate specifications are registered.
The detached runner resolves the training dependencies before evaluation.

Change only the training seed. Keep initialization, membership, original views, 30 epochs, and thresholds 0.15/0.85 fixed.
Reuse the completed seed-42 evaluation. Compare the same 1,408 retained views.
Report training and development separately. Measure stable successes, varied cases, and losses for each seed.
Keep model acceptance false. Variation can justify a separate proposal; it does not change the production gate.

Each control permits 1,800 s and 2 GiB. The total training ceiling is 60 min.
The retained seed-42 evaluation takes 14.04 s. Similar evaluation time is an estimate, not a guarantee.
The complete cycle permits 5 jobs. Output ceilings come from the existing specifications.

## HCF diagnosis

The completed T40 diagnostic covers 74 frames in 10 inspected development groups.
Each profile has 36 focused frames and 1 no-focus frame.

| HCF input | Correct focused selections | Focused misses | Correct no-focus abstentions |
| --- | ---: | ---: | ---: |
| Known boxes | 35 | 1 | 1 |
| Raw proposals | 3 | 33 | 1 |
| Mapped proposals | 5 | 31 | 1 |

Twenty-eight focused HCF frames have no proposal. Three mapped frames have proposals but scores below 0.85.
The mapping gains 3 large-control cases and loses 1 tall-control case.
For that tall control, overlap increases from 0.554646 to 0.974774.
Its score decreases from 0.900092 to 0.419631. The known-box score is 0.965420.
This separates geometry overlap from classification reliability. It does not identify the causal pixel change.
Standard known boxes select all 36 focused controls correctly. The HCF ring method provides no Standard proposals.
Keep this optional method separate from Standard detection.

## Remaining comparisons and exact blockers

### B405-002 — tall-control input sensitivity

Question: does small box displacement explain the mapped score loss, or does removed surrounding context explain it?
Use all 74 retained frames and the exact T40 source reports.
Keep source images, labels, classifier, threshold, and preprocessing fixed.
Compare the known body, mapped body, and raw proposal first.
Then isolate integer rounding and translation while preserving box size.
Test surrounding context separately. Do not combine displacement and context in one correction.
Measure scores, decisions, crop hashes, target recovery, and lost previous successes.
Accept a correction only when it recovers the target and preserves previous successes.
If neither factor explains the loss, inspect actual resized inputs and pixel sensitivity before training.
Blocker: Maximum-mini-NUIAK needs a qualified scored-intervention variant with explicit candidate correspondence.
T37 has no intervention parameter. T40 diagnoses cached scores only.
Allow 800 s and 100 MB per diagnostic after the variant passes qualification.
Update 2026-10-15 (INTERVENTION410): T41 qualifies on the tall-control pair through an isolated queue. A `none` arm reproduces the cached scores.
The 9 jobs in `Research/Experiments/b405-002-interventions.json` are approved. Each job changes 1 factor against its matched `none` arm.

### B405-104 — missing proposal coverage across native families

Question: can detector proposals recover cases where the HCF ring method returns no box?
Use the same 74 frames. Keep weights, threshold, grouping, and selection rules fixed.
Compare detector-only proposals with detector-first, optional HCF fallback.
Measure eligible-box recall, correct selection, false selection, and lost previous successes.
Accept added coverage only when matched retained decisions show no regression.
If the detector also misses these bodies, classify its geometry errors before selecting new training data.
Blocker: Maximum-mini-NUIAK needs detector outputs with candidate scores and boxes for these exact frames.
Existing HCF400 fallback reports use different inputs. They cannot establish this comparison.
Reuse answered B405-006 as the baseline method. Do not reopen its completed retained-data comparison.
Allow 800 s and 100 MB per diagnostic after the native detector variant qualifies.

### Standard artwork counterpart

Sillycon-TTR supplies 1 new Standard pair and repeats 1 retained HCF pair.
The archive has 31,843,235 bytes. Its SHA256 matches the published transfer manifest.
Safe extraction produces 39 entries and 36,786,593 bytes.
The archive includes an empty root directory marker. Excluding only that marker allows existing safety checks to pass.
The receiver receipt is published and read back successfully.
Sillycon-TTR owns shared source cleanup.

Keep the calibration role and shared lineage. Do not count the duplicate HCF pair as new evidence.
Different producer revisions prevent attribution of all pixel changes to the accessibility profile.
Native telemetry supports focus identity. It does not independently prove raster bounds.
The next comparison needs pixel qualification and explicit version-confound reporting before model use.

## Validation

The reconciliation helper verifies completed replacements without mutating queue files.
Tests reject altered outputs, altered specifications, failed successors, and duplicate sources.
Tests retain control differences for review instead of claiming equivalence automatically.
Focused checks cover the scientific catalog, compiler, and seed comparison.
Record final validation and runtime state in `reports/work/RECONCILE407/status.json`.

## Next substantial tranche

Review the 3-seed comparison as one batch. Identify stable gains and seed-dependent losses.
Qualify the tall-control intervention variant and native detector proposals on retained frames.
Use those results to select one proposal or input correction with matched regression evidence.
Keep additional training conditional on that diagnosis.
