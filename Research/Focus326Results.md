# FOCUS326: independent size, effect width, and contrast

## Decision

Reject both candidates. Neither preserves previous successes or detects the 4 tiny native changes.
Independent effects help relative to the coupled control, but do not improve the model enough for TTR.
Keep the current TTR model. No export or promotion occurs.

| Check | FOCUS325-average | Coupled effects | Independent effects |
| --- | ---: | ---: | ---: |
| Native correct, 640 pairs | 588 | 589 | 589 |
| Reversed native correct, 640 pairs | 580 | 584 | 585 |
| Replay correct, 668 pairs | 649 | 654 | 655 |
| Reversed replay correct, 668 pairs | 643 | 648 | 649 |
| Global changes correct, 226 pairs | 226 | 226 | 226 |
| Left distractions correct, 226 pairs | 155 | 54 | 132 |
| Left false changes | 64 | 73 | 72 |
| Center distractions correct, 226 pairs | 81 | 76 | 78 |
| Center false changes | 140 | 138 | 136 |
| Tiny changes correct, 4 pairs | 0 | 0 | 0 |
| Placeholder movements correct, 8 pairs | 8 | 6 | 6 |

Both candidates gain 9 native decisions and lose 8. Their net gain of 1 hides those losses.
The independent candidate loses 23 previous left-distraction successes. The coupled control loses 101.
Neither introduces a false change in the native set. Both increase false changes on left distractions.
Both preserve all 8 identical tiny negatives. Both miss all 8 forward/reversed tiny changes.
Native totals include training and previously inspected evaluation groups. They are not independent deployment accuracy.

The coupled arm improves its new authored training decisions from 328/960 to 409/960.
The independent arm improves its new authored training decisions from 361/960 to 589/960.
Those training totals use different images. They do not form a shared evaluation set.
The independent candidate still abstains on 351 training pairs, misses 9 changes, and makes 11 false changes.
The frozen visual features and trained projection do not adequately fit even this bounded authored task.
More synthetic volume alone is not justified by these results.

## Scope

Maximum-mini-NUIAK tests a controlled change to authored training data.
The existing local TTR script uses fixed effect constants. NUIAK changes no TTR source or runtime.
The NUIAK compositor reuses 3 approved artwork families and their training ancestry.
It renders 2 matched arms with 960 pairs each. Each arm contains 192 scenes.
There are 1,440 distinct ordered pairs across both arms. Shared scenes and artwork are not independent evaluation evidence.
These are sparse authored cards, not native UI captures or complete real-app screens.

## Independent controls

Body widths are 3 and 6 pixels after whole-frame encoding. Source widths are 30 and 60 pixels.
Border widths are 1 and 3 encoded pixels. Contrasts are 0.25 and 0.75.
The generator crosses these settings with 4 corners, 2 separations, and 3 artwork families.
Separations are 32 and 96 encoded pixels. Focus growth stays at 1.14.
Each scene supplies movement, unchanged-focus artwork changes, and identical frames. Nonidentical pairs include reversed order.
The coupled arm multiplies border width and contrast by body width divided by 6.
The independent arm retains the requested border width and contrast at both body sizes.
This matched comparison tests the combined coverage change. It does not isolate each parameter's causal effect on native accuracy.

The validator checks every image hash, visible change, allowed region, body box, focus label, and coverage cell.
All 1,920 pairs pass. A review checks 8 representative views before training admission.
Preparation rejects protected-group or protected-pixel overlap. Original training views and evaluation roles remain unchanged.
Both arms retain the original 240 authored examples and all 1,820 original views and weights.

## Measured effects

The table gives median changed-pixel areas at body width 3. A pixel counts when its mean RGB difference exceeds 1/255.

| Border width | Contrast | Coupled area | Independent area |
| --- | --- | ---: | ---: |
| 1 | 0.25 | 94 | 146 |
| 1 | 0.75 | 94 | 150 |
| 3 | 0.25 | 158 | 422 |
| 3 | 0.75 | 214 | 534 |

The independent arm spans maximum mean RGB differences of about 0.323–0.771 at this body size.
The previous tiny native examples affect 269–280 pixels, with maximum differences of 0.554–0.571.
The new parameter range covers weaker and stronger effects. It does not establish an exact native match.
At body width 6, both arms produce the same effects by design.
Unit tests confirm that width and contrast change pixels without changing body bounds.
The effect audit uses no model predictions as labels. It changes no evaluation membership or decision threshold.

## Training and verification

Both candidates start from FOCUS325-average and retain average pooling.
The existing trainer runs 30 epochs with seed 42, batch size 16, and learning rate 0.0001.
The auxiliary loss coefficient stays at 0.25. Thresholds stay at 0.15 and 0.85.
Both runs use identical optimizer counts and all 1,200 authored rows in their schedules.
Only the detail projection and correction layers train. Convolution and whole-frame weights remain frozen.
Preparation checks that the cached encoder matches the initializer. Each run checks image/cache parity and checkpoint reload.
Fixed final checkpoints prevent evaluation-based selection.

All 76 focused tests pass in 1.652 s. The offline Swift build passes in 4.29 s.
All 14 XCTest tests and 173 serial Swift Testing tests pass. Swift Testing takes 52.744 s.
Preparation takes 87.43 s. Generated artifacts remain under the 2 GiB budget.
The training loops take 1.47 s and 1.46 s. Complete runs take 154.76 s and 153.15 s.
Cache/image probability error is 0 for both candidates. Only the 4 permitted parameter tensors change.
Artifacts occupy about 73 MB. Evaluation dominates runtime; no external wait blocks execution.
No simulator capture, dependency download, Core ML export, or producer assignment occurs.

## Evidence

Raw evidence remains under `reports/work/FOCUS-326/`, outside Git.
`inputs.json` pins the runner, trainer, corpus, review, initial model, caches, and previous input contract.
`generation-source.py` retains the exact generator source recorded in the corpus.
Its hash is `b460f869175022f17b0680210ea2276751fec33f1ec2a8f40f5451a3e187ed8a`.
The corpus hash is `61675e342116726ed7aa4deac87915a384da2598e02f31e74197660a2f8dedf5`.
The validation hash is `eebe926748f094467e1d084e678e56e486ac5bedc97eee5c80d21893f88943d0`.
Per-run reports retain case IDs, groups, roles, and comparisons against previous candidates.

The coupled checkpoint hash is `1de9848a945c23e3f667c12d1cc8c211829139e12527cf59c351d4103e880195`.
The independent checkpoint hash is `7fa1e25bc23f214d77c74748134376a9a7a7590702cc63a0b5d7284193e0aaf7`.

- Software verification: passed.
- Data eligibility: authored training only; original evaluation roles remain unchanged.
- TTR integration: not assessed by this model experiment.
- Model requirements: failed; no promotion.

The coordinator stores the result at cursor 160 without confirmed forwarding.
The SMB fallback publishes `nuiak/responses/nuiak-focus326-result-01.json`. Exact size, hash, and readback pass.
Sillycon-TTR acknowledgment remains unconfirmed. The update tells Sillycon-TTR to keep its current model.

## Next substantial tranche

FOCUS327 should test whether the frozen detail filters prevent learning these examples.
Reuse FOCUS326's independent corpus, initializer, schedule, thresholds, and retained frozen-filter control. Do not regenerate or repeat that control.
First, test gradients and training-only fit on a balanced subset of the existing size, width, contrast, and negative conditions.
Then train 1 matched 30-epoch candidate with the detail convolutions enabled. Keep the whole-frame model and geometry outputs frozen.
Use the existing trainer and original-resolution detail views. Make no public API change.
Measure training fit and native transfer separately. Compare all previous successes, false changes, abstentions, and reversals.
Require cache/input parity, finite gradients, unchanged whole-frame weights, and a fixed final checkpoint.
Preserve the 2 GiB output and 8 GiB memory limits. Register exact input hashes and trainable parameters before execution.
If the training-only check fails, diagnose the inputs or loss before launching the full candidate.
Acceptance remains native improvement without lost previous successes or increased false changes.
This changes learned visual features, not another scalar score or an automatic volume increase.
