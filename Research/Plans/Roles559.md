# ROLES559 — Role-based detector classes (Screen Recognition style)

Date: 2026-11-01. Owner: Maximum-mini-NUIAK. Task authority: Tasks.md, RA557-16. Parent: CELLS558 (RA557-15).
Approved by the maintainer, 2026-11-01: "Lets try the new grouping."

## Problem

The detector separates classes by look, not by role. `primaryButton` and `secondaryButton` differ by fill.
On tvOS a filled button is usually the focused button, so the split mostly encodes focus. FocusRing already owns focus.
UIKit, SwiftUI and the accessibility `.button` trait have 1 button. Apple Screen Recognition (Zhang et al., CHI 2021) uses about 12 role classes.
The 41-class gate DS-G8 (≥ 0.85) is not met: Run 013 = 0.6322 on 13 supported classes.

## Role map

`scripts/roles559.py` maps the 41 schema classes to 13 roles at training time. The schema raw values do not change.

| Role | Schema classes |
|---|---|
| button | primaryButton, secondaryButton, destructiveButton, cancelAction, menuButton, link, disclosureGroup, keyboard and PIN keys |
| text | label |
| picture | imageView, mapView |
| textField | textField, secureField, searchField |
| toggle | toggle |
| adjustable | slider, stepperControl, picker, colorWell |
| segmentedControl | segmentedControl |
| pageControl | pageControl |
| cell | collectionItem, listRow |
| bar | tabBar, navigationBar, toolbar, sidebar, statusBar |
| dialog | alert, actionSheet, sheet, popover, contextMenu, tooltip |
| indicator | progressView, activityIndicator, refreshControl, scrollIndicator, dynamicIsland, homeIndicator |
| container | webContent |

`unknown` has no role. Keys map to `button`. This replaces CELLS558 S1.2 for this run only: by role a key is a button, not a content cell.
Fine roles (filled or tinted, destructive) can come later from a small attribute step after detection. They are not detector classes.

## Experiment

| Run | Data | Labels |
|---|---|---|
| C2-r2 (control) | CELLS558 C2 membership | 41 schema classes |
| R1 | the same 880 rows, groups and boxes | 13 roles |

Both: T89, initialization `nativeui-tvos-v3.0`, 30 epochs, learning rate 0.0001, fixed-last, 2 GiB, a 7,200 s limit.
`scripts/roles559_evaluate.py` scores v3, C2-r2 and R1 on the 13 roles. 41-class output maps to roles, then gets per-role NMS at IoU 0.45.

## Decision rule (fixed before registration)

- Supported: R1 ≥ C2-r2 on NewsTV development card recall, pill recall and focused coverage, and higher on at least 1;
  synthetic role AP50 on tvos557 and tvos558 ≥ C2-r2 − 0.01; no role loses more than 0.02 AP50.
- Contradicted: R1 is lower on any development metric and lower on synthetic AP50.
- Inconclusive: any other result. Then record it and do not repeat the same run.
- Supported next action: propose a role-based model track (schema version, Core ML parity, consumer mapping). No promotion here.

## Time

About 1 h of setup, about 1 h for R1 after C2-r2, and about 20 min of evaluation.
