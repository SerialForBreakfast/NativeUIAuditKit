# FOCUS327: trained detail filters

## Decision

Reject the candidate as a replacement. The detail filters learn the authored task better, but native failures remain.
Keep TTR's current model. No export or promotion occurs.

| Check | FOCUS326 retained control | FOCUS327 |
| --- | ---: | ---: |
| New authored training pairs correct, 960 | 589 | 736 |
| Authored movements correct, 384 | 244 | 291 |
| Authored artwork-only pairs correct, 384 | 153 | 253 |
| Native-derived set correct, 640 | 589 | 592 |
| Native-derived false changes | 0 | 4 |
| Reversed native-derived set correct, 640 | 585 | 590 |
| Replay correct, 668 | 655 | 660 |
| Reversed replay correct, 668 | 649 | 651 |
| Global lighting correct, 226 | 226 | 226 |
| Left distractions correct, 226 | 132 | 155 |
| Left false changes | 72 | 64 |
| Center distractions correct, 226 | 78 | 83 |
| Center false changes | 136 | 136 |
| Tiny native changes correct, 4 | 0 | 0 |
| Placeholder movements correct, 8 | 6 | 6 |

The candidate gains 9 native-derived decisions and loses 6 against the retained control.
All 6 losses concern unchanged-focus content contrast in 2 training families. They become abstentions.
Another 4 previously uncertain content-contrast cases become false changes. The net gain of 3 hides these problems.
It also loses 1 replay success while gaining 6.
The candidate preserves all 8 identical tiny comparisons. Reversed tiny changes remain 0/4.
Placeholder arrival remains 14/16. The model abstains on the other 2 arrival pairs and 2 movement pairs.

## Separate training and evaluation results

| Native-derived role | Pairs / groups | Control correct | Candidate correct |
| --- | ---: | ---: | ---: |
| Training | 548 / 17 | 500 | 503 |
| Development | 40 / 10 | 37 | 37 |
| Previously inspected reserved groups | 52 / 2 | 52 | 52 |

All 40 development pairs have unchanged focus. The 52 reserved pairs include 34 focus changes and 18 unchanged pairs.
The 4 tiny forward cases remain a separate development check. Reversals do not add independent examples.
These results do not establish unseen-app performance. The reserved groups have already informed earlier investigations.
The overall gain occurs in training groups, not the separate native development or reserved groups.

Authored training correctness improves by 147/960 against the control. Authored false changes fall from 11 to 3.
Authored missed changes fall from 9 to 6. Authored abstentions fall from 351 to 215.
These cells share 3 artwork families. More correct training pairs do not establish independent generalization.

## What the experiment establishes

The retained filters limit fit on the authored task. Updating those filters improves that fit with identical images and settings.
This improvement does not fix the tiny native cases or remove conflicting content-contrast decisions.
It does not prove that more epochs, more generated images, or another output threshold will solve the problem.

The whole-frame scores strongly favor unchanged focus on the tiny cases.
The detail branch adds scores between 1.94 and 5.12. It needs additions between 11.67 and 15.72 to reach the changed threshold.
That probability threshold remains 0.85.
The total forward scores remain between -8.93 and -7.53 before the sigmoid function.
The branches still fail together despite improved authored learning. Do not select a new threshold from these inspected cases.

## Execution and verification

The [registered plan](Plans/Focus327.md) reuses FOCUS326's independent images and retained control.
No images are regenerated. Original training views, labels, weights, and evaluation roles remain unchanged.
Preparation verifies exact feature agreement with the retained cache. Maximum feature error is 0.
The trainer uses indexed auxiliary inputs to avoid repeated image copies. Tests verify exact agreement with expanded inputs.

The initial probe uses 32 label-balanced training examples. It is a gradient check, not balanced coverage of every effect setting.
All detail layers receive finite, nonzero gradients. Probe loss falls from 0.67475 to 0.46768.
The probe weights are discarded. The full candidate starts again from FOCUS325-average.
The full training run includes every retained effect cell.

The candidate uses 30 epochs, seed 42, batch size 16, learning rate 0.0001, and auxiliary weight 0.25.
Only 10 detail and correction tensors change. Whole-frame and geometry weights remain unchanged.
Checkpoint reload produces identical scores. Thresholds remain 0.15 and 0.85; selection uses the fixed last checkpoint.

- Preparation: 121.10 s.
- Full training: 711.01 s, with 3,420 updates.
- Preparation, probe, training, and complete evaluation: 1,007.52 s.
- Peak process memory: 5,681,250,304 bytes, below 8 GiB.
- Focused tests: 79 pass in 1.607 s.
- Native SwiftPM build: passes in 0.33 s.
- Offline tests: 14 XCTest tests and 173 serial Swift Testing tests pass.
- Swift Testing duration: 54.303 s.

The default Swift build selects a signing path and fails on existing resource attributes.
The explicit native SwiftPM path passes without signing repair or service changes. Both logs remain preserved.
The full Python entrypoint and comparison report finish with exit code 0.

## Evidence and outcomes

Ignored evidence remains in `reports/work/FOCUS-327/`. It includes registration, exact source copies, view hashes, gradient checks, checkpoints, and case comparisons.
The report compares DTM085, FOCUS313, FOCUS319–326, and both FOCUS325 pooling candidates.
The candidate hash is `d6328fe53e30478fb6bcdda44d50ce4d382f41bc9ee6d44b1f1de1c0d17f89df`.
The retained control hash is `7fa1e25bc23f214d77c74748134376a9a7a7590702cc63a0b5d7284193e0aaf7`.

- Software: verified.
- Data: retained training roles only; no new admission or changed evaluation membership.
- TTR integration: not assessed by this experiment.
- Model requirements: failed; candidate retained for diagnosis only.

The [TTR feedback review](Focus327TTRFeedback.md) identifies usable features, missing chat delivery, and the current evaluation gap.
New TTR messages are not visible through this client. That gap does not block this completed experiment.
The coordinator stores the result at cursor 162 without confirmed forwarding.
The SMB fallback publishes `nuiak/responses/nuiak-focus327-result-01.json`. Exact size, hash, and parsed readback pass.
Sillycon-TTR acknowledgment remains unconfirmed. The message asks TTR to keep its current model and identify the missing feature updates.

## Next substantial tranche

FOCUS328 should distinguish growth and boundary changes from content-contrast changes before another large generation batch.
Use the retained FOCUS327 candidate and frozen-filter control. Reuse exact images and previous-success reports.
First, compare local edge changes, brightness changes, and the two branch contributions on training examples.
Use matched training-only perturbations to test which signal causes the conflicting decisions. Preserve their original group assignments.
Do not use inspected tiny cases to choose parameters or create training derivatives.
Then test 1 justified contrast-robust detail representation if the training-only diagnostic supports it.
Register the representation, inputs, fixed 30-epoch budget, and unchanged thresholds before training.
Keep whole-frame and geometry weights frozen. Reuse the original trainer and the complete regression report.
Keep the 2 GiB output, 8 GiB memory, and 2-thread limits. Do not launch an automatic sweep.
Acceptance requires fewer content-contrast errors and improved native decisions without losing previous successes.
If the diagnostic does not support a correction, report that result instead of running another unchanged fit.

In parallel, identify TTR's exact new renderer parameters and source revision through the existing request.
Use those capabilities for a bounded, measured comparison after their availability is verified.
New TTR implementation proposals still need human approval. Do not request another build or broad corpus without a specific gap.
