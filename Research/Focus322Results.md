# FOCUS322 — score separation and protected margins

Owner: Maximum-mini-NUIAK.

**Decision: reject the candidate.** It preserves the FOCUS319 decisions but does not improve them.

## Model results

| Measure | FOCUS313 | FOCUS319 | FOCUS321 | FOCUS322 |
| --- | ---: | ---: | ---: | ---: |
| Native correct / 640 | 598 | 581 | 520 | 581 |
| Native training correct / 548 | 514 | 491 | 432 | 491 |
| Inspected development correct / 40 | 33 | 38 | 36 | 38 |
| Inspected reserved correct / 52 | 51 | 52 | 52 | 52 |
| Replay correct / 668 | 668 | 646 | 640 | 646 |
| Reversed native correct / 640 | 602 | 579 | 494 | 579 |
| Lighting correct / 226 | 226 | 226 | 226 | 226 |
| Left false changes / 226 | 82 | 53 | 48 | 53 |
| Center false changes / 226 | 99 | 136 | 125 | 136 |
| Tiny changes correct / 4 | 0 | 0 | 0 | 0 |
| Placeholder movements correct / 8 | 2 | 8 | 6 | 8 |

FOCUS322 loses 0 decisions and gains 0 against FOCUS319 across the 7 main comparison sets.
The largest probability difference is less than 0.00000024. This is not a meaningful model improvement.
Compared with FOCUS313, it still loses 33 native successes and gains 16.
It still loses 22 replay successes and fails 8/24 nuisance strength and order checks against DTM085.
All 4 forward and reversed tiny changes remain misses. All 8 identical tiny pairs remain correct.
The native set has 57 abstentions and 2 missed changes.
Previously inspected reserved examples remain development evidence, not untouched final evaluation.

## What the scores permit

The audit uses the pinned FOCUS321 cache. It reads training scores only.
It includes 1,820 original views and 240 reviewed authored pairs.
Repeated and reversed views are not independent trials.

The solver finds no linear rule that separates every label at the fixed thresholds.
This remains true when the rule can use negative coefficients.
Original examples and authored examples also fail their separate positive-coefficient tests.
No exact pair of scores has conflicting labels in the combined set.
This result limits linear rules. It does not prove that every nonlinear rule must fail.

The next check protects 1,866 successful training rows from the unchanged FOCUS319 model.
It preserves their original signed scores up to `log(0.85/0.15) + 0.25`.
The constrained linear solution has the same weighted margin shortfall as the unchanged rule: 0.276883.
Another scalar fit is not justified under those constraints. No scalar candidate runs.

## The correction

The experiment adds a 33-parameter residual network over the 2 frozen scores.
It uses 8 tanh units, training-only normalization, and zero output weights at initialization.
The existing trainer runs 30 epochs with seed 42, batch 16, and learning rate 0.001.
It preserves original weights and auxiliary coefficient 0.25.
It uses squared margin loss instead of binary cross-entropy.
The experiment selects the last checkpoint. Thresholds remain 0.15 and 0.85.

After each update, the guard checks all successful training rows.
If an update breaks a protected margin, the guard halves it up to 12 times.
If no fraction passes, the guard restores the previous parameters.
The guard protects 3,307 scheduled rows, including repeated authored examples.
These repetitions do not increase independent support.

## Why training makes almost no progress

The guard limits all 3,420 updates. It fully restores 3,356 updates.
Original training decisions remain 1,649/1,820 correct. Authored decisions remain 217/240 correct.
The fit takes 7.71 s. Setup, parity checks, and fit take 8.32 s.
All 36 frozen tensors remain unchanged, including 2 normalization buffers.
Cached and image-based scores match exactly on 8 retained parity examples.
Reloaded checkpoint scores also match exactly.

A separate training-only diagnostic tests fixed nonlinear features from the initial network.
It allows 9 output coefficients within [-1, 1] while retaining the same protected margins.
The solver lowers weighted margin shortfall from 0.276883 to 0.273508, about 1.22%.
This is a feasibility result, not another trained or evaluated model.
The diagnostic does not use evaluation membership or select deployment thresholds.

The strict update guard blocks the tested optimizer direction, despite a small feasible improvement elsewhere.
Do not conclude that all nonlinear corrections fail. Do not repeat this backtracking fit with more epochs.
The next useful comparison must separate the constraints from the method that applies updates.

## Verification

All 55 focused Python tests pass.
The offline Swift build passes. All 14 XCTest tests and 173 serial Swift Testing tests pass.
Swift Testing takes 54.73 s.
The tests cover conflicting labels, linear separation, protected updates, deterministic fits, frozen branches, and invalid checkpoint versions.
The tests also preserve existing trainer behavior when the new modes are off.

Raw evidence stays in `reports/work/FOCUS-322/`.
The experiment uses resident dependencies. It starts no capture, download, export, or production change.

The audit takes 0.04 s. Fit through the complete comparison takes 185.37 s.
Outputs occupy about 2.04 MB. The observed process memory is about 1.49 GB during evaluation, not a measured peak.

| Artifact | SHA-256 |
| --- | --- |
| Candidate | `59b85aa1e61e8ae5464a0cb9a4165db815986c3703f2277d46d747458d79b7b0` |
| Comparison report | `0eef5081793e07ca9519d54fe02e041a48e4be669589bae0351c7fc86f239eaf` |
| Separation audit | `45fb8a2765fb903621a0451fb92db502083316b2cbd2dad62bfbc023c7ed0f66` |
| Guard diagnosis | `904ba5412e42330d00ac401c8ebe53796a4a06068cf5b072e855e4f13ad54a94` |

## Independent outcomes

The coordinator stores the start and result messages but does not confirm forwarding.
The result passes exact SMB readback at `nuiak/responses/nuiak-focus322-result-01.json`.
Sillycon-TTR acknowledgment remains unconfirmed. The update leaves the existing renderer request open.

- Software: focused tests, the offline build, and serial tests pass.
- Data: existing roles remain unchanged. Authored labels do not establish native fidelity.
- Integration: cached scores and image inference agree. No Apple conversion or TTR runtime qualification occurs.
- Model: no improvement over FOCUS319 occurs. Existing previous-success requirements remain unmet. No model is promoted.

## Next bounded comparison

Keep the image branches and initial nonlinear features fixed.
Fit only the 9 output coefficients with an explicit constrained solver, rather than blocking an unconstrained optimizer after each update.
Use the same training-only margin constraints. Compare the unchanged, backtracked, and directly constrained results on identical membership.
Keep the existing native, tiny-change, nuisance, reverse-order, and previous-success checks.
If the directly constrained result also adds no useful decisions, stop score-only changes and identify missing image evidence.
The 1.22% training diagnostic is not a forecast of native improvement. This next comparison does not require TTR capture or GPU work.
