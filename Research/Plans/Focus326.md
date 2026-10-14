# FOCUS326: independent effect coverage

The comparison completes. [Results](../Focus326Results.md) reject both candidates and record the next test.

Maximum-mini-NUIAK owns this user-approved comparison. No other worker receives an assignment.
The resident TTR renderer uses fixed focus scale, shadow blur, and ring widths.
Use the existing NUIAK compositor and reviewed artwork. Do not change the TTR checkout.

## Frozen experiment

Render authored rectangular cards with scale 1.14, a white border, and a soft halo.
Cross body widths 3 and 6 encoded pixels, border widths 1 and 3 pixels, and contrast 0.25 and 0.75.
Cross 3 approved artwork families, 4 corners, and separations 32 and 96 pixels.
Use focus movements, unchanged-focus artwork changes, and identical frames. Reverse nonidentical pairs.
Each arm contains 960 scheduled pairs from 192 scenes. Related scenes remain training-only.
The coupled arm scales border width and contrast by body width divided by 6.
The independent arm holds those 2 settings independent from body width.
This tests the combined coverage change. It cannot attribute native improvement to width or contrast alone.
Measure each axis separately before training. Include factorial counts and changed-pixel measurements.
Effects are authored, not measured native effects. Do not label them as simulator captures.

Initialize both runs from FOCUS325-average. Retain average pooling and freeze convolution and whole-frame weights.
Use the existing 1,820 original views and weights. Add each arm to the same previous 240 authored examples.
Use 30 epochs, seed 42, batch 16, learning rate 0.0001, and auxiliary coefficient 0.25.
Match optimizer updates and all authored row exposure. Keep thresholds 0.15 and 0.85.
Use fixed last checkpoints. Do not select using evaluation results.
Limit outputs to 2 GiB, threads to 2, and memory to 8 GiB. No wall-time limit applies.
Preserve original views and all evaluation exclusions. Verify decoded pixels and ancestry before admission.

## Acceptance and companion audit

Validate every image, hash, annotation, pair state, and coverage cell. Review representative images before training.
Reject clipping, invisible changes, label conflicts, unknown versions, and output collisions.
Verify cached/image parity and unchanged frozen weights. Compare all previous native, replay, nuisance, tiny, and placeholder checks.
Report gains, lost successes, misses, false changes, and abstentions separately.
Acceptance requires native gains without lost previous successes or increased false changes.
The companion audit measures effect footprints across all factorial cells without fitting another model.
Run focused tests and the required offline Swift build/test pass once after code integration.
Record software, data eligibility, integration, and model outcomes separately. Keep TTR updated with the measured result.
If both candidates fail, preserve evidence and diagnose the next causal question. Do not launch another automatic fit.
