# NativeUIAuditKit — Tasks

Open work only. Finished phases: [`CompletedTasks.md`](CompletedTasks.md).  
Current snapshot: [`Research/CurrentState.md`](Research/CurrentState.md).  
Streams: [`Research/PhaseMap.md`](Research/PhaseMap.md).
Full-backlog contracts: [`Research/ImplementationPlans.md`](Research/ImplementationPlans.md). Accepted decisions: [`Research/DeliveryDecisions.md`](Research/DeliveryDecisions.md).

Platform navigation: [iOS](#ios-platform-tasks) · [tvOS](#tvos-platform-tasks) ·
[shared integration and later models](#shared-integration-and-later-models) ·
[macOS](#macos-platform-tasks) · [consumer integration](#phase-9-screenauditkit-integration-remaining).
The packet queue below is the only execution-state/ownership list. Platform sections
group the same tasks; they do not create additional packet IDs or assignments.

## Worker packet queue

**Top dispatch priority (2026-09-21): failure-driven usable perception for TTR.**
Next new offline tranche: **PER-01 + PER-02**, the chevron-and-dialog benchmark,
followed by PER-04 visual-focus readiness. This refines, not abandons, the usable
FocusRing goal. Preserve active workers; no capture/training or peer request is
authorized by this planning update. [Detailed contracts](Research/Plans/TTRPerception.md).
Priority F1 supersedes legacy numeric ordering for new assignments; preserve existing
workers and authorized work. **Office visual-focus remains the model-delivery lane:**
P4-L smoke/intake → FR-B physical pilot + shipped baseline + qualified corpus → FR-C
candidate/export → separately authorized TTR comparison. Only the single smoke request
is currently authorized. [Office contracts](Research/Plans/OfficeFocusRing.md).
Simulator execution is paused by the user until further notice, independently of runtime
repair; preserve offline review/evidence and [simulator plans](Research/Plans/FocusRingSimulator.md).

Dispatch contracts: [`Research/ImplementationPlans.md`](Research/ImplementationPlans.md).
Workflow: [`Research/WorkerWorkflow.md`](Research/WorkerWorkflow.md). Owner is unassigned until dispatch.
These packets refine the parent tasks below; accepting preparation does not close their live-data gates.

Roadmap: [concurrent lanes](Research/IterationRoadmap.md). Priority is dispatch preference, not a requirement to finish an earlier row. Accept software slices separately from real-data qualification. Review rows have delivered worker evidence; do not redispatch them as unassigned work. Owner identities not recorded in this queue remain unspecified, not evidence that no worker exists.

| Priority | Packet | Parent | State | Prerequisite / next action |
|---|---|---|---|---|
| P0 | PER-01 | TTR-PERCEPTION | review (Codex worker; offline) | Evidence inventory, labeling/manifest and journey-group validation completed; missing real captures reported, never fabricated. Evidence: `reports/work/PER-01/handoff.md` |
| P0 | PER-02 | TTR-PERCEPTION | review (Codex worker; offline tranche) | Integrated chevron/dialog scorer, baseline adapter contract, and honest no-training gap report completed; real inference separately assigned. Evidence: `reports/work/PER-02/handoff.md` |
| P0 | PER-03 | TTR-PERCEPTION | blocked (unassigned) | Accepted benchmark/gap decision, numeric gates, eligible data and separate capture/training authority; reuse FR-B/FR-C for any FocusRing candidate |
| P1 | PER-04 | FOCUS-DET-05 | review (Codex worker; offline) | Physical-source crop/pair/evaluation readiness validator completed; no capture or duplicate model pipeline. Evidence: `reports/work/PER-04/handoff.md` |
| P1 | PER-05 | TTR-PERCEPTION | draft (unassigned) | Sequence contract review; existing-primitives transition benchmark before any temporal model |
| P2 | PER-06 | TTR-PERCEPTION | draft (unassigned) | Journey/identity label contract; screen/row matching evaluation after higher-priority benchmark work |
| — | TTR-PER | TTR-PERCEPTION | external proposal (unpublished) | Producer evidence and isolated comparison contract; requires separate publication and assignment in TVTestRig |
| 1 | H1 | INTEGRATION-01 | accepted | NUIAK source-pinned offline contract accepted; bilateral producer acceptance and genuine-bundle qualification remain open |
| 2 | P1-A | 6a-11 | accepted | Offline export software/schema accepted; P1-B still requires eligible pixels and assigned inference |
| 3 | P0-A | DATA-01 | blocked | Recovery handoff is incomplete: known roots have no originals and remaining label identity work is stalled; requires backup location or separately authorized P0-C |
| 4 | P4-A | INTEGRATION-01 / 6a-10 | accepted | Offline schema/version, fail-closed validation, normalization, and adversarial contract suite accepted; P4-L remains genuine-bundle blocked |
| 5 | P5-A | 6a-10 | accepted | Side-effect-free configuration preflight and negative-data tests accepted; P5-B still requires eligible corpora |
| 6 | P3-A | 6a-11 | accepted | Deterministic regression selector and toy-corpus leakage checks accepted; P3-B still requires eligible corpus/predictions |
| 8 | P4-B | 6a-10 | accepted | Split-safe assembly software and adversarial tests accepted; actual assembly remains data-gated |
| 9 | P2-A | 6a-11 | accepted | Strict reference-comparison software and compatibility checks accepted; P2-B remains corpus/prediction-gated |
| — | P0-B | DATA-01 | blocked | P0-A recovery evidence and exact authorized staged-copy plan |
| — | P0-C | DATA-01 | in progress | WKWebView/`HardNegative_2` route retired and native validation passed. After maintainer freed substantial disk headroom, fresh isolated native-only replacement capture is authorized for retry; `webContent` remains explicitly uncovered |
| — | P1-B | 6a-11 | blocked | P1-A and eligible original/replacement test pixels |
| — | P2-B | 6a-11 | blocked | P2-A and accepted P1-B artifacts |
| — | P3-B | 6a-11 | blocked | P3-A, eligible corpus, compatible P1/P2 software |
| F1 | P4-L | INTEGRATION-01 | blocked (staging access) | Approved container workaround stalled creating its directory; canceled owned processes, no lease/capture began. Maintainer is remote. Establish scoped storage access or producer-supported accessible export, then refresh Office readiness/authority. See reports/work/OFFICE-FOCUS-SMOKE/staging-attempt.md and output-path-rca.md |
| — | P5-B | 6a-10 | blocked | Eligible full corpora and accepted assembly/config interfaces |
| — | TRAIN-S | 6a-10 | blocked | P5-B and explicit bounded smoke assignment |
| — | TRAIN-F | 6a-10 | blocked | Accepted smoke and full-run assignment |
| — | TRAIN-Q | 6a-10 | blocked | Candidate plus eligible dual holdouts |
| — | FR-A | FOCUS-DET-05 | accepted | Offline quota/pair/split and ADR-0007 alignment validator accepted; FR-B remains capture-gated |
| F1 | FR-B | FOCUS-DET-05 | blocked | P4-L acceptance, physical-source review and separate pilot/scale harvest authority; visual-only corpus needs no semantic alignment matrix |
| F1 | FR-C | FOCUS-DET-05 | blocked | Accepted physical FR-B corpus and explicit training/export assignment; later TTR comparison separately authorized |
| F1 | SIM-DATA-01 | TASK-SIM-DATA-01 | paused (user; runtime blocked) | Simulator execution prohibited until renewed user authority. Read-only inventory found CoreSimulatorService unavailable; no UUID/helper/endpoint may be inferred. Resume after local simulator service and matching TTR helper/Fixture build are available. Evidence: `reports/work/SIM-DATA-01-02/runtime-inventory.md` |
| F1 | SIM-DATA-02 | TASK-SIM-DATA-01 | review | Simulator manifest/eligibility, grouping and paired frame-correct extraction implemented with offline adversarial coverage. Evidence: `reports/work/SIM-DATA-01-02/handoff.md` |
| F1 | SIM-DATA-03 | TASK-SIM-DATA-01 | paused (user) | Simulator execution remains prohibited; preserve prerequisites:  Accepted SIM-DATA-01/02 plus simulator capture authority; 42-recipe genuine pilot |
| F1 | SIM-DATA-04 | TASK-SIM-DATA-01 | paused (user) | Simulator execution remains prohibited; preserve prerequisites:  Accepted FR-SIM-BASE/pilot, frozen shared membership and assigned capture; ≥6,000 visual pairs |
| F2 | SIM-DATA-05 | TASK-SIM-DATA-01 | paused (user) | Simulator execution remains prohibited; preserve prerequisites:  Accepted pilot/interfaces and frozen shared membership; separate full-frame augmentation corpus |
| F1 | FR-SIM-BASE | FOCUS-DET-05 | paused (user) | Simulator execution remains prohibited; preserve prerequisites:  Genuine SIM-DATA-03 pilot and assigned baseline inference; offline tooling independently dispatchable; owner unassigned |
| F1 | FR-SIM-CAND | FOCUS-DET-05 | paused (user) | Simulator execution remains prohibited; preserve prerequisites:  FR-SIM-BASE, qualified SIM-DATA-04 corpus and explicit run/export assignment; owner unassigned |
| F1 | FR-SIM-TTR | FOCUS-DET-05 | paused (user) | Simulator execution remains prohibited; preserve prerequisites:  Candidate, frozen comparisons, producer acknowledgment and simulator authority; fake-backed preparation independent; owner unassigned |
| — | R-A | 6b-R-1 | review | Offline matrix/inventory validator distinguishes unique screenshots and genuine labeled examples |
| — | R-B | 6b-R-1 | blocked | R-A and authorized device/app window |
| — | R-C | 6b-R-1 | blocked | Complete qualified capture manifest; mAP additionally requires genuine boxes |
| — | MAC-A | 6c-1 | blocked | Documented DS-G8 pass |
| — | MAC-B | 6c-2 | blocked | Accepted coordinate spike |
| — | MAC-C | 6c-2 | blocked | Eligible macOS corpus and experiment assignment |
| — | BADGE-A | BADGE-01 | review | Append-only ID-41 badge taxonomy specification preserves current 41-class outputs |
| — | BADGE-B | BADGE-01 | blocked | Accepted 41-class milestone, badge contract and new corpus |
| — | CROP-A | 6a-12 | blocked | Accepted full-frame 6a-10 baseline |
| — | CROP-B | 6a-12 | blocked | Frozen crop evaluation and experiment assignment |
| — | UNI-A | 6b-U | draft | Eligible platform corpora, dedicated baselines and deployment budgets |
| — | UNI-B | 6b-U | blocked | Accepted unified readiness and experiment assignment |
| — | TV-I1 | INTEGRATION-01 | external proposal | TVTestRig owner assigns identity lifecycle work |
| — | TV-I2 | INTEGRATION-01 | external proposal | TVTestRig owner assigns offline artifact publication |
| — | SA-A | 9-2 | external proposal | ScreenAuditKit owner assigns contracts/fake-backed rules |
| — | SA-B | 9-3 | external proposal | Consumer injection interface and dependency assignment |
| — | DOC-A | DOC-01 | review | Permitted documentation corrections are ready; exact protected-skill patch awaits its required authority |
| — | REL-A | DIST-02 | blocked | Qualified selected-model evidence |
| — | REL-B | DIST-02 | maintainer-gated | Accepted release evidence and exact promotion/tag authority |
| — | HIST-A | DIST-01 | review | Read-only remediation assessment is ready; missing Git object requires maintainer recovery decision |

Architect acceptance (2026-09-19): H1 and the offline NUIAK software packets P1-A, P2-A,
P3-A, P4-A, P4-B, P5-A, and FR-A are accepted for their documented software-only scopes.
P0-A is blocked/incomplete, not accepted. See the [architect review evidence](reports/work/ARCHITECT-REVIEW-2026-09-19.md).
TVTestRig reports a non-attested default harvest contract; bilateral producer acceptance,
genuine-bundle validation, capture provenance, data eligibility, and model gates remain
independent and open. No eligibility policy is changed by this acceptance update.

No new owners are assigned by this planning update. A concurrent P0-A handoff arrived during
the documentation pass; its evidence awaits review and the assessment script was not edited
or executed by this architect task. Its presence is not proof of acceptance. Each handoff separately
reports software verified / data eligible / integration qualified / model gate passed. None of
these outcomes is asserted by publishing this queue.

## Status

- `[ ]` Not started
- `[~]` In progress
- `[x]` Done (move the whole task to `CompletedTasks.md` when every AC is `[x]`)
- `[!]` Blocked — see note

Do not put architecture notes, run logs, or IPC war stories in this file. Those go in `Research/` ([index](Research/README.md)).

---

## iOS platform tasks

**Target:** replace the shipped five-class `nativeui-ios-v2.0` only after the
41-class candidate passes all applicable gates. Historical Run 009 mAP50 is 0.586;
DS-G8 requires ≥0.85. Missing pixels prevent a new baseline today.

Detailed dispatch scope: [iOS platform delivery plan](Research/Plans/iOSPlatform.md).
These are substantial execution tranches over existing packets, not new task IDs:

| iOS deliverable | Existing packets / parent | What finishes the tranche | Office dependency |
|---|---|---|---|
| Recoverable, reproducible iOS corpus | P0-A/B/C; DATA-01 | Reviewed recovery decision, then separately authorized complete versioned splits and preservation evidence | None; reconstruction may require separately authorized iOS rendering |
| Integrated offline evaluation and readiness software | P1-A/P2-A/P3-A/P4-B/P5-A; 6a-10/11 | Review existing implementations, resolve assigned gaps, exercise required interfaces end-to-end, and verify all acceptance criteria | None |
| Run 009 iOS baseline and frozen diagnostics | P1-B/P2-B/P3-B; 6a-11 | Complete full-holdout predictions, compatible reference report, frozen regression membership/baseline | None; requires eligible iOS pixels and inference assignment |
| 41-class candidate readiness and execution | P5-B, TRAIN-S/F; 6a-10 | Frozen eligible inputs/configuration, then separately authorized smoke and full candidate | Planned mixed-data experiment needs qualified fixture corpus; Office remains released |
| Qualification and release evidence | TRAIN-Q, REL-A/B; 6a-10/DIST-02 | Independent holdout gates, package evidence, then maintainer-only promotion/tag | No fresh capture if accepted evaluation corpora exist |

**Next dispatch:** review the existing offline software as one coherent tranche,
not another tiny helper implementation; separately review P0-A and resolve its
remaining evidence/recovery decision. Both can proceed while Office is unavailable.
Workers do not self-accept earlier review-ready packets. This plan does not assign
workers, start generation/inference/training, or restore Office permission.

### TASK-DATA-01: Phase 6a dataset recovery and preservation [!]

Evidence: [2026-09-19 inspection](reports/dataset_availability_2026-09-19.md).
Contract: [P0 recovery assessment and staged recovery](Research/DatasetRecoveryPlan.md).
All 2,000 test image links are broken; 10,543 training and 2,696 validation links are also broken.
Cause is unknown. Preserve existing manifests, labels, links, and historical metrics.

- [!] P0-A: bounded recovery review found 0/15,239 expected originals at five documented roots; per-label identity evidence is partially verified (11,415/17,040) but local filesystem stalls prevent completion. See [`P0-A handoff`](reports/work/P0-A/handoff.md); do not dispatch P0-B/P0-C without the listed authority.
- [ ] Architect reviews exact recovery plan or replacement-corpus proposal
- [ ] P0-B (separate assignment): stage and verify recoverable pixels/annotations without overwriting historical artifacts
- [ ] P0-C (fallback): versioned reconstruction with new annotations/baseline if originals cannot be recovered; family-level splitting is complete and the failed `HardNegative_2` WKWebView route is retired ([record](reports/work/P0-C/web-content-blocker.md)). Native validation passed; the prior launcher exit 137 happened under 98% disk usage, and the maintainer has now cleared headroom for one fresh retry. The eventual corpus must report legacy `webContent` coverage as zero.
- [ ] Record independent test-corpus and training-corpus readiness; uncertain/regenerated identity uses a new corpus version
- [ ] Establish content manifest, retention ownership, and recovery verification before expensive evaluation/training

**AC:** Every required corpus member has verified image/annotation evidence, or the unrecoverable original is explicitly documented and a separately reviewed replacement protocol is established. No real-data downstream gate closes on a plan or labels alone.

---

### TASK-6a-10: Full-frame fixture retraining (41-class iOS) [!]

**Blocked on live TVTestRig batch output.** Ingest code is ready. Do not train on empty sidecars or `*_result.json` (model self-predictions). Format and IPC notes: [`Research/FixtureBatchIngest.md`](Research/FixtureBatchIngest.md).

**Additional data blocker (2026-09-19):** Phase 6a train/validation/test images are incomplete; TASK-DATA-01 must establish eligible corpora before assembly, training, or holdout evaluation.

**Requires:** Run 009 diagnosis (holdout mAP@0.5 = 0.586, DS-G8 ≥ 0.850). BP-32.

- [~] Review and integrate P4-B/P5-A software; retain separate configuration-valid and launch-eligible results — evidence [handoff](reports/work/INTEGRATED-IOS-TOOLCHAIN/handoff.md), architect acceptance pending
- [ ] P5-B: freeze eligible manifests and resolved configuration, including the explicit auxiliary role of tvOS examples; retain iOS-only reporting

- [x] `scripts/ingest_fixture_batch.py` + `scripts/test_ingest_fixture_batch.py` (16/16)
- [x] Coordinator IPC resolved in the recorded 2026-09-18 investigation; historical procedures are not current operating instructions
- [!] Live batch output, missing synthetic pixels, and Office/export access are independent blockers. The producer's current source records descriptive source context and does not require optional identity attestation for production/NUIAK fixture batch; re-verify against genuine output before using any data.
- [ ] Authorized Office `aatv fixture batch` — re-verify ingest against the genuine completed output once it exists
- [ ] Blend fixture corpus with Phase 6a synthetic set; retrain from Run 009 `best.pt`, 150 epochs, cosine annealing + warmup
- [ ] Evaluate on TVTestRig `held-out` split **and** synthetic withheld-template holdout
- [ ] Per-class AP50 on toggle and stepperControl ≥ 0.88; badge belongs to the later TASK-BADGE-01 milestone
- [ ] TRAIN-S / TRAIN-F / TRAIN-Q evidence accepted separately; no automatic experiment reruns

**AC:** Fixture mAP@0.5 ≥0.94 and mAP@0.5:0.95 ≥0.78; toggle and stepperControl AP50 ≥0.88 with real support; separately, complete iOS synthetic withheld-template DS-G8 mAP@0.5 ≥0.85. No platform-pooled mean or compact diagnostic suite substitutes for either holdout. Keep the shipped five-class model until release/promotion authority and evidence are complete.

---

### TASK-6a-11: Multi-corpus PyTorch reference eval [~]

**Requires:** a 6a-10 candidate, or continue using Run 009 weights as the baseline.

**Actual baseline inference blocked:** TASK-DATA-01 must restore/establish usable test pixels. Existing aggregate metrics are historical and must not be reported as current corpus availability. Serializer/comparison tests can continue offline.

- [x] `scripts/eval_reference_metrics.py` + `reports/pytorch_reference_metrics.json` (SHA-256 `226755b88642d1a68a0f9c3cad4b685d6d874352d48090b910c6b406ea61e405`)
- [x] Honest `available: false` for the three corpora that do not exist yet
- [~] Review P1-A/P2-A/P3-A against their original contracts and verify exporter/comparator/selector integration, not helper tests alone — evidence [handoff](reports/work/INTEGRATED-IOS-TOOLCHAIN/handoff.md), architect acceptance pending
- [ ] Per-image predicted boxes / scores / class IDs from `eval_phase6a.py` (needs a full inference pass)
- [ ] P1-B/P2-B: publish complete iOS Run 009 baseline artifacts with corpus/checkpoint/settings hashes; reconstructed pixels establish a new baseline, not reproduction of 0.586
- [ ] P3-B: freeze 200–300 diagnostic cases where coverage supports it, with explicit gaps; retain the complete holdout for DS-G8
- [ ] Populate `real_device_fixture_holdouts`, `production_tvos_system_holdout`, `frozen_regression_suite` when those image+box sets exist

---

### TASK-6a-12: Partial-crop robustness fork [ ]

**Requires:** TASK-6a-10 complete. Full-frame config stays the shipped default.

- [ ] Mosaic + random-crop aug (0.6×–1.0× bounding areas) as a **fork**, not the default
- [ ] Frozen partial-crop holdout, never merged into the full-frame holdout
- [ ] Full-frame mAP50 loss ≤1.0 percentage point vs 6a-10; crop mAP50 relative gain ≥15% (zero baseline requires a reviewed gate amendment)
- [ ] Measure and document in `Research/TrainingDataStrategy.md` that resizing a crop to 1920×1080 does not reconstruct missing full-frame context

---

## tvOS platform tasks

FocusRing and real Apple TV capture are tvOS work, not prerequisites for iOS-only
software acceptance or synthetic baseline evaluation. Office is released until
explicit new user authorization except the single Office smoke now requested in P4-L;
old advisory requests do not authorize any broader capture. Simulators remain paused.

### TTR-PERCEPTION: Failure-driven traversal perception

Canonical plan: [TTRPerception.md](Research/Plans/TTRPerception.md), revision 1.
Queue above is the sole status/ownership record. Deliver chevron-to-row association
and dialog/button/focus benchmarks first, physical visual-focus readiness next,
then sequence readiness and screen/row identity. Known traversal failures guide
development; independent journeys remain held out. TTR owns action authorization,
resume logic and teardown health. No model result grants Select permission.

First dispatch completes PER-01 + PER-02 software integration, adversarial tests,
coverage/missing-evidence report and a targeted-training recommendation together.
Real inference/data/model qualification remain separately gated. PER-04 is an
independent offline option; external requests remain unpublished proposals.

### tvOS Simulator datasets

#### TASK-SIM-DATA-01: Independent local simulator dataset lane [ ]

Canonical contracts: [SimulatorDatasets.md](Research/Plans/SimulatorDatasets.md), revision 1.
Deliver datasets only; packet state/ownership remains in the queue above.

- [ ] SIM-DATA-01: exact local runtime/build/UUID/endpoint record and authorized minimal capture with healthy cleanup
- [ ] SIM-DATA-02: integrated simulator manifest, eligibility, split grouping and frame-correct extraction, verified offline
- [ ] SIM-DATA-03: genuine 42-recipe pilot with complete accounting, overlays, intake and postflight evidence
- [ ] SIM-DATA-04: freeze ≥6,000 visual FocusRing pairs with scene/theme/hard-negative quotas and recovery evidence
- [ ] SIM-DATA-05: separate full-frame tvOS augmentation exports with class/style coverage, lineage and frozen splits

SIM-DATA-01 inventory and SIM-DATA-02 software are independent. Both must pass before
the pilot; FR-SIM-BASE then precedes SIM-DATA-04 scale-up. Secondary SIM-DATA-05
uses the same shared membership registry without blocking FocusRing.
Installation, simulator storage and capture require explicit execution authority.
No training, physical-device qualification, Office operation, Sillycon mutation, iOS
replacement corpus or DS-G8 credit. This visual-only lane does not require ADR-0007's
semantic alignment matrix and does not close FR-B/FR-C or real-device holdout work.

### TASK-6b-R-1: Scale real Apple TV hold-out captures [~]

Pipeline and qualification (R-2, R-3) are done. Remaining:

- [ ] ≥500 held-out real Apple TV screenshots across the app matrix (`dataset/tvos_captures/`, gitignored)

---

### FOCUS-DET-05: FocusRing v1.0 data + retrain [ ]

Simulator follow-ons: [FR-SIM-BASE / FR-SIM-CAND / FR-SIM-TTR](Research/Plans/FocusRingSimulator.md).

- [ ] Benchmark shipped model on the development pilot before scale-up; freeze final evaluation protocol
- [ ] Train/export one explicitly authorized simulator candidate and report six quality gates
- [ ] Compare focus decisions and bounded navigation in TTR; no simulator-only production promotion

Physical delivery now follows [OfficeFocusRing.md](Research/Plans/OfficeFocusRing.md).
Visual quality gates remain unchanged; the separate semantic alignment matrix is not a capture prerequisite.

v0.1 is shipped. Spec: [`Research/FocusRingDetectorSpec.md`](Research/FocusRingDetectorSpec.md).

- [ ] ≥6,000 labeled pairs (or Fixture RPC when it exists)
- [ ] Mix: `gridMatrix` ≥ 2,000, `mediaShelf` ≥ 1,500, `settingsList` ≥ 1,000, `actionDialog` / `heroCarousel` / `focusMaze` ≥ 500 each
- [ ] ≥ 20% `light` and ≥ 20% `highContrast` in `gridMatrix` + `mediaShelf`
- [ ] Held-out hard-negative n ≥100 across `light`/`highContrast` × `imageView`/`collectionItem`; every combination nonempty with separate counts/results
- [ ] Separately assigned ADR-0007 semantic alignment dataset/policy matrix remains open; it is not a prerequisite for physical visual-focus capture or training
- [ ] All six quality gates, including **non-vacuous** hard-neg FPR ≤ 0.5%
- [ ] Replace bundled `.mlmodelc` only after those gates pass

Office live harvest only. No Home / Select / Settings crawl (BP-40). IPC: [`Research/FixtureBatchIngest.md`](Research/FixtureBatchIngest.md).

---

## Shared integration and later models

### TASK-INTEGRATION-01: Incremental TVTestRig compatibility [ ]

Contract: [TVTestRigIntegrationContract.md](Research/TVTestRigIntegrationContract.md).
TVTestRig owns producer implementation and its queue; this task owns NUA consumer compatibility.

- [~] H1: source-pinned contract and deterministic offline cases are review-ready in [harvest-compatibility-v1.md](Research/schemas/harvest-compatibility-v1.md); producer bilateral acceptance/live evidence remain pending
- [~] P4-A: consumer validates/normalizes those cases; offline integrity never implies trusted capture; review evidence in `reports/work/P4-A/handoff.md`
- [~] Record supported producer versions and actionable incompatibility reports on each relevant change; the 2026-09-19 layout-v1/sourceDescription reconciliation is review-ready in [`reports/work/INTEGRATION-RECONCILIATION/handoff.md`](reports/work/INTEGRATION-RECONCILIATION/handoff.md)
- [ ] P4-L: validate one genuine completed bundle once export prerequisites are met; any new Office operation requires renewed user authority

**AC:** Software compatibility can be accepted independently of hardware/model quality. Live compatibility requires genuine evidence for a named producer revision. No new weights are required for producer/consumer iteration.

### TASK-BADGE-01: Versioned badge taxonomy and later model [ ]

Separate next model milestone; the current 41-class release does not wait on it.
Contracts: BADGE-A / BADGE-B in [model packets](Research/Plans/ModelsAndHardware.md).

- [ ] Define notification/status dot/count badge semantics and append category ID 41 without changing IDs 0–40
- [ ] Version taxonomy/library/dataset and make decoding use each model's declared category map
- [ ] Preserve legacy 41-class annotations/models and add producer/consumer compatibility fixtures
- [ ] After the 41-class milestone, generate paired badge annotations and train a separately identified 42-class candidate
- [ ] Badge AP50 ≥0.88 on supported holdouts plus applicable full-frame gates; report existing classes separately

---

### Phase 6b-U: Unified iOS + tvOS model [ ]

Keep separate shipped models unless every gate passes.

- [ ] Train a platform-balanced unified candidate
- [ ] No platform loses > 2 pt mAP@0.5 vs its dedicated model on identical holdouts
- [ ] tvOS `tabBar` AP ≥ 0.80 and no toolbar confusion
- [ ] tvOS focus P/R within 2 pt of dedicated model or FocusRing
- [ ] iOS FP does not rise on bottom chrome, status bar, home indicator, Dynamic Island
- [ ] Latency and size stay in budget

---

## macOS platform tasks

### Phase 6c: macOS model [ ]

**Requires:** Phase 6a gate (41-class iOS weights that clear DS-G8).

#### TASK-6c-1: macOS coordinate spike

- [ ] AppKit Y-flip: `y_flipped = window.contentView.bounds.height - frame.origin.y - frame.height`
- [ ] ±2 pt vs `NSBitmapImageRep` PNG
- [ ] `testMacOSCoordinateFlip` on macOS 15

#### TASK-6c-2: Templates + training

- [ ] ≥2,000 macOS images with Y-flipped coordinates
- [ ] mAP@0.5 ≥ 0.80 on withheld-template test
- [ ] `tooltip` AP ≥ 0.70
- [ ] Export `NativeUIDetector_macOS_v1`

---

## Phase 9: ScreenAuditKit integration (remaining)

9-1 (`NativeUIRecognizing`) is done. These live in the ScreenAuditKit repo.

### TASK-9-2: Contract extension [ ]

- [ ] `uiElements` required/forbidden/`minConfidence` on `ScreenAuditScreenContract`
- [ ] Rule IDs: `missingUIElement`, `unexpectedUIElement`, `uiElementBoundsViolation`, `uiElementTruncated`, `uiElementClipped`, `uiElementTargetTooSmall`, `inferredOSMismatch`
- [ ] `NativeUINoOpRecognizer` skips `uiElements` silently

### TASK-9-3: CLI flag [ ]

- [ ] `screenaudit validate --native-ui none|coreml` (default `none`)
- [ ] Missing models package → clear error, exit 1

---

## TASK-DOC-01: Documentation and skill consistency [ ]

Contract: DOC-A in [maintenance packets](Research/Plans/ConsumersAndRelease.md).

- [ ] Correct historical inference advice without changing shipped YOLO letterboxing
- [ ] Clarify prediction diagnostics are not training annotations
- [ ] Reconcile FocusRing artifact metadata with qualification milestone labels
- [ ] Correct stale phase/section references and validate changed links/skills
- [ ] Complete protected skill changes only through the permitted filesystem workflow

---

## Track 3: Release leftovers [~]

### TASK-DIST-01: History rewrite (maintainer call) [!]

Working-tree PII is redacted. Real values remain in already-pushed git history. Do not rewrite history without an explicit go-ahead.

- [x] `PROVENANCE.md` written and linked
- [x] Training data audited clean
- [x] Working-tree PII redacted (2026-09-18)
- [!] History rewrite / force-push — deferred on purpose

### TASK-DIST-02: Next release tag [!]

API review is done (`NativeUIDetectionRequest` stays the public name; `FocusRingClassifier` stays internal).

- [x] API decisions in `Research/NativeUIElementDetection.md` §4
- [x] `scripts/verify_models_package_standalone.sh`
- [ ] Tag (e.g. `2.1.0`) after TASK-6a-10 ships DS-G8-passing 41-class weights; CHANGELOG cites that model and the `pytorch_reference_metrics.json` hash
