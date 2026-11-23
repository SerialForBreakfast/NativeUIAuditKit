# Tasks backlog — archived 2026-11-09 (RESET604)

This file is the complete `Tasks.md` as of 2026-11-09 (SHA-256 ed7d9f7ee63dae293a5b0b27406f1a9d39e23ddaeb7edf1ebd755286123875a9). Nothing is deleted.
Joe paused all tracks except the tvOS detector and tvOS focus until 2026-11-30 (RESET604 D1). Active work is in [Tasks.md](Tasks.md).
To resume an item, move it back to `Tasks.md` with Joe's approval.

---

# NativeUIAuditKit — Upcoming tasks

## P0 — Visual parity with real apps

- [ ] Finish the [Office blinded review](reports/work/OFFICE603/office-blinded-gallery.html). Freeze accepted frames, annotation provenance and route groups before running Standard. The Office recording is development evidence.
- [ ] Admit the 4 prepared [B405-294 matched controls](Research/Experiments/batches/B405-294.json) after approval. Review both seeds and both brightness conditions against the completed Programme arms.
- [ ] Diagnose the Photo Guessing Game control lost at both seeds before changing production crop margins. [November 8 review](Research/NightlyReview20261108.md)



- [ ] Review the [50 similar development–pilot pairs](reports/work/EVAL601/scene-similarity.json). Reserve fresh layouts for qualification. Compare the 4 EVAL601 margin jobs against their original bounds. Inspect the lost Photo Guessing Game control before advancing a crop change.

- [ ] Review the [private evaluation gallery](reports/work/EVAL601/review.html). Compare the 4 EVAL601 real-app reports by app and seed. Check lost positive crops before selecting the next fit.

- [ ] Review COMP600 matched competitor training, native system controls and genuine app positives. Keep Store artwork separate. [Evidence and acceptance rules](Research/VerifiedCompetitors600.md).

- [ ] Review ART599 cue and neighbor interactions in both seeds. Compare the independent real-app panel. See [protocol and prior losses](Research/ArtworkComparison599.md).
- [ ] Maximum-mini-NUIAK: qualify production crops from the hash-joined competitor index for future training. The 840 training frames have 2,520 unfocused controls. Reserve 160 sports frames. [Split verification](reports/work/ART599/split-check.json).

- [ ] Maximum-mini-NUIAK: qualify the matched artwork delivery and executed pixels. Run the controlled transfer comparison. See [audit and decision rules](Research/VisualParityAudit.md).
  - 2026-11-07 (ARTPARITY595, provisional): shelf pair 1968 received and verified (`reports/work/ARTPARITY595/shelf-pair-intake.json`).
    Frozen baseline on 8 TTR native-truth frames: 0/8 correct for v3 and R5. FocusRing scores unfocused artwork as focused (shelf competitor 1.000); flat = brushed.
    [Report](reports/work/ARTPARITY595/shelf-pair-report.md). Executed runtime pixels (Alex/Sam) still open. Plan: [ArtParity595](Research/Plans/ArtParity595.md).

## ARTPARITY595 — Fixture-native artwork data for tvOS detection and focus (P0)

Owner: Maximum-mini-NUIAK. Plan: [ArtParity595](Research/Plans/ArtParity595.md). All results provisional for Joe. No promotion.

- [x] Read TTR replies 1962–1986 and acknowledge cursor 1986. Intake shelf pair 1968 (size, SHA-256, TTR verifier pass).
- [x] Frozen baseline on 8 TTR native-truth frames: 0/8 correct (v3, R5). FocusRing scores unfocused artwork as focused. [Report](reports/work/ARTPARITY595/shelf-pair-report.md).
- [x] Alex and Sam crops through the NUIAK production crop path; scores equal the runtime receipt (0.996 / 1.000). TTR-executed crops remain unavailable (`crop_identity`).
- [x] Review the 4 retained iOS losses: 3 low-contrast secondary text in rows, 1 label-geometry case; no clipping. [Review](reports/work/ARTPARITY595/ios-losses.md).
- [x] Send TTR the intake receipt, hard-negative fields and 5 capability requests (cursor 1992); route 6 BigDog messages (cursor 1994). Forward IDs pending.
- [x] Build TTR and Fixture at `8053ed1b` in `TTR/.local-work/artparity595`. Ingest script `scripts/artparity595_ingest.py`.
- [ ] Replace the idle running TTR app (`nuiak572` build) with the `8053ed1b` build. Blocked: the auto-mode safety check denied stopping the app. Needs Joe.
- [x] Capture 12 Programme screens (36 native-truth frames, all `verified_reopened`); ingested to `dataset/tvos_captures/artparity595/programme` (18 train, 18 lineage holdout).
- [ ] E1 (detector) waits for complete per-frame labels: R5 finds ≥ 3 unlabeled text items per frame (amendment in the plan).
- [ ] Proposal FIXTURE-SCALE597 (needs Joe): scale to 2,000–5,000 varied Fixture frames via `fixture batch` recipes or a TTR batch mode,
  seeded variation, complete SDK labels per frame; holdout by layout and asset lineage; judge on real apps only.
- [ ] Implement the adapter from Programme sidecars to the `sdk_native589` crop membership; then register E2, E3, E5 FocusRing arms.
- [ ] HARDNEG596 (no capture): FocusRing hard negatives from tvos560 generator crops. Plan: [HardNeg596](Research/Plans/HardNeg596.md).
  Queued 2026-11-07: 6 T06 fits (control ×2 seeds, mixed, hardneg, hardneg-mixed ×2 seeds; 10,400 rows each; about 25 min each) and 18 T37 evaluations; fdr001 baseline evaluations done.
  After the runner finishes: score all fits on the ARTPARITY595 frames (shelf, eligibility, Northstar) with the PyTorch crop path, apply the plan rule, report to Joe. No promotion.

## Parallel continuation — NATIVE590, IOS591, TEMPORAL592, and IOS594

Owner: Maximum-mini-NUIAK. Plan: [parallel comparisons](Research/Plans/Parallel590592.md). [Provisional results](Research/Parallel590592Results.md).
Keep all findings provisional for Joe. Standard and shipped models stay unchanged.

- [x] Repair admission for empty no-focus inventories. Verify 30 training crops and 12 development crops without another capture.
- [x] Execute the exact native repair graph within the remaining approved budget. Preserve its failed predecessor and unused specifications.
- [x] Review the 2 native fits. Both lose 11 legacy decisions. The native arm gains 4 related development selections.
- [x] Compare retained iOS training-best weights against fixed-final. The comparison fails retention. Stop checkpoint selection.
- [x] Score 6 native movement pairs with 3 frozen temporal models. Each gets 5 correct and misses the same case.
- [x] Review before-frame ablation. All 5 paired successes disappear after removal. Moving-background and dismissal coverage remain unavailable.
- [x] Admit IOS594 foreground-only geometry preservation through the existing runner. Keep all matched retention vetoes.
- [x] Record Joe’s explicit bounded-follow-up approval and admit all 4 NATIVE593 nodes.
- [ ] Review all findings before any accepted metric change or model promotion.

Native training counts distinguish presentations, unique rows, and unique image pixels. Original receipts remain preserved.
The runner owns execution. No TTR source, service, deployment threshold, or shipped model changes.

## Campaign preparation — next measured use

Owner: Maximum-mini-NUIAK. [Completed trial](Research/LangGraphPreparation586Results.md).
Runtime isolation, exact admission, persistent campaign state, and independent diagnostic progress verify.
Keep the LangGraph controller optional. Manual-work savings remain unmeasured.

- [ ] P1: measure hands-on preparation and release delays on the next eligible model campaigns.
  Reuse the existing templates and runner. Include preparation, repair, and review costs.
  See [consolidated LangGraph findings](Research/LangGraphFindings.md). Manual savings remain unestablished.
  Require fewer actual interventions or shorter avoidable delays before wider adoption.
  Do not infer improvement from job count or model accuracy claims.

## Standard delivery and remaining qualification

Owner: Maximum-mini-NUIAK. [Latest nightly review](Research/NightlyReview20261108.md).
Completed FOCUS581, FOCUS583, IOS579, and IOS582 execution is archived in CompletedTasks.md.
All computed findings remain provisional. No accepted metric or model promotion changes.

- [ ] P0: publish the Standard package hook through the next authorized Git handoff. Then verify TTR’s executed-input receipt.
  Owner: Maximum-mini-NUIAK. Preserve Sillycon-TTR’s reported pause. A reconstructed RGB hash does not satisfy this gate.
- [ ] P0: qualify actual focus, native readiness, and complete control coverage in the existing real applications.
  Reuse SDK572 and SDK539-APPS. Keep unobserved labels unknown. Do not add a second app-integration project.
- [ ] P1: finish the approved NATIVE589 and IOS588 graphs. Select corrections only after complete matched retention reports.
- [ ] P1: implement the shared temporal recipe using existing SDK hooks. [Exact scope](reports/work/FOCUS568/temporal-next.md).
  Record real background changes, observed focus, action timing, and transition versus settled frames. Reuse one adapter across scenarios.
- [ ] P1: prepare native negative crops with enabled visible controls and an observed no-focus reference.
  The disabled-control recipe produces no enabled negative crops. Preserve actual focus evidence and reject unavailable references.
  Freeze groups, roles, exact specifications, and existing capture budgets before admission. This nightly review performs no implementation or capture.
- [ ] P1: retain independent HCF qualification. Standard profile inference does not establish HCF observations.
- [ ] Joe review: inspect provisional findings for B405-280 through B405-286 before any accepted metric update or promotion.
- [ ] P2: make the queue report tolerate completion during readiness checks.
  Owner: Maximum-mini-NUIAK. Requirement: use a verified terminal state when the same check returns `job_state:complete`.
  Acceptance: cover pending-to-complete and running-to-complete transitions without hiding genuine blockers or rerunning a completed job.
  This affects counts only. It does not block execution. Existing implementation authority covers a later interactive tranche.

## Nightly review — November 4, 2026

Owner: Maximum-mini-NUIAK. See [the review](Research/NightlyReview20261104.md). Results remain provisional.
- [x] Review 148 attempts: 136 complete and 12 failed. Verify all final output inventories.
- [x] Reject IOS573 replacement: 1 gain and 2 losses against the matched control; 16 Run013 losses.
- [x] Reject HCF574 strict replacement: 14 correct selections versus 16, with 2 lost successes. Preserve the working observer.
- [x] P0: register and test the native adapter under UNBLOCK575. Four capture jobs and four dependent reviews are approved.
- [ ] P0: qualify focus and readiness hooks in NewsTV, Photo Guessing Game, and Swiftfin. Authentication alone does not qualify labels.
- [ ] P0: finish Standard executed-buffer receipts through TTR. Preserve shipped models and existing thresholds.
- [ ] P1: select one distinct iOS correction from IOS573 failure cases. Do not repeat the rejected preservation factor.
- [ ] P1: correct the replay condition receipt through an immutable successor. Keep the contradicted boost branch unselected.
- [ ] P1: fix stale dashboard snapshots without changing execution ownership.
Four native configurations are prepared, not admitted. Their combined reservation is 3200 s and 400 MB, not ready duration.
Fresh queue: 0 ready, 0 running, 399 dependent blockers and 3 other blockers. Useful ready duration is 0 s.
Catalog preparation records: B405-277, B405-278. No jobs are admitted, released, or continued during the November 4 review.

## METRICS571 — Incorrect metric references

- [x] Trace and retract circular RC561 accuracy, unreviewed replacement scores, WSP threshold claims, and unmeasured projections.
- [x] Preserve raw artifacts and before-change documents. Disable invalid RC561 producer and benchmark entry points.
- [ ] Obtain reviewed references and fresh application flows before proposing new accepted metrics.
See [metric audit](Research/MetricClaimsAudit571.md).


## IOS570 — iOS geometry preservation

- [x] Execute the matched geometry-preservation fit and full retention graph. All 19 jobs complete. The fit takes 1208 s. [Plan](reports/work/IOS570/plan.md).
- [x] Review provisional geometry results. Against the matched control: 3 gains and 2 losses. Against Run013: 21 gains and 15 losses. Reject replacement.
- [x] Select and evaluate IOS573 foreground geometry preservation. It fails retention. Select a distinct next correction from its lost cases.


## FOCUS568 — Native focus data and matched training

Owner: Maximum-mini-NUIAK. Plan: [Verified focus graph](reports/work/FOCUS568/plan.md).
- [x] Execute production crop preparation with verified source roles. All 92 pairs pass; the corpus has 294 training crops and 42 validation crops. Exclude 16 reserved protocol samples.
- [x] Recover completed receipts without retraining and score both fits. Both fail focus acceptance. The native fit loses 2 legacy successes; neither recovers full-screen selections. [Recovery](reports/work/FOCUS568/recovery.md).
- [x] Evaluate the predefined replay condition. It fails; keep the extra fit unselected.
- [ ] Implement the shared temporal motion/removal recipe using existing SDK hooks. [Exact requirements](reports/work/FOCUS568/temporal-next.md).
The tvOS and iOS detector graphs continue independently. Standard and optional HCF remain unchanged.
- [x] Integrate SDK dd4a2112 in the 3 source-built apps. Nine metadata observations authenticate successfully.
- [ ] **RC561-SDK-DELIVERY — P0.** Qualify actual focus, native readiness and visible geometry before benchmark capture. All 9 observations report unknown focus. [Consumer sequence](reports/work/FOCUS568/sdk-followup.md).
- [x] Fix unknown-focus and unresolved-role false passes in the SDK qualifier. Five tests pass; all resulting reports remain provisional.



## PARALLEL567 — Independent model graphs

Owner: Maximum-mini-NUIAK. Plan: [Cross-model work](reports/work/PARALLEL567/plan.md).
- [x] Compare 2 matched tvOS role initializers with fixed training and full generated-screen scoring. Four lost detections reject replacement. DIAG569 investigates their causes.
- [x] Compare iOS backbone freezing plus the classification teacher. Fifteen Run013 losses reject replacement. DIAG569 uses cached predictions to select the next correction.
- [ ] FOCUS568 implements qualification of FOCUS556 through production crops. Do not reuse the scratch manifest as admitted evidence.
- [ ] Prepare independent temporal content-motion and departure pairs with observed focus and timeline evidence.
- [ ] Prepare independent optional-HCF profile pairs and no-focus distractors. Preserve the working observer.
Keep all results provisional. The detached runner executes the admitted detector graphs.
The 25 jobs implement 2 independent comparisons, not 25 investigations. Catalog records: B405-271 and B405-272. Admission and current counts: reports/work/PARALLEL567/handoff.json.


## CORRECTION564 — proposal coverage correction

Owner: Maximum-mini-NUIAK. Plan: reports/work/CORRECTION564/Plan.md.
The surgery arms preserve legacy decisions but recover 0/21 selections. Results remain provisional.
- [x] Execute the four-job matched proposal correction through the detached runner. All 4 jobs complete. Corrected coverage is 17/21; selections remain 0/21. Results stay provisional.
- [ ] Review recovered cases, losses, wrong selections, and proposal coverage before selecting a training correction.


## Explicit user review — November 4, 2026

Owner: Maximum-mini-NUIAK. Policy: [UserEvidenceApproval](Research/UserEvidenceApproval.md).
- [x] Keep results provisional and require explicit chat approval before publishing claims or promoting models.
- [x] Remove signature verification, key enrollment, and protected-account requirements from this workflow.
- [ ] Present the next metric update or promotion proposal with evidence for Joe's review.

## WSP trial — controlled comparisons (November 3, 2026)

Owner: Maximum-mini-NUIAK. Plan: [Weight surgery trial](Research/Plans/WeightSurgeryTrial20261103.md).
- [x] P0: qualify source ancestry, evaluator independence, and real-checkpoint adapter support. SURGERY562 verifies retained ancestry records and tests real queue candidate creation.
- [x] P1: run the four fixed FocusRing arms through the detached queue. All arms complete; none recovers a full-screen selection.
- [ ] P1: compare random and projected detector heads with matched T89 training; repeat seed only after support.
- [ ] P1: report outcomes and select conditional qualification or diagnosis. No promotion in this trial.
SURGERY562 admits all 11 exact jobs. The background runner starts execution. Handoff snapshot: 2 complete, 1 running, 4 ready, 4 dependent.
SURGERY562 implements the 11-job diagnostic graph. Exact admission and execution status are recorded in reports/work/SURGERY562.
PARALLEL567 qualifies the T89 seed and initializer-preservation extension. Owner: Maximum-mini-NUIAK.
Acceptance: preserve old defaults, expose seed 42, verify loaded tensors before the first optimizer step, and admit matched fixed-epoch fits after qualification.

See [the November 1 review](Research/NightlyReview20261101.md).
IOS551 completes without resolving retention losses. Three cached CAPTURE553 comparisons are admitted; no overnight reserve is established.
See [ITERATION549 results](Research/Iteration549Results.md).

## REALAPP554 — First real-app measurements (P0, highest priority)

Owner: Maximum-mini-NUIAK. Plan: [RealApp554](Research/Plans/RealApp554.md). Parent: MEASURE553 M3.
2026-11-01: RA554-01 to 10 and the review recheck are done. Baseline: `reports/work/REALAPP554/pilot-v2/baseline-report.md`.
NewsTV control recall 23 / 207, COCO AP50 0.206. Focus: 0 of 15 focused frames found.

- [ ] **RA554-16 — P0.** Retrain FocusRing with real-app-like hard negatives (images, sheets, plain buttons) and pill-style focus. Compare on the RA554-15 set, then once on the holdout.
  Plan: [FOCUS556](Research/Plans/FocusRealApp556.md). About 3 h. Gates: development D1–D3, retention R1 (270 of 270), holdout once.
  - [ ] S1 — Qualify the in-progress focus_candidates556.py implementation and connect the development-only comparison to the queue.
    Owner: Maximum-mini-NUIAK. Acceptance: pinned checkpoints, crop parity, recorded retention, unchanged thresholds, no pilot reads, and exact job admission.
    Existing FOCUS556 authority covers this work. No new implementation occurs during the nightly review.
    Measured directly on 2026-11-01 (`focus556-s1.json`, `focus556-s1-retention.json`): checkpoint SHA-256s pinned, Core ML parity 187/187, thresholds unchanged, no pilot reads.
    Result: no candidate keeps retention (best R1 218/270). FDR-003 recognizes the pills; FDR-014 cuts false highs to 4 of 157.
    Still open: exact queue job admission for this comparison.
  - [x] S2 — Capture a training-only Fixture batch (role `focus-training`). Approved by the maintainer, 2026-11-01, as FocusRing training data.
    Done: 18 recipes, 92 rows, 184 frames (4K), 0 rejected; 31 selected-but-unfocused tab rows. 0 real-app pixel overlap. Receipt: `reports/work/FOCUS556/s2-receipt.json`.
    Data: `dataset/tvos_captures/focus556/out-4k` (gitignored). The producer split is advisory; S3 assigns groups.
  - [ ] S3 — Build the corpus: FDR-038 training set plus S2 crops; verify no real-app pixels.
    Status: open. An ad-hoc scratch script assembled 124 pairs without runner admission. Reopened under recovery plan. See [BreachOfTrustAudit20261103](Research/BreachOfTrustAudit20261103.md).
  - [ ] S4 — Train F1 (control) and F2 (hard negatives and tab pills); F3 only on its registered condition.
    Status: open. An unadmitted local script ran exploratory training. Reopen until approved queue admission runs. See [BreachOfTrustAudit20261103](Research/BreachOfTrustAudit20261103.md).
  - [ ] S5 — Measure, choose at most 1 candidate, measure the pilot holdout once. No promotion in this plan.
    Status: open. Previous exploratory results failed development gates. Reopened under recovery plan.
  Open dependency: background-fill focus style. Continue supported native tab recipes while the capability request is unresolved.
  Request sent to Maximum-mini-TTR, 2026-11-01: opaque focused and unfocused pill fills for `custom` focus. Stored at cursor 1847; not read yet.
  Qualification note: the inspected pilot is retained regression evidence. Reserve fresh flows for independent qualification.
- [ ] **RA554-11 — Decision.** Approve or decline a local Jellyfin server for Swiftfin content.
- [ ] **RA554-12 — Decision.** Approve or decline the Moonlight clone and the WeatherFeels Metal toolchain.
- [ ] **RA554-13 — P1.** Freeze multi-app holdout qualification set across qualified open-source applications.
  - Status, 2026-11-03: open. The agent previously marked this complete with agent-crafted reference labels.
  - The 8 screens in `reports/work/RC561/captures/` remain diagnostic development evidence.
  - They do not count as a frozen qualification holdout.
  - Reopened under [ModelQualificationRecovery20261103](Research/Plans/ModelQualificationRecovery20261103.md). See [BreachOfTrustAudit20261103](Research/BreachOfTrustAudit20261103.md).

## RC561 — SDK-qualified real-app corpus (P0, maintainer request 2026-11-02)

Plan: [REALCORPUS561](Research/Plans/RealCorpus561.md). Owner: Maximum-mini-NUIAK. Estimate: 30–50 h over several sessions.
Decisions 2026-11-02: clones approved (no VLC); local Jellyfin approved. Later the same day: the corpus is validation and analysis only (no training); target 100 layout-distinct screens.

- [ ] **RC561-01 — SDK qualification gate tooling.** Compute coverage, geometry, class, focus, alignment and stability from SDK drafts and review results.
  - User story: As the corpus owner, I want a measured SDK accuracy result per app, so that SDK labels are trusted only where they are accurate.
  - Acceptance criteria: an offline test covers each gate; NewsTV pilot data reproduces 207 of 207 confirmed rectangles.
  - Status, 2026-11-02 01:15: done. `scripts/sdk_qualification561.py` + `test_sdk_qualification561.py` (2 tests pass).
    Pilot review (`reports/work/RC561/sdk-qualification-pilot.json`): NewsTV 207 kept, 0 missed, 0 flagged, role 1.0; fails focus (SDK focus unknown on 9 of 9) and sample (9 frames).
    Photo Guessing Game and Swiftfin had no SDK hooks (0 SDK boxes).
- [x] **RC561-02 — Qualify the 3 current apps.** NewsTV, Photo Guessing Game, Swiftfin (absorbs RA557-08).
  - Acceptance criteria: each app has a gate table and a pass or fail with the failure mode.
  - Status, 2026-11-02: done ([report](reports/work/RC561/qualification-report.md)). All 3 apps fail automated qualification (NewsTV fails focus state and sample size; Photo Guessing Game and Swiftfin lack SDK hooks). Ground truth stays human-reviewed.
- [x] **RC561-03 — Intake new apps (C1).**
  - Acceptance criteria: license, revision, dependency and build receipt for each; failures recorded.
  - Status, 2026-11-02: done. Build receipts recorded for all candidates in `reports/work/RC561/`:
    - `apple-media-catalog-build-receipt.json`: build passed (arm64, x86_64).
    - `strimr-build-receipt.json`: build passed (arm64).
    - `plozz-build-receipt.json`: build passed (arm64).
    - `provenance-build-receipt.json`: build failed (requires recursive submodule checkout for `Cores/`).
    - Exclusions recorded: Apple-TV-Player and VLC skipped (CocoaPods); Moonfin skipped (dead repository URL).
- [x] **RC561-04 — Controlled content and multi-app navigation (C2, C3).**
  - Status, 2026-11-02: complete. Controlled content, multi-tab navigation, and live 4K captures verified on Simulator `62DA0048-BB6A-4726-9CCC-F842DF7BE985`:
    - Local Jellyfin 12.4 loopback server active on port 8096 for media-server apps (`plozz`, `strimr`, `swiftfin`).
    - `apple-media-catalog`: added `--tab <Stack|Buttons|Description|Search|Sidebar>` CLI argument support. Rebuilt and captured 5 distinct 4K flow screens.
    - `plozz`: captured `plozz-screen-01.png`.
    - `strimr`: captured `strimr-screen-01.png`.
    - `swiftfin`: launched on booted Simulator, captured `swiftfin-screen-01.png`.
    - Candidate model R5 Core ML evaluation (`scripts/eval_rc561_r5.py`) across all 8 screens detected 211 native UI controls (84 button, 71 cell, 35 text, 18 picture, 2 bar, 1 segmentedControl) with zero runtime faults.
    - Detections and bounding boxes recorded in `reports/work/RC561/rc561-detections-r5.json`. Next: ground-truth labeling and holdout scoring (RC561-05 / RA554-13).
- [ ] **RC561-05 — Multi-app holdout independent labeling and comparison against Standard (C4).**
  - Status, 2026-11-03: open. The agent previously created self-authored bounding boxes without human review.
  - Scored claims (50.00% recall, 19.43% precision) are invalid as independent accuracy evidence.
  - Reopened under [ModelQualificationRecovery20261103](Research/Plans/ModelQualificationRecovery20261103.md). See [BreachOfTrustAudit20261103](Research/BreachOfTrustAudit20261103.md).
  - Shipped models remain preserved. No promotion.
- [ ] **RC561-06 — Corpus capture and audit (C5).** Target: 8 qualified apps, 60 flows, 600 frames.
- [ ] **RC561-07 — Data roles (C6).** At least 3 holdout apps; other roles per D2.

## WSP — Weight-Space Programming for UI Perception Models (P1, follows ADR-0033)

Owner: Maximum-mini-NUIAK. Authority: [ADR-0033](Research/ADR-0033-Weight-Space-Programming-for-Perception-Models.md).
Goal: enable closed-form weight manipulation, linear projection, and task vector arithmetic without backpropagation or catastrophic forgetting.

- [x] **WSP-01 — Weight-Space Head Linear Projection Tooling.**
  - Status, 2026-11-02: complete (`scripts/wsp_head_projection.py`). Built projection matrix $P \in \mathbb{R}^{13 \times 41}$ from `ROLES559` taxonomy and transformed YOLO11 classification conv layers across all 3 detection scales ($W_{13} = P W_{41}$, $b_{13} = P b_{41}$) in closed-form. Tested on `phase6a_r013` with zero backpropagation.
- [x] **WSP-02 — Focus Bias Calibration and Task Vector Blending.**
  - Status, 2026-11-02: complete (`scripts/wsp_focus_patch.py`). Evaluated task vector arithmetic $\theta^* = \theta_0 + \alpha(\theta_{fdr003} - \theta_0) + \beta(\theta_{fdr014} - \theta_0)$ on MobileNetV4 FocusRing architecture across 278 layers.
  - Results (`reports/work/WSP/wsp-focus-results.json`): blending $\alpha = 0.20$ gives 10 of 10 pill crops scores above 0.01. This is not recall at 0.85. It suppresses positive decisions and fails acceptance.
- [x] **WSP-03 — Multi-Attribute Task Vector Arithmetic and Head Projection.**
  - Status, 2026-11-02: complete (`scripts/wsp_focus_retention.py`). Discovered head-space projection (`conv_head` + `classifier`, $\alpha = 0.50$) preserves 270/270 legacy retention decisions.
- [x] **WSP-04 — In-Distribution Retention Guard Verification.**
  - Status, 2026-11-02: complete (`scripts/wsp_focus_retention.py`). Head-projected model keeps 270/270 legacy retention (100% correct, 0 FN, 0 FP).
  - Development finding: fails all 3 real-app development gates on 21 focus frames (D1=3/21 vs gate $\ge 12$, D2=16/21 vs gate $\le 8$, D3=1/21 vs gate $\ge 5$). "10/10 pills" only reflects scores > 0.01, below 0.85 acceptance. Models remain experimental; shipped models preserved.
- [x] **WSP-05 — Experimental export and Core ML parity.**
  - Status, 2026-11-02: complete (`scripts/wsp_export_winning_model.py` and `scripts/wsp_verify_parity.py`).
  - Core ML package exported: `NativeUITrainer/focus_ring_runs/wsp01-head-conv050/export/FocusRingDetector.mlpackage` (5.03 MB).
  - Parity verified across both 270 legacy test crops and 187 REALAPP554 crops (decision agreement on the inspected crops only, max diff 0.0035, median diff 0.0010; `reports/work/WSP/wsp-parity-report.json`). No promotion.

## REALAPP557 — Improve real-app results (P0, follows REALAPP554)

Owner: Maximum-mini-NUIAK unless a task names another owner.
Goal: raise real-app detection and focus results on the shipped tvOS path, with evidence that the gains are real.
Sources: [pilot baseline](reports/work/REALAPP554/pilot-v2/baseline-report.md), [focus diagnosis](reports/work/REALAPP554/focus-diagnosis.md),
[focus development baseline](reports/work/REALAPP554/focus-dev-baseline.md), [FOCUS556 plan](Research/Plans/FocusRealApp556.md).

Baseline to beat (shipped models, TTR ac85177b, Simulator 62DA0048):

| Measure | Value | Set |
|---|---|---|
| Control recall | 23 / 207 | NewsTV pilot, 9 screens |
| `secondaryButton` (tab pills) recall | 1 / 153 | NewsTV pilot |
| `collectionItem` (cards) recall / precision | 22 / 54, 22 / 24 | NewsTV pilot |
| COCO AP50 / AP75 | 0.206 / 0.0 | NewsTV pilot |
| Focused controls found | 0 / 15 pilot, 0 / 21 development | 3 apps |

Rules for every task:
- Tune and compare on the focus development set (`review-dev`). Measure the pilot holdout (`review/labels-v2`) once per chosen candidate.
- Real-app pixels never enter training. NewsTV, Photo Guessing Game and Swiftfin are evaluation-only.
- A model candidate must keep previous successes: FocusRing 270/270 legacy decisions; the tvOS detector synthetic validation set.
- Register each training run in Research/ExperimentLog.md before it starts. Keep failed attempts and checkpoints.
- Record each result in this section and in the linked report. Do not change thresholds without development-set evidence.

Order: RA557-01, 02 and 03 first (diagnostics, no training). Their results set the design of RA557-04 to 06.

### Diagnostics (no training)

- [x] **RA557-01 — P0. Box tightness and resolution.** Estimate: 30 min.
  - User story: As the detector owner, I want to know why no detection reaches IoU 0.75, so that I fix the cause, not the symptom.
  - Requirements:
    1. For each of the 207 reviewed NewsTV boxes, find the best same-class and any-class detection. Record IoU and edge offsets in pixels.
    2. Report the IoU distribution and the mean signed offsets of left, top, right and bottom edges, and the width and height ratios.
    3. Downscale the 9 NewsTV frames to 1920 × 1080, replay them through the same runtime, and score them the same way.
    4. Keep the original 4K results unchanged. Write new outputs only.
  - Acceptance criteria:
    - A report gives the IoU histogram, systematic offsets, and 4K versus 1080p recall, AP50 and AP75.
    - The report names 1 primary cause (resolution, letterbox mapping, or box style) with its evidence, or states that the data cannot decide.
    - If 1080p improves AP75 or recall, the report gives the size of the gain and proposes the consumer change (input scaling).
  - Inputs: `review/labels-v2`, `replays/`, `scripts/real_app_pilot554.py`. Dependency: TTR `visual replay` (standing launch approval).
  - Out of scope: retraining, threshold changes.
  - **Result, 2026-11-01:** [report](reports/work/REALAPP557/ra557-01-box-tightness.md). Cause: box definition and class confusion, not resolution.
    Cards: width ratio 0.99, height 0.53 (the title area is outside the detection). Pills as `label`: text inside the pill, IoU 0.57. Pills as `primaryButton`: IoU 0.96.
    1080p input gives the same recall (23/207) and AP50 (0.206). No scaling change.
    Decision for the maintainer: `collectionItem` convention, whole cell with title (taxonomy, recommended) or artwork only.
    Source check: Fixture `pixel_bounds` (the `collectionItem` label) is the whole cell (440 × 420 px incl. caption); `artwork_geometry` (440 × 294) is separate telemetry.
    NewsTV SDK and the taxonomy also use the whole cell. Only `scripts/generate_tvos_dataset.swift`, which trained `nativeui-tvos-v3.0`, boxes the artwork alone.
    **Decision, 2026-11-01 (maintainer): whole cell.** Recorded in `Research/NativeUIElementDetection.md` §5.2.1. Generator change: RA557-13.

- [x] **RA557-02 — P0. Text proposals as focus candidates.** Estimate: 20 min.
  - User story: As the focus owner, I want focus candidates to include controls that the detector labels as text, so that pills can be selected at all.
  - Requirements:
    1. Score every proposal, including `label`, on the 21 development frames with the shipped FocusRing through `makeCrop`.
    2. Count focused controls with a covering candidate (IoU ≥ 0.5): non-text candidates only, and all candidates.
    3. Report the rank of the covering candidate and the number of candidates ≥ 0.85 in both cases.
    4. Repeat on the pilot only as a final check, after the development result is recorded.
  - Acceptance criteria:
    - Coverage with and without text proposals, per app, on the development set.
    - A statement of whether text proposals add coverage, and how many false highs they add.
    - No change to the runtime policy in this task. A policy proposal goes to RA557-06.
  - Inputs: `focus-dev-baseline.json`, `scripts/focus_diagnosis554.py`, `replays-dev/`.
  - **Result, 2026-11-01:** [report](reports/work/REALAPP557/ra557-02-text-candidates.md). Do not add text proposals: coverage stays 9 of 21; NewsTV false highs rise from a median 2 to 20 per frame.
    Cause: the detector proposes nothing on 5 of 5 focused main-tab pills, and only IoU 0.39–0.54 boxes on category pills.

- [ ] **RA557-03 — P0. Missed article cards.** Estimate: 30 min.
  - User story: As the detector owner, I want the 32 missed cards grouped by cause, so that new training data targets the right conditions.
  - Requirements:
    1. For each missed card, record row, column, scroll state, focus state of the frame, card size, and whether it touches content edges.
    2. Record the nearest detection of any class and its IoU.
    3. Compare the misses with the 22 found cards on the same attributes.
  - Acceptance criteria:
    - A table of miss causes with counts that adds up to 32.
    - For each cause, the Fixture or generator data that covers it, or a statement that no current producer covers it.
  - Inputs: `pilot-v2/report.json`, SDK snapshots in `capture-newstv/`.

### Model work

- [ ] **RA557-04 — P0. FocusRing retraining (FOCUS556 S3–S5).** Estimate: 2 h.
  - User story: As a TTR user, I want FocusRing to recognize real-app focus and reject unfocused content, so that focus selection works on real apps.
  - Requirements:
    1. S3: build 1 corpus from the FDR-038 training set and the S2 Fixture crops. Hold out 20% of S2 groups as Fixture validation.
    2. Verify crop parity through `makeCrop`, file and pixel hashes, and 0 real-app pixels.
    3. S4: register and run F1 (replay-only control) and F2 (replay plus S2). Register F3 with its condition (F2 passes D1 and D2 but fails R1).
    4. All runs: FDR-001 initialization, seed 42, ≤ 30 epochs, ≤ 30 min, ≤ 2 GiB, learning rate 0.00003, last checkpoint.
    5. S5: measure D1–D3 and R1–R3. Choose at most 1 candidate. Measure the pilot holdout once.
    6. When Maximum-mini-TTR supplies the pill-fill feature (cursor 1847), capture it as a follow-up batch. Do not wait for it.
  - Acceptance criteria (from FOCUS556):
    - Supported: D1 ≥ 12 of 21 with pills > 0 on ≥ 5 of 10; D2 ≤ 8 of 21; D3 ≥ 5 of 21; R1 270/270.
    - Any R1 loss is a regression and rejects the candidate.
    - A report gives every run, its results, and the decision. Checkpoints and failed runs are kept.
    - No Core ML replacement of the bundled model in this task.
  - Dependencies: S1 queue admission (nightly review item); RA557-02 result for the candidate set.

- [ ] **RA557-05 — P0. Detector tab-pill and text separation.** Estimate: 3 h, plus capture.
  - User story: As a TTR user, I want tab and category pills detected as controls, so that audits and focus see them.
  - Requirements:
    1. Write a training-only Fixture batch for the tvOS detector: `tabs`, `nested_tabs_v1` and `buttons` with text-only pills, light and dark.
    2. Add plain-text hard negatives: `canvas.labels` text near pills and cards.
    3. Get maintainer approval for the detector training role of this new batch. The S2 data is approved for FocusRing only.
    4. Fine-tune 1 tvOS detector candidate with full replay of the original synthetic training set.
    5. Evaluate on the 10 NewsTV development frames (pill focus) and the tvOS synthetic validation set.
    6. Include **focused** pills (filled and scaled) as positives. RA557-02 shows no proposal on 5 of 5 focused main-tab pills.
    7. Report detector coverage of the focused control on all 21 development frames (baseline: 9 of 21 at IoU 0.5).
  - Acceptance criteria:
    - `secondaryButton` recall on development pills rises from the measured baseline. The report states the baseline from the shipped model.
    - Focused-control coverage on the development set rises from 9 of 21.
    - tvOS synthetic validation mAP@0.5 stays within 0.01 of 0.9822 and no class loses more than 0.02 AP.
    - The candidate is measured once on the NewsTV pilot holdout. No promotion without the existing gates.
  - Dependencies: RA557-03; RA557-13 (whole-cell card labels). RA557-01 found no resolution fix is needed.
  - Label rule: Fixture `pixel_bounds` (whole cell). Do not use `artwork_geometry` as a detector label.

- [ ] **RA557-06 — P1. Focus selection policy.** Estimate: 1 h.
  - User story: As a TTR user, I want 1 focus answer when 1 candidate is clearly ahead, instead of an abstention whenever 2 candidates pass 0.85.
  - Requirements:
    1. After RA557-04, define a ranked policy: top candidate ≥ 0.85 and ahead of the second by a fixed margin.
    2. Fix the margin values before measurement. Compare 3 values at most on the development set.
    3. Report correct selections, wrong selections, and false selections on no-focus frames.
  - Acceptance criteria:
    - The policy gains correct selections on the development set with 0 new false selections on no-focus frames.
    - The holdout is measured once, for the chosen policy only.
    - A TTR change request goes to the owner only after this evidence exists.
  - Dependencies: RA557-04; RA557-02.

- [ ] **RA557-07 — P1. Off-screen proposal suppression (REAL550-FOCUS).** Owner: Sillycon-TTR. Verifier: Maximum-mini-NUIAK.
  - User story: As a TTR user, I want 1 invalid proposal not to cancel focus selection for the whole screen.
  - Requirements: Sillycon-TTR supplies a source change. Maximum-mini-NUIAK builds it from source and replays the same 42 frames.
  - Acceptance criteria: the 6 suppressed frames (4 pilot, 2 development) no longer return `partial_provider_result`, and no other replay result changes.
  - Status: evidence sent at cursor 1843; not read yet. Do not send a duplicate.

- [ ] **RA557-13 — P0. Whole-cell `collectionItem` labels and detector retrain.** Estimate: 3 h (generation about 3 min, training about 1.5 h).
  - User story: As a TTR user, I want card boxes to cover the whole cell with its title, so that boxes match the SDK, Fixture and taxonomy and pass IoU 0.75.
  - Done, 2026-11-01: `scripts/generate_tvos_dataset.swift` boxes 7 card types on the cell container (app, poster, card, shelf, avatar, app card, channel).
    Titles keep their own `label` boxes. A 50-image check: only those 58 boxes change, 676 stay identical, and every new box contains the old artwork box.
    Pixels change by at most 1 of 255 on at most 120 pixels in 12 images (render rounding). The original generator is deterministic.
  - Requirements:
    1. Regenerate the tvOS dataset at the original size (5,000 images, 200 per family) into a new folder. Keep `dataset/tvos_dataset` unchanged.
    2. Export it to a new YOLO folder. Verify class counts and that only `collectionItem` boxes differ from the old export.
    3. Register 1 fine-tune in ExperimentLog.md: initialize from `nativeui-tvos-v3.0`, ≤ 30 epochs, ≤ 2 GiB, matched seed. Standing training approval covers it.
    4. Evaluate on the new synthetic validation split, the old split (retention, `collectionItem` excluded from the old split), and the 9 NewsTV development-safe frames only after RA557-03.
    5. Measure the NewsTV pilot holdout once for the chosen candidate.
  - Acceptance criteria:
    - Synthetic validation mAP@0.5 ≥ 0.97 on the new labels; non-card classes lose ≤ 0.02 AP on the old split.
    - On NewsTV cards, median same-class IoU rises above 0.75 and card recall rises above 22 of 54.
    - No promotion or Core ML replacement in this task. Combine with RA557-05 before a release candidate.
  - Dependencies: RA557-03 (card miss causes); RA557-05 uses the same whole-cell rule for its Fixture data.
  - **Result, 2026-11-01:** queue job `ra557-13-wholecell-ft` complete (1,331 s). Candidate **rejected**: `label` AP50 −0.049 and NewsTV card recall 27 → 12 of 54.
    The convention is learned on synthetic data (card median IoU 0.852 → 0.997), but synthetic 1-line cells do not match NewsTV cells with text blocks.
    Next: real-like cells (artwork plus headline and summary) and a `label` retention gate. [Report](reports/work/REALAPP557/ra557-13/report.md).
    Note: the generator repeats screens (3,124 unique of 4,500); the v3 validation shared 74 images with training.

- [ ] **RA557-15 — P0. Real-like cells and tab-pill variation (CELLS558).** Plan: [CELLS558](Research/Plans/RealLikeCells558.md). Estimate: 5–6 h.
  - User story: As a TTR user, I want the detector to find real tvOS cards and tab pills, so that whole-cell boxes improve real apps, not only synthetic screens.
  - Requirements: S1 decisions (nested artwork, keyboard keys); S2 generator variation for 6 low-variation families; S3 a new `tvOSContentCells` family with 6 variants;
    S4 development references (NewsTV development SDK rectangles, clean synthetic test); S5 runs C1 (variation) and C2 (plus cells) through T89; S6 gates.
  - Acceptance criteria: on NewsTV development frames, card recall and pill recall rise above the v3 baseline and card median IoU ≥ 0.75;
    `label` and every other class lose ≤ 0.02 AP50 on the clean synthetic test; focused-control coverage rises from 9 of 21. No promotion.
  - Facts behind it: `tvOSTopTabBar` has 4 unique screens of 200; keys supply most `collectionItem` boxes; RA557-13 lost NewsTV cards (27 → 12 of 54).
  - Decisions approved by the maintainer, 2026-11-01: S1.1 artwork inside a cell is not a separate `imageView`; S1.2 keys stay `collectionItem` with a 25% training cap.
    Recorded in Research/NativeUIElementDetection.md §5.2.1. S1 is done.
  - Rule: the NewsTV pilot holdout is spent for detector comparisons; use development frames and a fresh holdout (RA554-13).
  - Status, 2026-11-01 16:41: S1–S5 done (generator variation, `tvOSContentCells`, memberships, references, `scripts/cells558_evaluate.py`).
    S5: C1, C2, C1b and C2b timed out at 1,800 s under host load. 18:25: maintainer approved more time; `cells558-c1-r2` and `cells558-c2-r2` run with a 7,200 s limit.
    S6, 2026-11-01 20:40 ([report](reports/work/REALAPP557/cells558/report.md)): C1 contradicted. C2 passes development (cards 60/60, IoU 0.759, focus 9/21)
    but fails retention (`label` −0.027 on the tvos557 test). Pills stay low (C2 6/170, C1 20/170). Conditional third run held until ROLES559 R1 reports. No promotion.
    Open decision: tab item class (`primaryButton` in the generator, `secondaryButton` in TTR Fixture and the pilot review).
- [ ] **RA557-16 — P0. Role-based detector classes (ROLES559).** Plan: [ROLES559](Research/Plans/Roles559.md). Estimate: 2.5 h.
  - User story: As a TTR user, I want the detector to name what an element does (button, text, cell), so that look and focus do not split 1 role into several classes.
  - Requirements: a training-time map from 41 classes to 13 roles (`scripts/roles559.py`); run R1 on the C2 rows with role labels; score v3, C2-r2 and R1 on roles (`scripts/roles559_evaluate.py`).
  - Acceptance criteria: the decision rule in the plan is applied and recorded; the schema raw values are unchanged; no promotion.
  - Approved by the maintainer, 2026-11-01. Reference: Apple Screen Recognition (CHI 2021) role classes. The tab-class question is not needed for R1.
  - Result, 2026-11-01 22:05 ([report](reports/work/REALAPP557/roles559/report.md)): inconclusive. R1 vs C2: card IoU 0.954 vs 0.759, pills 20 vs 12 of 170,
    button AP50 +0.17 to +0.22; focus 6 vs 9 of 21, `adjustable` −0.277 and `toggle` −0.045 on tvos558. Focused pills now box at IoU 0.40–0.48. No promotion.
- [ ] **RA557-17 — P0. Tab pills as buttons (PILLS560).** Plan: [PILLS560](Research/Plans/Pills560.md). Estimate: 3 h.
  - User story: As a TTR user, I want tvOS tab and category pills found as buttons, so that tab navigation is visible to audits.
  - Requirements: shared `TabRow` with pill `button` and nested `label` boxes; new `tvOSTabRows` family; unchanged families keep identical pixels; run R2; score with `scripts/roles559_evaluate.py`.
  - Acceptance criteria: the decision rule in the plan is applied and recorded; no promotion.
  - Diagnosis: R1 calls 120 of 170 NewsTV pills `text` and merges tab words into 1 line; its `button` boxes fit (median IoU 0.89).
  - Status, 2026-11-01 23:00: generator done (`TabRow`, `tvOSTabRows`); `dataset/tvos560/pills` has 25 families pixel-identical to tvos558.
    `pills560-r2` registered (896 train, 120 calibration). Expected 1,800 s timeout, then restart `pills560-r3` at 7,200 s, then scoring against R1.
  - Result, 2026-11-02 ([report](reports/work/REALAPP557/pills560/report.md)): inconclusive. Pills 20 → 160 of 170, focus 6 → 12 of 21, cards 60/60 at IoU 0.937.
    Retention: `textField` −0.089 and AP50 −0.011 on tvos558 without tab bars; the `button` loss on old test sets is only the old tab labels. No promotion.
    `textField` diagnosis, 2026-11-02: the loss is all PIN entry slots (R2 misses 57 of 102; median score 0.26 vs 0.96). Navigation and keyboard fields are unchanged.
  - R3 result, 2026-11-02 ([report](reports/work/REALAPP557/pills560/report.md#r3--pin-slot-repair-2026-11-02)): inconclusive. PIN slots 64/64, `textField` 1.000, pills 160/170.
    Fails: focus 8/21 (gate 10), `indicator` −0.022 (gate 0.02). Tab-label `text` falls 0.944 → 0.447.
    Cause: keys have no nested `label`, tab pills do. Needs a maintainer rule for text inside buttons (option A or B in the report). No promotion.
  - R4, 2026-11-02: maintainer chose rule B (no `text` box inside a `button`). `pills560-ruleb-r4` registered (membership-r4, 1,594 text boxes removed, pixels unchanged). Score with `--rule-b`.
  - R4 result, 2026-11-02 ([report](reports/work/REALAPP557/pills560/report.md#r4--rule-b-2026-11-02)): contradicted (focus 8/21). All synthetic gates pass; tvos558 without tab bars AP50 0.961 (R1 0.938).
    Focus diagnosis: on focused NewsTV pills the model boxes the lifted platter (about 1.5 times the SDK layout frame; IoU 0.4–0.6). By §5.2.1 that is a box error. 4 Photo cells lose score after the PIN rows. No promotion.
  - Focused pill check, 2026-11-02: NewsTV tabs use `.buttonStyle(.plain)`; the system platter is 1.3–1.6 × 1.6–1.8 times the frame. The generator draws its platter at the frame, so the model learns platter boxes.
    Maintainer approved, 2026-11-02: `TabRow` `.plain` platter style added; `dataset/tvos560/platter` generated; `pills560-platter-r5` registered (rule in plan).
    Style 2 fixed, 2026-11-02: boxes captured outside the scale (43 images change labels only). R5 data has 3 affected rows, so no R6 run.
    Cells fixed, 2026-11-02: focused cells captured on an unscaled copy (`dataset/tvos560/cells6`, 605 images relabeled, pixels unchanged). `pills560-cells-r6` registered.
    Open: `tvOSAppSwitcher` scales every card (1.05 focused, 0.95 unfocused) after capture.
  - R6 result, 2026-11-02 ([report](reports/work/REALAPP557/pills560/report.md#r6--focused-cells-keep-the-frame-box-2026-11-02)): **supported**. Photo focused-cell IoU 0.263 → 0.623, focus 16/21, pills 168/170, no synthetic AP50 loss.
    Current best role model: `pills560-cells-r6`. No promotion. Next: fresh holdout (RA554-13) and Core ML parity.
  - R6 Core ML, 2026-11-02 ([report](reports/work/REALAPP557/pills560/report.md#r6-core-ml-export-and-parity-2026-11-02)): exported (`NativeUITrainer/pills560-r6/final.mlpackage`). Backend parity holds on identical pixels (median score diff 0.0024).
    The shipping 640 × 640 input gives NewsTV focused-pill IoU 0.587 (PyTorch 640 × 384: 0.660). Next gates must score the 640 × 640 path. Next: fresh holdout (RA554-13).
  - Rescore on 640 × 640, 2026-11-02 ([report](reports/work/REALAPP557/pills560/report.md#rescore-on-the-shipping-640--640-input-2026-11-02)): gains hold (pills 166–168, focus 16–17/21).
    R5 and R6 become inconclusive: R5 `bar` −0.054, R6 Photo gain +0.013. R4 becomes inconclusive. Gates now use 640 × 640.
  - Diagnosis of `bar` loss, 2026-11-02 ([report](reports/work/REALAPP557/pills560/report.md#diagnosis-of-bar-score-change-on-640--640-input-2026-11-02)):
    The `bar` drop is isolated to `tvOSSettings` top navigation headers under square letterbox padding (confidence shifted from ~0.28 to ~0.15; IoU remains 0.84–0.92).
    The historical report records no misses in the inspected AVKitPlayback, ControlCenter, SidebarMenu, and tvos560Tabs slices. This is development evidence. R5 is selected as primary candidate for the fresh holdout (RA554-13).
  - R5 Core ML parity, 2026-11-02 ([report](reports/work/REALAPP557/pills560/report.md#r5-core-ml-export-and-parity-2026-11-02)):
    Exported `NativeUITrainer/pills560-r5/final.mlpackage` (5.1 MB). Backend parity holds on identical pixels (median score diff 0.0023, median IoU 0.9887).
    On shipping 640 × 640 letterbox: pills 168/170 (98.8%), cards 60/60 (median IoU 0.965), NewsTV focused-pill median IoU 0.601, Photo focused cell IoU 0.643, and focused coverage rises to 18 of 21 frames (85.7%). Next: fresh holdout (RA554-13).
  - R5 result, 2026-11-02 ([report](reports/work/REALAPP557/pills560/report.md#r5--system-plain-focus-platter-2026-11-02)): **supported**. NewsTV focused-pill IoU 0.454 → 0.631, focus 8 → 15/21, pills 169/170, no synthetic loss.
    No promotion. Next: fresh holdout (RA554-13) and Core ML parity; fix the style-2 label defect.
    R3 (`pills560-pin-r3`) adds 20 train and 2 calibration PIN screens to R2; registered with the 43,200 s guard. Rule in the plan.

### Measurement coverage

- [ ] **RA557-08 — P1. SDK registration for Photo Guessing Game and Swiftfin.** Estimate: 2 h.
  - User story: As the benchmark owner, I want SDK rectangles for every app, so that detection is scored on more than NewsTV.
  - Requirements:
    1. Add TTRDiagnostics hooks for buttons, fields, mode tiles and rows, as in `scripts/sdk539/newstv/`. Keep app behavior unchanged.
    2. Record the patch, the vendored file hashes and the build receipt.
    3. Recapture the existing development flows with SDK snapshots. Do not recapture the pilot holdout.
  - Acceptance criteria: both apps report registered rectangles in an active scene; drafts appear in the review page; the qualification receipt can set `sdkObservationsVerified` after review.

- [ ] **RA557-09 — P1. Text in the reference.** Estimate: 30 min, plus a decision.
  - User story: As the benchmark owner, I want text detections scored or excluded explicitly, so that control precision is not mixed with unreviewed text.
  - Requirements: decide 1 option. A: the scorer excludes `label` from control precision and reports text separately as unreviewed. B: a review pass adds text boxes.
  - Acceptance criteria: the report states the option. Precision numbers for controls no longer count the 285 unreviewed `label` detections as false.
  - Decision: maintainer chooses A or B. Recommendation: A now, B for the qualification set.

- [ ] **RA557-10 — P1. More apps and content (decisions).**
  - User story: As the benchmark owner, I want 5 qualified apps, so that results describe more than 1 app.
  - Requirements: maintainer decisions on a local Jellyfin server (RA554-11) and the Moonlight clone and WeatherFeels Metal toolchain (RA554-12).
  - Acceptance criteria: each decision recorded; approved apps get source builds, controlled content and the alert preflight.

- [ ] **RA557-11 — P1. Re-plan cases without a visible change.** Estimate: 20 min.
  - User story: As the benchmark owner, I want every planned case to show a different state, so that no case is a silent duplicate.
  - Requirements: find the correct presses for `newstv-news-home-second-article` and `swiftfin-connect-button` with SDK or OCR checks.
    Add a duplicate-pixel check to `real_app_session554.py session` that marks a case `failed: no_visible_change`.
  - Acceptance criteria: the session runner fails a case whose pixels equal the previous case; offline test covers it. New flows go to RA554-13, not to the pilot.

### Process fixes

- [ ] **RA557-12 — P2. Fixture endpoint ownership.** Estimate: 20 min.
  - User story: As a capture operator, I want a batch to refuse a Fixture endpoint that belongs to another Simulator, so that no attempt is wasted.
  - Requirements:
    1. Before `fixture batch`, check the port-8080 listener with `direct_tvos_capture.bind_target` for the target Simulator.
    2. Poll `/scene` until it answers before the batch. Stop the Fixture that the session started after the batch.
    3. Add these steps to the `tvtestrig` skill and update its manifest hash.
  - Acceptance criteria: a wrapper or documented command fails before the batch when the owner differs; offline test for the ownership check.

- [ ] **RA557-14 — P2. End-to-end runner self-test and dispatch check.** Estimate: 2 h. Idea source: memdoor `workflow-selftest` (read 2026-11-01; not installed, nothing adopted as code).
  - User story: As the maintainer, I want a self-test of the real runner process and a check that ready jobs start, so that a runner that answers but does not dispatch is found in minutes, not hours.
  - Context: 29 queue and 22 dashboard unit tests cover cycles, failed producers, interrupted attempts, timeouts, input changes, the runner lock and output limits.
    No test starts the actual dashboard server and runner. On 2026-10-31 a bad `--priority-task` value kept the server answering for about 7 h while it dispatched 0 jobs.
  - Requirements:
    1. Add `scripts/runner_selftest557.py`. It starts `research_dashboard_server.py` with `--resume-approved` on a free local port, against a scratch queue under `.build/debug-output/`.
    2. It submits canary jobs through the normal path: 1 quick success, 1 producer and consumer pair, 1 failing acceptance, 1 timeout, 1 output-limit breach, and 1 job whose input changes after submit.
    3. For each case it records PASS or FAIL with evidence (job state, attempt files, exit code) in `SELFTEST-<UTC time>.md` and a JSON receipt. Any FAIL makes the command exit 1.
    4. Each run includes a dispatch-liveness case: a ready approved job must start within a fixed limit (60 s) after the server starts.
    5. It stops the server and leaves the live queue (`reports/work/research-queue`), the port-8765 dashboard and all real jobs unchanged.
    6. Add a read-only `--check-live` mode: on the live dashboard, report the oldest ready approved job that has not started, and warn when it waits longer than 10 min. No job changes.
  - Acceptance criteria:
    - The self-test passes on the current code. Each negative case fails for its documented reason, and the report shows the evidence.
    - Reintroducing the 2026-10-31 fault in a scratch copy (an invalid priority-task value that skips validation) makes the liveness case FAIL.
    - `--check-live` finds a stalled ready job in a test fixture and reports nothing when jobs start.
    - Offline unit tests cover the report writer and the live check. The live queue has identical file hashes before and after a self-test run.
  - Out of scope: installing memdoor, its SSH gateway, external model providers, and any schedule. A recurring run needs explicit maintainer consent for that schedule.

## MEASURE553 — Real metrics first, then model improvement

Owner: Maximum-mini-NUIAK. P0. Plan: [MEASURE553](Research/Plans/Measure553.md).
The reviewed pilot now has real-app metrics. Qualification-scale evidence and retention checks remain required.

- [x] **M1 — REAL543-RUNTIME.** Convert audited `visual replay` exports into REAL543 predictions and a `real-app-runtime-v1` receipt.
  `scripts/real_app_runtime553.py` passes 18 tests. The ac85177b receipt binds the shipped tvOS detector and FocusRing digests.
  The 3 retained replays convert. All 3 stay abstentions because of suppression. These are Fixture path checks, not accuracy.
  Benchmark classes must use runtime role names, or the request supplies an explicit `classMap`.
- [ ] **M2 — Promotion gate.** Compare a candidate report with the baseline on the same freeze, with a paired whole-flow bootstrap.
  Pass only with 0 lost successes, 0 new wrong selections, 0 retention losses, an interval lower bound above 0, and the latency limit.
  The gate never sets `modelAccepted`. Implemented in `real_app_runtime553.py gate`; it waits for a real baseline report.
- [ ] **M3 — Real-app pilot.** Qualify apps, plan all capture points, capture in 1 batched session per target, and complete blinded review.
  App decision, 2026-10-31: NewsTV, Swiftfin, and Photo Guessing Game are approved and evaluation-only.
  The 5th app: Moonlight is recommended, with Provenance as the reserve. WeatherFeels needs a Metal toolchain decision.
  The maintainer completes the pilot review. Remaining scope is fresh qualification flows and application coverage. See [app candidates](Research/RealAppApplications543.md).
- [ ] **M4 — REAL550-FOCUS.** Sillycon-TTR supplies a bounded correction for off-screen geometry suppression. Maximum-mini-NUIAK verifies it.
  Requested at coordinator cursors 1814 and 1838. Do not send a duplicate request.
- [ ] **M5 — Detector improvement.** Train on full original data plus reviewed new data. Test 1 YOLO11s fit. Decide only through M2.
- [ ] **M6 — Batched native capture.** Follow [CAPTURE553](Research/Plans/CaptureSession553.md): 3 sessions for 37 blocked records.
  Capability check, 2026-10-31: 7 Session A records are ready on existing Fixture features (B405-104, 027, 052, 053, 054, 056, 007).
  They need 2 tvOS `fixture batch` calls: 1 for Apple TV 4K and 1 for Apple TV at 1080p. B405-106 uses the iOS generator.
  8 Session A records need new Fixture features. The invalid cursor-1840 envelope is corrected at cursor 1845. Forwarding remains unconfirmed.
  B405-240 and B405-241 wait for the Maximum-mini-TTR evidence offload (cursor 887).
  Recipes, 2026-10-31: 14 Apple TV 4K and 4 Apple TV at 1080p recipes, all development groups. See `reports/work/CAPTURE553/session-a-manifest.json`.
  Captured, 2026-10-31: 74 rows, 0 rejected, on a new clean Apple TV 4K Simulator (62DA0048) and the 1080p Simulator (C5E29075).
  All rows pass hash, observed focus, settled, and size checks. Receipt: `reports/work/CAPTURE553/session-a-receipt.json`.
  The tab cases include selected and focused tabs that differ (8 cases at 4K, 3 at 1080p).
  T59 now accepts `fixture-batch-capture-v1` inputs. It checks host-clock capture brackets in place of wall-clock bounds and records `fixture_instance_id` as unavailable.
  6 jobs are registered and approved: `capture553-labels-*` (T59) and `capture553-detect-*` (T56) for 4k-controls, 4k-artwork, and 1080p. Batch: `Research/Experiments/batches/CAPTURE553.json`.
  6 of 58 4K reference frames show an observed focused control. T59 labels them as focused frames, not as no-focus frames.
  Results, 2026-10-31 (development, unreviewed labels): all 6 jobs complete. tvOS v3.0 at 4K matches 17 of 116 `secondaryButton` labels; 73 get class `primaryButton`.
  At 1080p it matches 0 of 40 `secondaryButton` labels (35 wrong class) and 20 of 20 `listRow` labels. At 4K it detects 68 of 112 artwork `collectionItem` labels.
  Check first whether the Fixture `secondaryButton` taxonomy matches the detector classes before treating these as detector misses.
  Three T42 class-agnostic slices are admitted on November 1: capture553-geometry-4k-controls, capture553-geometry-4k-artwork, and capture553-geometry-1080p.
  Review taxonomy versus missing geometry before training. T57 focus comparisons still need their complete fixed inputs.
  Do not use the default `scripts/ingest_fixture_batch.py` split. It assigns train and holdout splits.
  Simulator 9026ECA9 still shows a NewsTV notification alert. It blocks capture there until someone answers it.

## PARALLEL551 — Shared unblockers and independent model campaigns

Owner: Maximum-mini-NUIAK. Implement the approved parallel-model plan. Standard remains first; HCF remains optional.
The following table supplies the existing dashboard. Tasks remain the authority; this table does not admit jobs.

<!-- model-tracks-v1 -->
| Track | Task | Current job prefixes | Question | Qualified inputs | Preparation state | Owner | Next action |
|---|---|---|---|---|---|---|---|
| tvOS detector | REAL543 | detector551- | Which missed controls need geometry or detector correction? | Retained registered-control geometry; incomplete full-screen labels | human review | Maximum-mini-NUIAK and maintainer | Review NewsTV labels; freeze the consumer baseline; prepare coverage, localization, and class reports. |
| Standard focus | REAL550 | standard551- | Do retained fallback gains survive the actual TTR path? | Three retained full-screen replays and frozen reference outputs | implementation | Maximum-mini-NUIAK | Qualify published provenance; compare crops and selection; preserve wrong-selection gates. |
| iOS detector | RETENTION547 | ios551- | Does class preservation retain old detections while learning native rows? | Admitted ROW545 training membership and full retained scorecards | implementation | Maximum-mini-NUIAK | IOS551 loses 15 Run013 detections. Prepare a changed factor after reviewing class and geometry evidence. |
| Optional HCF | QUEUE548 | hcf551- | Can the original fit resume exactly and improve independent observer coverage? | Original trainer and exhausted checkpoint; retained observer parity | implementation | Maximum-mini-NUIAK | Verify restoration with deduplication=False and remaining approved budgets before continuation. |
| Mixed focus | SDK509 | mixed551- | Do verified hard negatives reduce content-sensitive false positives? | Existing crop models and retained negative examples | missing evidence | Sillycon-TTR and Maximum-mini-NUIAK | Obtain independent training-role native products; compile matched crop rehearsal and negative-data arms. |
| Temporal focus | TEMPORAL544 | temporal551- | Does paired information distinguish focus movement from moving content? | Retained movement and unchanged pairs; one related sample group | missing evidence | Sillycon-TTR and Maximum-mini-NUIAK | Qualify independent departure and content-only groups; compare paired, single-frame, and control-local predictions. |
<!-- /model-tracks-v1 -->

- [ ] Qualify exact TTR source and observed Standard replay identities. Preserve unavailable crop identity explicitly.
- [x] Review IOS551-PRESERVE results and confirm the conditional diagnoses match the observed losses.
  IOS551 result, reviewed 2026-10-31: inconclusive against its matched control, contradicted against Run013.
  - The fit completes in 1,123 s. The preservation term runs (540 calls), but its mean penalty is 0.0081 against a loss near 0.93.
  - Against ROW545: 0 gains and 0 losses. Predictions differ, but no matched detection decision changes.
  - Against Run013: 20 gains and 15 losses. Against native-only: 80 gains and 19 losses.
  - The 7 conditional diagnoses correctly stay unselected, because the matched comparison has no loss to diagnose.
  - Decision: reject replacement. A coefficient of 1.0 is too weak to change decisions. Do not repeat it unchanged.
- [ ] Qualify native training-role production after Sillycon-TTR supplies the supported contract.
  Current test-only receipts remain review evidence. Verify 2 real recipes before claiming end-to-end native training.

## REAL550 — Standard consumer measurement

Owner: Maximum-mini-NUIAK. P0. [Verified replay results](Research/Real550ConsumerReplay.md).
Real-app accuracy is not established. Completed replay and activation checks are archived in CompletedTasks.md.

- [ ] **REAL550-PROVENANCE — P0.** Obtain observed source, preprocessing, taxonomy, and crop identities from the actual Standard runtime.
  Sillycon-TTR supplies missing runtime fields through BigDog-Coordinator. Maximum-mini-NUIAK verifies the published source and resulting receipts.
  TTR replies 1823–1829 confirm receipt and scoped ownership. Published source is ac85177b8c9d1185b8d20594e759134f5dc0dbd1.
  The isolated source build and signed package verification pass. The maintainer approves activation on 2026-10-31.
  Maximum-mini-TTR now runs ac85177b. The 3 retained replays pass audit with predictions identical to e8bbdd4a.
  The runtime observes source revision, preprocessing, and taxonomy identities. Crop identity and a selected result remain missing.
  Status is stored at coordinator cursor 1838. Forwarding remains unconfirmed.
  The source adds observed preprocessing and manifest identity. Executed crop identity remains unavailable.
  Record build-supplied base revision separately from clean-tree attestation. Preserve caller declarations as unverified.
  The structured producer and crop-contract request is stored at cursor 1836. Forwarding remains unconfirmed.
  Acceptance: one retained screenshot has reproducible inputs, loaded model hashes, runtime settings, predictions, and a scored result.
  Source-file hash agreement does not replace missing runtime observations. Continue independent label review while this dependency remains open.
- [ ] **REAL550-FOCUS — P1.** Diagnose crop scoring and rejected geometry using the 3 retained Standard replays.
  Compare proposed boxes, crop hashes, scores, and selected controls against matched references.
  Bypassing partial suppression produces 1 wrong selection, 1 correct selection, and 1 abstention. Keep the existing gate.
  Acceptance: a bounded correction preserves previous successes and adds no wrong selections on the declared regression set.
  Queue a correction only after its inputs, comparison, budget, and decision rule pass existing checks.
- [ ] **REAL550-SDK-STATE — P1.** Resolve the disagreement between XCTest foreground state and SDK inactive state in NewsTV.
  Sillycon-TTR supplies the SDK correction. Maximum-mini-NUIAK checks frame alignment and actual focus through the supported consumer route.
  Retain the original receipts. Keep focus unknown until evidence resolves the disagreement.
  Acceptance: app state, scene state, focus identity, and screenshot timing agree, or the report explicitly identifies unavailable evidence.
  Detection annotation review remains independent. REAL543 owns benchmark collection and scoring.

## RETENTION547 — Native row gains with retained iOS detection

Owner: Maximum-mini-NUIAK. P1. [Results and evidence](Research/Retention547Training.md).
Completed frozen, wider, checkpoint, and targeted rehearsal comparisons reject replacement of Run013.

- [ ] **RETENTION547-OBJECTIVE — P1.** Prepare a class-preserving training objective using training-only anchors.
  Diagnose the lost classes and controls from retained predictions before selecting the changed factor.
  Frozen training loses 16 Run013 detections. Wider additive training loses 8; its matched control loses 9.
  Checkpoint selection still loses 8. IOS549 loses 13 Run013 detections and 7 ROW545 detections.
  Define a matched control, exact training membership, evaluation exclusions, fixed epochs, storage, and approved execution budget.
  Keep evaluation images outside training and objective selection.
  Acceptance: full Run013, ROW545, and native-row reports show gains, lost successes, and new false detections separately.
  Reject candidates that fail existing retention gates. Do not repeat the failed configuration merely to occupy the runner.
  Use existing training and comparison templates. Record any missing objective support as a bounded implementation requirement.

## QUEUE548 — Optional continuation

Owner: Maximum-mini-NUIAK. [Completed independent comparisons](Research/Queue548Review.md).
Standard transfer and iOS geometry reviews are complete. Their findings inform REAL550 and RETENTION547.

The continuation and all 17 comparisons complete. Replacement is rejected. See CompletedTasks.md.

## TEMPORAL544 — Remaining temporal extensions

Owner: Maximum-mini-NUIAK. Assigned October 29, 2026.
Use the existing queue. The detached runner owns execution. Preserve REAL543 and PIPELINE538 priorities.
Completed native comparisons and before-frame ablation are archived in CompletedTasks.md.
Results: Research/Temporal544Ablation.md. Content-only negatives and independent departure groups remain required.

- [ ] **TEMPORAL544-DIFF — Extend the existing temporal adapter with a general pixel-difference comparator. P2. Needs adapter.**
  Compare the deterministic rule with retained temporal models on identical settled pairs.
  Define alignment, pixel scaling, comparison regions, and thresholds before scoring evaluation groups.
  Include movement, no-op input, and changed content with unchanged focus. Keep unknown states explicit.
  Use separate development groups to select thresholds. Preserve the existing Settings-specific rule and its supported scope.
  Report false changes, missed changes, abstention, and runtime by condition.
  Prefer the rule only when it recovers errors without losing retained successes. Otherwise retain the model or explicit abstention.
  Acceptance: positive isolated queue execution, malformed and changed-input rejection, group checks, and a second description using the same adapter.
  Owner supplies the qualified variant and exact eligible membership before registration. No extension implementation is assigned in this tranche.

- [ ] **TEMPORAL544-DESTINATION — Score where focus moves. P2. Needs adapter.**
  Extend reporting to score departure identity and arrival identity separately from whether any change occurred.
  Compare actual single-frame selection with paired selection on identical candidate controls and observed endpoint identities.
  Include missing proposals, duplicate labels, no-focus endpoints, and uncertain identity correspondence.
  Report correct destinations, wrong destinations, abstention, and proposal coverage. Preserve control and group identities.
  Accept a paired selector only when it improves destinations without new wrong selections or lost retained successes.
  Owner supplies qualified identity matching, tests, and complete model-input separation before queue admission.

Independent capture and training remain tracked by SDK509-TRAINING-DATA, PIPELINE538-TRAIN, and REAL543-TEMPORAL.
Those tasks supply separate groups, observed action receipts, and content-only negatives before broader qualification.

## REAL543 — Independent real-app accuracy, tvOS Standard first

Owner: Maximum-mini-NUIAK. Protocol: [RealAppValidation543](Research/RealAppValidation543.md).
The report adapter, blinded review export, identity checks, and isolated queue tests are implemented.
Real-app accuracy remains unestablished. Software fixtures do not satisfy benchmark acceptance.

- [ ] **REAL543-RUNTIME — P0.** Connect actual Standard full-screen predictions and observed model identities to the frozen report contract.
  Prove reproducible inputs, loaded hashes, preprocessing, and scored output on one retained screenshot.
  Published source e8bbdd4 builds. Three retained screenshot replays complete with verified export hashes.
  The reusable export audit passes all 3 actual receipts. All 3 results remain partial.
  Missing observed source/preprocessing/taxonomy/crop provenance still blocks baseline qualification.
  Bypassing partial suppression fails the wrong-selection gate. See REAL550.
  Optional HCF receipts do not satisfy this gate.
- [ ] **REAL543-APPS — P1.** Reuse SDK539-APPS. Attach source, content, ancestry, exposure, and SDK qualification receipts.
  Predetermine up to 10 pilot cases per qualified application. Record planned, rejected, missing, and captured cases.
  NewsTV builds, installs, and returns 23 authenticated SDK control rectangles. Cleanup passes.
  NewsTV has 1 captured pilot case and 9 planned cases. Two trials of the same case remain one sample.
  XCTest activation passes. SDK state remains inactive; focus remains unknown. REAL550-SDK-STATE owns this discrepancy.
  Qualify screenshot-to-SDK alignment and controlled content before admitting further cases through existing capture templates.
  Keep the 9 remaining cases predetermined. Record missing and rejected cases instead of silently replacing them.
  TTR receives exact errors and improvement requests; see Research/TTRIntegrationErrors543.md.
  Swiftfin dependencies resolve and its Simulator build passes with approved macros. SDK runtime qualification remains open.
  WeatherFeels needs the missing Apple Metal toolchain. XcodeGen now builds locally.
  Photo Guessing Game builds from pinned source without new dependencies. It adds a distinct game interface.
  Four candidates are identified. Three source builds pass. Zero applications satisfy all benchmark gates.
  SDK539-APPS owns selection of the fifth independent application. Do not count Fixture, NavigationConsumer, or application forks.
  Continue Swiftfin and game integration while WeatherFeels lacks the Apple Metal toolchain.
  Record dependency approval separately before downloading the missing toolchain.
  Game controlled-content mode now builds and passes process-repeatability checks.
  SDK hooks, runtime locale qualification, exposure review, and blinded labels remain open.
  See Research/RealAppApplications543.md for separate gates and next actions.
- [ ] **REAL543-REVIEW — P1.** Export blinded drafts and obtain human review of complete visible controls and focus.
  Start with [the captured NewsTV case](reports/work/REAL550/newstv-blinded-review/index.html).
  The draft contains 23 SDK rectangles. A maintainer or designated reviewer checks all visible controls without model predictions.
  Verify pixel bounds, clipping, occlusion, semantic classes, and controls absent from SDK registration.
  Preserve unknown labels. Report completeness and excluded counts. Unknown focus is not verified no-focus.
  Acceptance: every scored case has reviewed labels. Score false positives only on screens with complete annotations.
- [ ] **REAL543-PILOT — P1.** Queue the 50-screen target through the actual consumer and repair evaluation defects.
  Freeze the protocol, baseline models, preprocessing, thresholds, reviewed labels, and membership before inference.
  Keep SDK reference labels outside model inputs. Run no training, threshold tuning, or model promotion within this benchmark.
  Reuse the existing queue adapter and official COCO cross-check. Preserve the historical custom AP definition separately.
  Report per-class precision and recall, misses, unmatched detections, AP50, AP75, AP50–95, and localization errors.
  Report focus selections, wrong selections, abstentions, unknown references, verified no-focus false selections, latency, and execution failures.
  Show numerators, denominators, class support, and missing coverage. Keep failed inference cases in the case accounting.
  Report smaller qualified scope honestly. Keep iOS preparation independent and HCF outside the Standard headline.
- [ ] **REAL543-QUALIFY — P1.** Freeze 200 additional cases across 5 apps, with 8 flows and 5 capture points each.
  Use 40 additional screens per qualified application. Exclude pilot flows, duplicate images, and related sequences.
  Freeze images, reviewed labels, membership, models, and thresholds before inference. Reject membership drift and cross-partition duplicates.
  Report failures, per-app metrics, and equal-application summaries. Resample whole flows within applications for exploratory uncertainty.
  Describe the selected test population. Five applications do not establish deployment-wide accuracy.
  Score predeclared candidates separately on identical inputs. Report recovered cases, lost successes, and new wrong selections.
  When results guide model changes, classify those cases as development evidence. Reserve fresh cases for subsequent qualification.
- [ ] **REAL543-FOLLOWUP — P1.** Make separate training tasks from confirmed errors ranked by harm, frequency, and application coverage.
  Preserve previous successes. Do not train or promote inside the benchmark.
- [ ] **REAL543-TEMPORAL — P2.** After the static baseline, test movement, dismissal, settling, and changing backgrounds separately.


## SDK539 — Portable consumer integration across 5 independent apps

- [ ] **SDK539-PORTABILITY — Qualify a documented Git-to-SDK integration. P1.** Owner: Maximum-mini-NUIAK; coordinate SDK fixes with Sillycon-TTR through BigDog-Coordinator.
  Goal: a developer builds from a pinned Git revision and obtains useful UI/focus evidence without private machine setup knowledge.
  Preserve PIPELINE538 capture-to-comparison work. Treat the observed workspace mismatch as a portability test case. The approved Developer workspace switch passes project-scoped status and Simulator readiness on October 26.
  Test active-workspace discovery, project-mode selection, artifact destinations, enrollment, and actionable setup errors before navigation.
  Keep workspace selection separate from folder access. Do not silently switch a running consumer or assume source checkout selects its workspace.
  Record setup steps, manual interventions, integration code, build time, first valid packet time, and exact failures.
  Acceptance: a second clean consumer configuration follows the same published instructions without a machine-specific code patch.

- [ ] **SDK539-APPS — Qualify 5 independent open-source tvOS applications. P1.** Owner: Maximum-mini-NUIAK, with Sillycon-TTR for SDK requirements.
  Target is 5 independently verified app integrations, not 5 Fixture layouts or copies of the NavigationConsumer sample.
  Audit the current count from source/build/runtime receipts. Do not assume the sample establishes one independently qualified app.
  Select diverse source-build candidates: media, game, news/reader, utility, and another distinct interaction pattern where viable.
  Verify repository activity, license and assets, tvOS Simulator build support, mockable content, and usable functionality without a proprietary paid dependency.
  Use pinned Git source and controlled content. Do not use App Store binaries or claim candidates are qualified before source builds pass.
  Keep app-code permissions separate from rights to third-party media and training data. Record allowed data use per app.
  For each app, test minimal SDK integration, registration, actual focus, bounds, timeline provenance, capture, export, reopen, and cleanup.
  Exercise focus movement and a supported interruption such as scrolling or dismissal. Mark unsupported scenarios explicitly.
  Reuse one recipe/schema and report format across apps. Record required app hooks and avoid consumer-specific SDK forks.
  Include UIKit and SwiftUI coverage when verified candidates support them. Do not invent app availability to fill categories.
  Compare a second qualified tvOS Simulator device/runtime configuration after the first passes. Physical-device trials require separately named scope and approval.
  Preserve app-specific ancestry across training and evaluation. SDK integration success does not establish model accuracy or training admission.
  Completion: 5 rows with exact revisions, licenses, build receipts, runtime evidence, integration effort, limitations, and pass/fail decisions.
  Prepare bounded queue jobs after each candidate passes prerequisites. Continue independent apps when one dependency blocks.
  This task authorizes investigation and integration planning. Record exact build/install/capture scopes before operations that need additional authority.

## SDK540 — Screenshot versus structured observation benchmark

- [ ] **SDK540-COMPARISON — Measure observation cost and decision quality. P1.** Owner: Maximum-mini-NUIAK; coordinate consumer contracts with Sillycon-TTR.
  Goal: determine whether structured observations reduce data and latency while preserving correct UI decisions and useful diagnoses.
  Reuse the same retained, instrumented routes and matched checkpoints from SDK539. Start with replay; live policy comparison follows separately.
  Compare 3 arms: full screenshot at every step; bounded SDK state/deltas; SDK state/deltas with screenshots on defined uncertainty or visual events.
  Keep a periodic full-state resynchronization in delta-based arms. Report its cost and recovery behavior.
  Use the same task, action budget, consumer/model version, and evaluation cases. Preserve an independent reference oracle unavailable to the evaluated arm.
  Fix initial state, image resolution/compression, requested task, prompt, and decision policy before execution.
  SDK input may contain observed focus and hierarchy. Declare this information advantage; do not describe it as compression of identical information.
  Report information availability and payload efficiency separately. Do not assume a structured representation preserves all visual evidence.
  Measure bytes generated, retained and transmitted; screenshot count; encoding and query latency; consumer latency; and task completion.
  Measure wrong actions, missed controls, stale focus, incorrect settling, missed visual defects, restoration failures, and diagnostic correctness.
  Include scrolling/recycled cells, delayed readiness, dismissal/focus return, background motion, and incomplete SDK registration.
  Negative cases include lost deltas, missing events, stale identities, unknown focus, missing visual styling, and incorrect app declarations.
  Predeclare screenshot fallback rules. Missing required visual evidence must trigger fallback or explicit unknown, not an invented conclusion.
  Report cost per correct decision and successful route, plus error counts and matched differences by app/group.
  Record token counts or billed usage only when available from the actual consumer. Do not infer token savings from byte reductions.
  No external upload or paid model call is authorized by this task. Use local retained evidence first; scope external evaluation separately if needed.
  Acceptance thresholds and permitted regressions must be fixed before evaluation; never trade unreported reliability losses for lower payload size.
  A replay establishes observation/decision quality on fixed inputs. Only a later closed-loop trial establishes navigation success under each policy.
  Deliver a comparison report and a supported observation policy, or retain full screenshots if the reduced-data arms lose required information.
  No efficiency or reliability improvement is claimed before measurement. This is a task definition, not an admitted benchmark job.

### SDK540 execution sequence

Record baseline costs during collection and navigation-map work. Run the full matched benchmark after those collection improvements stabilize.

- [ ] **SDK540-01 — Freeze the matched benchmark inputs. P1.** Owner: Maximum-mini-NUIAK. Inventory qualified retained routes before requesting captures.
  Select cases with complete screenshots, SDK observations, action receipts, and independent expected outcomes. Record missing coverage by scenario.
  Freeze app/group membership, consumer version, screenshot encoding, decision questions, fallback rules, budgets, and acceptance thresholds.
  Deliver a pinned manifest and 3 observation configurations. Do not require all 5 SDK539 apps before a clearly scoped pilot.
- [ ] **SDK540-02 — Queue matched observation replays. P1.** Owner: Maximum-mini-NUIAK. Depends on SDK540-01.
  Use existing templates where supported. If one adapter is missing, name its exact input/output contract and qualify it once.
  Produce comparable full-image, structured-state, and hybrid reports from the same retained checkpoints.
  Measure generation, storage, transmission, and consumer costs separately. Mark unmeasured costs unavailable.
  Include negative cases and resynchronization overhead. Prove a second app/configuration uses the same adapter without a new script.
- [ ] **SDK540-03 — Publish the efficiency and reliability decision. P1.** Owner: Maximum-mini-NUIAK. Depends on SDK540-02.
  Show matched bytes and latency per step, screenshot frequency, correct decisions, missed defects, and cost per successful evaluated task.
  State what information each arm receives. Separate reduced payload from SDK-only information gains.
  Recommend full-image, structured, or hybrid use per task type. Reject a lower-cost policy that fails the fixed reliability gate.
  Define a bounded live-route follow-up only after replay passes. Do not report replay success as closed-loop navigation success.

## MODEL536 — Promotion paths across all models

Use [the model promotion plan](Research/ModelPromotion536.md) for dependencies, existing adapters, acceptance, and stop rules.
IOS534 and row535 complete. Both quarantine candidates fail retention. ROW537 recovers one text label but detects no row bodies. Qualify corrected row training groups next.
Prioritize TVOS515 consumer parity alongside native profile acquisition.
Keep independent model streams separate. Do not duplicate existing fits or describe missing-input branches as ready.

### Immediate work classification — October 25, 2026

This table references existing tasks. It does not create duplicate jobs or replace earlier P0 commitments.
All 4 workstreams retain P1 priority. Order describes selection within this tranche.

| Order | Existing task | Work type | Readiness | Completion evidence |
|---|---|---|---|---|
| 1 | TVOS515-CONSUMER | Consumer integration and qualification | Implementation needed; retained reference results exist | Exact TTR model and crop parity preserves 15 gains, prior successes, and no-focus outcomes; report full-path latency |
| 2 | SDK530-PRODUCER, then GRAPH531-APPLY | Shared producer integration | Git source and 21 offline checks pass; live session entry, restoration, and training-role contract remain open | One queued bounded pair completes acquisition, verification, and cleanup; independent training products retain explicit role checks |
| 3 | ROW537 | Independent experiment review | Both retained comparisons complete; neither candidate is promotable | Compare 18 visible row/text pairs against Run013; name gains and losses; select or reject one corrected-membership training hypothesis |
| 4 | SDK509-TRAINING-DATA, then SDK510-MATCHED-TRAINING | Conditional data qualification and model experiment | Depends on independent eligible native groups; not executable training yet | Recover departure without background-only false changes or lost retained successes; compare against single-frame and temporal baselines |

Maximum-mini-NUIAK owns integration and local comparisons. Sillycon-TTR supplies missing producer contract information through BigDog-Coordinator.
Work on items 1 and 2 independently. Item 3 does not depend on TTR.
Prepare item 4 alongside producer integration, but do not relabel review-only pairs for training.
Retain submitted budgets and immutable specifications. Define exact membership and budgets before admitting additional jobs.

## WORKFLOW533 — Result-driven independent comparisons

- [ ] **FOCUS541 — Diagnose retained TTR focus failures. P1.** Owner: Maximum-mini-NUIAK. Receive 5 named generic feedback archives from Sillycon-TTR through the approved transfer flow. The shared volume is currently unmounted. Check exact model identity, source-image and crop hashes, 16% expansion, 256-pixel resizing, pixel metadata, probability output, and proposal coverage. Reuse recorded outputs before inference. Acceptance: case-linked cause or exact unresolved boundary, matched prior-success checks, and one justified next correction. Preserve all exposed-data exclusions. No model promotion or new training is implied. See [review](Research/NightlyReview20261029.md).

- [ ] **PIPELINE538-TRAIN — Admit independent native training groups. P1.** Owner: Maximum-mini-NUIAK. Capture repair and automatic review now pass for unchanged focus and actual movement through one adapter. Current producer output remains test-only. Obtain the documented training/development contract, preserve evaluation ancestry, and connect eligible groups to existing matched training batches. Do not relabel the reviewed pairs. See [UNBLOCK542](Research/Unblock542NativeAndRows.md).
- [ ] **UNBLOCK534-ROW — Measure actual RTLMirror row bounds. P1.** Owner: Maximum-mini-NUIAK. The current label and row annotations measure the same Text view. Use native row geometry for new captures. The native correction passes 3 XCTest cases and all 22 captured containment checks. Four offscreen pairs and 2 button-bound failures prevent full-family training admission. Review partial row diagnostics before corrected training membership. Preserve existing images and benchmarks. See [REVIEW535](Research/Review535RowsAndQueue.md). ROW542 confirms that confidence 0.05 still detects 0/18 row bodies. Stop threshold tuning for this gap. Prepare complete training-only native row annotations. See [UNBLOCK542](Research/Unblock542NativeAndRows.md).

## GRAPH531 — Resilient decision graphs

See [recovery behavior and activation contract](Research/Graph531Resilience.md).

- [ ] **GRAPH531-APPLY — Use recovery in the native producer graph. P1.** Owner: Maximum-mini-NUIAK. Connect the missing profile producer, evidence qualification, eligible crop preparation, training, and retained comparisons. Define exact recovery and inconclusive branches. Do not claim this graph is executable before producer inputs exist.

## SDK530 — Native training producer and matched iOS correction

See [verified findings and admitted graph](Research/SDK530NativeLabelsAndIOS.md).

- [ ] **SDK530-PRODUCER — Connect observed profiles to eligible native groups. P1.** Owner: Maximum-mini-NUIAK. Use TTR's collector and continuity verifier. Reply 1513 confirms test-only output and supplies session entry/cleanup. The training contract is sent through BigDog-Coordinator at cursor 1514; Sillycon-TTR acknowledges the contract at cursor 1517, but implementation and consumer admission remain open. Message 1509 delivers source 337b6f7 and collect-focus-pair. All 21 offline checks pass. The approved Developer workspace selection passes status, configuration status, and Simulator readiness. Connect owned-session entry and restoration to the queue using explicit project scope. The producer currently requires test roles; resolve independent training/development support before admission. Produce independent training/development groups with observed focus, bounds, and exact source identities. Preserve existing review exclusions. Do not require detector roles for binary focus. Prepare concrete capture and launch scope before any additional required consent.

## SDK529 — Native UI and timeline adoption

See [capability audit, contracts, and acceptance checks](Research/SDK529CapabilityAdoption.md).

The corrected removal/restoration sequence passes native focus and image alignment.
Frozen crop models still miss the focused scene. Supplemental resolution adds no focus gains.
The matched iOS recipe loses retained detections. Geometry review identifies competing labels and missing coverage.
See [verified findings and next decisions](Research/SDK529FocusStateStrategy.md).

- [ ] **SDK529-ROLES — Review native sample semantics. P1.** Owner: Maximum-mini-NUIAK. Provide evidence-backed detector roles for left and right, or keep them unmapped. Native UIButton class alone does not distinguish primary and secondary controls. Acceptance: pinned mapping evidence and deterministic unknown-role rejection.

- [ ] **SDK529-02 — Qualify native class and geometry annotations. P1.** Owner: Maximum-mini-NUIAK. Use reviewed mappings, measured transforms, and product-specific completeness. Release eligible independent model streams.
- [ ] **SDK529-03 — Extend pair intake to episodes. P1.** Owner: Maximum-mini-NUIAK. Preserve event references, timing, lifecycle, playback, and history gaps. Keep episode ancestry separate across splits.
- [ ] **SDK529-04 — Qualify timeline alignment and capture settling. P1.** Owner: Maximum-mini-NUIAK. Coordinate missing SDK events with Sillycon-TTR through BigDog-Coordinator.
  Goal: produce correctly timed screenshots for focus training and distinguish focus changes from animation or background movement.
  Start with one controlled directional action. Record input delivery, observed focus, geometry changes, available callback starts/completions, and screenshot intervals.
  Inventory actual SDK events first. Mark unavailable callback completion evidence explicitly; do not infer completion from a callback name.
  Compare fixed-delay capture against observed focus and geometry stability on the same scenario definitions.
  Extend the comparison separately to focused-control removal/restoration, modal dismissal/focus return, and unchanged focus with moving content.
  Use stable control IDs, app/run identity, event sequence, source revision, group ancestry, and explicit clock uncertainty.
  Reuse sdk_episode529 and existing capture/comparison templates. Add only a required missing connection after identifying its contract.
  Report frame alignment, premature captures, unknown states, missed transitions, acquisition latency, and retained-result regressions.
  Acceptance: each reviewed frame has supported before/transition/settled evidence or an explicit unknown result.
  A settled label needs a declared observation window and evidence for the relevant control region; stable geometry alone is insufficient.
  Callback completion does not prove pixel settling. Moving background content must not automatically prevent control-region settling.
  Preserve transient frames for temporal analysis. Admit static training crops only after their own alignment and label checks pass.
  Negative checks cover missing events, conflicting clocks, stale run identity, focus changes during capture, and absent completion signals.
  Correlate inputs only through explicit identifiers or declared uncertainty. Timestamp proximity alone does not prove causality.
  Dependencies: qualified producer/session cleanup for new captures; retained episode analysis can proceed independently.
  Define exact frame/input counts, observation windows, and approved time/storage budgets before queue admission.
  Do not change data roles, infer no-focus from disabled controls, or promote a model from this timing test.
  Completion: a queued comparison publishes a report that selects a supported capture policy or names the exact missing SDK evidence.
  This entry defines work. It does not claim a new capture job is admitted or running.
  Test matrix for UIKit and SwiftUI:
  - Registration: UIKit registration records measured identity, parent, bounds, and visibility. SwiftUI appearance registers; description changes update; disappearance unregisters.
  - Identity reuse: remove and recreate a control. Require generation-aware identity or an explicit unresolved identity result; reject stale updates.
  - Focus: UIKit records actual didUpdateFocus callbacks separately from shouldUpdateFocus decisions. SwiftUI records binding changes with their own provenance.
  - Rejected focus: deny a requested focus change. Require a rejected decision without a fabricated actual-focus change.
  - Lifecycle: instrument appearance, disappearance, loading, and ready where supported. Missing instrumentation yields unavailable, not an inferred event.
  - Gesture: exercise began, changed, ended, cancelled, and failed paths through supported hooks. Preserve input identity and handler outcome independently.
  - Callback completion: compare a synchronous handler with delayed UI work. Handler return must not imply animation or asynchronous completion.
  - Layout: change bounds and scroll offsets. Require fresh measured revisions; reject stale revisions. A revision alone must not mark pixels settled.
  - Dismissal: close a controlled overlay or player. Observe destination registration, actual focus return, geometry, and capture timing without imposing an unsupported callback order.
  - Moving content: change background pixels with fixed focused-control geometry. Distinguish background motion from focus movement and control settling.
  - Clock and history: inject missing events, excessive clock uncertainty, and app-run changes. Mark affected temporal labels unknown and preserve usable static evidence.
  Compare equivalent UIKit and SwiftUI scenarios using the same supported action, content, capture budget, and control-region measurement.
  Do not require identical callback sequences across frameworks. Test observable outcomes and evidence coverage instead.
  Each report names framework, scenario, action/control IDs, app/run identity, source revision, event provenance, event time, capture interval, and clock uncertainty.
  Report expected versus observed events, missing hooks, handler outcomes, actual focus, geometry changes, and before/transition/settled/unknown classification.
  Compare fixed delay and event-plus-stability strategies on premature captures, valid aligned frames, wait time, timeouts, and retained successes.
  Predeclare the stability window, control-region pixel criterion, timing uncertainty bound, and passing thresholds before execution.
  Verify negative cases reject unsupported claims while keeping unrelated ready experiments executable.
  Deliver automated positive and negative checks, one bounded UIKit/SwiftUI comparison report, and a case-linked capture-policy decision.
  If an SDK hook is missing, record its exact API/event requirement and affected scenario for Sillycon-TTR; continue supported cases.
  These are acceptance tests to implement and run. No new test pass is claimed by this task update.
- [ ] **SDK529-05 — Test auto-hide, dismissal, and focus return. P1.** Owner: Maximum-mini-NUIAK. Use controlled scenes and explicit destinations. Measure stale selections, temporary no-focus, and reacquisition.
- [ ] **SDK529-06 — Select diverse episode failures. P2.** Owner: Maximum-mini-NUIAK. Compare equal-budget diverse and random selection. Preserve previous successes and independent evaluation groups.

## SDK528 — Independent retained resolution

See [approved experiment and current boundaries](Research/SDK528IndependentResolution.md).

- [ ] **SDK528-RESOLUTION — Review 960 versus 1280 geometry. Priority P1.** Owner: Maximum-mini-NUIAK. Eight approved group jobs retain every baseline success. The aggregate reports gains and losses. Require full focus regression before any runtime correction. Stop if no useful control recovery appears.

## UNBLOCK527 — Matched training and SDK producer

See [results and admitted work](Research/Unblock527Results.md).

- [ ] **IOS527 — Review matched bias-warmup correction. Priority P1.** Owner: Maximum-mini-NUIAK. Both approved graphs preserve membership and prior successes. The runner executes 2 fits, matched scoring, retention reports, and conditional diagnoses. Reject any retained losses. Do not promote from trainer metrics.
- [ ] **SDK527 — Verify source-built packet acquisition. Priority P1.** Owner: Maximum-mini-NUIAK. Successor sdk527-native-packet-r3 uses the verified TTR candidate. Preserve failed attempts. Check observed profile and group membership before training admission. Refresh expired enrollment only through the supported setup path.

## NIGHTLY525 — Unblock useful training and correct readiness

See [nightly findings and exact next actions](Research/NightlyReview20261025.md).

- [ ] **FRICTION526-CAPTURE — Qualify the supported SDK producer. Priority P1.** Owner: Maximum-mini-NUIAK. New and repeated bounded Simulator captures are authorized. Start with 1 layout, at most 2 frames, 800 s, and 100 MB. Connect current enrollment, observed focus, frame bounds, and profile evidence. Use action timing only for temporal products. Preserve original roles and exclusions. Coordinator message 1464 requests the supported source entrypoint from Sillycon-TTR. Do not launch a remote duplicate. Acceptance: one verified packet releases crop preparation through the runner. See [audit](Research/Friction526Audit.md).
- [ ] **FRICTION526-CONTRACT — Remove campaign-name coupling from capture validation. Priority P1.** Owner: Maximum-mini-NUIAK. The v2 session contract removes successor-ID allowlists and passes 76 tests. Generalize remaining SDK/profile production only after the producer exists. Preserve exact job approvals, dependencies, target ownership, budgets, and immutable receipts. Support Standard-only production without requiring optional HCF. Prove two campaigns use configuration only. Activate central validator changes only at a qualified idle boundary. See [audit](Research/Friction526Audit.md).

- [ ] **NIGHTLY525-READINESS — Reconcile historical readiness and summary rows. Priority P1.** Owner: Maximum-mini-NUIAK. Six completed successors are now linked, including tvos511-size-decision. No inference repeats. Diagnose the 59.11 s snapshot cost. Preserve runner ownership and active work.

## STREAM518 — Longer matched training and retained SDK review

See [verified findings and admitted training](Research/Stream518MatchedTraining.md).


## STREAM517 — Retained recovery and confidence diagnosis

See [verified results and active graphs](Research/Stream517RecoveryAndConfidence.md).


## STREAM516 — Parallel capture, SDK, and iOS progress

See [verified progress and activation boundary](Research/Stream516ParallelProgress.md).


## STREAM515 — Consumer parity and independent iOS comparison

See [verified Standard gain and executable graph](Research/Stream515Qualification.md).

- [ ] **TVOS515-CONSUMER — Qualify the exact resolution fallback through TTR. Priority P1.**
  Owners: Maximum-mini-NUIAK and Sillycon-TTR. Standard gains 15 selections without losses or new wrong selections in retained development.
  The current observer uses different models. Require pinned exports, crop parity, selected-resolution receipts, prior-success checks, and measured latency.
  Coordinator message 1403 requests the supported interface. Preserve Standard and disable navigation.
## SDK513 — Qualified preparation and producer requirements

See [implementation and evidence](Research/SDK513Preparation.md).

- [ ] **SDK513-PRODUCER — Qualify independent training groups through the reusable adapters. Priority P1.**
  Owners: Sillycon-TTR for producer data; Maximum-mini-NUIAK for intake and matched comparisons.
  Require observed profiles, matching-host freshness, independent layouts, and exact exclusions.
  Cross supported transitions with layouts. Source revision 630969a4 passes the portable construction check. Observed focus profiles remain missing.
  Request 1407 records the group-scope review. Full 48-pair capture approval remains separate.
  Bind eligible crops to T06. Queue temporal comparisons separately when their prerequisites pass.

## STREAM512 — Regression qualification and additive rehearsal

See [findings and executable graphs](Research/Stream512Followups.md).

- [ ] **SDK512 — Qualify committed intake and registered-control training scope. Priority P1.**
  Owner: Maximum-mini-NUIAK with Sillycon-TTR. Source commit eb7397d9 is fetched. SDK513 qualifies pair verification and preparation. The standalone audit passes after source repair f8cdd641.
  Require matching-host freshness and independent training groups. Complete screen labels do not block qualified control-crop training.
  Request 1393 specifies 6 training and 2 development groups as a pilot. Existing capture budgets remain unchanged.


## STREAM511 — Independent model investigations

See [graphs, decisions, and data requirements](Research/Stream511IndependentExperiments.md).

- [ ] **STREAM511-DATA — Qualify a shared SDK corpus for separate model streams. Priority P1. Owner: Maximum-mini-NUIAK with Sillycon-TTR.**
  Coordinator request 1387 consolidates existing requests. Do not duplicate producer work.
  Require committed source, separate training ancestry, observed focus, explicit profiles, complete class coverage and exclusions.
  Prioritize visible no-focus controls, selected-but-unfocused controls, and background changes with unchanged focus.
  This unblocks Standard crop, optional HCF, temporal focus, and eligible detector training independently.
  The existing SDK505 test group remains excluded. Geometry stability does not prove pixel settling.


## SDK508 — Corrections from native comparisons

See [completed comparisons and decisions](Research/SDK508Results.md).

- [ ] **SDK509-TRAINING-DATA — Qualify separate native focus groups. Priority P1. Owner: Maximum-mini-NUIAK with Sillycon-TTR.**
  SDK509 rejects wider-context and aspect-preserving crops as native repairs. Both models still need representative native button evidence.
  Request existing supported recipes, explicit visual profile, observed focus appearance, and separate training groups.
  Preserve the SDK505 test group and all evaluation exclusions. Admit training only after provenance, geometry, labels, and group checks pass.
  Requirement message 1370 is stored through BigDog-Coordinator. Forwarding and producer acceptance remain unconfirmed.
- [ ] **SDK510-MATCHED-TRAINING — Compare appearance and background preservation. Priority P1. Owner: Maximum-mini-NUIAK.**
  SDK509 shows color-sensitive departure and background-only confusion. Use separate approved training groups once SDK509-TRAINING-DATA passes.
  Keep matched initialization, membership, epochs, and original-data rehearsal. Change only the supported training intervention.
  Predeclare departure recovery, no-focus false selections, and zero lost retained successes. Queue complete comparisons with each fit.
  Check existing training adapters first. If absence labels need an extension, qualify it before admission.
  Do not train on the inspected SDK505 group or add unverified labels.
- [ ] **SDK508-DEPARTURE — Correct missed focus departure. Priority P1. Owner: Maximum-mini-NUIAK.**
  The temporal baseline and both candidates miss pair-5. Preserve the 5 correct pairs and earlier retained successes.
  Compare a justified correction against both sets. Do not count temporal change as destination selection.
  SDK509 rejects symmetric maximum and grayscale scoring. Grayscale recovers departure but introduces a false background-change result for all 3 models.
  Seed-44 grayscale also loses 39 retained successes. Keep preprocessing unchanged; the next correction requires matched training data.
  See [SDK509 scope and results](Research/SDK509CorrectionTranche.md).

## SDK506 — Follow-ups from retained evidence

See [verified results and limits](Research/SDK506Results.md).

- [ ] **SDK506-UNION — Compare combined proposals. Priority P1. Owner: Maximum-mini-NUIAK.**
  Scoped coverage is 7/8; general coverage is 6/8. Their union covers 8/8 registered boxes in 2 related SDK frames.
  Score combined proposals against retained successes and negatives before any policy change. Incomplete inventory prevents precision claims.
  SDK508 rejects the frozen HCF fallback union after a new false selection. Mixed union preserves 4 no-focus endpoints but recovers no focus.
  Defer broader union work until the known-box crop failures have a supported correction.
- [ ] **SDK506-COMPATIBILITY — Restore the pinned helper path. Priority P1. Owner: Maximum-mini-NUIAK with Sillycon-TTR.**
  Running and pinned builds differ in sandbox entitlements. Exact executable hashes are sent at cursor 1358.
  Qualify the matching runtime without changing retained campaign identities or repeating completed captures.
  Supported preflight confirms the pinned application is not running. The running Developer Tool application passes its own preflight.
  Do not infer a sandbox defect or silently switch applications.

Both temporal candidates classify 4/4 retained pairs correctly versus 2/4 with the before frame removed.
Keep calibration roles unchanged. Independent moving-background and no-focus evidence remains required.

## SDK505 — Native evidence tranche

See [scope, bounded cases, and acceptance checks](Research/SDK505Tranche.md).

- [ ] **SDK505-TRANSITIONS — Qualify action-linked pairs. Priority P1. Owner: Maximum-mini-NUIAK with TTR producer.**
  Cover arrival, departure, movement, unchanged focus, and content-only movement. Preserve delivered action and ordered packet evidence.
  SDK507 verifies 6 action-linked pairs. Content motion remains unverified; do not label that case as qualified moving-background truth.
  SDK509 verifies changed background pixels with unchanged focus. This does not establish continuous motion.
- [ ] **SDK505-LABELS — Qualify detector inventory and taxonomy. Priority P1. Owner: Maximum-mini-NUIAK with TTR producer.**
  Corpus audit is implemented and approved. Require explicit coverage/exclusions and reviewed class mappings before training admission.
- [ ] **SDK505-REPAIR — Qualify committed pending-layout repair. Priority P1. Owner: Maximum-mini-NUIAK.**
  TTR reports successful trials but uncommitted source. Obtain a committed revision and scoped regression receipts before local qualification.

The native SDK delivery is received, verified, and scored. Its shared copy is removed by TTR after the exact receipt.
The approved TTR launch restores readiness through the app's own helper. Separate training recipes still need confirmation.
The 3 unattempted session jobs use an older pinned helper that still refuses the connection. Their approvals fail before dispatch.
The combined report is approved but waits on those sessions. Preserve specifications and completed capture evidence.

## SDK501 — Use observed UI evidence

See [implemented adapter, requests, and producer requirements](Research/SDKEvidence501.md).

The 2 SDK501 audits complete and verify. They expose 68 measured body observations and 4 transitions from retained calibration captures.
Missing annotation completeness, condition tags, and no-focus evidence remain explicit requirements.
- [ ] **SDK501-PRODUCER — Qualify equivalent portable SDK output. Priority P1. Owner: Maximum-mini-NUIAK.**
  SDK502 verifies the packet schema in committed local revision cf17ed0e. A tested review-only consumer now exists.
  SDK503 verifies unchanged packet schema in the isolated Developer checkout at ae310e08.
  The request compiler passes 2 configuration-only queue cases and rejects a wrong app. Ten focused tests pass.
  Request 1334 asks Sillycon-TTR for existing native packets, exact provenance, hashes, and original roles through BigDog-Coordinator.
  SDK504 receives and verifies 2 retained native focused packets. Both queue checks complete and their output hashes verify.
  Observed no-focus, navigation transitions, and complete detector labels remain missing. Preserve requested test roles and single-frame semantics.
  Exact transfer receipt 1340 is stored. TTR cleanup acknowledgment remains pending. Do not repeat captures to qualify the importer.
  Prepare one geometry request and one transition request through the existing campaign interface.
  Acceptance: frame-bound observed labels, explicit exclusions, preserved ancestry, and configuration-only reuse.
  New capture scope and missing TTR implementation remain separate requirements. Do not change Maximum-mini-TTR source here.
  See [SDK packet contract, passing software checks, and exact remaining dependency](Research/SDKPacket502.md).

## Current tranche — MATCHED499 detector and focus repairs

See [review, decisions, qualification, and repair branches](Research/Matched499DetectorAndFocus.md).
The completed fit results reject the frozen and teacher candidates. Standard retention remains required.
Detector training is qualified for the tested T89 path. All 36 focused qualification tests pass.

- [ ] **IOS500 — Repair localization retention. Priority P1. Owner: Maximum-mini-NUIAK.**
  Mixed freezing gains 13 detections and loses 32 across 2,030 related labeled occurrences under class-agnostic matching.
  STREAM511 qualifies retained training-only labels and queues a coverage-selection correction with complete comparisons.
  Broader SDK training still requires separate eligible groups and complete class coverage. Preserve evaluation exclusions.
- [ ] **MATCHED499-TRAINING — Admit only a justified matched repair. Priority P1. Owner: Maximum-mini-NUIAK.**
  The training adapter is qualified. Exact repair selection waits for the geometry and class comparison.
  General tvOS training also needs complete training-only labels beyond the scoped focusable-control annotations.
  Preserve development exclusions. Record membership, initialization, changed factor, fixed epochs, and retained comparison jobs before admission.
- [ ] **IMPORT500-TTR — Restore readiness and release remaining sessions. Priority P0. Owner: Maximum-mini-NUIAK.**
  The import correction passes 41 tests and an isolated import of 8 retained images. The approved dashboard restart passes.
  The retained import successor is approved. Three unattempted session successors and the report are registered.
  Capture approvals remain withheld: Maximum-mini-TTR refuses its app-managed endpoint through both checked helpers.
  Verify the active workspace and readiness without switching workspaces or repeating captures. Then approve exact successors within existing budgets.
  Keep the background runner available for independent jobs. Preserve the failed original session.

The completed 26 jobs answer 3 questions. See [model status and next priorities](Research/ModelStatus500.md).
The detached runner owns the new comparisons. Cached geometry work is short and does not fill an overnight window.

## Current implementation — FIXTURE498 and COVERAGE498

October 24 review supersedes the admission snapshots below.
Recovery completes. Session 1 then fails on artwork metadata compatibility; MATCHED499-IMPORT owns that repair.
COVERAGE498 recovers 14 iOS labels and 6 tvOS labels without losing previous class-correct detections.
Incomplete annotations prevent precision claims. MATCHED499 owns the next comparisons.

See [qualification, experiment questions, and limits](Research/Fixture498RecoveryAndCoverage.md).

FIXTURE498 recovery completes. IMPORT500-TTR owns the remaining runtime gate.
The completed COVERAGE498 review is archived in CompletedTasks.md. MATCHED499 owns its follow-up comparisons.

## Current review — PROPOSAL497 and Fixture connection

Nightly update: all 8 comparisons complete with verified outputs. Standard detector boxes cover only 6 of 40 focused observations.
The summary used the wrong output filename. Approved successor `proposal497-native-report-r2` reuses the completed evidence.
See [the dated review](Research/NightlyReview20261024.md). Earlier admission snapshots below are historical.

FIXTURE497-SETUP launch and recovery evidence are complete. The current endpoint failure is tracked separately above.
- [ ] **PROPOSAL497-LABELS — Qualify training annotations for missed Standard controls. Priority P1. Owner: Maximum-mini-NUIAK.**
  Reuse existing detector and label templates. Separate missing boxes from class errors using the completed matched reports.
  Use training-only groups. Do not turn these development observations into training labels.
  Acceptance: observed bounds, class completeness, preserved evaluation exclusions, and a matched detector comparison with previous-success checks.
  Existing local training authority applies within recorded budgets. Missing labels remain a producer requirement, not guessed values.

- [ ] **PROPOSAL497 — Review matched teacher scores on retained general-detector boxes.**
  Eight T57 comparisons and one T58 native-control report are registered and approved.
  The runner completes the button comparison. Seven comparisons remain pending at the admission snapshot.
  The report waits for its producers. This is a dependency, not a failed prerequisite.
  Reuse resolution454 proposals and completed TEACHER495 and TEACHER496 models. Do not repeat captures or training.
  Separate missing proposals, scoring failures, gains, lost successes, and no-focus outcomes by profile.
  Both models remain rejected for Standard consumer regressions. Do not promote from this diagnostic.
  This is a short diagnostic batch, not an overnight workload.
- [ ] **ADRSPIKES493-CONNECTION — Qualify the bounded Fixture connection repair.**
  Supported caller export succeeds. All 9 files and 26,143 bytes verify without recapture or restart.
  The retained report has 2 failed cases, 6 unattempted cases, and no accepted image pairs.
  The next case fails with `serviceUnavailable` and `urlError:-1004`. Sillycon-TTR receives the exact failure through BigDog-Coordinator.
  Preserve failed evidence. Require supported connection recovery and valid images before releasing the 4 comparisons.
  Opening the existing source-built Maximum-mini-TTR app restores coordinator readiness. Simulator ownership is clear.
  TTR reply 1302 supplies the launch path. The bound Fixture endpoint now settles with measured controls.
  FIXTURE498 tracks the tested recovery successor. The original failed records remain unchanged.

See [verified teacher results and TTR reply](Research/Teacher495Results.md).

## Current implementation — TEACHER495 preservation and training anchors

Owner: Maximum-mini-NUIAK. Updated October 23, 2026.
The active T06 extension adds a fixed teacher penalty without changing default training or batch membership.
The new T93 adapter selects exact training-only anchors from retained source membership.
Twenty-three focused tests pass, including actual trainer execution on CPU and positive and negative isolated queue paths.
Two anchor descriptions reuse the same adapter. Teacher weights and buffers remain fixed in the qualification tests.

Activation is complete after explicit maintainer approval. All 23 focused tests pass on the active sources.
Seven eligible approvals receive exact source checks. The same runner resumes without cancellation.
TEACHER495 comparison is complete and rejected for 6 lost Standard consumer negatives. See the current review above.
  Admitted and approved: 36 jobs across the training graph and reused Standard retention graph.
  This is 1 fit, 17 scoring conditions, comparisons, terminal decisions, and bounded reporting branches.
  A second request reuses candidate scores for Standard retention. It needs no new script or inference.
  The teacher fit uses 7,200 training rows and 5,400 source-verified anchors across 148 groups.
  Keep 30 epochs, 1,800 s, 2 GiB, and all previous-success gates. Do not resume this variant without restoration qualification.

`teacher495-training-anchors` is registered and approved independently. The runner owns its execution.
Both graphs are admitted. See [qualification and runtime requirements](Research/TeacherPreservation495.md).

## Current tranche — RESERVE494 independent retention comparisons

Owner: Maximum-mini-NUIAK. Updated October 23, 2026.
Readiness recheck: retained recovery is pending with intact approval and no incomplete recorded dependencies.
The runner is healthy and executes `native494-frozen-train`. Do not interrupt this fit to dispatch recovery.
The 4 session comparisons remain dependent on verified recovery cleanup, not on another export request.
IOS493 matched reporting still waits for its comparison producers. IOS494 original-only training is pending with intact approval.
No new fits are admitted during this recheck. Overnight coverage remains unmet.
FREEZE493 completes and rejects replacement. Standard known-box scoring loses 11 successes and adds 2 wrong selections across 72 observations.
IOS493 gains 14 detections and loses 32 against Run013. Its full-training matched report remains pending.
Preserve current models. These are development results, not release qualification.

The completed RESERVE494-RESULTS review is archived in CompletedTasks.md. Both candidates fail retention.

Recovery and the 4 approved session comparisons remain unstarted at this check. Their existing cleanup dependency remains strict.
No captures repeat. See [current findings](Research/ADR493SourceExportQualification.md#latest-retained-comparisons-and-2-independent-training-questions).

## Current tranche — verified export and IOS493 frozen backbone

Owner: Maximum-mini-NUIAK. Updated October 23, 2026.
TTR source `c6742694` passes signed build, exact-process preflight, and retained recovery export.
Exported sizes and hashes verify. The missing marker remains absent. No captures or Simulator restarts repeat.
Sillycon-TTR acknowledges the verified export through BigDog-Coordinator at cursor 1255.
The admission update activates after the current fit finishes. No running attempt is cancelled.
Recovery, 4 r3 session comparisons, and their report receive exact approval. Original r2 specifications remain preserved.
- [ ] **ADRSPIKES493-RESULTS — Review retained recovery and session comparisons.**
  Require verified cleanup before the 4 comparisons execute.
  Preserve the failed case. Resume only the 7 unattempted cases within the original remaining budget.
  Compare observed labels and setup time across separate, reused, reused, and separate sessions.
  Do not repeat captures after an export failure. The detached runner owns execution.

IOS493 qualifies the real YOLO11 backbone freeze path. Twenty focused tests pass.
The 30-epoch fit completes in 689.54 s with 128 verified training images.
All 300 frozen tensors remain unchanged across 31 checks. This verifies training behavior, not model accuracy.
The idle update rechecks 32 unstarted Standard and iOS approvals without changing their specifications.
Runner 51554 resumes approved execution with Standard comparisons first.
The graph compares all 6 retained iOS conditions against Run013 and the completed full-training control.
FREEZE493 Standard training completes in 527.31 s. Partial known-box results lose 7 successes and add 2 wrong selections.
Reject Standard replacement. Finish the pending reports without another fit.
Preserve shipped models and the optional observer. These graphs do not constitute an overnight reserve.
See [verified results and active admission](Research/ADR493SourceExportQualification.md#latest-recovery-admission-active-and-ios-frozen-fit-complete).

## Current tranche — retained export and Standard frozen features

Owner: Maximum-mini-NUIAK. Updated October 23, 2026.
TTR source `55054bcd` builds and passes exact-process preflight. Export fails at `caller_destination_write`, Cocoa code `513`.
BigDog-Coordinator stores the finding for Sillycon-TTR at cursor 1246. No captures repeat. The 4 session comparisons remain gated.
FLOW478-07 now has a real T06 encoder-freeze option, including fixed BatchNorm buffers and per-epoch integrity checks.
The focused suite passes 37 tests. All 28 FREEZE493 jobs receive exact approval.
Runner 66290 starts `freeze493-standard-train`. The graph retains 25 dependent jobs and 2 conditional decision branches.
The full Swift test run is incomplete after more than 3 min without progress. Swift compilation passes.
Use [the current evidence](Research/ADR493SourceExportQualification.md#independent-longer-comparison-freeze493) for admission and execution status.
This is 1 investigation, not 28 independent investigations. Its runtime remains unmeasured.
Keep REHEARSAL482-RESERVE separate: the real iOS detector adapter still needs qualified encoder-freeze support.
Do not repeat rejected learning-rate, suppression, or seed comparisons to fill the queue.

Earlier source qualification update: [TTR export and independent comparisons](Research/ADR493SourceExportQualification.md).
The signed source build passes, but the actual retained export returns `persistenceFailed` before output creation.
Sillycon-TTR needs to expose the failing stage and qualify actual app/helper access. Request stored at coordinator cursor 1232.
Do not repeat captures or restart again. Keep the 4 session comparisons gated until existing recovery checks pass.
The runner receives 13 independent metadata jobs: 1 Standard review comparison, 6 iOS suppression arms, and 6 matched controls.
Standard group-aware selection improves review coverage on the new continuation failure pool. It does not improve model accuracy.
All 13 metadata jobs complete. Reject iOS suppression: it loses 20, 1, and 16 detections in 3 conditions.
The other 3 conditions preserve detection counts. Preserve Standard and all failed evidence.

Nightly review: [October 23 findings](Research/NightlyReview20261023.md).
At that nightly snapshot, ready work is 0 jobs. FREEZE493 admission above supersedes that execution snapshot.
B405-260 is reviewed and rejected for retained losses. Do not repeat the best-versus-final comparison.
Next implementation: qualify the committed TTR export repair through a matching source build and verify retained recovery proof.
Acceptance: exact exported bytes and hashes, explicit absent-marker state, unchanged recovery guards, and no repeated captures.
Owner: Maximum-mini-NUIAK for consumer qualification; Sillycon-TTR for source defects.
This releases the 4 approved session comparisons only after recovery passes.
Keep independent Standard motion membership and iOS semantic label qualification separate from that dependency.

## P1 — Six bounded ADR spikes — ADRSPIKES493

Geometry follow-up: both retained-output comparisons complete and pass output hash verification.
Each suppresses 2 harmful text changes, with 0 gains and 0 losses against the original detector.
These are related development cases, not independent model improvements. Standard remains unchanged.
The next OCR test needs observed semantic roles or independent complete labels, not another threshold sweep.
TTR export repair is pushed at `6e4a55a23932cb8a7c5937c1434a9aed82d4edc6`.
Verify a matching source-built Maximum-mini-TTR runtime before exporting retained recovery proof.
No TTR source edits or repeated captures occur during this tranche.

Latest review: all 6 mixed-model scoring runs finish with verified hashes and exact paired score parity.
Median total step time improves 13.9%; loading effects prevent a general speed claim. No production setting changes.
TTR confirms receipt of the recovery export blocker at cursor 1204. No source repair is delivered yet.
The 4 session comparisons remain dependent. Both independent OCR successors complete; the text-only rule is rejected for lost successes.
See [current findings and exact export requirement](Research/ADRspikes493Results.md#latest-review-mixed-model-scoring-and-evidence-export).

Maintainer requests these tasks on 2026-10-22. These entries authorize preparation, not new capture or model promotion.
Owner: Maximum-mini-NUIAK. The detached runner owns approved execution.
Keep Standard first. Keep iOS detection separate from tvOS focus. Report optional HCF results separately.
Preserve shipped models, previous successes, original evidence, and evaluation roles.
Do not change active source pins. Do not install dependencies or create schedules.

Prepare spikes 01, 02, and 03 first. Spike 03 can proceed independently of Fixture availability.
2026-10-22: [First-pass evidence and remaining work](Research/ADRspikes493Results.md).
The runner completes `adr493-retained-focus-review` in 0.71 s.
Four session jobs and their comparison report are now registered and approved.
Their IDs are `adr493-session-1` through `adr493-session-4` and `adr493-session-report`.
The background runner owns execution. Admission does not establish native capture success.
The first native attempt fails with TTR `resourceContended` after 2.738 s. The other captures and report remain blocked.
Maximum-mini-TTR must identify the campaign or transfer that blocks start. General readiness does not expose this owner.
Follow-up identifies campaign `A22DBCB6-F160-4EC1-8FD0-50FA7D801101` in `cleanup_unknown` after `cleanupTimedOut`.
It retains 1 failed case and 7 unattempted cases. The current resume command recovers and starts those 7 cases.
The maintainer approves recovery and those 7 unattempted cases within the remaining original budget.
`adr493-retained-campaign-recovery` uses supported Simulator restart and exact-manifest resume through the background runner.
The four immutable successors are `adr493-session-1-r2` through `adr493-session-4-r2`.
Their report is `adr493-session-report-r2`. Verified recovery output gates the first comparison.
Original admissions are revoked. Original specifications, failed evidence, and dispatch markers remain preserved.
Do not change TTR source, remove recovery markers, or repeat captures.
Recovery attempt 1 fails after 21.432 s. Simulator restart passes, but campaign resume returns `resourceContended`.
Reconciliation confirms an unchanged checkpoint, 7 unattempted cases, and 518.902681 s remaining.
The four r2 comparisons remain approved and dependency-blocked. They are not ready work.

- [ ] **ADRSPIKES493-RECOVERY — Qualify TTR campaign recovery against real restart receipts.**
  Proposed source owner: Sillycon-TTR. Execution owner: Maximum-mini-TTR.
  Recovery proof decoding requires exactly 1 inventory entry. The companion saves the full host inventory; this restart returns 11 entries.
  Confirm the persisted proof rejection and accept exact-target evidence without assuming a single installed Simulator.
  Preserve cleanup, ownership, timestamp, manifest, and cumulative budget checks.
  Add a regression test using an actual companion report with multiple Simulators.
  Require a specific failure reason for rejected recovery proof.
  Unblocks the 7 approved remaining cases and four session comparisons. Do not repeat the failed capture.
  Do not edit TTR here. Use Git and a source build for any delivered repair.
  Preserve the failed NUIAK attempt. Use a named successor after the repair passes qualification.
  BigDog-Coordinator stores `nuiak-adr493-recovery-mismatch-20261022-v1` at cursor 1191.
  The message requests routing to Sillycon-TTR and includes receipt hashes and acceptance checks.
  Forwarding and recipient acceptance remain unconfirmed. Do not infer delivery from storage.
  Update: TTR reply `ttr-adr493-recovery-evidence-20261022-v2` confirms receipt of forwarded request 1192.
  TTR reports a tested repair, but source remains uncommitted and undelivered through Git.
  The persisted restart report exists but macOS denies content access, including the scoped retry.
  The requested prior marker is absent. Message `nuiak-adr493-proof-access-20261022-v2` requests a supported read-only export path.

The maintainer approves each capture job for 800 s and 250 MB, subject to ownership and restoration checks.
Prepare spikes 04, 05, and 06 next. Do not wait for every spike before admitting a qualified independent batch.
Each spike produces one concise decision report. Passing a spike does not accept its whole ADR.

- [ ] **ADRSPIKES493-01 — Identify focus errors on difficult negatives.**
  Progress: the new review adapter verifies 456 retained observations without new inference.
  It preserves all successes and separates profiles, proposal methods, and no-focus cases.
  Remaining: verify explicit decorative-border, bright-artwork, and selected-unfocused condition labels before reporting their accuracy.
  Related: [ADR-0010](Research/ADR-0010-Hard-Negative-Diversity-and-Edge-Case-Induction.md).
  Question: Which verified negative conditions cause wrong focus selections in the retained models?
  Inputs: retained decorative-border, bright-artwork, selected-unfocused, and no-focus captures with observed focus and original groups.
  First inventory actual label support. A selected appearance alone does not prove an unfocused label.
  Reuse completed scores when model, pixels, boxes, preprocessing, and thresholds match.
  Use T37 for compatible native selection inputs. Use T63 for qualified consumer crops.
  Compare the retained baseline and current candidate on identical conditions. Keep known-box and proposal-based outcomes separate.
  Measure wrong selections, abstentions, missed focus, gains, lost successes, and support by original group and profile.
  Acceptance: every scored case has verified truth; every retained success remains included; no unsupported category receives an accuracy claim.
  Supported: identify a repeatable confusion and prepare a targeted training-data request with disjoint groups.
  Contradicted: close the tested confusion hypothesis when both models already handle the supported conditions.
  Inconclusive: name the missing observed state or independent group. Request only that missing material.
  Preparation blocker: verify which retained captures distinguish selection from observed focus.
  Bound: at most 6 new diagnostics, each 800 s and 100 MB. No new training in this spike.

- [ ] **ADRSPIKES493-02 — Measure native batch-session reuse.**
  Progress: the running source build validates 4 matched A/B/B/A plans with 4 transition recipes each.
  Readiness reports clear ownership. The correct connection uses app-managed mode, not the older project override.
  The NUIAK adapter now calls the existing campaign API and preserves the `reuse_runner` comparison.
  Four approved capture jobs form a serial dependency chain. The final report compares all four outputs.
  Software qualification passes positive and negative cases through an isolated actual queue.
  Native execution and observed annotation qualification remain runner-owned outcomes.
  Native blocker: TTR rejects campaign start despite clear general readiness. Exact retained ownership remains unavailable.
  A later status request for the new campaign ID returns `invalidArgument`.
  macOS denies checkpoint inspection, including the scoped retry. Obtain a supported TTR ownership diagnosis before a successor.
  Acceptance: bind the running helper, preserve campaign IDs, verify terminal cleanup, export once, and compare annotations and measured stage times.
  Qualify cancellation and partial export before activation. Do not change sources used by an active job.
  The older Ruby schedule helper forces project mode and TTR-local outputs. Do not use it unchanged with this app-managed session.
  Related: [ADR-0019](Research/ADR-0019-Batched-Renderer-and-Asset-Pipeline.md).
  Question: Does one persistent Fixture session reduce capture overhead without reducing valid outputs?
  Inputs: a verified local TTR source build, an available authorized Simulator, and 4 supported deterministic recipes.
  Inspect current batch interfaces and existing receipts before writing an adapter. Do not build a second renderer.
  Compare separate sessions with one reused session. Keep recipes, ordering, target, build, assets, and output requirements fixed.
  Use an A/B then B/A order for 2 repetitions. Each arm contains the same 4 recipes.
  Record setup, capture, export, validation, total time, rejected cases, and valid annotated frames per minute.
  Compare element identities, geometry, observed focus, and annotations. Explain pixel differences caused by native timing.
  Acceptance: both arms meet the same capture contract and restoration checks. Session reuse creates no missing or stale observations.
  Supported: prefer reuse if both repetitions reduce total time without lowering accepted output counts or correctness.
  Contradicted: retain the existing path if reuse creates stale state, missing annotations, or no repeatable benefit.
  Inconclusive: separate environmental variation from setup cost. Do not claim a percentage improvement.
  Preparation blocker: current batch API, recipe compatibility, target ownership, and exact capture authority need verification.
  Maximum-mini-TTR supplies missing producer capability only if local source inspection confirms that gap.
  Bound: 4 capture jobs, each 800 s and 250 MB, under the maintainer's explicit approval.

- [ ] **ADRSPIKES493-LABELS — Obtain frame-bound difficult-negative conditions.**
  Owner: Maximum-mini-NUIAK for intake; TTR producer implementation needs separate assignment.
  Reuse existing captures when their observed fields meet the contract.
  Do not infer selection or decoration from recipe names or model scores.
  The current capture adapter exports verified focus and control geometry with calibration ancestry.
  Remaining requirements and acceptance checks are in [SDK training requirements](Research/TTRSDKTrainingRequirements.md).
  SDK work remains proposed. Do not edit Maximum-mini-TTR source for this task.

- [ ] **ADRSPIKES493-03 — Compare diverse and random failure review samples.**
  Progress: the tvOS review adapter passes 10 focused tests and positive/negative queue qualification.
  Its first retained pool gives no category-coverage advantage over random selection. Do not adopt it as a better selector.
  Standard uses 18 cases per arm. Optional HCF uses 17 cases per arm. Each uses seeds 49301, 49302, and 49303.
  Remaining: qualify a separate iOS detector input connection. Do not mix platform pools.
  Related: [ADR-0024](Research/ADR-0024-Opt-In-Model-Feedback.md).
  Question: Does group-aware selection expose more distinct verified failure types than uniform random selection at equal review size?
  Inputs: completed local model reports with case identities, verified outcomes, original groups, and capture ancestry.
  Separate iOS detection and tvOS focus pools. Exclude cases without trustworthy truth from verified-failure counts.
  Freeze a deterministic selection rule using existing error categories and group coverage. Do not use a new learned selector.
  Compare 20 selected cases with 20 random cases per supported pool. Use 3 fixed random seeds recorded before scoring.
  If a pool has fewer than 20 eligible independent groups, reduce both arms equally and report the actual support.
  Measure distinct error categories, unique groups, duplicate ancestry, unusable cases, and selection time.
  Do not claim human review-time savings without measured review time.
  Acceptance: both arms use the same eligible pool and sample size; seeds reproduce membership; labels and data roles remain unchanged.
  Supported: use diverse selection if it covers more error categories without fewer unique groups than every random arm.
  Contradicted: retain uniform sampling if diversity adds no coverage or concentrates related cases.
  Inconclusive: report ties, sparse categories, or unstable comparisons. Do not infer population accuracy from failure samples.
  Preparation blocker: qualify the existing selector on real case records. T84's presence alone does not establish compatibility.
  Bound: at most 8 metadata diagnostics, each 800 s and 100 MB. No capture, transfer, training, or telemetry service.

- [ ] **ADRSPIKES493-04 — Test the value of correct screen context before training a classifier.**
  Related: [ADR-0022](Research/ADR-0022-Screen-Context-for-Focus-and-Navigation.md).
  Question: Would correct layout or active-region context improve existing focus decisions at all?
  Inputs: retained matched predictions and independently observed or reviewed list, grid, and overlay labels.
  Keep intended recipes separate from observed context. Leave unavailable ownership or active-region fields unknown.
  Reserve distinct groups for defining and testing one fixed context-to-method rule before comparing outcomes.
  Compare current context-free decisions with that rule using correct context. This is a diagnostic upper bound, not a deployable model.
  Measure recovered selections, lost successes, new wrong selections, no-focus behavior, and incorrect exclusion of valid controls.
  Acceptance: the rule uses no test-case focus truth; all context labels have evidence; unknown context preserves baseline behavior.
  Supported: prepare a separate visual-context spike only if the rule gains selections without losses or new wrong selections.
  Contradicted: stop classifier work for this use if correct context provides no useful gain.
  Inconclusive: name missing context labels or insufficient separate groups. Do not fabricate a context accuracy result.
  Preparation blocker: audit returned overlay records and qualify any missing read-only importer.
  Bound: at most 4 diagnostics, each 800 s and 100 MB. No new classifier, capture, or navigation changes.

- [ ] **ADRSPIKES493-05 — Test OCR on localized class errors.**
  Connection implemented: `scripts/ocr_class_comparison493.py` compiles short requests into existing queue specifications.
  Thirteen focused tests pass, including actual isolated queue success and invalid-request failure.
  Two approved successors reuse Run013 predictions and 30 retained frames each: `adr493-ocr-pro-a-r2` and `adr493-ocr-se-a-r2`.
  The first attempts fail at the 20 s image deadline. Preserve them and reuse the 7 completed OCR outputs.
  Successors permit 60 s per image within the unchanged 800 s total and 100 MB limits.
  Both successors complete in 5.881 s and 4.197 s. The SE successor reuses all 7 retained OCR outputs.
  Each condition gains 0 detections and loses 2 previous successes from the same scene group. Reject this text-only rule.
  The connection is complete. Context-aware refinement remains separate; preserve these regression cases before any follow-up.
  The background runner owns execution. These conditions share ancestry and are not independent corpora.
  A fixed disjoint-group vocabulary preserves unknown and ambiguous text. Production fusion remains unchanged.
  Native labels remain incomplete. Report supplied-label diagnostics only; do not claim false-positive or release qualification.
  Related: [ADR-0014](Research/ADR-0014-Hierarchical-Detection-and-OCR-Fusion.md).
  Question: Can existing OCR resolve wrong classes where the detector already finds the correct control box?
  Inputs: verified development cases with adequate box overlap, wrong class identity, and complete applicable labels.
  Include matched prior successes, ambiguous text, and no-text controls. Do not use reserved final-audit cases for rule development.
  Reuse existing Vision OCR tooling and fusion code. Preserve production taxonomy and raw detector outputs.
  Freeze one OCR-to-class rule on separate development groups. Unknown or ambiguous OCR retains the baseline prediction.
  Compare detector-only output with OCR-assisted output on identical boxes and images.
  Measure corrected classes, newly wrong classes, unchanged ambiguity, OCR failures, and total latency.
  Acceptance: evaluation groups stay separate from rule development; the report preserves original predictions and class identities.
  Supported: prepare broader qualification only if OCR recovers classes without losing retained successes.
  Contradicted: stop the tested rule if it creates errors or text does not distinguish the confused classes.
  Inconclusive: report missing labels or class semantics instead of forcing a role from text.
  Remaining: qualify missing labels before broader accuracy claims. Do not repeat the rejected text-only comparison.
  Bound: at most 6 diagnostics, each 800 s and 100 MB. No detector training or taxonomy change.

- [ ] **ADRSPIKES493-06 — Measure supported scoring batch sizes.**
  Preparation verifies 16 retained production crops and the existing T07 CPU scorer.
  The new description compares batch sizes 4 and 8 in order 4/8, 8/4, 4/8.
  It keeps the model, tensors, membership, thresholds, and 2 Torch threads fixed.
  Require paired score error at most 0.0001 and identical 0.15/0.85 decisions before interpreting timing.
  The existing adapter measures total step time, not separate loading, preprocessing, inference, or peak memory.
  These missing measurements limit any speed claim. Do not change production defaults from this small diagnostic.
  Batch description: `reports/work/ADRSPIKES493/scoring-efficiency-batch.json`.
  All 6 jobs are approved. The handoff snapshot shows 4 complete, execution 5 active, and execution 6 dependent.
  Next: review paired parity and median total time. Do not infer model improvement from these timing tests.
  Review complete: all three pairs have identical scores and decisions. Median step time falls from 1.060 s to 0.922 s.
  This 13.0% reduction applies only to the retained 16-row CPU workload. Production defaults remain unchanged.
  Next comparison: frozen mixed checkpoint, reversed first-arm order, one preparation job and six scoring jobs.
  Use `reports/work/ADRSPIKES493/mixed-efficiency-compiled.json`. Keep this short workload separate from overnight capacity.
  Related: [ADR-0011](Research/ADR-0011-Measured-Training-Efficiency.md).
  Question: Can a supported larger inference batch reduce scoring time without changing predictions?
  Inputs: one qualified retained crop set, a pinned model, the existing batch harness, and a fixed backend.
  Inspect supported batch-size controls. Do not add unsupported parameters to template descriptions.
  Compare the current supported batch size with one larger supported size on identical crops and ordering.
  Use 3 repetitions with alternating order. Report first-load cost separately from repeated scoring.
  Measure total time, model loading, crop preparation, scoring, output agreement, and memory where existing tooling measures it.
  Acceptance: use the existing numerical parity limit; require identical threshold decisions and complete output membership.
  Supported: adopt only the tested batch size if median time decreases and all correctness checks pass.
  Contradicted: keep the current size if outputs differ, memory fails, or timing shows no benefit.
  Inconclusive: report missing stage measurements or noisy timing. Do not substitute timeout ceilings for measured duration.
  Preparation blocker: verify the current harness and template expose the same batch control on the resident backend.
  Bound: at most 6 diagnostics, each 800 s and 100 MB. The runner serializes accelerator use with current experiments.

### ADRSPIKES493 completion and handoff

For each spike, record exact inputs, template version, executable job IDs, measured duration, findings, and the next decision.
Keep preparation-only items out of ready counts. Report unmatched labels and unsupported measurements explicitly.
When a small adapter connection is missing, create one bounded implementation item linked to the affected spike.
Do not add broad infrastructure or repeat answered experiments to occupy the queue.
Close a spike with supported, contradicted, or inconclusive evidence. Keep its ADR status unchanged unless separately reviewed.

## P0 — Deliver the optional HCF observer to TTR — HCF490

FP32 passes the complete 38-observation TTR replay. All 264 crop hashes match; maximum score error is below 0.000003.
The 2 failed-crop checks and all 14 prior-crop checks pass.
Maximum-mini-TTR now runs the corrected optional observer. Saved-image execution verifies both expected compiled model hashes.
Standard resources remain unchanged. Navigation stays disabled. The old build remains available for rollback.
Both FP32 runtime jobs pass. Median CPU inference is 2.63 ms for HCF and 2.71 ms for mixed, excluding proposals.
Both geometry jobs complete. Measured bodies do not recover selection; the mixed model produces 2 false-positive crops.
Native focus is verified. Best focused-body proposal IoU is 0.168; the accessibility profile remains unknown.
Paired-frame scores show the expected HCF arrival increase and departure decrease, but absolute selection still fails.
Mixed departure moves in the wrong direction; an unchanged negative stays at 0.967.
The existing transition model detects the native switch in both orders. This remains one training-source pair.
All four T47 jobs pass. Seeds 42 and 44 preserve the native switch in both orders with score 1.0.
Their earlier 408-pair reports preserve all prior successes and reduce false changes. Seed 43 remains excluded after a lost success.
Next: qualify P10/P12/P14 motion controls with verified Standard profiles and native labels.
The matched matrix and decision rules are in Research/HCF490Results.md, under “Next batch”.
- [ ] **HCF490-motion-intake:** Maximum-mini-NUIAK verifies existing native motion recipes and receipts before requesting new captures.
  Ask Sillycon-TTR through BigDog-Coordinator for delivery evidence against planned MOT and FIX-SCROLL work.
  Acceptance: matched static/moving backgrounds, fixed/moved/absent observed focus, pinned versions, and intact source groups.
- [ ] **HCF490-motion-score:** Maximum-mini-NUIAK admits 3 existing T47 jobs after intake passes.
  Compare FOCUS329 and notification seeds 42/44. Keep thresholds fixed and preserve previous successes.
- [ ] **HCF490-absence-contract:** Maximum-mini-NUIAK qualifies explicit absent-focus endpoints before temporal scoring.
  Require native absence evidence and deterministic rejection of unknown labels. Do not invent an endpoint sentinel.
  Keep static no-focus observer replay independent from this temporal requirement and the motion producer.
Moving-background accuracy remains unmeasured. Missing qualification inputs are preparation work, not ready experiments.
The runtime check abstains on 10 proposals. It proves model loading and export integrity, not additional accuracy.
Keep navigation disabled. Independent app qualification remains separate.

Earlier quantized and FP16 qualification: corrected TTR proposals recover 16/16 HCF selections from 0/16 across 4 retained conditions.
Standard-profile selections remain 10/16. All 6 no-focus observations remain correct. No previous successes are lost.
All 264 crop RGB hashes match independent preprocessing. Broader score parity fails on 2 crops despite unchanged threshold decisions.
Do not activate the resources. Keep the running app, Standard, and shipped models unchanged.
The maintainer sets the optional observer package limit to 50,000,000 bytes per model.
The 6 FP16 jobs pass. The broader consumer replay still fails score parity on 2 crops.
That failure leads to the passing FP32 comparison described above. Preserve these failed variants and their receipts.
Keep the 0.01 score-error gate and regression checks unchanged. Preserve failed quantized variants.
Twenty-six focused host tests pass; 4 historical-input tests remain skipped.
The no-focus comparison successor removes duplicate detector hashes. It preserves the original failed attempt and all 6 frame observations.
Five T60 jobs provide cached policy reports. Do not count this short work as an overnight reserve.

Latest October 21 qualification: single-weight compression passes all 98 crops for both frozen checkpoints.
TTR verifies 98 crop hashes and fallback decisions across 14 retained full-frame inputs.
Thirteen host tests pass; 4 historical-input tests remain skipped. Standard and the active app remain unchanged.
Next: qualify TTR-generated proposals and explicit resource activation. Frozen research proposals do not prove that consumer path.
All 16 new export and parity jobs complete through the background runner. Preserve their receipts and all rejected variants.
See Research/HCF490Results.md for exact errors, package sizes, scope, and previous success checks.

October 21 continuation: approved Maximum-mini-TTR source changes implement frozen fallback and lineage fields.
Host tests pass 11 checks; 4 historical tests remain skipped. The active app remains unchanged.
Broader conversion parity fails partition 4 for both models. This is a score mismatch, not a time-budget exhaustion.
Two approved palette6 correction chains test the exact failed inputs through existing T10/T11 templates.
Do not activate fallback resources before parity and actual TTR input-lineage checks pass.
See [current evidence](Research/HCF490Results.md).

Maintainer priority: 2026-10-21. Execute this delivery tranche next, without interrupting active jobs.
HCF remains optional. Preserve Standard, iOS, shipped models, and previous successes.
This priority changes the next tranche, not the broader product goals.
These entries define preparation and acceptance work. They are not admitted execution jobs.
Reuse HCF389 delivery work and retained consumer evidence. Do not create duplicate peer assignments.

- [ ] **HCF490-01 — Freeze one delivery candidate and reconcile consumer evidence.**
  Owner: Maximum-mini-NUIAK.
  Identify the exact model, hashes, preprocessing, thresholds, proposal implementation, and supported control families.
  Read the latest TTR consumer receipt. Reuse verified tests and identify missing checks.
  Acceptance: one reproducible configuration and an explicit list of verified and unverified consumer requirements.
  Do not retrain merely to start this delivery tranche.
  Progress: HCF396 is frozen for integration. TTR's 8-case inference receipt exists and T14 verification completed.
  Current review verifies retained hashes and zero threshold changes. Stronger lineage and the current full-screen path remain open.
  See [verified findings and exact remaining requirements](Research/HCF490Results.md).

- [ ] **HCF490-02 — Confirm the actual TTR box source.**
  Owner: Maximum-mini-NUIAK. Receiving project: Sillycon-TTR, through BigDog-Coordinator.
  Confirm screenshot-derived proposals for uninstrumented apps. Keep SDK-supplied boxes as a separate supported mode.
  Preferred focus identifies intent, not observed focus. Evaluation labels must not enter screenshot-only inference.
  Acceptance: TTR names its source, coordinate convention, implementation version, and handling of missing boxes.
  Record the forwarded request ID and receiving owner before claiming delivery.
  TTR reply 1111 confirms caller body boxes; HCF396 remains research-only, not build13's baseline provider.
  Production provider/provenance/export work stays with existing EXP-REVIEW-01/02/03. Exact T23 requirements are sent at cursor 1112.

- [ ] **HCF490-03 — Prepare a complete-path Fixture comparison.**
  Owner: Maximum-mini-NUIAK. Depends on HCF490-01 and HCF490-02.
  Use existing templates for full screenshots, proposals, crop scores, selection, abstention, and matched reporting.
  Cover clear rings, decorative borders, light backgrounds, small controls, transitions, no-focus scenes, and retained successes.
  Reuse captures first. Define exact membership, data roles, groups, limits, and restoration requirements before admission.
  Use observed focus and frame-aligned bounds as labels. Distinguish observed no-focus from unknown labels.
  Acceptance: the real TTR input path runs without hidden boxes in screenshot-only mode.
  Report proposal recall, selection gains, losses, wrong selections, abstentions, and runtime by case and family.
  Let the detached runner execute authorized jobs. Do not navigate or capture from this planning entry alone.
  Offline batch completes. HCF396 loses 12 known-box native successes against the mixed model. General replacement fails.
  Two T61 geometry diagnostics reuse button and decoration results. They require no captures, inference, or training.
  Both initial diagnostics fail because the batch supplies the wrong receipt type. Preserve their failed attempts.
  Corrected `hcf490r2-geometry` successors pin execution receipts. The receipt reader verifies both corrected bindings.
  Both successors complete with verified outputs. Buttons match 32/32 observations; decoration matches 12/32.
  Select T60 abstention fallback across all 5 retained conditions. Keep boxes, scores, thresholds, and Standard unchanged.
  Reject on losses to either model, new wrong selections, or no-focus regressions.
  All 5 T60 jobs pass: HCF 15/16 versus candidate 3/16 and mixed control 14/16, with no losses or new wrong selections.
  Select fallback for broader regression and consumer feasibility. Do not change Standard or silently install the mixed model.
  Preserve 8 revoked stale-reference specifications. These comparisons do not establish the missing TTR production integration.

- [ ] **HCF490-04 — Verify transfer beyond Fixture.**
  Owner: Maximum-mini-NUIAK. Depends on the fixed configuration from HCF490-01.
  Use an available qualified app with different layouts and verified observed labels.
  Keep related frames in the same group. Do not tune on this comparison.
  Acceptance: report the complete path and retained-success comparison on named app and build versions.
  If no suitable app exists, record the exact input requirement without blocking the Fixture integration test.
  New installations and SDK modifications require their applicable authority.

- [ ] **HCF490-05 — Decide and hand off the optional observer.**
  Owner: Maximum-mini-NUIAK. Consumer owner: Sillycon-TTR.
  Depends on HCF490-03 and HCF490-04, or an explicitly narrower Fixture-only trial decision.
  Acceptance: preserve prior successes, add no wrong selections on the declared comparison, and verify correct no-focus behavior.
  Require consumer confirmation of the loaded model and preprocessing. Report coverage gaps and unsupported cases explicitly.
  Package the supported mode, configuration, results, rollback reference, and consumer instructions through the existing delivery contract.
  Enable only the optional observer after applicable acceptance. Keep navigation disabled and Standard unchanged.
  A Fixture-only trial is not a general release. Full-screen qualification remains distinct from crop-scoring qualification.
  Reply 1117 reports default-off observer source integration. All 5 metadata files pass transfer verification.
  Native UI/build qualification and T23 lineage remain with Sillycon-TTR. No activation or model acceptance is claimed.
  HCF490Results records the failed native comparisons and the experimental observer limits for consumer review.
  Runtime reply 1125 supplies 9 app-process checks. Both metadata files verify; counts and navigation flags agree.
  Remaining gap: TTR must define model_confidence and supply the actual decision score. Native UI review and T23 remain open.
  Score semantics now close: all 45 prior and 9 new annotations match the focus-probability thresholds.
  Portable five-producer intake passes for passive review. Partial states and unknown labels remain preserved.
  Six broader scoring jobs cover edge clearance, tall controls, and diamond decoration before fixed T60 regression.
  All 6 scoring jobs and 3 T60 fallback regressions complete with verified outputs.
  Broader HCF fallback gets 12/12 versus 10/12, without losses or new wrong selections. Combined HCF gets 27/28.
  Corrected single-root extraction and paired receiving-Mac checks pass. Exact receipts are stored at coordinator cursor 1151.
  Passive intake is accepted. App launch, native UI, independent app accuracy, and T23 remain unqualified.
  Nine approved T37/T57 jobs test retained lower-confidence proposals with decoration and no-focus regression checks.
  Apply fixed fallback after verifying scoring receipts. Reject losses or new wrong selections before any consumer change.
  All 9 scoring jobs now complete with verified outputs. Seven cached fallback comparisons reuse these scores.
  Maximum-mini-TTR source checkout is verified at dd40d8bf. Its signed build completes in 77.19 s.
  Exact candidate verification, paired receiver checks with the app, and passive app status pass.
  The observer is available and remains disabled. Navigation remains disabled for this provider.
  Seven fallback comparisons complete. Lower-confidence proposals recover 3 Standard-profile cases without losses or new wrong selections.
  These development results do not change Standard or qualify the TTR fallback integration.
  Do not substitute downloaded binaries. Preserve the existing TTR session and background runner.
  Remaining consumer requirements: native UI/new candidate qualification and T23 lineage. No full observer acceptance is claimed.
  If a gate fails, name the failing cases and smallest justified correction. Do not open an unrelated training campaign.

## P1 — Declarative Fixture datasets through TTR — DATASET491

Maintainer approves this investigation on 2026-10-21. HCF490 delivery remains P0.
Owner: Maximum-mini-NUIAK. Capability review destination: Sillycon-TTR through BigDog-Coordinator.

- [ ] **DATASET491-01 — Reconcile delivered capabilities and define the smallest request contract.**
  Confirm existing full-screen recipes, batch interfaces, annotations, export, interruption recovery, and restoration capabilities.
  Locate the reported 7-app library and exact delivery receipts before requesting replacement implementation.
  Requests name recipes, seeds, variations, roles, groups, required outputs, target, and measured budgets.
  Cover movement, unchanged focus with content changes, arrival, and observed no-focus. Keep unknown focus distinct.
  Require frame-aligned bounds, stable IDs, observed focus, action timestamps, source versions, and immutable receipts.
  Preferred focus remains intent. Keep evaluation labels out of screenshot-only inference.
  Review diverse mockable layouts: media, news, game menus, catalogs, and utilities. HCF is a separate optional profile.
  Acceptance: map each requirement to an existing interface or an exact missing capability and responsible owner.

- [ ] **DATASET491-02 — Prove request-to-comparison reuse with existing templates.**
  Depends on DATASET491-01. Connect only missing interfaces; do not build another workflow framework.
  Prepare 2 bounded requests. The second changes configuration without a new script.
  Validate returned labels, coordinates, roles, groups, duplicate exposure, output completeness, and restoration automatically.
  Preserve legitimate identical-frame pairs. Resume unfinished cases without repeating verified captures.
  Successful intake releases only the exact approved comparison. A failed case blocks only its dependents.
  Acceptance: both requests produce ingestible datasets and comparison reports through the detached runner.
  Pin actual budgets and qualified targets before execution. This investigation does not authorize arbitrary capture or peer implementation.
  Record preparation time, execution time, manual interventions, and exact failures. Preserve Standard and previous successes.

## P0 — Deliver executable research chains — FLOW478

Nightly review: [October 22 findings](Research/NightlyReview20261022.md).
The runner waits without a current job. Readiness still fails on `.DS_Store`; useful ready duration remains unavailable.
Prioritize NIGHTLY489-READINESS, RECOVERY488, and REHEARSAL482-RESERVE before more repeated single-pair HCF checks.
No new jobs or budget extensions follow from this review. Keep native motion preparation separate from independent Standard and iOS work.

- [ ] **NIGHTLY489-READINESS — Ignore non-directory entries in queue enumeration.**
  Owner: Maximum-mini-NUIAK. `backlog_pipeline.py status` fails on `jobs/.DS_Store/spec.json`.
  Restore readiness counts before claiming overnight capacity. Do not change pinned sources during active execution.
  Acceptance: test metadata files beside real jobs, preserve valid-job counts, and verify CLI/dashboard readiness.
  No training, capture, or service restart is authorized by this task.
  See [the nightly findings and priority changes](Research/NightlyReview20261021.md).
  Implementation and focused tests pass. CLI readiness succeeds. Running-dashboard activation waits for an idle boundary.

- [ ] **RECOVERY488 — Qualify repeat-aware crop continuation.**
  Owner: Maximum-mini-NUIAK. DEDUP486 exposure preserves completed epoch 16 with repeat 9.
  The maintainer approves up to 30 additional minutes after parity passes, within the original 30 epochs and 2 GiB limit.
  Existing qualification and restore adapters hard-code repeat 1. Extend support without changing sources used by running jobs.
  Acceptance: uninterrupted versus restored state parity, wrong-contract rejection, preserved checkpoint, and cumulative budget accounting.
  Use bounded chunks under the existing 800 s continuation limit. Create explicit scoring successors after a qualified continuation.
  Do not restart from zero or reuse the repeat-1 proof. See [the reviewed findings](Research/Review488Results.md).
  Repeat-9 parity now passes exactly on an original training subset. Full checkpoint settings and subset membership verify.
  `dedup486-exposure-resume23` is revoked before execution after a source-pin conflict. Preserve its record; do not count it as ready.
  Done 2026-10-22: 2-step chain parity passes exactly; the revoked reservation is released.
  `dedup486-exposure-chunk23` and `dedup486-exposure-chunk30` are approved, with 27 `dedup486-exposure-r2-*` successors.
  Chunk 1 fails the evidence check (unread `negatives` dependency) after reaching epoch 23 in 346 s.
  Repaired: `dedup486-exposure-chunk23r2` and `chunk30r2` (700 s each) and 27 `dedup486-exposure-r3-*` successors are approved.
  `chunk23r2` completes in 345 s and passes all checks; `chunk30r2` runs next. Allowance used: 346 + 345 s so far.
  The r3 chain completes: chunk30r2 reaches epoch 30, and 27 r3 jobs run. Reviewed in DEDUP486-REVIEW below.
  See [the binding record](Research/Recovery488AndIOS491.md#bounded-continuation--qualified-and-bound-2026-10-22).

- [ ] **DEDUP486-REVIEW — Review independent Standard exposure comparisons.**
  Owner: Maximum-mini-NUIAK. Compare unique-pixel and near-matched-exposure arms against the completed Standard control.
  Require all 17 retained conditions and zero lost previous successes before replacement consideration.
  Report changed family weighting and positive-class weight. Do not claim isolated duplicate-removal causality.
  See [the experiment and stopping decisions](Research/Dedup486Results.md).
  Reviewed 2026-10-31 (r3 exposure arm): contradicted. Standard fixed-proposal selection is unchanged (0 gains, 0 losses).
  The HCF known-box arm loses 9 previous successes and adds 3 wrong selections. Standard known-box loses 2 and adds 3.
  Decision: reject replacement. Arms and related frames are not independent trials.

- [ ] **REHEARSAL482-RESERVE — Qualify a bounded optimization comparison for detector training.**
  Owner: Maximum-mini-NUIAK. Priority: P1. This is implementation work, not a ready experiment.
  Both 64-frame arms regress. Check existing adapters for lower learning rate or frozen-backbone support.
  Acceptance: actual detector training supports one changed setting, preserves default behavior, and passes positive and failure tests.
  Prepare matched controls and retained comparisons. Do not launch an unqualified novel adapter or an arbitrary sweep.
  The supported lower-learning-rate variant passes caller and failure tests. IOS491 has 17 approved jobs, including matched cached reports.
  IOS491 is reviewed: contradicted. It gains 15 and loses 46 Run013 detections; `label` loses 19. Reject replacement.
  Do not run further learning-rate fits for this membership. Diagnose the lost `label` and `homeIndicator` cases first.
  See [the result](Research/Recovery488AndIOS491.md#result).

Owner for all items: Maximum-mini-NUIAK.
The detached runner owns experiment execution.
These are implementation tasks, not claims of ready jobs.
Keep Standard and iOS first. Keep HCF separate and optional.
Preserve previous successes, evaluation roles, original attempts, and shipped models.
Do not change scheduled tasks without explicit consent.

- [ ] **FLOW478-01 — Finish the current repairs.**
  Implement the remaining GROOM477 recovery and iOS annotation work listed below.
  Recovery successors must reuse completed restoration and the 8 button frames.
  iOS successors must export standalone text labels and pass completeness and geometry checks.
  Completion: verified recovery releases captures and comparisons; qualified iOS membership passes the existing trainer-input checks.
  Preserve any failed gate. Name its exact repair instead of treating every failure as another capture requirement.
  Current evidence: button restoration and all 8 dependent comparisons complete without recapture.
  Row restoration completes after verified retention. Its original 8 frames remain preserved.
  Two corrected iOS producers pass annotation checks. Trainer preparation accepts 28 frames and excludes 4 clipped frames.
  Three remaining native captures use verified retention before restoration.
  Live completion and comparison results remain required.
  Tab and decorative-border successors now complete with restoration.
  The no-focus capture and downstream comparisons remain with the runner.

- [ ] **FLOW478-02 — Complete reusable investigation batches.**
  Depends on FLOW478-01 only for the affected inputs.
  Connect existing generation, label preparation, training, scoring, comparison, and terminal reporting adapters.
  Each description names the question, control, changed factor, input roles, limits, regression checks, and resulting decision.
  Add implementation only for a demonstrated missing connection.
  Test actual producer outputs against consumer inputs before admission.
  Completion: 2 distinct campaigns use the same batch compiler without a new campaign script.
  Their terminal reports identify gains, lost successes, wrong selections, uncertainty, and the next action.
  Both IOS478 graphs compile and receive approval through the same implementation.
  Original fits exceed their checkpoint output limits.
  IOS478R successors preserve training settings and retain fewer intermediate checkpoints.
  Final comparisons remain required before closing this item.

- [ ] **FLOW478-03 — Prepare the research program and independent reserve.**
  Begin independently of capture recovery.
  Map existing ADRs, approved tasks, and unanswered results into a rolling 4-week investigation plan.
  Cover Standard detection, classification, focus, no-focus behavior, iOS, optional HCF, and useful workflow measurements.
  Identify shared prerequisites so dependent jobs do not count as independent investigations.
  Prepare 48 hours of useful ready work when qualified inputs and approved budgets support that duration.
  Otherwise, report the measured duration available and the exact preparation work needed.
  Completion: every investigation has an actionable decision and a ready, conditional, implementation-needed, rejected, or superseded state.
  Do not create arbitrary sweeps or extend training merely to fill the target.

- [ ] **FLOW478-04 — Connect bounded follow-ups and repair handoffs.**
  Depends on FLOW478-02 for supported batch contracts.
  Encode approved actions for supported, contradicted, inconclusive, and invalid-evidence outcomes.
  Use existing producer adapters for missing data when the repair contract is supported.
  If a repair needs code, produce one deduplicated implementation task with its owner and acceptance checks.
  Do not claim that a generated implementation task executes itself.
  Preserve per-branch and cumulative budgets.
  Completion: queue tests prove valid branching, invalid-evidence refusal, restart recovery, and no duplicate execution.
  An unselected branch remains separate from a real blocker.
  FLOW479 repairs the live request-read and typed-result failures.
  The controls decision automatically releases its diagnostic branch; 5 diagnostics complete at this check.

- [ ] **FLOW478-05 — Prove independent execution and useful decisions.**
  Depends on FLOW478-02 through FLOW478-04.
  Use actual campaigns and isolated fault tests; do not disrupt active experiments to manufacture a failure.
  Completion: at least 3 independent investigations finish with verified decision reports.
  At least 1 approved follow-up executes without another manual admission step.
  An isolated blocked-branch test proves unrelated ready work remains eligible.
  Report ready duration, preparation delays, avoidable idle time, and resolved research questions.
  Do not equate completed job counts with improved models.

- [ ] **FLOW478-06 — Close the nightly-review handoff during the next work session.**
  Keep the nightly review planning-only.
  Reconcile each actionable finding with an existing task, completed answer, or explicit rejection.
  Implement authorized high-impact repairs during the work session.
  Completion: each selected repair either releases verified executable work or records an exact remaining requirement.
  Preserve original failures and show which experiments each repair releases.
  Do not close the handoff merely because task descriptions exist.

Priority order: finish FLOW478-01 while preparing independent work in FLOW478-03.
Then complete batch reuse and follow-ups before claiming FLOW478-05.
FLOW478-06 applies throughout this tranche.

The [rolling research program](Research/Plans/ResearchProgram478.md) maps 4 weeks of independent and conditional work.
IOS478 controls and toggles each use the same 14-job compiler.
Each graph includes a fixed regression follow-up.
The 48 h ready-work target remains unmet. Reserved execution limits are not runtime estimates.

- [ ] **FLOW478-07 — Qualify frozen-feature training for B405-191.**
  Owner: Maximum-mini-NUIAK. Priority: P1.
  Real T06 encoder freezing and strict boolean configuration checks are implemented. The focused suite passes 37 tests.
  CPU qualification keeps actual encoder parameters and buffers fixed while the classifier updates. Buffer corruption fails verification.
  FREEZE493 runs the unchanged Standard membership against the completed full-training control and all 17 retained conditions.
  Pending: full-run encoder checks, matched results, and case-linked acceptance. No model promotion follows from software checks.
  Frozen checkpoint restoration remains explicitly unsupported. Do not use T77 example outputs as resident model checkpoints.
- [ ] **FLOW478-08 — Qualify teacher anchors for B405-195.**
  Owner: Maximum-mini-NUIAK. Priority: P1.
  Acceptance: detached teacher gradients, no evaluation ancestry, and preserved retained regressions.
  Reuse existing training and comparison components.
  This is the next independent training preparation priority after the admitted frozen-feature comparisons.
  Pin the retained teacher and NCTRL417 training-only anchor membership. Preserve initialization, exposure, preprocessing, and thresholds.
  Compare the existing full-adaptation control against one predeclared teacher penalty. Reuse completed control scores.
  Require actual model training tests before admission. Example tensors do not qualify the adapter.
  Include all 17 retained conditions and the consumer path in terminal reporting.
  Reject any new wrong selection or lost previous success. Report uncertain results without automatic extension.
  Keep the fit within 30 epochs, 1,800 s, and 2 GiB. Measure runtime before claiming overnight coverage.
- [ ] **FLOW478-09 — Add full-corpus iOS regression evaluation to the reusable batch.**
  Owner: Maximum-mini-NUIAK. Priority: P0 after native pilot decisions.
  Acceptance: unchanged class order, pinned original labels, fixed preprocessing, and complete retained-case accounting.
  Native development gains do not qualify replacement.

## P0 — Review qualified producer graphs — GROOM477

- [ ] Verify restoration-only recovery and the derived button receipt. Do not repeat the 8 completed button frames.
  Keep the recovery guard until Standard restoration, Fixture state, and closed ownership pass.
- [ ] Review the 4 gated native captures and 40 matched diagnostic successors as one batch.
  Compare fixed DETECTOR469R thresholds and original versus CROP471 crop selection.
  Preserve Standard, no-focus outcomes, and every previous success.
- [ ] Maximum-mini-NUIAK: complete iOS text annotations in UIKitControls and UIKitToggleForm.
  The 32 generated frames pass geometry checks, but standalone visible text has no `label` annotations.
  Export standalone labels through the existing generator. Review canonical button classes.
  Rebuild T46 and queue explicit replacement producers with the same training-reserved groups.
  Acceptance: complete supported-instance coverage, geometry checks, duplicate checks, and unchanged evaluation exclusions.
  Keep the current 32 frames training-ineligible and preserve their evidence.
- [ ] Qualify the iOS trainer inputs after label admission.
  Resolve ambiguous button-role classes separately. Preserve Run 013 initialization and the retained evaluation suite.
- [ ] Load the new unselected-branch presentation at the next controlled dashboard restart.
  Do not interrupt the running experiment graph.

See [the graph, qualification limits, and decisions](Research/Plans/Groom477.md).

## P0 — Remove root blockers, not safeguards — GROOM476

- [ ] Maximum-mini-NUIAK: reconcile remaining historical native and low-dose entries against verified successors.
  Do not hide an unresolved question merely because its attempt is old.

See [backlog cleanup and remaining requirements](Research/Groom476Results.md).

## P1 — Independent iOS geometry review — NIGHTLY475

- [ ] Maximum-mini-NUIAK: qualify independent interruption class evidence before detector training.
  IMPORT472 review conversion is complete. Agent-reviewed action records do not establish canonical detector classes.
  Acceptance requires image-linked class decisions, explicit unknown labels, preserved development roles, and separate training membership.
  This unblocks B405-252 through B405-254 only where their remaining input requirements also pass.

See [nightly findings](Research/NightlyReview20261020.md).

## P0 — Preserve detector gains without losing successes — REVIEW470

- [ ] Maximum-mini-NUIAK: obtain independent class review before detector class evaluation of the interruption records.
  IMPORT472 accepts review conversion only. It preserves 12 events, 7 image hashes, and 1 group.
  Canonical classes remain withheld. Profiles remain unavailable.
  Review declared artwork labels and overlay roles against independent evidence.
  Do not convert unknown underlay focus to no-focus negatives.
  B405-048, B405-111, and B405-252 through B405-254 require separate readiness checks.
  Conversion alone does not unblock training or complete-path accuracy claims.

Plans: [new hypotheses](Research/Plans/NativeHypotheses470.md) and [matched detector results](Research/Detector469RResults.md).
Latest review: [fallback results and longer work](Research/Review470Results.md).
Standard, iOS, previous successes, and shipped models remain unchanged. HCF stays optional.

## P0 — Qualify reserved producer outputs — RECOVERY464

- [ ] Sillycon-TTR: review whole-shard storage admission as an extension of the existing advisory forecast.
  Require a finite caller budget for capture, restoration, and closure before input.
  If insufficient, return a typed blocker and offload requirement before capture starts.
  Accept verified offload receipts without discarding journals or repeating completed capture events.
  Test insufficient space, interrupted offload, restart, stale receipts, and restoration reserve use.
  This is a feature proposal for prioritization, not authority to modify TTR or raise quotas.

The iOS label and class-map review remains independent. Its completed diagnostics do not establish model gains.

## P0 — Verify recovery and conditional captures — RECOVERY463

- [ ] Review the queued recovery and automatic admission gate as a batch.
  USB offload and hash verification pass. Read-only storage accounting passes under the unchanged 1 GiB policy.
  The gate admits 4 exact captures only after Standard restoration, Fixture restoration, and closed ownership pass.
  Preserve the failed row shard and all journals. Do not clear the guard manually.
- [ ] Review the 36 matched analyses after their capture dependencies complete.
  Preserve Standard, no-focus outcomes, the lost tab case, and previous successes.
  Keep the separate 18 training groups unadmitted until complete capture and label qualification.

Plan: [verified offload and recovery](Research/Plans/Recovery463.md).

## P0 — Explicit Standard recovery and exact TTR repair — RECOVERY462

- [ ] Resolve the new row capture's TTR storage failure before another capture attempt.
  The raw route reply reports evidence budget exhaustion. Restoration stops before input.
  Preserve the partial capture and guard. Verify offload and restoration before releasing dependent jobs.
  The current batch has 2 completed jobs, 1 exhausted attempt, and 39 dependent jobs.
  No training groups qualify from this failed development capture.

- [ ] Review the four remaining captures and their matched comparisons as a batch.
  Standard preparation now precedes the unchanged HCF round-trip restoration check.
  Native restoration passes. An evidence-only successor repairs the unread retention receipt without repeating navigation.
  The review completes. The corrected admission gate checks serial retention dependencies before releasing captures.
  The gate completes and approves the four captures. The runner starts row-top capture without a restart.
  Four remaining development captures and 36 analysis jobs use explicit successors.
  The gate approves only the four pinned captures after verified restoration and fresh ownership checks.
  Preserve completed captures, old failures, original guard bytes, and regression cases.
- [ ] Maximum-mini-TTR: identify the source revision and deployment path for the reported repaired binary.
  The delivered `2974a8e2` identifier is a binary hash, not a Git revision.
  Maximum-mini-NUIAK verifies both transfer manifests and four report files. Local runtime qualification remains separate.
  The existing handoff continues through coordinator message 974. Stored does not establish delivery.
- [ ] Use durable campaign resume and export retry only for records with a verified campaign identity.
  These existing captures use the direct route adapter. They have no TTR campaign identifier to resume.
  Retention-only recovery preserves the completed 24-frame capture without repetition.
  The failed training producer remains incomplete and unadmitted.

Plan: [recovery sequencing](Research/Plans/RetentionRecovery461.md).
The background runner owns execution. Standard and iOS models remain unchanged.

## P0 — Retention-only recovery and remaining captures — RETENTION461

Plan: [measured retention recovery](Research/Plans/RetentionRecovery461.md).

- [ ] Review the RECOVERY462 result for explicit Standard verification before the recovery round trip.
  `native461-restore-training-failure` reports original and observed HCF. Navigation normalization does not set Standard.
  Preserve its guard. Require verified Standard, Fixture restoration, and closed ownership before releasing captures.
  The retention-only recovery completes without repeating the 24 captured frames.
- [ ] Review the four development capture successors and their matched comparison graph.
  Preserve completed button-top results, original failed attempts, and every previous success.
- [ ] Diagnose the training profile failure before any retry of that incomplete producer.
  It is not a retention failure. Do not treat its incomplete evidence as admitted training data.


## P0 — Independent iOS label review and matched comparisons — IOS460

- [ ] Review the 44 additional unmatched boxes from B405-214 before reporting precision.
  Maximum-mini-NUIAK owns this review. Metadata identifies 31 boxes near labels and 13 without nearby labels.
  These categories do not establish false detections. Keep uncertain labels unknown and preserve original annotations.
- [ ] Review B405-249 and B405-250 across all 6 retained iOS sets.
  Class-agnostic matching separates class errors from missing boxes. Button-role grouping tests annotation ambiguity only.
  Compare against retained class-aware results. Do not change production labels or thresholds.
- [ ] Qualify the training inputs for existing B405-020 before queue admission.
  Freeze new training groups, hashes, complete reviewed labels, and exclusions for all retained development and audit groups.
  Qualify T89 with the iOS class map and Run 013 initialization. Its generic trainer is not proof of iOS input qualification.
- [ ] Queue a matched control and one evidence-backed correction after input qualification.
  Use equal exposure, identical initialization, seed, preprocessing, epochs, and fixed-last selection.
  Compare every retained supported class and preserve prior successes. Do not use the 180 development frames for fitting.
  Keep the existing 30-epoch, 1800 s, 2 GiB bounds unless a separately recorded budget applies.

These iOS diagnostics have no TTR dependency. Their outputs do not establish model improvement.
The new jobs reuse predictions; they are short diagnostics, not overnight training work.


## P0 — New native evaluation — NATIVE459

Plan: [new native evaluation](Research/Plans/NativeEvaluation459.md).

Unique-inode accounting and retention-only recovery are qualified in RETENTION461.
Finite campaign reservations replace the logical-path and fixed archive limits. Original evidence remains unchanged.

- [ ] Review B405-242 through B405-248 after their dependent captures and reports complete.
  The 52 template jobs separate label validity, detector coverage, crop selection, and full-screen focus.
- [ ] Qualify the separate reserved training corpus after its producer gate and captures complete.
  Do not use development captures as training replacements. Preserve all prior regression cases.
- [ ] Select at most one correction from the combined findings. Keep known robustness losses binding.

Recovery passes in 94.15 s. The corrected development gate completes without another recovery run.
The original failed gate receipts remain intact. The training producer gate remains dependent work.

## P0 — Recover captures with bounded retention — NATIVE458

Plan: [native capture retention](Research/Plans/NativeStorage458.md).

- [ ] Review the two successor admission gates for 6 development captures and 6 reserved producer captures.
  Each chain waits for verified retention after its previous capture. Preserve every failed attempt.
- [ ] Qualify the 18 reserved groups after capture. Keep development cases excluded from training.
- [ ] Compile the matched detector fit and full comparisons with the existing DETECTOR457 compiler after admission.
  Preserve the lost tab case, Standard successes, and no-focus checks. No new fit is ready yet.

Storage compaction preserves 184 PNG paths and all journals. The current guard passes at 281,125,624 bytes.
The background runner starts the recovery without a restart. Conditional capture work is not ready training duration.

## P0 — Detector training and capture readiness — DETECTOR457

Plan: [reusable detector campaigns](Research/Plans/DetectorCampaign457.md).

The storage correction and explicit recovery successor now live under NATIVE458. Preserve the original exhausted attempt.
- [ ] Maximum-mini-NUIAK: qualify the 18 reserved training groups after native capture succeeds.
  Require measured bounds, complete labels, observed focus, hashes, ancestry, and explicit training admission. Reservations are not data.
- [ ] Maximum-mini-NUIAK: compile the admitted detector fit and full comparisons through `detector_campaign457.py`.
  Keep 640 pixels, confidence 0.5, 30 epochs, 2 h, and 2 GiB. Include the retained lost tab check.
Both detector reports complete. Preserve the 6 Standard robustness losses and the lost tab case.

The reusable compiler connects T89, T56, T57, and a case-linked decision without another script per campaign.
The controls and robustness reporting jobs reuse completed outputs. They do not provide overnight training work.
The Standard correction remains rejected despite 5 gains on the control slice.
The new corpus is blocked. No new fit is admitted with missing inputs.

## Recovery after verified storage cleanup — STORAGE456

Recovery and conditional admission complete. The first released capture fails from storage exhaustion.
The remaining five stop at the recovery guard. DETECTOR457 tracks the current blocker.

The maintainer approves a bounded 1 GiB policy for this recovery work. The 128 MiB restoration reserve remains unchanged.
The exact storage inspection passes with 561,232,024 bytes retained. All failed sessions and recovery journals remain intact.
The 22 isolated recovery and admission tests pass. Each job keeps its existing execution and output limits.
The policy remains a hard stop. Do not increase it again automatically or delete failed evidence.
Review storage after recovery before expanding capture work beyond these 6 frozen jobs.
Evidence stays under `reports/work/STORAGE456/`. Standard models and previous successes remain unchanged.

## Nightly priorities — 2026-10-18 Pacific

Report: [nightly findings](reports/work/NIGHTLY-20261019/Review.md).
ANNOTATION454 completes 24 diagnostic jobs and rejects the resolution increase. Overnight training capacity is not yet qualified.
The runner owns execution. Report measured duration separately from timeout ceilings.

- [ ] Maximum-mini-NUIAK: prepare new independent training layouts after native capture recovery. B405-232 through 234 are reviewed.
  Preserve the lost tab match before any detector replacement. Do not repeat fitting on the same 3 layouts without new evidence.
Lower-confidence review completes: 0 gains and 1 Standard loss. Keep confidence 0.5.
Preserve training regression `b405-167-tab-selected-b405-027-tab-selected-1-standard-item-1-0`, control `item-1`.
- [ ] Maximum-mini-NUIAK: prepare standalone text, image, and missing container examples after capture recovery.
  Canonical mapping is qualified, but retained text and images are all nested inside controls.
  Require complete native inventories and independent training groups. Do not invent standalone labels from nested content.
- [ ] Maximum-mini-NUIAK: review unmatched iOS boxes from B405-230/231 before any threshold decision. Both completed analyses remain inconclusive.
- [ ] Maximum-mini-NUIAK: review the received accessibility contract with accepted and rejected import examples. Require published source and native receipts before admission.

Acceptance: preserve ancestry, unknown focus, pair abstentions, image geometry, and profile evidence. Do not treat proposed pairs as training labels.
The TTR documents are hash-verified under `reports/work/NIGHTLY-20261019/intake`. Receipt cursor 919 proves storage, not delivery.
These requirements do not authorize peer cleanup, new services, or source uptake.

## P0 — Repeatable research campaigns — RESEARCH451

Owner: Maximum-mini-NUIAK. Contract: [outcome-led research graphs](Research/Plans/ResearchGraph451.md).
This milestone joins research priorities with reusable execution. Existing BOXTRANSFER450 jobs stay unchanged.
RESEARCH451-01 through 06 are complete. The remaining milestone tasks appear below.

| Task | Priority and dependencies | Deliverable and acceptance |
|---|---|---|
| RESEARCH451-08 | P1; next 3 campaigns | Record approval-to-decision time, interventions, avoidable idle time, useful decisions, and retained successes. Establish missing baselines; do not claim unsupported savings. |

RESEARCH451-07 qualifies the existing shared approval read on a fixed 5-job workload.
Median time falls from 0.958 s to 0.181 s across 3 paired runs. All decisions remain identical.
The isolated test retains full source hashing. It does not change live approvals or execution.
Next: complete 08 alongside eligible model work. Missing intervention and idle-time records remain unavailable.
Reuse the completed T17 preparation comparison before planning another cache benchmark.
Its 24-frame test reports 3.237 s separate versus 1.065 s shared preparation, with identical decoded metadata.
This supports preparation reuse only. It does not establish training speed or model gains.
RESEARCH453 adds receipt-verified combined findings and separate readiness lanes to the read-only dashboard.
Unassigned work stays explicit. Missing duration history is unavailable, not the job budget.
The 3 new T88 diagnostics use the existing compiler. They reuse baseline inference and change only the detector candidate.
Their counts measure training correspondence, not held-out accuracy. The IoU 0.1 match rule does not establish usable proposal recall.
The original runner and Standard models remain unchanged. General UI annotation coverage remains a separate producer requirement.
TRAINING452 qualifies the short crop-training request through existing preparation, trainer, scorer, and comparison adapters.
Two retained campaigns execute 18 reporting nodes. Two supported branches remain unselected because regressions persist.
Both decisions exactly match their original scientific fields. No training or inference repeats.
The final 13 focused tests and 191 offline Swift tests pass. The broader 58-test workflow regression suite also passes.
New training still requires eligible inputs and a prior log entry. Detector annotation work remains separate and blocked on complete labels.
Evidence: `reports/work/TRAINING452/native-qualification.json` and `handoff.md`.
The coverage campaign completes 7 nodes and rejects replacement: 0 gains, 1 loss, and 0 new wrong Standard selections.
The spacing campaign preserves its no-focus validator failure. Three `-r2` successors reuse completed comparisons without repeating scoring.
All 3 successors complete. Spacing gains 2 selections without losses or new wrong selections and preserves the no-focus abstention.
Both final reports reject replacement because retained regressions remain. No model changes follow.
See the exact requests and receipts under `reports/work/RESEARCH451`. No runner restart occurs.
Keep BOXTRANSFER450's consumer regression visible. Do not promote from the new development comparison alone.
The next detector correction needs complete eligible training annotations; do not use inspected development offsets for training.
Any TTR request must name the required output, available capability, acceptance checks, owner, and exact work it unblocks.
No recurring review or new execution authority is created by this milestone.

## P0 — Measured-box transfer — BOXTRANSFER450

Owner: Maximum-mini-NUIAK. Plan: [GEOMETRY449](Research/Plans/Geometry449.md).

- [ ] Require training-only evidence before any new fit. Preserve all previous successes and no-focus abstentions.

The 6 comparisons and grouped review are complete under RESEARCH451. Replacement remains rejected.

All 12 GEOMETRY449 audits complete. Six misses lack matching proposals; two have usable boxes but fail selection.
The neighbor and shelf boxes are 16.9% and 14.1% taller than known bodies. Scores fall to 0.717 and 0.842.
This suggests box sensitivity, not a causal height correction. Do not lower thresholds or train on development offsets.
BOXTRANSFER450 reuses the completed measured-box model and detector outputs. All 6 jobs pass preflight and receive exact approvals.
All 17 focused tests pass. The runner owns execution. No capture, training, or production changes occur.
See [the comparison plan](Research/Plans/BoxTransfer450.md).

CASCADE446 completes all 10 jobs: 31/40 focused selections versus 29/40, with 0 lost successes and 0 new wrong selections.
All 3 no-focus abstentions remain correct. Both gains occur in 1 original group.
The report contains 13 case identifiers across 11 original groups. It does not establish independent deployment accuracy.
COVERAGE447 registers and approves all 30 jobs in groups of 10 after 20 focused tests pass.
Preflight identifies 6 ready preparation jobs and 24 dependent jobs. The runner receives them without a restart.
Standard controls acceptance. HCF remains unchanged. No further training or policy change is justified yet.

All 30 coverage jobs and 7 final comparison jobs complete.
The extension remains at 12/20 correct focused selections, with 0 gains, 0 losses, and 0 new wrong selections.
The no-focus frame still abstains. Wider efficacy remains inconclusive across 4 original groups.
All 12 cached audits pass preflight and receive exact approvals after 12 focused tests pass.
The existing runner owns execution. No policy change or additional training is justified yet.

WORKFLOW435 completes short request authoring and read-only graph inspection.
Use `workflow_batch435.py prepare` to match registered scoring jobs without manual pair assembly.
Use `workflow_batch435.py inspect --text` to separate dependency waits from actionable failures.
See [the tested workflow](Research/Plans/WorkflowPreparation435.md).

- [ ] Measure authoring-to-ready time before adding another workflow abstraction.
  STANDARD443 uses the qualified transaction option. Preserve individual checks and explicit job IDs.


## P0 — Recovery release and Standard review — REVIEW432

Owner: Maximum-mini-NUIAK. See [the review and branch requirements](Research/Plans/Review432.md).

- [ ] Resolve the Maximum-mini-TTR HCF evidence storage budget before a recovery successor.
  `native431-recovery` exhausts with `resourceContended`. Restoration is not started. The failing check dispatches no input.
  Preserve the attempt. Verify offload and `storage-budget.json` before explicit resumption. `native433-admit` remains blocked.
- [ ] Bind the tested GATE437 successor after TTR storage permits a recovery successor.
  The gate preserves the original byte hash and compares complete marker values after serialization.
  Maximum-mini-TTR reports 31.3 GiB retained against 512 MiB. The coordinator stores the offload request at cursor 887.
  Forwarding is not confirmed. Do not remove peer evidence or bypass restoration.
- [ ] Review the 6 native capture receipts and downstream data checks. Preserve original groups and development exclusions.
  Failed or interrupted gate attempts need explicit review. Do not bypass restoration or revoke history.

## Graph viewer follow-up — GRAPH430

Owner: Maximum-mini-NUIAK. The 2D read-only companion runs on loopback port 8766.
The original dashboard and runner remain on port 8765. See [the implementation plan](Research/Plans/ExperimentGraphViews430.md).

- [ ] Select a private repository before publishing future internal dashboard work.
- [ ] Consider same-port integration only during an approved idle maintenance window.
- [ ] Keep 3D views deferred until the 2D views receive maintainer review.


## ADR review and disposition

Use the [prioritized ADR index](Research/ADR-Index.md). Historical findings have a separate archive index without moved source files.

- [ ] Use existing templates and typed graph conditions before proposing another workflow framework.
- [ ] Reconcile ADR-0019 with current TTR capabilities before defining new renderer implementation.
- [ ] Verify delivery receipts before updating the older ADR-0023 implementation status.


## Standard reserve and preparation — RESERVE429

Owner: Maximum-mini-NUIAK. Plan: [reserve comparisons](Research/Plans/Reserve429.md).

- [ ] Review B405-230 and B405-231 before selecting the next independent iOS correction.
- [ ] Bind workflow runtime comparisons to real artifacts through existing templates.
- [ ] Report ready duration and conditional duration separately. The 48-hour target remains unmet until evidence supports it.


## Queue cleanup and task preparation — BLOCKERS428

Owner: Maximum-mini-NUIAK.

The replacement map retires 25 original DETECTOR422 entries after verified v2 completion.
It links 54 PROFILE424 entries to PROFILE425. These retire only after each replacement completes.
All specifications, attempts, checkpoints, and results remain unchanged. The runner remains active.

- [ ] Review the remaining HCF402 small-control and wide-control chains for completed replacements before new execution.
- [ ] Review HCF389 next-actions against later proposal results before retaining its old dependency.
- [ ] Qualify Sillycon-TTR repair `2657ec7aac2da5d324b0d3576c58836650ef24e9` through an immutable consumer recovery successor.
  REPAIR431 builds and verifies the exact revision in 191.832 s. The idle candidate is replaced with its previous app preserved.
  Exact-target preflight passes. Job `native431-recovery` is approved for the existing runner; capture qualification remains pending.
  See [Repair431](Research/Plans/Repair431.md). Do not clear the guard or qualify the 6 capture drafts before restoration passes.
  Source and published report reviewed on 2026-10-18. TTR reports 3 successful snapshots across reconnect and restart.
  Its tested candidate includes unrelated changes. Maximum-mini-NUIAK must qualify the exact published repair before releasing capture dependencies.
  Retained sequence2 command and PNG metadata returned through coordinator request `nuiak-repair430-source-review-20261018-v2`, stored at cursor880.
  This replaces the unstructured v1 at cursor877. Forwarding and recipient acknowledgment remain separate from storage.
- [ ] Prepare the next batch from existing templates and retained inputs. Name missing producers separately from missing adapters.


## P0 — Review supplemental proposals (SUPPLEMENTAL427)

Owner: Maximum-mini-NUIAK. Plan: [fixed supplemental comparison](Research/Plans/Supplemental427.md).

- [ ] Review the 8 queued comparisons. Reject any lost success or new wrong selection; report Standard first.
- [ ] Keep no-focus outcomes separate. Do not infer safe navigation from a development comparison.
- [ ] Compare measured-box crop results when complete, including the previously lost TTR positive crop.
- [ ] Qualify TTR's repair after source and regression evidence arrive. Keep the native recovery guard until restoration passes.

Do not create scheduled tasks without explicit maintainer consent. This rule is recorded in AGENTS.md.

## P0 — Preserve gains before combining detectors (REVIEW426)

Owner: Maximum-mini-NUIAK. Report: [matched review](Research/Plans/MatchedReview426.md).

- [ ] Review completed measured-box scores against jitter, including the lost TTR positive crop. Do not choose a correction from incomplete comparisons.
- [ ] Verify PROFILE425 producer receipts after dispatch. Consumers stay blocked until verified outputs exist.
- [ ] Audit why all 32 matched tab labels become `primaryButton`. Check training labels and checkpoint class mapping before new training.
- [ ] Sillycon-TTR: inspect the retained app logs and deliver the snapshot-return repair with regression evidence.

The scoped detector recovers row selections but loses 6 Standard successes and adds 5 wrong HCF selections on retained conditions.
Jitter improves retained crops but loses 1 positive crop in the original TTR set. Neither candidate replaces the baseline.

## P0 — Repair producers before retrying exhausted work (CONTINUATION425)

Owner: Maximum-mini-NUIAK. Plan: [attempt review and producer repair](Research/Plans/Continuation425.md).

- [ ] Review PROFILE425 producers and matched training successors. They repair missing dependencies, not insufficient runtime.
- [ ] Compare PROFILE425 Standard results against retained successes. Keep all shipped models unchanged.
- [ ] Sillycon-TTR: inspect the snapshot logs and return the repair revision with regression evidence.
- [ ] Maximum-mini-NUIAK: qualify restoration after that repair, then admit native capture successors.

The audit finds no useful qualified checkpoint continuation. The only timeout already has a completed successor.
The 74 other failed attempts need repair or successor reconciliation, not automatic additional runtime.
Keep continuations below ordinary ready work. Preserve all checkpoints and original attempts.

## P0 — Repaired native capture and Standard profile transfer (REPAIR424)

Owner: Maximum-mini-NUIAK. Plan: [recovery and profile transfer](Research/Plans/Repair424AndProfileTransfer.md).

- [ ] Sillycon-TTR: repair the screenshot-return timeout found by `tier-native-recovery424`. Runner delivery succeeds; the client times out after 30 s.
- [ ] Maximum-mini-NUIAK: qualify a fresh recovery successor after that repair. Cleanup passes, but Standard restoration remains unverified.
- [ ] Admit native capture successors only after verified Standard restoration. Preserve failed attempts and the recovery guard.
- [ ] Execute B405-124 through the existing templates. Compare Standard-only, joint-profile, and HCF-only training with matched exposure.
- [ ] Compare all candidates against retained successes before selecting another correction. Keep Standard production unchanged.
- [ ] Fill the remaining overnight capacity with supported corpus stages. Do not report diagnostic timeout ceilings as ready duration.
- [ ] Qualify 6 prepared native recipe shards after recovery. They target 144 development frames across 6 layout groups.

The profile comparison has 4,432 paired identities across 255 training groups and unchanged development membership.
Its estimated training duration is 80 min. This does not establish a full night of useful ready work.
All 3 fits and 51 scoring jobs are registered and approved. The continuous runner resumes after recovery fails.
The dispatch repair passes focused tests. No active worker source changes are part of this preparation.

## P0 — Nightly review follow-up (NIGHTLY423)

Owner: Maximum-mini-NUIAK. Report: [Nightly review](Research/Plans/NightlyReview423.md).

- [ ] Qualify Sillycon-TTR revision `4b2f49c0b1c62f07090cd1acec47bea3bfa824ac` on Maximum-mini before native recovery.
- [ ] Verify source identity, helper identity, retained observations 16/17, and the bounded restoration receipt.
- [ ] After recovery passes, register capture successors. Keep the guard until verified restoration.
- [ ] Review OFFSET421 matched scores before choosing another crop correction. The jitter fit completes 30 epochs; accuracy remains pending.
- [ ] Review DETECTOR422-v2 against the 16 completed baseline jobs. Keep detector geometry and crop selection results separate.
- [ ] Use the completed B405-230/231 reports to prepare reviewed unmatched-box labels. Both reviews remain inconclusive for threshold adoption.

Sillycon-TTR messages 852/854 supply the repair revision and peer checks. Independent consumer qualification remains open.
The coordinator stores the NUIAK response at cursor 855. This does not establish forwarding or native recovery.
The review registers 12 cached diagnostics through T42. The background runner owns execution.
Standard remains primary. HCF remains optional. No model or runtime setting changes.

### Review-process improvements

- [ ] Add a bounded receipt index for nightly reports. Use completion timestamps and attempt identities, not file modification times.
- [ ] Show superseded failures separately from current blockers. Preserve every original attempt.
- [ ] Show ready duration by research track and the next dependency. Job count alone does not establish overnight coverage.

These are preparation tasks, not authority to change active worker code during this review.

## P0 — Training preparation and detector qualification

Owner: Maximum-mini-NUIAK. Plans: [proposal errors](Research/Plans/TrainingProposalErrors.md) and [template source review](Research/Plans/Template418QualificationReview.md).

- [ ] Review OFFSET421 training and matched scoring outputs against the retained mixed model. Require zero lost successes and new wrong selections.
- [ ] Build T64 comparison bundles from completed OFFSET421 receipts. Report each native family, retained condition, and profile separately.
- [ ] Review DETECTOR422 training and 40 matched checks. Separate scoped proposal improvement from general UI detector qualification.
- [ ] If scoped proposals help, test supplemental proposal use against retained Standard, artwork, and no-focus successes.
- [ ] Prepare exhaustive annotations before training a replacement general UI detector. DETECTOR422 qualifies 3 control classes only.
- [ ] Review T90 checkpoint evidence. Require restoration parity before any resumed detector run.
- [ ] Correct T67–T86 integration gaps before scientific admission. Do not treat synthetic software tests as model evidence.

The 7 approved `proposal419` diagnostic jobs complete. Results are recorded in CompletedTasks.md.
OFFSET421 qualifies 50 unique training correspondences. Its 3 corrected preparation jobs complete with unchanged development data.
The matched batch defines 2 training jobs and 34 dependent scoring jobs. See [the plan](Research/Plans/Offset421AndRefinementReview.md).
T89 software checks do not establish completed detector qualification. T67 does not currently train a YOLO model.
DETECTOR422 v2 preparation passes the resident T89 dataset consumer with explicit training-only diagnostics.
The original proposed calibration split shares layout ancestry and is revoked before training.
The successor retains 21 unique training images across 5 source groups and 3 layouts. All development groups stay excluded.
OFFSET421 results remain pending at this review. Do not choose a new crop correction before matched scoring finishes.
Do not bulk-admit the proposed novel experiments. Their exact missing requirements appear in the source review.

## P0 — Qualify conservative proposal selection

Owner: Maximum-mini-NUIAK. Plan: [Matched consumer comparison](Research/Plans/TTRMatchedConsumer.md).

### Immediate blocker — B405-220 native capture recovery

B405-220 through B405-228 register 45 jobs using existing templates. They target 34 new development frames across 4 groups.
The button capture fails before collecting frames. TTR reports an ambiguous Standard-setting observation after 3 inputs.
The helper and Fixture hashes match their qualified versions. Postflight reports clear ownership, but NUIAK cannot verify restoration.
The recovery guard remains. The other 4 capture approvals are revoked; the 40 analysis jobs wait on verified capture inputs.

- [ ] Sillycon-TTR: replay the retained observations and deliver the qualified route correction for Maximum-mini consumer verification.
- [ ] Maximum-mini-NUIAK: pin the corrected TTR helper and run the qualified v2 recovery through the background queue.
- [ ] Maximum-mini-NUIAK: register explicit successors for failed captures after verified recovery. Do not overwrite attempts.
- [ ] Maximum-mini-NUIAK: approve capture jobs at an idle dispatch boundary to avoid the observed approval race.
- [ ] Maximum-mini-NUIAK: register T66 comparisons after the new T57 reports and verified receipts exist.

The legacy recovery job is registered but not approved. The current gate rejects its v1 specification.
The v2 adapter passes 8 software checks and positive/negative isolated queue checks.
Job `tier-native-recovery-v2` explicitly waits for the qualified TTR route repair. No unchanged route retry is approved.

Update, 2026-10-17: Sillycon-TTR reply at cursor 832 confirms that no corrected build exists yet.
Maximum-mini-NUIAK fetched TTR source through `e40eb22b`. Its observation matcher still rejects the retained pair.
The running Maximum-mini-TTR app remains the older build under `.local-work/nuiak-hcf362/DerivedData`.
The assignment to `TVTestRig-Max-Astra` was incorrect. The maintainer assigns the repair to Sillycon-TTR.
The mistaken worker confirms its work stopped. Its patch and candidate remain preserved, unadopted review material.
Sillycon-TTR reports 31 checks and a verified Standard/HCF restoration. Maximum-mini verification remains pending.
Maximum-mini-NUIAK receives and hash-verifies the 4 offered result files from messages 841, 843, and 845.
The exact retained pair and optional local patch are published through the approved share with size and SHA-256.
Owner correction and handoff message `nuiak-hcf-owner-correction-20261018-v1` is stored at cursor 847.
Sillycon-TTR still needs to replay the exact pair and deliver its source revision or reviewed delta.
Resume after Sillycon-TTR returns that evidence and Maximum-mini-NUIAK qualifies the consumer build.
Then admit a fresh recovery successor before capture successors. Preserve the guard and Standard models.
Software checks do not verify native recovery. Keep the capture guard until the native receipt passes.
The route failure is now traced to irrelevant clipped-label OCR variation on Display.
Both observations agree on page, focus, Standard value, and the complete prefix through Focus Style.
Sillycon-TTR owns the narrowly tested observation-matching correction, not another capability check or blind retry.
The exact reproduction and acceptance checks are stored in coordinator message at cursor 827.
Message `nuiak-ttr-native-recovery-20261017-v1` is stored at cursor 825. Forwarding remains unverified.
No user action is identified yet. Do not ask the user to toggle settings without a specific verified need.

- [ ] Prepare independent native groups for the 25% model with Standard detection and optional HCF ring support.
- [ ] Include verified no-focus scenes and decorative distractors. Freeze groups before collecting new results.
- [ ] Retain the separate TTR artwork failure as a blocking replacement test.
- [ ] Review the 44 additional unmatched iOS detections before claiming improved precision.
- [ ] Integrate qualified B405-196 offsets into the resident crop trainer after correspondence review. See [verified inputs and checks](Research/Plans/TrainingProposalErrors.md).

B405-196 has 40 admitted training frames, 5 groups, and 21 unique image hashes.
T87 and T88 now prepare training-only inputs and measure errors. Matched training integration remains open.
B405-229 completes and rejects suppression: 17 fewer unmatched boxes cost 41 labeled matches, with no gains.
See CompletedTasks.md. Do not repeat this failed correction or change Standard.

The lower-exposure model is rejected. Completed work moves to CompletedTasks.md.
The threshold and policy batches are complete. The 25% model gains 4 Standard selections without losses in the policy test.
Independent-group qualification remains necessary. This does not approve the model or runtime policy.
These are bounded diagnostics, not an overnight training workload. Standard remains unchanged.
The 50% exposure proposal stays deferred because both tested native doses produce excessive artwork false positives.

## TTR chat review — 2026-10-17

Maximum-mini-NUIAK reads TTR updates through cursor 807. TTR's corrected priorities message supersedes its invalid first message.
The offered scroll-observer archive already exists locally. Its 16,698,609 bytes and full SHA-256 match the offer.
TTR reports 0 detected focused crops, 4 missed focused crops, 7 false positives, 8 true negatives, and 1 abstention.
These are 20 Standard-profile development crops from 4 frames, not HCF accuracy or a current release comparison.

- [ ] Confirm TTR can access the supplied source identities and exact mapping before implementation. Preserve Standard and navigation restrictions.

Replies `nuiak-ttr-review-20261017-v1` and `nuiak-ttr-review-20261017-source-v1` are stored at cursors 809 and 811.
Forwarding and recipient acknowledgment remain unverified. No new execution authority or capture request was sent.
TTR also proposes temporal-motion and scale/scroll parity investigations. These proposals do not create approved jobs.

### Matched consumer comparison: preparation and acceptance

The archive's model contract already links the delivered experimental bundle to checkpoint `hcf375c-70-crop-train`.
Its reference receipt records loaded-model, source-model, helper, backend, and input identities.
The earlier identity blocker was too broad. Check whether the October 17 rerun changed these identities; do not request existing evidence again.

- Maximum-mini-NUIAK verifies the 4 images and 20 native body records, including hashes, actual Standard profile, and observed focus labels.
- Preserve related frames as development groups. Do not admit these inspected failures to training or final audit.
- Reproduce the baseline crops and retained RGB hashes before interpreting score changes.
- Compare the baseline and mixed candidate on identical membership, body boxes, and production preprocessing.
- Keep crop thresholds 0.85 and 0.7 distinct from the frame selection rule. Report both explicitly.
- Report per-case gains, losses, wrong targets, misses, abstentions, and timing. Retained successes remain a separate required comparison.
- Separate PyTorch comparison from Core ML/Vision parity. A changed backend cannot establish model-only improvement.
- Reuse existing templates where their input contracts fit. Any archive-to-template adapter remains an explicit preparation dependency.

Future TTR handoffs should keep model, helper, input, label, preprocessing, and result identities in one manifest.
Measure preparation time and missing-field round trips. Request more capture only when existing evidence cannot answer the next question.
Follow-up `nuiak-ttr-matched-followup-20261017-v1` corrects the earlier blocker without assigning new TTR execution.

Matched scoring is complete. The candidate detects 4 focused crops but adds 9 false positives against the delivered checkpoint.
Neither model selects correctly on these 4 frames. All 20 RGB hashes match TTR's records.
Both Vision cohorts pass the fixed 0.01 replay tolerance. This does not establish deployment accuracy.
Results message `nuiak-ttr-matched-results-20261017-v1` is stored at cursor 815. Forwarding remains unverified.

## P0 — FOCUS-PIPELINE-PILOT and immediate follow-up

Owner: Maximum-mini-NUIAK. Maintainer priority: pilot first, then this follow-up before further model variants.
Plan: [Detector boxes to focus selection](Research/Plans/DetectorFocusPipelinePilot.md).
Status: the pilot completes. The candidate gets 16/24 correct per profile using detector boxes, versus 4/24 for the retained baseline.
The corrected 13-job graph completes. A new Standard diamond-decoration loss blocks replacement.
All 15 cached comparisons complete. Reject older-model fallback because it adds 3 wrong selections.
HCF-only ring preference preserves tested decisions, but the Standard regression remains. No model changes.
B405-204 admits 8 cached geometry audits. They measure box errors and paired score changes before training preparation.
See [the fixed policy plan](Research/Plans/DetectorFocusPolicy.md), B405-202 and B405-203.
See [the findings and follow-up](Research/Plans/DetectorFocusFollowup.md). These are short diagnostics, not overnight capacity.
Keep Standard unchanged and HCF optional. The detached runner owns experiment execution.

| Task | Work | Acceptance and decision | Dependency |
| --- | --- | --- | --- |
| [ ] FOCUS-PIPELINE-NEXT-01 | Separate wrong classes from missing control geometry. | Reuse B405-188 results where membership matches. Decide whether detector repair needs class or box improvements. | Pilot result; compatible cached detector outputs. |
| [ ] FOCUS-PIPELINE-NEXT-02 | Measure realistic box errors and sensitivity. | Compare unchanged boxes with measured errors. Preserve the tall-control regression and previous successes. Decide whether B405-196 training is justified. | Pilot correspondence checks; development geometry. |
| [ ] FOCUS-PIPELINE-ERROR-PREP | Prepare realistic training box errors for B405-196. | Pin training-only proposal/body matches. Qualify a deterministic sampler and equal exposure against generic jitter. Keep inspected failures out of training. | Maximum-mini-NUIAK supplies verified training matches and a qualified sampler. |
| [ ] FOCUS-PIPELINE-RING-VERIFY | Verify HCF-only ring preference on separate groups. | Preserve Standard and no-focus decisions. Require no new wrong selections or lost successes. Do not claim a Standard correction. | Pin independent native groups and compatible T57 reports before queue admission. |
| [ ] FOCUS-PIPELINE-NEXT-04 | Prepare and verify TTR observation-only consumption. | Match loaded model, preprocessing, boxes, and decisions against NUIAK references. Report runtime differences separately. | Offline pilot result; exact receiving TTR owner and interface. |
| [ ] FOCUS-PIPELINE-NEXT-05 | Review all branches and choose the next correction. | Identify proposal, geometry, classification, or integration failures. Require previous-success checks before any replacement decision. | Complete matched reports or explicit unavailable branches. |

Estimate: 2–4 h for pilot preparation and qualification; 4–8 h total including local follow-up preparation.
These estimates exclude new capture, training, background scoring, and TTR execution.
Register qualified branches incrementally. Do not wait for TTR to finish independent local comparisons.
Reuse existing backlog records rather than duplicating their experiments.

## DISCOVERY417 — additional hypotheses and research sources

Owner: Maximum-mini-NUIAK. [Tests and source recommendations](Research/Plans/ResearchDiscovery417.md).
B405-195 through B405-198 add teacher preservation, realistic proposal errors, scene diversity, and isolated crop context.
Each record names its control, decision, and missing adapter or input. These are not ready execution jobs.
Prioritize realistic proposal errors after correspondence checks. Reuse PAPER417-SUBSET for scene diversity.
Use community discussions to find ideas, then verify original sources before adopting methods.

## INSIGHTS417 — follow-ups from native-control training

Owner: Maximum-mini-NUIAK. These 6 investigations are preparation tasks, not ready execution jobs.
Use existing templates and retain completed controls. Keep Standard primary and HCF optional.

| Priority | Record | What does it test? | What will it decide? |
| --- | --- | --- | --- |
| P0 | B405-193 | Raw versus corrected boxes on the tall-control regression. | Whether geometry repair can preserve the native-training gains. |
| P0 | B405-189 | Native exposure at fixed total training exposure. | The smallest useful native quota that preserves artwork successes. |
| P1 | B405-190 | Transfer to a native family excluded from training. | Whether shared effects transfer or each family needs examples. |
| P1 | B405-191 | Frozen encoder versus full crop training. | Whether a smaller update preserves more previous successes. |
| P1 | B405-192 | Worst-family versus mean-loss checkpoint selection. | Whether checkpoint selection hides weak families. |
| P1 | B405-194 | Persistent selected-tab styling while focus moves elsewhere. | Whether the new model confuses selection with focus. |

B405-189 and B405-190 share PAPER417-SUBSET. They do not need separate membership scripts.
B405-193 needs exact checkpoint, proposal, mapping, and capture references plus a verified unchanged replay.
B405-191 needs a qualified freeze variant. B405-192 needs retained epoch checkpoints and separate selection and comparison groups.
B405-194 extends B405-027/B405-167. Reuse their evidence before requesting new Maximum-mini-TTR captures.
Diagnostics retain 800 s and 100 MB limits. Freeze training settings and explicit budgets before admission.
No capture, training, promotion, or runner change occurs from these planning entries.

## AUDIT417 — priorities from completed comparisons

B405-177 now completes: 42/48 known-box selections, but 0/48 mapped selections and 1 lost raw-proposal success.
Do not promote the candidate. Prioritize native proposal coverage and reusable subset preparation.
B405-188 adds 6 approved class-free comparisons to distinguish iOS class errors from missing geometry.
See the audit follow-up for how these findings change the paper-inspired experiments.

Owner: Maximum-mini-NUIAK. [Audit and next decisions](Research/Plans/ExperimentAudit20261017.md).
Complete B405-177 comparisons first. Prioritize ENG405-06 and PAPER417-SUBSET for the next implementation tranche.
Run 013 gains 228 detections but loses 66 previous successes. Native tvOS results show class and proposal failures.
Registered and approved: 15 cached diagnostic jobs under B405-185 through B405-187.
These jobs test position, geometry, and overlapping proposals. They do not provide an overnight workload.
Keep Standard unchanged. The detached runner owns execution.

## PAPER417 — research-driven experiment preparation

Owner: Maximum-mini-NUIAK. [Controls, budgets, and template contracts](Research/Plans/ResearchPapers20261017.md).
Catalog records B405-180 through B405-184 are planning records, not executable jobs.
Keep current execution unchanged. Standard remains primary; HCF stays optional.

| Priority | Task | What does it test or enable? | Acceptance |
| --- | --- | --- | --- |
| P2 | PAPER417-PAIRS | Build within-screen target and distractor groups for B405-180. | Preserve crop hashes and roles; reject conflicting focus and cross-scene pairs. |
| P1 | PAPER417-STATES | Separate no-focus truth, missing proposals, and unknown observations for B405-182. | Positive and negative queue tests preserve distinct truth states and reject stale observations. |
| P0 | PAPER417-SUBSET | Produce reproducible subsets for B405-181 and B405-184. | Preserve group separation and coverage; reject impossible quotas; demonstrate reuse with 2 descriptions. |
| P2 | PAPER417-RANK | Compare binary loss with an added focus-ranking loss for B405-180. | Qualify the binary control and reject invalid pairs before a matched candidate fit. |
| P2 | PAPER417-IMPORT | Review and normalize independent iOS labels for B405-183. | License, provenance, taxonomy, overlap, and bounded sample checks pass before admission. |

Reuse B405-059 for prior sampling evidence and B405-004/B405-058 for prior no-focus evidence.
Complete DETECTOR417 and NCTRL417 reviews before freezing new training controls.
Assign template IDs during implementation. Do not create queue specifications with unsupported template names.


## DETECTOR417 — native detector work across tracks

Owner: Maximum-mini-NUIAK. Updated 2026-10-17. [Plan](Research/Plans/NativeDetector20261017.md).

- Done: T55 prepares development labels from retained native sources with verified hashes, groups, taxonomy, and bounds.
- Done: T56 reuses existing detector inference and T42 matching without requiring an older scorecard.
- Registered and approved: 18 iOS jobs and 9 tvOS jobs. The detached runner owns execution.
- B405-178: compare Run 009 and Run 013 on 180 iOS frames across 45 qualified families.
- B405-179: score 24 tvOS images across 6 development groups. Compare class-aware and class-agnostic outcomes.
- Partial review at 20:28 UTC: 10 jobs complete. Run 013 gains 108 and loses 34 detections on the first 90 iOS frames.
- Native PyTorch execution passes on those groups. Remaining layout and tvOS comparisons remain pending.
- Software validation passes 32 tests. Preserve the 34 regression cases before planning a detector repair.
- Next: combine detector failure rankings with completed NCTRL417 results. Select matched repairs across qualified tracks.
- Training blocker: Maximum-mini-NUIAK must qualify the detector training adapter and freeze repair membership before new detector fits.

## ACTIONS417 — HCF jitter comparison and queue fixes

Owner: Maximum-mini-NUIAK. Updated 2026-10-16. [Plan and results](Research/Plans/Actions417.md).

- Done: approval no longer waits for running jobs; post-run failures name their cause; training reports have schema tests; the trainer has an exposure control (`repeat`) and records its exposure.
- Done: the matched-exposure control shows that jitter, not extra exposure, explains the box tolerance (B405-138, 139).
- Done: on identical ring proposals, jitter is correct on all 8 focused HCF frames that have a proposal, with 0 lost (B405-140).
- Done (P0): native ring pixels on the 28 missed frames (B405-147, T52). The ring is bright on all 28; the kernel's side-support gate fails on the short left and right sides. The self-check passes 8/8.
- Done (P0): short-side sampling (B405-148) recovers 0 of 28 and loses nothing. A debug kernel shows the real cause: the low-quality 960 px drawing erases the thin ring on some sides (support 0.00).
- Done (P0): high-quality drawing (B405-150) recovers 0 of 28 and loses nothing on native frames. It restores the bottom ring side, but the short left and right sides still fail. It loses 1 of 52 synthetic proposals (B405-151).
- Done: the combined kernel setting (B405-152, B405-153) recovers 11 of 28 missed focused HCF frames with 0 native losses and 0 Standard or no-focus proposals. It loses 1 synthetic proposal that was already wrong, so the rule confirms it contradicted.
- Done: the maintainer accepted the synthetic loss. Jitter on mapped combined proposals (B405-154) is correct on 19 of 36 focused HCF frames, against 8 on frozen proposals, with 0 lost, 0 wrong, and Standard unchanged. Raw combined boxes give 11 wrong selections because ring bounds are not body bounds.
- Done: B405-154 confirmed supported on the mapped source. The 17 frames without a proposal all fail the inner moat test, because the ring is 1 px thicker than the 3 px search window.
- Done: B405-155 to B405-157. The inner kernel gives proposals on 36 of 36 focused HCF frames, and jitter selects 36 of 36 correctly on mapped proposals. It adds 0 Standard or no-focus proposals, and synthetic frames rise to 72 of 264 with 0 lost.
- Done: all 16 gained synthetic proposals map to the focused control (IoU 0.65 to 0.98). The unused light-background capture gets 0 proposals from every kernel, because its background is above the 160 brightness threshold (B405-158, B405-161).
- Done: B405-160, B405-162, and B405-163. The new 140 to 180 pt layouts pass for every kernel, so they do not separate the kernels.
- Done (GROOM-20261017 batch 1): on independent 120 pt layouts the inner kernel proposes on 8 of 8 focused HCF frames (frozen 0), jitter selects 8 of 8, and 6 no-focus frames abstain. HCF-only training loses Standard (2 of 36), confounded by exposure.
- Done (batch 2): jitter is seed-stable on inner proposals (44 of 44 at seeds 372 and 373, 0 wrong). Jitter fails native tab focus (0 of 16); the retained model gets 12 of 16 with 0 wrong. HCF-only training with matched exposure: Standard 28 of 36 (inconclusive).
- Done (batch 3): neither crop model handles native button, row, or tab focus (jitter 0 of 24; retained 6 of 24; 0 wrong). Native control crops are a training need.
- Approved: scoped TTR kernel proposal and native-control training use of B405-042/B405-167, with separate development groups.
- Handoff: v2 has a rejected status field. Corrected `nuiak-native-controls-20261017-kernel-v3` is stored at cursor 799 with exact readback.
- Forwarding and recipient acceptance remain pending.
- Native preparation complete: T53 admits 40 training frames across 5 groups and 48 new development frames across 6 separate groups.
- T05 and T54 pass production crop preparation and matched membership checks. Both fits use 7,200 samples per epoch and identical development.
- Existing execution: 48 NCTRL417 jobs cover capture, admission, crops, membership, baselines, 2 fits, and 30 candidate evaluations.
- Next review: compare per-family gains and losses, artwork retention, selected-tab negatives, and no-focus abstention. Apply the frozen decision rules together.
- Process: AGENTS.md now requires complete decision branches, batch exceptions, and useful ready duration across qualified tracks.
- Validation follow-up: 176 Swift tests pass with the timeout/cancellation test excluded after a sampled `NativeOwnedProcess.run` stall.
- Plan: [NativeControls20261017](Research/Plans/NativeControls20261017.md). Keep original captures and prior results unchanged.
- Pending decisions: 4 seed runs for B405-174 and capture approval timing. See Research/Plans/Groom20261017.md.
- T46 label and prediction adapters are implemented as T55 and T56. Native diagnostic jobs are registered under DETECTOR417.
- Next (P0): build the crop subset producer (B405-122), after its exact membership requirements pass.
- Next (P1): add detector and combined detector-first proposals for the 74 frames, after detector inference on them.
- Done (user-approved Step 5): jitter's box tolerance repeats at seeds 372 and 373. The proposal gain does not: both methods reach 8/8 on mapped proposals, and raw proposals vary by seed (B405-141–146).
- Next (P1): use jitter for the next HCF crop candidate, and evaluate it on mapped proposals, not raw outer-ring proposals.
- Engineering: approval during execution is live. Shared-module edits still need an idle runner, because adapter pins stay strict.

## STATUS-20261016 — Big Dog coordinator chat

Owner: Maximum-mini-NUIAK. Read 2026-10-16: cursors 758–788 (14 Sillycon-TTR forwards, none urgent).
Sent at the user's request: receipt through cursor 788 (state `read`, `work_accepted` false); replies `nuiak-status-20261016-receipts-v1` (cursor 789) and `nuiak-status-20261016-model293-v1` (cursor 791). Readback text matches. Both are `stored` with empty `read_by` and `provider_delivered` false, so TTR has not received them yet.
Our request at cursor 755 is still `stored` with no `read_by`, but TTR quotes it in message 762: keyboard ownership, non-affine geometry, and observer receipt are tracked follow-ups.

- Received and verified (size and SHA-256): `ttr-hcf-observer-20261015-reference.json` and the scroll-observer archive and summary, in `reports/work/TTR-INTAKE-20261016/`. The archive is not extracted.
- B405-086 (actual TTR inference) is confirmed supported: the observer receipt matches all 8 reference crops. `hcf396-14-ttr-verification` is superseded by `b405-086-receipt`.
- TTR asks NUIAK to keep Settings filled rows, Home tiles, and custom controls as separate families, with the actual profile as an independent label. Our B405-042/134 result agrees.
- TTR's custom Standard catalog gives TP 0, FN 4, FP 7 with the HCF crop model. That model is HCF-profile only; Standard frames are outside its domain.
- MODEL-DIST-02: TTR embeds models now and asks for artifacts, digests, macOS 14 support, and redistribution status. Its detector tree `86c16915…` differs from our recorded `86cc39b1…`; reconciliation is requested.
- Off-image proposals: TTR sees a box at y 2163 in a 2160 frame. NUIAK recommends rejecting boxes with no visible area and asks for the frames.
- EXP-REVIEW-04: TTR asks for a minimal intake schema and importer receipt for flagged review exports. NUIAK owns this; not started.
- Sent records and results: `reply-receipts*.json`, `reply-model293*.json`, `ack-788*.json` in `reports/work/TTR-INTAKE-20261016/`.
- Maintainer decision: per-artifact redistribution for embedded models.

## TEMPLATES413 — template builds for the open backlog

Owner: Maximum-mini-NUIAK. Started 2026-10-15. The user approves parallel template sessions.
Each session reserves 1 template ID, writes its own adapter and tests, plans the records it unblocks, and records results in Research/Plans/Backlog410.md.

| Wave | ID | Template | Unblocks | Session | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | T44 | Quota comparison (B405-041) | 38 records | t44-quota | Complete: B405-041 supported; family and theme quotas need a decision |
| 1 | T45 | Native button, row, and tab capture recipe | 27 records | t45-button-capture | Built and tested. Rows and tabs measured in both profiles, buttons in Standard only. User-approved B405-042 captures complete. HCF changes artwork only: button, row, and tab frames are identical between profiles (B405-042, B405-134 contradicted) |
| 1 | T46 | iOS native capture (ENG405-03) | 20 records | t46-ios-capture | Done: B405-031, 034, 035 supported. `swift test` hangs in Core ML tests that T46 does not touch |
| 1 | T47 | Temporal evaluation (ENG405-05) | 12 records | t47-temporal | Done: `temporal_pairs414.py` qualified on D1 and FOCUS366. B405-061 contradicted (no movement asymmetry). B405-063 inconclusive. 10 records wait for named producers (Backlog410.md). |
| 1 | — | Jitter crop preparation and T41 fresh-model mode (B405-118) | Crop robustness | geometric-jitter-crop-tr | Jitter training failed after 707 s: a parallel edit changed pinned `template_adapters395.py`. Successors requested |
| 2 | T48 | Representation comparison (B405-075–080, 114) | 7 records | representation-t48 | Done: B405-075 and B405-114 supported (larger context and aspect-fit lose most prior successes). B405-076–080 have exact requirements (Backlog410.md) |
| 2 | — | Small extensions: T10 6-bit (B405-128), T20 taxonomy (B405-125), T25 kernel settings (B405-119), Swift fallback (B405-127) | 1 record each | small-template-extension | Running (resumed after usage limit) |
| 2 | — | T46 rendered-body measurement | 7 records (B405-032, 033, 036–040) | t46-ios-capture | Done: B405-032 supported (34 of 48 families pass; toggle boxes 2 pt narrow). B405-033 and 036–040 still need strings, overlay, scroll, state fields, or decisions |
| 2 | T49 | T47 Settings-row scorer (B405-067, 068) and transition training (B405-126) | 3 records | t47-temporal | Done: B405-067 contradicted; B405-068 answered by ADR-0018; B405-126 inconclusive (gain +39 to +41 against a 7-case control seed range, but seed 43 loses 1 success); maintainer decision on the 0-loss rule |
| 2 | T50 | T42 extensions (fit, state, edge, suppression) and T50 Vision rectangles for the remaining detector-case records | 12 records | add-detector-case-match | Done: 6 answered (B405-013, 024, 029 supported; 018, 025, 028 contradicted). B405-022 inconclusive, needs presentation-layer bounds. B405-019, 020, 027, 030, 106 have exact requirements (Backlog410.md) |
| 3 | — | Later-model templates (B405-091–100) | 10 records | — | After their repairs and gates |

Data, not templates, blocks B405-122 and B405-124 (frozen membership files), the T07 and T11 data records, and the T37 native groups.
Decisions block B405-123 (CALIBRATION102) and the frozen family and theme quotas for B405-041.

Rule: parallel sessions edit shared pinned modules only while the runner has no current job (see the backlog-grooming skill).

Dashboard speed, 2026-10-15: a snapshot of 1,042 jobs takes 24–44 s. Full code-pin hashing in `research_approval.is_approved` takes about 9 s, and output checks without the display cache take most of the rest.
Done: the server returns the last snapshot at once and rebuilds it in the background. An action still waits for a fresh build.
Done at an idle boundary: code pins in `is_approved` and `research_trust.drift` use the stat-keyed display cache on the display path only. The runner keeps full hashing. A snapshot now takes 6–9 s cold and 1.5–1.7 s warm; a page loads in 0.03 s.
The dashboard shows a status line and Next steps at the top. Superseded jobs are in their own collapsed section, like completed jobs.

## BACKLOG410 — experiment conversion pipeline and grooming cycle

Owner: Maximum-mini-NUIAK. Updated 2026-10-15. [Plan and results](Research/Plans/Backlog410.md).
Use the [backlog-grooming skill](.agents/skills/backlog-grooming/SKILL.md) at each research session start and at the dashboard refill warning.
The BACKLOG405 table below is generated. Do not edit its rows by hand.

Answered: 25 records, including B405-002, 073, 074, 011–017, 021, 026, 107, 108, and 115–117, 129. See the results in BACKLOG410.
Codified: 12 experiments from PROGRAM384, S391, and HCF results are now catalog records B405-118–129 with named blockers.
Run `backlog_pipeline.py blockers` for the current ranking.

Next work, ranked by the records it unblocks:

| Priority | Work | Unblocks | Owner | Status |
| --- | --- | --- | --- | --- |
| P0 | Geometric-jitter crop preparation (T05 variant) and a T41 fresh-model mode (B405-118) | Crop robustness decision | Maximum-mini-NUIAK | Proposed session |
| Done | Detector-inference template T43 ([INFERENCE412](Research/Plans/DetectorInference412.md)) | B405-023, 121, 130 answered: keep 0.50 and 640 px | Maximum-mini-NUIAK | Complete |
| Done | Quota comparison template T44 (`scripts/quota_comparison413.py`). B405-041 supported: 0 admitted observations, 13 frozen deficits | 38 records | Maximum-mini-NUIAK | Adapter complete; quota decision below |
| P1 | NUIAK capture plan with `native_button` focus for buttons, rows, and tabs | 27 T03 records | Maximum-mini-NUIAK | Needs recipe version |
| P2 | iOS native capture adapter (ENG405-03) | 20 records | Maximum-mini-NUIAK | Needs adapter |
| P2 | `temporal-evaluation` adapter (ENG405-05) | 14 records | Maximum-mini-NUIAK | Needs adapter |
| P3 | Small single-record adapters: T25 kernel settings (B405-119), T20 taxonomy (B405-125), T10 6-bit (B405-128), Swift fallback entrypoint (B405-127) | 1 record each | Maximum-mini-NUIAK | Needs adapter |

Human reviews and decisions from the results:

- Review the 194 navigationBar and 297 textField boxes that overlap no label. Are they unlabeled objects? (B405-129)
- Review the label definitions of middle-right and top-left iOS labels, and of small labels (B405-116).
- Review pageControl label geometry. The model never matches it at IoU 0.5 (B405-115).
- Review button-role and wide-toggle label definitions (B405-015, B405-016).
- Decide CALIBRATION102. It blocks the calibration-role threshold study (B405-123).
- Freeze or change the proposed family and familyTheme quotas in `Research/Experiments/focus-quotas413.json` (B405-041). Proposal: 50 training related groups each for artwork, buttons, rows, tabs, and keyboard; light and highContrast each 20 % of a family's groups. Also confirm that quota themes mean the Fixture system theme, not the light background of HCF371 cases.

Sent 2026-10-15 at the user's request: `nuiak-backlog410-ttr-needs-v1` to the coordinator, stored at cursor 755. The readback text matches. The coordinator status is `stored`, `read_by` is empty, and `provider_delivered` is false. TTR has not received it yet.
Receipt for cursor 747 sent: state `read`, read cursor 747, `work_accepted` false. Records: `reports/work/BACKLOG410/`.
Read, not acknowledged: TTR status 749, 752, and 754 (NAV-PROBE-01–04). TTR's outer-ring-v2 finds no supported ring under HCF in Settings, so its navigation trials refuse before input. TTR plans detector correction with hard negatives. It asks NUIAK for no work.
Decision needed: may an agent fetch the Maximum-mini-TTR checkout? The TTR rules forbid Git writes; NUIAK rules permit `git pull --ff-only`.

## RECONCILE409 — queue inventory, blockers, and deferred jobs

Owner: Maximum-mini-NUIAK. Updated 2026-10-15. [Plan and results](Research/Plans/Reconciliation409.md).

The queue has 805 jobs: 715 complete, 82 superseded, 6 blocked, 2 exhausted, and 0 ready.
The [mapping](Research/Experiments/reconciliation409.json) adds 66 superseded jobs to RECONCILE407. Successor output hashes pass verification.
Twelve stale approvals are revoked. No job fails only the approval code check, so no approval renewal is necessary.
The dashboard shows superseded jobs separately. The runner is active and waits for approved work.

Blocked jobs:

| Jobs | Missing input | Owner | Resume condition |
| --- | --- | --- | --- |
| `hcf402-factor-small-controls`, `hcf402-factor-wide-controls` | Fixture body geometry: `non_affine_transform` makes it unavailable for 72-point and wide controls in the HCF profile | Sillycon-TTR (Fixture source); Maximum-mini-NUIAK verifies locally | The Fixture reports measured geometry for all planned controls in both profiles. Then register `-r2` captures. |
| `hcf402-report-r2-small-controls`, `hcf402-report-r2-wide-controls`, `hcf402-measure-small-controls`, `hcf402-measure-wide-controls` | Completed captures from the row above | Maximum-mini-NUIAK | Register report successors on the `-r2` captures |
| `hcf396-14-ttr-verification` | Actual observer inference receipt | Sillycon-TTR | TTR runs the consumer check after Autonav qualification |

Deferred exhausted jobs. None of them only needs more time, so no EXTENSION408 restart is proposed:

| Job | Failure | Reason for deferral |
| --- | --- | --- |
| `hcf402-factor-small-controls` | `settle_timeout:missing_body` after 4 of 8 frames | Capture restarts are not supported. Needs the Fixture repair above. |
| `hcf402-factor-wide-controls` | `settle_timeout:missing_body` after 4 of 8 frames | Same as above |
| 18 other exhausted jobs | `timeout`, `process_failed`, or a missing evidence read | Superseded by completed successors in RECONCILE409 |

Withdrawn: `hcf389-next-actions`. Its adapter writes fixed blocker text that HCF396 results contradict. The HCF389 table below holds current requirements.

INTERVENTION410 (2026-10-15): the T41 adapter is done. B405-002 has 9 approved jobs. The estimated ready duration is about 1 min (9 jobs of about 5 s each).
The remaining adapters below produce the next ready jobs:

| Priority | Work | Unblocks | Owner |
| --- | --- | --- | --- |
| Done | T41 scored box intervention (`scripts/box_intervention410.py`) | B405-002: 9 jobs registered and approved as `agent:claude-intervention410` | Maximum-mini-NUIAK |
| Done | T42 `detector-case-match` adapter (ENG405-02, `scripts/detector_case_match411.py`) | 10 records (B405-011, 012, 014 to 017, 021, 026, 107, 108): 15 jobs registered and approved as `agent:claude-casematch411` | Maximum-mini-NUIAK |
| P2 | Fixture recipe and focus manifest qualification (B405-041) | 12 T03 tasks | Maximum-mini-TTR, with Maximum-mini-NUIAK |

PROGRAM384-D1 result: only the seed changes, and the training-view correct count varies by 45 of 1,392 views.
Seed 43 loses 3 baseline successes, and seeds 42 and 44 lose 0. The 16 development views do not vary.
Decision: a single-seed difference of 45 training views or fewer is not attributable to a correction. Keep the 0-loss rule until the maintainer decides.

Coordinator: the host answers on 2026-10-15. Messages 729–747 are read, but no acknowledgments are sent.
Sillycon-TTR asks for receipt confirmation of its Fixture06, Autonav, and Settings survey results (cursors 735–746).
These are status reports. They do not request NUIAK execution.

## RECONCILE407 — reviewed successors and control comparisons

Owner: Maximum-mini-NUIAK. Updated 2026-10-14.
[Reconciliation and next comparisons](Research/Plans/Reconciliation407.md).

The 22 stale jobs have 14 completed successors with verified output hashes.
Their old specifications and attempts remain unchanged. Withdraw these obsolete jobs from future execution.
The exact mapping is in [reconciliation407.json](Research/Experiments/reconciliation407.json).
The dashboard can still show these preserved records as blocked. Scientific closure does not rewrite queue lifecycle.

The maintainer approves both PROGRAM384 controls. Current checks pass for both exact specifications.
The 2 evaluations and 1 comparison report also have current approvals.
The detached runner owns these 5 jobs. Keep the retained seed-42 evaluation.

Open comparisons:

- PROGRAM384-D1: complete. See RECONCILE409 for the seed-variation result and decision.
- B405-002: separate crop alignment sensitivity from lost context on the tall-control case. T41 jobs `b405-002-*` are approved. The detached runner executes them.
- B405-104: qualify proposal transfer on the 28 missing HCF cases. Reuse B405-006 as the retained fallback baseline.
- Standard artwork counterpart: retain calibration roles and compare producer versions before any model experiment.

Sillycon-TTR supplies 1 new Standard pair and a duplicate HCF pair. Archive verification passes.
The two profiles use different producer revisions. They cannot isolate the causal effect of HCF.
The shared receipt is published and verified. Sillycon-TTR owns source cleanup.

## BACKLOG405 — scientific backlog and queue conversion

The maintainer approves HCF-first preparation on 2026-10-14. This supersedes the older preparation priority below.
HCF remains optional. Running jobs, existing approvals, Standard behavior, and final-audit boundaries stay unchanged.

[Plan](Research/Plans/ExperimentBacklog405.md) · [Scientific catalog](Research/Experiments/backlog405.json) · [Engineering tasks](Research/Experiments/engineering405.json).
The catalog contains 106 unresolved scientific tasks and 8 answered references. Engineering tasks do not count toward that minimum.
Tasks.md owns status. The catalog defines comparisons and requirements; the execution queue owns attempt status.
Every row expands through its matching catalog ID and shared profile. Parent task IDs preserve the existing roadmap links.

The first T40 job combines B405-001 and B405-002. It uses 9 verified reports covering 74 retained frames.
The maintainer approves `backlog405-native-failure-analysis` on 2026-10-14. The existing runner completes it in 0.321 s.
Output hashes pass verification. B405-001 identifies missing proposals as the first repair target. The tall-control correction remains open.
No ready duration follows from the 106-task count. Existing approved work remains independent.

<!-- BACKLOG:BEGIN generated by scripts/backlog_pipeline.py render-tasks -->
| ID | Owner | Status | Priority | Scientific question | Jobs | Result |
| --- | --- | --- | --- | --- | --- | --- |
| B405-004 | Maximum-mini-NUIAK | Needs data | P0 | No-focus rejection | – | – |
| B405-005 | Maximum-mini-NUIAK | Needs data | P0 | Decorative-border confusion | – | – |
| B405-007 | Maximum-mini-NUIAK | Needs data | P0 | Resolution transfer | – | – |
| B405-008 | Maximum-mini-NUIAK | Needs data | P0 | Settling sensitivity | – | – |
| B405-009 | Maximum-mini-NUIAK | Needs data | P0 | Complete-pipeline calibration | – | – |
| B405-010 | Maximum-mini-NUIAK | Needs data | P0 | Independent HCF audit | – | – |
| B405-019 | Maximum-mini-NUIAK | Needs data | P1 | OCR-assisted classification | – | – |
| B405-020 | Maximum-mini-NUIAK | Conditional | P1 | Targeted iOS repair | – | – |
| B405-022 | Maximum-mini-NUIAK | Needs decision | P1 | Focused-body localization | 2/2 | inconclusive |
| B405-027 | Maximum-mini-NUIAK | Needs data | P1 | Selected tabs versus focus | – | – |
| B405-030 | Maximum-mini-NUIAK | Conditional | P1 | Targeted tvOS repair | – | – |
| B405-033 | Maximum-mini-NUIAK | Needs data | P2 | Long and localized text | – | – |
| B405-036 | Maximum-mini-NUIAK | Needs data | P2 | Sheets and dialogs | – | – |
| B405-037 | Maximum-mini-NUIAK | Needs data | P2 | Scrolling and clipping annotations | – | – |
| B405-038 | Maximum-mini-NUIAK | Needs data | P2 | Generated control states | – | – |
| B405-039 | Maximum-mini-NUIAK | Needs data | P2 | Independent iOS layout families | – | – |
| B405-040 | Maximum-mini-NUIAK | Conditional | P2 | Synthetic-to-real transfer | – | – |
| B405-043 | Maximum-mini-NUIAK | Needs data | P2 | Controlled artwork exchange | – | – |
| B405-044 | Maximum-mini-NUIAK | Needs data | P2 | Movement and content contrast pairs | – | – |
| B405-045 | Maximum-mini-NUIAK | Needs data | P2 | Parent selection and child focus | – | – |
| B405-046 | Maximum-mini-NUIAK | Needs data | P2 | Keyboard focus coverage | – | – |
| B405-047 | Maximum-mini-NUIAK | Needs data | P2 | Nested navigation coverage | – | – |
| B405-048 | Maximum-mini-NUIAK | Needs data | P2 | Occlusion and overlays | – | – |
| B405-049 | Maximum-mini-NUIAK | Needs data | P2 | Source-derived layouts | – | – |
| B405-050 | Maximum-mini-NUIAK | Conditional | P2 | Generation scale | – | – |
| B405-052 | Maximum-mini-NUIAK | Needs data | P1 | Growth-preserving representation | – | – |
| B405-053 | Maximum-mini-NUIAK | Needs data | P1 | Shadow context | – | – |
| B405-054 | Maximum-mini-NUIAK | Needs data | P1 | Native shading | – | – |
| B405-056 | Maximum-mini-NUIAK | Needs data | P1 | Peer context | – | – |
| B405-057 | Maximum-mini-NUIAK | Needs data | P1 | Single-control scenes | – | – |
| B405-058 | Maximum-mini-NUIAK | Needs data | P1 | No-focus Standard scenes | – | – |
| B405-059 | Maximum-mini-NUIAK | Conditional | P1 | Failure-targeted sampling | – | – |
| B405-060 | Maximum-mini-NUIAK | Conditional | P1 | HCF-assisted Standard training | – | – |
| B405-062 | Maximum-mini-NUIAK | Needs data | P1 | Content-only negatives | – | – |
| B405-063 | Maximum-mini-NUIAK | Needs decision | P1 | No-op actions | 1/1 | inconclusive |
| B405-064 | Maximum-mini-NUIAK | Needs data | P1 | Scrolling separation | – | – |
| B405-065 | Maximum-mini-NUIAK | Needs data | P1 | Animated backgrounds | – | – |
| B405-066 | Maximum-mini-NUIAK | Needs data | P1 | Repeated identities | – | – |
| B405-069 | Maximum-mini-NUIAK | Needs data | P1 | Capture timing sensitivity | – | – |
| B405-070 | Maximum-mini-NUIAK | Conditional | P1 | Targeted temporal repair | – | – |
| B405-076 | Maximum-mini-NUIAK | Needs data | P3 | Position transfer on new structures | – | – |
| B405-077 | Maximum-mini-NUIAK | Needs data | P3 | Scale-aware representation | – | – |
| B405-078 | Maximum-mini-NUIAK | Needs data | P3 | Screen-level selection | – | – |
| B405-079 | Maximum-mini-NUIAK | Conditional | P3 | Alternative image features | – | – |
| B405-080 | Maximum-mini-NUIAK | Conditional | P3 | Unified focus detector | – | – |
| B405-082 | Maximum-mini-NUIAK | Needs data | P0 | Complete pipeline latency | – | – |
| B405-083 | Maximum-mini-NUIAK | Needs data | P0 | Backend differences | – | – |
| B405-084 | Maximum-mini-NUIAK | Needs data | P0 | Cold and warm runtime | – | – |
| B405-088 | Maximum-mini-NUIAK | Needs data | P0 | Supported OS transfer | – | – |
| B405-089 | Maximum-mini-NUIAK | Needs data | P0 | Real-app model transfer | – | – |
| B405-090 | Maximum-mini-NUIAK | Needs data | P0 | Navigation utility | – | – |
| B405-091 | Maximum-mini-NUIAK | Conditional | P4 | Screen-context recognition | – | – |
| B405-092 | Maximum-mini-NUIAK | Conditional | P4 | Masked screen similarity | – | – |
| B405-093 | Maximum-mini-NUIAK | Conditional | P4 | Localized OCR | – | – |
| B405-094 | Maximum-mini-NUIAK | Conditional | P4 | iOS partial-crop robustness | – | – |
| B405-095 | Maximum-mini-NUIAK | Conditional | P4 | Unified iOS/tvOS detection | – | – |
| B405-096 | Maximum-mini-NUIAK | Conditional | P4 | Platform sampling balance | – | – |
| B405-097 | Maximum-mini-NUIAK | Conditional | P4 | Badge separation | – | – |
| B405-098 | Maximum-mini-NUIAK | Conditional | P4 | macOS coordinate qualification | – | – |
| B405-099 | Maximum-mini-NUIAK | Conditional | P4 | macOS synthetic transfer | – | – |
| B405-100 | Maximum-mini-NUIAK | Conditional | P4 | macOS candidate qualification | – | – |
| B405-101 | Maximum-mini-NUIAK | Needs data | P0 | Static border width | – | – |
| B405-102 | Maximum-mini-NUIAK | Needs data | P0 | Static border contrast | – | – |
| B405-103 | Maximum-mini-NUIAK | Needs data | P0 | Clipped native HCF controls | – | – |
| B405-104 | Maximum-mini-NUIAK | Needs data | P0 | Mapping across control families | – | – |
| B405-105 | Maximum-mini-NUIAK | Needs data | P0 | Profile correspondence under producer change | – | – |
| B405-106 | Maximum-mini-NUIAK | Needs data | P1 | Stepper control gate | – | – |
| B405-109 | Maximum-mini-NUIAK | Needs data | P2 | Held-out hard-negative quota | – | – |
| B405-110 | Maximum-mini-NUIAK | Needs data | P2 | Fixture content diversity at fixed layout | – | – |
| B405-111 | Maximum-mini-NUIAK | Needs data | P1 | Same-screen modal interruption | – | – |
| B405-112 | Maximum-mini-NUIAK | Needs data | P1 | Transition direction order | – | – |
| B405-113 | Maximum-mini-NUIAK | Conditional | P1 | Small label-noise tolerance | – | – |
| B405-123 | Maximum-mini-NUIAK | Needs decision | P1 | Calibration-role thresholds | – | – |
| B405-124 | Maximum-mini-NUIAK | Existing execution | P0 | Cross-profile transfer matrix | 2/3 | – |
| B405-126 | Maximum-mini-NUIAK | Needs decision | P2 | Notification correction across seeds | 6/6 | inconclusive |
| B405-158 | Maximum-mini-NUIAK | Needs decision | P0 | Kernel settings on the unused light-background capture | 3/3 | inconclusive |
| B405-159 | Maximum-mini-NUIAK | Needs decision | P0 | Jitter scoring on the unused light-background capture | 3/3 | inconclusive |
| B405-161 | Maximum-mini-NUIAK | Needs adapter | P0 | Outer-ring kernel on light backgrounds | – | contradicted |
| B405-174 | Maximum-mini-NUIAK | Needs decision | P0 | Scoring the matched-exposure HCF-only model | 3/3 | inconclusive |
| B405-180 | Maximum-mini-NUIAK | Needs adapter | P0 | Within-screen focus ranking against convincing distractors | – | – |
| B405-181 | Maximum-mini-NUIAK | Needs adapter | P0 | Equal-budget random, balanced, and failure-targeted generation | – | – |
| B405-182 | Maximum-mini-NUIAK | Needs adapter | P0 | No-focus truth versus missed or uncertain focus | – | – |
| B405-183 | Maximum-mini-NUIAK | Needs data | P1 | Independent mobile UI evaluation with MUIAnno | – | – |
| B405-184 | Maximum-mini-NUIAK | Needs adapter | P1 | Coverage-preserving data refinement before model scaling | – | – |
| B405-185 | Maximum-mini-NUIAK | Needs decision | P1 | Locate native iOS detector regressions by screen region | 7/7 | inconclusive |
| B405-186 | Maximum-mini-NUIAK | Needs decision | P1 | Separate small and badly fitted native iOS controls | 7/7 | inconclusive |
| B405-188 | Maximum-mini-NUIAK | Needs decision | P0 | Separate class errors from missing geometry in native iOS regressions | 7/7 | inconclusive |
| B405-190 | Maximum-mini-NUIAK | Needs adapter | P1 | Native-control transfer between families | – | – |
| B405-191 | Maximum-mini-NUIAK | Needs adapter | P1 | Frozen features versus full crop training | – | – |
| B405-192 | Maximum-mini-NUIAK | Needs adapter | P1 | Worst-family checkpoint selection | – | – |
| B405-193 | Maximum-mini-NUIAK | Needs data | P0 | Raw-box regression and corrected geometry | – | – |
| B405-194 | Maximum-mini-TTR | Needs data | P1 | Selected-tab appearance without focus | – | – |
| B405-195 | Maximum-mini-NUIAK | Needs adapter | P1 | Preserve old predictions during native adaptation | – | – |
| B405-196 | Maximum-mini-NUIAK | Needs adapter | P0 | Measured proposal errors versus random crop jitter | – | – |
| B405-197 | Maximum-mini-NUIAK | Needs adapter | P1 | More scenes versus repeated views at equal frame count | – | – |
| B405-198 | Maximum-mini-NUIAK | Needs adapter | P1 | Same control under changing crop context | – | – |
| B405-206 | Maximum-mini-NUIAK | Needs decision | P0 | Review matched TTR frame selections | 2/2 | inconclusive |
| B405-209 | Maximum-mini-NUIAK | Needs decision | P0 | Explain lower-exposure row regressions and tab gains | 5/5 | inconclusive |
| B405-215 | Maximum-mini-NUIAK | Needs decision | P0 | Measure tvOS controls recovered at lower confidence | 8/8 | inconclusive |
| B405-220 | Maximum-mini-NUIAK | Existing execution | P0 | Do new native layouts provide verified focused controls and matched no-focus evidence for the fixed proposal policy? Comparison: capture. | 0/5 | – |
| B405-221 | Maximum-mini-NUIAK | Existing execution | P0 | Do all new native frames have consistent measured body labels, groups, hashes, and recorded null-focus states? Comparison: labels. | 0/5 | – |
| B405-222 | Maximum-mini-NUIAK | Existing execution | P0 | Do native ring proposals cover the new controls without assigning native focus to decorative content? Comparison: rings. | 0/5 | – |
| B405-223 | Maximum-mini-NUIAK | Existing execution | P0 | Does the fixed detector threshold recover controls on new groups without changing model or input membership? Comparison: detect-high. | 0/5 | – |
| B405-224 | Maximum-mini-NUIAK | Existing execution | P0 | Does the fixed detector threshold recover controls on new groups without changing model or input membership? Comparison: detect-low. | 0/5 | – |
| B405-225 | Maximum-mini-NUIAK | Existing execution | P0 | Does the pinned crop model preserve known-box selection on the new native groups and abstain on null-focus scenes? Comparison: known-baseline. | 0/5 | – |
| B405-226 | Maximum-mini-NUIAK | Existing execution | P0 | Does the pinned crop model preserve known-box selection on the new native groups and abstain on null-focus scenes? Comparison: known-candidate. | 0/5 | – |
| B405-227 | Maximum-mini-NUIAK | Existing execution | P0 | Do identical detector boxes produce correct full-screen focus selections on the new native groups at the fixed threshold? Comparison: focus-high. | 0/5 | – |
| B405-228 | Maximum-mini-NUIAK | Existing execution | P0 | Do identical detector boxes produce correct full-screen focus selections on the new native groups at the fixed threshold? Comparison: focus-low. | 0/5 | – |
| B405-230 | Maximum-mini-NUIAK | Needs decision | P1 | Locate iOS threshold recovery and extra boxes by screen region | 6/6 | inconclusive |
| B405-231 | Maximum-mini-NUIAK | Needs decision | P1 | Measure iOS threshold recovery by control size | 6/6 | inconclusive |
| B405-233 | Maximum-mini-NUIAK | Needs decision | P1 | Separate learned training coverage from unseen row failures | 2/2 | inconclusive |
| B405-239 | Maximum-mini-NUIAK | Needs data | P0 | Native coverage: 18 new training groups | – | – |
| B405-240 | Maximum-mini-NUIAK | Needs data | P0 | Native coverage: fixed detector correction | – | – |
| B405-241 | Maximum-mini-NUIAK | Needs data | P0 | Native coverage: independent full-screen comparison | – | – |
| B405-242 | Maximum-mini-NUIAK | Existing execution | P0 | Verify new native development labels | 1/6 | – |
| B405-243 | Maximum-mini-NUIAK | Existing execution | P0 | Measure the retained detector on new native groups | 1/6 | – |
| B405-244 | Maximum-mini-NUIAK | Existing execution | P0 | Test detector recovery on new native groups | 1/6 | – |
| B405-245 | Maximum-mini-NUIAK | Existing execution | P0 | Measure outline coverage on new native groups | 1/6 | – |
| B405-246 | Maximum-mini-NUIAK | Existing execution | P0 | Separate crop classification from missing proposals | 2/12 | – |
| B405-247 | Maximum-mini-NUIAK | Existing execution | P0 | Measure the complete focus path on new native groups | 2/12 | – |
| B405-248 | Maximum-mini-NUIAK | Existing execution | P0 | Combine new native focus findings across families | 0/4 | – |
| B405-249 | Maximum-mini-NUIAK | Needs decision | P0 | Separate iOS class errors from missing control boxes | 6/6 | inconclusive |
| B405-250 | Maximum-mini-NUIAK | Needs decision | P1 | Measure ambiguous button roles without changing production labels | 6/6 | inconclusive |
| B405-252 | Maximum-mini-NUIAK | Needs adapter | P1 | Separate overlay focus from unavailable underlay | – | – |
| B405-253 | Maximum-mini-NUIAK | Needs adapter | P1 | Measure image-only ambiguity across returned states | – | – |
| B405-254 | Maximum-mini-NUIAK | Needs adapter | P1 | Separate modal body localization from action focus | – | – |
| B405-258 | Maximum-mini-NUIAK | Needs decision | P1 | Standard checkpoint timing on T37 retained cases | 30/30 | inconclusive |
| B405-262 | Maximum-mini-NUIAK | Needs decision | P1 | Recover native proposals with fixed-model input size | 6/6 | inconclusive |
| B405-263 | Maximum-mini-NUIAK | Needs decision | P1 | Qualify proposal scale on retained negatives | 10/10 | inconclusive |
| B405-271 | Maximum-mini-NUIAK | Awaiting review | P1 | Matched role-head initialization | 2/2 | – |
| B405-272 | Maximum-mini-NUIAK | Awaiting review | P1 | Frozen features with a classification teacher | 2/2 | – |
| B405-273 | Maximum-mini-NUIAK | Awaiting review | P0 | Verified native focus additions with matched replay | 2/2 | – |
| B405-274 | Maximum-mini-NUIAK | Awaiting review | P1 | Explain four generated-screen detector losses | 1/1 | – |
| B405-275 | Maximum-mini-NUIAK | Existing execution | P1 | Explain retained Run013 losses from cached predictions | 0/1 | – |
| B405-276 | Maximum-mini-NUIAK | Awaiting review | P1 | iOS box-distribution teacher preservation | 2/2 | – |
| B405-278 | Maximum-mini-NUIAK | Needs data | P0 | SDK572 qualify real-app focus and readiness observations | – | – |
| B405-280 | Maximum-mini-NUIAK | Awaiting review | P0 | NATIVE576 production crops from aligned native packets | – | – |
| B405-281 | Maximum-mini-NUIAK | Awaiting review | P1 | IOS577 low-floor diagnosis of retained misses | – | – |
| B405-282 | Maximum-mini-NUIAK | Awaiting review | P0 | NATIVE578 matched review-only native focus scores | – | – |
| B405-283 | Maximum-mini-NUIAK | Awaiting review | P1 | IOS579 foreground classification preservation | – | – |
| B405-284 | Maximum-mini-NUIAK | Awaiting review | P0 | FOCUS581 restricted native transfer with full retention | – | – |
| B405-285 | Maximum-mini-NUIAK | Awaiting review | P1 | IOS582 paired wide teacher preservation under current source | – | – |
| B405-286 | Maximum-mini-NUIAK | Awaiting review | P1 | FOCUS583 exact donor parameters with baseline BatchNorm state | 10/10 | – |
| B405-288 | Maximum-mini-NUIAK | Awaiting review | P1 | IOS588 geometry-only teacher ablation for 7 confidence losses | – | – |
| B405-289 | Maximum-mini-NUIAK | Awaiting review | P1 | NATIVE589 matched replay and newly admitted SDK focus crops | – | – |
| B405-290 | Maximum-mini-NUIAK | Awaiting review | P1 | IOS591 retained training-best versus fixed-final checkpoint | – | – |
| B405-291 | Maximum-mini-NUIAK | Awaiting review | P1 | TEMPORAL592 native movement and before-frame dependence | – | – |
| B405-292 | Maximum-mini-NUIAK | Awaiting review | P1 | NATIVE593 replay teacher with frozen native training membership | – | – |
| B405-293 | Maximum-mini-NUIAK | Awaiting review | P1 | IOS594 foreground-only geometry with classification preservation off | – | – |
| B405-294 | Maximum-mini-NUIAK | Existing execution | P1 | Matched original training controls on the parallax shelf | 4/8 | – |
<!-- BACKLOG:END -->

### Separate engineering work

| ID | Owner | Status | Existing parent | Outcome |
| --- | --- | --- | --- | --- |
| ENG405-01 | Maximum-mini-NUIAK | In verification | T393-04 | Cached native diagnosis |
| ENG405-02 | Maximum-mini-NUIAK | Done (T42) | S391-03 | Detector per-case matching. 13 other records that name this template still need plan blocks. |
| ENG405-03 | Maximum-mini-NUIAK | Done (T46) | TASK-6a-10 | iOS native capture variant with rendered-body check. B405-033 and B405-036 to 040 still need the inputs named in the catalog. |
| ENG405-04 | Maximum-mini-NUIAK | Needs data | S391-04 | Standard tvOS producer variants |
| ENG405-05 | Maximum-mini-NUIAK | Needs adapter | FOCUS-TRANSITION-49 | Temporal evaluation variant |
| ENG405-06 | Maximum-mini-NUIAK | Conditional | T395-VARIANTS | Detector training and restore variant |
| ENG405-07 | Maximum-mini-NUIAK | Needs adapter | T393-05 | Complete runtime variants |
| ENG405-08 | Maximum-mini-NUIAK | Needs decision | W394-05b | DVC operating-cost comparison |
| ENG405-09 | Maximum-mini-NUIAK | Needs adapter | T395-EFFICIENCY | Shared preparation and cache integrity |
| ENG405-10 | Maximum-mini-NUIAK | Needs data | T393-08 | Consumer verification variants |
| ENG405-11 | Maximum-mini-NUIAK | In verification | T393-10 | Catalog and template evolution |
| ENG405-12 | Maximum-mini-NUIAK | Open | T393-10 | Template failure matrix |
| ENG405-13 | Maximum-mini-NUIAK | Open | Before committing | Serial package validation passes (174 Swift Testing tests). The default parallel `swift test` stall (44 tests start and never finish) is unresolved. |
| ENG417-01 | Maximum-mini-NUIAK | Done | TASK-6a-10 | iOS generator repair for T46 (ACTIONS417): requested appearance in SwiftUI templates, drawn switch and search-platter bodies, chrome cover, hidden native scroll indicators, body rule v2. Default output unchanged. Successors B405-135, 136, 137 confirmed supported: 45 of 48 families pass bounds (rule v2), 48 of 48 render light and dark. Research/Plans/Backlog410.md, section "ACTIONS417 — iOS generator repair". |

The 7 answered inventory subjects are recorded in CompletedTasks.md. They are not pending experiments.
Detailed blockers name the missing input, responsible Machine-Project, and exact resume condition in the catalog.
Validation passes: 35 focused Python tests and 174 offline Swift tests. See the BACKLOG405 verification receipt.
ENG405-11 retains future schema compatibility checks. ENG405-12 retains broader variant failure qualification.


## EXTENSION408 — restart exhausted jobs with larger limits

Owner: Maximum-mini-NUIAK. [Policy and implementation](Research/Plans/Extension408.md).
The dashboard shows exhausted jobs with a reason, an estimate from recorded progress, and suggested limits.
The maintainer saves a restart as a new approved successor job. It runs after ordinary ready work, in save order.
Limits above the default policy need a maintainer override for that exact specification hash.
`scripts/restart_research_dashboard.py` stops and restarts the server safely. The maintainer uses it on 2026-10-14.
A shared snapshot cache reduces a warm dashboard snapshot from 29 s to 1.3 s.
Validation passes: 276 tests across the queue, continuation, extension, and dashboard suites.
RECONCILE409 finds no unstarted job that fails only its code check. No renewal is pending.
No restart is saved on the live queue.

## CONTINUATION403 — prepare useful bounded continuations

Dashboard readiness correction: [DASHBOARD406](Research/Plans/Dashboard406.md) verifies the other 24 pending jobs.
Of these, 22 have changed registered code inputs. Only 2 report approval as their sole runtime blocker.
The deployed UI separates Ready, Awaiting approval, and Blocked. Pending remains a not-started filter.
Next: reconcile stale jobs with completed successors before proposing replacements or approval of the 2 remaining controls.

Owner: Maximum-mini-NUIAK. [Policy and implementation](Research/Plans/Continuation403.md).
The runner selects ordinary ready work before approved bounded continuations.
The retained timeout is superseded by HCF388's completed 30-epoch run. Do not repeat it.

| Task | What does it test? | What will the result decide? |
| --- | --- | --- |
| C403-CHUNKS | Can a useful long diagnostic save and restore progress at bounded chunk boundaries? | Admit a continuation only when an unresolved question justifies the remaining budget. |
| C404-PROPOSALS | Why do native outline proposals miss controls that the crop model classifies correctly? | Test proposal corrections before more classifier training. |
| C404-TALL | Why does fixed inset mapping lose a tall-control success? | Reject replacement until the correction preserves that success. |

The fixed-last crop restore path passes a matched comparison. See [CHECKPOINT404](Research/Plans/Checkpoint404.md).
Other restore configurations remain unqualified. These tasks do not expand training budgets.
The background runner remains active. No existing reviewed failure qualifies for automatic continuation.

This file contains open work only. The background runner executes approved experiment jobs.
[Completed work and historical evidence](CompletedTasks.md) are separate from this queue.

## Queue trust status — 2026-10-13

Fabricated jobs ran on 2026-10-13. See [RCA Addendum A](Research/RCA-20261013-Mock-Experiment-Generation.md) for the verified scope.
- The runner, the CLI, and the dashboard now run only approved jobs. Approval is per job and runs authenticity checks.
- New jobs use `research-spec-v2`. Each job must state its question, controlled comparison, next action for each outcome, and Machine-Project owner.
- The reconciled ledger is `reports/work/QUEUE-TRUST-20261013/ledger-recheck-v2.json`. It accounts for all 573 revoked approvals.
- The evidence labels describe recorded artifacts. They do not prove model accuracy. Replay and independent review remain required.
- An empty queue means starvation. Report it. Do not add fabricated results or repetitive filler jobs.

## Groomed active backlog — dispatch from this table only

### Current scope and next preparation — 2026-10-13

General UI detection, classification, and Standard focus detection are the main goals.
HCF remains separate and optional. This rule replaces earlier HCF-first planning text below.
Do not interrupt the running queue or change approved specifications, settings, or execution order.
The detached runner continues its approved work. This section changes future preparation priorities only.

Standard NUIAK does not require HCF, an HCF download, or an OS setting change.
Keep HCF models and results separate. HCF success does not approve default integration.
Compare any shared correction against a Standard-only control and retained Standard successes before acceptance.
Keep existing model gates and final evaluation exclusions unchanged.

| Priority / task | What does it test? | What will the result decide? | Preparation requirement |
| --- | --- | --- | --- |
| P0 — PROGRAM384-E1 | Which real controls are missed or classified incorrectly? | Which classes, sizes, and positions need targeted Standard data? | Verify the input contract for retained reports; reuse predictions instead of repeating inference. |
| P0 — FOCUS363-B | Which Standard scenes and focus conditions lack evidence? | Which producer cases fill real coverage gaps? | Audit retained manifests by domain, family, group, and position. Report unsupported cells. |
| P0 — FOCUS373-LOSSES / PROGRAM384-D1 | Does notification training cause losses beyond variation between runs? | Retain the correction, diagnose its specific losses, or reject it. | Review saved cases and matched controls first. Preserve existing replay requirements. |
| P1 — PROGRAM384-B1 | Can the actual fallback select focus without known boxes? | Improve proposals or the focus classifier, based on the measured failure. | Add the missing fallback entrypoint before claiming executable readiness. |
| P1 — FOCUS355 / PROGRAM384-E3 | Do targeted Standard examples improve position and control coverage? | Keep a data correction only if it improves the target and preserves previous successes. | Use findings above to freeze recipes, groups, matched controls, and explicit budgets. Do not repeat answered tests. |
| Conditional — FOCUS360-E01 | Do movement and content examples give conflicting training signals? | Choose a justified correction only if saved comparisons leave this question unresolved. | Implement the read-only diagnostic entrypoint; preserve original images and crops. |

Maximum-mini-NUIAK owns this preparation. These rows reuse existing tasks; they do not create duplicate jobs or claim executable readiness.
Continue approved iOS work independently of tvOS and HCF evidence.
Keep detection, classification, focus selection, and transition metrics separate in every comparison.
Record Standard gains and lost successes before considering any HCF-assisted training for the main models.

### STANDARD391 — combined review implementation and experiments

Owner: Maximum-mini-NUIAK. [Implementation plan](Research/Plans/StandardResearch391.md).
Standard detection, classification, and focus come first. HCF remains optional.
These are preparation tasks, not submitted jobs. Existing execution and approvals remain unchanged.

| Priority / task | What does it test or deliver? | What will it decide? | Next requirement |
| --- | --- | --- | --- |
| P1 S391-03 | Lower-confidence proposals and duplicate handling | Can proposals recover misses without losing correct selections? | Actual fallback baseline complete; pin one lower detector threshold and a controlled grouping test |
| P1 S391-04 | Targeted Standard Fixture producers | Which matched examples address demonstrated gaps? | TTR accepts 2 matched calibration plans; qualify capture and prepare row size/position variants |
| P1 S391-05 | One justified fitting, fusion, or data correction | Does the change improve the target without lost successes? | S391-01 findings, qualified inputs, fixed controls, complete regression graph |
| P2 S391-06 | Boundary features against original crops | Does boundary detail add useful information? | Existing feature tests and geometric masks; preserve baseline views |
| P2 S391-07 | Preprocessing or compression comparison | Does a measured runtime or package problem improve without changed decisions? | Current bottleneck measurement and parity adapter |
| P2 S391-08 | One alternate detector feasibility check | Is a larger comparison worth its cost? | Current proposal results, exact license, resident tools, Apple conversion check |
| P3 S391-09 | Optional HCF-assisted Standard training | Can paired teacher evidence help without an inference dependency? | Qualified counterparts and matched Standard-only control; separate from active HCF work |

The plan defines 14 diagnostic comparisons, 3 producer designs, and conditional training branches.
Do not count these proposals as ready queue capacity. Reuse completed answers and existing job identities before registration.
S391-01 and S391-02 are complete. See [findings and tests](Research/Standard391Results.md) and CompletedTasks.md.
The [S391-03 baseline](Research/Standard392Results.md) finds 0 gains and 1 lost success from the actual fallback.
Next: lower-confidence proposals, duplicate handling, and queued native pilot capture. Keep current execution unchanged.

### TEMPLATE393 — reusable experiment preparation

Owner: Maximum-mini-NUIAK. Priority: High, within the requested HCF workflow improvement.
[ADR-0028](Research/ADR-0028-Reusable-Experiment-Templates.md) defines 14 template contracts.
[Implementation plan](Research/Plans/ExperimentTemplates393.md) maps them to every remaining HCF389 step.
These are implementation tasks, not ready execution jobs. Do not interrupt the runner or change submitted specifications.

| Task | What does it deliver? | What will it decide or prove? |
| --- | --- | --- |
| T393-04 | Evidence, groups, and candidate templates | Which completed HCF results can we reuse safely? |
| T393-05 | Core ML export, Vision parity, and runtime templates | Can the frozen HCF candidate support an optional TTR trial? |
| T393-06 | Native capture, qualification, and preparation templates | Can TTR supply the missing coverage through bounded jobs? |
| T393-07 | Crop and detector training templates | Can justified training resume and preserve comparison controls? |
| T393-08 | Audit, package, and consumer verification templates | Does the optional HCF package meet HCF389 completion requirements? |
| T393-09 | Controlled setup and batching measurements | Which reuse methods save time without changing results? |
| T393-10 | Version and capability maintenance checks | Can new use cases leave submitted jobs unchanged? |

T393-01 through T393-03 complete for the bounded development-crop binding. See CompletedTasks.md.
Next, prepare export and coverage branches using retained HCF evidence.
Standard detection remains the product goal. This work neither makes HCF mandatory nor replaces existing HCF389 tasks.

### TEMPLATE395 — executable adapters and qualification

### HCF402 — new native coverage and useful follow-up work

Owner: Maximum-mini-NUIAK. [Plan](Research/Plans/NativeCoverage402.md).
Use one batch description and existing adapters. Do not start a second runner.

| Priority | Test | What will it decide? | Required input or next step |
| --- | --- | --- | --- |
| P0 | Native corners, decoration, and no-focus capture | Can the producer supply verified new development evidence? | 18-frame T03 batch; native restoration required |
| P0 | Frozen mapping on new groups | Does mapping improve body alignment without hiding false proposals? | T34 depends on the native receipt; no refitting |
| P0 | Sillycon-TTR consumer scores | Does the consumer reproduce the approved 8-crop result? | Sillycon-TTR accepts the existing human approval and returns inference evidence |
| P1 | Crop selection on new native cases | Does the full pipeline preserve successes and abstain on no-focus frames? | Qualified new capture and a no-focus-aware selection report |
| P1 | Native decoration coverage | Does ordinary border artwork cause wrong selections? | Qualify an owned-artwork or static-border recipe beyond the square-glyph pilot |
| P1 | Per-case iOS gains and losses | Which prior correct detections does Run 013 lose? | Match retained predictions with reviewed labels; aggregate AP is insufficient |
| P1 | iOS small page controls | Does original-resolution detail recover missed small controls? | Freeze matched proposals and supported class labels before inference |
| P1 | tvOS proposal recall | Are absent boxes the main remaining focus error? | Freeze deployable proposals and native body labels on new groups |
| P1 | No-focus crop abstention | Does the classifier reject decoration when no control has focus? | Qualified null-focus captures and fixed selection threshold |
| P2 | Decorative border width | Which static widths resemble HCF borders? | Qualify static border control; vary width only |
| P2 | Decorative border contrast | Does background contrast change false selection? | Same static border geometry and frozen artwork |
| P2 | Clipped HCF control | Where does the fixed map fail near screen boundaries? | Native clipping receipts and body geometry; do not infer hidden bounds |
| P2 | Native control size | Does the fixed pixel inset transfer across control sizes? | Matched native size pairs outside fitting groups |
| P2 | Border-to-body family transfer | Does one mapping fit buttons and posters? | Qualify each native family before comparing |
| P2 | Animation settling | Can the observer avoid early confident selections? | Timed native observations and frame timestamps |
| P2 | Standard artwork exchange | Do unchanged-focus artwork swaps cause false changes? | Matched Standard capture pairs with observed focus |
| P2 | Standard selected-tab decoys | Does selection appearance replace actual focus evidence? | Native selected and focused identities recorded separately |
| P2 | iOS navigation bars | Which confusion or geometry error explains the retained regression? | Case-linked labels and cached Run 009/013 predictions |
| P2 | iOS buttons | Does class confusion explain false detections better than geometry? | Matched primary and secondary button cases |
| P2 | iOS progress and toggles | Do unsupported states cause the retained AP loss? | Reviewed state slices; no inferred labels |
| P3 | Batch authoring cost | Does one description reduce preparation work against the previous script? | Record matched authoring, validation, and registration timings |
| P3 | Shared decode cache | When does reuse reduce USB input time? | Same hashes, output order, and alternating measured runs |
| P3 | Cache invalidation | Does a changed crop or preprocessing version reject cached features? | Qualified cache adapter and positive/negative fixtures |
| P3 | Missing producer output | Does the queue block only dependent jobs? | Isolated producer failure and independent sibling test |
| P3 | USB loss during reads | Does the worker fail predictably without accepting partial results? | Injected read failure; do not disconnect the live drive |
| P3 | Output limit recovery | Does the queue preserve failure evidence and stop oversized output? | Isolated bounded producer; no live quota change |
| P3 | Preparation sharing | Can compatible scoring jobs share setup without state leakage? | Matched separate/shared execution and exact output checks |
| P3 | Core ML batch size | Which supported batch path improves throughput without changed decisions? | Fixed exported model and compatible runtime inputs |

These rows are preparation work until their exact inputs and adapters pass checks.
Do not count blocked rows as ready jobs or repeat completed tests merely to occupy hardware.
Keep new HCF evidence separate from Standard model changes.
The registered factor batch contains 10 bounded producers and 10 dependent geometry reports.
Its factors and decisions are listed in the plan. Each producer requires the corrected focused pilot.
The Standard class report, batch compiler, idle-boundary admission, and null-ID decoder checks are recorded in CompletedTasks.md.
The corrected no-focus capture and its report remain queued as explicit R4 successors.

### HCF397 — retained integration requirements

Owner: Maximum-mini-NUIAK. [Plan and measured findings](Research/Plans/HCF397.md).
The approved batch uses reusable descriptions. Standard stays unchanged; HCF remains optional.

| Priority | Test or work | What will it decide? | Requirement |
| --- | --- | --- | --- |
| P0 | TTR crop observer integration | Does TTR load the exact optional model and reproduce decisions? | Return actual inference with T23 identities and crop lineage; observer wrapper is available |
| P1 | Fixed-map native qualification | Does the frozen HCF401 mapping preserve gains on new native groups? | Freeze new groups and native capture recipes without changing the mapping. [HCF401 results](Research/Plans/HCF401.md). No-focus and decoy coverage remain required. |
| P1 | Native no-focus and decoration producer | Does the selector abstain when no control has focus? | Executable recipe and observed no-focus labels |
| P1 | Independent full-screen audit | Does the complete feature preserve Standard successes? | Frozen new groups, qualified proposals, and fixed thresholds |

TTR confirms normalized top-left outer-ring-v2 candidate bounds. These are not qualified body bounds or a deployable selector.
The boundary tests fail replacement criteria. Their findings are in CompletedTasks.md.
HCF398 separates completed execution from changed-source reproducibility without relaxing approval checks.
Five diagnostics and the corrected 6-job source graph complete. The first crop count failure remains preserved.
TTR ring proposals plus crop scoring do not qualify as a replacement. Actual TTR observer inference remains pending.
See [HCF398](Research/Plans/HCF398.md). This graph is useful short work, not 24 h of execution.

### TEMPLATE395 qualification details

Owner: Maximum-mini-NUIAK. [Implementation and authoring plan](Research/Plans/ExecutableTemplates395.md).
All 14 template identifiers have executable bindings. Qualification remains separate from implementation.
The background runner executes the bounded qualification jobs. Standard models remain unchanged.

| Priority / task | What does it test? | What will the result decide? | Exact remaining requirement |
| --- | --- | --- | --- |
| P1 T395-CONSUMER | TTR inference from the exact bundle | Does TTR load and score it correctly without navigation authority? | Sillycon-TTR has all bytes. The user approves the 20 min, 1 GiB Swift/Ruby check. Await actual inference and independently verify the receipt. |
| P2 T395-VARIANTS | Detector and checkpoint-resume bindings | Which additional variants are safe to expose through descriptions? | Separate positive and negative qualification; the current training binding covers crop restart only |
| P2 T395-EFFICIENCY | Shared preparation versus separate preparation | Does reuse save time without changing outputs? | Fixed inputs, repeated measurements, and identical predictions |

Completed software and retained-data work belongs in CompletedTasks.md.
HCF396 completes bounded native capture, package size repair, and Vision parity. TTR verification remains blocked on actual consumer results.
Do not count blocked downstream jobs as ready work or model successes.

### WORKFLOW394 — existing tools review, independent of HCF

Owner: Maximum-mini-NUIAK. Priority: P2; do not block TEMPLATE393 or HCF389.
[ADR-0029](Research/ADR-0029-Workflow-Tools-Versus-Templates.md) records the completed source review.
[Comparison plan](Research/Plans/WorkflowComparison394.md) defines one preparation → scoring → report comparison against DVC.
DVC 3.67.1 is installed in the approved isolated USB environment. All 3 matched repetitions produce identical reports.
See [results and limits](Research/Workflow394Results.md). Framework adoption is not approved.

| Task | What does it test? | What will it decide? | Requirement |
| --- | --- | --- | --- |
| W394-05b | Comparable effort and operating cost | Does DVC remove enough maintenance to justify migration? | Authoring effort and full cost remain unmeasured; defer adoption |

### HCF389 — optional experimental Core ML model

The maintainer requests the complete prototype. [HCF389](Research/Plans/HCF389.md) defines the remaining work and completion checks.
HCF388 continues unchanged. Its development report alone does not complete the model.
The first 5 specifications now have implemented entrypoints. See the readiness table in HCF389.
Explicit export support and Vision inference are implemented through TEMPLATE395.
The idle-boundary engine update does not interrupt an active job. Package size currently blocks actual parity.

| Task | What it tests or delivers | What the result decides | Status |
| --- | --- | --- | --- |
| HCF389-03 | Selection without known boxes | Whether proposals or classification limit actual selection | Independent-rule comparison complete; TTR outer-ring-v2 source/interface remains required |
| HCF389-04 | Native coverage and reserved groups | Which missing cases the Fixture must capture | Executable catalog inventory; new group reservation remains open |
| HCF389-05 | Native HCF capture shards | Whether new cases have verified labels and useful coverage | Needs HCF389-04 and qualified target |
| HCF389-06 | Rules versus learned selection | Which method handles absent focus and distracting controls | Needs HCF389-03 and verified captures |
| HCF389-08 | Broader PyTorch/Core ML parity | Whether Vision preserves decisions across deployment conditions | HCF396 sample passes; deployment proposal and no-focus membership remain required |
| HCF389-09 | Complete runtime benchmark | Whether the full pipeline meets latency and memory needs | CPU crop timing passes measurement; proposal cost, memory, and other backends remain unmeasured |
| HCF389-10 | Frozen audit and retained successes | Whether the prototype meets measured acceptance checks | Needs fixed settings, parity, and untouched groups |
| HCF389-11 | Optional TTR delivery contract | Whether TTR can verify and load the experimental model | Archive bytes received; accepted observer adapter and model identity checks remain required |
| HCF389-12 | TTR shadow inference receipt | Whether TTR loads and uses the exact model correctly | Needs actual TTR inference, not another transfer receipt |

DONE means a tested experimental Core ML package and verified TTR inference, not production promotion or navigation authority.
Failed model gates require diagnosis. They do not justify removing tests or calling the prototype complete.

### Current tranche — 2026-10-14 UTC

**HCF388 finishes the approved development comparison.** See [the execution plan](Research/Plans/HCF388.md).
The graph contains 9 individually approved jobs: 3 training runs, 3 evaluations, and 3 reports.
Training inputs pass readiness. Reports wait for their producers, not another chat approval.
The detached USB runner starts HCF388. Focused tests pass 117 checks; the clean offline Swift suite passes 173 tests and 14 XCTest tests.
Startup confirms the first crop repeat at epoch 14 of 30. The dashboard returns HTTP 200.
The detector uses 30 epochs with early stopping disabled, a 2 h limit, and unchanged calibration selection.
Two balanced-unique crop repeats use seeds 372 and 373. They compare against completed seed 371.
The graph estimates 1.5–2.5 h, not an all-night workload. The runner waits after finishing; it does not repeat work.
No model gains deployment approval. Final audit stays closed.
The active project is `/Volumes/training-drive/data/NUIAK/project/NativeUIAuditKit`. Do not run the parked original checkout.
Completed migration, crop comparisons, and diagnostics move to CompletedTasks.md.

| Task | What it tests | What the result decides | Current requirement |
| --- | --- | --- | --- |
| HCF388 detector | Complete 30 epochs and compare rules, crop, and detector outputs | Whether full-screen detection preserves successes without known boxes | Training → evaluation → method report |
| HCF388 crop repeats | Repeat balanced unique training with 2 new seeds | Whether 264 known-box successes repeat without losses | Two training/evaluation pairs → seed report |
| HCF388 study report | Join all matched results and limitations | Which candidate deserves deployment tests or further diagnosis | Method and seed reports complete |
| QUEUE-SYNC-01 | Report queue changes without changing execution ownership | Whether both peer displays preserve real attempt history | Local outbox tests pass; BigDog-Coordinator must supply the receiver contract |

The 25-question inventory is `Research/ResearchSpecs/HCF376/investigations-v2.json`.
Questions without qualified inputs remain blocked. They do not count as ready work.
The existing rows below retain earlier scope. This checkpoint supersedes their older execution states.

HCF376 completes all 7 crop steps. Balanced repeated and balanced unique each select 264 of 264 known controls.
HCF-only repeated selects 130; HCF-only unique selects 132. No result establishes deployable or no-focus accuracy.
HCF388 preserves the incomplete 11-epoch detector attempt. Explicit successors replace its blocked descendants.
No failed attempt receives an automatic retry.

Next preparation: qualify USB outputs for other approved training branches before refreshing their changed code approvals.
QUEUE-SYNC-01 still needs BigDog-Coordinator's reporting API and receiver revisions.
Sillycon-LittleDog reports preparation at cursor 633. Sillycon-TTR acknowledges migration at cursor 640.
Neither reply supplies the missing reporting API. Remote reporting remains blocked; experiments stay independent.
The coordinator stores the completed migration update at cursor 641. Forwarding of that update remains unconfirmed.
LittleDog's requested reporting examples are published as `nuiak/nuiak-queue-sync-examples-v1.zip` on the approved share.
The verified archive contains 10 real sanitized events, exact source hashes, import notes, and 21 passing reporting tests.
Coordinator cursor 645 records the response. LittleDog forwarding, receipt, and parser qualification remain pending.
BigDog-Coordinator still owns the live reporting API. The experiment runner remains unchanged.
The requested Standard artwork pair arrives with verified archive and member hashes.
Different producer versions and body sizes prevent causal HCF claims. It stays outside training.
The delivery request is complete; no duplicate capture is requested.

Each row has an owner, a question, a controlled test, inputs, a decision, and authority. Rows below this section that lack these fields are not dispatchable.

| ID | Owner | Question | Controlled test | Inputs or blocker | Decision → next action | Authority | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| QUEUE-SYNC-01 | Maximum-mini-NUIAK; Sillycon-LittleDog; BigDog-Coordinator | Can both worker displays track real queue work without duplicate execution? | [Reporting bridge](Research/Plans/QueueWorkerReporting.md): durable events, shared task identities, and restart tests. | Existing app imports executable tasks, not external reports. Coordinator returns unknown_task at cursor 605. It needs to register or map this task and route the receiver contract request. | Verified delivery and history → use shared reporting. Failure → preserve local execution and repair reporting only. | Maintainer-approved design and peer implementation request; no new service grants or remote controls | Blocked: task routing and read-only receiver API; experiments continue |
| PROGRAM384-D1 | Maximum-mini-NUIAK | Which decisions change across matched control repeats? | Reuse verified seed 42. Train seeds 43 and 44 with the same initialization, membership, 30 epochs, and thresholds. | 7 approved steps; seed 42 must first pass its replay. Score 1,408 fixed views by role. | Variation → inspect cases before proposing a gate change. Stable subset → keep the current rule. No automatic gate change. | Each new training run: 1,800 s/2 GiB; diagnostics: 800 s/100 MB | Approved; background runner |
| FOCUS373-LOSSES | Maximum-mini-NUIAK | Why does the notification correction lose 6 previous successes? | Per-case margins of the 6 lost cases against the matched control's 22 lost cases. | Completed `focus373-repair-decision-v2` outputs. | Losses within control churn → confirm with seeds (D2). Losses specific → diagnose before training. | Diagnostic | Proposed |
| PROGRAM384-B1 | Maximum-mini-NUIAK | How accurate is the library fallback `resolveTVOSFocus`? | The actual Swift heuristic against observed focus on retained native frames. | The method is internal. The existing FocusRingTool supports crop and model inference, not this fallback. Add a bounded test entrypoint first. | Measure correct, wrong, and abstained selections. Use the result as a baseline, not a model gate change. | Diagnostic proposal; 800 s/100 MB after input qualification | Blocked: fallback entrypoint |
| PROGRAM384-E1 | Maximum-mini-NUIAK | Which controls does the tvOS detector miss on real screens (346 of 583 found)? | Join retained predictions and body geometry by exact image and control identity. | Both reports exist under REAL-MODEL-SCORECARD-36. The new report contract requires queue dependencies; these reports predate the queue. | Class/size gaps → select targeted generation. Unknown style → report unsupported coverage. Do not rerun inference to satisfy a contract. | Cached diagnostic; 800 s/100 MB | Blocked: verified external-report input contract |
| PROGRAM384-C1-REVIEW | Maximum-mini-NUIAK | Which shared HCF misses need new data? | Review the completed 4-method report by family and profile. | `hcf-trust-c1-errors-v1` outputs. Size, contrast, and position are unsupported, not inferred. | Shared misses → inspect geometry. Method differences → propose a controlled comparison. | Read-only review; no new model acceptance | Approved review |
| FOCUS360-E01 | Maximum-mini-NUIAK | Do movement and content-only training updates work against each other? | Gradient comparison without weight changes. | Local checkpoints and membership. A read-only entry point is not yet written. | Conflict → select a conflict-aware correction. No conflict → skip FOCUS360 E02 and E03. | Diagnostic | Preparation |
| FOCUS363-B | Maximum-mini-NUIAK | Which movement, appearance, and transfer conditions lack support? | Coverage audit of retained manifests. | Retained manifests. | Names the missing producer cases. | Diagnostic | Open |
| PROGRAM384-R4 | Maximum-mini-NUIAK | Do the HCF recovery and storage controls of TTR `a9b3412c` work on this machine? | Local build of Maximum-mini-TTR source; recovery and storage checks without repeated captures. | Local TTR build at `a9b3412c`. | Pass → use the new controls. Fail → report the exact failure to Maximum-mini-TTR. | Capture needs the Simulator target check | Open |
| TRUST-REPLAY | Maximum-mini-NUIAK | Do historical results reproduce from frozen inputs? | 1 training replay, 3 evaluations, 1 native comparison, and 3 report replays. | 8 approved jobs; explicit per-file comparison rules. No broad timestamp exclusions. | Match → review evidence before changing the trust label. Mismatch → retain both outputs and diagnose. | Training: 1,800 s/2 GiB; others: 800 s/100 MB | Approved; after HCF |
| TRUST-HISTORY | Maximum-mini-NUIAK | Which earlier claims remain unsupported? | Map original approvals, replay receipts, and historical completion notes. | All 573 approvals reconciled. Deleted attempts cannot be recreated. | Supported → label exact scope. Unsupported → withdraw claim, not evidence. | Read-only review | Approved; replay results pending |
| TRUST-PUBLIC | Maximum-mini-NUIAK | Can the reviewed repair enter public Git history safely? | Review each changed file and every unpushed commit. Run hooks and tests. | 4 repair commits pass hooks. The 2 prior commits pass the added-line private-term scan. Full review remains required. | All checks pass → prepare push. Any unresolved content → keep local and name it. | Approved commits; no hook bypass | Blocked: complete review of prior work |

<details>
<summary>Older plans and remaining acceptance checks — reconcile before dispatch</summary>

These records preserve earlier requirements. They are not current execution status or additional approvals.
Completed checkboxes move to CompletedTasks.md. The approved table above controls dispatch.

## Next priorities at a glance

The table below predates the trust repair. Use it for context; dispatch only from the groomed table above.

Statuses reflect the last recorded review. This edit does not check live execution.
High Contrast Focus is shortened to HCF.

| Priority | Experiment or preparation task | What do we change and measure? | What question does the result answer? | Next requirement |
| --- | --- | --- | --- | --- |
| Done | [Which method detects native HCF best? — HCF371](Research/Plans/HCF371.md) | Compare fixed rules, the retained model, a crop candidate, and a full-screen candidate on 264 development frames. | Correct of 264: rule 62, retained model 63, crop candidate 137, detector 134. No model is accepted. | Successor: HCF375C. Final audit stays closed. |
| P0 | [Do training groups push the model in opposing directions? — FOCUS360](Research/Plans/Focus360.md) | Compare movement and content-only gradients without changing weights. | Which correction addresses the remaining native misses? Longer training recovers no native movements. | Prepare the diagnostic from verified local inputs. |
| P0 | [Can smaller image files preserve focus evidence? — FOCUS359](Research/Plans/Focus359.md) | Resize or compress the same screenshots. Measure storage, processing time, missed movements, and false changes. Test lossless PNG separately. | Which formats save space without removing the small visual changes our models need? | Review all 8 queued results before changing storage. |
| Partly done | [Does HCF visibly change this control? — HCF357–358](Research/Plans/WorkflowHCF357.md) | Compare matched Standard and HCF captures. | Yes for native image cards (HCF368–370, 12 states). Buttons show no difference. Other families are unmeasured. | Visibility survey of other families (PROGRAM384-A3). One open TTR request: the Standard counterpart of the artwork row. |
| P0 | [Can realistic screens mislead focus detection? — FOCUS359](Research/Plans/Focus359.md) | Change artwork without moving focus. Separately test selected tabs, identical neighboring items, and corner positions. Count wrong decisions. | Does the model follow actual focus, or does it follow bright styling, artwork, or screen position? | Qualify the missing family source, recipes, and capture evidence. |
| Partly done | [Can we build trustworthy HCF examples? — HCF357](Research/Plans/WorkflowHCF357.md) | Check labels, duplicates, and role leaks (HCF374). | No label conflicts and no cross-role pixel duplicates. Only 615 of 8,000 training crops are unique. | Use deduplicated crops (HCF375C). |
| Done (first result) | [Is HCF easier to detect across a screen or within a control? — HCF357](Research/Plans/WorkflowHCF357.md) | HCF371 compares both approaches. | Similar on development frames (137 against 134). The crop result uses known boxes, not deployable proposals. | Deployable proposal recall remains unmeasured. |
| P1 | [Can workers complete a task without manual repair? — WORKFLOW357](Research/Plans/WorkflowHCF357.md) | Send 1 bounded task through preparation, execution, and result verification. Record missing inputs, duplicate starts, and manual interventions. | Which handoff steps can run unattended, and which still need correction? | LittleDog preparation contract and BigDog-NUIAK capacity report. |
| P1 | [Which visual cue causes our remaining errors? — FOCUS355](Research/Plans/Focus355.md) | Change 1 cause at a time: artwork, control size, focus effect, position, or scrolling. Measure misses and false changes. | Should the next correction change training examples, visible detail, or how the model combines evidence? | Use the individual tests below. Reuse completed comparisons. |
| P2 | [When do Apple Vision tools add useful evidence? — VISION353](Research/Plans/Vision353.md) | Compare text recognition, rectangles, similarity, tracking, and selected combinations on the same labeled screens. Measure errors and runtime. | Which tools correct errors, which introduce errors, and which cost time without helping? | Use the individual tests below. |
| Stretch | [Can a backup actually restore our experiment? — HCF357](Research/Plans/WorkflowHCF357.md) | Restore a dataset part and saved training state on another machine. Check hashes and repeat the recorded evaluation. | Can we recover useful data and results before removing a local copy? | Qualified destination, reserved capacity, and retention owner. |

## PROGRAM384 proposals — await maintainer selection

Source: [PROGRAM384](Research/Plans/ExperimentProgram384.md). C1, D1, and the HCF375C successor have new approved jobs.
Owner for all tracks: Maximum-mini-NUIAK. R4 and A3 also need Maximum-mini-TTR app behavior.

| Track | Items in priority order | Depends on | Authority |
| --- | --- | --- | --- |
| 0 Repair | R1 complete: the model is internal and experimental. R2: HCF375C replaces unrun HCF375/B. R3: crop intake rejects label conflicts and groups identical decoded pixels. Replays remain open. R4 remains open. | — | Existing |
| D Transitions | D1 control × 3 seeds for the churn floor; D2 notification correction × 3 seeds; D3 content negatives matched in magnitude; D4 effect-mask target | D2 needs D1. D4 needs A1 | Standing training approval |
| B Rules | B1 measure `resolveTVOSFocus`; B2 analyze the outline rule's 25 wrong selections; B3 pair-difference rule; B4 calibrated rule-first cascade | B4 needs C3 | Existing |
| A Labels | A1 L0/L1 agreement on HCF371; A2 effect geometry; A3 visibility survey of other families; A4 no-focus scenes | A3 and A4 need Fixture capture | Capture needs the Simulator target check |
| C HCF models | C1 miss analysis; C3 calibration on the calibration role; C2 learning curve; C4 cross-profile matrix; C5 crop-centric storage | C2 and C4 after C1 | Standing training approval |
| E tvOS detector | E1 real-screen error taxonomy; E2 640 vs 1280 px inference; E3 diversity vs volume fine-tune; E4 capture-artifact augmentation | E3 after E1 | Standing training approval |
| Gated | Pretrained features, contrastive pretraining, Siamese architecture, pseudo-labels, RT-DETR, HCF stages larger than 1 GPU-hour | Maintainer approval | New authority |

## Queue rules

- Unblock approved experiments before adding unrelated experiments. Keep independent jobs running.
- If human action is required, name the exact action, affected jobs, and restart condition immediately.
- Use the current preparation priorities above. Preserve the execution order of already approved jobs.
- Show the test and the decision before implementation details.
- Name the behavior under test, not only its project ID.
- Describe what changes, what stays fixed, and which errors we count.
- State the question that the result answers. Do not present a hoped-for improvement as a result.
- Separate preparation checks from model experiments. File delivery alone does not show model improvement.
- Keep only unfinished acceptance checks in this file.
- Move completed checks and their results to `CompletedTasks.md`.
- Keep blocked work visible with the missing input and responsible owner.
- Do not count blocked plans as ready experiment jobs.
- Keep proposals separate from approved execution.
- Preserve previous successes, data roles, budgets, and model gates.
- Reconcile older open work before dispatch. Do not rerun experiments because an old checkbox remains open.

## Open acceptance checks

### HCF374 — Do repeated images waste storage or distort training?

Maximum-mini-NUIAK owns [the duplicate audit and TTR requirements](Research/HCF374Duplicates.md).
The existing runner accepts 4 bounded audits without interrupting HCF371.
The first 2,000 admitted frames have 2,000 distinct pixel identities across 250 scene groups.

- [ ] Review the Vision controls. Would similarity filtering discard genuine focus changes or HCF differences?
- [ ] Qualify TTR's duplicate fix after active capture finishes. Require separate event records and reusable payload references.

No file deletion, membership change, app replacement, or automatic promotion occurs in this audit.

### FOCUS373 — adopt graph experiments without duplicating work

HCF371 remains first. [The graph review](Research/Plans/Focus360.md#graph-v1-adoption--focus373-2026-10-13) defines controls, inputs, decisions, and limits.
The first 15 jobs have 14 completions. The final previous-success report remains queued behind HCF work.
Nine follow-up jobs now pass readiness checks and enter the approved queue. HCF371 has explicit execution priority.
The live dashboard now separates completed outcomes. See the execution update for results and remaining requirements.

- [ ] **B — Which position and condition combinations are missing?** Prepare matched native movement, content-only, boundary, and scroll cases.
- [ ] **C — Can conflict-aware updates preserve movement?** Use E01 evidence to select 1 correction against unchanged training.
- [ ] **D — Does teacher retention add value?** Compare rehearsal alone with rehearsal plus distillation using training-eligible inputs only.
- [ ] **E — Does an improvement repeat?** Repeat 1 promising comparison with matched seeds within its recorded budget.
- [ ] **F — Does targeted generation save useful work?** Compare uniform and failure-targeted selection at equal data and training budgets.

### FOCUS373 software tasks — outside the experiment queue

- [ ] **ENG1 — Preserve evaluation identity and roles.** Extend current manifests and FOCUS372-ENG3. Reject role leakage and changed inputs.
- [ ] **ENG3 — Prepare native capture successors.** All 7 original requests pass offline compilation. Set the approved local target in new requests.
- [ ] **ENG3 — Qualify capture inputs.** Check seeds, storage, target ownership, and visible changed factors after HCF releases the target.
- [ ] **ENG4 — Measure time to a decision.** Extend existing events and compact messages. Keep inconclusive outcomes and report missing timing evidence.

Maximum-mini-NUIAK owns these tasks. All 7 supplied requests currently mark data as calibration-only; preserve those original files.
Do not use their images for training. A new training producer requires explicit roles, independent groups, and qualified native labels.
The notification candidate keeps the dimmed corner but loses 6 previous successes. Diagnose those cases before another training correction.

### FOCUS372 — adopt the useful TTR handoff changes

HCF371 remains first. [The updated FOCUS360 plan](Research/Plans/Focus360.md#handoff-adoption-update--focus372-2026-10-13) maps the handoff to existing investigations.

- [ ] Get sender cleanup confirmation for `focus372-20261013-v1`. The exact receipt is published and verified.
- [ ] Prepare HCF control-family coverage after the first HCF371 decision. Preserve its frozen groups and current runner.
- [ ] Prepare matched artwork/focus, selected-tab, and identical-row comparisons under E04. Validate each requested rendering change first.

### FOCUS372 software work — outside the experiment queue

These are implementation tasks, not additional runnable experiments. Maximum-mini-NUIAK owns them unless stated otherwise.

- [ ] **ENG1 — Read compact captures correctly.** Use the received raw `is_focused` and `rendered_body_geometry` fields. Require consumer parity and fail on missing geometry.
- [ ] **ENG2 — Reject unsupported generation requests.** Validate override names and changed factors before dispatch. Ask TTR only for controls absent locally.
- [ ] **ENG3 — Report complete gains and losses.** Extend existing reports. Require all comparisons and zero lost retained successes before candidate advancement.
- [ ] **ENG4 — Make bounded failure requests.** Add validated case-linked requests through the existing coordinator. Keep delivery separate from execution approval.

The plan defines inputs, acceptance tests, owners, and dependencies for each task. No new scheduler, automatic promotion, or navigation authority is proposed.

### HCF371 — execute the native HCF comparison graph

Maximum-mini-NUIAK freezes the study. The background runner executes 34 approved jobs without chat supervision.
See [the plan](Research/Plans/HCF371.md) and [the corrected graph](Research/ResearchSpecs/HCF371-r4/graph.json).

The initial rules find all 12 retained HCF states correctly and abstain on all 12 Standard states.
These related cases do not establish general accuracy. The larger matched comparison remains queued.
Simulator cannot write directly to USB. The first failed capture restores state successfully.
The installed Simulator does not honor its documented stdout option. The second failed attempt also restores state.
The corrected jobs stage 1 screenshot locally. The worker verifies the USB copy before removing that exact temporary screenshot.
The original specifications and failed evidence remain unchanged. The corrected graph reuses both completed reports.
Revision 4 also keeps Fixture's required outer theme unchanged. Composition colors supply the separate dark and light backgrounds.

- [ ] Freeze a justified candidate before final audit. Qualify deployable proposals, the production regression suite, and Core ML conversion separately.
- [ ] If training times out while loss improves, qualify longer execution and checkpoint resume before continuation.

Result (`hcf371r5-92-decision`, 264 development frames): rule 62 correct and 25 wrong; retained model 63 and 5; crop candidate 137 and 0; detector 134 and 0.
Both learned candidates trained on HCF frames only. No model is accepted, and the final audit stays closed. Successor: HCF375C.
Keep original captures on verified USB. Retain matched Standard images and all failed evidence.
Training permits 30 epochs and 1,800 s per candidate under the unchanged runner. A timeout does not become a successful run.
No automatic promotion or navigation authority follows from queue completion.

### HCF361 — qualify updated capture features separately

Maximum-mini-NUIAK owns preparation. The background runner completes all 6 HCF370 jobs.

- **Test:** Change focus to the other corners, move controls centrally, and exchange artwork in separate matched captures.
- **Decision:** Does each change preserve a repeatable HCF difference near the observed focused control?
- **Evidence:** Each producer supplies 8 native frames, profile receipts, body bounds, and verified restoration.
- **Limits:** Each job keeps the 800 s and 100 MB limits. Each capture also permits 1 GiB of native receipts.
- **Data role:** All related images remain development data. No inspected image enters a final audit or training set.
- [ ] Qualify the updated Maximum-mini-TTR app separately when this capture batch ends.

HCF369 verifies spatial differences on all 6 earlier focused states. Recovery no longer blocks capture.
All 3 HCF370 captures finish with verified cleanup. All 3 comparisons pass on another 24 native frames.
The changed artwork, central positions, and opposite corners preserve the measured native cue.
See [the completed results](Research/HCF369Results.md). These inspected cases stay development-only.
The checkout is at `a9b3412c`. Capture retains the previously qualified app and helper; source updates do not replace them.
The new source adds recovery, storage accounting, and more precise checks for clipped Settings rows.
Use those controls after local qualification. Do not replace the app during an active capture.

### Lower-priority reserve — longer experiments with a clear decision

The maintainer approves adding these items to the backlog. This section reuses existing studies rather than creating duplicate assignments.
These are preparation tasks, not ready jobs. Do not count them as executable capacity before their inputs and entrypoints pass checks.
Maximum-mini-NUIAK owns preparation and acceptance. BigDog-NUIAK can execute approved GPU jobs after input and capacity checks.
The budgets below are planning ceilings, not measured runtime estimates or new grants for unavailable resources.

| Priority and existing task | Test | What will the result decide? | Prerequisite and planning budget |
| --- | --- | --- | --- |
| P2 — HCF357 data stages | Compare 1,000, 5,000, and then 20,000 accepted HCF frames with fixed evaluation groups. | Does more independent training data improve selection, or does a specific control family need another method? | Qualified OS HCF data and a useful first baseline. Use the existing 24 GPU-hour scale allocation, not another allocation. Stop expansion after 2 stages without useful gain. |
| P2 — FOCUS363 C repeatability | Repeat the useful HCF detector and crop-classifier configurations with 3 seeds total. | Does the improvement repeat, or depend on initialization? | Select configurations before repeats. Use the existing 12 GPU-hour seed allocation. Report paired results and variation, not only the best seed. |
| P2 — FOCUS363 D native correction | Compare frozen and trainable feature branches on new native training pairs with matched content negatives. | Can native examples correct the failure that authored position changes did not fix? | New eligible training groups; exclude inspected native cases. First run the existing gradient diagnostic. Plan 2 runs, each up to 4 GPU-hours. Confirm the applicable budget before dispatch. |
| P2 — FOCUS363 F weak-group training | Compare equal group sampling with a loss that gives weak groups more influence. | Can weak conditions improve without losing movement or prior successes? | Verified groups and a useful baseline. Plan 2 matched runs, each up to 4 GPU-hours. Freeze group definitions before fitting. |
| P2 — RESEARCH340 D1 effect curriculum | Compare strong-to-native effect training with native-strength-only training at equal update counts. | Do stronger early effects help native recognition, or teach a synthetic shortcut? | Qualified renderer controls and separate native evaluation. Plan 2 matched runs, each up to 4 GPU-hours. Do not use authored effects as OS HCF labels. |
| P2 — FOCUS359 native families | Generate new families and reserve whole families before training. Compare matched scene factors and model predictions. | Do improvements transfer beyond familiar templates and artwork? | Qualify local TTR families first. Plan a resumable producer with a 90 min ceiling and bounded shards. Measure a pilot before choosing the frame count. |
| P2 — FOCUS360 temporal diagnosis | Capture ordered movement, scrolling, animation, and interruption sequences. Compare causal stability rules with pair scores. | Which failures require history rather than another image-pair correction? | Verified times, focus observations, and restoration. Plan a 60 min producer and a 30 min replay. Train no temporal model unless simple rules leave repeatable errors. |
| P3 — FOCUS360 E02 weight interpolation | Test the 3 predefined weight blends between compatible checkpoints. Reuse the completed output-blend rejection. | Can related weights preserve gains where their output scores cannot? | E01 must justify this test. Plan a 30 min batch with full retained comparisons. Do not tune coefficients against final evaluation. |

Each prepared item needs named inputs, hashes, an executable producer, storage limits, dependencies, and a complete comparison report.
Use the existing 250 GiB HCF study ceiling. Reserve remote capacity separately. Do not sum planning budgets into automatic execution authority.
Keep 800 s and 100 MB defaults for small diagnostics. Longer jobs need their explicit frozen budget before submission.
Prepare input checks and downstream comparisons while producers run. Do not wait for an empty queue to prepare the next stage.
If a condition fails, queue the supported diagnosis rather than repeat the same training run.
Do not extend a completed run merely to occupy hardware. A continuation needs improving loss, saved resume state, and a fixed question.

### FOCUS366 — preserve movement while learning notification changes

Owner: Maximum-mini-NUIAK. Priority: P0. Status: both arms rejected (`focus373-repair-decision-v2`): control 301/392 correct with 22 lost; notification 342/392 with 6 lost. Next: FOCUS373-LOSSES and PROGRAM384-D1 in the groomed table.
The [frozen plan](Research/Plans/FocusNotification366.md) defines the 81-job graph and its final checks.
All 9 generation shards and admission pass. The 252 fresh pairs contain no exact RGB matches with the 392 development pairs.
The [completed graph results](Research/FocusGraphs364Results.md) provide the exact failures and the retained comparisons.

| Test | What will the result answer? | Required input |
| --- | --- | --- |
| Generate matched notification examples on Settings and dialog layouts. | Can a correction reject notification changes without missing focus movement? | New training artwork groups and a frozen recipe. Keep the 392 inspected pairs as development comparisons. |
| Pair those examples with dimmed corner movements. | Can the correction preserve `artwork-s1-focus_maze-005` and the other previous successes? | Same initialization, training budget, crop path, and thresholds for control and correction. |
| Separate covered controls from visible controls. | Should an interruption cause abstention instead of a confident stable decision? | Preserve the measured overlay geometry and add explicit visibility labels. |
| Run the full retained comparison after training. | Does a candidate improve the target without losing old successes elsewhere? | Frozen original suite plus FOCUS364 and FOCUS365 development comparisons. |

- [ ] Complete 28 comparisons per run. Preserve the exact dimmed-corner movement and all retained FOCUS329 successes.
- [ ] Check the union of earlier correct decisions from FOCUS329, gamma348, and movement349 on the 392 pairs.

The coordinator stores structured update `nuiak-focus366-notification-training-02` at cursor 501. TTR forwarding remains unconfirmed.
Native OS HCF stays under HCF361–362. Authored outlines do not replace OS HCF evidence.

### FOCUS363 — turn the methodology review into useful model decisions

The [work packages and technical plans](Research/Plans/FocusLearning363.md) define scope, owners, tests, and decision rules.
Planning is complete. These cards are not submitted experiment jobs or new execution grants.
Reuse existing HCF361 and FOCUS360 tasks; do not create duplicate capture or training studies.
The bounded graph implementation and FOCUS364–365 diagnostics are complete. See [results](Research/FocusGraphs364Results.md).

| Priority | Test | What will the result answer? | Next requirement |
| --- | --- | --- | --- |
| P0 | A: Make native HCF capture reliable. | Can the queue produce repeatable OS HCF examples and restore settings? | Existing HCF362 clipped-row repair and recovery qualification. |
| P0 | B: Audit and fill benchmark coverage. | Can we measure movement misses, appearance errors, and transfer separately? | Retained manifests can be audited now; new native coverage depends on A. |
| P0 | C: Compare HCF rules, crop classification, and full-screen detection. | Does training improve selection beyond existing methods? | Existing HCF361 admitted corpus and frozen comparisons. |
| P1 | D: Test the transition model's remaining restriction. | Does qualified native training resolve failure after authored branch training did not? | Review FOCUS355/356, complete FOCUS360 E01, and prepare eligible native training pairs. |
| P1 | E: Compare pretrained spatial features. | Does a different encoder represent the focus cue more usefully? | Exact model, license, resident weights or approved download, memory check, and bounded run contract. |
| P2 | F: Compare weak-group learning with balanced sampling. | Can training improve weak conditions without suppressing movement? | Reliable groups and a useful C or D baseline; frozen settings and budget. |

- [ ] Complete B's retained-data coverage audit without waiting for A.
- [ ] Complete A through the existing native capture task and preserve failed attempts.
- [ ] Prepare C through the existing HCF study budget and data gates.
- [ ] Register D only when its inputs or tested restriction differ meaningfully from completed branch work.
- [ ] Qualify E before any new download or worker dispatch.
- [ ] Select F only when group support justifies the comparison.

Keep the background runner unchanged during planning. Submit complete comparison chains when their inputs and authority qualify.

### HCF361 — native HCF model prototype

Plan: [Native data, scale, comparisons, and Core ML acceptance](Research/Plans/HCF361.md).
The maintainer makes this study the immediate model priority. Completed preparation appears in `CompletedTasks.md`.

| Order | Test | What will the result answer? | Next requirement |
| --- | --- | --- | --- |
| 1 | Qualify reliable profile checks and visible native effects. | Does repeated capture preserve verified OS state and show the expected control effect? | Build and roundtrip pass. TTR must correct the clipped-row text mismatch. Preserve failed attempts and the recovery guard. |
| 2 | Capture 12 scenes per qualified family, with 4 focus targets, 2 profiles, and repeats. | Is the visible effect repeatable and tied to focus rather than capture noise? | Step 1, fresh target ownership, and verified restoration. Keep this pilot in development. |
| 3 | Generate the first frozen paired corpus. | Can we supply 1,000 unique HCF training frames and separate evaluation groups? | Qualified family, real recipes and assets, connected ancestry, and USB reservation. The 2,720-frame design is prepared. |
| 4 | Compare rules, existing models, and proposal recall. | Which errors must training fix? Does the crop approach receive the focused control? | Done in HCF371, except proposal recall, which remains unmeasured. |
| 5 | Train the crop and full-screen candidates at equal budgets. | Which approach improves matched selection without losing previous successes? | Done in HCF371 (HCF frames only). Successor: HCF375C. |
| 6 | Test scaling, then export the selected candidate to Core ML. | Does the gain repeat and survive Apple conversion? | Useful first-stage result, frozen audit, preserved successes, and runtime parity. No navigation authority. |

The 1,000-frame design reserves 250 training groups and 30 groups for each separate evaluation role.
The maintainer approves native capture. HCF training requires the enabled OS setting, not authored borders or artwork themes.
The proposal review stays in HCF361. Keep its 7 blocks and existing budgets; do not create a competing reset queue.
Simulator-to-Office equivalence remains unproven. Keep the Office journey in development and report its results separately.
These are requested groups, not proof of independent evidence. Connected template and artwork checks still apply.
Keep existing HCF358 planning specifications unchanged. Create executable successors only after their exact inputs qualify.

### FOCUS360 — choose corrections from the 2 research proposals

Plan: [Test design, proposal review, and peer requests](Research/Plans/Focus360.md).
These cards are preparation work, not ready queue jobs. Keep the background runner unchanged.

| Priority | Test | What will the result answer? | Next requirement |
| --- | --- | --- | --- |
| P0 | E01: compare gradients from movement and content-only cases. | Do the training updates work against each other? | Prepare a local read-only entrypoint. Checkpoints and membership are present. |
| P2 | E02: test compatible weight blends only if E01 supports them. | Can we preserve gains without losing movement detection? | Structure checks pass. Output blending already fails to recover the native misses. |
| P0 | E04: cross artwork changes with focus movement on native screens. | Does artwork hide or imitate the focus change? | Reuse local endpoint cases. Prepare a mutation-based producer for the remaining comparison. |
| P1 | E03: test 1 correction against unchanged training. | Does a justified retention method preserve previous successes? | E01 findings and a frozen training configuration. |
| P1 | E05: compare original crops with added usable boundaries. | Do proposals or crops remove the evidence the model needs? | Reuse existing coverage reports and identify remaining gaps. |
| P1 | E06: compare causal rules on 2-frame and 4-frame sequences. | Which failures require timing or more frames? | Local intervals lack precise settling labels. Extend the existing timed producer. |
| P1 | E07: compare targeted examples with uniform examples. | Which data improves the model faster at equal cost? | Qualified failure cases and fixed selection rules. |
| P1 | E08: compare Standard training with HCF-assisted training. | Can HCF help when deployed images use Standard mode? | Verify visible HCF effects and matched Standard counterparts. |
| P1 | E09: audit independent support for stability claims. | Which error claims need more independent evidence? | Reuse BD18 and compatible qualified predictions. |
| P2 | E10: test separate native screen families. | Do gains transfer beyond familiar layouts and artwork? | Check shared sources and freeze eligible groups. |

- [ ] Prepare E01 locally. Use optional BigDog-NUIAK feedback without making it an input dependency.
- [ ] Prepare the remaining controlled-mutation comparison using TTR's received capability matrix and retained `size-1` case.
- [ ] Convert qualified cards into tested queue jobs with pinned inputs and explicit limits.
- [ ] Review results before selecting conditional training. Preserve previous successes and final-audit exclusions.

The [local audit](Research/Focus360LocalAnswers.md) answers the checkpoint, retained-case, timing, and output-blending questions.

### Dashboard descriptions — live deployment pending

- [ ] Load the updated dashboard during a safe server restart. Do not stop active experiments to apply this display change.

**Check:** Confirm that rows, the current-task panel, and the inspector explain the test and the question it answers.
**Decision:** Is the live page using the tested display code? The static export already includes the descriptions.
The live server retains its imported code. Reloading the browser alone does not update that code.

Expand a task to read its remaining checks. The first groups contain current work.
Older follow-ups remain open until their evidence supports closure or replacement.
The archive preserves their original context, acceptance criteria, and restrictions.
This cleanup does not approve new work or change execution limits.

The HCF study retains its 48 GPU-hour, 50,000-frame, and 250 GiB limits.
The macOS work waits for the iOS DS-G8 gate.
ScreenAuditKit changes require assignment in that repository.
Git history changes require the maintainer's explicit approval.

## FOCUS359 — native family experiments and efficient input storage

<details>
<summary>4 open checks — expand details</summary>

Plans: [Plan and 20-proposal review](Research/Plans/Focus359.md).

- [ ] Review TTR's independent field mapping and supply 1 existing read-only consumer specification. File receipt and shared-copy cleanup are complete.
- [ ] Standard artwork counterpart: merged into the single open TTR request under FOCUS358 / HCF358.
- [ ] Turn qualified hero-swap, selected-tab, identical-row, and corner recipes into executable producer successors.
- [ ] Review FOCUS358 and FOCUS359 complete reports before any further training or storage changes.

</details>

## FOCUS358 / HCF358 — duration comparison and complete HCF queue graph

<details>
<summary>3 open checks — expand details</summary>

Plans: [Plan](Research/Plans/Focus358.md).

- [ ] Receive the Standard counterpart of the unmatched artwork row from TTR (the single open request). Image-card visibility is already qualified (HCF368–370).
- [ ] Test storage reduction before 20,000 or 50,000-frame collection exceeds the 250 GiB limit.
- [ ] Receive BigDog-NUIAK capacity and LittleDog preparation contracts. Do not assume remote execution or backup readiness.

</details>

## WORKFLOW357 / HCF357 — reliable queue and substantial HCF study

<details>
<summary>8 open checks — expand details</summary>

Plans: [Approved plan](Research/Plans/WorkflowHCF357.md).

- [ ] W4: obtain LittleDog's qualified preparation contract and complete one read-only task.
- [ ] W5: complete one coordinated handoff through independent verification.
- [ ] H2: qualify producer quota and offload behavior with TTR. Visible HCF is qualified for image cards only (HCF368–370).
- [ ] H4: implement and verify full training resume before longer detector/classifier runs.
- [ ] H5: execute both approaches within 48 GPU-hours and compare retained successes.
- [ ] H6: qualify Core ML candidates and optional TTR shadow use.
- [ ] S1–S5, stretch: qualify backup storage, queue backup/restore, test recovery, then enable safe retention.

</details>

## FOCUS355 — position and branch learning

<details>
<summary>18 research questions — expand tests and expected answers</summary>

Plans: [Plan and 20 ranked problems](Research/Plans/Focus355.md).

Each test below retains the input requirements and limits in the linked plan.
These questions are not claims that every test is ready to run.

- [ ] **P03 — Artwork changes without focus movement.** Exchange artwork while focus stays fixed. Match the amount of pixel change to real movements. **Answer:** Does the model recognize focus, or merely large image changes?
- [ ] **P04 — Learn strong effects before subtle effects.** Compare training that starts with exaggerated growth against training using only normal-strength effects. Use equal training budgets. **Answer:** Does easier early training help the model recognize subtle native effects?
- [ ] **P05 — Small controls versus thin effects.** Change control size and effect width separately. Keep backgrounds and original-resolution crops fixed. **Answer:** Do misses come from small controls, thin effects, or detail lost during resizing?
- [ ] **P06 — Separate growth, shadow, and border.** Show each effect alone, then in combinations absent from training. **Answer:** Can the model combine useful cues, or does it memorize familiar combinations?
- [ ] **P07 — Identical neighboring posters.** Move focus between identical posters and vary their spacing. Count wrong locations as well as missed changes. **Answer:** Can the model locate focus without using artwork differences?
- [ ] **P08 — Bright decoration on unfocused controls.** Add borders, badges, and shadows while actual focus stays fixed. **Answer:** Which decorations cause false selections or false focus changes?
- [ ] **P09 — Controls partly outside the screen.** Move controls toward screen edges in measured steps. Record full and visible bounds. **Answer:** How much clipping makes detection unreliable?
- [ ] **P10 — Scrolling without focus movement.** Compare scrolling behind fixed focus with focus moving across a stationary screen. Match motion direction and distance. **Answer:** Can the model separate background motion from focus movement?
- [ ] **P11 — A different item inside the same focus box.** Change the selected item while its screen position stays fixed. Record item identity separately from box position. **Answer:** Can we distinguish item changes from movement of the visible focus box?
- [ ] **P12 — Focus during animation.** Capture before, during, and after a focus transition with measured times. **Answer:** When can we report settled focus without declaring readiness too early?
- [ ] **P13 — Missing or stale captures.** Replay duplicated, delayed, missing, and mismatched frames. **Answer:** Does the system reject stale evidence and recover without falsely reporting stability?
- [ ] **P14 — No control has focus.** Compare verified no-focus scenes with matched scenes containing 1 focused control. **Answer:** Can the system report no selection instead of inventing one?
- [ ] **P15 — Modals and loading screens.** Add interruptions over unchanged content. Include harmless overlays for comparison. **Answer:** Does the system notice interruptions without treating every overlay as a focus change?
- [ ] **P16 — Crowded controls.** Change spacing, overlap, control count, and effect width while keeping artwork fixed. **Answer:** Do neighboring effects cause errors that need different training data or better control regions?
- [ ] **P17 — HCF on versus off.** Compare rules and models on qualified, matched profile captures. **Answer:** Does HCF improve focus detection, and does that improvement remain when HCF is off?
- [ ] **P18 — Realistic artwork versus simple placeholders.** Compare equally sized training sets with realistic media scenes and simpler matched scenes. Reserve different artwork for evaluation. **Answer:** Does visual variety improve generalization, or add distraction without useful learning?
- [ ] **P19 — Generated screens versus real apps.** Evaluate fixed candidates on reviewed Office captures and separately reserved app groups. **Answer:** Which improvements survive outside Fixture, and which real failures need targeted examples?
- [ ] **P20 — Confidence when focus really changes.** Compare confidence settings chosen from all pairs with settings chosen from changed pairs. Keep calibration and audit groups separate. **Answer:** Does a reassuring overall score hide missed changes reported as stable?

</details>

## VISION353 — low-priority Vision investigations

<details>
<summary>15 Vision investigations — expand tests and expected answers</summary>

Plans: [Implementation plan](Research/Plans/Vision353.md).

- [ ] **A1 — Available Vision controls.** Check installed requests, versions, and settings on a small retained input. **Answer:** Which controls actually exist, including any model-specific temperature setting?
- [ ] **A2 — Similar-looking screens with different focus.** Compare image similarity, pixel differences, and focus scores on identical labeled pairs. **Answer:** Can similarity skip analysis without missing subtle focus movements?
- [ ] **A3 — Fast versus accurate text recognition.** Compare recognition modes and language correction against reviewed text. Count missing and incorrect labels and measure runtime. **Answer:** Which settings save time without losing useful text?
- [ ] **A4 — Rectangles as extra control candidates.** Compare rectangle detection, the UI detector, and their combined boxes. **Answer:** Do rectangles recover missed controls or mainly add false candidates?
- [ ] **A5 — Read only selected screen regions.** Compare full-screen text recognition with restricted regions and text-size settings. **Answer:** Can we save time without losing small labels or shifting their coordinates?
- [ ] **B1 — Repeatability across Vision versions.** Repeat identical inputs across supported versions and compare scores, decisions, and runtime. **Answer:** Which results can safely share a cache?
- [ ] **B2 — Follow a control across frames.** Track controls through movement, identical neighbors, and temporary obstruction. **Answer:** When does tracking lose the correct control and need fresh detection?
- [ ] **B3 — Remove scrolling before comparison.** Compare original frames with frames aligned to cancel screen translation. **Answer:** Does alignment reduce scrolling errors, or also remove useful focus-growth evidence?
- [ ] **B4 — Detailed motion versus cheap differences.** Compare optical flow with pixel differences on scrolling, growth, and animated backgrounds. **Answer:** Does detailed motion analysis improve decisions enough to justify its runtime and memory?
- [ ] **B5 — Old frames in the cache.** Replay repeated, missing, delayed, and out-of-order frames. **Answer:** Does the system clear stale results before they create false stable decisions?
- [ ] **C1 — Attach text to detected controls.** Compare detector output with output enriched by recognized text. **Answer:** Does text correct control identity, or attach the wrong label to nearby controls?
- [ ] **C2 — Combine tools that disagree.** Compare fixed combinations of similarity, text, tracking, and model scores. Count misses, false changes, and withheld decisions. **Answer:** When should the system trust combined evidence or report uncertainty?
- [ ] **C3 — Make confidence match observed errors.** Adjust score scaling using separate calibration groups and valid raw model scores. **Answer:** Does confidence better predict errors without hiding missed changes?
- [ ] **C4 — Run expensive tools only when needed.** Compare staged execution with running every tool on each recorded episode. **Answer:** How much time can we save without missing events or declaring readiness early?
- [ ] **C5 — Runtime and image orientation.** Compare supported compute settings and image rotations with unchanged preprocessing. **Answer:** Which settings preserve decisions and box coordinates while meeting runtime limits?

</details>

## GENERATION352 — queued Fixture producers

<details>
<summary>2 open checks — expand details</summary>

Plans: [the implementation and results](Research/Plans/Generation352.md).

- [ ] Resolve the settling failure before a revised capture. Do not retry the existing attempt.
- [ ] Complete the 4 comparisons after a complete replacement dataset passes checks.

</details>

## HCF350 — paired HCF queue and TTR pilot

<details>
<summary>3 open checks — expand details</summary>

Plans: [Plan](Research/Plans/HCF350.md).

- [ ] Receive the qualified pilot and source references. Validate every offered pair before preparing executable successors.
- [ ] Bind existing scorers to pinned inputs. Compare profiles, methods, false selections, small controls, and boundary coverage first.
- [ ] Review batch results before selecting additional captures or a training correction.

</details>

## FOCUS349 — movement preservation and Office capture analysis

<details>
<summary>1 open checks — expand details</summary>

Plans: [Plan](Research/Plans/Movement349.md).

- [ ] Compare the supplied source hashes and update the Office audit without assuming command and video counters are equal.

</details>

## FOCUS350 — use real movements to test effect separation

<details>
<summary>7 open checks — expand details</summary>

Plans: [FOCUS349](Research/Plans/Movement349.md).

- [ ] Review the 4 Office disagreements. Keep assistant notes separate from human-confirmed labels and native observations.
- [ ] Freeze separate cases for adjacent growth, edge movement, mixed control sizes, and focus arrival.
- [ ] Check the approved local Fixture before requesting remote capture. Preserve the Office development exclusion.
- [ ] Generate matched movement and content-change examples with fixed artwork, positions, and control sizes.
- [ ] Reuse retained model predictions through exact input and preprocessing checks. Do not repeat unchanged control inference.
- [ ] Select 1 correction only after these cases show the remaining error. Freeze its equal-budget control before training.
- [ ] Require recovered target movements without losing retained successful decisions. Report abstentions and false changes separately.

</details>

## TEST-OWNED-PROCESS — investigate intermittent cancellation wait

<details>
<summary>4 open checks — expand details</summary>

- [ ] Reproduce the saved `NativeOwnedProcess.run` wait after child exit with the existing cancellation test.
- [ ] Inspect the process group and `waitUntilExit()` ordering without changing production behavior first.
- [ ] Test a justified correction with failure, timeout, and cancellation cases.
- [ ] Require one serial suite pass without leaving runner-owned child processes.

</details>

## RESEARCH340 — measured queue and dashboard; controlled inputs pending

<details>
<summary>2 open checks — expand details</summary>

Plans: [Plan](Research/Plans/MeasuredResearch340.md).

- [ ] Complete controlled coverage for the 20 investigations. Each blocked specification names its missing input.
- [ ] Compare at most 3 justified candidates after controlled evidence supports them.

</details>

## FOCUS344 — explain native misses before another correction

<details>
<summary>6 open checks — expand details</summary>

Plans: [R4 and R3](Research/Plans/NativeAppExperiments343.md); [background plan](Research/Plans/BackgroundResearch344.md).

- [ ] Prepare the next fixed batch from that result. Do not repeat rejected crop-size tests.
- [ ] Compare native and authored body height, aspect ratio, effect width, and original-detail occupancy.
- [ ] Prepare one matched-size campaign with the current local Fixture before requesting remote capture.
- [ ] Pin source/build evidence before admitting new training images.
- [ ] Compare fixed native controls with identical and distinct artwork. Keep position and effect fixed.
- [ ] Select at most 1 justified correction with an equal-budget control and all retained regression checks.

</details>

## FOCUS345 — prepare the planned native app experiments

<details>
<summary>4 open checks — expand details</summary>

Plans: [12 scoped experiments](Research/Plans/NativeAppExperiments343.md).

- [ ] Qualify one LUMA capture example before a campaign.
- [ ] Freeze R1–R4 inputs and executable specifications after required observations pass intake.
- [ ] Qualify R5–R10 when navigation, clipping, text, and interruption observations become available.
- [ ] Reserve R11–R12 for multiple qualified app families and measured frame sequences.

</details>

## RESEARCH338 — research queue qualified by exact replay

<details>
<summary>1 open checks — expand details</summary>

Plans: [Plan](Research/Plans/RESEARCH338.md).

- [ ] Add epoch checkpoints if longer runs require them. Current trainers do not support epoch resume.

</details>

## HCF337 — handoffs closed; pilot scorer ready; native truth pending

<details>
<summary>1 open checks — expand details</summary>

Plans: [Plan](Research/Plans/HCF337.md).

- [ ] Score the existing rules and the shipped model on the 48-screen campaign when verified truth exists.

</details>

## HCF333 — High Contrast assistance

<details>
<summary>3 open checks — expand details</summary>

Plans: [Implementation and next comparison](Research/Plans/HCF333.md).

- [ ] Qualify the supported Maximum-mini-TTR profile lifecycle before new native HCF capture.
- [ ] Complete the 48-screen development campaign with independent layout groups and explicit negative coverage.
- [ ] Compare fixed rules with compatible model outputs before choosing 1 learned correction.

</details>

## Older open backlog

<details>
<summary>Earlier follow-ups and platform work — review before dispatch</summary>

These entries retain their existing requirements. They are not a list of ready jobs.
**Not groomed (2026-10-13).** Many entries lack a Machine-Project owner, a controlled comparison, or a decision rule.
Do not dispatch an entry from this section. First move it to the groomed table with all fields. Earlier owner labels are historical.
Check later results before starting an older task. Keep its original acceptance criteria unless the maintainer approves a change.

## Focus improvement program — October 9

<details>
<summary>7 open checks — expand details</summary>

Plans: [ranked contracts](Research/Plans/HeadlessEffectExperiments.md); [FOCUS301](Research/Plans/FocusImprovementProgram.md).

### TTR proposals — not approved for execution

- [ ] **TTR318-A — qualify sequence evidence.** Proposed owner: Sillycon-TTR; NUIAK reviews results.
  Needs human approval. Check actual actions, observed focus, capture timing, errors, and independent model outcomes.
- [ ] **TTR318-B — separate catalog discovery from approval.** Proposed owner: Sillycon-TTR.
  Needs human approval. Use an independently approved hash and test stale, changed, oversized, and unrelated files.
  [Review and acceptance requirements](Research/TTR318Review.md) define both proposals. No worker is dispatched.
### Approved focus work

- [ ] **FOCUS332 — preserve original crops and add boundary evidence.** Proposed; awaiting assignment.
  Owner: Maximum-mini-NUIAK. Keep the FOCUS327 control unchanged and add a zero-initialized correction using boundary crops.
  This experiment increases the detail budget from 2 crops to 4 crops. Measure memory and latency explicitly.
  Test 1 fixed 30-epoch run against every previous-success set. Keep membership, weights, thresholds, and evaluation exclusions unchanged.
  Acceptance: useful native gains without lost previous successes or increased false or missed changes.
  [Inputs, scope, tests, and acceptance](Research/Focus331Results.md#next-substantial-tranche).
- [ ] **FOCUS314 — qualify configurable authored pairs.** Maximum-mini-NUIAK owns intake; Sillycon-TTR reviews the producer request.
  Extend headless308 repairs with explicit pair states and effect controls. Require repeatable pixels, valid geometry, and complete counts.
- [ ] **FOCUS315 — isolate effect visibility.** Maximum-mini-NUIAK owns 216 matched diagnostic comparisons after FOCUS314.
  Score existing models by effect, strength, position, and nuisance condition. Keep ambiguous visual cases separate.
- [ ] **FOCUS316 — compare synthetic transfer.** Maximum-mini-NUIAK owns 3 matched fits after FOCUS315 and FOCUS313.
  Compare original-only, mixed-strength, and strong-to-weak training. Preserve original views and previous-success checks.
- [ ] **FOCUS317 — test diversity before volume.** Maximum-mini-NUIAK owns acceptance; BigDog-NUIAK can run a named portable assignment.
  Requires successful FOCUS316 transfer. Compare 1,024 versus 4,096 pairs under equal updates and unchanged native checks.

</details>

## Active goal — complete Big Dog coordination support / NUIAK

<details>
<summary>3 open checks — expand details</summary>

- [ ] Review useful findings, final answer, stop/recovery, usage, cleanup, and original-attempt release evidence.
- [ ] Support connected operator controls, two-host qualification, independent restore, and explicit cutover after the first useful delivery.
- [ ] Complete exact transfer receipts and sender-owned cleanup through each handoff.

</details>

## Proposed — screen context for focus and navigation / NUIAK

<details>
<summary>5 open checks — expand details</summary>

- [ ] Inventory trustworthy context labels in retained images. Identify missing classes and related evaluation groups.
- [ ] Check whether correct context improves an existing focus failure before training a classifier.
- [ ] Compare fixed OCR/layout rules with one bounded learned candidate when data supports the comparison.
- [ ] Measure downstream focus errors, regressions, unknown results, and runtime cost on matched inputs.
- [ ] If qualification passes, verify Apple inference and propose a TTR observer integration.

</details>

## FOCUS-LOOP / NUIAK — measured repair with local generation (historical; not the current priority)

<details>
<summary>2 open checks — expand details</summary>

Plans: [Execution plan](Research/Plans/EvidenceDrivenFocusQualification.md#highest-priority--focus-improvement-cycle).

- [ ] Test a qualified candidate through TTR on matched navigation tasks. Preserve the current model if any required gate fails.
- [ ] Report whether the selected failure improves without regressions. Select the next failure from the measured results.

</details>

## Review — STORAGE-LIVE-03 / Codex (SSD inputs qualified; tracked r7 cleanup pending)

<details>
<summary>1 open checks — expand details</summary>

Plans: [Implementation plan](Research/Plans/ArtifactStorage.md#storage-live-03--active-ios-dataset-compatibility-next-implementation-tranche).

- [ ] Maintainer untracks old r7 generated export; then inventory/rebind its links and
  reclaim r7 source.39,487tracked files prevent safe automatic cleanup without a huge
  machine-specific diff. [Exact commands](reports/storage/README.md#ios-exports-after-storage-live-03).

</details>

## Review — REFERENCE-TRANSITION-50 / Codex architect (capture/training blocked)

<details>
<summary>1 open checks — expand details</summary>

Plans: [Canonical extension](Research/Plans/FocusTransitionLearning49.md#reference-transition50-continuation).

- [ ] Complete newly authorized8case TTR acquisition and one temporal candidate:
      first case failed81.069s/cleanupTimedOut,7unattempted,0accepted. One supported
      reconciliation retained cleanup; no retry/restart. Request transition50-cleanup.

</details>

## Review — FOCUS-TRANSITION-49 / Codex architect (candidate data blocked)

<details>
<summary>1 open checks — expand details</summary>

Plans: [Contract](Research/Plans/FocusTransitionLearning49.md).

- [ ] Run one candidate only with admitted train/development membership; otherwise
      record exact admission/coverage blockers, not a calibration-trained model.

</details>

## Review — FOCUS-AUGMENTATION-47 / Codex

<details>
<summary>3 open checks — expand details</summary>

Plans: [Approved comparison](Research/Plans/FocusAugmentation47.md).

- [ ] Qualify current producer export and retained native-button/grid-density plans;
      inventory actual row/tab/button implementations and missing aspect/position coverage.
- [ ] Define and obtain scoped approval for exact new training membership and whole-family
      holdouts; keep reviewed61reference images as calibration unless reassigned explicitly.
      Use paired-content focus switches and bright/dark unfocused distractors.
- [ ] Ingest/QA the approved diverse batch and run one matched translation-only comparison
      against FSF003, scoring the unchanged500synthetic/46real and reference challenges.
      Report target recall and wrong selections jointly, with a grouped failure gallery.
      Data admission/capture authority must cover the chosen batch before execution.

</details>

## Review — REFERENCE-BENCHMARK-45 / Codex

<details>
<summary>3 open checks — expand details</summary>

Plans: [Scope](Research/Plans/ReferenceBenchmark45.md).

- [ ] Choose exact reference role; recommended retain the
      61distinct images as development challenge data, not an independent test.
- [ ] Qualify retained smoke export after producer repair, then execute the planned
      native spatial coverage with measured positions; broaden artwork aspect ratios.
- [ ] Build paired-content hard-negative training membership with whole-family holdouts,
      run one justified data comparison and score unchanged synthetic/real challenges.
      New capture/admission/training follows its scoped authority; no unchanged rerun.

</details>

## Review — REFERENCE-IMPORT-44 / Codex

<details>
<summary>3 open checks — expand details</summary>

Plans: [Scope](Research/Plans/ReferenceImport44.md).

- [ ] Exact role/membership decision for reference data.
- [ ] Qualify missing native control families and distributed focus positions.
- [ ] Run fixed-model data-diversity comparison with unchanged existing evaluation
      after new-family admission/held-out membership is designated.

</details>

## Review — TTR-UPDATE-43 / Codex

<details>
<summary>2 open checks — expand details</summary>

Plans: [Scope](Research/Plans/TTRUpdate43.md).

- [ ] Resume export of retained smoke campaigns after writer/access repair; no recapture.
- [ ] Extend native Settings/tab scene coverage and freeze new data-use membership.

</details>

## Review — REAL-TRANSFER-42 / Codex

<details>
<summary>3 open checks — expand details</summary>

Plans: [scope](Research/Plans/RealTransfer42.md).

- [ ] Qualify source/runtime generation of native rows, buttons, tabs and mixed
      artwork scenes; implement executable grouped coverage plan before capture.
- [ ] Resolve native pageControl visible-body versus container supervision; add
      representative new validation membership before the repaired iOS comparison.
- [ ] Execute the resulting scoped generation/training comparisons once new data
      membership and use are approved. Preserve existing real diagnostic roles.

</details>

## Review / source mapping blocked — PROPOSAL-RECOVERY-37 / Codex

<details>
<summary>1 open checks — expand details</summary>

Plans: [scope and fixed experiment](Research/Plans/ProposalRecovery37.md).

- [ ] Map native coverage33 to published TTR source, build locally, and prepare the
  same admitted groups for crop versus full-screen comparison. Execution/admission
  scope remains explicit; diagnostic real frames stay diagnostic.

</details>

## Queued lower priority — LOCAL-SETTINGS-MAP-35 / Codex

<details>
<summary>3 open checks — expand details</summary>

- [ ] Build/launch current local TTR with its matching helper/runner; record source
  and runtime identity. Resolve concrete signing/dependency blockers if encountered.
- [ ] Run supported bounded read-only Settings traversal on the explicit Simulator;
  preserve settings values, unknown-context stops, omissions and cleanup evidence.
- [ ] Export Markdown/Mermaid graph and coverage ledger; distinguish partial mapping
  from exhaustive/repeatable navigation. Send sanitized findings to TTR using the
  existing shared handoff, with exact artifact transfer scope if required.

</details>

## Review / producer readiness blocked — NATIVE-TRANSITIONS-34 / Codex

<details>
<summary>1 open checks — expand details</summary>

- [ ] TTR resolve4scroll_moved after endpoints: requested item-1 versus observed
  item-2, verified=false/is_settled=false/stableMilliseconds=0. Replay corrected
  evidence after source-contract repair; request `nuiak-20261002-transition34-native-readiness`.
  [Handoff](reports/work/NATIVE-TRANSITIONS-34/handoff.md).

</details>

## Review / capture qualification pending — SETTINGS-BRIGHTNESS-33 / Codex

<details>
<summary>1 open checks — expand details</summary>

Plans: [brightness33](Research/Plans/SettingsBrightness33.md).

- [ ] Qualify actual grid captures/export and map to the48case comparison intent;
  planner success does not complete runtime/data admission.

</details>

## Review / producer evidence blocked — ACCESSIBILITY-ASSISTED-29 / Codex

<details>
<summary>2 open checks — expand details</summary>

Plans: [Evidence, consumer contract and priorities](Research/Plans/AccessibilityAssistedFocus29.md).

- [ ] Coordinate TTR profile inspect/apply/verify/restore support and shortcut feasibility;
  qualify contrast/transparency/motion individually before combined profiles. Switch
  Control remains a discovery spike with scan/input-focus distinction and verified exit.
- [ ] Qualify ordinary-body geometry and focus with human samples against a plain-Vision
  baseline; obtain explicit data-role/admission decision, then replay real FDR036 pairs.
  Fresh physical capture and model execution retain applicable authorization.

</details>

## Review / next — SETTINGS-STABILITY-23 / Codex

<details>
<summary>1 open checks — expand details</summary>

- [ ] Validate beyond two real focus moves before runtime integration/promotion.
  Completed33correct/0wrong/15abstained comparison,9/9guarded generated stress,
  action accounting and105Python/134Swift tests:
  [handoff](reports/work/SETTINGS-STABILITY-23/handoff.md).

</details>

## Review / next — FOCUS-RECORDED-STRUCTURAL-22 / Codex

<details>
<summary>1 open checks — expand details</summary>

- [ ] Human sample acceptance: one eight-frame grouped, prefilled queue across all
  four appearance families; choose source role before exact admission/encoding.

</details>

## Review — FOCUS-CAMPAIGN-INTAKE-19 / Codex

<details>
<summary>1 open checks — expand details</summary>

- [ ] Apply the single campaign command to the pending actual48case producer export,
  then obtain one sampled human review. No new data advertised as of04:17UTC.
  Preserve calibration/source ancestry; admission/training is a separate decision.

</details>

## Next — after FOCUS-LOCAL-PLAN-18

<details>
<summary>2 open checks — expand details</summary>

- [ ] Receive existing48appearance+16transition captured data exports. Updated local
  helper now passes48case planner/consumer parity and deterministic/rejection checks;
  no need for a producer build or repeated capture. Full local generation/export
  remains unqualified; exact source revision still needed for reproducibility.
- [ ] Resolve retained Vision helper file access: exact original pair retry now fails
  before_preflight/access_denied/NSCocoaErrorDomain513; no sidecar or importer result.
  Request supported grant/IPC path, not restart/recapture. [Evidence](reports/work/FOCUS-LOCAL-PLAN-18/handoff.md).

</details>

## Next — after FOCUS-INTERRUPTIONS-17

<details>
<summary>2 open checks — expand details</summary>

- [ ] Receive the first four structural-family proof originals and exact published
  TTR repair revision afterbdfac475; build locally from Git, not a producer binary.
  Historical02:16:17UTC report of four passed is superseded by the02:55UTC report
  of48appearance+16transitions verified locally. Consumer acceptance still awaits
  delivery; follow the existing18 captured-data request, not a new capture request.
- [ ] Before interruption training admission, resolve overlay settling/focus ownership,
  two fullscreen baseline verification mismatches and image/observation-time binding.
  Retainedr2 diagnostics complete:20frames,168members,447crop checks;98covered/removed
  bodies excluded;8not-settled;6unique screens. Do not recapture unchanged originals.
  [Findings](reports/work/FOCUS-INTERRUPTIONS-17/handoff.md).

</details>

## Review — FOCUS-VISIBILITY-16 / Codex

<details>
<summary>1 open checks — expand details</summary>

- [ ] Resolve actual source revision: configured local TTR master46dce7b and fetched
  simulator-harvest967d585 lack CorpusCoverageRequest.swift. Requested branch/commit
  or commit/push only; no Git writes or dirty-checkout replacement. The historical
  zero-pair failure is superseded by producer02:55UTC completion claims; actual
  running planner verification passed in18. Source identity remains unresolved.

</details>

## Review — FOCUS-HANDOFF-15 / Codex

<details>
<summary>1 open checks — expand details</summary>

- [ ] Sync TTR source through Git and build/test locally; request only a producer
  commit/push and branch/commit identity if needed, never a build or binary handoff.
  Coverage planning is already verified by18; do not repeat it as unfinished work.
  Qualify generation/resume/export separately when exact source/runtime inputs exist.
  Keep existing async captured-data intake usable; preserve checkout/runtime permissions.

</details>

## Review — FOCUS-STRUCTURE-14 / Codex

<details>
<summary>1 open checks — expand details</summary>

Plans: [plan](Research/Plans/FocusStructure14.md).

- [ ] Receive first four measured structural proofs plus producer digest vectors
  and a clipped-scroll inventory example; qualify live geometry/membership before
  expanding production collection. TTR self-service generation/export remains parallel.

</details>

## Next — structural coverage after FOCUS-INTAKE-13

<details>
<summary>2 open checks — expand details</summary>

- [ ] Decide source role/exact admission for new25pairs only if useful for the next
  changed-data experiment. Six sampled checks are human-approved October1PDT;
  [acceptance](reports/work/FOCUS-INTAKE-13/sample-acceptance.md). No automatic
  training or independent-test designation. This is not the missing structural diversity.
- [ ] TTR structural successor: first prove composite card, ranked row, home icon and
  hero with explicit whole-control/child geometry; then planned48pair matrix. Existing
  request `nuiak-20261001-transfer10-coverage`; no new runtime dispatch in this tranche.

</details>

## Deferred backlog — DIVERSE-UI-CORPUS (not current critical path)

<details>
<summary>13 open checks — expand details</summary>

Plans: [UI component intake](Research/Plans/UIComponentIntake.md); [Canonical contracts, sheet budgets, exact crop rules and prompts](Research/Plans/GeneratedMediaAssets.md); [Canonical plan](Research/Plans/DiverseNativeUICorpus.md).

### Review — UI-SOURCE-177 / Codex (2026-10-05)

- [ ] UI-IMPORT-A — first Apple media screen + SwiftUI-Kit control adapter; exact
  source/notices, deterministic content, offline build and observed geometry/intake.
- [ ] UI-IMPORT-B — ParallaxView custom-focus cell; resource/license review, transformed
  body/glow/clipping audit, native before/after intake; depends baseline adapter.
- [ ] UI-IMPORT-C — minimal Swiftfin/dependency closure or isolated shelf/picker,
  plus separately scoped iOS Catalog styles; no player/server import by default.
- [ ] UI-IMPORT-D — source-separated batched corpus and matched data-only utility
  comparison after adapter acceptance; immutable lineage/holdouts and retention gates.
### Low-priority companion — generated media artwork (2026-10-05)

- [ ] ART-A — proposed TTR producer ownership; NUIAK reviews interchange: freeze sheet/asset manifest and inspect existing TTR import
  contract; implement deterministic crop/validation CLI with real entrypoint and
  collision/geometry/ancestry tests. No generation or producer edits.
- [ ] ART-B — proposed TTR producer ownership: reviewed development-only pilot, at most7requests/64assets:
  12posters,16thumbnails,32avatars,4backdrops. Validate every cell, retain originals,
  report yield/cost/time; no automatic retries. Depends ART-A.
- [ ] ART-C — TTR/NUIAK: source-backed asset intake and native browsing/detail
  compositions, matched procedural/generated-artwork pilot and separate layout
  comparison. Producer gaps require its own task. Depends accepted ART-B/runtime.
- [ ] ART-D — proposed TTR asset expansion / NUIAK utility evaluation: expand in small frozen sheet units toward provisional ceiling
  368assets/36totalrequests only after pilot utility review; reserve ancestry groups,
  then one logged data-only evaluation. No implied production promotion or recurring
  generation. Depends ART-C; price/budget recorded at execution.
- [ ] DUC-A — NUIAK: rights-reviewed source/asset register and independent screen-family
  coverage matrix; rank Apple samples, MIT tvOS components, Swiftfin and any actually
  available Ferret-UI2 data. Reject/replace unclear content; preserve notices.
- [ ] DUC-B — TTR + NUIAK: agree and implement one native scene adapter and measured
  per-frame annotation export through existing contracts; verify focus growth,
  clipping, hierarchy and screenshot correlation. Depends onDUC-A source approval.
- [ ] DUC-C — TTR: expand approved source families and seeded appearance/structure
  controls; generate balanced same-content focus pairs with competitors and native
  geometry. Depends onDUC-B; pilot targets are not production qualification gates.
- [ ] DUC-D — NUIAK: integrate all-frame QA plus stratified random and targeted
  prefilled human review, with defect-rate/confidence assumptions and OS/renderer
  requalification. Reuse existing review tooling; validate onDUC-C pilot.
- [ ] DUC-E — NUIAK: group source/layout ancestry before splits, then assign a matched
  data-only comparison on withheld families and separate real-app evaluation;
  retain/reject by predeclared results before scaling or release.

</details>

## iOS platform tasks

<details>
<summary>17 open checks — expand details</summary>

Plans: [iOS platform delivery plan](Research/Plans/iOSPlatform.md).

### TASK-DATA-01: Phase 6a dataset recovery and preservation [!]

- [!] P0-A: bounded recovery review found 0/15,239 expected originals at five documented roots; per-label identity evidence is partially verified (11,415/17,040) but local filesystem stalls prevent completion. See [`P0-A handoff`](reports/work/P0-A/handoff.md); P0-B still needs a recoverable source/copy assignment; authorized P0-C proceeded independently.
- [ ] P0-B (separate assignment): stage and verify recoverable pixels/annotations without overwriting historical artifacts
- [ ] P0-C (fallback): r6 reconstruction and content seal review-ready ([handoff](reports/work/IOS-R6-20260923/handoff.md)). All16,940 members structurally validate under explicit Finder-only auxiliary exclusion; prior14,340 prefix and failed-run evidence preserved. Zero duplicates/leakage; coverage gaps and independent backup remain open. No model inference/training occurred.
- [ ] Record independent test-corpus and training-corpus readiness; uncertain/regenerated identity uses a new corpus version
- [ ] Establish content manifest, retention ownership, and recovery verification before expensive evaluation/training
### TASK-6a-10: Full-frame fixture retraining (41-class iOS) [!]

- [ ] P5-B: freeze eligible manifests and resolved configuration, including the explicit auxiliary role of tvOS examples; retain iOS-only reporting
- [!] Existing development bundles do not establish required class coverage, held-out independence or training eligibility. Source descriptions are not attestation; revalidate exact artifacts at intake.
- [ ] P5-B: identify eligible auxiliary fixture inputs and their platform-specific role; Office is optional, not an iOS baseline prerequisite
- [ ] Blend fixture corpus with Phase 6a synthetic set; retrain from Run 009 `best.pt`, 150 epochs, cosine annealing + warmup
- [ ] Evaluate on TVTestRig `held-out` split **and** synthetic withheld-template holdout
- [ ] Per-class AP50 on toggle and stepperControl ≥ 0.88; badge belongs to the later TASK-BADGE-01 milestone
- [ ] TRAIN-S / TRAIN-F / TRAIN-Q evidence accepted separately; no automatic experiment reruns
### TASK-6a-11: Multi-corpus PyTorch reference eval [~]

- [ ] Populate `real_device_fixture_holdouts`, `production_tvos_system_holdout` when those image+box sets exist (`frozen_regression_suite` now populated)
### TASK-6a-12: Partial-crop robustness fork [ ]

- [ ] Mosaic + random-crop aug (0.6×–1.0× bounding areas) as a **fork**, not the default
- [ ] Frozen partial-crop holdout, never merged into the full-frame holdout
- [ ] Full-frame mAP50 loss ≤1.0 percentage point vs 6a-10; crop mAP50 relative gain ≥15% (zero baseline requires a reviewed gate amendment)
- [ ] Measure and document in `Research/TrainingDataStrategy.md` that resizing a crop to 1920×1080 does not reconstruct missing full-frame context

</details>

## tvOS platform tasks

<details>
<summary>16 open checks — expand details</summary>

Plans: [TTRPerception.md](Research/Plans/TTRPerception.md); [SimulatorDatasets.md](Research/Plans/SimulatorDatasets.md); [model/hardware packets](Research/Plans/ModelsAndHardware.md).

#### TASK-SIM-DATA-01: Independent local simulator dataset lane [ ]

- [ ] SIM-DATA-01: exact local runtime/build/UUID/endpoint record and authorized minimal capture with healthy cleanup
- [ ] SIM-DATA-02: integrated simulator manifest, eligibility, split grouping and frame-correct extraction, verified offline
- [ ] SIM-DATA-03: genuine 42-recipe pilot with complete accounting, overlays, intake and postflight evidence
- [ ] SIM-DATA-04: freeze ≥6,000 visual FocusRing pairs with scene/theme/hard-negative quotas and recovery evidence
- [ ] SIM-DATA-05: separate full-frame tvOS augmentation exports with class/style coverage, lineage and frozen splits
### TASK-6b-R-1: Scale real Apple TV hold-out captures [~]

- [ ] ≥500 held-out real Apple TV screenshots across the app matrix (`dataset/tvos_captures/`, gitignored)
### FOCUS-DET-05: FocusRing v1.0 data + retrain [ ]

- [ ] Benchmark shipped model on the development pilot before scale-up; freeze final evaluation protocol
- [ ] Train/export one explicitly authorized simulator candidate and report six quality gates
- [ ] Compare focus decisions and bounded navigation in TTR; no simulator-only production promotion
- [ ] ≥6,000 eligible labeled pairs through the qualified capture/intake path
- [ ] Mix: `gridMatrix` ≥ 2,000, `mediaShelf` ≥ 1,500, `settingsList` ≥ 1,000, `actionDialog` / `heroCarousel` / `focusMaze` ≥ 500 each
- [ ] ≥ 20% `light` and ≥ 20% `highContrast` in `gridMatrix` + `mediaShelf`
- [ ] Held-out hard-negative n ≥100 across `light`/`highContrast` × `imageView`/`collectionItem`; every combination nonempty with separate counts/results
- [ ] ALIGN-A/B: separately assigned ADR-0007 semantic alignment dataset/policy remains open; it is not a prerequisite for physical visual-focus capture or training
- [ ] All six quality gates, including **non-vacuous** hard-neg FPR ≤ 0.5%
- [ ] Replace bundled `.mlmodelc` only after those gates pass

</details>

## Shared integration and later models

<details>
<summary>13 open checks — expand details</summary>

Plans: [model packets](Research/Plans/ModelsAndHardware.md); [model packets](Research/Plans/ModelsAndHardware.md#uni-a--unified-model-experiment-readiness).

### TASK-INTEGRATION-01: Incremental TVTestRig compatibility [ ]

- [~] Record supported producer versions and actionable incompatibility reports on each relevant change; the 2026-09-19 layout-v1/sourceDescription reconciliation is review-ready in [`reports/work/INTEGRATION-RECONCILIATION/handoff.md`](reports/work/INTEGRATION-RECONCILIATION/handoff.md)
- [ ] P4-L: validate one genuine completed bundle once export prerequisites are met; any new Office operation requires renewed user authority
### TASK-BADGE-01: Versioned badge taxonomy and later model [ ]

- [ ] Define notification/status dot/count badge semantics and append category ID 41 without changing IDs 0–40
- [ ] Version taxonomy/library/dataset and make decoding use each model's declared category map
- [ ] Preserve legacy 41-class annotations/models and add producer/consumer compatibility fixtures
- [ ] After the 41-class milestone, generate paired badge annotations and train a separately identified 42-class candidate
- [ ] Badge AP50 ≥0.88 on supported holdouts plus applicable full-frame gates; report existing classes separately
### Phase 6b-U: Unified iOS + tvOS model [ ]

- [ ] Train a platform-balanced unified candidate
- [ ] No platform loses > 2 pt mAP@0.5 vs its dedicated model on identical holdouts
- [ ] tvOS `tabBar` AP ≥ 0.80 and no toolbar confusion
- [ ] tvOS focus P/R within 2 pt of dedicated model or FocusRing
- [ ] iOS FP does not rise on bottom chrome, status bar, home indicator, Dynamic Island
- [ ] Latency and size stay in budget

</details>

## macOS platform tasks

<details>
<summary>7 open checks — expand details</summary>

Plans: [MAC-A](Research/Plans/ModelsAndHardware.md#mac-a--macos-coordinate-spike); [MAC-B/MAC-C](Research/Plans/ModelsAndHardware.md#mac-b--macos-generator-and-corpus).

#### TASK-6c-1: macOS coordinate spike

- [ ] AppKit Y-flip: `y_flipped = window.contentView.bounds.height - frame.origin.y - frame.height`
- [ ] ±2 pt vs `NSBitmapImageRep` PNG
- [ ] `testMacOSCoordinateFlip` on macOS 15
#### TASK-6c-2: Templates + training

- [ ] ≥2,000 macOS images with Y-flipped coordinates
- [ ] mAP@0.5 ≥ 0.80 on withheld-template test
- [ ] `tooltip` AP ≥ 0.70
- [ ] Export `NativeUIDetector_macOS_v1`

</details>

## Phase 9: ScreenAuditKit integration (remaining)

<details>
<summary>5 open checks — expand details</summary>

Plans: [SA-A](Research/Plans/ConsumersAndRelease.md#sa-a--screenauditkit-contracts-and-native-rules); [SA-B](Research/Plans/ConsumersAndRelease.md#sa-b--dependency-bridge-and-native-cli-mode).

### TASK-9-2: Contract extension [ ]

- [ ] `uiElements` required/forbidden/`minConfidence` on `ScreenAuditScreenContract`
- [ ] Rule IDs: `missingUIElement`, `unexpectedUIElement`, `uiElementBoundsViolation`, `uiElementTruncated`, `uiElementClipped`, `uiElementTargetTooSmall`, `inferredOSMismatch`
- [ ] `NativeUINoOpRecognizer` skips `uiElements` silently
### TASK-9-3: CLI flag [ ]

- [ ] `screenaudit validate --native-ui none|coreml` (default `none`)
- [ ] Missing models package → clear error, exit 1

</details>

## TASK-DOC-01: Documentation and skill consistency [ ]

<details>
<summary>4 open checks — expand details</summary>

Plans: [maintenance packets](Research/Plans/ConsumersAndRelease.md).

- [ ] Correct historical inference advice without changing shipped YOLO letterboxing
- [ ] Clarify prediction diagnostics are not training annotations
- [ ] Correct stale phase/section references and validate changed links/skills
- [ ] Complete protected skill changes only through the permitted filesystem workflow

</details>

## Track 3: Release leftovers [~]

<details>
<summary>2 open checks — expand details</summary>

Plans: [HIST-A](Research/Plans/ConsumersAndRelease.md#hist-a--history-remediation-decision-package); [HIST-B](Research/Plans/RemainingDelivery.md#hist-b--maintainer-history-disposition); [REL-A/REL-B](Research/Plans/ConsumersAndRelease.md#rel-a--qualified-model-release-evidence).

### TASK-DIST-01: History rewrite (maintainer call) [!]

- [!] HIST-B: maintainer disposition/recovery/migration; rewrite and force-push deferred without exact authority
### TASK-DIST-02: Next release tag [!]

- [ ] Tag (e.g. `2.1.0`) after TASK-6a-10 ships DS-G8-passing 41-class weights; CHANGELOG cites that model and the `pytorch_reference_metrics.json` hash

</details>

</details>


</details>

<!-- FLOW478-REPAIRS:BEGIN -->
## Generated repair handoff

These tasks do not grant execution authority.
Regenerate this section after reviewing the affected campaigns.

The reviewed campaigns have no implementation blockers.

<!-- FLOW478-REPAIRS:END -->

- [ ] **VERIFY516 — Diagnose the stalled Swift verification. Priority P2.** Owner: Maximum-mini-NUIAK. The offline suite stalls in Vision semaphore waits. Inspect reports/work/STREAM516/swift-test-stall.txt. Reproduce with bounded serial tests. Preserve model and queue behavior. Acceptance: the relevant suite completes or a specific existing failure is isolated.

- [ ] **FOCUS565 — Diagnose focus discrimination. Priority P1.** Owner: Maximum-mini-NUIAK. Four diagnostics complete. Grayscale fails preservation. The feature probe fails before inference; FOCUS566 supplies explicit successors. Preserve every prior success. Review provisional results before training changes. See reports/work/FOCUS565/plan.md.

- [ ] **FOCUS566 — Native focus feature comparison. Priority P1.** Owner: Maximum-mini-NUIAK. Admit 2 fixed training-only probes for stretch and aspect-fit. Reject grayscale: 71 lost legacy positives and 1 new wrong selection. Preserve the failed FOCUS565 probe. Review provisional feature evidence before a training correction. See reports/work/FOCUS566/review-and-plan.md.

- [x] **DIAG569 — P1.** Owner: Maximum-mini-NUIAK. Diagnose the 4 tvOS losses and 15 Run013 losses. Use cached iOS predictions. Retain tvOS raw proposals for review. Do not train until the cause supports a specific correction.
