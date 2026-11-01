# FOCUS556 — FocusRing for real apps (REALAPP554 RA554-16)

Date: 2026-11-01. Owner: Maximum-mini-NUIAK. Priority: P0. Task authority: Tasks.md, RA554-16.
Evidence: [focus diagnosis](../../reports/work/REALAPP554/focus-diagnosis.md), [development baseline](../../reports/work/REALAPP554/focus-dev-baseline.md).
This plan admits no job and starts no training. Each run is registered in ExperimentLog.md before it starts.

## Problem

The shipped FocusRing (FDR-001, v0.1) finds 0 focused controls on real apps: 0 of 15 pilot frames and 0 of 21 development frames.
2 model defects cause most failures:

1. **False positives.** Unfocused images, sheets and buttons score ≥ 0.85. 2 or more candidates reach 0.85 on 19 of 21 development frames.
   FDR-001 trained with 0 hard negatives (FOCUS-DET-05).
2. **Unknown focus styles.** The reviewed focus box scores < 0.70 on 16 of 21 development frames. All 10 NewsTV pill frames score 0.00.

A third limit is not a FocusRing defect: no non-text proposal covers the focused control on 12 of 21 development frames.
That gap belongs to the detector (tab pills, RA554 detection finding). Report it separately.

## Rules that bind this plan

- NewsTV, Swiftfin and Photo Guessing Game are evaluation-only. No crop from them enters training.
- The 21 development frames are for comparison only. The 21 pilot frames are the holdout: measure them once, after a candidate is chosen.
- Do not choose a threshold on real-app frames. Keep 0.85 and the 0.70–0.85 ambiguity band.
- Lessons: FDR-037 trained narrowly and fell from 270 to 155 of 270 previous test decisions. FDR-038 replayed reviewed legacy data at learning rate 0.00003 and still lost 11.
  Every run must replay previous data and pass retention checks.
- Training uses the standing approval: at most 3 runs, each ≤ 30 epochs, ≤ 30 min and ≤ 2 GiB. No Core ML export or promotion without passing all gates.

## Measures

| Measure | Set | Baseline (FDR-001) | Supported if |
|---|---|---|---|
| D1. Reviewed focus box ≥ 0.85 | Development, 21 | 4 | ≥ 12, and NewsTV pills > 0 on ≥ 5 of 10 |
| D2. Frames with ≥ 2 candidates ≥ 0.85 | Development, 21 | 19 | ≤ 8 |
| D3. Runtime-equivalent correct selections | Development, 21 | 0 | ≥ 5 (limited by the proposal gap) |
| R1. Previous test decisions | Legacy 270 crops | 270 | 270 (no lost success) |
| R2. Reserved procedural crops | 16 | 8 (FDR-001) | ≥ 14 |
| R3. Poster calibration | 8 | 3 | not worse |

Outcomes:
- **Supported:** D1, D2 and D3 pass, and R1 loses 0.
- **Contradicted:** D1 or D2 does not improve.
- **Regression:** R1 loses any previous success. Reject, even if D1–D3 improve.
- **Inconclusive:** D1 and D2 improve, but D3 does not, because no proposal covers the focused control. Hand the result to the detector track.

The holdout (pilot, 15 focused) is measured once for the chosen candidate. Report it beside the development result.

## Steps

### S1 — Score retained candidates on the real-app development set (no training, about 20 min)

Score the reviewed focus boxes and all proposals of the 21 development frames with every retained FocusRing candidate (`fdr002` to `fdr038`, and FOCUS319/329 when they export the same crop interface).
Use `scripts/focus_diagnosis554.py` with a `--model` option. Report D1 and D2 for each candidate, next to its recorded R1 result.
Decision: if a retained candidate passes D1, D2 and R1, go to S5 with it. Otherwise S1 names which earlier data change helped most.

### S2 — Capture a training-only Fixture batch (about 45 min, 1 Simulator session)

Capture new Fixture frames for training only. Use the CAPTURE553 batch path and a new data role, `focus-training`. Do not reuse CAPTURE553 frames, because their role is development.
Content, chosen to match the real-app failures without using real-app pixels:

| Need | Fixture recipe | Real-app failure it targets |
|---|---|---|
| Unfocused artwork, posters and photos | `canvas` artwork, `bright_unfocused` | imageView false positives |
| Unfocused large panels and cards | `settings_rows`, `buttons` with large bodies | sheet and collectionItem false positives |
| Plain text near controls | `canvas.labels` | label proposals |
| Focused and unfocused top-tab pills | `tabs`, `nested_tabs_v1`, with a selected tab that differs from the focused tab | NewsTV pill focus |
| Focused and unfocused buttons with custom focus | `custom` focus with scale, border and shadow | Photo Guessing Game and Swiftfin buttons |

Unfocused crops come from every unfocused control in a frame, not only from the 1 baseline frame.
Check before capture: run `real_app_session554.py alert-check`, and reserve new group IDs.
Missing feature: Fixture `custom` focus has no background-fill change, which is the NewsTV pill style. Ask Maximum-mini-TTR for it in 1 request. Native `tabs` pills are the fallback.

### S3 — Prepare the training corpus (about 30 min)

Build 1 manifest: the FDR-038 training set (48 artwork, 48 procedural and 56 reviewed legacy crops) plus the S2 crops.
Hold out 20% of S2 groups as a Fixture validation split. Pairs never straddle splits.
Verify hashes, crop geometry through `makeCrop`, and the absence of any real-app image (file and pixel hashes).

### S4 — Train (registered runs, about 10 min each on MPS)

| Run | Change | Purpose |
|---|---|---|
| F1 | FDR-038 recipe on replay data only, matched steps | Control: what replay alone does on real apps |
| F2 | F1 plus S2 hard negatives and tab positives | Test the main hypothesis |
| F3 (conditional) | F2 with higher replay weight | Only if F2 passes D1 and D2 but fails R1 |

All runs start from FDR-001, use seed 42, 30 epochs, batch 64, learning rate 0.00003, and the last checkpoint.
Register F3 now, with its condition. The runner starts it only if the condition holds.

### S5 — Measure and decide (about 20 min)

1. Measure R1–R3 and D1–D3 for each run.
2. Choose at most 1 candidate by the rules above. Measure it once on the pilot holdout.
3. Report results, failures and lost successes. Keep all checkpoints.
4. If a candidate is supported: export through `export_focus_ring_coreml.py`, check Core ML parity, and replay the 21 + 21 frames through TTR with that model.
   Promotion needs the FOCUS-DET-05 gates as well, so this plan does not replace the bundled model.

## Time

About 3 h of agent work, plus 1 TTR request if the pill fill feature is missing.
Slow steps: the S2 capture session and the S1 scoring of about 30 candidates.

## Maintainer decisions

1. Approve the new `focus-training` Fixture capture in S2 as training data. The alternative is to change CAPTURE553 frames from development to training, and this plan does not recommend that.
2. Approve 1 request to Maximum-mini-TTR for a Fixture background-fill focus style, or accept native `tabs` pills as the only pill source.
3. Confirm that the FOCUS3xx change model (focus change between 2 frames) stays a separate track. It needs a before and an after frame, which `visual replay` does not supply.
