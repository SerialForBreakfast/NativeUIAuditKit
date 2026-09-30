# Representative focus validation — 2026-09-29

Fixed threshold **0.85**. Native bounds; production16%/256 crops. Both frozen models scored312/312 inputs; no failed predictions.
Paired targets and complete-frame competitors are separate correlated populations, not624 independent examples.
These are development diagnostics; no independent qualification or export parity claim.

## SYNTH05 native-fixture diagnostic

| Stratum | Positive / paired negative support | Shipped TP / FP | FDR-010 TP / FP |
|---|---:|---:|---:|
| buttons | 4 / 4 | 0 / 0 | 4 / 0 |
| tabs | 10 / 10 | 1 / 0 | 10 / 0 |
| artwork | 32 / 32 | 6 / 2 | 0 / 0 |
| rows | 4 / 4 | 0 / 0 | 4 / 0 |

Complete-frame selection (50 frames):
- shipped: {"no_focus": 39, "unique_correct": 7, "wrong": 4}; absent outcomes=0.
- fdr010: {"no_focus": 32, "unique_correct": 18}; absent outcomes=0.

The candidate handles the18 native button/tab/row cases but misses all32 artwork positives. Its75% macro recall hides a zero artwork stratum; it is not a pass.
The shipped model has7 unique-correct,4 wrong and39 no-focus frames. FDR-010 has18 unique-correct,0 wrong and32 no-focus.
All native selected-but-unfocused tab competitors remain negative. Bright selection is not focus.
One reported Simulator/OS, dark theme, seed7, shared procedural ancestry: no independent-source claim.

## Retained real-screen transfer

All362 saved scores per model were checked;315 settled candidate crops enter the descriptive table.47 remain outside that population. Preserve per-benchmark exclusions and complete-frame coverage.
| Stratum | Positive / negative support | Shipped TP / FP | FDR-010 TP / FP |
|---|---:|---:|---:|
| buttons | 3 / 3 | 3 / 0 | 0 / 0 |
| tabs | 3 / 21 | 1 / 10 | 0 / 0 |
| artwork | 12 / 181 | 5 / 31 | 1 / 7 |
| rows | 7 / 64 | 2 / 0 | 2 / 0 |
| other | 2 / 19 | 1 / 0 | 0 / 0 |

Four-stratum macro recall: shipped50.89%, FDR-0109.23%. Real buttons/tabs both0 for FDR-010, despite synthetic success. Unknown independence and tiny support preclude broad performance claims.
The24-frame benchmark retains13 complete settled frames: shipped3 unique-correct, candidate2. The separate eight-frame benchmark is not silently added to the complete-frame denominator.
The companion `real-transfer.json` preserves each benchmark, exclusions, incomplete frame states and source bindings.

## Decision

**Do not export FDR-010 or repeat unchanged training.** Keep shipped unchanged. Collect missing artwork/focus-mechanism/context diversity and genuine OS transfer references; retain buttons/tabs/rows for nonregression.
Backend differences: shipped CoreML CPU; candidate PyTorch CPU. This is not export parity, and elapsed times are not directly comparable latency.
Ranked machine-readable misses and false positives are in `errors.json`; every entry binds exact sample ID, original image, bounds and qualified crop. No new crop or image inference was used to render this report.
