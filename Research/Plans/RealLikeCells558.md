# CELLS558 — Real-like cells and tab pills for the tvOS detector

Date: 2026-11-01. Owner: Maximum-mini-NUIAK. Task authority: Tasks.md, RA557-15. Parent: REALAPP557.
Evidence: [RA557-01](../../reports/work/REALAPP557/ra557-01-box-tightness.md), [RA557-02](../../reports/work/REALAPP557/ra557-02-text-candidates.md),
[RA557-13](../../reports/work/REALAPP557/ra557-13/report.md). Box rule: [NativeUIElementDetection §5.2.1](../NativeUIElementDetection.md).
This plan admits no job and starts no training.

## Problem

RA557-13 taught whole-cell boxes on synthetic screens (card median IoU 0.852 → 0.997), but real-app results got worse:
NewsTV card recall fell from 27 to 12 of 54, and `label` lost 0.049 AP50. 3 data facts explain this:

1. **Synthetic cells do not look like real cells.** Every generator cell has artwork and at most 1 short title line.
   Real tvOS cells often hold a text block (headline, summary, metadata) inside the cell. NewsTV cells are about 686 px tall at 4K.
2. **Most `collectionItem` boxes are keys, not content cards.** Keyboard keys (4,480) and PIN keys (1,760) dominate the training boxes.
3. **Several families barely vary.** Unique screens of 200: `tvOSAlert` 2, `tvOSTopTabBar` 4, `tvOSAudioSubtitles` 4, `tvOSSplitSettings` 6, `tvOSSettings` 8, `tvOSSidebarMenu` 12.
   The detector has seen only 4 distinct tab bars, which fits the tab-pill result (1 of 153).

## Rules

- NewsTV, Photo Guessing Game and Swiftfin are evaluation-only. Do not copy their layouts, text or pixels. Use generic tvOS patterns with random variation.
- Box rule §5.2.1: a cell box is the whole cell. Text inside a cell keeps its own `label` box.
- Artwork inside a cell is part of the cell. It is not a separate `imageView`. Label `imageView` only for a standalone image.
  Reason: the RA557-13 candidate called 38 NewsTV cards `imageView`. This rule needs a check against the taxonomy before adoption (S1).
- The NewsTV pilot holdout is spent for detector comparisons: RA557-13 used it for the baseline and 1 candidate.
  Compare candidates on the development references (S4). A fresh holdout comes from new flows (RA554-13).
- Training uses T89 within its 1,800 s limit, the standing approval, an ExperimentLog entry before registration, and no promotion.

## Steps

### S1 — Decide 2 label details (about 20 min, decision)

1. Artwork inside a cell: no separate `imageView` (recommended), or keep the current nested `imageView`.
2. Keyboard and PIN keys: keep them as `collectionItem` with a sampling cap, or relabel them `secondaryButton`.
   Recommendation: keep the class, and cap keys at 25% of `collectionItem` boxes in training. Relabeling changes the taxonomy meaning for every consumer.

### S2 — Fix generator variation (about 1 h)

For the 6 low-variation families, make the seed change real content:
- `tvOSTopTabBar`: tab count 3–8, label sets from a word list, focused index, selected index (different from focused in at least 30% of screens), pill style (filled focus, underline, plain).
- `tvOSAlert`, `tvOSSettings`, `tvOSSplitSettings`, `tvOSSidebarMenu`, `tvOSAudioSubtitles`: vary item count, text, focused item and light or dark theme.

Acceptance: ≥ 150 unique screens of 200 for each of these families; all boxes still match their views; all other families unchanged (diff check like RA557-13).

### S3 — Add a real-like cell family (about 1.5 h)

Add 1 generator family, `tvOSContentCells`, with 6 cell variants. Each screen draws 1–3 rows; the seed picks variants, sizes and text.

| Variant | Content inside the cell |
|---|---|
| A | Poster, 1–2 title lines below |
| B | Landscape artwork, headline (1–2 lines), summary (2–3 lines), metadata row |
| C | Artwork with the title on a gradient inside the image |
| D | Text-only panel: headline and summary, no artwork |
| E | Wide hero cell with a nested `primaryButton` |
| F | A shelf scrolled so that the first and last cells are partly off screen (clipped boxes) |

Vary: cells per row 2–6, aspect ratios, font sizes, text length, theme, and the focused cell (scale, glow, filled text panel).
Labels: whole-cell `collectionItem`; each text line block `label`; nested buttons with their own class.

Acceptance: 400 unique screens; every cell box contains its text boxes; a sample review of 20 screens confirms that boxes match the drawn cells.

### S4 — Development references (about 30 min)

- NewsTV development frames (10): SDK rectangles for cards, main tabs and categories (23 per frame). They are unreviewed for boxes,
  but the pilot review confirmed 207 of 207 NewsTV SDK rectangles. Label them "SDK-registered, pilot-confirmed source".
- The synthetic clean test set: pixel-unique test images from the regenerated dataset.
- Retention: `label` AP50 and every class AP50 on the original-convention clean test set (RA557-13 method).

### S5 — Train and compare (2 runs, about 25 min each)

| Run | Data | Purpose |
|---|---|---|
| C1 | Whole-cell labels and S2 variation fixes, key cap | Control: does variation alone recover tabs and keep `label`? |
| C2 | C1 plus `tvOSContentCells` | Test the real-like cells |

Both: T89, initialize from `nativeui-tvos-v3.0`, 30 epochs, learning rate 0.0001, fixed-last, a stratified subset that fits 1,800 s.
Register a third run only if C2 passes the development gates but fails retention (condition fixed before C1 starts).

### S6 — Measure and decide (about 30 min)

| Gate | Set | Baseline (v3, PyTorch) | Supported if |
|---|---|---|---|
| Card recall | NewsTV development, SDK cards | measure in S4 | higher than baseline |
| Card median IoU | NewsTV development | measure in S4 | ≥ 0.75 |
| Tab and category pill recall | NewsTV development, SDK tabs | measure in S4 | higher than baseline |
| Focused-control coverage | 21 focus development frames | 9 of 21 | higher |
| `label` AP50 loss | synthetic clean test | 0 | ≤ 0.02 |
| Any class AP50 loss | synthetic clean test, original convention | 0 | ≤ 0.02 |

Report Core ML parity for a supported candidate before any TTR replay. No promotion in this plan.

## Time

About 5–6 h of agent work. Slow steps: the generator changes and their checks, 2 training runs, and evaluation.

## Maintainer decisions

Approved 2026-11-01: both S1 decisions as recommended.
- S1.1: artwork inside a cell is part of the cell, not a separate `imageView`.
- S1.2: keyboard and PIN keys stay `collectionItem`; training caps keys at 25% of `collectionItem` boxes.


1. S1.1: artwork inside a cell is not a separate `imageView` (recommended).
2. S1.2: keep keys as `collectionItem` with a 25% cap (recommended), or relabel them.
