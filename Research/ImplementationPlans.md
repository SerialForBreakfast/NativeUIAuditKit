# Full backlog implementation packet catalog

**Revision:** 4, 2026-09-19. This replaces combined P1–P5 contracts and revision-3 slice overrides. Each catalog row is one independently dispatchable assignment. Current state/owner lives only in [Tasks.md](../Tasks.md); [IterationRoadmap.md](IterationRoadmap.md) gives scheduling and [DeliveryDecisions.md](DeliveryDecisions.md) records accepted choices. Plans are not evidence that work ran.

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

## Current Office model-delivery amendment

[OfficeFocusRing.md](Plans/OfficeFocusRing.md), revision 1, refines existing P4-L/FR-B/FR-C
without duplicate packet IDs: one authorized smoke request, intake, separately authorized
physical visual pilot/baseline/corpus, candidate and TTR comparison. Simulator execution
is paused by the user; its packet evidence and offline review remain preserved.

## Common execution contract

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

## FocusRing simulator delivery — execution remains paused

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

“Complete <packet-id or explicit tranche of packet IDs>, revision 4 plus the execution amendment, from Research/ImplementationPlans.md and its linked contracts. Follow AGENTS.md and Research/WorkerExecution/SKILL.md. Verify repository, ownership, prerequisites, and the integrated outcome. Implement all assigned behavior and caller integration, run focused/adversarial and required repository checks, fix in-scope failures, and return criterion-by-criterion four-outcome evidence. Do not stop at helper or packet checkpoints while authorized work remains; report progress in commentary and continue. Stop only when the assigned tranche is completed for review, concretely blocked after independent work is finished, or interrupted by the user/actual runtime limits. Preserve unrelated changes and safety gates; mark review, not accepted.”

For external packets, replace NUA operating paths with the owning repository's approved assignment and instructions. For hardware, training, recovery-copy or promotion packets, name the authorized operation and verified prerequisites explicitly; catalog inclusion alone is not authorization.
