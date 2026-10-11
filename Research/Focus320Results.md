# FOCUS320: conflicting training signals

Owner: Maximum-mini-NUIAK. The diagnostic, fixed 30-epoch candidate, and complete model comparison finish.
Reject the candidate. Some authored decisions improve, but native regressions remain.

## Results

| Measure | FOCUS313 control | FOCUS319 | FOCUS320 |
| --- | ---: | ---: | ---: |
| Native correct / 640 | 598 | 581 | 581 |
| Native training correct / 548 | 514 | 491 | 497 |
| Inspected development correct / 40 | 33 | 38 | 32 |
| Inspected reserved correct / 52 | 51 | 52 | 52 |
| Replay correct / 668 | 668 | 646 | 665 |
| Reversed native correct / 640 | 602 | 579 | 582 |
| Lighting correct / 226 | 226 | 226 | 226 |
| Left false changes / 226 | 82 | 53 | 78 |
| Center false changes / 226 | 99 | 136 | 105 |
| Center correct / 226 | 82 | 85 | 64 |
| Tiny changes correct / 4 | 0 | 0 | 0 |
| Placeholder movements correct / 8 | 2 | 8 | 4 |

FOCUS320 loses 19 native successes and gains 2 against FOCUS313. Eighteen losses occur in the 2 known training families.
The other loss occurs in the inspected dark artwork condition. Native abstentions increase from 40 to 57.
Replay loses 3 successes. Reversed native comparisons lose 21 and gain 1.
Center comparisons lose 30 correct decisions and gain 12. Fewer false changes than FOCUS319 do not establish better overall accuracy.
Nine of 24 strength/order checks lose successes against DTM085. Do not promote this candidate or change deployment thresholds.

Authored movement training correctness stays at 40/80, versus 74/80 for FOCUS319.
Authored artwork-only correctness rises from 8/80 to 18/80, versus 63/80 for FOCUS319. All 80 identical comparisons remain correct.
The correction reduces some disruption but also removes much of the authored learning benefit.
This is not a successful native improvement.

## Measured cause

The audit uses all 1,820 original training views and all 240 authored pairs with their actual exposure weights.
It checks fresh initialization, the FOCUS313 control, and the rejected FOCUS319 candidate.
It computes gradients only for the trainable detail branch. Evaluation cases do not select the correction.

| Checkpoint | Original gradient norm | Authored gradient norm before 0.25 weight | Combined direction cosine |
| --- | ---: | ---: | ---: |
| Fresh initialization | 0.05755 | 22.70160 | 0.5284 |
| FOCUS313 | 0.06303 | 34.97163 | 0.1801 |
| FOCUS319 | 3.54372 | 17.09991 | -0.9085 |

The cosine compares the original gradient with the combined authored gradient. A negative value means opposing directions.
At initialization, the weighted authored gradient is about 99 times larger. At FOCUS313, it is about 139 times larger.
Thus, a loss coefficient of 0.25 does not imply a small training influence.
At FOCUS319, artwork-only gradients oppose changed-focus examples in both affected native families: cosines -0.8142 and -0.8113.
Authored movements instead oppose unchanged examples in those families. The pooled gradient hides these condition-level differences.
These measurements describe 3 checkpoints. They do not prove every update caused the observed regressions.
The diagnostic takes 126.88 s.

## Selected correction

Keep the original gradient. Remove the authored component that opposes it.
Cap the remaining authored norm at the original norm. Then apply the existing 0.25 coefficient.
If the original gradient is zero, the added gradient is zero.
This is 1 combined correction. The experiment cannot assign separate benefits to projection and magnitude control.
Adam uses past updates and scales coordinates separately. The raw gradient constraint does not guarantee preserved model decisions.

Keep the FOCUS319 architecture, original views, weights, detail crops, initializer, auxiliary schedule, and number of updates unchanged.
Train for 30 epochs with seed 42, batch 16, learning rate 0.0001, and 2 CPU threads.
Select the fixed last checkpoint. Keep thresholds 0.15/0.85. Preserve inspected reserved cases outside training.
No new images, capture, downloads, export, or production changes occur.

The run performs 3,420 updates in 736.83 s. It projects opposing gradients in 1,975 updates and caps magnitude in 3,419.
Preparation, training, and primary evaluation take 979.21 s. The audit takes another 126.88 s.
Sampled process memory stays below 4 GiB. This is not an exact peak measurement.
The final checkpoint reloads with exact score parity. An independent check confirms all 24 frozen tensors remain unchanged.

## What the failure tells us

At epoch 10, original loss is 0.0207, versus 0.2438 for FOCUS319. Yet final native correctness does not improve.
Low average training loss is not enough to preserve individual decisions or margins.
The tiny cases receive positive added scores of 4.58–5.54. They require 11.67–15.72 to overcome the frozen classifier and reach threshold.
The detail branch therefore detects useful evidence but does not change these decisions correctly.
This does not prove a fusion change will work. It supplies a more specific hypothesis than another volume increase.

Next, test how the classifier combines whole-frame and detail scores using retained training cases.
Measure margins by group, then compare 1 bounded combination rule against the unchanged control.
Keep native development checks, nuisance cases, and every previous-success check fixed. Do not tune on inspected reserved cases.
Do not repeat the same projection experiment or start a larger authored corpus without evidence of transfer.

## Evidence and limits

Raw evidence stays under `reports/work/FOCUS-320/`.
`registration.json` records gradient groups, input hashes, models, and measured training membership.
`diagnostic.json` records all condition comparisons. The training registration records the exact correction and source hashes.
Authored labels remain authored labels. Native and inspected reserved results retain their existing scope.
The test does not establish physical-device or unseen-app performance.

All 45 focused Python tests pass in 1.09 s. They check projection, magnitude limits, frozen weights, deterministic updates, and unchanged default behavior.
The actual report command exposes a relative-path defect. The corrected command accepts project-relative paths and rejects folders outside report storage.
The failed report log remains available. The repaired report completes without another model fit.
The final offline build passes in 4.19 s. All 14 XCTest tests and 173 serial Swift Testing tests pass after the report repair.
Swift Testing takes 52.019 s. The tests use the native SwiftPM engine and resident dependencies.
Logs stay under `.build/focus320-*`. No system service or dependency changes occur.

Candidate SHA-256: `8fe42cecc8ae1e156d8a3411ae2782e297c9ce8dba42c5c6a1245cec8cdb211a`.
Comparison SHA-256: `50e2db59e6fac1ca79edec2ed10e3c41ff8238c9850ae280e0b57c2fc253474e`.

## Coordination

The configured coordinator endpoint refuses the connection after scoped network approval.
The SMB fallback publishes `nuiak/responses/nuiak-focus320-start-01.json` with exact readback.
The message has 1,003 bytes and SHA-256 `6fa528d40723091fe78c92f19556282e06e430339a1408d02c492e0b068ff598`.
Sillycon-TTR acknowledgment remains unconfirmed. The message does not request a new worker assignment.

The result also passes exact SMB readback at `nuiak/responses/nuiak-focus320-result-01.json`.
It has 1,620 bytes and SHA-256 `510a069057e27a21f99903f3e2ab41a2c3f1646fe35d8df8cbfc04a85f4af298`.
This proves publication, not peer reading or acceptance. No new artifact transfer is required for this advisory result.

| Outcome | State |
| --- | --- |
| Software verification | Passed: focused tests, real report command, offline build, and serial Swift tests |
| Data eligibility | Unchanged: admitted original training and reviewed authored data; existing evaluation exclusions remain |
| Integration | Local training and evaluation pass; new native or Apple model integration is not assessed |
| Model acceptance | Failed: previous successes regress and tiny changes remain undetected |
