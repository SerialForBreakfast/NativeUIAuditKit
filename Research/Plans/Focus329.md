# FOCUS329 — preserve appearance and test boundary evidence

Maximum-mini-NUIAK owns this approved experiment. Use retained images only.

## Diagnostic

- Read every native-derived training row in the fixed TRANSITION-249 membership.
- Verify image and metadata hashes. Match scenes to image hashes and observed focus identities.
- Read all measured controls in both frames. Require the same control IDs. Keep interiors separate from the surrounding 35 px band.
- Preserve clipping reports. Missing geometry stays unavailable.
- Measure changes at original resolution. Compare boundary change with interior change.
- Measure how much boundary change the existing 2 image-selected windows contain.
- Report content-change conditions separately. Repeated rows do not establish independent support.
- Compare known-box measurements with an image-only edge-change measurement inside existing detail windows.

Known boxes serve diagnosis only. Candidate inputs cannot include correct boxes or focus identities.
Do not select settings from development or reserved rows.

## Conditional candidate

If native training evidence supports boundary information, register 1 additive correction before training.
Keep raw appearance, original views, membership, weights, thresholds, and the existing trainer.
Use 30 epochs, seed 42, batch 16, and fixed-last selection. Freeze whole-frame and geometry weights.
Record the exact representation and initializer after diagnosis, before execution.
The completed diagnostic supports 1 added-edge comparison, with important limits.
Known boundary fractions separate the content cases. Image-only edge ratios give weaker separation in both contributing families.
Use FOCUS325-average initialization to match FOCUS327. Preserve the original 12 detail channels.
Add 6 per-frame RGB gradient magnitudes to the first detail convolution.
Compute fixed forward differences in x and y. Average their magnitudes. Set added convolution weights to 0.
Check initial prediction agreement before training. Train detail filters and correction weights only.
Use learning rate 0.0001 and auxiliary coefficient 0.25. Keep the FOCUS327 schedule and original detail crops.
Use 2 CPU threads, at most 8 GiB memory, and at most 2 GiB new output.
No wall-time limit applies. Do not export or promote a failed candidate.

## Acceptance

Compare false changes, missed changes, abstentions, and previous successes on all existing comparison sets.
Require native gains without lost previous successes or increased missed changes.
If native boundary evidence cannot support the correction, finish the diagnosis without an unsupported training run.
Test missing geometry, mismatched focus, changed hashes, clipping, empty differences, and role exclusions.
Run focused tests and 1 integrated offline Swift build/test pass.
Update the local queue and send the producer-relevant result to Sillycon-TTR through coordinator chat.
