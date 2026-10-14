# FOCUS328: separate growth from content contrast

Maximum-mini-NUIAK owns this approved experiment. Preserve all original images, labels, groups, weights, and previous-success checks.

## Diagnostic

Use training rows only. Measure brightness changes, edge changes, and contributions from both model branches.
Compare FOCUS327 with its fixed-filter control on the same rows.
Apply fixed contrast changes to training detail crops without moving their boundaries.
These changes test sensitivity. They do not create native labels or additional independent examples.
The fixed perturbation changes the central 128-pixel region. It covers crop content but only part of a full-frame fallback.
Report these conditions separately. Do not describe every perturbation as a global contrast change.

Test 1 proposed representation: standardize each detail frame within its content area, separately for each color channel.
Use a standard deviation floor of 0.05. Map standardized values with `0.5 + 0.2 * z`, then limit values to `[0, 1]`.
Keep the existing black margins. If the detail view contains full-frame pixels, preserve and normalize the complete frame.
Keep crop selection, whole-frame inputs, and original-resolution extraction unchanged.
This representation removes broad brightness and contrast differences. It can also remove useful focus cues.
Measure that risk before training. Do not choose constants from development results.

Proceed only if training contrasts affect the current detail scores and normalization reduces those changes while retaining growth differences.
Record the diagnostic before candidate registration. If it fails, stop candidate training and report the cause.

## Matched candidate

Reuse FOCUS325-average initialization and the exact FOCUS327 schedule. Compare with completed FOCUS327 and FOCUS326 runs.
Train detail filters and their output layer for 30 epochs. Freeze whole-frame and geometry weights.
Use learning rate 0.0001, batch size 16, seed 42, and auxiliary weight 0.25.
Use thresholds 0.15 and 0.85. Select the last checkpoint, not the best development result.
Use 2 CPU threads, at most 8 GiB memory, and at most 2 GiB new outputs.
Keep outputs in `reports/work/FOCUS-328`. The standing approval removes the wall-time limit.

## Verification and decision

Test identical frames, contrast changes, growth preservation, reversal, finite gradients, invalid inputs, and checkpoint reloads.
Verify unchanged original views and frozen weights. Run all retained native, reversed, replay, nuisance, tiny, and placeholder checks.
Report gains and losses for each data role. Inspected cases remain development evidence.
Accept improvement only with fewer contrast errors, native gains, and no lost previous successes.
Run focused tests and 1 offline Swift build/test pass. Do not export or promote a failed candidate.

Return the result to TTR through coordinator chat. Use the approved SMB fallback if forwarding remains unconfirmed.
Keep publication, forwarding, acknowledgment, and model acceptance separate.
