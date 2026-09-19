# Full backlog implementation packet catalog

**Revision:** 4, 2026-09-19. This replaces combined P1–P5 contracts and revision-3 slice overrides. Each catalog row is one independently dispatchable assignment. Current state/owner lives only in [Tasks.md](../Tasks.md); [IterationRoadmap.md](IterationRoadmap.md) gives scheduling and [DeliveryDecisions.md](DeliveryDecisions.md) records accepted choices. Plans are not evidence that work ran.

## Common execution contract

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

“Implement <packet-id>, revision 4, from Research/ImplementationPlans.md and its linked contract. Follow AGENTS.md and Research/WorkerExecution/SKILL.md. Verify the assigned repository, ownership and this packet's prerequisites in Tasks.md. Perform only its authorized operations; preserve unrelated changes and historical evidence. Return the four-outcome handoff with acceptance evidence and the next unblocked action; mark review, not accepted.”

For external packets, replace NUA operating paths with the owning repository's approved assignment and instructions. For hardware, training, recovery-copy or promotion packets, name the authorized operation and verified prerequisites explicitly; catalog inclusion alone is not authorization.
