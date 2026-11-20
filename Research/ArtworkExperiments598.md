# Artwork and focus experiments

Maximum-mini-NUIAK admitted 27 T63 diagnostics. Each scores one of 8 completed HARDNEG596 fits or FDR001 on one of 3 panels. Shelf and Northstar supply 3 frames and 8 boxes. Field Atlas and Cinema Programme each supply 3 frames and 12 boxes. Each job has an 800 s guard and 100 MB output cap. [Specifications](../reports/work/ART598/descriptions.json) and [admission check](../reports/work/ART598/admission.json).

Use the 0.85 unique-selection rule. Check baseline decisions and crop hashes against retained local production references. Inspect threshold crossings and losses per frame. Compare each fit against the control for its seed. Northstar uses the 2 retained model proposals. Other panels use supplied boxes. All results describe development evidence. Reuse successful candidates on the exposed real panel before reserving fresh application flows.

## Capture analysis

The 304 training frames comprise 76 scenes with 4 positions each. Three adjacent position changes per scene give 228 contrasts. On each contrast sum absolute RGB differences in the union of the departing and arriving control boxes. Repeat with 16% expansion on each side. Divide by total full-frame change, pool the three contrasts per scene, then report the median scene fraction. The rectangles approximate the production crop footprint before resizing. They do not measure which pixels influence a prediction.

| Configured cue | Scenes | Body share | Expanded share |
|---|---:|---:|---:|
| Glow | 6 | 1.01% | 99.91% |
| Growth | 5 | 59.69% | 100% |
| Combined | 3 | 42.63% | 99.55% |
| Parallax | 30 | 54.61% | 98.13% |
| Native button | 15 | 62.18% | 82.32% |
| Background | 7 | 100% | 100% |
| Border | 10 | 100% | 100% |

[Per-scene measurements](../reports/work/ART598/crop-margin.json). The next generation comparison should hold assets and layout fixed across glow and border. Cross that factor with bright versus dark neighboring artwork. Record stable focus IDs and negative competitors at each position. Compare crop-only versus expanded evidence after the production resize. This directly tests whether the retained halo survives resizing and helps the model choose correctly. The current source groups differ across cues, which limits causal attribution.

Sillycon-TTR reports 912 same-frame competitor observations for the 304 training frames. The producer plans a companion index. Verify its image hashes, bounds, identities, and role before using these as training negatives. Reserve all 56 sports frames for evaluation. Keep future real-app qualification independent of both Fixture splits.
