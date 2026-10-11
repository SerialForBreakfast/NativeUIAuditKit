# FOCUS323 — direct constrained output fit

Owner: Maximum-mini-NUIAK.

**Decision: reject the candidate.** It adds 1 correct distraction decision but does not improve native focus detection.

## Model results

| Measure | FOCUS313 | FOCUS319 / FOCUS322 | FOCUS323 |
| --- | ---: | ---: | ---: |
| Native correct / 640 | 598 | 581 | 581 |
| Replay correct / 668 | 668 | 646 | 646 |
| Reversed native correct / 640 | 602 | 579 | 579 |
| Reversed replay correct / 668 | 666 | 644 | 644 |
| Lighting correct / 226 | 226 | 226 | 226 |
| Left distraction correct / 226 | 144 | 160 | 161 |
| Left false changes / 226 | 82 | 53 | 53 |
| Center false changes / 226 | 99 | 136 | 136 |
| Tiny changes correct / 4 | 0 | 0 | 0 |
| Placeholder movements correct / 8 | 2 | 8 | 8 |

The 1 gained left-distraction decision was previously an abstention. It was not a false change.
Across the 7 main sets, the candidate loses 0 successes against FOCUS319 and FOCUS322.
It still loses 33 native successes and 22 replay successes against FOCUS313.
The native set retains 2 missed changes and 57 abstentions.
All 4 forward and reversed tiny changes remain misses. All 8 identical tiny pairs remain correct.
The candidate fails 8/24 nuisance strength and order checks against DTM085.
The other 23 strength and order summaries match FOCUS319. Equal summaries do not prove identical case decisions.

## Can this output layer fix the tiny cases?

A post-evaluation diagnostic maximizes each tiny-case score under the same training constraints and coefficient limits.
It uses the fixed hidden features. It does not fit or select another candidate.
The best possible scores range from -6.471 to -4.330 across the 8 forward and reversed cases.
Every bound remains below the change threshold of 1.735.
Therefore, no output coefficients within this tested family and its constraints can detect these cases.

This result does not prove that all score-based models fail.
It does not establish bounds for different hidden features, coefficient limits, or training constraints.
Each bound is optimized separately. The diagnostic does not claim one model achieves every bound together.
The known development failures remain excluded from training and final evaluation.

## Method

The experiment fits 9 output coefficients over the initial FOCUS322 nonlinear features.
It keeps image branches, hidden features, normalization, data roles, and thresholds unchanged.
The existing constrained routine uses the resident SciPy HiGHS solver with 2 threads.
It minimizes weighted linear margin shortfall with each coefficient between -1 and 1.
The target remains `log(0.85/0.15) + 0.25`.
The solver protects 1,866 successful training rows. These rows are not independent trials.
Original weights and the authored schedule retain coefficient 0.25.

The experiment runs 1 direct solve. It does not use epochs, a sweep, or evaluation-based selection.
FOCUS322 uses squared margin loss. This comparison changes both the loss and the update method.
Do not attribute every difference to the solver alone.

## Training result

The weighted margin shortfall falls from 0.276883 to 0.273508, about 1.22%.
The fit takes 0.018 s. All 1,866 protected training decisions remain correct.
The float32 model has minimum protected slack 0. Its measured objective matches the solver within 0.000000003.
Original training correctness remains 1,649/1,820. Authored correctness remains 217/240.
Authored false changes fall from 14 to 12, but abstentions rise from 9 to 11.
This is reduced confidence in 2 mistakes, not 2 additional correct detections.

All 38 frozen tensors remain unchanged.
Cached and image-based predictions match exactly on 8 retained parity examples.
Checkpoint reload preserves those predictions exactly.

## Verification scope

The experiment uses the existing image evaluator and comparison reports.
It tests native, reversed, replay, nuisance, authored, and tiny-change cases.
The comparison includes FOCUS313, FOCUS319, FOCUS320, FOCUS321, FOCUS322, and DTM085.
Previously inspected reserved cases remain development evidence. They do not become untouched final evaluation.

Raw evidence stays under `reports/work/FOCUS-323/`.
No capture, dependency download, export, worker execution, or production change occurs.

All 59 focused Python tests pass.
The offline Swift build passes. All 14 XCTest tests and 173 serial Swift Testing tests pass.
The build takes 0.30 s. Swift Testing takes 53.97 s.
Fit through complete evaluation takes 173.54 s. Outputs occupy about 2.04 MB.
Observed process memory is about 1.57 GB during evaluation, not a measured peak.

| Artifact | SHA-256 |
| --- | --- |
| Candidate | `a07a3b0436c0137a2f1076fae601e07a745c40e48e7d86da31da5b77f07656df` |
| Comparison report | `212ef8c8b04f98b2f7e7606b20bde19c5e565a328800cffa1a438ae1fb5ea495` |
| Tiny-case bounds | `ac88a2856c80abe0958912a72980e7c2bef8a9fc5e7c7c24d6f16924d0b8ae13` |

## Independent outcomes

The coordinator stores start and result messages but does not confirm forwarding.
The result passes exact SMB readback at `nuiak/responses/nuiak-focus323-result-01.json`.
Sillycon-TTR acknowledgment remains unconfirmed. Existing renderer work remains open.

- Software: focused tests, the offline build, and serial tests pass.
- Data: existing training roles remain unchanged. Authored rendering does not establish native fidelity.
- Integration: image/cache parity passes. Apple conversion and a new TTR runtime test do not occur.
- Model: native improvement does not occur. Previous-success requirements against earlier controls remain unmet. No model is promoted.

## Next substantial tranche

Stop repeated adjustments to these 2 scalar scores.
Audit the detail features before the model reduces them to a scalar.
Use matched focus changes and artwork-only changes from retained training examples.
Measure separation by control size, effect strength, and surrounding content.
Use known native failures for diagnosis only. Do not move them into training.
If the richer features separate the training cases, test 1 bounded readout change against all previous successes.
If they do not, identify the missing visual evidence before asking for more images.
Reuse existing renderer controls when new paired examples become necessary. New producer work still needs human approval.
