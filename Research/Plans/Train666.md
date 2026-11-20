# TRAIN666 — Fix the training and evaluation process for the tvOS models

## Context

Joe asked why the models do not improve and how to get a robust training workflow.
The nightly review of 15 November reports "no verified model improvement". The scoreboard has had no accepted row since 1 November.

The diagnosis in RESET604 (9 November) was correct. The process then went back to the old habits within 3 days.
This plan states the evidence, ranks the big wins, and adds enforcement so the process cannot drift again.

Joe's decisions for this plan (16 November, in chat):
- Run D1 now on existing labels as a baseline.
- Do 1 review block of 3 to 4 h to label the benchmark.
- Allow real apps into training, split by whole app.

## Diagnosis (evidence from the repository)

### What works — keep it

- **Label and loader verification.** Labels pass through importer, writer and loader with 0.0 px error. Corrupted frames are rejected by name. The framework contract with TTR is accepted.
- **Run integrity.** Fits are pinned, hashed and reproducible. Paired seeds and same-seed controls are standard.
- **Honest reporting.** Failed gates are reported as failures. Nothing was promoted on weak evidence.
- **The diagnostics already found the answers** (next section). They were not acted on.

### The 4 signals that were not acted on

| Signal | Evidence | What it means |
|---|---|---|
| Full-data training works | D1 probe, 1 epoch, 4,728 rows, from pretrained weights: 378 / 438 real-app controls (AP50 0.79). Shipped: 103 / 438. | Data scale is the largest lever. The run never went past 1 epoch. |
| Focus is limited by the detector | Shelf focus swaps: 30 / 30 with supplied boxes, 14 / 30 with detector boxes. | Fix proposals first. Focus-classifier fits cannot repair missing boxes. |
| The comparative selector beats the crop classifier | Arm B: 29 / 36 focused on R5 boxes. FocusRing v0.1: 0 / 36 even with supplied boxes. | The formulation is the problem, not the crop training set. COMP600 trained the wrong model. |
| Fine-tunes forget | BREADTH662: both broad arms lost all 33 Standard successes. R5 keeps 5 / 30 Fixture buttons; Standard keeps 14 / 437 NewsTV buttons. | Small fine-tunes move the model between domains. Train 1 model on the union of the data. |

### Pain points

1. **No benchmark.** TVBench: 0 of 150 screens labelled. Noise floor: not measured. Minimum detectable effect: not set.
   Each experiment builds its own panel (50 appearances over 13 panels; 19 related screens of 1 app). Results between experiments cannot be compared.
2. **Effects are smaller than seed noise.** BREADTH662: +4.9 points at seed 371 and −0.75 at seed 372. COMP600: 3 recoveries against 9. The 25 "gained appearances" were 3 controls repeated on 12 screens.
3. **The zero-loss veto is back.** COMP600 needed "zero lost correct selections" on 27 cases. With this seed variance, a good model also fails that gate. RESET604 rule R1 removed this veto.
4. **Training sets are tiny, and augmentation is off.** Recent fits: 60 images / 369 labels for 100 epochs; 300-screen detectors.
   `scripts/train_detector604.py` sets `mosaic=0`, `fliplr=0`, `mixup=0`, `rect=True`, fixed-last checkpoint, 0 calibration rows. This setup memorizes.
5. **Training is 100 % synthetic.** Every real-app screen is evaluation-only. The real-app gap can only close by luck.
6. **Small targets vanish.** Screens are 3840 × 2160, letterboxed to 640 (6× smaller). All candidates missed all 244 Watch Later child buttons. Changing only inference to 960 did not help, because the models were trained at 640.
7. **Label policy changed under the experiments.** The 12 November contract made all current training data "legacy" and paused D1. Strictness on label purity blocked the only run with enough data.
   The same change moved the denominators (114 NewsTV articles changed from `cell` to `button`), so older and newer scores do not compare.
8. **Too many hypotheses.** Rule R3 allows 3. In 7 days there were 138 work folders and experiment IDs 604 to 665. Paused tracks ran anyway: COMP600 (FocusRing crop variants) and 14 iOS folders.
9. **Compute is idle.** 15 November: 2,926 s of execution and 83,165 s idle (3.4 % used). Queue: 0 ready, 440 dependent, 129 exhausted, 421 superseded.
10. **Review is the bottleneck.** 15 min per week cannot label 150 screens. Agents filled the wait with diagnostics.
11. **Process weight.** `AGENTS.md` 940 lines, `CurrentState.md` 5,819, `ExperimentLog.md` 7,338, 1,678 scripts. Each session spends its budget on records. Parallel workers edit the same files.

### Root cause

The team optimizes evidence quality per experiment. It does not optimize the model.
Without a fixed benchmark, each result needs a custom panel, a custom gate and a custom report. That work consumes the week, and no result can be accepted.

## Big wins, in order

### W1 — Run D1 at full scale now (largest expected gain)

- Membership: `v3-d1` (6,320 rows), roles collapsed to the 10 contract classes with `scripts/roles559.py` output mapped to `framework_projection604.tvos_classes()`. Drop rows of the 2 removed roles.
- Initialization: pretrained `yolo11n.pt`, not a shipped checkpoint.
- Seeds 371 and 372, 100 epochs, through the existing T107 adapter (`train_detector604.queue_run`, `scripts/reset604_queue_plan.py`). About 8 to 11 h per fit on the M4.
- This is a baseline, not a release candidate. Its labels are legacy. Contract-clean TTR rows replace legacy rows as families qualify (T2.5d).
- Expected scoreboard change: control recall on TVBench development well above shipped (probe: 86 % against 24 %). State this before the run.

### W2 — Build the benchmark once (unblocks every decision)

- Corpus: the 42 development screens plus the 146 queued sealed screens (`sealed-plan-v2.json`, `review-sealed-v2/`). Target 150 layout-distinct screens, at least 8 sources.
- Drafts from SDK and accessibility evidence (`scripts/real_app_session554.py`). Joe validates in 1 block of 3 to 4 h with `scripts/real_app_review554.py`.
- Labels: class-agnostic box + contract role where source evidence exists, else "role unknown". Focus: `focused`, `known_no_focus`, or `unknown`. Mark each screen complete or partial.
- Count 1 unit per layout. Repeated states of 1 screen do not count again.
- Freeze `tvbench-v1` by hash. Agents do not open sealed images or per-frame outputs.
- Then measure the noise floor: 3 seeds of the D1 recipe. Publish the minimum detectable effect on the scoreboard.

### W3 — One scorer, three numbers

`scripts/tvbench.py` reports, per app and as an equal-app mean, with bootstrap intervals by app:
1. **Localization recall and precision, class-agnostic** (IoU 0.5). This is what an agent needs to find a target.
2. **Role accuracy on localized targets** (confusion matrix). This is what an audit needs. It follows ADR-0034.
3. **Focus:** top-1 on focused screens, false selections on `known_no_focus` screens.

A candidate is accepted on a paired gain beyond the noise floor. Lost cases are listed, not a veto (rule R1).

### W4 — Real data and a real training recipe

- **App-level split.** Training apps: NewsTV, Photo Guessing Game, TVCatalog (already heavily inspected). Sealed test: all other apps. No app is on both sides.
- **Augmentation on.** Compare the current recipe with: mosaic on, scale jitter, HSV jitter, random crop. No horizontal flip (UI is not mirror-symmetric).
- **Small targets.** Compare 640 with 1280 for both training and inference, and with 2 × 2 tiled training crops. Check Core ML latency for each.
- **Model size.** YOLO11n against YOLO11s (T3.2).
- **Checkpoint choice.** Use the calibration split (506 rows) for best-epoch selection in place of fixed-last.
- Run these as 1 planned grid of at most 6 arms, 2 seeds each. Judge all arms on TVBench development.

### W5 — Focus: stop crop-classifier work, ship the formulation change

- Stop FocusRing crop variants (COMP600, HARDNEG596, Programme). They were already paused by T0.1.
- Arm A (T4.1): add a `focused` class to the D1 successor (`v3-f1-arma`, 5,585 rows). The model then sees the whole screen and the neighbours.
- Arm B (T4.2): the comparative selector with a "no focus" option, on D1 boxes. It is already integrated in Swift (`ComparativeFocusSelector`).
- Judge both on TVBench focus numbers. Add explicit `known_no_focus` screens to the benchmark, because none of the 50 COMP600 frames had one.

### W6 — Keep the machine busy with real fits

One 100-epoch fit takes about 8 h. Queue the W1 and W4 fits back to back. Target more than 60 % runner use.
Close or supersede the 440 dependent and 129 exhausted jobs in 1 pass, so the queue shows only live work.

## Process rules with enforcement

| Rule | Enforcement |
|---|---|
| At most 3 active hypotheses | `Tasks.md` gets 1 "Active hypotheses" table with 3 rows. A new row needs a closed row. The nightly review fails if admitted jobs belong to no row. |
| Every model decision uses TVBench | `scripts/tvbench.py` is the only source for a decision table. Custom panels are labelled "debug" and cannot open or close a hypothesis. |
| Predicted effect before the run | The job specification must carry `expectedScoreboardChange`. The compiler (`hcf_templates395.py`) rejects a training job without it. |
| No decision below 30 independent screens | The scorer prints the independent-layout count and refuses a verdict below 30. |
| Label policy is versioned | A contract change creates a new benchmark label version and a re-score of the baselines. It does not pause training. |
| Paused tracks stay paused | iOS, HCF, FocusRing crop variants: no admissions until the tvOS detector has an accepted scoreboard row. |
| Weekly cadence | Monday: 1 review pack (15 min). 1 decision per hypothesis per week. Nightly reviews shrink to 1 page: scoreboard delta, runner use, blockers. |
| Records stay small | New results go to the scoreboard and 1 short report per hypothesis. `CurrentState.md` gets a 1-page "now" section; older text moves to an archive file. |

## Steps

**Day 0 (today, after approval)**
1. Record this plan as `Research/Plans/Train666.md`. Add the "Active hypotheses" table to `Tasks.md` with H1 = D1 full-scale, H2 = recipe grid (W4), H3 = focus formulation (W5).
2. Build the 10-class D1 membership from `v3-d1`. Verify it with `detector_training419.prepare` and the loader readback (`qpacket_import604.decode_tensors`).
3. Admit D1 seeds 371 and 372 through T107. Record both in `Research/ExperimentLog.md` first, with the expected scoreboard change.
4. Prepare the TVBench review pack for Joe's block: drafts, exception-first order, about 150 screens.

**Days 1 to 3**
5. Joe's review block. Freeze `tvbench-v1` (development and sealed manifests, hashes).
6. Extend `scripts/tvbench.py` with the 3 numbers, equal-app means, bootstrap intervals and the 30-layout guard.
7. Score shipped Standard, R5 and both D1 seeds on TVBench development. Run the third D1 seed for the noise floor. Publish the scoreboard rows.

**Days 3 to 10**
8. Build the app-split membership (training apps added to D1 data). Run the W4 grid, 2 seeds per arm.
9. Run focus Arm A and Arm B on the best detector.
10. Pick 1 detector + focus candidate. Score the sealed test once. Bring 1 review pack to Joe (T5.1).

**In parallel, unchanged:** TTR delivers contract-clean Fixture families (T2.5c, T2.5d). Each qualified family replaces legacy rows in the next membership version.

## Critical files

- Reuse: `scripts/train_detector604.py`, `scripts/hcf_templates395.py` (T107), `scripts/reset604_queue_plan.py`, `scripts/ttr_detector_ingest604.py`, `scripts/framework_projection604.py`, `scripts/tvbench.py`, `scripts/real_app_review554.py`, `scripts/real_app_session554.py`, `scripts/comparative_focus604.py`.
- Change: `scripts/train_detector604.py` (augmentation and image-size options, best-epoch selection), `scripts/tvbench.py` (3 numbers, intervals, guard), `scripts/hcf_templates395.py` (`expectedScoreboardChange` check).
- Records: `Research/Plans/Train666.md` (new), `Tasks.md`, `Research/Scoreboard.md`, `Research/ExperimentLog.md`, `Research/CurrentState.md`.

## Authority needed (not granted by this plan alone)

- D1 fits: standing training approval covers local approved-backlog training; D1 is T3.1. Joe's answer "Run D1 now" lifts the 12 November pause. Each fit reserves 43,200 s.
- Real apps in training: Joe's answer changes data roles for NewsTV, Photo Guessing Game and TVCatalog. Record the exact message and scope in `Tasks.md`.
- No promotion, export or model package change without Joe's separate approval.

## Verification

- D1 membership: `prepare` succeeds; class order equals `tvos_classes()`; decoded tensors match the row boxes; 0 overlap with TVBench sealed apps.
- Fits: complete epoch history, final checkpoint digest, Core ML export parity (`scripts/coreml_parity562.py`).
- Benchmark: frozen manifest hashes; independent-layout count at least 30 for the first decision; baselines re-score to the same numbers twice.
- Scorer: unit tests for the 3 numbers, the equal-app mean, and the below-30 refusal. Existing 27 RESET604 Python tests and `swift test --no-parallel` stay green.
- Process: the next nightly review shows at most 3 hypotheses, runner use, and scoreboard rows with intervals.

## Addendum, 2026-11-16 — TTR annotations are the trusted synthetic source

Joe's direction: TTR can supply perfectly annotated synthetic data, and these annotations have been reliable.

Evidence in this repository:
- Composition captures: 3,214 of 3,214 frames matched their recipe expectations.
- NavigationConsumer milestone: 76 targets through importer, writer and loader with 0.0 px error, and 11 of 11 frames equal to TTR's own projection.
- Fixture Q1/Q5: 22 targets matched the frozen keys, and 50 corruption probes were rejected.
Known limits: scrolled shelves (TTR R604-05 is open), and classes for custom views (`ttr_convention`, not admitted by the contract).

### What changes

1. **Training labels need no human review.** Joe's review time goes only to the real-app benchmark.
2. **Trust by family, not by frame.** NUIAK qualifies each new recipe family once (1 Q-packet with keys and corrupted twins). After that, NUIAK admits frames of that family by the automated importer checks and a 1 % sample audit. Per-frame reconciliation reports stop.
3. **The limit moves from label quality to coverage and realism.** The open question is no longer "is the label right". It is "does the data look like real apps, and does it cover the 10 classes".
4. **The TTR SDK gives the same labels on real apps.** An open-source tvOS app built with the SDK yields real pixels with reliable labels and no review. This is the main route for real-app training data (app-level split).
5. **The loop closes on benchmark errors.** Each benchmark scoring produces a miss list by class, size and layout. NUIAK turns the top misses into recipe requests. TTR adds recipes. The next fit uses the new frames.
6. **Volume is cheap.** Capture runs at about 1 image per second. 20,000 frames take about 6 h. Diversity (layout groups, artwork, text, theme, focus position) matters more than frame count.

### What does not change

- The benchmark stays real-app, human-reviewed and sealed. Synthetic accuracy is a report line, never a decision.
- The contract `tvos-framework-projection-v1` stays the label rule. Custom views stay out of strict training data.
- Decisions need a paired gain on the benchmark beyond the noise floor.
- D1 (legacy labels) stays the baseline. A TTR-native model must beat it on the benchmark to replace it.

### Risk to measure, not assume

Synthetic-only detectors have not transferred to real apps so far (shipped Standard finds 14 of 437 NewsTV buttons). Reliable labels do not remove that gap.
So the first TTR-native fit is a 3-arm comparison: TTR synthetic only, TTR synthetic + SDK real-app frames, and the D1 baseline.


### H1 baseline measurement correction before the paired D1 result

The original 103/438 and 378/438 estimates were same-role matches from reports with different manifest fingerprints. They cannot quantify class-agnostic recall. The submitted jobs retain the original prediction for audit. On the same frozen development-v2 references and current TVBench scorer, Standard and the historical one-epoch probe localized 404/460 and 398/460 control appearances respectively. NewsTV contributed 437 of the 460. Equal-app localization recall was 77.6% and 93.8%; Photo Guessing Game contributed 21 references and Swiftfin two. For the completed seed pair report both per-app and equal-app rates, the pooled counts and each seed difference. The historical probe cannot establish a paired H1 result. [Standard replay](../../reports/work/TRAIN666/development-rescore/Standard-matched-focus-dev42.json) · [One-epoch replay](../../reports/work/TRAIN666/development-rescore/D1-historical-probe-matched-focus-dev42.json)
