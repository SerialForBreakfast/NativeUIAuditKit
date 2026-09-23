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

**APPEAR-C — delivered appearance intake review, NUIAK architect:** [latest handoff](reports/work/APPEAR-C/visual-intake/handoff.md).
Three catalog themes/12 pairs/54 verified files admitted development-only;8 distinct
pairs because high_contrast equals dark. Existing destructiveButton intake fixed;
Appearance-v1 consumer support now passes3/3 producer vectors and43 Python checks;
offline Swift build plus14 XCTest/93 Swift Testing pass in approved host context.
All12 retained catalog pairs still validate. Delivered10 artwork/bright/placeholder/dock
pairs now pass independent byte/label/crop intake:48 files,20 unique production crops,
zero exact overlap against458 scoped prior samples. Seed7 siblings remain development;
no independent evaluation or training approval. APPEAR-B1 adapter now delivered for review.
The [reservation-binding follow-up](reports/work/APPEAR-B1/reservation-binding/handoff.md)
requires exact source/membership-bound v2 evaluation reservations. Producer family
contract/artifact handoff is still unavailable locally; existing request remains open.
Distinct high-contrast/Photos-like and independent evaluation families remain open;
all catalog variants reserved together, no model scores/training. [Contract](Research/Plans/CatalogAppearanceQualification.md).

| Priority | Packet | Scope | State/owner | Evidence and resume condition |
|---|---|---|---|---|
| F1 | TTR-CATALOG-01 | New catalog/Top Shelf compatibility | partial review — NUIAK architect; dialog and local catalog paths qualified | [Smoke](reports/work/TTR-CATALOG-01/smoke-0514/handoff.md):2/2 pairs admitted development-only. [APPEAR-C](reports/work/APPEAR-C/handoff.md) now qualifies local corrected catalog; not receipt of Sillycon's separate retained artifact. Supported chunk export works around signed CLI staging denial. Top Shelf visible rendering remains untested; no training qualification. |

**Backlog reconciliation (2026-09-22):** every packet maps to the
[implementation catalog](Research/ImplementationPlans.md). Missing residual contracts
are now in [RemainingDelivery.md](Research/Plans/RemainingDelivery.md). Existing
owners/acceptances are preserved; new rows are unassigned, not execution authority.
Direct review, retention preparation, coverage decisions and bounded reviewed labeling
can proceed without the Fixture repair. Do not duplicate accepted software or collect
another pilot/scale corpus merely to close alternate acquisition-lane IDs.

**Parallel tvOS acquisition (2026-09-22, ADR-0009 approved):**
[ADR-0009](Research/ADR-0009-Direct-tvOS-Simulator-Generation.md) establishes direct
Fixture/OS generation without waiting for TTR capture/export. The approved execution
plan is [TVGEN-01–04](Research/Plans/RemainingDelivery.md#tvgen-01--reuse-and-runtime-design-review):
direct design/admission review, a native two-control proof, a 42-recipe shipped-model
baseline, then a separately authorized scale/training handoff. Keep TTR work and active
iOS reconstruction intact. Either qualified simulator lane may provide FocusRing
development data; TTR integration and physical promotion remain separate.

**Architect acceptance (2026-09-22):** PER-01 supplied-evidence inventory/software and
PER-02/04/05/06 offline scopes accepted after integrated review and corrections.
[Acceptance and remaining capture gaps](reports/work/PERCEPTION-ACCEPTANCE/handoff.md).
Zero real benchmark cases or training pairs are newly qualified. Preserve P0-C ownership.

**Top dispatch priority (2026-09-21): failure-driven usable perception for TTR.**
Offline FocusRing launch preparation and evidence-audit corrections are accepted for
their original offline scopes. **PER-01/02/04/05/06 offline scopes are accepted**;
the supplied real-image inventory is reviewed, but gold labels and independent real
benchmark membership remain absent. Next: qualified data, not duplicate helpers;
prioritize smoke/intake once the capture fix is ready and execution is authorized.
[Completion and review](reports/work/PERCEPTION-INTAKE/handoff.md). This preserves the usable
FocusRing goal. Preserve active workers; no capture/training or peer request is
authorized by this planning update. [Detailed contracts](Research/Plans/TTRPerception.md).
Priority F1 supersedes legacy numeric ordering for new assignments; preserve existing
workers and authorized work. **ADR-0008 supersedes the earlier Office-first sequence:**
simulator smoke/intake → development pilot/baseline → qualified corpus → separately
authorized candidate/comparison. Office is later physical-transfer validation.
The prior single-smoke authorization does not authorize another run, broad capture
or training. Preserve [Office contracts](Research/Plans/OfficeFocusRing.md) and
[simulator evidence/plans](Research/Plans/FocusRingSimulator.md).

**Iteration review:** [change-scoped verification and visual coverage](Research/IterationEfficiency.md)
govern feedback cadence. Producer shared status reports screenshot repair evidence
at 2026-09-22 04:55 UTC; this is not local capture/intake qualification or fresh
runtime availability. Next integration action is candidate reconciliation and an
explicitly authorized complete smoke/intake, not another generic readiness-only loop.

Dispatch contracts: [`Research/ImplementationPlans.md`](Research/ImplementationPlans.md).
Workflow: [`Research/WorkerWorkflow.md`](Research/WorkerWorkflow.md). Owner is unassigned until dispatch.
These packets refine the parent tasks below; accepting preparation does not close their live-data gates.

Roadmap: [concurrent lanes](Research/IterationRoadmap.md). Priority is dispatch preference, not a requirement to finish an earlier row. Accept software slices separately from real-data qualification. Review rows have delivered worker evidence; do not redispatch them as unassigned work. Owner identities not recorded in this queue remain unspecified, not evidence that no worker exists.

| Priority | Packet | Parent | State | Prerequisite / next action |
|---|---|---|---|---|
| F1 | FOCUS-VISUAL-02 | FOCUS-DET-05 | review (NUIAK architect) | [Home comparison](reports/work/FOCUS-VISUAL-02/handoff.md): six frames/72 tiles; shipped2/6 correct unique selections, FP16/int8 0/6 at0.85. Box sensitivity and compression threshold failures retained. Nine Python + offline Swift checks pass. Next OS-FOCUS-04 offline mixed-source assembly/preflight, then eligible mixed-appearance acquisition; no capture/training performed. |
| F1 | FOCUS-VISUAL-01 | FOCUS-DET-05 | review (NUIAK architect) | [Photos appearance regression](reports/work/FOCUS-VISUAL-01/handoff.md): shipped1/2 focused buttons, FP16/int8 0/2; box sensitivity and expanded int8 probability tolerance failure.87 Focus tests pass. Next existing Home-tile visual review/comparison, then eligible mixed-style training proposal; no TTR dependency or promotion. |
| F1 | FOCUS-EXP-01 | FOCUS-DET-05 | review (NUIAK architect): four arms completed | [Handoff](reports/work/FOCUS-EXP-01/handoff.md): 46 reviewed pairs, 37 train/9 validation; warm+stretch reaches18/18 validation decisions versus shipped7/18 at0.85. Scratch+stretch also18/18; no demonstrated aspect-fit win. Same-app development only, runtime parity differs, no promotion. Next: independent native Home/style challenge set before further training. |
| F1 | FOCUS-PARITY-01 | FOCUS-DET-05 | review: corrected-producer replay passed (NUIAK architect) | [Plan](Research/Plans/FocusIntegrationReplay.md); [corrected replay](reports/work/FOCUS-PARITY-01/corrected-20260923/handoff.md): 10/10 exact crops and same-CPU scores, source512ea619. Backend differences reported separately; no model-driven navigation or quality qualification. Next obtain source-backed independent appearance-family contract/evidence under APPEAR-C. |
| F1 | TV-FIX | INTEGRATION-01 | external request acknowledged; repair pending | TTR owns native non-view focus binding; request nuiak-20260922T061302Z-fixture-nonview-focus acknowledged06:36Z. Fixture HTTP restored at16:29Z; installed bytes unchanged, fresh412-sample telemetry still non_view/unmapped_item. [Current diagnostic](reports/work/TTR-CHECK-20260922-1622/fixture-followup.md). No producer edits here. |
| P1 | DATA-RET | DATA-01 / FOCUS-DET-05 | ready planning (unassigned); copy gated | Inventory/restore verifier; maintainer-selected independent backup destination and authority before copying. Reuse corpus retention evidence. |
| P1 | IOS-COV | DATA-01 / 6a-10 | ready decision preparation (unassigned) | Resolve uncovered webContent/support gates from P0-C audit; preserve target, map and active owner. |
| P1 | PER-DATA | TTR-PERCEPTION | bounded review delivered (NUIAK architect); full benchmark coverage blocked | [44 dispositions/39 development reviews](reports/work/PER-DATA/handoff.md), including4 button boxes/2 appearance-focus labels. Five exclusions, zero admitted positive chevron/dialog cases; source/journey/privacy gaps remain.25 perception tests pass. No training or independent-evaluation eligibility. |
| F1 | FOCUS-COMPRESS-01 | FOCUS-DET-05 | review (NUIAK architect) | [One int8 candidate](reports/work/FOCUS-COMPRESS-01/handoff.md):2,612,925 bytes,48.14% smaller, zero threshold changes on12 crops; max FP16 drift0.000000715255.78 Focus tests and offline Swift checks pass. Broader challenge required; no retraining/promotion. [Contract](Research/Plans/NativeOSFocus.md#focus-compress-01--assigned-2026-09-22). |
| P1 | PER-LIVE | TTR-PERCEPTION | blocked (unassigned) | Eligible PER-DATA and inference authority; reuse PER-02, freeze experiment gates before PER-03. |
| P2 | TEMP-LIVE | TTR-PERCEPTION | proposed offline spike (unassigned); live qualification blocked | [Temporal visual-verification spike](Research/Plans/TemporalVisualVerificationSpike.md) compares native-only, single-frame NUIAK and temporal-diff guardrails on controlled Fixture/replay interruption cases. No real account/call/mirroring events or model training. A separate real ordered-journey/inference assignment is still required for qualification. |
| P2 | ID-LIVE | TTR-PERCEPTION | blocked (unassigned) | Reviewed reference/query journeys and inference authority; reuse PER-06. |
| P2 | R-LABEL | 6b-R-1 / 6a-11 | blocked (unassigned) | Qualified physical captures and annotation scope; separate from500-screenshot coverage. |
| P2 | DATA-VIS | DATA-01 / FOCUS-DET-05 | ready inventory (unassigned) | Controllable-state matrix; renderer implementation separately scoped, preserve active captures. |
| later | DATA-SIM | DATA-01 / FOCUS-DET-05 | deferred research (unassigned) | Optional similarity feasibility; exact pixels/lineage remain policy, no automatic filtering. |
| later | ALIGN-A | ADR-0007 | deferred (unassigned) | Semantic contract/policy with real producer capability; not a visual-focus prerequisite. |
| later | ALIGN-B | ADR-0007 | blocked (unassigned) | ALIGN-A, actual cursor/navigation observations and dedicated operation authority. |
| — | HIST-B | DIST-01 | maintainer-gated | Exact defer/remediation disposition, recoverable objects and migration procedure; no agent git writes. |
| F1 | OS-FOCUS-01 | FOCUS-DET-05 | review: approved live probe passed (NUIAK architect) | [Recording/replay](reports/work/OS-FOCUS-01/live-20260922-0712/handoff.md): six inputs, seven verified states/four unique frames; native focus visually aligns. Independent of TTR/Fixture. In-test postflight passed; post-teardown process present, responsiveness not established. |
| F1 | OS-FOCUS-02 | FOCUS-DET-05 | review: root-sweep development tranche (NUIAK architect); broader coverage open | [Handoff](reports/work/OS-FOCUS-02/handoff.md): 25 inputs, 26 observations, 22 unique frames, 12 reviewed native pairs; production crop/intake CLI and shipped baseline. At 0.85: TP1/FN11/FP3/TN9. No new weights or training approval. |
| F1 | OS-FOCUS-03 | FOCUS-DET-05 | partial review / Home blocked (NUIAK architect) | [Handoff](reports/work/OS-FOCUS-03/handoff.md): Home runner/intake integrated; three zero-direction trials lack stable HeadBoard focus. No admitted Home data or exhaustive coverage. Independent fallback delivered Apps3 train + Remotes6 challenge pairs, frozen before scoring. Next: observation-only Home identity investigation, then separately authorized segment; no TTR dependency. |
| F1 | OS-FOCUS-04 | FOCUS-DET-05 | FDR-008 appearance diagnostics review (NUIAK architect) | [Handoff](reports/work/FOCUS-VISUAL-03/handoff.md):0/8 correct unique Home/Photos decisions; Home negatives FP0→5. All532 variants/checkpoint comparisons complete;9 Python+offline Swift checks pass. No export/promotion. Next APPEAR-A, not another same-data run. |
| F1 | APPEAR-A | OS-FOCUS-04 | review — live pilot complete (NUIAK architect) | [APPEAR-A2](reports/work/APPEAR-A2/handoff.md):24 recipes/100 frames/76 pairs admitted development-only; shipped11 vs FDR-00873 focused hits/76, FP9 vs0. Six training-overlap crops; not independent holdout. Home/artwork request remains open. |
| F1 | APPEAR-A1 | APPEAR-A | review — current worker | [Integrated handoff](reports/work/APPEAR-A1/handoff.md): closed24-recipe/76-pair catalog, offline source readiness, production crop intake;37 Python/93 Swift tests pass. No capture/training; next authorized exact-target pilot. |
| F1 | APPEAR-B | OS-FOCUS-04 | partial review — offline proposal delivered; independent evaluation open (NUIAK architect) | [Handoff](reports/work/APPEAR-B/handoff.md):202 candidate train/9 retention-validation/6 known-challenge pairs; all162 Fixture pairs connected, no cross-partition conflict.50/50 source-mass proposal frozen. No independent appearance holdout or training approval. |
| F1 | APPEAR-B1 | APPEAR-B | review — NUIAK architect, integrated offline adapter | [Handoff](reports/work/APPEAR-B1/handoff.md):212 candidate training pairs +9 native retention-validation,50/50 native–Fixture sampling, preserved protected evidence;91 Python tests and full offline Swift checks pass. Real trainer preflight blocks on independent evaluation, selection reference and approval. Next qualify reserved evaluation inputs; no capture/training authorized here. [Contract](Research/Plans/FocusAppearanceAcquisition.md#appear-b1--development-proposal-adapter). |
| F1 | FOCUS-EXPORT-01 | FOCUS-DET-05 | review / parity and byte-gate enforcement delivered (NUIAK architect) | [Follow-up](reports/work/FOCUS-EXPORT-01/size-and-coverage.md): export-01 parity12/12, max error0.00000357628;5,038,123 bytes exceeds5MB. Corrected exporter enforces5,000,000 bytes; fresh export correctly fails.70 Python/93 Swift tests pass. Compression now delivered separately in FOCUS-COMPRESS-01; broader challenge remains required. No promotion or retraining. |
| F1 | TVGEN-01 | FOCUS-DET-05 | review (NUIAK architect; design/runtime inventory delivered) | [Assigned plan](Research/Plans/ParallelTVOSAcquisition.md), matching installed Fixture launched and exact endpoint verified; [handoff](reports/work/TVGEN/handoff.md). No producer edits. |
| F1 | TVGEN-02 | FOCUS-DET-05 | direct dialog qualified / broader scope open (NUIAK architect) | [Genuine smoke](reports/work/TTR-SMOKE-20260922-2119/continuation.md): two development pairs, v1.4 runtime crops, visual review and shipped inference pass execution; native labels/health verified. No model-quality pass. Source planning still matches four pinned hashes. |
| F1 | TVGEN-03 | FOCUS-DET-05 | 36/42 recipes retained / kitchen-sink native observations blocked (NUIAK architect) | [Setup and capture handoff](reports/work/TVGEN-SETUP-20260923/handoff.md): authorized clean-copy installation passed existing signature; repaired media boundary passed. 138 retained pairs; six kitchen-sink recipes/108 pairs remain. Source6093663 routes kitchen-sink to Components without procedural native probe; capture stopped on no_sample. Focus Maze bottom-row clipping also reported for review. Preserve all receipts; resume only after reviewed repair. Full pilot admission/baseline and training remain blocked; TTR sidecar-v2 qualification is separate. Prior integrated32 Python +14 XCTest/93 Swift tests unchanged. |
| F1 | TVGEN-04 | FOCUS-DET-05 | planned (unassigned) | Accepted direct pilot/baseline, frozen split plan and scale authority; existing FocusRing quotas, cross-lane leakage audit and training handoff |
| F1 | EVIDENCE-AUDIT | PER-01 / PER-02 / PER-04 | accepted (original offline scope) | Audit/gate corrections reviewed and 14 tests rerun; [acceptance](reports/work/PERCEPTION-INTAKE/handoff.md). Legacy cross-split data remains unqualified; broader supplied-evidence review is now recorded under PER-01. |
| F1 | FOCUS-LAUNCH | FOCUS-DET-05 | accepted (original offline scope) | Runtime crop, CoreML adapter and capture-plan compiler reviewed/tested; [acceptance](reports/work/PERCEPTION-INTAKE/handoff.md). No capture/training or model-quality pass. |
| F1 | FOCUS-CONSUMER | SIM-DATA-02 / FOCUS-DET-05 | accepted (offline scope) | Validator/extraction/preflight foundations accepted; v1.2 remains inspectable only, new runtime-crop parity delivered in FOCUS-LAUNCH. [Review](reports/work/FOCUS-LAUNCH/review.md). No genuine data qualification. |
| P0 | PER-01 | TTR-PERCEPTION | accepted (inventory/software only) | 44 images visually triaged; 3,000 crops re-audited; explicit quarantine and coverage gaps. No gold labels or real corpus requalification. [Acceptance](reports/work/PERCEPTION-ACCEPTANCE/handoff.md). |
| P0 | PER-02 | TTR-PERCEPTION | accepted (offline scope) | Integrated baseline/scorer reviewed; missing-payload, association-abstention and dimension validation corrected; 19 tests pass. Real evidence/model gates remain open. [Acceptance](reports/work/PERCEPTION-ACCEPTANCE/handoff.md). |
| P0 | PER-03 | TTR-PERCEPTION | blocked (unassigned) | Accepted benchmark/gap decision, numeric gates, eligible data and separate capture/training authority; reuse FR-B/FR-C for any FocusRing candidate |
| P1 | PER-04 | FOCUS-DET-05 | accepted (offline scope) | Physical byte/frame-specific intake → runtime crops → baseline/proposal CLI verified; 56 focus tests pass. Genuine intake and legacy corpus remain unqualified. [Acceptance](reports/work/PERCEPTION-ACCEPTANCE/handoff.md). |
| P1 | PER-05 | TTR-PERCEPTION | accepted (offline scope) | Production primitive boundary, causal policy and 16 tests verified; out-of-frame helper replies rejected; nine synthetic sequences replayed. No live qualification. [Acceptance](reports/work/PERCEPTION-ACCEPTANCE/handoff.md). |
| P2 | PER-06 | TTR-PERCEPTION | accepted (offline scope) | Production anchor adapter, identity abstention/invalidation and 17 tests verified; 15 synthetic cases replayed. Real held-out support/TTR integration unqualified. [Acceptance](reports/work/PERCEPTION-ACCEPTANCE/handoff.md). |
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
| — | P0-C | DATA-01 | in progress (NUIAK architect) | Corrected schema/geometry/native chrome and MenuButton diversity; failed attempts preserved. Eight native tests, 346 independent preflight pairs, 14 Python tests and 92 Swift tests pass. [r5 continuation](reports/work/P0-C/reconstruction-configuration-r5.md) preserves 7,500 verified completed captures and collects the remaining 9,440 toward the unchanged 16,940 target. Final corpus eligibility remains open; no training; `webContent` uncovered. |
| — | P1-B | 6a-11 | blocked | P1-A and eligible original/replacement test pixels |
| — | P2-B | 6a-11 | blocked | P2-A and accepted P1-B artifacts |
| — | P3-B | 6a-11 | blocked | P3-A, eligible corpus, compatible P1/P2 software |
| F1 | P4-L | INTEGRATION-01 | deferred (ADR-0008 simulator-first) | Physical bundle intake is later transfer validation. First repair and qualify the simulator fixture/export/intake loop; no Office capture is implied. |
| — | P5-B | 6a-10 | blocked | Eligible full corpora and accepted assembly/config interfaces |
| — | TRAIN-S | 6a-10 | blocked | P5-B and explicit bounded smoke assignment |
| — | TRAIN-F | 6a-10 | blocked | Accepted smoke and full-run assignment |
| — | TRAIN-Q | 6a-10 | blocked | Candidate plus eligible dual holdouts |
| — | FR-A | FOCUS-DET-05 | accepted | Offline quota/pair/split and ADR-0007 alignment validator accepted; FR-B remains capture-gated |
| F1 | FR-B | FOCUS-DET-05 | deferred (ADR-0008 simulator-first) | Physical corpus is later transfer validation after the qualified simulator pilot, baseline, candidate, and separate physical authority. |
| F1 | FR-C | FOCUS-DET-05 | deferred (ADR-0008 simulator-first) | Physical candidate/comparison work follows simulator candidate evidence and a separately authorized transfer-validation lane. |
| F1 | SIM-DATA-01 | TASK-SIM-DATA-01 | capture/IPC transfer passed; export CLI defect open (NUIAK architect) | [Continuation](reports/work/TTR-SMOKE-20260922-2119/continuation.md): all12 retained files transferred/hash-verified by documented read-job, four PNGs decoded. No recapture for export. Native CLI export still fails; consumer admission tracked separately. |
| F1 | SIM-DATA-02 | TASK-SIM-DATA-01 | review: v2 consumer software verified / genuine intake pending (NUIAK architect) | [Handoff](reports/work/SIM-DATA-02-V2/handoff.md):83 Python tests, Swift build and14 XCTest/93 Swift Testing checks pass. Strict brackets, byte-bound development-only v1.5 production crops and existing baseline CLI integrated. Legacy data preserved; no invented frame IDs. Exact repaired runtime artifact and genuine v2 bundle remain unavailable locally; no training. |
| F1 | SIM-DATA-03 | TASK-SIM-DATA-01 | blocked (genuine v2 intake and pilot coverage) | V2 consumer software verified; actual completed v2 bundle still needed. Independent TVGEN-03 retains36 recipes/138 pairs; six kitchen-sink recipes remain after reported producer repair. Preserve old failures. No duplicate capture, scale or training authorization. [Evidence](reports/work/SIM-DATA-02-V2/handoff.md). |
| F1 | SIM-DATA-04 | TASK-SIM-DATA-01 | blocked | Accepted FR-SIM-BASE/pilot, frozen shared membership and assigned simulator capture; ≥6,000 visual pairs |
| F2 | SIM-DATA-05 | TASK-SIM-DATA-01 | blocked | Accepted pilot/interfaces and frozen shared membership; separate full-frame augmentation corpus |
| F1 | FR-SIM-BASE | FOCUS-DET-05 | blocked | Qualified SIM-DATA-03 or TVGEN-03 pilot and assigned baseline inference; reuse existing offline tooling; owner unassigned |
| F1 | FR-SIM-CAND | FOCUS-DET-05 | blocked | Accepted baseline, qualified SIM-DATA-04 or TVGEN-04 corpus and explicit run/export assignment; owner unassigned |
| F1 | FR-SIM-TTR | FOCUS-DET-05 | blocked | Candidate, frozen comparisons, producer acknowledgment and simulator authority; fake-backed preparation independent; owner unassigned |
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
| — | DOC-A | DOC-01 | review | TVTestRig skill revision 7 is ingested with manifest-verified signing, helper-preflight, and app-owned fixture-job guidance; architect review remains required |
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

**Next dispatch:** preserve active P0-C reconstruction; complete its audit/retention
and IOS-COV decision, then P1-B/P2-B/P3-B when test pixels qualify. Offline software
is already accepted; do not redispatch it wholesale. DATA-RET and IOS-COV preparation
can proceed independently of capture.
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
- [ ] P0-C (fallback): native-only reconstruction underway with corrected source and an authorized bounded deterministic-variant policy ([r5 continuation](reports/work/P0-C/reconstruction-configuration-r5.md)). r1–r3 remain rejected and unused; only independently verified completed r4 batches enter the new version, with explicit lineage and unfinished output preserved separately. Full 16,940-member integrity/coverage/leakage acceptance remains open; legacy `webContent` coverage remains zero. No model inference/training is included.
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

**AC:** Fixture mAP@0.5 ≥0.94 and mAP@0.5:0.95 ≥0.78; toggle and stepperControl AP50 ≥0.88 with real support; separately, complete iOS synthetic withheld-template DS-G8 mAP@0.5 ≥0.85. Every future qualifying baseline/candidate report also records per-class AP and mean AP at IoU 0.50, 0.70 and 0.90 on the identical frozen cases; these geometry measurements complement rather than replace the existing gates. No platform-pooled mean or compact diagnostic suite substitutes for either holdout. Keep the shipped five-class model until release/promotion authority and evidence are complete.

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

PER-01 supplied-evidence review and PER-02/04/05/06 offline scopes are accepted.
The [coverage matrix](reports/work/PERCEPTION-ACCEPTANCE/evidence-and-gaps.md) records
remaining gold-label, genuine-bundle and independent-journey gaps; no existing corpus
was promoted. Do not redispatch these software foundations while TTR is repaired.
Real inference/data/model qualification remain separately gated; the broader
TTR-PER proposal is distinct from already published runtime-blocker requests.

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
- [ ] ALIGN-A/B: separately assigned ADR-0007 semantic alignment dataset/policy remains open; it is not a prerequisite for physical visual-focus capture or training
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
- [!] HIST-B: maintainer disposition/recovery/migration; rewrite and force-push deferred without exact authority

### TASK-DIST-02: Next release tag [!]

API review is done (`NativeUIDetectionRequest` stays the public name; `FocusRingClassifier` stays internal).

- [x] API decisions in `Research/NativeUIElementDetection.md` §4
- [x] `scripts/verify_models_package_standalone.sh`
- [ ] Tag (e.g. `2.1.0`) after TASK-6a-10 ships DS-G8-passing 41-class weights; CHANGELOG cites that model and the `pytorch_reference_metrics.json` hash
