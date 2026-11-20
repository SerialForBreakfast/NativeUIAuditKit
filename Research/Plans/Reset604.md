# RESET604 — project audit and recovery plan for measurable model wins

Owner: Maximum-mini-NUIAK. Date: 2026-11-09. Status: plan approved by Joe in chat on 2026-11-09, after 1 correction (local capture only). Decisions D1–D4 need explicit answers.

## R604-16 implementation and route acceptance

Maximum-mini-NUIAK and Sillycon-TTR use the [accepted 10-role table](../Contracts/tvos-framework-projection-v1.md). Each visible item has a target, owned metadata, an exclusion reason, or an unresolved observation. Preserve frame identity, observed focus, construction evidence and class order through the final loader.

| Route | Verified result | Next action |
|---|---|---|
| NavigationConsumer catalog sample | 11 frame records, 7 distinct images and 76 targets passed the final tensor check. All 10 corrupted twins failed their named checks. | Use this as the loader regression control. |
| Native Fixture | Q1 and Q5 passed independent semantic keys and loader checks. Unfocused sibling screenshots establish nominal geometry for all 20 button instances. | Test scrolling and occlusion on Q2 and Q3. |
| Independent real app | The populated TVCatalog Description route passed a pre-capture key for 19 objects, 6 loader targets and actual focus. | Buttons adds 17 targets. Both corrected tab strips pass. Apple accessibility resolves all 10 disputed button bodies. Verify the producer correction on re-export. [Independent comparisons](../../reports/work/RESET604/bar-boundary-v1/README.md). [TVCatalog result](../../reports/work/RESET604/tvcatalog-framework-trial/result-v1.json) |

For each pending route, verify the screenshot digest, account for every visible object, and compare decoded classes and source-pixel boxes against the key. Record unresolved items and unknown focus. Publish the two route outcomes before building strict training membership. [Requested route receipts](../../reports/work/RESET604/route-verification-604/requested-routes.json) · [Loader readback](../../reports/work/RESET604/route-verification-604/sample/milestone-readback-v1.json)

## Context

Joe asks why model performance does not improve, despite new diverse data from TVTestRig (TTR), and asks for an audit and a task list.
No model has shipped since 2026-09-18. Every nightly review since 2026-10-20 says "no verified model improvement".
The first real-app test (2026-11-01) shows the shipped tvOS models find 23 of 207 controls and 0 of 15 focused controls.
This audit uses the repository records as of 2026-11-09. It changes no file. All numbers below come from those records.

## Audit — why there are no big gains

### F1. There is no ruler that can show a win
- Human-reviewed real-app data: 46 frames from 3 apps (23 pilot, 23 development). Complete control labels exist for 1 app (NewsTV, 19 frames).
- The pilot holdout is spent. The RC561 "holdout" used agent-made labels and is withdrawn (MetricClaimsAudit571).
- Decisions use panels of 4 to 21 frames. Seed noise is larger than the effects:
  ART599 gives 7 vs 2 at seed 371 and 9 vs 0 at seed 372; SWEEP602 gives 4/4 at one seed and 0/4 at the other.
- Result: a real gain and a random change look the same. Nothing can be approved, so nothing ships.

### F2. TTR data does not reach training
- All 6 tvOS detector runs (R1–R6) train on 776–916 images from `scripts/generate_tvos_dataset.swift`. They use 0 TTR frames.
- FocusRing "native" runs use 30 native crops. TTR delivered 840 training frames with 2,520 competitors; they still wait for "qualification".
- `dataset/tvos_captures` has 2,169 images in 132 folders. Most are evidence for diagnostics, not training rows.
- Detector use of Fixture frames (ARTPARITY595 E1) is blocked: Fixture labels omit text items, so labels are incomplete.

### F3. Training is too timid, and the acceptance rule rejects every candidate
- Pattern of the 185 training jobs: fine-tune the shipped synthetic checkpoint, YOLO11n, 30 epochs, learning rate 0.0001, 157–1,030 images.
- The veto: a candidate must lose 0 previous successes on legacy (mostly synthetic) sets.
  Example (2026-10-17): native selections improve from 12/48 to 42/48; the candidate is rejected for 1 lost legacy case.
- The legacy sets do not predict real-app accuracy (synthetic 0.98 vs real 0.21). The veto protects the wrong thing.

### F4. The focus model answers the wrong question
- `resolveTVOSFocusWithEvidence` scores each control crop alone against a fixed 0.85 threshold (`NativeUIDetectionRequest.swift:764`).
- Focus is comparative: 1 control looks different from its neighbors. A lone crop of bright artwork scores 1.000 unfocused.
  Evidence: Alex 0.996 vs Sam 1.000; 0/8 on TTR native-truth frames; 0/15 and 0/21 on real apps; 3/19 real positives pass 0.85.
- About 5 weeks of work varied the crop classifier (margins, hard negatives, weight surgery, artwork). None changed the formulation.

### F5. The one loop that worked was stopped
- On 2026-11-01/02, inspection of real frames found 4 generator label defects in 2 days (artwork-only boxes, scaled boxes, platter size, nested text).
  Development results moved from 20 to 168 of 170 pills and from 5 to 18 of 21 focused controls (provisional).
- The loop stopped because no labeled real frames remained to inspect or to confirm on. Work moved back to small synthetic comparisons.

### F6. Effort goes to process, not to models
- Queue: 5,136 jobs. 4,757 are diagnostics with 7.8 h total compute (about 6 s each). Training totals 57 h in about 6 weeks. The runner is idle 96–99% of the time.
- Repository: 1,627 Python scripts (182,000 lines), 660 test files, 292 plans, `Tasks.md` 4,246 lines, `AGENTS.md` 940 lines, `CurrentState.md` 5,804 lines.
- About 10 tracks run in parallel (tvOS detector, FocusRing, iOS 41-class, HCF, temporal, weight-space, LangGraph, teacher preservation, artwork, competitors).
- Training-limit policy (12 h) is not applied everywhere: both COMP600 fits timed out at 1,800 s on 2026-11-08.

### F7. Trust failures added more gates, and the gates now block work
- Recorded failures: fabricated holdout labels, toy training stubs, scores above 0.01 reported as recall, scoring on a non-shipping input shape.
- The response was more approval steps. Now 9 jobs wait for approval and the automatic check rejects admissions.
- Joe's review time is the scarce resource, and it is not planned: 66 Office frames and 8 RC561 screens wait for review.

### Short answer
We cannot measure a win (F1), the new data is not in the training sets (F2), the training recipe and veto prevent change (F3),
and the focus model is built on a formulation that cannot work (F4). The process volume (F6, F7) hides these 4 facts.

## Recovery plan

Principle: 1 goal, 1 ruler, 1 scoreboard. Goal: tvOS control detection and focused-control selection on real apps, through the shipping Core ML path.

### Phase 0 — Freeze and simplify (0.5 day, needs Joe's decisions D1–D4 below)
- T0.1 Pause all tracks except the tvOS detector and tvOS focus. Record paused tracks in `Tasks.md` (iOS 41-class, HCF, temporal, weight-space, LangGraph, teacher preservation, margin and brightness sweeps).
- T0.2 Move the active task list to 1 short section (target: under 150 lines). Archive the rest to `CompletedTasks.md` or a dated backlog file. Do not delete records.
- T0.3 Save this plan as `Research/Plans/Reset604.md`. Add `Research/Scoreboard.md` (1 table; the only source for headline numbers).
- T0.4 Apply the 12 h training guard to every training template (COMP600 used 1,800 s). Reuse `scripts/research_execution_policy.py`.
  Finding (2026-11-09): the template compiler already applies 43,200 s. The 2 COMP600 fits were hand-written specifications with 1,800 s.
  `scripts/training_limit_lint604.py` (read-only) lists 50 unfinished training specifications below the policy. Do not edit `research_queue.py` for this: every approval pins that file.
  Rule: compile training jobs through `hcf_templates395.py`, or restart a short job with EXTENSION408.

### Phase 1 — Build the ruler: TVBench v1 (week 1; Joe: about 3–4 h review, once)
- T1.0 All captures run locally through Maximum-mini-TTR on the local Simulator. No frame requests go to other machines.
- T1.1 Corpus: 150 layout-distinct screens from at least 8 sources: NewsTV, Photo Guessing Game, Swiftfin, Apple media catalog sample, Strimr, Plozz, Office (Kanopy) recording, tvOS system screens.
  Reuse RC561 builds and captures (`reports/work/RC561`, `dataset/real_apps`), OFFICE603, and the REALAPP554 capture scripts.
- T1.2 Split by app, never by frame: development 50 screens (open for inspection) and test 100 screens (sealed).
  Sealed means: agents do not open test images or per-frame outputs; the scorer prints aggregate counts only.
- T1.3 Labels: drafts from SDK rectangles or accessibility frames, then Joe's validate-and-flag review (existing REALAPP554 review page). Record reviewer provenance per frame.
  The existing rule in `scripts/real_app_benchmark543.py` rejects model predictions as references; keep it.
- T1.4 Scorer `scripts/tvbench.py` (thin wrapper over `real_app_benchmark543.py` and `coreml_parity562.py`): shipping path only (Core ML, 640 × 640 letterbox, explicit thresholds).
  Measures: control recall and precision at IoU 0.5 per role; focus top-1 accuracy; false selection rate on no-focus screens; per-app table; bootstrap intervals by app.
- T1.5 Baselines on TVBench: shipped `nativeui-tvos-v3.0` + FocusRing v0.1, and candidate R5. Train the R5 recipe with 3 seeds to measure the noise floor.
- Acceptance: scoreboard shows baselines with intervals and a stated minimum detectable effect. Joe approves the benchmark, not a model.

### Phase 2 — Put TTR data into training (weeks 1–2, runs in parallel with Phase 1)
- T2.1 Capture locally with Maximum-mini-TTR (`$NUIAK_TTR_ROOT`, default `~/Developer/TVTestRig`) and the Fixture on the local tvOS Simulator. Do not ask Sillycon-TTR for frames.
  Target: 5,000 frames with seeded variation (layout, artwork edition, theme, focus position), native focus truth and SDK labels (scope of proposal FIXTURE-SCALE597).
  Use the Fixture launch arguments and `fixture batch` recipes that already exist (Programme, Field Atlas, Cinema, Studio Shelf, Pavilion, galleries), with TTR observe/snapshot brackets.
  Start with a 200-frame pilot to measure the capture rate, then run the rest as bounded capture jobs. Hold out by layout family and asset lineage.
  Check Simulator ownership and idle state first (standing build and launch approval, 2026-10-31).
- T2.1b Send Sillycon-TTR feature requests only, when the local Fixture lacks a capability. Expected requests: labels for every visible control including text, and a seeded batch-variation mode.
  Get each new feature through Git (`git pull --ff-only`), then build TTR and the Fixture from source on Maximum-mini.
- T2.2 Decide the `text` role (D3): remove `text` from the detector roles and let OCR supply text. Then Fixture labels are complete enough, and E1 unblocks without waiting.
- T2.3 Converter from TTR sidecars to detector membership. Reuse `scripts/artparity595_ingest.py`, `pills560_membership.row` and `roles559.sidecar_roles`.
- T2.4 Use the 840 delivered frames and the 36 Programme frames now, as the first TTR training rows.
- Acceptance: 1 membership with generator rows + TTR rows, label audit (sizes, roles, focus counts), no overlap with TVBench apps.

### Phase 3 — Detector D1: a real training run (week 2; about 6–10 h compute)
- T3.1 Train on all generator data (5,800 images, fixed labels) + TTR rows: 100 epochs, default learning-rate schedule, from the pretrained YOLO11 weights (not from the shipped synthetic checkpoint).
- T3.2 2 planned comparisons only: model size (YOLO11n vs YOLO11s) and input size (640 vs 960). 3 seeds for the chosen arm.
- T3.3 Judge on TVBench development; inspect misses there; fix generator or label defects; repeat at most 3 times. Then score the sealed test once.
- Acceptance: test control recall and precision beat the baseline by more than the measured noise. Legacy synthetic sets are reported, not a veto.

### Phase 4 — Focus F1: change the formulation (weeks 2–3)
- T4.1 Arm A (cheapest): focus as a detector output. Add a `focused` class box on the focused control, so the model sees the whole frame and the neighbors.
  Labels are free: generator element IDs already end in `_focused`, and TTR supplies native focus truth.
- T4.2 Arm B (if A is not enough): a comparative selector. Score all candidates of 1 frame together (softmax over candidates plus a "no focus" option) instead of a fixed 0.85 threshold per crop.
- T4.3 Baseline: FocusRing v0.1 on the same detector boxes. Stop work on crop-classifier variants until A or B is measured.
- Acceptance: TVBench test focus top-1 accuracy and no-focus false selections beat the baseline by more than the noise.

### Phase 5 — Review and ship (week 3)
- T5.1 1 review pack for Joe (1 page): scoreboard before and after, per-app table, regressions, limits, exact files. Joe approves metrics and promotion separately (AGENTS.md, 2026-11-04).
- T5.2 After approval: export, parity check (`scripts/coreml_parity562.py`), update `NativeUIAuditKitModels`, README table from the scoreboard, report to TTR.

### Process rules that replace current habits
- R1 Acceptance = paired gain on TVBench beyond the noise floor, with listed regressions. The "0 lost legacy successes" veto becomes a report line (needs D2).
- R2 No decision from fewer than 30 independent screens. Small panels are for debugging only.
- R3 At most 3 active hypotheses. Each states the expected scoreboard change before it runs. No queue-filling diagnostics.
- R4 Each training change runs with at least 2 seeds before anyone reads it as an effect.
- R5 Headline numbers come only from the scorer output and the scoreboard file. A perfect score triggers a label check.
- R6 1 weekly review pack for Joe (about 15 min). Approvals are batched there.
- R7 Proposal only: consolidate `AGENTS.md` (940 lines, many superseded sections) into current rules + a history file. Joe edits or approves; agents do not change it on their own.

## Decisions — Joe, 2026-11-09 (answers in chat)
- D1: "Pause all (Recommended)". Only the tvOS detector and tvOS focus stay active for 3 weeks (until 2026-11-30).
- D2: "Replace veto (Recommended)". The TVBench rule (R1) replaces the zero-loss legacy veto. Joe still approves every metric update and promotion.
- D3: "Remove text (Recommended)". The tvOS detector has 12 roles; OCR supplies text.
- D4: "150 screens (Recommended)". 50 development + 100 sealed test screens; about 3–4 h review once, then about 15 min per week.
- Correction before approval: capture locally with Maximum-mini-TTR. Send Sillycon-TTR feature requests only; get features through Git.

## Decisions as proposed
- D1 Pause the listed side tracks for 3 weeks.
- D2 Replace the zero-loss legacy veto with the TVBench rule (R1).
- D3 Remove `text` from the tvOS detector roles (OCR supplies text).
- D4 Review budget: about 3–4 h once for TVBench labels, then about 15 min per week.

## Critical files
- Existing, reused: `scripts/real_app_benchmark543.py`, `scripts/coreml_parity562.py`, `scripts/roles559.py`, `scripts/roles559_evaluate.py`, `scripts/pills560_membership.py`,
  `scripts/artparity595_ingest.py`, `scripts/generate_tvos_dataset.swift`, `scripts/detector_training419.py`, `scripts/research_execution_policy.py`, `Sources/NativeUIAuditKit/Detection/NativeUIDetectionRequest.swift` (focus selection, Phase 4 only).
- New: `Research/Plans/Reset604.md`, `Research/Scoreboard.md`, `scripts/tvbench.py` (+ test), TVBench manifests under `dataset/real_apps/tvbench-v1/`.
- Edited: `Tasks.md` (short active section), `Research/CurrentState.md` (pointer to the scoreboard).

## Verification
- Phase 1: `scripts/tvbench.py` reproduces the REALAPP554 pilot numbers (23/207, AP50 0.206, focus 0/15) on the pilot frames. Its test rejects prediction-derived labels and per-frame output for sealed apps.
- Phase 1: 3-seed R5 runs give a noise floor; the scoreboard states the minimum detectable effect.
- Phases 3–4: every reported number has a scorer output file, model hash, benchmark manifest hash and seed list. Core ML parity passes on the 640 × 640 path.
- Offline package checks stay green: `swift build`, `swift test`, and the focused Python tests.
- First execution step after approval: Phase 0 only (T0.1–T0.4), then start T1.1 and T2.1 in parallel. Estimate to first scoreboard: 5–7 days, limited by captures and Joe's label review.
