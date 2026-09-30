# FDR-014: sampler corrected; real-screen acceptance still fails

The single authorized run completed all 30 epochs. No epoch passed the unchanged
selection rules, so there is no selected checkpoint and no export or promotion.
Rebalancing training alone is insufficient on this corpus; this does not establish
that data coverage is the only cause or that the architecture is adequate.

## Controlled comparison

Same 363 training pairs, nine retention pairs, 453 real selection crops,
64 exclusions, FDR007 initialization, fresh optimizer, preprocessing, hyperparameters
and MPS backend as FDR013. Only training sampling changed: buttons, tabs, artwork
and rows each receive 25%, balanced by label. Source-first 50/50 was intentionally
replaced. Exact membership and non-sampling experiment fields were checked equal.
Actual seed-42 draws across 30 epochs: 5,497 buttons, 5,479 tabs, 5,366 artwork,
5,438 rows. Seventeen true tab pairs were identified from scene metadata;
three nested-tab child-button pairs remain buttons.

| Development diagnostic (not selected checkpoints) | FDR013 | FDR014 |
|---|---:|---:|
| Eligible epochs | 0/30 | 0/30 |
| Lowest false positives / 418 unfocused controls | 21 (epoch 19) | 10 (epoch 4) |
| Correct focus detections / 35 at that epoch | 2 | 2 |
| Final epoch correct detections / false positives | 7 / 39 | 4 / 35 |
| Epochs preserving 18/18 retention decisions | 29/30 | 30/30 |

The minimum-FP snapshots are descriptive, not a replacement checkpoint policy.
Epoch 4 still misses 33/35 focused controls, including every focused artwork and
tab example, and produces one multiple-focus frame. Epoch 23 detects one of three
focused tabs and has four uniquely correct frames, but also 26 false positives
and two wrong-focus frames. Six epochs detect one tab; none detects more than one.
The minimum balanced real loss occurs at epoch 2: 9 correct detections with
70 false positives. Neither low training loss nor isolated gains yield a usable model.

Every epoch fails the real-improvement, artwork and complete-frame guards.
Rows fail in 21 epochs, buttons in 24, other controls in one. Retention passes all
30. The trainer's generic terminal message mentions retention, but **retention is
not this run's blocker**. The detailed guards above are authoritative.

## Verification and limits

`selection-verification.json` replays initialization and all 30 epochs using the
existing metric implementation: 14,601 stored scores, exact membership and labels,
all loss/guard/stratum/frame calculations reproduced. Frozen implementation hashes
remain unchanged. Exact recurring error IDs and image/crop references are retained.
Seven controls are false positives in every epoch; these are repeated development
observations, not seven independent source groups.

No best.pt exists. The conditional selected-checkpoint CPU/related-synthetic
comparison is therefore not applicable. No last.pt substitution or new inference
was performed. Results use training-time MPS predictions on development selection
data, not untouched qualification data or CoreML export parity.

## Next assignment: repair the real-screen contrast gap before another run

1. Audit the already offered native100-r2/canvas-v2 delivery against the exact
   persistent errors in `selection-verification.json`. Count useful distinct
   contrasts, not just pairs. Do not admit unresolved geometry or evaluation overlap.
2. Prioritize same-artwork focused/unfocused pairs with unchanged background and
   visible competing controls. Verify the production crops retain the distinguishing
   cue. Then cover selected-but-unfocused versus truly focused tabs and missed rows.
3. Use grouped native-label and crop review, with human attention only for ambiguous
   cases. Keep the real selection set out of training; related screens retain their
   ancestry and cannot become independent qualification evidence.
4. If the offered data does not cover those contrasts, return a precise small capture
   assignment. If labels/crops are verified and contrasts are already covered, test
   representation/preprocessing as a separate controlled hypothesis—not more epochs.

No new transfer, capture or further training was performed in this tranche. The
existing TTR request for artwork/tab contrasts and geometry repair remains the next
producer action; this result does not add a new producer requirement.
