# HARDNEG596 — FocusRing hard negatives from synthetic tvOS screens (no capture)

Date: 2026-11-07. Owner: Maximum-mini-NUIAK. Parent: ARTPARITY595 (Tasks.md P0 visual parity). Requested: "add some substantial experiments to the queue".
Results stay provisional until Joe reviews them. No promotion. The detached runner executes.

## Problem

ARTPARITY595 found that FocusRing scores unfocused bright artwork and plain background as focused
(shelf competitor 1.000; Northstar Sam 1.000 over focused Alex 0.996; plain crop 0.998). 0/8 TTR native-truth frames are correct.
New Fixture captures wait on a TTR app replacement. The tvos560 synthetic screens already label every control as focused or unfocused.

## Data

- Base: the artwork crop corpus used by NCTRL417 (`jitter413-crops-jitter/crops.json`), unchanged.
- New crops (`scripts/hardneg596_membership.py`), production crop path, from tvos560:
  `tab`, `button`, `row` (native families) and `cell`, `plain` (artwork families: unfocused and focused cards, empty background as label 0).
  tvos560 `train` split → train; `test` split → development; images whose pixels occur in train are skipped; groups are per image.
- Selection reuses `native_control_membership.select` (the T54 code): 3,600 rows per label; mixed arms use 900 native rows per label.

| Arm | Artwork part | Native part | Seeds |
|---|---|---|---|
| control | base | none | 371, 372 |
| mixed | base | generator tab/button/row | 371 |
| hardneg | base + generator cells + plain negatives | none | 371 |
| hardneg-mixed | base + generator cells + plain negatives | generator tab/button/row | 371, 372 |

Training: T06 (`hcf_factor_train376.train`), profile `balanced`, 30 epochs, fixed-last, initialization `fdr001` (the NATIVE590/593 base).
Evaluation: T37 (`native_selection404.run`) on the completed NCTRL417 native development captures and proposals for button, row and tab,
for every arm and for the `fdr001` baseline. After training, score the ARTPARITY595 development frames (shelf pair, ArtworkEligibility-v1, Northstar) offline.

## Decision rule (fixed before registration)

- Supported: hardneg-mixed beats control (both seeds) on correct native selections without new wrong selections, and on the
  ARTPARITY595 frames the unfocused-artwork and plain crops fall below 0.85 while the focused crops stay at or above 0.85 in more frames than the baseline.
- Contradicted: hardneg-mixed loses correct selections against control in both seeds, or the artwork false positives do not fall.
- Inconclusive: any other result, or seed 371 and 372 disagree. Record it; do not repeat the same runs.
- Attribution: hardneg vs control isolates the artwork negatives; mixed vs control isolates native generator crops.
- Limitation: development frames are synthetic or previously exposed. A supported result goes to real reviewed positives (VisualParityAudit 19) and TTR Programme holdout before any claim.
