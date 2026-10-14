# FOCUS313: separate detail regions with a frozen classifier

Owner: Maximum-mini-NUIAK. Both matched experiments, regression reports, and software verification complete.

## Result and decision

Neither candidate passes acceptance. Do not promote either model.
The 2-window model gains 12 native decisions and loses 3 previous successes against DTM085.
It improves 5 native decisions against the 1-window control without losing another native decision.
However, it still misses all 4 tiny changes in both directions.

| Measure | DTM085 | 1 window | 2 windows |
| --- | ---: | ---: | ---: |
| Native correct / 640 | 589 | 593 | 598 |
| Native training correct / 548 | 505 | 511 | 514 |
| Development correct / 40 | 33 | 33 | 33 |
| Previously inspected reserved correct / 52 | 51 | 49 | 51 |
| Replay correct / 668 | 667 | 668 | 668 |
| Reverse native correct / 640 | 582 | 602 | 602 |
| Lighting correct / 226 | 226 | 226 | 226 |
| Left false changes / 226 | 81 | 78 | 82 |
| Center false changes / 226 | 121 | 107 | 99 |
| Center correct / 226 | 80 | 96 | 82 |
| Tiny changes correct / 4 | 0 | 0 | 0 |

The center false-change reduction mostly becomes abstention in the 2-window model. Do not report it as 22 additional correct decisions.
The 1-window model loses previous successes in 1 of 24 strength/order checks. The 2-window model regresses in 3.
These sets contain training and repeatedly inspected development evidence. They do not establish unseen-app performance.

### Why the tiny changes still fail

The first window contains 49.5%–50.4% of their difference energy. Two windows contain essentially 100%.
Raw fractions can exceed 1 by about 0.00000012 from floating-point summation. This is numerical rounding, not extra coverage.
The frozen classifier strongly favors unchanged. Its raw scores range from -13.98 to -9.94 before the probability conversion.
The 2-window correction adds another -2.16 to -2.00. It reinforces the wrong decision despite seeing both changed regions.
At the changed threshold of 0.85, these examples need positive corrections of 11.67–15.72 instead.
This diagnosis does not justify changing the threshold. It shows that this learned correction does not recognize the required effect.
Do not add more windows or epochs without a different, testable training hypothesis.

### Cost

The training loops take 230.29 s and 342.76 s for 3,420 optimizer updates each.
Preparation, both fits, checkpoint checks, and regression scoring take 973.69 s overall.
The completion receipt records 14,758,100 output bytes before later report files.
Sampled process memory stays below 8 GiB. Samples do not establish the exact peak.
Both runs verify unchanged frozen weights and exact checkpoint reload results.

## Contract and software

Compare 1 versus 2 image-selected regions. Both models have 339,932 parameters.
Both models preserve the original classifier and geometry weights exactly.
Only the shared detail encoder and added correction can change.
Both runs use DTM085 initialization, 30 epochs, batch 16, seed 42, and learning rate 0.0001.
Thresholds remain 0.15 and 0.85. Select the final checkpoint without tuning on evaluation cases.
All 1,820 original training views, labels, weights, and group assignments remain unchanged.
The 1-window detail hash exactly matches FOCUS310.
The second window uses the highest remaining average difference energy among nonoverlapping 32-pixel windows.
Both frames use the same coordinates. Source crops retain original pixels where available.
Encoded-only inputs keep their existing fallback. No annotation box selects a model input.
If no second region has positive energy, repeat the first region. Identical pairs use full-frame views.

The audit finds 1,442 entries with 2 separate windows, 12 with 1 window, and 366 identical pairs.
These are schedule entries, not independent scenes. Both runs keep the same first window and source references.

## Verification

All 34 focused Python tests pass. They cover source identity, frozen weights, crop alignment, edge windows, reverse order, and checkpoint loading.
The integrated offline Swift build passes with SwiftPM's native engine in 1.59 s.
The default engine fails because Finder metadata appears on a generated resource bundle.
Removing that attribute from the generated bundle does not resolve the next build attempt.
No source resource, certificate, or system service changes.

The first run stalls inside Apple Vision. A 1 s process sample records that wait.
The user then approves stopping only test processes 34204 and 34178. Maximum-mini-NUIAK verifies their identities before stopping them.
The current integrated serial run passes 14 XCTest tests and 173 Swift Testing tests.
Swift Testing takes 51.742 s. The current offline build also passes in 0.65 s.
The log is `.build/focus319-swift-test-serial.log`. Earlier failure evidence remains available.

## Headless companion

Maximum-mini-NUIAK runs the unchanged TTR renderer from source `d06a64bd`.
The renderer produces shelf, grid, hero detail, and navigation layouts without the app or Simulator.
An explicit empty asset directory selects built-in placeholders. This is deliberate diagnostic input, not missing-artwork admission.
The output contains 8 PNGs and 4 sidecars plus the batch manifest.
Independent intake passes expected-layout, dimension, hash, sidecar, and authored-identity checks.
The score report compares arrival, departure, and identical-frame pairs through existing model entrypoints.
All 3 models score 10/16 comparisons correctly. Eight correct comparisons are identical-frame controls.
All models detect shelf arrival and departure. None detects hero-button or tab arrival and departure.
The baseline abstains on both grid changes. The 2-window model misses both instead.
These cases remain authored development evidence. They do not enter training or establish native focus accuracy.
Visual review of grid and hero detail confirms visible selected controls. Grid growth overlaps the subtitle area.
The renderer also changes text weight and brightness. Its current outputs do not isolate growth alone.

The companion then renders a second focused control in each layout through the existing `--focus-id` option.
Matching unfocused-image hashes establish identical base pixels across the 2 render operations.
Pairing the focused images supplies 8 authored A-to-B comparisons, including reversals.
All 3 models detect both shelf directions, abstain on both grid directions, and miss both hero and tab directions.
That is 2/8 correct for each model. Arrival-only semantics do not explain the whole failure.
Rendering the 4 alternate states and scoring all 3 models takes 4.76 s with resident tools and warm caches.
This timing excludes the first renderer invocation and does not predict artwork-heavy throughput.
The experiment needs no new TTR pair command. Effect strength and layout controls remain missing.

## TTR review and authority

[TTR318](TTR318Review.md) reviews temporal tracking, catalog polling, and verified archive reuse.
TTR318-A and TTR318-B are proposals awaiting human approval. No worker receives an execution assignment.
The coordinator stores advisory review `nuiak-focus313-ttr318-review-01` at cursor 145.
Its SMB copy passes exact readback. Forwarding and peer acknowledgment remain unconfirmed.
The maintainer's rule now appears in AGENTS.md and CoordinatorWorkflow.md.
The coordinator stores result `nuiak-focus313-result-01` at cursor 146.
The SMB result contains 2,196 bytes and passes exact readback.
Its SHA-256 is `848c5086cbfe2b0604ec78ee2aa5ea7f786a526de9a09c9bd0b984598dec2acf`.

| Outcome | State |
| --- | --- |
| Software verification | 34 focused tests pass; current offline build, 14 XCTest tests, and 173 Swift Testing tests pass |
| Data eligibility | Original training roles remain unchanged; authored outputs remain development-only |
| Producer integration | Headless rendering and independent intake pass for the tested placeholder layouts only |
| Model acceptance | Both candidates fail; no promotion |

## Evidence

Raw evidence stays under `reports/work/FOCUS-313/`. Model checkpoints remain local and unpromoted.
Build, test, rendering, and training logs stay under `.build/focus313-*`.
The registration records exact input, model, source, and helper hashes before training.
No Git write, new training role, model export, or navigation authority occurs.

## Next substantial tranche

FOCUS319 completes the supported authored comparison. Its candidate improves authored decisions but loses native successes.
Use its retained examples to measure conflicting training signals before another fit. Keep the original views and previous-success checks.
Do not treat stronger synthetic scores as native improvement.
