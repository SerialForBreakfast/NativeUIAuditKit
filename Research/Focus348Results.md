# FOCUS348 — large appearance gain, unacceptable movement losses

## Decision

Reject both candidates as replacements. Keep FOCUS329 unchanged.
Gamma augmentation improves the target condition, but loses previous successes.
The unchanged-image control also loses previous successes outside the original authored set.
Preserve both checkpoints and all comparison evidence for diagnosis.

## Completed training

Both arms finish 10 epochs from the same FOCUS329 checkpoint.
Both use seed 42, batch 16, learning rate 0.0001, and 2 CPU threads.
Both preserve 1,820 original views and their exact detail crop hashes.
Both reuse 1,200 approved authored pairs through the same auxiliary schedule.
Only the candidate transforms auxiliary source images with gamma 1.5.
This changes crop selection for 288/1,200 pairs. Original primary views remain unchanged.
Both train only existing detail and correction layers. Frozen layers remain unchanged.
Both saved checkpoints reproduce their in-memory predictions exactly.

| Arm | Training job, including preparation | Training epochs |
|---|---:|---:|
| Unchanged-image control | 456.5 s | 10 |
| Gamma candidate | 533.6 s | 10 |

## Target comparison

These counts use 1,392 authored pairs after the same source gamma transformation.
There are 464 movement pairs and 928 stable-focus pairs.
The corpus contains training-related groups. These are not independent final evaluation cases.

| Measurement | Equal-budget control | Gamma candidate |
|---|---:|---:|
| Correct decisions | 577/1,392 | 1,099/1,392 |
| Correct movement detections | 444/464 | 372/464 |
| Correct stable decisions | 133/928 | 727/928 |
| False focus changes | 587 | 26 |
| Movement reported as stable | 0 | 25 |
| Abstentions | 228 | 242 |

The candidate gains 594 correct stable decisions, but loses 72 correct movement decisions compared with the control.
The net gain is 522 correct decisions. The movement loss prevents acceptance.
Gamma augmentation does not recover any of the 8 native corner movements.
On transformed native pairs, the control abstains on 4 movements and misses 4.
The candidate reports all 8 movements as stable. Both recognize the 8 stable native pairs.
Native app/build matching remains unresolved. These native cases remain development-only.

## Previous successes

Each entry shows correct decisions and lost previous successes relative to FOCUS329.
Do not sum related frame orders as independent evidence.

| Retained set | Control correct / losses | Gamma correct / losses |
|---|---:|---:|
| Original authored and native development pairs | 1,053/1,408; 0 lost | 1,154/1,408; 41 lost |
| Native-derived forward | 592/640; 2 lost | 592/640; 6 lost |
| Native-derived reversed | 598/640; 0 lost | 593/640; 4 lost |
| Replay forward | 660/668; 0 lost | 662/668; 1 lost |
| Replay reversed | 651/668; 1 lost | 656/668; 1 lost |
| Global disturbance | 226/226; 0 lost | 226/226; 0 lost |
| Left disturbance | 155/226; 0 lost | 163/226; 0 lost |
| Center disturbance | 84/226; 1 lost | 90/226; 0 lost |
| Identical-artwork neighbors | 32/32; 0 lost | 32/32; 0 lost |
| Placeholder arrival | 14/16; 0 lost | 12/16; 2 lost |
| Placeholder movement | 6/8; 0 lost | 6/8; 0 lost |

The 2 native forward control losses become abstentions in existing training families.
Their probabilities move from about 0.113 to 0.205. This illustrates that a soft preservation loss does not guarantee preservation.
The gamma candidate loses 37 original authored movement successes and 4 artwork-only successes.

## Queue and verification

Both training jobs and 10 priority comparison jobs complete.
The remaining 25 jobs start in detached automatic mode.
They cover 19 remaining appearance conditions and 6 jobs for retained disturbance strengths and frame orders.
Their results remain pending at this checkpoint. The rejection decision does not depend on their success.
Run `scripts/report_appearance348.py` after all 35 comparison jobs complete.
The reporter refuses a full report when required comparisons are missing.
The current core report is `reports/work/FOCUS-348/core-results.json`.
Raw predictions, labels, input hashes, settings, and model hashes remain with each queue attempt.

At the final execution check, 16 comparison jobs complete and 19 remain ready for detached execution.
The actual neighbor, placeholder, and disturbance-strength entrypoints all complete successfully.
Automatic mode resumes without errors. Every remaining job passes its input hash checks.
The measured window from the first training launch is 28.5 min, excluding initial inspection and planning.
The initial estimate is 30–60 min for foreground work. Remaining diagnostics continue separately.

Ninety-four focused tests pass, followed by 13 experiment tests that include the additional training invariant check.
The offline Swift build and 187 Swift tests pass.
Initial sandbox failures remain preserved. Scoped retries pass without service or signing changes.
No Git writes, production changes, exports, or native captures occur in this tranche.

## Next decision

Finish the remaining comparisons before another fit.
Measure positive-versus-negative training conflicts on the exact gamma pairs.
Test whether class-balanced replay or explicit positive-margin preservation can retain the false-change reduction without losing movement detection.
Do not treat this proposal as a proven correction or start an automatic sweep.
Continue the separate native size and LUMA compatibility work. Appearance augmentation does not solve native transfer.
See [queue readiness](Focus348QueueReview.md) for exact prerequisites and the received LUMA v2 contract.
# Final comparison update

All 35 comparison jobs finish. The report contains 56 condition sets.
The unchanged-image control loses 8 retained successful decisions. Gamma loses 56.
These totals include related frame orders and nuisance strengths. They are not independent trials.
Gamma retains the large target false-change reduction, but its movement losses remain unacceptable.
Keep FOCUS329 unchanged. FOCUS349 tests movement influence without changing original crops or thresholds.
Complete evidence: `reports/work/FOCUS-348/results.json`.
