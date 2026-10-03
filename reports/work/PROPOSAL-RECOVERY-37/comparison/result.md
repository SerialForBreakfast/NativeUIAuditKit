# Proposal recovery and selective semantics

Reused development data. These are proposal recall figures, not focus selection or precision.

| Arm | Body matches /583 | Focused matches /46 | Proposals |
|---|---:|---:|---:|
| yolo | 346 | 21 | 1084 |
| raster | 214 | 20 | 375 |
| vision | 298 | 35 | 1104 |
| ocrSupportedRows | 11 | 5 | 23 |
| yoloRaster | 393 | 32 | 1386 |
| allGeometry | 432 | 42 | 2289 |

Selective iOS result: `{'samples': 24, 'originalExact': 12, 'coarseButton': 24, 'hinted': 3, 'correctHints': 3, 'wrongHints': 0}`.
Cancel is a selective hint; other labels abstain. No truth relabeling or semantic accuracy extrapolation.
