# TRAIN666 H2: data and recipe for media-app cards (plan, 2026-11-25)

Joe, in chat on 2026-11-25: "Yes, plan H2". This plan belongs to row H2 of the "Active hypotheses" table in `Tasks.md`. It adds no hypothesis.
It is a plan only. Nothing is admitted, captured or trained. Results stay provisional until Joe approves them.
Rules: [model-improvement-loop](../ModelImprovementLoop/SKILL.md). Recipe source: [TRAIN666 W4](Train666.md).

## Why

Accepted evidence on the 31-layout set ([H1](../../reports/work/TRAIN666/h1-scoring-31layouts/README.md), [H3 arm G](../../reports/work/TRAIN666/h3-arm-g/README.md)):
- D1 equal-app localization recall is 0.588 and 0.610 against Standard 0.561. The intervals overlap. Plozz regresses (62 and 59 against 85 of 137).
- With D1 + S0n, focus is 40–42 of 58 correct. Most remaining wrong picks are media screens where no detector box covers the focused card.
- Media-app misses by class (D1 s372, class-agnostic IoU ≥ 0.5): poster cells 31 of 68, artwork pictures 10 of 51, bars 0 of 8, buttons 164 of 302.
- Misses by size: objects over 2 % of the screen 59 of 135, the worst size band. **The gap is large artwork, not small targets.**

D1 trains on generator `cells6` frames (4,035) and Fixture compositions (1,592). It has no poster-grid Fixture layout and no real app.

## Data for H2 (membership D2)

Benchmark apps (Swiftfin, Plozz, Strimr, TVSettings, HeadBoard) never enter training. Training apps: NewsTV, TVCatalog, Photo Guessing Game (C1).

| Source | Rows | Content | State |
|---|---|---|---|
| D1 membership | 5,645 | generator cells, Fixture compositions | admitted |
| Fixture `reset604/batch-v1` | up to 1,287 | `media_shelf`, `grid_matrix`, settings and canvas recipes | captured; left out of `v3-d1` without a recorded reason (step 1) |
| New Fixture poster capture | about 2,000 | `grid-uniform-poster` (qualified 16 / 16), `media_shelf`, hero + rail, seeded artwork and focus position | needs Joe's approval (decision 1) |
| Training-app real frames | about 40–100 | NewsTV (cards), TVCatalog (product art), Photo Guessing Game (photos), Joe-reviewed | role change of dev42 frames (decision 2) |

Expected D2 size: about 8,000–9,000 rows. It is larger than D1, so it shows no drift sign.

## Arms (2 seeds each: 371, 372)

| Arm | Data | Recipe | Question |
|---|---|---|---|
| D1 (exists) | D1 | YOLO11n, 640, 100 epochs, fixed last epoch | baseline |
| A | D2 | D1 recipe unchanged | Does poster and real data close the media gap? |
| B | D2 | A + augmentation: mosaic, scale jitter, HSV jitter, random crop; no horizontal flip | Does augmentation transfer to real apps? |
| C | D2 | B + YOLO11s | Does model size help large artwork? |

- All arms start from pretrained YOLO11 weights, not from a shipped checkpoint.
- Every arm picks its best epoch on the calibration split (TRAIN666 W4), not the last epoch.
- **1280 and 2 × 2 tiles are left out.** The evidence shows large objects missed most, so a small-target arm would test the wrong cause. They stay available if arm A shows a small-object gap.

## Steps

| Step | Work | Time |
|---|---|---|
| 1 | Find why `v3-d1` dropped `batch-v1`; audit label completeness of its `media_shelf` and `grid_matrix` rows (1 % audit + importer checks) | 1 h |
| 2 | Q-packet and pilot of the new Fixture poster capture (200 frames) on Maximum-mini-TTR; measure the capture rate | 1–2 h |
| 3 | Full poster capture (about 2,000 frames, bounded capture jobs) | from the pilot rate |
| 4 | Build D2: `prepare`, class counts, overlap check against all 5 benchmark apps, data roles | 30 min |
| 5 | Log arms in `Research/ExperimentLog.md`; compile T107 through `scripts/hcf_templates395.py` | 30 min |
| 6 | 6 fits on the detached runner, back to back | see below |
| 7 | Score every fit with `tvbench.py eval --roles` on `manifest-31layouts.json`, plus S0n focus; 1 report | 1 h |

Fit time from D1 (8.1 h for 5,645 rows, YOLO11n): about 11–13 h per YOLO11n fit and about 20–25 h per YOLO11s fit on D2.
Total about 85–95 h of runner time. Fits above 12 h need an EXTENSION408 restart (decision 3). Do not shorten fits.

## Expected scoreboard change (written before admission)

On the 31-layout set, for both seeds of the best arm:
- equal-app localization recall at least 0.69 (D1 s372: 0.610);
- media-app poster cells at least 50 of 68, artwork pictures at least 25 of 51;
- Plozz recall at least 85 of 137 (Standard's level);
- equal-app precision at least D1 − 0.05;
- with S0n: focus at least 46 of 58 correct, wrong picks at most 8.

Arm A alone is expected to give most of the recall gain. Arms B and C are expected to add at most 3 points each.

## Outcomes and stopping rules

- **Supported:** the predictions hold for both seeds of 1 arm, and the gain over D1 is larger than the seed difference.
- **Contradicted:** arm A gains less than 2 recall points over D1 on both seeds. Then the data is not the cause; report before running B and C.
- **Inconclusive:** the seeds disagree on the direction.
- **Regression:** any app loses more than 3 recall points against the same D1 seed. List lost cases; do not veto.
- **Stop early:** if step 1 shows that `batch-v1` labels are incomplete, admit only the rows that pass. If the poster pilot fails qualification, run arm A on the other sources and report the missing source.
- **Benchmark caution:** the 31 layouts are development frames that were opened in review. A sealed test stays a separate task.

## Joe's decisions needed

1. Fixture poster capture: about 2,000 frames on Maximum-mini-TTR (local Simulator, bounded jobs, 800 s per capture job).
2. Move the reviewed training-app frames (dev42 NewsTV and Photo Guessing Game, plus any reviewed TVCatalog frames) from development to training.
   After that, dev42 is no longer an independent check for those apps.
3. EXTENSION408 restarts for fits above 12 h, with the counted output limit set per spec hash (D1 used 8 GiB).

Steps 1, 4 and 5 are checks within the standing approval. Steps 2–3 need decision 1. Step 6 runs within the standing training approval after decisions 2 and 3.

## Joe's decisions — approved 2026-11-25

Joe: "Approve all 3". Record: `reports/work/user-approvals/train666-h2-decisions-20261125.json` (plan SHA-256 `d0289b0d…` before this note).
Covered: the poster capture, the dev42 role change and EXTENSION408 restarts, as written above. Not covered: metrics, acceptance, promotion.

## Step 1 result and an open data-role conflict (2026-11-25)

- **`batch-v1` cannot be admitted.** The `v3-d1` audit excluded 1,392 Fixture-batch rows as `incomplete_labels`.
  Its plain recipes do not declare every visible control, and an unlabelled control trains as background. 0 rows pass, so the stop rule applies.
- **Training-app real frames:** only 23 dev42 frames have complete labels (NewsTV 19, Photo Guessing Game 4). The 2 Swiftfin frames stay out (benchmark app).
- **Poster data exists but is held out.** `composition:poster_grid` is a NUIAK Fixture family hold-out (`HELD_OUT` in `scripts/fixture_recipes604.py`).
  `v3-d1/held-out.json` already holds 514 complete rows of this family (266 focused, 248 no-focus; 4,004 cells).
  The new poster capture (decision 1) would be the same family. Training on it changes the family hold-out, which decision 1 did not cover.
- Poster capture and D2 wait for Joe's decision on the hold-out.

## Joe's decision on the poster hold-out (2026-11-25)

Joe: "Yes, train on posters". Record: `reports/work/user-approvals/train666-h2-poster-holdout-20261125.json`.
- `composition:poster_grid` moves from the Fixture family hold-out to training for D2: the 514 complete held-out rows and the new poster capture.
- The other 3 held-out Fixture families stay held out. The real-app benchmark decides H2; it never enters training.

## Progress, 2026-11-25 (after the hold-out decision)

- `scripts/fixture_recipes604.py --poster N`: varied poster-grid recipes from the qualified `grid-uniform-poster` source.
  It varies card shape (tall 2:3, wide 16:9, square), card size, columns (up to 7), rows (1–3), gap and grid position, and samples up to 6 focus targets.
  Every card stays fully on screen. The capture audit checks each frame against its recipe. 16 pilot recipes: `reports/work/RESET604/recipes-poster-pilot`.
- `scripts/d2_membership666.py`: D2 base `reports/work/TRAIN666/membership/d2-base` (no new capture yet). `prepare` passes.
  - 5,944 rows: 5,509 train, 435 calibration. 0 overlap with the 31-layout and sealed benchmarks; 0 train/calibration group overlap.
  - Added: 279 unique poster rows (the 514 held-out rows repeat each unfocused baseline), 20 real frames (NewsTV 19, Photo Guessing Game 1).
  - 3 Photo Guessing Game frames are dropped: they hold objects with no class, which would train as background.
  - `pageControl` has 0 examples.
- Blocked: the poster pilot needs TTR in project mode. The running TTR app (`phone-remote-candidate-5`, started 18:17) is in app-managed mode and was not started by this session.

## Poster capture, 2026-11-25 (provisional)

- Pilot (`recipes-poster-pilot`, 16 recipes): 16 / 16 accepted, 92 rows (184 frames) in 144 s. Capture audit 184 / 184 frames pass.
- Full run (`recipes-poster-v1`, 350 recipes, seed 667): chunk 1 accepted 15 recipes (96 rows; audit 192 / 192 pass).
  The other 335 recipes were refused before capture (`coordinator_preflight: simulator_cleanup_required`). No frame was sent.
- Cause: at 18:43 the TTR window started a Simulator Remote live-control session on the same Simulator (setup sheet, automatic target selection).
  The session holds ownership (operation `9C59A2AD`). This looks like interactive use of the TTR window; NUIAK did not stop it.
- Resume: when the Simulator is free, capture recipes 15–349 into a new folder (`poster-v1b`); the runner keeps the refused chunks as complete.

## Admission, 2026-11-25

Joe: "Submit fits now". D2 `reports/work/TRAIN666/membership/d2-v1` (SHA-256 35718078…), `prepare` passes: 5,728 train + 435 calibration rows.
Poster rows: 279 released + 219 new (planned about 2,000). Real frames: 20.
4 fits submitted and approved through `scripts/h2_queue_plan666.py`: arms A and B × seeds 371 and 372, 86,400 s and 8 GiB each (decision 3).
`train666-h2a-d2-e100-s371` is running: about 7 min per epoch, counted output 6.3 GB at epoch 1. Arm C waits for a `yolo11s.pt` download approval.

## Note, 2026-11-25 (Maximum-mini-NUIAK, main session)

Joe answered the same hold-out question in the main session: "Yes, release it". It matches the recorded fork decision ("Yes, train on posters") and its scope.
No second D2 or fit was made. H2 execution stays with the fork session that submitted the 4 fits.

## Arm C time check, 2026-11-25

Joe approved the `yolo11s.pt` download ("Approve the yolo11s download"). The main session downloaded it (SHA-256 85a76fe8…; [record](../../reports/work/user-approvals/train666-h2-yolo11s-download-20261125.json)).
Maximum-mini-NUIAK measured the step time before submission ([timing](../../reports/work/TRAIN666/h2-arm-c-timing-20261125.json)):
- Arm A runs at about 390 s per epoch, so about 10.8 h per fit.
- Arm B (square mosaic batches) needs about 640 s per epoch, so about 17.7 h per fit. This is inside the 86,400 s maximum.
- Arm C (YOLO11s and square batches) needs about 1,300 s per epoch, so about 36 h per fit. This is above the 86,400 s validator maximum.
An EXTENSION408 restart starts from epoch 0, so a restart cannot finish arm C. Fewer epochs would change the experiment, and AGENTS.md forbids that.
Arm C is not submitted. Joe chooses 1 of 2 options:
1. Add an exact checkpoint resume (`checkpoint-v1`) to T107. Then run each arm C fit as 2 chunks of about 18 h through `research_continuations.py`.
2. Remove arm C from H2. The plan expects at most 3 points from arm C.
Revised runner time for the 4 submitted fits: about 57 h (2 × 10.8 h + 2 × 17.7 h).
