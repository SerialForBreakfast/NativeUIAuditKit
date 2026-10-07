# Measure and reproduce native focus effects

Task: TRANSITION-253. Tasks.md owns status and priority.

## Goal and limits

Measure the visible transformation between unfocused and focused controls. Build a reproducible renderer and test its fidelity on separate native examples.
Pixel equality is a measured outcome, not a promised result. Different parameter combinations can produce similar images.
Record uncertainty when the visible evidence cannot identify one unique parameter value.
This work extends FOCUS-RENDER-203 with native measurement. Reuse its renderer where suitable instead of creating a competing pipeline.

NUIAK owns measurements, comparison, and model evaluation. TTR owns required changes to Fixture.
Big Dog can perform a later bounded parameter search on verified reference images.
Do not interrupt TRANSITION-249 or change its input package.

## 1. Establish reference measurements

Inspect current local Fixture interfaces and retained examples first.
Use the native focus renderer, not requested effects or a procedural approximation, as the reference.
Pin source, build, OS, device profile, display scale, dimensions, appearance, and accessibility settings.
Record image content mode, control bounds, clipping, corner shape, and observed focus identity.
Keep layout bounds separate from rendered effect bounds.

Start with opaque shapes, asymmetric registration marks, and neutral backgrounds. Then add textured artwork, alpha edges, and contrasting backgrounds.
Use asymmetric marks to distinguish scale, translation, anchor position, cropping, and content-mode changes.
Include several control sizes and positions, including edges. Coordinate this coverage with TRANSITION-252.
Capture repeated unchanged references to measure frame noise and settling variability before fitting parameters.
If animation timing matters, retain timestamped sequences. Two endpoints cannot identify an animation curve.
Do not infer remote-driven parallax from a stationary settled pair.

Command-line orchestration can operate an existing Fixture runtime. It does not require the TTR desktop capture pipeline if existing interfaces suffice.
Native UIKit rendering still requires a supported native runtime. A Linux image renderer alone cannot supply native reference pixels.
Use an exact simulator identity and approved runtime scope. Do not install, restart, or modify another repository implicitly.

## 2. Implement the measurement command

Extend existing image comparison and procedural rendering tools. Provide separate inspection, fitting, and rendering modes.
Inspection performs no capture, fitting, or simulator mutation.
Read an immutable manifest of reference images, observations, roles, and hashes.
Reject missing images, changed hashes, incompatible dimensions, unknown coordinate conventions, and output collisions.
Preserve originals. Declare color conversion, alpha handling, pixel scale, and interpolation explicitly.

Measure these components separately where the evidence permits:

- Horizontal and vertical scale, translation, and transformation anchor.
- Content scaling and clipping within the control.
- Corner shape and visible silhouette.
- Shadow offset, opacity, spread, and blur.
- Brightness, tint, and spatial highlight profile.
- Temporal growth and shadow curves from timestamped sequences.
- Motion-driven tilt and layer offsets from separately qualified motion sequences.

Keep a shared coordinate system for before and after images. Independent crop resizing can remove the growth being measured.
Compare aligned native and rendered pixels using fixed masks for the body, border, shadow, and background.
Report exact differing pixels, channel errors, edge displacement, and regional residual maps.
Large unchanged backgrounds must not conceal a poor match around the control.

## 3. Fit a bounded renderer

First estimate geometry from registration marks and silhouettes. Then fit shadow and highlight parameters using the fixed geometry.
Use a coarse-to-fine bounded search or an appropriate optimizer for coupled parameters.
Use binary search only for a measured monotonic relationship. A coupled image-error objective is not generally monotonic.
Freeze parameter ranges, objective weights, maximum evaluations, seed, and output limits before search.
Keep all trials and the selected parameters. Record the selection rule and parameter uncertainty.
Do not tune against reserved validation scenes.

Use published implementations as initial hypotheses, not Apple constants:

- [Custom focus effects](https://devsign.co/notes/custom-focus-effects-in-tvos): author-defined scale, shadow, motion, and animation examples.
- [ParallaxView](https://github.com/PGSSoft/ParallaxView): reusable parameter concepts; review its exact revision and license before copying code.
- [Apple native rendering](https://developer.apple.com/documentation/uikit/uiimageview/adjustsimagewhenancestorfocused): version-specific native reference behavior.

## 4. Verify fidelity before generating volume

Reserve different artwork, backgrounds, sizes, and positions before parameter fitting.
Compare the fitted renderer with a simple scale-only baseline on identical native references.
Report residuals against the repeated-native noise measurement. A low mean error does not establish pixel equality.
Claim pixel equality only for exact decoded equality under the stated rendering configuration.
Otherwise publish the measured error and unsupported effects. Do not describe an approximation as an exact native reproduction.
Keep simulator and physical-device results separate. No physical-device capture is included in this packet.

Tests cover known synthetic transforms, parameter recovery, alpha edges, clipping, color conversions, temporal ordering, and repeated-input determinism.
Also test unknown observations, missing reference members, changed hashes, and role leakage.
Run focused tests and one integrated offline package check after code changes.

## 5. Test training usefulness

After renderer qualification, freeze one control and one treatment using the established model and equal training budgets.
The treatment adds rendered focus effects on diverse eligible artwork and backgrounds.
Include non-focus zoom, shadow, brightness, and content changes as negative examples.
Keep native reserved examples outside fitting, threshold selection, and renderer adjustment.
Compare missed changes, false changes, abstentions, and prior successes by position and appearance.
Generated effect labels describe the renderer's action. They do not establish native focus truth.
Scale generation only if the matched comparison improves native results without failing existing gates.

## Handoff and next action

Deliver the reference inventory, reproducible commands, parameter report, residual images, tests, and matched training proposal.
Report software verification, data eligibility, native fidelity, and model qualification separately.
The first action is a retained-reference and local-capability audit with a bounded reference matrix.
If exact native observations or rendering controls are missing, name the required TTR change while completing offline tooling.
This document authorizes no automatic large search, new service, download, model promotion, or physical-device operation.

## Retained-image formula comparison — 2026-10-07

Use the existing TRANSITION253 measurement command. Do not start a second renderer or change running jobs.
FOCUS-RENDER-203 assigns its renderer to Big Dog. No reusable local renderer appears in the current scripts inventory.

Fit lighting on the 4 training pairs from `233:recipe-00` only.
Check the frozen formulas on recipes 03, 04, and 05. These remain development checks with their existing training role.
Do not read recipes 06 or 07 for this experiment. Preserve their reserved role.
Reuse the previous median geometry. Report that geometry as fitted, not an Apple constant.

Compare 3 fixed formulas:

- Shared scalar gain and bias from the previous experiment.
- The previous quadratic correction, fitted again on the same 4 pairs.
- A white elliptical highlight, with bounded gain, bias, position, width, and strength.

For the highlight, use `output = color * (1 - alpha * gaussian) + alpha * gaussian`.
Fit 7 parameters with 2 fixed starting points and at most 100 optimizer evaluations per start.
Use every 16th interior pixel for fitting. Score all interior pixels at the original crop resolution.
Select the starting point by fitting error only. Keep both trial results.
Use CPU computation with 1 thread. Limit new outputs to 100 MB.

Reject changed input hashes, changed prior membership, output collisions, and non-training fitting members.
Record unsupported pairs instead of changing their geometry or labels.
Report each recipe separately. Do not select a formula from one pooled score alone.
Keep all formulas in the report, including failures.

This comparison measures lighting, not a complete compositor. Backgrounds, borders, and shadows remain outside its fitting objective.
Do not admit these diagnostic images as native training data.
The next full rendering test needs a clean background and a measured silhouette for each control.

## Border and shadow comparison — retained references, r3

Reuse the same 16 pairs and preserve their roles. Fit recipe 00 only.
Use the observed body and visible bounds to separate interior, border, and exterior support.
Report partial clipping. Do not treat a clipped rectangle as a measured alpha silhouette.
Keep the r2 highlight parameters and growth fixed.

Test corner radii of 0, 8, 16, 24, and 32 pixels on fitting borders.
Test shadow blur widths of 6, 12, 24, and 48 pixels with vertical offsets of 0, 8, 16, and 32 pixels.
Fit one nonnegative shadow strength per candidate, capped at 0.8. Select parameters from fitting error only.
This measures added darkening against the unfocused frame, not absolute native shadow opacity.
Use quarter-resolution fitting and full-resolution checks. Preserve all candidate scores.
Composite the effect over the unchanged frame. Limit the shadow to its declared finite support.
Score body borders and exterior pixels separately. Do not let unchanged backgrounds hide border errors.

Use 1 CPU thread, no capture, no model training, and less than 100 MB of new output.
If the exterior brightens or the border model fails, report that mismatch instead of expanding the search automatically.
Test clipping, repeatability, background preservation, invalid bounds, and known shadow recovery.
Return a qualification decision and the exact missing reference components before any training proposal uses these renders.

After r3 completes, check its fixed parameters on 8 retained artwork pairs from `234:recipe-00` and `234:recipe-03`.
These pairs retain their training role. Use no parameter fitting or selection from their results.
Compare the same region metrics. Preserve unsupported cases and previous results.
This check tests artwork sensitivity before any new capture or larger parameter search.

The artwork check shows native scale 1.14773 for taller controls, versus 1.172083 in the fitting group.
Add 2 diagnostic comparisons on the same 8 artwork pairs. Do not fit their pixels.
First, derive a constant increase in the longest dimension from the 4 original fitting controls.
Apply `scale = 1 + increase / longest_dimension` with the center fixed.
Second, use recorded native geometry as an idealized diagnostic. Keep that result separate from the predicted formula.
Keep lighting, radius, and shadow parameters fixed. This tests whether geometry explains the artwork error.

## Source artwork and content mapping — r4

Use the same 8 training-role artwork pairs from recipes `234:recipe-00` and `234:recipe-03`.
Verify the embedded recipe and asset hashes before decoding. Preserve source images and all existing data roles.
Compare source artwork mapped into observed resting bounds against the resting screenshot interior.
Compare source artwork mapped into observed focused bounds against the focused screenshot interior.
Compare both against the previous screenshot-warp method using the same observed geometry and frozen highlight parameters.
Observed focused geometry is a diagnostic input, not a deployable prediction.

Keep the source asset's fill/fit rule and anchor. Report alpha coverage and source dimensions.
Report raw pixel errors and high-frequency errors separately. Use a fixed Gaussian width of 2 pixels for frequency separation.
For diagnosis, report blur widths of 0, 1, 2, and 4 pixels without selecting a production setting.
Fit per-channel gain and bias on each pair only as a labeled diagnostic upper bound.
These fitted checks do not qualify renderer transfer or supply training images.
Report whether clean background and native alpha references exist. Do not infer these references from rectangular boxes.

Implement this comparison in the existing measurement command family. Add synthetic mapping, alpha, and malformed-input tests.
Use resident CPU libraries with 1 thread. Limit new outputs to 100 MB and preserve existing results.
Finish the 8-pair comparison, focused tests, offline Swift build and tests, and a measured decision about the next native capture.

The first completed r4 comparison does not improve the focused match from original artwork.
Keep that negative result. Add one fixed coordinate comparison using the already enlarged screenshot as input.
Derive coordinate denominators only from the original 4 fitting pairs in `233:recipe-00`.
Compare coordinates scaled by control width and height against coordinates scaled by the longest control dimension.
Keep highlight parameters frozen. Report all alternatives on the same 8 artwork pairs; do not select a production renderer.
This tests whether crop proportions cause the transfer failure. It does not fit the artwork checks.

## Controlled local reference campaign — r5

The r4 coordinate comparison leaves the wide-artwork error near 11.6. Use a controlled native comparison next.
Use local TTR and Simulator `9026ECA9-77DB-4AE6-8FE6-BB239E9571FA` after fresh readiness and ownership checks.
Reuse the qualified app/helper and capture/export path. Preserve its app-owned runtime storage.
Use the first owned thumbnail from retained recipe `234:recipe-03` for every control.
Capture 4 recipes: 2 control widths, 260 and 360 points, crossed with 2 uniform backgrounds, dark and light.
Keep control height, artwork, anchor, content mode, labels, positions, OS, and accessibility settings fixed.
Each recipe contains 4 targets. Expect 16 native pairs and 32 checked production crops.
Keep all examples in the existing pilot artwork's development-training family. This is a diagnostic capture, not independent evaluation.
Limit explicit output to 512 MiB. Preserve failed attempts; do not repeat ambiguous mutations.

Verify complete export hashes, recipe equality, native focus observations, geometry, and production crops.
Measure growth and frozen-lighting residuals by size and background. Compare matched focused interiors across backgrounds.
If geometry and content match, this contrast can isolate the background effect within the tested rendering configuration.
Finish with current Fixture health, readiness, and cleanup evidence. Keep training and full renderer qualification separate.
