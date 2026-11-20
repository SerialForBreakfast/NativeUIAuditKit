# RESET604: implementation audit and handoff
Maximum-mini-NUIAK · 2026-11-11 · Review window: November 9–11, through the November 11 working-tree inspection.

**Decision: keep Standard. Do not start either proposed 100-epoch fit on the current manifests.** The team produced real captures, usable development evidence, and a working training probe. It has not demonstrated improved accuracy in the shipping consumer. Two inexpensive corrections can make the next training comparison informative.

## What the last 2 days produced

I compared the supplied work log and [recovery plan](Plans/Reset604.md) with the active USB checkout at Git HEAD `b4661168e`. The checkout includes working-tree changes. Use the [dated SHA-256 list](../reports/work/RESET604/audit-20261111.sha256) to identify the files reviewed. The commit alone does not identify this implementation.

| Claim | Evidence and verdict |
|---|---|
| Fixture capture completed | The [state file](../dataset/tvos_captures/reset604/batch-v1/runner-state.json) records 319 recipe attempts across 21 chunks, 17 rejections and 1,287 accepted rows. I counted 2,574 PNG files on disk. The index has 340 recipes. Do not describe the 21 omitted recipes as executed. A PNG count does not verify settlement or label quality. |
| D1 and F1 use 6,700 images each | Verified from the 2 [membership files](../reports/work/RESET604/membership). Both list identical image references in identical order. D1 has 6,700 distinct declared image digests: 6,194 training and 506 calibration. These are shared inputs, not 13,400 independent images. |
| No overlap | The 454 held-out rows share no recorded group IDs or encoded-image hashes with D1. The ingest check covers named manifests and exact hashes. It does not establish separation by near-duplicate, asset, layout ancestry, or previously viewed flow. |
| The one-epoch probe ran | The [receipt](../reports/work/RESET604/runs/d1-e1-probe/train-receipt.json) and [epoch record](../reports/work/RESET604/runs/d1-e1-probe/detector/results.csv) agree on a one-epoch run. The epoch took 292.817 s. The receipt refers to 5,371 training images and a different manifest hash. It does not validate the current 6,194-image training set. |
| 100 tests passed | I reran all 13 named Python test modules: **100 passed in 7.752 s**. This reproduces the test count. It does not verify annotation truth, a fresh model fit, actual consumer parity, or capture identity. I did not repeat the Swift build. The original agent did not claim to run Swift tests. |
| The sealed benchmark is nearly complete | The [plan](../dataset/real_apps/tvbench-v1/sealed-plan.json) records 98 review candidates under 6 source labels. It does not establish 98 accepted independent screens or 6 verified apps. The 42 development screens are separate. Do not add the counts and report 140 evaluated screens. |

I rehashed all 42 development screenshots and 42 normalized label files against the [development manifest](../dataset/real_apps/tvbench-v1/dev-manifest.json). All 84 matched. I recounted saved outcomes; I did not rerun inference, authenticate each human decision, or rehash the entire training corpus. I did not open sealed images or per-frame sealed results. This audit identifies incorrect or unsupported claims. It does not establish intent.

## What the saved results say

All 3 development reports use the same manifest fingerprint. They cover 42 screens across 11 recorded app/flow combinations. They do not establish 42 independent flows. Of the 438 scored controls, 437 come from NewsTV, 1 from Photo Guessing Game, and none from Swiftfin. Focus coverage is broader than box coverage.

| Offline detector + FocusRing | Controls matched at IoU 0.50 | Custom AP50 | Correct / wrong / abstained on 36 focused screens | False selections on 6 known no-focus screens |
|---|---:|---:|---:|---:|
| [Shipped detector](../reports/work/RESET604/tvbench-dev-shipped-focus.json) | 120/438 | 0.4684 | 1 / 34 / 1 | 6/6 |
| [R5](../reports/work/RESET604/tvbench-dev-r5-focus.json) | 436/438 | 0.9553 | 0 / 36 / 0 | 6/6 |
| [D1 one-epoch probe](../reports/work/RESET604/tvbench-dev-d1-e1-probe-focus.json) | 378/438 | 0.7899 | 4 / 31 / 1 | 6/6 |

R5 recovered many NewsTV detections but lost the only matched Photo Guessing Game control. It also lost the shipped detector's only correct focus selection. D1 retained that focus success and recovered 3 other screens. Neither candidate fixed a known no-focus screen. These are paired development observations. Missing control annotations in Swiftfin do not imply zero controls on screen.

The AP calculation used 23 eligible screens. The saved reports say the official evaluator was unavailable. The numbers above come from the custom fallback. They are neither official COCO AP nor percentages of screenshots understood. The [scoreboard](Scoreboard.md) needs a status correction: development reports exist; independent qualification remains unestablished. Keep provisional values out of accepted metrics until Joe reviews the evidence.

## Corrections before costly training

1. **Correct ambiguous F1 targets.** I counted 5,576 images with 1 focused box, 878 with none, and **246 with 2 distinct focused boxes**. The last group includes 217 training and 29 calibration images. All 246 come from generator sources. The [converter](../scripts/ttr_detector_ingest604.py) infers generator focus from an ID suffix. Two target boxes contradict a single-winner objective. A missing target does not establish no focus. Use observed focus, known no-focus, or unknown. Exclude ambiguous focus supervision until resolved. Preserve eligible detector labels on those images.
2. **Correct D1 label completeness.** All 580 native sweep rows say `labelsComplete=True`, although the converter explicitly calls them partial 4-target annotations. The [Fixture pilot](../reports/work/RESET604/fixture-pilot.md) also documents partial instrumentation. Missing in-scope controls can become background during ordinary detector training. Check coverage against the 12-role taxonomy. Exclude partial scenes from the full-frame loss unless the trainer demonstrably ignores unreviewed regions. Keep verified positives available for focus comparisons.
3. **Restore app and flow identity before human review.** The [Office importer](../scripts/tvbench_sealed_prep604.py) assigns every imported image to Kanopy and 1 flow. The [prior Office review](NightlyReview20261108.md) identified 66 settled Kanopy frames. The new plan assigns 76 Office candidates to Kanopy. Pixel differences cannot establish app identity or settlement. Join each image hash to its command, endpoint, app, and route. Quarantine missing joins. Keep previously inspected Office and RC561 cases in development unless a distinct, unexposed flow can be proven. Capture fresh routes for qualification. Adding 2 screenshots alone cannot fix this.
4. **Preserve what the reviewer actually confirmed.** The [normalizer](../scripts/tvbench_dev_manifest604.py) converts unflagged unknown visibility to visible and appends reviewer confirmation. It drops wrong-box and wrong-class objects. In the 2 source review directories, 437 unflagged objects had unknown visibility and no explicit confirmation string. This does not prove the boxes wrong. Document whether accepting the frame confirmed each unchanged box. Preserve source flags, corrections, unresolved counts, and completeness. Do not treat a dropped unresolved object as evidence of complete coverage.
5. **Prove consumer parity.** The [Python scorer](../scripts/tvbench.py) offers every non-focus detection above threshold to FocusRing. The [Swift consumer](../Sources/NativeUIAuditKit/Detection/NativeUIDetectionRequest.swift) first filters by focusable type and records crop or prediction failure. Compare both paths on retained development screens. Require identical input and crop hashes, eligible proposals, score thresholds, winners, abstentions and explicit failures. Account for every submitted crop. Record both model hashes, runtime revision and timing. Treat the existing reports as offline measurements until this passes.
6. **Make the metric and inputs reproducible.** Report official and custom AP in separate fields. The CLI uses a truth-value fallback that can discard a valid official AP of zero. Test zero, missing evaluator, missing output, partial labels, and wrong-class matches. Verify source hashes at scoring time. Key cached inputs by preprocessing configuration. Freeze image, label, recipe, model and evaluator versions. Fail admission on missing exclusion manifests or group conflicts. Check both exact hashes and related flows, layouts and assets.
7. **Make attempts and budgets auditable.** The [batch runner](../scripts/fixture_batch_runner604.py) uses the start offset as its completed-chunk key. Changing the skip list or batch size can silently reuse an old completion. Bind completion to the ordered recipe IDs and hashes. Preserve skipped and rejected IDs separately. Write immutable memberships per arm and run. The probe's historical membership path now contains different bytes. The [trainer](../scripts/train_detector604.py) records a 43,200 s policy value; that field does not enforce a timeout. Verify the actual runner limit and effective optimizer settings before dispatch.

## Next tranche: 2 independent tracks, 1 decision per experiment

| Owner and first action | Pass condition | Next decision |
|---|---|---|
| Maximum-mini-NUIAK: repair the development scorer and reconcile Maximum-mini-TTR replay. | Match proposals, eligible crops and outcomes on the same pixels. Include a wrong pick, abstention, and known no-focus case. Record any execution failure separately. | If paths disagree, fix the first divergent stage. If they agree, use the consumer to compare candidates. |
| Maximum-mini-NUIAK: rebuild D1/F1 memberships as explicit successors. | Audit source coverage, all competing focus boxes, unknown states, class support, group separation and excluded rows. Retain originals. | Admit D1 only with valid detector supervision. Admit F1 only with valid single-focus or known no-focus supervision. |
| Maximum-mini-NUIAK and Joe: repair the real-app reference in parallel. | Verify app and route before opening review. Blind Joe to predictions. Count accepted screens, distinct flows, complete objects, known no-focus and uncovered classes per app. | Prioritize a second app with complete control labels. Freeze fresh qualification flows before examining predictions. Do not use additional NewsTV controls to disguise missing app coverage. |
| Maximum-mini-NUIAK: run 1 matched detector experiment through the detached runner after the first 2 gates pass. | Compare matched control and corrected native-data treatment. Fix initialization, taxonomy, example count, schedule, seed pair, thresholds and retention panels. Declare primary metric and stop rule before dispatch. | Continue only if gains repeat across seeds and extend beyond NewsTV. Report lost controls and false positives per flow. Stop if only synthetic recall improves. |
| Maximum-mini-NUIAK: compare focus choices using identical detector proposals and supplied reference boxes. | Report recovered and lost selections, abstentions, and false selections on known no-focus separately. Preserve previous successes in the comparison. | If supplied boxes help, inspect proposal coverage or cropping. If both paths fail, test a comparative selector with an explicit no-focus outcome. |

Estimate: 9.4 h per 100-epoch fit is a linear extrapolation from 1 smaller epoch. It is not a measured runtime. Four fits at that rate would take about 37.5 h before export and scoring. Use a noise estimate from the actual recipe. A different R5 training run cannot establish D1 or F1 variability. Group uncertainty by whole flows within apps. Pair candidates on the same screens. Do not promote from this development set.

## Reporting contract for the next agent

- Report separately: prepared inputs, completed execution, independently checked evidence, and Joe's decision.
- For each result, link an immutable manifest, model fingerprints, evaluator identity, and matched control. Give counts by app and flow.
- List failed executions, exclusions, unknown labels, lost previous successes, and new wrong selections. Preserve unsuccessful attempts.
- Publish provisional findings for review. Only Joe approves a headline metric or a model promotion. Routine experiments need no additional metric approval.
- Keep the separately paused iOS, HCF and temporal tracks unchanged under [the active task list](../Tasks.md). This audit provides no new evidence about those models.

**First deliverable:** the corrected memberships and a retained-frame parity report. They make the next training result interpretable without exposing the qualification set.
