# Full backlog implementation packet catalog

## Focus improvement program — October 9

[FOCUS301](Plans/FocusImprovementProgram.md) defines 10 evidence-backed investigation priorities and independent execution contracts.
It reuses existing task IDs, scorers, trainers, and feedback tools.
The first batch checks causes with retained data. Later batches fill measured gaps and test 1 correction.
Each contract specifies inputs, metrics, limits, tests, acceptance, and ownership.
Coordination MVP1 gates remote dispatch, not local analysis. Tasks.md remains the sole queue.

## Production delivery order — October 7

Use [Tasks.md](../Tasks.md#production-roadmap--execution-order-october-7) for current priority, owner, readiness, and completion criteria.
The plan catalog below preserves experiment contracts. Its older “next” statements do not override the current queue.

The delivery sequence is measured failure, fixed comparison, regression acceptance, independent evaluation, CoreML parity, and optional TTR validation.
Each stage supplies evidence for the next. Coordination readiness alone supplies no model-quality evidence.

### Separate model decisions

[Release preparation](ReleasePreparation.md) defines RELEASE300 and the manual sequence for TTR 0.4.3 RC.
[Model release contract](ModelReleaseContract.md) defines offline catalog and archive checks. It is not an application installer.
[Sillycon-TTR handoff](TTRModelHandoff.md) records the implemented preview runtime, native installer limits, and required consumer checks.

[ADR-0024](ADR-0024-Opt-In-Model-Feedback.md) defines optional, reviewed feedback without navigation authority.
[Feedback contracts](Plans/OptInModelFeedback.md) define FEEDBACK298-A through D and separate consensus from labels.
[Release readiness](../reports/work/MODEL-DISTRIBUTION-293/readiness.md) records current inventory, real CLI checks, and unresolved release requirements.

[ADR-0023](ADR-0023-Optional-Model-Distribution.md) proposes optional model downloads through GitHub Releases, with resource-free SPM code.
[Optional model distribution](Plans/OptionalModelDistribution.md) defines 293-A through 293-F, with dependencies, tests, evidence, and approval boundaries.
Start inventory, package separation, and local installation together. TTR feedback does not block those offline tasks.
No release or API change occurs in the planning assignment.

[Focus signal and representation](Plans/FocusSignalRepresentation.md) records completed comparisons and defines TRANSITION299's fixed weak-effect diagnostic.
It separates positive additions from identical-image negatives. It reuses retained frames, unchanged roles, and both completed controls.

[EVAL90](Plans/FocusTransitionLearning49.md#october-7-execution-contract--real-app-evaluation) defines the bounded real-app evaluation contract.
Its 6 conditions remain separate from Fixture regression checks. Actual target, app, and label evidence precede capture.

- The transition model decides whether focus changes across frames. It also needs unchanged-content, scrolling, and disturbance tests.
- The single-frame focus model identifies focus appearance. It needs ordinary-profile artwork and hard-negative tests.
- iOS and tvOS element detectors locate and classify controls. Each needs its own taxonomy and full-screen geometry evaluation.
- An optional HCF model uses verified accessibility profiles. It cannot substitute assisted images for ordinary-profile evaluation.

Do not pool these metrics into one accuracy claim. Preserve the current shipped models until their replacement gates pass.

### Experiment-to-worker contract

NUIAK supplies exact training membership, exclusions, initializer, source, preprocessing, thresholds, schedule, resource limits, and acceptance criteria.
Big Dog verifies resident inputs and reports missing files before execution. Reuse retained packages where hashes match.
Return checkpoint identity, completion and failure records, complete predictions, timings, and resource measurements.
NUIAK independently checks parity, case accounting, and individual regressions before deciding admission or promotion.
TTR owns its optional observer integration, navigation safeguards, and current runtime evidence.
Source synchronization and local builds remain the normal TTR integration path.

### Production decision record

For each candidate, record development versus untouched evaluation groups, class/condition support, and the exact applicable quality gates.
Include precision, recall, abstention, false focus/change rates, geometry, latency, size, and grouped uncertainty where supported.
Name unsupported conditions. Do not convert missing labels or insufficient independent groups into passing scores.
The existing DS-G8, FocusRing, platform-specific, and package gates remain unchanged.
Agree any missing product acceptance thresholds before inspecting the corresponding final evaluation results.
Release evidence includes model identity, category map, preprocessing, rollback artifact, and the supported OS/profile matrix.
Simulator and physical-device results remain separate. All physical trials need their applicable scope.

### Review cadence

After each substantive comparison, update the task outcome and select the next hypothesis from measured errors.
After each peer delivery, reconcile exact receipts and update only the affected dependencies.
Keep completed experiments in the archive. Preserve failed evidence without presenting old launch requests as active work.
Keep topology, credentials, host-specific recovery details, and worker execution records in ignored coordination reports.

[Screen context / ADR-0022](ADR-0022-Screen-Context-for-Focus-and-Navigation.md):
proposed comparison of rules, a small visual classifier, and optional native evidence.
Measure downstream focus and navigation benefit before integration. This does not replace the current focus repair priority.

[Native focus effect measurement / TRANSITION-253](Plans/NativeFocusEffectMeasurement.md):
measure native geometry and appearance, fit a bounded renderer, verify reserved references, then test training usefulness.
October 7: mapping, background, smoothing, and color-space checks do not qualify the approximation for training.
Prioritize genuine native captures for the next controlled model comparison.
[Latest diagnostic and separate HCF access requirements](../reports/work/HCF-COLOR-263/handoff.md).

[Highest priority: focus improvement cycle](Plans/EvidenceDrivenFocusQualification.md#highest-priority--focus-improvement-cycle).
TRANSITION264 rejects position reweighting that preserves class totals but reduces unchanged content-change influence.
TRANSITION265 completes that position comparison with preserved condition weights. It improves left disturbances but loses artwork correctness.
TRANSITION266 completes balanced fitting and condition weighting. Targeted training improves, but retained regressions prevent promotion.
TRANSITION270 completes that initialization comparison. Small fitting reaches 64/64 and full replay reaches 668/668.
Disturbance regressions still block promotion. Next, audit training influence and compare retention-aware loss using admitted examples.
STATUS271 refines the decision: measure group weights, loss, gradients, and decision margins before choosing a training change.
INFLUENCE278 completes that audit. Opposing content-group gradients dominate remaining loss; two local perturbations confirm the trade-off.
CONFLICT281 completes the matched update comparison. The control reproduces DTM077 exactly; the treatment fails regression checks.
Next, measure signal preservation and spatial separation at model input resolution before selecting one representation comparison.
Use admitted labels for retention. Do not preserve an old model's mistakes through unverified target scores.
Keep challenge images outside training and report their repeated development use separately from independent evaluation.
Use admitted native data before further capture. [Evidence and next tranche](../reports/work/TRANSITION-270/handoff.md).
Repair 1 measured visual failure through local generation, controlled training and reserved evaluation.
NUIAK owns the complete cycle. TTR supplies missing capabilities asynchronously.
Big Dog supplies assigned analysis and training. Tasks.md records execution state.

[Evidence-driven focus / EVIDENCE223](Plans/EvidenceDrivenFocusQualification.md):
integrated cached reporting, native truth audit and matched authored baselines;
BD18/22/25/14/27 extensions, followed by qualified205/206 feedback campaign.

[Artwork-backed model improvement / 199–207](Plans/ArtworkModelImprovement204.md):
five integrated tranches:199+204 reusable diverse artwork;200/202 native campaigns;
205transition contrasts;206FocusRing hard negatives;207detector clutter utility.
Reuses existing contracts, keeps203 stretch/nonblocking and197 independent. Tasks.md
owns execution state; this plan is not a peer dispatch or model result.

[ADR-0020 / FOCUS-RENDER-203](ADR-0020-Procedural-Focus-Rendering-Feasibility.md):
bounded Big Dog prompt-only versus deterministic procedural focus-rendering spike;
geometry/repeatability checks, not native fidelity or training admission.

[ADR-0019 / RENDER-202](ADR-0019-Batched-Renderer-and-Asset-Pipeline.md): proposed
desktop-independent persistent native batching, Big Dog artwork reuse and explicitly
separate procedural augmentation; bounded qualification contract, not runtime evidence.

[LOCAL-IMAGE201](Plans/LocalImageGeneration201.md): high-priority Big Dog local
artwork preparation and Mac mini feasibility; installation approval gated, no generation yet.

[GEN-PARITY199 / IOS-ASSET200](Plans/GeneratorParity199.md): source-backed tvOS/iOS
generation gap audit, shared-artwork reuse/batch planning and bounded native adapter.

[Big Dog background backlog198](Plans/WorkerBacklog198.md): low-priority resident
audit, conditional CUDA benchmark, focus comparison and proposal scoring; reuse
existing TTR mining/QA assignments, preserve native admission and Apple qualification.

[UI-SOURCE177 findings and UI-IMPORT-A–D](Plans/UIComponentIntake.md): source-pinned
native component/media-screen intake strategy, licensing/dependency findings and
one generated-sheet geometry trial; low-priority adapters, not automatic imports.

[Generated media assets ART-A–D](Plans/GeneratedMediaAssets.md): low-priority
poster/thumbnail/avatar/backdrop library, bounded sheet prompts, deterministic crops,
native Fixture import and matched utility evaluation. Planning only; no generation
executed. Complements, does not replace, the deferred diverse native UI corpus.

[Next integrated focus-reliability tranche](Plans/FocusTransitionLearning49.md#next-integrated-tranche--focus-reliability)
orders three complementary outcomes: test training-only identical-frame negatives
after data-use approval; independently diagnose incorrect candidate selection; and
prepare independent evaluation plus source-backed layout28 intake. Tasks.md owns
execution state. The Settings mapping effort supplies incremental branch evidence,
not a prerequisite for the local diagnostics. Existing DTM018+DTM020 references remain.

[Changes since a101851](../reports/change-summary-since-a101851.md) summarizes native
intake, admission, model comparisons, preparation improvements and remaining gaps.

[RESOLUTION-96](Plans/FocusTransitionLearning49.md#resolution96--fixed-higher-resolution-change-head-comparison)
completed the192×128comparison and a failing identical-frame invariant probe;
derived-negative augmentation requires the requested maintainer decision.

[SIGNAL-95](Plans/FocusTransitionLearning49.md#signal95--resolution-evidence-before-another-experiment)
measures resolution signal and matched-negative coverage before another experiment.

[CONTEXT-93 / INTAKE-94](Plans/FocusTransitionLearning49.md#context93-and-intake94--paired-context-comparison-and-layout28-intake)
records the paired-context comparison and independently verified layout28transfer;
candidate replacement and new schema eligibility remain unmet.

[CHANGE-92](Plans/FocusTransitionLearning49.md#change92--admitted-native-action-adaptation-and-preparation-reuse)
completed one rejected change-head adaptation and removed repeated provenance
traversal; [handoff](../reports/work/CHANGE-92/handoff.md) records the next decision.

[PREP-91](Plans/FocusTransitionLearning49.md#prep91--single-decode-preparation-and-remaining-change-error-review)
removes duplicate endpoint decoding and diagnoses stationary-box identity changes;
preserves corpus hashes, labels and old experiment seals.

[EVAL-90](Plans/FocusTransitionLearning49.md#eval90--independent-transition-evidence-acquisition-contract)
separates useful Fixture training growth from missing independent native validation
and final sources. Planning only; actual membership and runtime prerequisites open.

[NATIVE-89](Plans/FocusTransitionLearning49.md#native89--fixed-paired-logit-diagnostic-and-runtime-response)
rejects fixed paired subtraction on retained evidence; runtime response delivered.
[Handoff](../reports/work/NATIVE-89/handoff.md).

[NATIVE-88](Plans/FocusTransitionLearning49.md#native88--frozen-failure-decomposition)
separates frozen ranking and change failures; no training. [Handoff](../reports/work/NATIVE-88/handoff.md).

[NATIVE-87](Plans/FocusTransitionLearning49.md#native87--guarded-admission-integration)
completed approved68/5admission and DTM020comparison. Settings paired0/5→2/5,
still exposed development rather than qualification. [Handoff](../reports/work/NATIVE-87/handoff.md).

[NATIVE-86](Plans/FocusTransitionLearning49.md#native86--action-membership-and-reusable-calibration-proposals)
delivers exact24action proposal and batched calibration candidates/encodings; role
decision remains separate from successful preparation. [Handoff](../reports/work/NATIVE-86/handoff.md).

[NATIVE-84](Plans/FocusTransitionLearning49.md#native84--source-backed-rich-and-collection-compatibility)
and [NATIVE-85](Plans/FocusTransitionLearning49.md#native85--retained-coverage-before-another-acquisition)
complete strict retained compatibility and coverage auditing; supersede historical
source/intake blockers below. New calibration roles and local runtime recovery remain
separate. [Handoff](../reports/work/NATIVE-84/handoff.md).

[NATIVE-83](Plans/FocusTransitionLearning49.md#native83--retained-collection-intake-and-local-runtime-diagnosis)
received/inspected36new pairs; strict semantic compatibility awaits source, local
capture awaits retained-operation recovery. [Handoff](../reports/work/NATIVE-INTAKE-83/handoff.md).

[INTAKE-82](Plans/FocusTransitionLearning49.md#intake82--portable-intake-and-admission-regression-boundary)
completes portable receipt/admission regression coverage and retained intake recheck;
rich-v2 source compatibility remains a separate blocker.
[Handoff](../reports/work/INTAKE-82/handoff.md).

[SIZE-81](Plans/FocusTransitionLearning49.md#size81--restore-candidate-scale-to-visual-ranking)
complete: training fit preserved, Settings endpoints 1/10 → 2/10 but pairs 0/5.
Small true controls remain missing; follow up through grouped coverage and retained
rich24 intake, not an unchanged model rerun. [Handoff](../reports/work/SIZE-81/handoff.md).

[CHANGE-80](Plans/FocusTransitionLearning49.md#change80--native-change-adaptation-and-ranking-diagnosis)
completed one change-only adaptation; native training misses fixed, Settings ranking
remains unqualified. [Handoff](../reports/work/CHANGE-80/handoff.md).

Latest BATCH79candidate:77role approval materialized44/5, DTM017completed with failing
Settings transfer. [Native handoff](../reports/work/BATCH-79-B/native-handoff.md).
This supersedes older pending-role/candidate statements below; no promotion.

[BATCH-79](Plans/FocusTransitionLearning49.md#batch79--retained-data-to-reusable-experiment-campaign)
is the integrated retained-data/cache/campaign contract. Reuse accepted tools rather
than another journal or trainer. Offline incremental-cache software is verified;
[B handoff](../reports/work/BATCH-79-B/handoff.md). Rich source publication, explicit
data-role/capture decisions and expanded candidate protocol remain pending.

[NATIVE-PROPOSALS-78](Plans/FocusTransitionLearning49.md#native-proposals78--calibration-coverage-before-training)
complete:24/24native endpoints covered by both unchanged proposers. Calibration
inputs retained for reuse,77data-role decision remains separate.

[NATIVE-ADMISSION-77](Plans/FocusTransitionLearning49.md#native-admission77--exact-native-role-proposal):
12native-table calibration→train proposal awaits explicit maintainer role decision.
Software guards/collector verified; no admission or training launched.

[NATIVE-INTAKE-76](Plans/FocusTransitionLearning49.md#native-intake76--retained-native-coverage-and-throughput)
received36native pairs and reviewed throughput reports.12directional pairs pass
inspection;24rich-v2pairs require source publication/consumer support. Training roles
unchanged. [Evidence](../reports/work/NATIVE-INTAKE-76/handoff.md).

[RANK-75](Plans/FocusTransitionLearning49.md#rank75--visual-ranking-and-crop-batching)
completed; [evidence](../reports/work/RANK-75/handoff.md). Visual ranking still fails
Settings transfer; batching/crop reuse verified. Native coverage remains next, not
another unchanged training run.

PROPOSAL-RANK-74 automatic union bank complete; [evidence](../reports/work/PROPOSAL-RANK-74/handoff.md).
Its planned visual-ranking comparison is now completed in RANK-75; native appearance
coverage is the remaining gap, not another unchanged box-regression run.

[PROPOSALS-73 / PROPOSAL-RANK-74](Plans/FocusTransitionLearning49.md#proposals73--candidate-coverage-diagnostic):
retained proposal coverage diagnosed; next build source-bound actual/oracle candidate
banks before training a visual ranker.

[COMPATIBILITY-72](Plans/FocusTransitionLearning49.md#compatibility72--producer-contract-binding):
wire-name mapping/source audit complete; stationary reference planning gap remains.

[CAMPAIGN-71](Plans/FocusTransitionLearning49.md#campaign71--campaign-to-corpus-batching):
offline campaign journal, incremental intake and dependency-scoped prepared reuse.
COVERAGE-70 completed both comparisons; native transfer remains unsolved.

[SPATIAL-TRANSITION-56](Plans/FocusTransitionLearning49.md#spatial56--spatial-fit-diagnostic-and-deconfounded-coverage-audit):
spatial fit diagnostic and coverage audit complete; DTM003 fails the4pair gate.
[GLOBAL-CONTEXT-57](Plans/FocusTransitionLearning49.md#next-proposal--global-context57-and-deconfounded-intake):
context diagnostic complete: cells8/8, boxes0/4; metadata intake CLI delivered.
[GEOMETRY-58](Plans/FocusTransitionLearning49.md#next-proposal--geometry58):
geometry-logit diagnostic2/4paired boxes; source inventory/debt cleanup complete.
[GEOMETRY-59](Plans/FocusTransitionLearning49.md#next-proposal--geometry59):
overlap diagnostic3/4paired boxes; no-scroll24case matrix delivered.
[GEOMETRY-60](Plans/FocusTransitionLearning49.md#next-proposal--geometry60):
tiny-fit gate passes4/4; full30epoch candidate underfits. Gradient evidence delivered.
[FIT-61](Plans/FocusTransitionLearning49.md#next-proposal--fit61):
full24/24training fit passed; Settings transfer fails; reporting improvements delivered.
[TRANSFER-62](Plans/FocusTransitionLearning49.md#next-tranche--transfer62):
completed169evaluations, no-scroll CLI and published producer compatibility request.
[ROBUSTNESS-63](Plans/FocusTransitionLearning49.md#next-tranche--robustness63):
completed translation comparison and source audit; robustness gain with fit regression.
[EXPOSURE-64](Plans/FocusTransitionLearning49.md#next-tranche--exposure64):
completed; trained-view fit restored, real-domain transfer still fails.
[GENERALIZATION-65](Plans/FocusTransitionLearning49.md#next-tranche--generalization65):
completed frozen probes and explicitly approved 32/5 admission.
[PREPARED-66](Plans/FocusTransitionLearning49.md#next-tranche--prepared66):
verified reusable training inputs integrated into existing trainer; no launch.
[DATA-67](Plans/FocusTransitionLearning49.md#next-tranche--data67):
completed controlled32pair candidate: perfect training fit, Settings transfer fails.
[TEMPORAL-68](Plans/FocusTransitionLearning49.md#next-tranche--temporal68):
completed: change decisions improve, localization remains unqualified; batch plan delivered.
[LOCALIZE-69](Plans/FocusTransitionLearning49.md#next-tranche--localize69):
completed; three-shape/position coverage gap measured and shared-encoding parity verified.
[COVERAGE-70](Plans/FocusTransitionLearning49.md#next-tranche--coverage70):
next two controlled geometry-coverage augmentation comparisons with one intake/batched evaluation.

[STORAGE-LIVE-01](Plans/ArtifactStorage.md): explicit read-only SSD mappings,
verified bulk migration, real-consumer compatibility and recovery instructions.

[DIRECT-TRANSITION-55](Plans/FocusTransitionLearning49.md#localization55--approved-controlled-comparison-and-metadata-companion):
completed localization-loss comparison and independent shipped metadata reconciliation;
DTM002 not usable, next representation diagnostic remains separately scoped.

[DIRECT-TRANSITION-54](Plans/FocusTransitionLearning49.md#execution54-approval--october3):
DTM001 approved split/30epoch execution, checkpoint parity and training-fit/transfer diagnosis.

[DIRECT-TRANSITION-53](Plans/FocusTransitionLearning49.md#direct-paired-image53):
direct six-channel box/change baseline,29source-bound pairs, exact role proposal;
implemented; exact split admitted and fit executed in54/55.

[CORRESPONDENCE-52](Plans/FocusTransitionLearning49.md#feature-correspondence52):
feature-consensus replay, mixed-motion diagnosis and direct paired-image next decision.

[CORRESPONDENCE-51](Plans/FocusTransitionLearning49.md#correspondence51--retained-pixel-comparison):
completed controlled wide-template replay and transfer check; default unchanged,
native positive correspondence still blocks the measurement learner.

[REFERENCE-TRANSITION-50](Plans/FocusTransitionLearning49.md#reference-transition50-continuation):
actual retained reference replay, whole-group feasibility and authorized8case acquisition;
capture cleanup failure and consumer correspondence—not missing authority—block training.

[FOCUS-TRANSITION-49](Plans/FocusTransitionLearning49.md): retained action-level audit,
paired-measurement learning/prediction adapter and admission-gated candidate. Separate
from single-frame FocusRing; current training blockers and ownership remain in Tasks.md.

[ACCESSIBILITY-TRACKING-30](Plans/AccessibilityTracking30.md): exact producer failure
diagnosis, retained alignment comparison and existing Home-reference preparation.
[Integrated handoff](../reports/work/ACCESSIBILITY-TRACKING-30/handoff.md).

[ACCESSIBILITY-ASSISTED-29](Plans/AccessibilityAssistedFocus29.md): current TTR
accessibility evidence, optional annotation-assistance contract and prioritized
ordinary real-pair qualification. High Contrast outlines and ordinary body boxes
remain separate; implementation/admission state is in Tasks.md.

[Settings Swift ADR](ADR-0018-Settings-Swift-Pixel-Parity.md): arithmetic port matches
the existing pipeline; tested Vision tracking substitution rejected. Local29/25
implementation and remaining real-data gaps are in the
[integrated handoff](../reports/work/ACCESSIBILITY-ASSISTED-29/handoff.md).

[NATIVE-FOCUS-TRANSFER-28](Plans/NativeFocusTransfer28.md): frozen-model cue probes,
real reference-pair coverage audit and guarded offline advisory caller. Local results
complete; real native-artwork paired evidence remains required before integration.

[NATIVE-FOCUS-EFFECT-SPIKE-26](Plans/NativeFocusEffectSpike26.md): approved native
focus capture/learning spike, 1,000 training plus 250 grouped evaluation pairs,
local USB storage and stage timings. Actual runtime qualification is recorded in
the linked handoff; source delivery and measured-body compatibility remain explicit.

[Corpus lifecycle ADR](ADR-0017-Corpus-Lifecycle-and-OS-Support.md): accepted OS
support and proportionate retention policy; automation backlog is CORPUS-LIFECYCLE-27.

[FOCUS-INTAKE-13](Plans/FocusIntake13.md): verified25 delivery, production crop QA,
single sampled-review queue and retained whole-scene gain/loss diagnostic. No new
training admission or runtime dispatch; Tasks.md holds next structural coverage work.

[LOCAL-TOOLS-02](../reports/work/LOCAL-TOOLS-02/handoff.md): completed CLI/MCP
implementation and bounded retained-image runtime verification under tranche 2.
Next assignment is focus corpus coverage, not another CLI wrapper.

[Local-first delivery](Plans/LocalFirstDelivery.md): current five-tranche scope and
acceptance contract. Tasks.md holds execution state. Supersedes conflicting older
next-action prose, not historical evidence or execution boundaries.

[FDR021-PIXEL-PARITY](Plans/FocusFDR021PixelParity.md): complete candidate-only
straight-RGB compatibility repair;333production input/score parity passes. TTR
consumer adoption/identity qualification is next, not another training run.

[FDR021-COREML](Plans/FocusFDR021Export.md): complete encoder+head exported/compiled;
333direct RGB parity passes, production opaque-buffer parity fails. Next assignment:
resolve alpha semantics with legacy regression evidence before TTR integration.

[FOCUS-REVIEW-CONTINUE-16](Plans/FocusReviewContinuation.md): integrated human
review/crop/admission/changed-data trainer path; real pending-state preflight and
generated positive/negative integration tests. New labels and model execution
remain separate gates, not unfinished adapter work.

[FOCUS-RETAINED-NEXT-15](Plans/FocusRetainedNext.md): retained coverage discovery,
actual FDR020 input/loss audit and conditional changed-data proposal. Four-frame
human review pending; no new model/capture execution.

[TRAIN-MPS-COMPARE-14](Plans/MPSBatchComparison.md): matched batch8/16local MPS
diagnostics, four trials under one1800s budget, no default/model promotion changes.

[TRAIN-MPS-DIAG-13](Plans/MPSBoundedTiming.md): frozen512/64 early-training
diagnostic through the existing trainer, guarded local MPS execution and receipts.

[TRAIN-OHEM-TIMING-12](Plans/OHEMBatchTiming.md): shape-compatible OHEM repair,
optional trainer timing and offline verification; no model execution.

[FOCUS-OFFLINE-PRODUCTIVITY-11](Plans/FocusOfflineProductivity.md): optional
annotation filtering, retained-score decision reporting and MPS-only efficiency
audit/benchmark preparation. No CUDA, inference, capture or training execution.

[FOCUS-R2-COMPAT-09](Plans/FocusR2CompatibilityCapture.md): strict additive recipe
compatibility, regression/caller tests and user-approved three-pair proof subject
to actual matched local runtime; no remaining21or training.

[FOCUS-CONTRAST-PREP-05](Plans/FocusMatchedAppearancePilot.md):24pair matched
appearance contract, producer capability request and first-proof acceptance;
preparation only, capture/training separately authorized.

[FOCUS-FIT-PREP-02](Plans/FocusFullCorpusFitPreparation.md): full-corpus fitting
proposal and retained artwork receipt/crop review; no training execution.
Its explicit execution amendment assigns FOCUS-FULL-FIT-03/FDR020, now complete:
[handoff](../reports/work/FOCUS-FULL-FIT-03/handoff.md).

[FOCUS-REPAIR-INTAKE-04](Plans/FocusRepairIntake04.md): producer repair receipts,
real supplied-sidecar consumer tests and artwork-policy compatibility review.

[FOCUS-INTEGRATION-03](Plans/FocusIntegrationReadiness03.md): retained TTR Vision
import acceptance and exact development-validation coverage/next-experiment decision.

[Optional annotation Vision import](Plans/AnnotationVisionImport.md): user-added
scope alongside FOCUS-GEOMETRY-LIVE-02; supplied OCR/boxes only, no automatic labels.

[FOCUS-GEOMETRY-LIVE-02](Plans/FocusGeometryLive02.md): updated local TTR acceptance,
bounded measured artwork trial, crop comparison and next-data decision.

[FOCUS-CONTROL32-ADMIT-01](Plans/FocusControl32Admission.md): exact approved
32-pair data admission and additive assembly; no model execution approval.

[FOCUS-OFFLINE-PREP-03](Plans/FocusOfflinePreparation03.md): completed duplicate
sensitivity,64pair consumer preparation and exact retained-pair addition proposal;
no capture/training/admission.

[VISION-ANNOTATION-COMPARE-01](Plans/VisionAnnotationComparison.md): completed
fixed native rectangle/OCR comparison; optional filtering trial recommended.

[ANNOTATOR-AUTO-DETECT-01](Plans/AnnotatorAutoDetect.md): optional local candidate
rectangles and batch preview in the existing human-review editor.

[FOCUS-GEOMETRY-ADAPTER-01](Plans/FocusGeometryAdapter.md) implements the explicit
diagnostic artwork-layout role through existing native intake and production crops.

[FOCUS-GEOMETRY-CORPUS-01](Plans/FocusGeometryCorpus.md) specifies retained reuse,
geometry roles and a bounded contrast trial; no automatic model/device execution.

[FOCUS-PAIRED-INTAKE-01](Plans/FocusPairedIntake.md) implements one approved cached
paired-loss experiment and independently receives/validates native12/native100.

[FOCUS-ARTWORK-AUDIT-01](Plans/FocusArtworkAudit.md) audits retained artwork contrasts
and proposes the bounded next representation/ranking experiment after FDR015.

[FOCUS-RESET-01](Plans/FocusDiagnosticReset.md) reconciles cached ranking, runtime
selection and strict gate metrics, inspects crops, and bounds a pretrained baseline.

[HUMAN-BENCHMARK-02](Plans/HumanSupplementBenchmark.md) admits the reviewed real-app
supplement for development regression and compares shipped/FDR-010 at fixed0.85;
no training admission or invented full-frame completeness.

[FOCUS-REPRESENTATIVE-01](Plans/FocusRepresentativeValidation.md) freezes real and
synthetic development validation and a coverage-driven production campaign without
another training run or implicit capture. [SYNTH05 intake](Plans/Synth05ConsumerIntake.md)
supplies native artwork/hierarchy diagnostics, not training admission.

[FDR-010 / limited production milestone](Plans/FocusLimitedProduction.md) binds
the approved single gap-targeted development run, frozen real-screen comparison,
conditional observer artifact and unchanged production qualification requirements.

[SYNTH-FOCUS-FACTORY-01](Plans/SyntheticFocusFactory.md) defines approved synthetic
factory direction, dock repair qualification, clean configurable canvas, native
sweep/pair semantics and bounded campaign acceptance. Deployment/producer edits
remain explicitly gated; Tasks.md records current ownership and blockers.

[SIM-FOCUS-DEV-01](Plans/LocalSimulatorFocusDevelopment.md) has collected/reviewed
52 local TTR/Fixture pairs and implemented explicit training-extension admission.
The approved narrower retention-selected FDR-009 completed30 epochs; epoch3 retained
18/18 native decisions. [Run handoff](../reports/work/FDR-009/handoff.md). Full candidate
gates remain unchanged; transfer evaluation is next. Local capture is qualified for the
completed four-control recipes, not remote switching or the failed nine-control dock.

[FOCUS-OFFLINE-DIAG-01](Plans/OfflineFocusDiagnosis.md) diagnoses retained validation
scores, audits candidate coverage and prepares the EXT-CAP-01 consumer checklist;
no inference, challenge analysis or hardware operation.

[TTR-EXTERNAL-CONTROL-01](Plans/TTRSupervisedExternalControl.md) is the P0 human-approved
external pairing/qualified-lease and capture-delivery workflow request. Current work
is documentation/coordination; producer implementation needs its own assignment.
Tasks.md remains the authoritative queue.

[PHOTOS-PILOT-01](Plans/PhotosFocusPilot.md) prepares the supervised, user-driven
Office Photos pilot and diagnostic human-review intake. No native label substitution,
training admission, model inference or autonomous navigation; live readiness and
maintainer availability remain separate from software verification.

[TEMP-FOCUS-DEV](Plans/TemporalVisualVerificationSpike.md#assigned-development-precursor-temp-focus-dev-2026-09-23)
is the retained-image temporal localization precursor; genuine ordered journeys,
interruptions and end-to-end detector geometry remain separate TEMP-LIVE work.

[APPEAR-EVAL-RESERVE](Plans/FocusAppearanceAcquisition.md#appear-eval-reserve--reservation-acquisition-and-candidate-preparation)
groups untouched source reservations, missing-coverage acquisition/intake, evaluation
freeze and one candidate preparation. [Reservation requirements](../reports/work/APPEAR-EVAL-RESERVE-20260923/reservation-plan.md)
are not admitted evaluation membership. Training requires separate approval.
[September27 received-data tranche](Plans/FocusAppearanceAcquisition.md#next-tranche--received-data-intake-and-validation-baseline-2026-09-27)
specifies the approved local intake, validation-only comparison and candidate
preparation. [September27 findings](../reports/work/APPEAR-EVAL-RESERVE-20260927/metrics.md)
recommend no model replacement; final challenge stays unscored. Current
priority/ownership is in Tasks.md.

**Revision:** 7, 2026-09-24. Adds measured training-efficiency contracts under [ADR-0011](ADR-0011-Measured-Training-Efficiency.md). Existing contracts remain valid except explicit amendments. State/ownership lives only in [Tasks.md](../Tasks.md); dependencies in [IterationRoadmap.md](IterationRoadmap.md). Plans are not execution authority or evidence that work ran.

## Supplemental packet index

Every queued packet has an explicit row in this catalog. The tables contain contracts,
not a second status board. Completed evidence linked elsewhere does not replace a
forward contract. Apply [review-ready completion rules](Plans/QueueCompletion.md#review-ready-work)
to review rows; do not redispatch accepted implementation. Historical next-action
paragraphs below are context; current dispatch and ownership are in Tasks.md.

| Packet | Contract |
|---|---|
| HUMAN-REVIEW-01 | [Local setup and real annotation round trip](Plans/LocalHumanAnnotationReview.md#human-review-01--local-setup-and-real-annotation-round-trip) |
| HUMAN-REVIEW-02 | [Defect audit and review queues](Plans/LocalHumanAnnotationReview.md#human-review-02--audit-defects-and-prioritize-review) |
| HUMAN-REVIEW-03 | [Automatic recorder-to-review integration](Plans/LocalHumanAnnotationReview.md#human-review-03--connect-the-automatic-recorder-to-review) |
| HUMAN-REVIEW-04 | [Human-label admission and dataset candidate](Plans/LocalHumanAnnotationReview.md#human-review-04--explicit-human-label-admission-and-dataset-candidate) |
| TRAIN-EFF-A | [Effective-configuration audit and offline tooling](Plans/TrainingEfficiency.md#train-eff-a) |
| TRAIN-EFF-B | [Isolated throughput and stage-cost benchmark](Plans/TrainingEfficiency.md#train-eff-b) |
| TRAIN-EFF-C | [Adoption and bounded learning comparison](Plans/TrainingEfficiency.md#train-eff-c) |
| APPEAR-A | [Implementation and acceptance](Plans/FocusAppearanceAcquisition.md#appear-a--source-capability-audit-and-bounded-ground-truth-pilot) |
| APPEAR-A1 | [Implementation and acceptance](Plans/FocusAppearanceAcquisition.md#appear-a1-integrated-software-tranche-assigned-2026-09-23) |
| APPEAR-B | [Implementation and acceptance](Plans/FocusAppearanceAcquisition.md#appear-b--freeze-independent-challenge-and-one-future-experiment-proposal) |
| APPEAR-B1 | [Implementation and acceptance](Plans/FocusAppearanceAcquisition.md#appear-b1--development-proposal-adapter) |
| APPEAR-C | [Implementation and acceptance](Plans/CatalogAppearanceQualification.md) |
| APPEAR-EVAL-RESERVE | [Implementation and acceptance](Plans/FocusAppearanceAcquisition.md#appear-eval-reserve--reservation-acquisition-and-candidate-preparation) |
| DATA-PROBE-INTAKE | [Implementation and acceptance](Plans/VisualStateCoverage.md#data-probe-intake--offline-export-admission) |
| FOCUS-COMPRESS-01 | [Implementation and acceptance](Plans/NativeOSFocus.md#focus-compress-01--assigned-2026-09-22) |
| FOCUS-EXP-01 | [Implementation and acceptance](Plans/FocusLearningExperiment.md) |
| FOCUS-EXPORT-01 | [Implementation and acceptance](Plans/NativeOSFocus.md#assigned-candidate-exportparity--2026-09-22) |
| FOCUS-PARITY-01 | [Implementation and acceptance](Plans/FocusIntegrationReplay.md) |
| FOCUS-VISUAL-01 | [Implementation and acceptance](Plans/NativeOSFocus.md#focus-visual-01--reviewed-appearance-comparison-assigned-2026-09-22) |
| FOCUS-VISUAL-02 | [Implementation and acceptance](Plans/NativeOSFocus.md#focus-visual-02--existing-home-appearance-comparison-assigned-2026-09-23) |
| OS-FOCUS-01 | [Implementation and acceptance](Plans/NativeOSFocus.md) |
| OS-FOCUS-02 | [Implementation and acceptance](Plans/NativeOSFocus.md#native-expansion-tranche--2026-09-22) |
| OS-FOCUS-03 | [Implementation and acceptance](Plans/NativeOSFocus.md#os-focus-03--deterministic-home-screen-coverage) |
| OS-FOCUS-04 | [Implementation and acceptance](Plans/NativeOSFocus.md#os-focus-04--incremental-native-and-fixture-corpus) |
| P2-METRICS | [Implementation and acceptance](Plans/QueueCompletion.md#p2-metrics) |
| REPO-CLEANUP-20260923 | [Implementation and acceptance](Plans/QueueCompletion.md#repo-cleanup-20260923) |
| TEMP-FOCUS-DEV | [Implementation and acceptance](Plans/TemporalVisualVerificationSpike.md#assigned-development-precursor-temp-focus-dev-2026-09-23) |
| TTR-CATALOG-01 | [Implementation and acceptance](Plans/QueueCompletion.md#ttr-catalog-01) |
| TTR-PROVIDER-01 | [Implementation and acceptance](Plans/QueueCompletion.md#ttr-provider-01) |

## Remaining-work amendments and direct acquisition

[APPEAR-C catalog/appearance qualification](Plans/CatalogAppearanceQualification.md)
delivers bounded real catalog intake and independent-evaluation readiness audit.
Theme aliases and one common renderer family must not become false holdout coverage.
The [integrated family tranche](../reports/work/APPEAR-FAMILY-EVAL-20260923/handoff.md)
now includes new-preset intake,19-pair/neighbor-sensitivity comparisons and expanded
development membership. [Next grouped assignment](../reports/work/APPEAR-FAMILY-EVAL-20260923/next-tranche.md)
combines reservation, bounded acquisition/intake, independent evaluation and preparation
for one separately authorized candidate, rather than separate helper-sized handoffs.

[APPEAR-B1 development adapter](Plans/FocusAppearanceAcquisition.md#appear-b1--development-proposal-adapter)
now has an [integrated handoff](../reports/work/APPEAR-B1/handoff.md) and
[versioned contract](schemas/focus-appearance-experiment-v1.md). Existing entrypoints
consume frozen membership/source-balanced weights while retaining missing independent
evaluation, selection-reference and approval blockers. No operation authority implied.

[APPEAR-A1 bounded catalog extension](Plans/FocusAppearanceAcquisition.md#appear-a1-integrated-software-tranche-assigned-2026-09-23)
now has an [integrated handoff](../reports/work/APPEAR-A1/handoff.md): source-pinned24-group
catalog, offline readiness and production intake regression coverage. Old contracts
remain intact. The APPEAR-A2 pilot subsequently completed; remaining independent
evaluation is APPEAR-EVAL-RESERVE, not repeated pilot capture.

[APPEAR-A/B](Plans/FocusAppearanceAcquisition.md) turn FDR-008's measured Home/Photos
failures into a source-capability audit, separately authorized bounded pilot and
independent appearance evaluation. They do not authorize producer edits or another run.

[OS-FOCUS-04 development-experiment integration](schemas/focus-development-experiment-v1.md)
extends existing assembly and trainer preflight for reviewed retained Fixture/native
data. The [one-run proposal](../reports/work/FOCUS-RETAINED-01/experiment-proposal.md)
remains separate from production eligibility and execution approval. No TTR dependency.

[SIM-DATA-02 sidecar-v2 extension](schemas/harvest-compatibility-v1.md#assigned-sidecar-v2-consumer-extension--2026-09-23)
covers strict producer brackets, simulator-only v1.5 production crops and existing
baseline integration. Offline compatibility does not qualify a fresh producer build.

[FOCUS-VISUAL-01](Plans/NativeOSFocus.md#focus-visual-01--reviewed-appearance-comparison-assigned-2026-09-22)
compares reviewed appearances, frame focus decisions and box sensitivity across
shipped/FP16/int8 without admitting legacy images for training.

[FOCUS-COMPRESS-01](Plans/NativeOSFocus.md#focus-compress-01--assigned-2026-09-22)
isolates one weight-only int8 candidate and compares it to preserved FP16/Torch.
[PER-DATA bounded review](Plans/RemainingDelivery.md#per-data--reviewed-real-perception-benchmark)
admits explicitly reviewed legacy native evidence for development only, with
unknown-source/privacy/training safeguards. Neither packet changes shipped models.

[FOCUS-EXPORT-01: isolated candidate CoreML parity](Plans/NativeOSFocus.md#assigned-candidate-exportparity--2026-09-22)
binds experimental export identity to FDR-007 and compares production CoreML CPU
against frozen Torch challenge evidence. No capture, training or promotion.

[FOCUS-EXP-01: bounded focus-learning experiment](Plans/FocusLearningExperiment.md)
compares checkpoint initialization and crop shape using reviewed, screen-grouped
native data through an isolated experimental entrypoint in the existing trainer.
It does not waive production data or model gates.

[FOCUS-PARITY-01: record/replay/compare](Plans/FocusIntegrationReplay.md) isolates
actual producer/consumer preprocessing before attributing failures to model weights.

[OS-FOCUS-04: incremental native/fixture corpus](Plans/NativeOSFocus.md#os-focus-04--incremental-native-and-fixture-corpus)
defines immutable additions and existing-trainer integration without waiting for TTR.
The [native incremental slice](../reports/work/OS-FOCUS-03/handoff.md) now has
protocol v2, one completed candidate and separate challenge evaluation; broader
mixed-source integration remains open. See the [next boundary](Plans/NativeOSFocus.md#latest-delivery-and-next-boundary).

[OS-FOCUS-01/02: independent native OS focus](Plans/NativeOSFocus.md) adds a
third acquisition lane, using native XCTest observations rather than Fixture or
TTR services. Runtime execution and data admission are separate checkpoints.

[OS-FOCUS-03: deterministic Home coverage](Plans/NativeOSFocus.md#os-focus-03--deterministic-home-screen-coverage)
extends that lane with observed-graph snakes, conditional spirals and short
direction-pair coverage; it is not implemented by the initial Settings probe.

[RemainingDelivery.md](Plans/RemainingDelivery.md) supplies missing contracts.
Existing detailed packets remain canonical. Review-ready work needs evidence review,
not automatic reimplementation; preserve active owners. Current source-kind policy
and explicit scoped assignments supersede retired attestation, Office-first and
blanket-pause assumptions in historical contracts.

| Packet | Contract |
|---|---|
| TV-FIX | [Detailed implementation contract](Plans/RemainingDelivery.md#tv-fix--native-fixture-focus-identity-repair) |
| TVGEN-01 | [Detailed implementation contract](Plans/RemainingDelivery.md#tvgen-01--reuse-and-runtime-design-review) |
| TVGEN-02 | [Detailed implementation contract](Plans/RemainingDelivery.md#tvgen-02--complete-direct-runner-admission-and-native-smoke) |
| TVGEN-03 | [Detailed implementation contract](Plans/RemainingDelivery.md#tvgen-03--full-development-pilot-and-shipped-baseline) |
| TVGEN-04 | [Detailed implementation contract](Plans/RemainingDelivery.md#tvgen-04--qualified-direct-scale-corpus-and-training-handoff) |
| DATA-RET | [Detailed implementation contract](Plans/RemainingDelivery.md#data-ret--corpus-retention-and-recovery-verification) |
| IOS-COV | [Detailed implementation contract](Plans/RemainingDelivery.md#ios-cov--reconstruction-coverage-and-41-class-qualification-decision) |
| PER-DATA | [Detailed implementation contract](Plans/RemainingDelivery.md#per-data--reviewed-real-perception-benchmark) |
| PER-LIVE | [Detailed implementation contract](Plans/RemainingDelivery.md#per-live--real-chevrondialog-baseline-and-training-decision) |
| TEMP-LIVE | [Temporal visual-verification spike](Plans/TemporalVisualVerificationSpike.md); [real transition-readiness qualification](Plans/RemainingDelivery.md#temp-live--genuine-transition-readiness-evaluation) |
| ID-LIVE | [Detailed implementation contract](Plans/RemainingDelivery.md#id-live--genuine-screen-and-row-identity-evaluation) |
| R-LABEL | [Detailed implementation contract](Plans/RemainingDelivery.md#r-label--trustworthy-physical-holdout-annotations) |
| DATA-VIS | [Detailed implementation contract](Plans/RemainingDelivery.md#data-vis--controlled-visual-state-coverage) |
| DATA-STATE-01 | [Native state contract and residual contrasts](Plans/VisualStateCoverage.md#packet-boundaries-and-remaining-delivery) |
| DATA-SCHEDULE-01 | [Bounded schedule contract](Plans/VisualStateCoverage.md#packet-boundaries-and-remaining-delivery) |
| DATA-PROBE-01 | [Adapter and native qualification contract](Plans/VisualStateCoverage.md#packet-boundaries-and-remaining-delivery) |
| TTR-DIALOG-01 | [Software review and genuine intake](Plans/QueueCompletion.md#ttr-dialog-01) |
| FOCUS-RECEIPT-01 | [Actual focus execution and consumer migration contract](Plans/FocusExecutionReceipt.md) |
| DATA-SIM | [Detailed implementation contract](Plans/RemainingDelivery.md#data-sim--near-duplicate-similarity-feasibility) |
| ALIGN-A | [Detailed implementation contract](Plans/RemainingDelivery.md#align-a--semantic-alignment-contract-and-offline-policy) |
| ALIGN-B | [Detailed implementation contract](Plans/RemainingDelivery.md#align-b--semantic-dataset-qualification) |
| HIST-B | [Detailed implementation contract](Plans/RemainingDelivery.md#hist-b--maintainer-history-disposition) |
| EVIDENCE-AUDIT | [Accepted audit evidence](../reports/work/EVIDENCE-AUDIT/handoff.md); reuse, do not reopen |
| FOCUS-LAUNCH | [Launch preparation](Plans/FocusRingLaunchPreparation.md); accepted scope only |
| FOCUS-CONSUMER | [Consumer readiness](Plans/FocusRingConsumerReadiness.md); accepted scope only |

Residual mapping: iOS recovery→P0-A/B/C+DATA-RET+IOS-COV; actual references→
P1-B/P2-B/P3-B+P4-L+R-LABEL/R-C; visual focus→TVGEN or SIM-DATA then FR-SIM;
physical transfer→FR-B/C; real perception→PER-DATA/PER-LIVE/TEMP-LIVE/ID-LIVE;
semantic work→ALIGN-A/B. Later models, consumers and release retain detailed
contracts below. Accepted software never silently closes data/integration/model gates.

## Failure-driven TTR perception priority amendment

[TTRPerception.md](Plans/TTRPerception.md), revision 1 (2026-09-21), defines the next
new offline tranche: PER-01 + PER-02 chevron/dialog benchmark, followed by visual-focus
readiness. It preserves active workers and existing model/data gates. Proposed TTR
requests are not published or assigned. No capture or training follows from this catalog.

2026-09-22 targeted completion: [PerceptionIntakeCompletion.md](Plans/PerceptionIntakeCompletion.md)
defines the assigned PER-02/PER-04 integration and existing-deliverable review;
do not redispatch already implemented foundations. Evidence:
[integrated handoff](../reports/work/PERCEPTION-INTAKE/handoff.md).

2026-09-22 architect review: [PerceptionAcceptance.md](Plans/PerceptionAcceptance.md)
defines the evidence/acceptance tranche; [decision and gaps](../reports/work/PERCEPTION-ACCEPTANCE/handoff.md)
supersede the earlier pending-review guidance. No live controller or dataset qualification
is implied by offline packet acceptance.

| Packet | Contract |
|---|---|
| PER-01 | [Evidence and split-safe benchmark](Plans/TTRPerception.md#per-01--evidence-inventory-labels-and-split-safe-benchmark-contract) |
| PER-02 | [Chevron/dialog benchmark and training decision](Plans/TTRPerception.md#per-02--chevron-and-dialog-benchmark-and-targeted-training-decision) |
| PER-03 | [Targeted data and one candidate](Plans/TTRPerception.md#per-03--targeted-data-and-one-perception-candidate) |
| PER-04 | [Visual-focus readiness](Plans/TTRPerception.md#per-04--visual-focus-robustness-and-physical-consumer-readiness) |
| PER-05 | [Transition-readiness evaluation](Plans/TTRPerception.md#per-05--bounded-transition-readiness-evaluation); [v1 sequence/observation contract](schemas/transition-sequences-v1.md); [handoff](../reports/work/PER-05/handoff.md) |
| PER-06 | [Screen/row identity](Plans/TTRPerception.md#per-06--screen-and-row-identity-under-change); [v1 identity contract](schemas/identity-benchmark-v1.md); [handoff](../reports/work/PER-06/handoff.md) |
| TTR-PER | [External evidence/comparison proposal](Plans/TTRPerception.md#ttr-per--producer-evidence-and-isolated-comparison-proposal) |

## Historical Office model-delivery amendment

[OfficeFocusRing.md](Plans/OfficeFocusRing.md), revision 1, refines existing P4-L/FR-B/FR-C
without duplicate packet IDs: one authorized smoke request, intake, separately authorized
physical visual pilot/baseline/corpus, candidate and TTR comparison. Sequencing is now
superseded by [ADR-0008](ADR-0008-Simulator-First-tvOS-FocusRing-Development.md):
simulator first, Office later for transfer validation. Plans do not grant execution.

## Common execution contract

2026-09-22 assigned TVGEN-01/02/03 and independent TTR smoke:
[ParallelTVOSAcquisition.md](Plans/ParallelTVOSAcquisition.md).
[Implementation evidence and remaining live blocker](../reports/work/TVGEN/handoff.md).
The direct lane avoids desktop capture/export but still depends on trustworthy
Fixture-native labels. A reference screenshot is not a completed focus sweep.

[Approved ADR-0009 TVGEN-01–04](ADR-0009-Direct-tvOS-Simulator-Generation.md#implementation-tranches)
defines the parallel direct tvOS generator tranches, now refined in RemainingDelivery:
two-control native proof → 42-recipe shipped-model baseline → separately authorized
scale/training handoff. Preserve delivered TVGEN-01/02 work; the ADR itself grants no
runtime authority.

[IterationEfficiency.md](IterationEfficiency.md) defines change-scoped test cadence,
producer handoff evidence and prioritized visual-state coverage. Apply it within
existing packets; do not reopen accepted software or weaken qualification gates.

Platform-oriented grouping for the existing iOS packets:
[iOS platform delivery plan](Plans/iOSPlatform.md). It defines substantial execution
tranches without duplicating the Tasks.md state/ownership queue or changing model gates.

**Execution amendment (2026-09-19):** Rows are reviewable contracts, not mandatory
turn boundaries. Dispatch substantial coherent tranches when the user requests broader
work; finish all assigned packets, integration, verification, and handoff before ending
the turn. AGENTS.md's execution contract overrides any interpretation of "bounded" as
permission to stop after a helper. Per-packet gates and safety authority remain unchanged.

- Read AGENTS.md's mandatory research sequence before code, [WorkerWorkflow.md](WorkerWorkflow.md), the [worker skill](WorkerExecution/SKILL.md), and only the assigned packet plus its named context. Do not load all packet documents merely to execute one row.
- Assignment must name the packet/revision, owning repository, allowed operation and current owner. Check pre-existing changes before editing; evidence of a new worker script is not permission to overwrite it. Coordinate shared schemas/queue edits through the architect.
- File scope includes the packet's named implementation files, tightly related tests and required research changes, plus additive reports. Expansion to another subsystem/repository or a new gate requires an explicit amended assignment.
- Software permits scoped edits and offline tests; real inference, generation, harvest, recovery copy, training, promotion and git writes are separate authorities. Preserve project filesystem boundaries, caches and historical artifacts. External packet proposals execute only in their owner's authorized workspace.
- Each handoff uses `reports/work/<packet-id>/handoff.md` (or authorized external equivalent) and records four outcomes: **software verified**, **data eligible**, **integration qualified**, **model gate passed**. Values are pass/fail/not-run/not-applicable with reasons/evidence. Integrity and provenance are distinct subclaims of data/integration; mock integrity does not imply trusted data.
- Code changes require focused behavioral tests plus offline `swift build`/`swift test` with in-project output/cache/temp settings. No network dependency resolution. Documentation-only changes need link/content/diff review. Record missing prerequisites and unrelated existing failures honestly.
- Stop only the affected operation for unavailable inputs or new authority. Complete independent in-scope software work. No repeated deterministic failure, automatic experiment sweep, live retry loop or fabricated result.
- Handoff includes changed files, base revision/dirty-state preservation, commands/exit codes, model/corpus/settings hashes where applicable, criterion-by-criterion evidence, synthetic vs real scope, learnings and next unblocked action. Worker marks review; architect accepts. Parent tasks close only when their own AC pass.

## Recovery, evaluation and readiness

| Packet | Parent | Contract |
|---|---|---|
| P0-A | TASK-DATA-01 | [Bounded recovery assessment](DatasetRecoveryPlan.md#p0-a--bounded-recovery-assessment) |
| P0-B | TASK-DATA-01 | [Staged recovery](DatasetRecoveryPlan.md#p0-b--staged-recovery-and-verification-separate-assignment) |
| P0-C | TASK-DATA-01 | [Versioned reconstruction](DatasetRecoveryPlan.md#p0-c--versioned-reconstruction-fallback) |
| H1 | TASK-INTEGRATION-01 | [Source-pinned harvest contract](TVTestRigIntegrationContract.md#h1--pin-the-current-compatibility-contract) |
| P1-A | TASK-6a-11 | [Prediction export software](Plans/EvaluationAndTraining.md#p1-a--prediction-export-software) |
| P1-B | TASK-6a-11 | [Real baseline inference](Plans/EvaluationAndTraining.md#p1-b--run-009-real-baseline-inference) |
| P2-A | TASK-6a-11 | [Reference-comparison software](Plans/EvaluationAndTraining.md#p2-a--reference-comparison-software) |
| P2-B | TASK-6a-11 | [Real reference integration](Plans/EvaluationAndTraining.md#p2-b--real-reference-integration) |
| P3-A | TASK-6a-11 | [Regression-selector software](Plans/EvaluationAndTraining.md#p3-a--deterministic-regression-selector-software) |
| P3-B | TASK-6a-11 | [Freeze/evaluate real suite](Plans/EvaluationAndTraining.md#p3-b--freeze-and-evaluate-real-regression-suite) |
| P4-A | TASK-INTEGRATION-01 / TASK-6a-10 | [Bundle validation/normalization](Plans/EvaluationAndTraining.md#p4-a--consumer-bundle-validation-and-normalization) |
| P4-B | TASK-6a-10 | [Split-safe assembly](Plans/EvaluationAndTraining.md#p4-b--split-safe-assembly-software) |
| P4-L | TASK-INTEGRATION-01 | [Genuine-bundle qualification](TVTestRigIntegrationContract.md#p4-l--first-genuine-bundle-integration) |
| P5-A | TASK-6a-10 | [Configuration-only preflight](Plans/EvaluationAndTraining.md#p5-a--validation-only-training-preflight) |
| P5-B | TASK-6a-10 | [Actual candidate readiness](Plans/EvaluationAndTraining.md#p5-b--actual-candidate-readiness) |

## tvOS Simulator datasets

Offline launch preparation: [FOCUS-LAUNCH](Plans/FocusRingLaunchPreparation.md),
with [runtime crop/baseline](schemas/focus-consumer-v1.md) and
[capture-plan](schemas/focus-capture-plan-v1.md) interfaces. This does not authorize capture/training.

Offline extension: [FocusRing consumer readiness](Plans/FocusRingConsumerReadiness.md)
(`FOCUS-CONSUMER`); acceptance evidence in
[handoff](../reports/work/FOCUS-CONSUMER/handoff.md). Does not close live qualification.

Additive lane revision 1, 2026-09-20: [canonical contracts](Plans/SimulatorDatasets.md).
Dispatch using that revision and the common execution contract. Catalog inclusion is
not installation/capture authority or evidence of data eligibility.

| Packet | Parent | Contract |
|---|---|---|
| SIM-DATA-01 | TASK-SIM-DATA-01 | [Independent local runtime](Plans/SimulatorDatasets.md#sim-data-01--independent-local-producer-runtime) |
| SIM-DATA-02 | TASK-SIM-DATA-01 | [Consumer and dataset contracts](Plans/SimulatorDatasets.md#sim-data-02--simulator-aware-consumer-and-dataset-contracts) |
| SIM-DATA-03 | TASK-SIM-DATA-01 | [Genuine simulator pilot](Plans/SimulatorDatasets.md#sim-data-03--bounded-genuine-simulator-qualification) |
| SIM-DATA-04 | TASK-SIM-DATA-01 | [FocusRing dataset freeze](Plans/SimulatorDatasets.md#sim-data-04--scale-and-freeze-focusring-simulator-data) |
| SIM-DATA-05 | TASK-SIM-DATA-01 | [Detector augmentation corpus](Plans/SimulatorDatasets.md#sim-data-05--tvos-detector-augmentation-corpus) |

## FocusRing simulator delivery — operation-specific authority

Revision 1: [canonical contracts](Plans/FocusRingSimulator.md). These follow the
simulator dataset packets; training and TTR operation retain separate authority.

| Packet | Parent | Contract |
|---|---|---|
| FR-SIM-BASE | FOCUS-DET-05 | [Shipped baseline and protocol](Plans/FocusRingSimulator.md#fr-sim-base--shipped-model-baseline-and-evaluation-protocol) |
| FR-SIM-CAND | FOCUS-DET-05 | [One experimental candidate](Plans/FocusRingSimulator.md#fr-sim-cand--one-trained-and-exported-experimental-candidate) |
| FR-SIM-TTR | FOCUS-DET-05 | [TTR comparison](Plans/FocusRingSimulator.md#fr-sim-ttr--ttr-focus-and-navigation-comparison) |

## Model and hardware work

| Packet | Parent | Contract |
|---|---|---|
| TRAIN-S | TASK-6a-10 | [Bounded smoke](Plans/ModelsAndHardware.md#train-s--bounded-full-frame-smoke-execution) |
| TRAIN-F | TASK-6a-10 | [Full training](Plans/ModelsAndHardware.md#train-f--41-class-full-frame-training) |
| TRAIN-Q | TASK-6a-10 | [Dual-holdout qualification](Plans/ModelsAndHardware.md#train-q--dual-holdout-qualification) |
| FR-A | FOCUS-DET-05 | [Offline readiness](Plans/ModelsAndHardware.md#fr-a--focusring-softwaredata-readiness) |
| FR-B | FOCUS-DET-05 | [Authorized harvest](Plans/ModelsAndHardware.md#fr-b--qualified-focusring-harvest) |
| FR-C | FOCUS-DET-05 | [Candidate/export qualification](Plans/ModelsAndHardware.md#fr-c--focusring-candidate-and-export-qualification) |
| R-A | TASK-6b-R-1 | [Holdout specification](Plans/ModelsAndHardware.md#r-a--real-tvos-holdout-capture-specification) |
| R-B | TASK-6b-R-1 | [Incremental captures](Plans/ModelsAndHardware.md#r-b--incremental-real-device-captures) |
| R-C | TASK-6b-R-1 | [Freeze/benchmark](Plans/ModelsAndHardware.md#r-c--freeze-and-benchmark-tvos-holdout) |
| MAC-A | TASK-6c-1 | [Coordinate spike](Plans/ModelsAndHardware.md#mac-a--macos-coordinate-spike) |
| MAC-B | TASK-6c-2 | [Generator/corpus](Plans/ModelsAndHardware.md#mac-b--macos-generator-and-corpus) |
| MAC-C | TASK-6c-2 | [Candidate/packaging evidence](Plans/ModelsAndHardware.md#mac-c--macos-candidate-and-packaging-evidence) |
| BADGE-A | TASK-BADGE-01 | [Taxonomy/decoder compatibility](Plans/ModelsAndHardware.md#badge-a--append-only-taxonomy-and-decoder-compatibility) |
| BADGE-B | TASK-BADGE-01 | [Badge corpus/candidate](Plans/ModelsAndHardware.md#badge-b--badge-corpus-and-candidate) |
| CROP-A | TASK-6a-12 | [Fork/evaluation definition](Plans/ModelsAndHardware.md#crop-a--crop-fork-and-frozen-evaluation-definition) |
| CROP-B | TASK-6a-12 | [Candidate qualification](Plans/ModelsAndHardware.md#crop-b--crop-candidate-qualification) |
| UNI-A | Phase 6b-U | [Experiment readiness](Plans/ModelsAndHardware.md#uni-a--unified-model-experiment-readiness) |
| UNI-B | Phase 6b-U | [Candidate comparison](Plans/ModelsAndHardware.md#uni-b--unified-candidate-and-comparison) |

## External consumers, maintenance and release

| Packet | Parent | Contract / owner |
|---|---|---|
| TV-I1 | TASK-INTEGRATION-01 | [Identity coordination](Plans/ConsumersAndRelease.md#tv-i1--authoritative-harvest-identity-coordination); TVTestRig |
| TV-I2 | TASK-INTEGRATION-01 | [Producer compatibility artifacts](Plans/ConsumersAndRelease.md#tv-i2--reproducible-producer-compatibility-artifacts); TVTestRig |
| SA-A | TASK-9-2 | [Contract/rules](Plans/ConsumersAndRelease.md#sa-a--screenauditkit-contracts-and-native-rules); ScreenAuditKit |
| SA-B | TASK-9-3 | [Dependency/CLI](Plans/ConsumersAndRelease.md#sa-b--dependency-bridge-and-native-cli-mode); ScreenAuditKit |
| DOC-A | TASK-DOC-01 | [Evidence-based maintenance](Plans/ConsumersAndRelease.md#doc-a--evidence-based-documentation-and-skill-maintenance); NUA |
| REL-A | TASK-DIST-02 | [Release evidence](Plans/ConsumersAndRelease.md#rel-a--qualified-model-release-evidence); NUA |
| REL-B | TASK-DIST-02 | [Promotion/tagging](Plans/ConsumersAndRelease.md#rel-b--maintainer-promotion-and-tagging); maintainer |
| HIST-A | TASK-DIST-01 | [History decision package](Plans/ConsumersAndRelease.md#hist-a--history-remediation-decision-package); architect/maintainer |

## Dispatch text

“Complete <packet-id or explicit tranche of packet IDs>, revision 6 catalog and the linked contract's revision/amendments, from Research/ImplementationPlans.md and its linked contracts. Follow AGENTS.md and Research/WorkerExecution/SKILL.md. Verify repository, ownership, prerequisites, and the integrated outcome. Implement all assigned behavior and caller integration, run focused/adversarial and required repository checks, fix in-scope failures, and return criterion-by-criterion four-outcome evidence. Do not stop at helper or packet checkpoints while authorized work remains; report progress in commentary and continue. Stop only when the assigned tranche is completed for review, concretely blocked after independent work is finished, or interrupted by the user/actual runtime limits. Preserve unrelated changes and safety gates; mark review, not accepted.”

For external packets, replace NUA operating paths with the owning repository's approved assignment and instructions. For hardware, training, recovery-copy or promotion packets, name the authorized operation and verified prerequisites explicitly; catalog inclusion alone is not authorization.
