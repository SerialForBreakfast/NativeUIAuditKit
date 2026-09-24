# NativeUIAuditKit — Tasks

**Review-ready tranche (2026-09-23, NUIAK architect):** P1-B, P2-B, and P3-B
iOS r6 Run 009 replacement baseline completed. Evaluated all 2,000 replacement test
members using Run 009 best.pt; 100% accounted for (0 failures). Supported 13 classes
mAP@0.50 = 0.5549, mAP@0.50:0.95 = 0.3982. 28 unsupported classes reported as
unavailable without imputing AP 0.0 (P2-METRICS). Verified prediction-artifact-v1
with reference_comparison, froze 250-member synthetic regression suite with zero
leakage, and published actionable error analysis. [Handoff](reports/work/IOS-R6-BASELINE-20260923/handoff.md).
tvOS APPEAR-EVAL-RESERVE candidate pool (221 pairs + 9 retention) remains frozen;
evaluation source acquisition blocked pending peer delivery over SMB. DS-G8 remains open.

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

**Queue audit2026-09-23:**103 packet IDs map to explicit contracts in the
[revision6 catalog](Research/ImplementationPlans.md). Review means evidence needs
acceptance, not permission to repeat implementation. Historical run IDs and VIS-A/B/C
work breakdowns are not additional assignments. Existing owners are preserved;
rows without a named owner require assignment before implementation. Platform
checklists summarize parent acceptance and do not override packet state.

**Next substantial dispatches (not new execution authority):**

1. **FocusRing first — APPEAR-EVAL-RESERVE + TTR-DIALOG-01 intake:** reconcile
   preserved source reservations and delivered artifacts; qualify genuinely untouched
   appearance groups and actual Photos buttons, freeze evaluation, and finish one
   candidate proposal. Unknown/undelivered groups remain gaps. New transfer, capture,
   inference and training each retain their assigned scope; no same-data retraining.
2. **Independent iOS — IOS-COV + P1-B/P2-B/P3-B:** review r6 data-use/coverage,
   prepare checkpoint/export preflight and deterministic diagnostic membership;
   after separate inference approval, deliver the full replacement baseline and
   compatible reference/suite together. No TTR dependency.
3. **Offline compatibility — TTR-PROVIDER-01 + review FOCUS-RECEIPT-01:** validate
   migration examples, old/new receipt semantics and exact peer package requirements;
   live adoption remains a TTR-owned assignment. Do not infer model reliability.
4. **Local coverage/retention — DATA-VIS/STATE/SCHEDULE/PROBE-INTAKE + DATA-RET:**
   review six-case evidence, freeze missing-axis/addon proposal, reconcile sealed
   inventory and backup requirements. New rendering/copy needs separate authority.

All review rows use the [completion contract](Research/Plans/QueueCompletion.md#review-ready-work).
Each closure records software, data, integration and model outcomes independently.
This local planning audit requires no SMB update and establishes no fresh runtime health.

**REPO-CLEANUP-20260923 — review (NUIAK architect):** report-specific ignores,
generated test catalog instead of report dependency,119 retained artifact hashes
verified,11 Python tests and123 Swift tests/build pass. [Handoff and maintainer steps](reports/work/REPO-CLEANUP-20260923/commands.md).
No deletion, staging or de-indexing performed; historical tracked evidence requires
separate review. The94-path list is a historical snapshot, not a staging list for the
current r6 changes. Recompute the intended file set under the [cleanup contract](Research/Plans/QueueCompletion.md#repo-cleanup-20260923).

**P2-METRICS — software review (NUIAK architect):** corrected missing-key zero substitution,
reject invalid/nonfinite values and test actual comparison integration. Targeted
accepted-P2 correction, not a new evaluator or inference assignment.
[Handoff](reports/work/P2-METRICS/handoff.md):14 focused/integration tests and required
offline package checks pass; missing class metrics stay unavailable, never AP0.

**TTR-PROVIDER-01 — source assessment review, NUIAK architect:** peer's pinned public API
cannot identify actual focus backend/partial scoring. [Source-backed response and
implementation contract](Research/Plans/FocusExecutionReceipt.md). No model agreement
may be inferred from shared score fields or packaged-resource presence.

**FOCUS-RECEIPT-01 — software review (NUIAK architect):** additive detailed
result receipt, actual loader/cache identity, per-candidate dispositions and recoverable
resource boundary. [Contract](Research/Plans/FocusExecutionReceipt.md). Public API
extension is present at baseline7588a92; consumer adoption is not implied. [Handoff](reports/work/FOCUS-RECEIPT-01/handoff.md)
and [consumer migration](reports/work/FOCUS-RECEIPT-01/migration.md):9 focused tests,
14 XCTest+109 Swift Testing and offline build pass. Peer adoption/live integration
remain separate; no model, TTR/runtime or training mutation.

**TTR-DIALOG-01 — software review, NUIAK architect:** source-pinned closed dialog_style hash/
schema compatibility through real ingest and crop entrypoints; adversarial regressions,
offline checks and peer status. No capture, runtime repair or training approval.
[Handoff](reports/work/TTR-DIALOG-01/handoff.md):144styles through ingest/normalization,
actual test-only crop CLI,28Python tests and113Swift tests pass. Genuine repaired
producer bundle and independent evaluation groups remain outstanding.

**DATA-PROBE-01 — six-case native slice review-ready; NUIAK architect:**
[opt-in adapter and catalog v2](reports/work/DATA-PROBE-01/handoff.md). Canonical batch
validation, fixed overflow font metadata, explicit Chrome theme path and owned-window
cleanup implemented. Exact-target build/capture now passed for seed19 probe-0/1
in UIKitControls, ChromeCoverage and DynamicTypeOverflow. [Native review](reports/work/IOS-R6-20260923/visual-review.md).
Six cases are development-only; broader visual-axis coverage remains open.

**DATA-PROBE-INTAKE — software review (NUIAK architect):** bounded read-only iOS probe export
consumer, byte/schema/config/geometry checks and truthful coverage through the CLI.
[Contract](Research/Plans/VisualStateCoverage.md#data-probe-intake--offline-export-admission).
[Handoff](reports/work/DATA-PROBE-INTAKE/handoff.md): actual CLI positive/negative
tests, strict byte/schema/config/geometry checks, duplicate reporting and offline
package checks. Six genuine native probes now pass independent intake and visual
review ([evidence](reports/work/IOS-R6-20260923/visual-review.md)); no training approval.

**DATA-SCHEDULE-01 — software review, NUIAK architect:** planning-only generator catalog,
required joint-coverage regression checks and deterministic development groups.
No capture, existing recipe changes, training eligibility or rendered-theme claim.
[Handoff](reports/work/DATA-SCHEDULE-01/handoff.md):144 planned rows,48batch limit;
8Python tests,14XCTest+98SwiftTesting and full build pass. Native adapter and Chrome
light/dark rendering are now verified for the six-case slice; broader intersections remain open.

**DATA-STATE-01 — software and bounded native review; NUIAK architect:** opt-in v1.2 unknown-aware enabled/selected
state through capture types, UIKit collection, writer, schema selection and offline
regressions. Preserve default v1.0 bytes and frozen corpus. Native runtime validation
and independent rendering schedules remain separate. Six probes verify12 native
UIControl enabled/selected observations and null unknown states; disabled/selected
contrasts remain uncovered. No training authority.
[Handoff and verification](reports/work/DATA-STATE-01/handoff.md):6Python tests,
14XCTest+96SwiftTesting pass;10writer outputs pass full local schema validation.

**APPEAR-EVAL-RESERVE — blocked at source reservation; preparation review, NUIAK architect (2026-09-23):**
[Contract](Research/Plans/FocusAppearanceAcquisition.md#appear-eval-reserve--reservation-acquisition-and-candidate-preparation).
Independent evaluation acquisition and candidate preparation assigned together.
Twenty required role/stratum slots are specified; none yet source-bound. Actual
Photos buttons are not covered by photos_like artwork. Coordinator/Fixture responded in the recorded handoff;
source-backed untouched groups, not another runtime rebuild, are the current dependency.
Candidate retention-reference binding revalidated through actual assembly:460 rows,
221 candidate pairs+9 retention pairs, unchanged membership/sampling, zero leakage.
Ten independent-evaluation role/stratum gaps remain; no capture/freeze/training.
[Integrated handoff](reports/work/APPEAR-EVAL-RESERVE-20260923/handoff.md).
Shared request `nuiak-20260923T163800Z-evaluation-source-reservations` published/read back;
peer acknowledgment remains unverified.

Producer17:42:55Z now reports four representative styles captured:8 pairs/48 files;
consumer intake remains separate. No untouched allocation or actual Photos-button
route/labels supplied. [Resume review](reports/work/APPEAR-EVAL-RESERVE-20260923/resume-review.md)
revalidates candidate/reference hashes and requests concrete source rows or an explicit
unsupported response; no generic rebuild, recapture or training requested.

**APPEAR-C — delivered appearance intake review, NUIAK architect:** [latest handoff](reports/work/APPEAR-C/visual-intake/handoff.md).
**New family archive received; independent evaluation blocked:** [admission audit](reports/work/APPEAR-FAMILY-HANDOFF-20260923/evaluation-readiness.md).
Superseding integrated tranche review (NUIAK architect): [full handoff](reports/work/APPEAR-FAMILY-EVAL-20260923/handoff.md).
Consumer repaired from local cda0a32 Git objects; all3 bundles/9 pairs admitted for
development.19-pair/252 neighbor-variant comparisons complete; all models0/9 unique
base-frame decisions. Expanded proposal221 candidate pairs+9 retention; reference
floor prepared.48 Python/107 Swift tests pass. No training/capture/promotion.
Next [grouped evaluation-to-candidate tranche](reports/work/APPEAR-FAMILY-EVAL-20260923/next-tranche.md),
not another helper: qualify untouched groups and preserve the now-bound retention
reference before one separately approved candidate. Current seed7 diagnostics remain development.

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
contract now resolved through local cda0a32 objects; independent-group coverage remains open.
Distinct high-contrast/Photos-like/blank rendering is now reviewed; true Photos-button
coverage and independent evaluation groups remain open;
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
| F1 | FOCUS-VISUAL-02 | FOCUS-DET-05 | review (NUIAK architect) | [Home comparison](reports/work/FOCUS-VISUAL-02/handoff.md): six frames/72 tiles; shipped2/6 correct unique selections, FP16/int8 0/6 at0.85. Box sensitivity and compression threshold failures retained. Nine Python + offline Swift checks pass. OS-FOCUS-04 assembly and experiments are delivered; next APPEAR-EVAL-RESERVE independent coverage; no capture/training performed. |
| F1 | FOCUS-VISUAL-01 | FOCUS-DET-05 | review (NUIAK architect) | [Photos appearance regression](reports/work/FOCUS-VISUAL-01/handoff.md): shipped1/2 focused buttons, FP16/int8 0/2; box sensitivity and expanded int8 probability tolerance failure.87 Focus tests pass. Home comparison is delivered; next APPEAR-EVAL-RESERVE independent coverage; no TTR dependency or promotion. |
| F1 | FOCUS-EXP-01 | FOCUS-DET-05 | review (NUIAK architect): four arms completed | [Handoff](reports/work/FOCUS-EXP-01/handoff.md): 46 reviewed pairs, 37 train/9 validation; warm+stretch reaches18/18 validation decisions versus shipped7/18 at0.85. Scratch+stretch also18/18; no demonstrated aspect-fit win. Same-app development only, runtime parity differs, no promotion. Next: independent native Home/style challenge set before further training. |
| F1 | FOCUS-PARITY-01 | FOCUS-DET-05 | review: corrected-producer replay passed (NUIAK architect) | [Plan](Research/Plans/FocusIntegrationReplay.md); [corrected replay](reports/work/FOCUS-PARITY-01/corrected-20260923/handoff.md): 10/10 exact crops and same-CPU scores, source512ea619. Backend differences reported separately; no model-driven navigation or quality qualification. APPEAR-C family intake is delivered; next TTR-PROVIDER-01 adoption review and APPEAR-EVAL-RESERVE independent membership. |
| F1 | TV-FIX | INTEGRATION-01 | source-scoped repair evidence review; residual coverage open (TTR owner) | The09-22 non_view diagnostic is historical, not a blanket current blocker. Later two-control v2 smoke and APPEAR-C native catalog intake pass for recorded builds. TVGEN-03 kitchen-sink/geometry gaps still need exact-source reconciliation; no fresh runtime check or producer edit in this audit. |
| P1 | DATA-RET | DATA-01 / FOCUS-DET-05 | local scope review (NUIAK architect); external copy gated | [r6 seal](reports/work/IOS-R6-20260923/handoff.md):38,529 content files/9.51GB readback verified; prefix recovery evidence retained. Maintainer is retention owner; independent backup destination still unassigned. Same-volume copies are not independent backup. |
| P1 | IOS-COV | DATA-01 / 6a-10 | review-ready (NUIAK architect) | [Coverage decision and Addon proposal](reports/work/IOS-COV-20260923/ios-coverage-decision-and-addon-proposal.md): r6 baseline established across 2,000 test images (mAP@0.50=0.5549 across 13 supported classes). 28 missing classes documented; webContent milestone exception defined; targeted 2,800-pair native addon proposed across 4 dedicated families with zero leakage. |
| P1 | PER-DATA | TTR-PERCEPTION | bounded review delivered (NUIAK architect); full benchmark coverage blocked | [44 dispositions/39 development reviews](reports/work/PER-DATA/handoff.md), including4 button boxes/2 appearance-focus labels. Five exclusions, zero admitted positive chevron/dialog cases; source/journey/privacy gaps remain.25 perception tests pass. No training or independent-evaluation eligibility. |
| F1 | FOCUS-COMPRESS-01 | FOCUS-DET-05 | review (NUIAK architect) | [One int8 candidate](reports/work/FOCUS-COMPRESS-01/handoff.md):2,612,925 bytes,48.14% smaller, zero threshold changes on12 crops; max FP16 drift0.000000715255.78 Focus tests and offline Swift checks pass. Broader Home/Photos challenges are delivered and expose failures; use APPEAR-EVAL-RESERVE, no promotion. [Contract](Research/Plans/NativeOSFocus.md#focus-compress-01--assigned-2026-09-22). |
| P1 | PER-LIVE | TTR-PERCEPTION | blocked (unassigned) | Eligible PER-DATA and inference authority; reuse PER-02, freeze experiment gates before PER-03. |
| P2 | TEMP-LIVE | TTR-PERCEPTION | proposed offline spike (unassigned); live qualification blocked | [Temporal visual-verification spike](Research/Plans/TemporalVisualVerificationSpike.md) compares native-only, single-frame NUIAK and temporal-diff guardrails on controlled Fixture/replay interruption cases. No real account/call/mirroring events or model training. A separate real ordered-journey/inference assignment is still required for qualification. |
| F1 | TEMP-FOCUS-DEV | TEMP-LIVE / FOCUS-DET-05 | review (NUIAK architect) | [Handoff](reports/work/TEMP-FOCUS-DEV-20260923/handoff.md):36 retained-image replays; diff finds9/9 reference arrivals, shipped+diff6/9 versus single-frame0/9. Constructed switches reveal ambiguity: diff2 correct/2 wrong/14 abstentions of18; combined shipped0 correct/1 wrong/17 abstentions.51 tests pass. No live route/model qualification; actual ordered journeys next. |
| P2 | ID-LIVE | TTR-PERCEPTION | blocked (unassigned) | Reviewed reference/query journeys and inference authority; reuse PER-06. |
| P2 | R-LABEL | 6b-R-1 / 6a-11 | blocked (unassigned) | Qualified physical captures and annotation scope; separate from500-screenshot coverage. |
| P2 | DATA-VIS | DATA-01 / FOCUS-DET-05 | inventory review (NUIAK architect) | [14,340-sidecar joint coverage +12 retained render probes](reports/work/DATA-VIS-20260923/handoff.md); [bounded additions](Research/Plans/VisualStateCoverage.md). No corpus mutation/capture. |
| later | DATA-SIM | DATA-01 / FOCUS-DET-05 | deferred research (unassigned) | Optional similarity feasibility; exact pixels/lineage remain policy, no automatic filtering. |
| later | ALIGN-A | ADR-0007 | deferred (unassigned) | Semantic contract/policy with real producer capability; not a visual-focus prerequisite. |
| later | ALIGN-B | ADR-0007 | blocked (unassigned) | ALIGN-A, actual cursor/navigation observations and dedicated operation authority. |
| — | HIST-B | DIST-01 | maintainer-gated | Exact defer/remediation disposition, recoverable objects and migration procedure; no agent git writes. |
| F1 | OS-FOCUS-01 | FOCUS-DET-05 | review: approved live probe passed (NUIAK architect) | [Recording/replay](reports/work/OS-FOCUS-01/live-20260922-0712/handoff.md): six inputs, seven verified states/four unique frames; native focus visually aligns. Independent of TTR/Fixture. In-test postflight passed; post-teardown process present, responsiveness not established. |
| F1 | OS-FOCUS-02 | FOCUS-DET-05 | review: root-sweep development tranche (NUIAK architect); broader coverage open | [Handoff](reports/work/OS-FOCUS-02/handoff.md): 25 inputs, 26 observations, 22 unique frames, 12 reviewed native pairs; production crop/intake CLI and shipped baseline. At 0.85: TP1/FN11/FP3/TN9. No new weights or training approval. |
| F1 | OS-FOCUS-03 | FOCUS-DET-05 | partial review / Home blocked (NUIAK architect) | [Handoff](reports/work/OS-FOCUS-03/handoff.md): Home runner/intake integrated; three zero-direction trials lack stable HeadBoard focus. No admitted Home data or exhaustive coverage. Independent fallback delivered Apps3 train + Remotes6 challenge pairs, frozen before scoring. Next: observation-only Home identity investigation, then separately authorized segment; no TTR dependency. |
| F1 | OS-FOCUS-04 | FOCUS-DET-05 | FDR-008 appearance diagnostics review (NUIAK architect) | [Handoff](reports/work/FOCUS-VISUAL-03/handoff.md):0/8 correct unique Home/Photos decisions; Home negatives FP0→5. All532 variants/checkpoint comparisons complete;9 Python+offline Swift checks pass. No export/promotion. APPEAR-A pilot is delivered; next APPEAR-EVAL-RESERVE, not another same-data run. |
| F1 | APPEAR-A | OS-FOCUS-04 | review — live pilot complete (NUIAK architect) | [APPEAR-A2](reports/work/APPEAR-A2/handoff.md):24 recipes/100 frames/76 pairs admitted development-only; shipped11 vs FDR-00873 focused hits/76, FP9 vs0. Six training-overlap crops; not independent holdout. Home/artwork request remains open. |
| F1 | APPEAR-A1 | APPEAR-A | review — current worker | [Integrated handoff](reports/work/APPEAR-A1/handoff.md): closed24-recipe/76-pair catalog, offline source readiness, production crop intake;37 Python/93 Swift tests pass. Original software-only scope; subsequent APPEAR-A2 pilot delivered. Next review/reuse, not recapture. |
| F1 | APPEAR-B | OS-FOCUS-04 | partial review — offline proposal delivered; independent evaluation open (NUIAK architect) | [Handoff](reports/work/APPEAR-B/handoff.md):202 candidate train/9 retention-validation/6 known-challenge pairs; all162 Fixture pairs connected, no cross-partition conflict.50/50 source-mass proposal frozen. No independent appearance holdout or training approval. |
| F1 | APPEAR-B1 | APPEAR-B | review — NUIAK architect, integrated offline adapter | [Handoff](reports/work/APPEAR-B1/handoff.md):212 candidate training pairs +9 native retention-validation,50/50 native–Fixture sampling, preserved protected evidence;91 Python tests and full offline Swift checks pass. At original handoff trainer preflight blocked on evaluation, selection reference and approval; reference binding is now delivered, while independent evaluation and approval remain open. Next qualify reserved evaluation inputs; no capture/training authorized here. [Contract](Research/Plans/FocusAppearanceAcquisition.md#appear-b1--development-proposal-adapter). |
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
| 2 | P1-A | 6a-11 | accepted | Offline export software/schema accepted; r6 pixels exist, P1-B needs data-use review/checkpoint preflight and assigned inference |
| 3 | P0-A | DATA-01 | blocked | Recovery handoff is incomplete: known roots have no originals and remaining label identity work is stalled; requires a newly identified original source; completed replacement P0-C is independent |
| 4 | P4-A | INTEGRATION-01 / 6a-10 | accepted | Offline schema/version, fail-closed validation, normalization, and adversarial contract suite accepted; P4-L remains genuine-bundle blocked |
| 5 | P5-A | 6a-10 | accepted | Side-effect-free configuration preflight and negative-data tests accepted; P5-B still requires eligible corpora |
| 6 | P3-A | 6a-11 | accepted | Selector/leakage checks accepted; P3-B can prepare r6 membership now, with corpus review and prediction qualification separate |
| 8 | P4-B | 6a-10 | accepted | Split-safe assembly software and adversarial tests accepted; actual assembly remains data-gated |
| 9 | P2-A | 6a-11 | accepted | Strict reference-comparison software and compatibility checks accepted; P2-B remains corpus/prediction-gated |
| — | P0-B | DATA-01 | blocked | P0-A recovery evidence and exact authorized staged-copy plan |
| — | P0-C | DATA-01 | r6 content seal review-ready (NUIAK architect) | [Handoff](reports/work/IOS-R6-20260923/handoff.md):16,940 pairs,12,540/2,400/2,000; zero decoded duplicates/leakage;14,340 prefix and2,323 rejected trials preserved. Finder metadata explicitly excluded from content seal, not deleted. Visible support39/12/13 classes; no training approval or DS-G8 claim. |
| — | P1-B | 6a-11 | review-ready (NUIAK architect) | [Handoff](reports/work/IOS-R6-BASELINE-20260923/handoff.md): evaluated all 2,000 r6 replacement test images using Run 009 best.pt. 100% accounted for (0 failures). Supported 13 classes mAP@0.50=0.5549, mAP@0.50:0.95=0.3982; 28 unsupported classes unavailable (not AP 0.0). |
| — | P2-B | 6a-11 | review-ready (NUIAK architect) | [Handoff](reports/work/IOS-R6-BASELINE-20260923/handoff.md): prediction-artifact-v1 exported and self-compared with reference_comparison (2,000 samples); pytorch_reference_metrics.json updated with r6 baseline. |
| — | P3-B | 6a-11 | review-ready (NUIAK architect) | [Handoff](reports/work/IOS-R6-BASELINE-20260923/handoff.md): frozen 250-member synthetic regression suite generated via regression_selector with zero train/val leakage. |
| F1 | P4-L | INTEGRATION-01 | deferred (ADR-0008 simulator-first) | Physical bundle intake is later transfer validation. First repair and qualify the simulator fixture/export/intake loop; no Office capture is implied. |
| — | P5-B | 6a-10 | blocked | Eligible full corpora and accepted assembly/config interfaces |
| — | TRAIN-S | 6a-10 | blocked | P5-B and explicit bounded smoke assignment |
| — | TRAIN-F | 6a-10 | blocked | Accepted smoke and full-run assignment |
| — | TRAIN-Q | 6a-10 | blocked | Candidate plus eligible dual holdouts |
| — | FR-A | FOCUS-DET-05 | accepted | Offline quota/pair/split and ADR-0007 alignment validator accepted; FR-B remains capture-gated |
| F1 | FR-B | FOCUS-DET-05 | deferred (ADR-0008 simulator-first) | Physical corpus is later transfer validation after the qualified simulator pilot, baseline, candidate, and separate physical authority. |
| F1 | FR-C | FOCUS-DET-05 | deferred (ADR-0008 simulator-first) | Physical candidate/comparison work follows simulator candidate evidence and a separately authorized transfer-validation lane. |
| F1 | SIM-DATA-01 | TASK-SIM-DATA-01 | bounded runtime/export integration review (NUIAK architect) | [Genuine smoke](reports/work/TTR-CATALOG-01/smoke-0514/handoff.md): completed two-control job,12 verified files, supported chunk export and healthy postflight. Signed CLI export defect remains distinct; do not recapture verified jobs. Fresh operation needs exact-build preflight/authority. |
| F1 | SIM-DATA-02 | TASK-SIM-DATA-01 | software plus bounded genuine v2 intake review (NUIAK architect) | [Software](reports/work/SIM-DATA-02-V2/handoff.md) and later [genuine two-pair intake](reports/work/TTR-CATALOG-01/smoke-0514/handoff.md) establish named-scope compatibility. APPEAR-C extends catalog/appearance evidence. No blanket current-build, full-pilot or training qualification. |
| F1 | SIM-DATA-03 | TASK-SIM-DATA-01 | full-pilot coverage blocked (unassigned) | Genuine v2 intake exists;42-recipe coverage remains incomplete. TVGEN-03 has36 retained recipes/138 pairs, six kitchen-sink gaps. Reconcile shared lineage and exact repaired-source evidence before authorized missing-cell capture; do not confuse catalog smoke with full pilot or duplicate direct-lane data. |
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
| — | TV-I1 | INTEGRATION-01 | external proposal; current-contract review required | Reconcile retired attestation assumptions against current producer. Assign only evidenced lifecycle gaps in TTR; do not restore obsolete identity machinery. |
| — | TV-I2 | INTEGRATION-01 | external proposal | TVTestRig owner assigns offline artifact publication |
| — | SA-A | 9-2 | external proposal | ScreenAuditKit owner assigns contracts/fake-backed rules |
| — | SA-B | 9-3 | external proposal | Consumer injection interface and dependency assignment |
| — | DOC-A | DOC-01 | guidance review; shared guides published/read back (NUIAK architect) | [Maintenance](reports/work/DOC-A/skills-20260923/handoff.md): corrected skills, operational lessons, SMB receipts and unique BP IDs. User approved standing contributor guide maintenance; both shared guides and DOC-A entry verified, other status fields preserved. Peer acknowledgment unverified. No runtime/model operation or new peer assignment. |
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
DS-G8 requires ≥0.85. Replacement r6 pixels now exist; review and an explicit
inference assignment remain required. Historical original pixels remain unavailable.

Detailed dispatch scope: [iOS platform delivery plan](Research/Plans/iOSPlatform.md).
These are substantial execution tranches over existing packets, not new task IDs:

| iOS deliverable | Existing packets / parent | What finishes the tranche | Office dependency |
|---|---|---|---|
| Recoverable, reproducible iOS corpus | P0-A/B/C; DATA-01 | Reviewed recovery decision, then separately authorized complete versioned splits and preservation evidence | None; reconstruction may require separately authorized iOS rendering |
| Integrated offline evaluation and readiness software | P1-A/P2-A/P3-A/P4-B/P5-A; 6a-10/11 | Review existing implementations, resolve assigned gaps, exercise required interfaces end-to-end, and verify all acceptance criteria | None |
| Run 009 iOS baseline and frozen diagnostics | P1-B/P2-B/P3-B; 6a-11 | Complete full-holdout predictions, compatible reference report, frozen regression membership/baseline | None; requires eligible iOS pixels and inference assignment |
| 41-class candidate readiness and execution | P5-B, TRAIN-S/F; 6a-10 | Frozen eligible inputs/configuration, then separately authorized smoke and full candidate | Planned mixed-data experiment needs qualified fixture corpus; Office remains released |
| Qualification and release evidence | TRAIN-Q, REL-A/B; 6a-10/DIST-02 | Independent holdout gates, package evidence, then maintainer-only promotion/tag | No fresh capture if accepted evaluation corpora exist |

**Next dispatch:** review the sealed r6 corpus, then separately authorize P1-B/P2-B/P3-B
Run009 baseline on the complete2,000-image replacement test split. Report absent-class
AP as unavailable. Offline software is already accepted; do not redispatch it wholesale.
Independent backup and remaining class/visual-axis coverage remain separate work.
Workers do not self-accept earlier review-ready packets. This plan does not assign
workers, start generation/inference/training, or restore Office permission.

### TASK-DATA-01: Phase 6a dataset recovery and preservation [!]

Evidence: [2026-09-19 inspection](reports/dataset_availability_2026-09-19.md).
Contract: [P0 recovery assessment and staged recovery](Research/DatasetRecoveryPlan.md).
Historical original export: all2,000 test links,10,543 training links and2,696
validation links were broken. This is not the availability of the new r6 corpus.
Cause is unknown. Preserve existing manifests, labels, links, and historical metrics.

- [!] P0-A: bounded recovery review found 0/15,239 expected originals at five documented roots; per-label identity evidence is partially verified (11,415/17,040) but local filesystem stalls prevent completion. See [`P0-A handoff`](reports/work/P0-A/handoff.md); P0-B still needs a recoverable source/copy assignment; authorized P0-C proceeded independently.
- [x] Replacement protocol and deterministic-variant continuation authorized; r6 delivered for review
- [ ] P0-B (separate assignment): stage and verify recoverable pixels/annotations without overwriting historical artifacts
- [ ] P0-C (fallback): r6 reconstruction and content seal review-ready ([handoff](reports/work/IOS-R6-20260923/handoff.md)). All16,940 members structurally validate under explicit Finder-only auxiliary exclusion; prior14,340 prefix and failed-run evidence preserved. Zero duplicates/leakage; coverage gaps and independent backup remain open. No model inference/training occurred.
- [ ] Record independent test-corpus and training-corpus readiness; uncertain/regenerated identity uses a new corpus version
- [ ] Establish content manifest, retention ownership, and recovery verification before expensive evaluation/training

**AC:** Every required corpus member has verified image/annotation evidence, or the unrecoverable original is explicitly documented and a separately reviewed replacement protocol is established. No real-data downstream gate closes on a plan or labels alone.

---

### TASK-6a-10: Full-frame fixture retraining (41-class iOS) [!]

**Blocked on qualified experiment inputs and launch approval, not blanket TTR availability.** Ingest software is accepted. Do not train on empty sidecars or `*_result.json` (model self-predictions). Format and IPC notes: [`Research/FixtureBatchIngest.md`](Research/FixtureBatchIngest.md).

**Current data boundary:** r6 has complete16,940-member structural evidence, but
train/validation/test class support is39/12/13. IOS-COV must resolve applicability
and coverage gaps; P5-B must bind eligible fixture and synthetic inputs before training.

**Requires:** Run 009 diagnosis (holdout mAP@0.5 = 0.586, DS-G8 ≥ 0.850). BP-32.

- [x] P4-B/P5-A original offline software accepted2026-09-19; configuration validity remains separate from launch eligibility
- [ ] P5-B: freeze eligible manifests and resolved configuration, including the explicit auxiliary role of tvOS examples; retain iOS-only reporting

- [x] `scripts/ingest_fixture_batch.py` + `scripts/test_ingest_fixture_batch.py` (16/16)
- [x] Coordinator IPC resolved in the recorded 2026-09-18 investigation; historical procedures are not current operating instructions
- [!] Existing development bundles do not establish required class coverage, held-out independence or training eligibility. Source descriptions are not attestation; revalidate exact artifacts at intake.
- [ ] P5-B: identify eligible auxiliary fixture inputs and their platform-specific role; Office is optional, not an iOS baseline prerequisite
- [ ] Blend fixture corpus with Phase 6a synthetic set; retrain from Run 009 `best.pt`, 150 epochs, cosine annealing + warmup
- [ ] Evaluate on TVTestRig `held-out` split **and** synthetic withheld-template holdout
- [ ] Per-class AP50 on toggle and stepperControl ≥ 0.88; badge belongs to the later TASK-BADGE-01 milestone
- [ ] TRAIN-S / TRAIN-F / TRAIN-Q evidence accepted separately; no automatic experiment reruns

**AC:** Fixture mAP@0.5 ≥0.94 and mAP@0.5:0.95 ≥0.78; toggle and stepperControl AP50 ≥0.88 with real support; separately, complete iOS synthetic withheld-template DS-G8 mAP@0.5 ≥0.85. Every future qualifying baseline/candidate report also records per-class AP and mean AP at IoU 0.50, 0.70 and 0.90 on the identical frozen cases; these geometry measurements complement rather than replace the existing gates. No platform-pooled mean or compact diagnostic suite substitutes for either holdout. Keep the shipped five-class model until release/promotion authority and evidence are complete.

---

### TASK-6a-11: Multi-corpus PyTorch reference eval [~]

**Requires:** a 6a-10 candidate, or continue using Run 009 weights as the baseline.

**Actual baseline:** r6's complete2,000-image test split is available for review.
Use the [r6 baseline contract](Research/Plans/EvaluationAndTraining.md#r6-baseline-tranche).
Verify checkpoint, data-use scope and inference approval; preserve0.586 as historical,
non-comparable evidence. No new inference has run.

- [x] `scripts/eval_reference_metrics.py` + `reports/pytorch_reference_metrics.json` (SHA-256 `226755b88642d1a68a0f9c3cad4b685d6d874352d48090b910c6b406ea61e405`)
- [x] Honest `available: false` for the three corpora that do not exist yet
- [x] P1-A/P2-A/P3-A original offline scopes accepted2026-09-19; targeted P2-METRICS correction remains separately reviewable
- [x] Per-image predicted boxes / scores / class IDs from baseline evaluation (prediction-artifact-v1 with 2,000 accounted images)
- [x] P1-B/P2-B: publish complete iOS Run 009 baseline artifacts with corpus/checkpoint/settings hashes; reconstructed pixels establish a new baseline, not reproduction of 0.586
- [x] P3-B: freeze 200–300 diagnostic cases where coverage supports it, with explicit gaps; retain the complete holdout for DS-G8 (250 members frozen via regression_selector)
- [ ] Populate `real_device_fixture_holdouts`, `production_tvos_system_holdout` when those image+box sets exist (`frozen_regression_suite` now populated)

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
explicit new user authorization. Old smoke requests are not continuing reservations.
Simulator operations require their own current assignment; prior authorized evidence
remains valid within its recorded scope, and this queue grants no runtime authority.

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

Dispatch contracts: R-A/R-B/R-C in [model/hardware packets](Research/Plans/ModelsAndHardware.md),
plus [R-LABEL](Research/Plans/RemainingDelivery.md#r-label--trustworthy-physical-holdout-annotations)
for quantitative ground truth. Screenshot count alone does not establish mAP support.

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

- [ ] ≥6,000 eligible labeled pairs through the qualified capture/intake path
- [ ] Mix: `gridMatrix` ≥ 2,000, `mediaShelf` ≥ 1,500, `settingsList` ≥ 1,000, `actionDialog` / `heroCarousel` / `focusMaze` ≥ 500 each
- [ ] ≥ 20% `light` and ≥ 20% `highContrast` in `gridMatrix` + `mediaShelf`
- [ ] Held-out hard-negative n ≥100 across `light`/`highContrast` × `imageView`/`collectionItem`; every combination nonempty with separate counts/results
- [ ] ALIGN-A/B: separately assigned ADR-0007 semantic alignment dataset/policy remains open; it is not a prerequisite for physical visual-focus capture or training
- [ ] All six quality gates, including **non-vacuous** hard-neg FPR ≤ 0.5%
- [ ] Replace bundled `.mlmodelc` only after those gates pass

Physical FR-B is fixture-only. Simulator Fixture/direct and native OS lanes have
separate contracts and operation scopes; no unrestricted Home/Settings crawl is granted. IPC: [`Research/FixtureBatchIngest.md`](Research/FixtureBatchIngest.md).

---

## Shared integration and later models

### TASK-INTEGRATION-01: Incremental TVTestRig compatibility [ ]

Contract: [TVTestRigIntegrationContract.md](Research/TVTestRigIntegrationContract.md).
TVTestRig owns producer implementation and its queue; this task owns NUA consumer compatibility.

- [x] H1: original source-pinned offline contract accepted; version-specific cases in [harvest-compatibility-v1.md](Research/schemas/harvest-compatibility-v1.md); producer bilateral acceptance/live evidence remain pending
- [x] P4-A: original offline validation/normalization accepted; offline integrity never implies trusted capture; evidence in `reports/work/P4-A/handoff.md`
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

Dispatch UNI-A/UNI-B via [model packets](Research/Plans/ModelsAndHardware.md#uni-a--unified-model-experiment-readiness);
numeric platform budgets and dedicated baselines precede any training assignment.

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

Contract: [MAC-A](Research/Plans/ModelsAndHardware.md#mac-a--macos-coordinate-spike).

- [ ] AppKit Y-flip: `y_flipped = window.contentView.bounds.height - frame.origin.y - frame.height`
- [ ] ±2 pt vs `NSBitmapImageRep` PNG
- [ ] `testMacOSCoordinateFlip` on macOS 15

#### TASK-6c-2: Templates + training

Contracts: [MAC-B/MAC-C](Research/Plans/ModelsAndHardware.md#mac-b--macos-generator-and-corpus).

- [ ] ≥2,000 macOS images with Y-flipped coordinates
- [ ] mAP@0.5 ≥ 0.80 on withheld-template test
- [ ] `tooltip` AP ≥ 0.70
- [ ] Export `NativeUIDetector_macOS_v1`

---

## Phase 9: ScreenAuditKit integration (remaining)

9-1 (`NativeUIRecognizing`) is done. These live in the ScreenAuditKit repo.

### TASK-9-2: Contract extension [ ]

Contract: [SA-A](Research/Plans/ConsumersAndRelease.md#sa-a--screenauditkit-contracts-and-native-rules);
external proposal until ScreenAuditKit assigns it under its own repository rules.

- [ ] `uiElements` required/forbidden/`minConfidence` on `ScreenAuditScreenContract`
- [ ] Rule IDs: `missingUIElement`, `unexpectedUIElement`, `uiElementBoundsViolation`, `uiElementTruncated`, `uiElementClipped`, `uiElementTargetTooSmall`, `inferredOSMismatch`
- [ ] `NativeUINoOpRecognizer` skips `uiElements` silently

### TASK-9-3: CLI flag [ ]

Contract: [SA-B](Research/Plans/ConsumersAndRelease.md#sa-b--dependency-bridge-and-native-cli-mode).

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

Contracts: [HIST-A](Research/Plans/ConsumersAndRelease.md#hist-a--history-remediation-decision-package)
and [HIST-B](Research/Plans/RemainingDelivery.md#hist-b--maintainer-history-disposition).

Working-tree PII is redacted. Real values remain in already-pushed git history. Do not rewrite history without an explicit go-ahead.

- [x] `PROVENANCE.md` written and linked
- [x] Training data audited clean
- [x] Working-tree PII redacted (2026-09-18)
- [!] HIST-B: maintainer disposition/recovery/migration; rewrite and force-push deferred without exact authority

### TASK-DIST-02: Next release tag [!]

Contracts: [REL-A/REL-B](Research/Plans/ConsumersAndRelease.md#rel-a--qualified-model-release-evidence).

API review is done (`NativeUIDetectionRequest` stays the public name; `FocusRingClassifier` stays internal).

- [x] API decisions in `Research/NativeUIElementDetection.md` §4
- [x] `scripts/verify_models_package_standalone.sh`
- [ ] Tag (e.g. `2.1.0`) after TASK-6a-10 ships DS-G8-passing 41-class weights; CHANGELOG cites that model and the `pytorch_reference_metrics.json` hash
