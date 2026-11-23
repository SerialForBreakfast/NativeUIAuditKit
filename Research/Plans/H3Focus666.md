# TRAIN666 H3: focus formulation, 2 matched arms (plan, 2026-11-22)

Joe, in chat on 2026-11-22: "Plan both arms".
This plan belongs to row H3 of the "Active hypotheses" table in `Tasks.md`. It adds no hypothesis.
It is a plan only. Nothing here is admitted or started. Results stay provisional until Joe approves them.

## Why

- The shipped FocusRing threshold finds almost no focused control with any detector: 0–4 of 36 (dev42), 1 of 18 (Kanopy), 0 of 34 (AX-dev).
- The comparative selector is better but not stable across detector seeds ([selector-axdev](../../reports/work/TRAIN666/selector-axdev/README.md)):
  - AX-dev: Standard 23, D1 seed 371 24, D1 seed 372 15 correct of 34. Seed 372 makes 15 wrong picks.
  - Every D1 wrong pick has a box on the focused control. The selector picks another box.
- The current selector was fitted on reference boxes from `v2-focus-supervision`, not on detector boxes.

## Arms

| Arm | Change | Detector boxes | Compute |
|---|---|---|---|
| Baseline | Current comparative selector (`comparative-focus-604-v2`, gate 0.28) and FocusRing 0.85 | D1 seeds 371 and 372 | none (scores exist) |
| S — selector refit | Refit the comparative scorer and gate on D1 detector boxes | D1 seeds 371 and 372 | CPU, no detector fit |
| F — focus in the detector | Train D1's recipe with an 11th class, `focused` | Arm F's own boxes, seeds 371 and 372 | 2 detector fits |

### Arm S: refit the selector on D1 boxes

1. **Debug check first (no decision).** On the 8 AX-dev screens where seed 371 is correct and seed 372 is wrong, compare:
   - the IoU of each seed's box with the reference focused box;
   - the rim, halo and inner features of both boxes.

   This shows whether small box shifts change the features. If yes, box jitter goes into the refit.
2. **Training frames.** Use the `train` rows of `RESET604/membership/v3-focus-supervision` that have verified focus: `focused` with 1 focused box, or `no_focus`. TVBench overlap is 0.
3. **Boxes.** Run both D1 seeds over these frames through the shipping Core ML path (confidence 0.25, NMS IoU 0.30). Pool the 2 seeds' boxes, so the selector sees both box styles.
   - Match the reference focused box to a detector box at IoU ≥ 0.5.
   - If no detector box matches, leave the frame out of the scorer fit. Keep it in the gate fit as "focus not localized".
   - Add box jitter only if step 1 shows that box shifts change the features. Take the jitter size from the measured IoU of matched boxes on dev42 and AX-dev.
4. **Gate.** Calibrate the "no focus" gate out of fold on D1's `calibration` rows (374 focused, no `no_focus`) plus the `no_focus` train rows. D1 did not train on its calibration rows.
5. **Export.** Core ML scorer and gate, with the existing parity check (winner match on 42 of 42 dev frames).

**Known risk:** D1 trained on most of these frames, so its boxes there are cleaner than on real apps. The pooled seeds and the jitter reduce this risk but do not remove it.

### Arm F: `focused` as a detector class

1. **Membership** `TRAIN666/membership/d1-focused-11class` (new, immutable):
   - D1's 10 classes and boxes, unchanged, plus 1 `focused` box from `v3-focus-supervision` on each focused row.
   - Rows: 4,456 focused + 233 `no_focus` train rows; 374 focused calibration rows. Total 5,063.
   - **Removed:** the 582 D1 rows with `unknown` or `ambiguous` focus (451 + 131). Without a `focused` box they would teach the model that no control is focused. Missing focus is `unknown`, never "no focus".
   - This set is 10.3 % smaller than D1 (5,645). The skill lists a smaller training set as a drift sign, so Joe must approve it.
2. **Fit:** the D1 recipe without changes, which keeps the comparison matched.
   - T107 through `scripts/hcf_templates395.py`, pretrained YOLO11n start, 100 epochs, seeds 371 and 372.
   - Limit 43,200 s per fit. About 8.1 h per fit from the D1 timing.
   - Hard-linked images count about 5 GB of output, so each fit needs an EXTENSION408 restart with 8 GiB. Joe's earlier 8 GiB approval covered the 2 D1 restarts only.
3. **Decode check before the fit.** The Core ML NMS keeps boxes per class (`pickTop.perClass: true`). But `tvbench._coreml_predict_preproc_keyed` takes only the arg-max class of each output box. If the `focused` box and its control box come from 1 output row, 1 of the 2 disappears.
   - Add an offline test with a synthetic confidence vector that has 2 classes above the cutoff.
   - If the test fails, change the decode so that `focused` is read from its own score. Then re-score the baselines with the new scorer hash before any arm F score.
4. **Swift path:** the shipping library does not read a `focused` class yet. This is needed before shipping, not for the comparison.
   - Checked 2026-11-22: Swift also does not read 6 of D1's 10 role labels (`cell`, `button`, `picture`, `bar`, `dialog`, `indicator`). Any D1 or arm F ship needs a taxonomy decision first.

## Scoring

- `scripts/tvbench.py eval --roles`, on the same 3 development sets as H1: dev42 v3-focus-unknown labels, Kanopy and AX-dev.
- Report both seeds for every arm, per app and as the equal-app mean:
  - focus top-1 (correct, wrong pick, abstention);
  - false selections on `known_no_focus` screens;
  - class-agnostic localization recall and precision, to show any regression from the extra class.
- **No decision is possible yet.** The sealed TVBench has 0 of 100 frames. The development sets have no layout IDs and fewer than 30 independent layouts. Only 9 `known_no_focus` screens exist (6 + 2 + 1). The H3 decision waits on the same benchmark work as H1.

## Expected scoreboard change (written before admission)

| Arm | Prediction |
|---|---|
| S | Both seeds reach at least 24 of 34 correct on AX-dev and at least 28 of 36 on dev42. The seeds differ by at most 3 screens on each set. Wrong picks are at most 6 per seed on AX-dev. |
| F | Both seeds match or beat arm S on the equal-app focus mean. No-focus false selections are no higher than arm S. Localization recall is within 1 point of the same D1 seed on each set. |

## Outcomes and stopping rules

- **Supported:** the prediction holds for both seeds.
- **Contradicted:**
  - arm S: after the refit, the seeds still differ by more than 3 screens on AX-dev;
  - arm F: arm F is below arm S on the focus mean for both seeds.
- **Inconclusive:** the 2 seeds disagree on the direction.
- **Regression:** arm F localization recall falls by more than 2 points against the same D1 seed on any set. List lost cases, do not veto.
- **Stop early:** if arm F seed 371 gets focus top-1 no better than FocusRing on all 3 sets, stop seed 372 and report the failure.
- **Lost cases:** list each screen that changes from correct to wrong or abstention.

## Order and budget

| Step | Work | Wall time | Output |
|---|---|---|---|
| 1 | Arm S debug check | 10 min | < 10 MB |
| 2 | Arm F decode test (and fix if it fails) | 30 min | code + test |
| 3 | Arm F membership, `prepare` and overlap checks | 20 min | < 50 MB |
| 4 | Arm F fits, 2 seeds in sequence on the detached runner | about 17 h | 2 × 8 GiB counted |
| 5 | Arm S refit (D1 inference over about 5,000 frames × 2 seeds, then fit) | 1–2 h, can run during step 4 | < 2 GiB |
| 6 | Score all arms on 3 sets, write 1 H3 report | 30 min | < 100 MB |

Total about 19 h, mostly unattended arm F training.

## Joe's decisions needed

1. Arm F membership without the 582 rows of unknown focus (5,063 rows, 10.3 % smaller than D1).
2. EXTENSION408 restarts with 8 GiB counted output for the 2 arm F fits.
3. If the decode test fails: the scorer change and the re-score of the baselines.

Arm S and the checks in steps 1–3 need no new authority. They are diagnostics and CPU fits within the standing approval.

## Changes after Joe's approval (2026-11-22, "Approve both, start")

- **Arm F limits:** the 8 GiB limit is recorded as a maintainer override for each exact spec hash before submission. No attempt has to fail on `output_limit` first. The jobs are `train666-h3f-11class-e100-s371` and `-s372`.
- **Arm F class loss:** `indicator` has 0 examples in the arm F membership (D1: 710). All indicator boxes were on rows of unknown focus. Arm F localization is compared without `indicator`.
- **Arm F decode check:** the exported NMS is per class (`pickTop.perClass: true`). `tvbench` already reads a `focused` detection as the focus box and removes it from the control list. A synthetic test of the arg-max decode cannot show what the trained model does. The check therefore runs on the trained model: on calibration frames, count how often the focused control has both a `focused` box and its control box. No scorer change is made before that.
- **Arm S debug result:** the focused box does not cause the seed flips. A false nested `toggle` box inside the focused Settings row does. Box jitter is not used. A nested-candidate filter is scored as a separate variant (S0n, S1n). It was designed on AX-dev, so its AX-dev result is optimistic.
- **Arm S gate:** the existing out-of-fold gate on train rows is used. D1's calibration rows have no `no_focus` frame.
- **Arm S result:** [report](../../reports/work/TRAIN666/h3-arm-s/README.md). The refit (S1) is contradicted. The nested filter on the current selector (S0n) meets the arm S prediction. Arm F is compared against both S0 and S0n.
