# Native-focus spike — completed October 2, 2026

**Result: native focus appearance is learnable in this synthetic setup when enlargement
and surrounding pixels are preserved. Real-app use needs reference-window validation.**

All1,250pairs are received on USB:1,000training and250reserved synthetic evaluation
pairs. All5,000target crops pass. Both encoding and training comparisons completed.

## Matched results

Predeclared0.85threshold on the same250held-out pairs (500controls:250focused,
250unfocused), with fixed final checkpoints and no evaluation-based selection:

| Model/input | Correct controls | Both states correct | False focused | Missed focused |
|---|---:|---:|---:|---:|
| Existing FDR021, standard crops |283/500 (56.6%)|33/250|2|215|
| FDR035, new standard crops |433/500 (86.6%)|183/250|67|0|
| FDR036, fixed reference window |500/500 (100%)|250/250|0|0|

FDR035/036 used identical initial weights, seed42,2,000training controls and1,000
updates;33.12s/33.47s training. Both fit all training examples. At0.5, standard crops
score395/500; reference windows remain500/500. All67standard-crop errors at0.85are
unfocused targets on dark backgrounds. Common windows fix all67without new errors.
Measured body growth spans12.9–18.2%width and16.7–21.8%height.

## Real-screen transfer

FDR035 replayed unchanged315development+18retention controls. Focused artwork found
improved2/12→9/12, but falsely focused artwork increased3/181→149/181. Correct
complete-frame selection fell12/14→0/14 (nine no-focus, five multiple-focus).
Settings-row focused recall fell7/7→0/7. Both retain18/18native retention controls.
**Reject FDR035 as a replacement.** This is narrow synthetic specialization with
severe transfer failure: training fit is perfect and synthetic positives recognized.
FDR036 has no compatible reference windows for that retained set; real transfer is
unanswered. Existing shipped models remain unchanged.

## Capture and storage

- 2,500screenshots;14,536,675,677bytes of verified exports on USB.
- 1,250successful cases; one pre-capture Xcode probe failure recovered separately.
  Original failure and24+1recovery accounting retained.
- Successful case duration: median7.61s, p95 9.73s. Producer campaign time totals
  9,561s; this excludes manual recovery/debug idle time.
- Receiver copy/hash checks:39.05s total. Production/comparison crops:248.23s total,
  performed alongside capture. Internal free space at completion: about11GiB.
- Encoding6.49s/5.92s, including read/decode and cache writes. Generation dominates;
  USB was adequate. Consumer originals/crops/caches are on USB, while TTR retains
  app-owned staging. Whole capture workflow roughly3h including recovery/debug idle.
- Postflight reports can_run=true and persisted ownership clear. Capture and crop
  workers exited0; the Simulator and TTR applications remain available.

[Final replayed metrics](final-results/summary.json) · [Optional random samples and error review](final-results/review.md)

## Interpretation

The comparison is per-body production16%context versus a common window with20%
context, anchored to a known unfocused reference. It changes scale and context
together, not growth alone. Primary scoring covers each nominated target twice;
it is not whole-screen selection or a test of the excluded bright distractor crops.
Evaluation uses two withheld configurations and a withheld artwork family, sharing
one native renderer/OS. Real-app transfer is a separate unchanged333-control replay
for the standard-crop candidate only.
Larger body occupancy alone could explain the common-window success; this does not
prove isolated subtle shading/shadow recognition. Evaluation artwork luminance is
entirely mid-range. Broader dark/bright artwork and real-app claims remain unqualified.

## Verified software and companion

58focused Python tests (final-regression-tests-corrected.log), offline Swift build,
14XCTest+120Swift Testing tests pass. A test-command module-name typo was corrected;
the final suite has zero failures.
The integrated caller uses the production Swift cropper with an explicit USB input
root and the existing training entrypoint. CORPUS-LIFECYCLE-27 is implemented and
tested: explicit OS policy, immutable membership, historical replay and read-only
cleanup advice. [Companion handoff](../CORPUS-LIFECYCLE-27/handoff.md).

Source/annotation compatibility failures and the successful recovery are preserved
in [history](history.md). Final report recomputes both synthetic metrics, FDR021
baseline and retained333-control scoring from saved predictions. All workers exited0.
[TTR publication/readback](coordination.md) verified, peer final acknowledgment pending.

## Recommended next substantial tranche

1. **Real paired validation:** audit existing reviewed sequences for native artwork
   transitions with trustworthy unfocused references and matched control identity;
   freeze usable coverage and replay FDR036. Capture only concrete gaps if necessary.
   Measure reference/tracking failures separately from classification.
2. **Explain the cue:** compare scale/occupancy versus surrounding appearance using
   predeclared matched ablations and content-only/illumination negatives. Keep this
   evaluation membership fixed; additional experiments require their own scope.
3. **Integration decision:** define specialist applicability and uncertain outcomes,
   then test an offline advisory caller alongside the existing detector. Export and
   promotion follow real-transfer evidence.

These are recommended follow-ups, not completed qualification. TTR batching supplied
this run; pacing/parallelism remains an optional measured optimization.
