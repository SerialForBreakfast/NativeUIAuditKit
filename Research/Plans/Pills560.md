# PILLS560 — Tab pills as buttons (role detector)

Date: 2026-11-01. Owner: Maximum-mini-NUIAK. Task authority: Tasks.md, RA557-17. Parent: ROLES559 (RA557-16).
Requested by the maintainer, 2026-11-01: "Fix pill box fit."

## Diagnosis (R1 on NewsTV development frames, 170 SDK pills)

- R1 overlaps 168 of 170 pills. It calls 120 of them `text`, 27 `button` and 21 `cell`.
- When R1 says `button`, the box fits: median IoU 0.89, width ratio 1.03, height ratio 1.08.
- The `text` boxes are a median 2.07 times wider than 1 pill: R1 reads a row of tab words as 1 text line.
- The issue is the class and the grouping, not box tightness.

Generator causes (`TabBarView`):
1. Tab text has no nested `label` box. In all other families plain text is `label`; here the same plain text must be `button`.
2. The tab box includes a 9 px underline strip below the pill.
3. Each screen has 1 centered tab row with a headline. Real tvOS apps often show 1–2 left-aligned rows above content, with no tab focused.

## Changes

- A shared `TabRow` view: each tab has a pill `button` box (padding included, underline excluded) and a nested `label` box for its text.
- `tvOSTopTabBar` uses `TabRow`, with spacing 4–30 px and leading or centered alignment.
- A new family `tvOSTabRows` (400 images at the 5,400 base): 1–2 tab rows, then 1 content shelf from `CellRowSpec`.
  Focus: a tab in row 1 (30%), a tab in row 2 (30%), or a cell (40%). Selected-but-not-focused tabs stay as hard negatives.
- All other families keep identical pixels (the new family is generated last). Check: SHA-256 match for every unchanged family.
- Real apps stay evaluation-only. Use generic tab words only.

## Experiment

| Run | Data | Labels |
|---|---|---|
| R1 (control) | ROLES559 rows | 13 roles |
| R2 | R1 rows; `tvOSTopTabBar` rows replaced by regenerated images; plus 120 train and 16 calibration `tvOSTabRows` images | 13 roles |

T89, initialization `nativeui-tvos-v3.0`, 30 epochs, learning rate 0.0001, fixed-last, 2 GiB. Restart at 7,200 s after a 1,800 s timeout, as for R1.

## Decision rule (fixed before registration)

- Supported: NewsTV development pill recall (button, IoU ≥ 0.5) ≥ 60 of 170 (3 times R1);
  card recall ≥ 58 of 60 and card median IoU ≥ 0.90; focus coverage ≥ 6 of 21 (R1);
  role AP50 ≥ R1 − 0.01 on tvos557 and tvos558; `text` and `button` AP50 lose ≤ 0.02.
- Contradicted: pill recall ≤ 30 of 170, or card recall < 55 of 60.
- Inconclusive: any other result. Record it; do not repeat the same run.
- No promotion. A supported R2 goes to a fresh holdout (RA554-13) and Core ML parity before any TTR replay.

## R3 — PIN slot repair (added 2026-11-02, after R2)

R2 result: pills 160/170, focus 12/21, cards 60/60 (IoU 0.937). The `button` loss on old test sets is the old tab-label convention only.
The real loss is `textField` on PIN slots: R2 misses 57 of 102 at score 0.25 (R1: 5); median `textField` score 0.26 (R1: 0.96).
Hypothesis: new pills teach "small box with text inside = button + nested label"; PIN slots look the same, and training has only 13 PIN screens (median family: 30).

| Run | Data |
|---|---|
| R2 (control) | PILLS560 R2 rows |
| R3 | R2 rows plus 20 train and 2 calibration `tvOSPINEntry` screens (seed 561; pixels identical in tvos558 and tvos560) |

T89, initialization `nativeui-tvos-v3.0`, 13 roles, 30 epochs, learning rate 0.0001, fixed-last, 43,200 s guard.
Scoring: `scripts/roles559_evaluate.py` (development, old sets) and `scripts/pills560_retention.py` (sets without the tab-label confound, PIN slots).

Decision rule (fixed before registration):
- Supported: pills ≥ 150/170; focus ≥ 10/21; cards ≥ 58/60 with median IoU ≥ 0.90; on tvos558 without tab bars, AP50 ≥ R1 − 0.01,
  `textField` ≥ R1 − 0.02, and no role loses more than 0.02 against R1; tvos560 tab `button` AP50 ≥ 0.95.
- Contradicted: `textField` on tvos558 without tab bars stays more than 0.05 below R1, or pills fall below 120/170.
- Inconclusive: any other result. Supported next step: fresh holdout (RA554-13) and Core ML parity. No promotion.

## R4 — rule B: text inside a button is part of the button (added 2026-11-02, after R3)

R3 result: inconclusive. PIN slots 64/64 and `textField` 1.000, but focus 8/21 and tab-label `text` 0.944 → 0.447.
Cause: conflicting labels. Tab pills and context-menu items had nested `text` boxes; PIN and keyboard keys had none.
Maintainer decision, 2026-11-02: rule B. No `text` box inside a `button` box. This matches Apple Screen Recognition; OCR reads the button words.

Rule B is a role-map rule (`scripts/roles559.py`, `button_text=False`). A `text` box is removed when at least 90% of it lies inside a `button` box.
The 41-class sidecars and all pixels stay unchanged. No regeneration.

| Run | Data |
|---|---|
| R3 (control) | `membership-r3.json` |
| R4 | `membership-r4.json`: R3 rows, groups and roles; 1,594 `text` boxes inside buttons removed (`tvOSTabRows`, `tvOSTopTabBar`, `tvOSContextMenu`) |

T89, initialization `nativeui-tvos-v3.0`, 13 roles, 30 epochs, learning rate 0.0001, fixed-last, 2 GiB, 43,200 s guard.
Scoring: both scorers with `--rule-b`. Truth drops `text` inside buttons for all models.
Each earlier model is also scored with rule B on its predictions (`+B`). This tests whether a post-processing filter alone is enough.

Decision rule (fixed before registration; R1 and R3 values are rule-B scores):
- Supported: pills ≥ 150/170; focus ≥ 10/21; cards ≥ 58/60 with median IoU ≥ 0.90; PIN slots ≥ 60/64;
  on tvos558 without tab bars, AP50 ≥ R1 − 0.01 and no role loses more than 0.02 against R1; tvos560 tab AP50 ≥ 0.95.
- Contradicted: focus ≤ 8/21 (no gain over R3), or pills < 120/170, or PIN slots < 50/64.
- Inconclusive: any other result.
- Filter check: if R3+B meets every synthetic gate that R4 meets, R4 adds only the development measures. Record that.
Supported next step: fresh holdout (RA554-13) and Core ML parity. No promotion.

Rule-B baseline, recorded before R4 started training: R1 tvos558 without tab bars AP50 0.938 (gate ≥ 0.928); R3 0.934, tab AP50 0.990, focus 8/21.
The `+B` filter lowers AP50 for every model, so post-processing is not a substitute. See the [report](../../reports/work/REALAPP557/pills560/report.md).

## R5 — system `.plain` focus platter (added 2026-11-02, after R4)

R4 result: contradicted (focus 8/21). All synthetic gates pass; tvos558 without tab bars AP50 0.961.
Diagnosis: NewsTV tabs use `.buttonStyle(.plain)`. On focus, tvOS draws a platter 1.3–1.6 times wider and 1.6–1.8 times taller than the button frame.
The generator drew its focused platter at the frame, so the model boxes the visible platter (R4 For You: 384 × 157 px; frame 266 × 99 px).
Calibration: NewsTV adds about 16 pt above and below and 16–34 pt at each side. TTR Fixture bordered buttons grow only about 4 pt per side (scale 1.03–1.11).

Generator change (`TabRow`): half of focused tab rows draw a white platter 12–18 pt beyond the frame vertically and 14–32 pt horizontally, with shadow and no scale.
A first version also scaled by 1.00–1.05. `captureFrame` reads the frame after `scaleEffect`, so the labels scaled too. The scale was removed before any use.
The same defect exists in old style 2 (scale 1.1): its labels are 1.1 times the frame. 59 such rows now use the platter instead and get frame labels. Remaining style-2 rows keep the defect (open).
The `button` box stays the frame (§5.2.1). A separate random salt keeps all other draws unchanged.
Dataset: `dataset/tvos560/platter`. Only `tvOSTopTabBar` and `tvOSTabRows` change; all other families must be pixel-identical to `dataset/tvos560/pills`.

| Run | Data |
|---|---|
| R4 (control) | `membership-r4.json` |
| R5 | `membership-r5.json`: R4 rows; `tvOSTopTabBar` and `tvOSTabRows` rows point to the regenerated images at the same index, rule-B labels |

Configuration as R4. Scoring: both scorers with `--rule-b`. New development measure: median best IoU on the 10 focused NewsTV pills (`newsFocusMedianIoU`; R4 value is measured with the same code before R5 results are read).

Decision rule (fixed before registration):
- Supported: NewsTV focused-pill median IoU ≥ 0.60 and focus ≥ 12/21; pills ≥ 150/170; cards ≥ 58/60, IoU ≥ 0.90; PIN slots ≥ 60/64;
  tvos558 without tab bars AP50 ≥ R4 − 0.01 and no role loses more than 0.02 against R4; tvos560 tab AP50 ≥ 0.95 (old tab images, frame labels).
- Contradicted: NewsTV focused-pill median IoU ≤ R4 + 0.03, or pills < 140/170.
- Inconclusive: any other result. No promotion.

R5 membership: `membership-r5.json` (sha256 a660a439…). 170 tab rows repointed; 53 have new pixels (48 train), 14 have new labels (former style-2 rows). Other rows keep their R4 pins.

## Style-2 label fix (2026-11-02, after R5) — no training run

Fix: `TabRow` style 2 (focused tab lifted by 1.1) now captures the button and label boxes outside `scaleEffect` (`captureFrame(id:if:)` and an invisible unscaled copy).
Check: `dataset/tvos560/style2` against `dataset/tvos560/platter`: pixels identical (3 `tvOSContentCells` images with ±2 rendering noise); labels change in 43 images, all focused style-2 tabs, exactly 1/1.1.
R5 membership has 3 affected training rows (`membership-r6.json`, sha256 4ba157f3…). A run cannot measure 3 labels above run-to-run noise, so no R6 job is registered.
Future datasets use the fixed generator.

Open (same defect, measured): focused content cells in `tvOSContentCells` and `tvOSTabRows` (and their play buttons) are 1.06 times the frame, because `.scaleEffect(1.06)` follows `captureFrame`.
`tvOSAppSwitcher` focused cards are 1.37 × 1.31 times unfocused cards; part of that may be layout, not scale (not checked).

## R6 — focused cells keep the frame box (added 2026-11-02, after R5)

Defect: `ContentCellsView.cell` applied `.scaleEffect(1.06)` after `captureFrame`. Focused cells, their text and play buttons were labeled 1.06 times the frame.
Fix: the cell is drawn scaled without captures; an invisible unscaled copy (overlay) records the boxes. Style-2 tabs use the same fix.
Dataset: `dataset/tvos560/cells6`. Against `style2`: pixels identical (1 noise image); labels change in 605 images (all exactly 1/1.06).
`tvOSAppSwitcher` also scales every card (focused 1.05, unfocused 0.95) and lays out focused cards larger; not changed here (open).

| Run | Data |
|---|---|
| R5 (control) | `membership-r5.json` |
| R6 | `membership-r6.json` (sha256 2de3e1a7…): R5 rows and pixels; `tvOSContentCells`, `tvOSTabRows`, `tvOSTopTabBar` rows use `cells6` labels. 148 rows change labels (132 train, 16 calibration) |

Configuration as R5. Scoring: both scorers with `--rule-b`. New measure: median best IoU on the 11 focused Photo Guessing Game cells (`otherFocusMedianIoU`; R5 is scored with the same code).
Synthetic test sets keep the old 1.06 labels on focused cells. AP50 is not affected (IoU about 0.89); AP75 may fall slightly.

Decision rule (fixed before registration):
- Supported: Photo focused-cell median IoU ≥ R5 + 0.02; focus ≥ 15/21; NewsTV focused-pill median IoU ≥ R5 − 0.02; pills ≥ 160/170; cards ≥ 58/60 with median IoU ≥ R5 − 0.01;
  PIN slots ≥ 60/64; tvos558 without tab bars AP50 ≥ R5 − 0.01, no role loses more than 0.02 against R5; tvos560 tab AP50 ≥ 0.95.
- Contradicted: Photo focused-cell median IoU ≤ R5, or focus < 13/21.
- Inconclusive: any other result. No promotion.
