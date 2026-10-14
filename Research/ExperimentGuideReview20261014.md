# Recommendations for the proposed experiment execution guide

Date: 2026-10-14. Status: analysis for discussion, not an execution plan or approval.

This review covers the supplied guide for applying the technical audit and research recommendations through the existing queue.
It follows the recommendation format of the [research ideas review](ResearchIdeasReview20261014.md).

The guide has useful goals: complete experiment graphs, shared evaluation, clear decisions, and preserved failure evidence.
Its sample commands and specifications are not ready to execute. Several differ from the current implementation.
Standard UI detection, classification, and focus remain the main goals. HCF transfer remains a separate optional experiment.

## Priority overview

| Priority | Recommendation | Decision |
| --- | --- | --- |
| P0 | Match examples to the real queue interfaces | Adopt before converting this guide into executable work |
| P0 | Register comparisons and a decision with each training run | Adopt using existing dependencies and approvals |
| P0 | Batch compatible evaluations | Adopt after output-equivalence and restart tests |
| P1 | Measure proposal recall and selection separately | Adopt controlled diagnostic arms, not the combined proposed change |
| P1 | Test scale-aware score combination and preserved margins | Test separately after reviewing existing results |
| P1 | Review constrained fitting of the existing features | Reuse earlier findings before introducing new pooling |
| P2 | Test boundary-aware pooling | Treat as a representation change with its own matched control |
| P2 | Compress a candidate that fails its size gate | Test only against a current measured packaging problem |
| P2 | Distill optional HCF evidence into Standard training | Require verified pairs and an equal-budget Standard control |

## 1 Keep ownership separate from execution

**Idea:** use Tasks.md for ownership and the detached queue for execution.

**Fit:** this matches the existing workflow and prevents competing task boards.

**Recommendation:** adopt. Link each question to its job specifications and decision report.
Keep execution, evidence quality, and model acceptance separate in the dashboard.

**Correction:** do not assume the guide's task-state names define the current executable schema.
Use the states that the actual queue and local task records support.
The [graph ADR](ADR-0027-Evidence-Guided-Experiment-Graphs.md) describes the intended research structure.

## 2 Use the graph implementation that exists

**Idea:** connect questions, producers, qualification, experiments, decisions, and delivery through explicit dependencies.

**Fit:** this makes the reason for each experiment visible and limits blocking to affected work.

**Recommendation:** adopt the design, but use the current schema.
The current validator accepts 4 executable kinds: producer, qualification, experiment, and decision.
It stores the question on each node. It does not accept a separate EvaluationSuite kind.

**Correction:** the ADR's 6 conceptual types are not 6 implemented executable node types.
Current graph nodes reference submitted jobs and specification hashes.
The supplied JSON uses different field names and does not provide complete executable inputs.
Counts such as 1,820 views cannot replace a manifest, data roles, and hashes.

See [the current validator](../scripts/research_graph.py).
Do not add a new schema merely to make the attachment's examples valid.

## 3 Preserve failures without accepting avoidable inactivity

**Idea:** reject placeholder results, retain failed attempts, and create explicit successors after diagnosis.

**Fit:** this protects the evidence and prevents false progress from inflated job counts.

**Recommendation:** adopt. An empty ready queue is preferable to fabricated or useless experiments.
However, an empty queue still requires a preparation review when approved useful work remains blocked.
Name the missing input, responsible worker, and exact next action.

**Correction:** do not make every attempt path end in `attempts/1`.
Use the recorded attempt identity. Preserve every attempt and its actual state.
Do not use an invented status constant unless the implementation supports it.

## 4 Prepare the complete comparison before training

**Idea:** prepare training, evaluation, regression checks, and the final decision together.

**Fit:** this removes unnecessary waits for another chat turn after training finishes.

**Recommendation:** adopt using the existing registration and approval path.
Validate the complete graph before admitting its executable jobs.
Record partial registration explicitly if a preparation step fails.

**Correction:** the guide does not establish that current registration is transactional.
Do not describe several separate submissions as atomic without testing that behavior.
Each job still needs its own valid specification and applicable approval.

## 5 Replace the proposed command checklist

**Idea:** provide repeatable checks for readiness, registration, execution, and review.

**Fit:** useful, but incorrect commands can silently prevent work or encourage an unnecessary second runner.

The source inspection finds these differences:

| Proposed command | Current implementation | Recommendation |
| --- | --- | --- |
| `research_graph.py --validate` or `--register` | The module exposes validation functions, not these command-line actions | Use an existing campaign registration adapter |
| `research_approval.py --approve-spec` | The parser uses `approve`, `revoke`, and `list` | Use individual job identities and the existing approval contract |
| `research_queue.py --run-cycle` | The parser uses a `run` subcommand | Leave execution to the existing detached runner |
| `research_monitor.py --campaign ... --summary` | The parser exposes `status`, `resume`, and `report` | Use supported reporting interfaces |
| `research_readiness.py` without arguments | The parser requires job arguments | Check the named jobs |
| `research_trust.py --check` | The inspected module has no command-line entrypoint | Use its supported callers or focused tests |

**Recommendation:** P0 documentation correction before anyone uses the guide as an operating procedure.
Check parser definitions without running mutation commands.
Do not let an imported guide grant approval or start a runner.

## 6 Keep budgets and storage specific to each job

**Idea:** verify storage and route large artifacts to the approved USB volume.

**Fit:** this supports larger datasets without exhausting internal storage.

**Recommendation:** preserve the 800 s and 100 MB diagnostic defaults.
For training, read the approved specification and any recorded exception.
Reserve temporary space as well as final retained bytes.

**Correction:** do not turn the guide's 8 GiB memory value or training timeout into a universal requirement.
Do not treat a copied volume identifier as proof that the correct volume is mounted now.
The active checkout already resides on USB; describe compact versus bulk artifacts rather than assuming every repository file is internal.
Keep target identifiers and machine-specific paths in local configuration, not reusable public examples.

## 7 Test score combination and margin preservation separately

**Idea:** reduce whole-frame influence for small changes and penalize decisions that approach the abstention region.

**Fit:** this targets the measured tension between small movements and content-only false alarms.

**Recommendation:** use [STANDARD390](Plans/Standard390.md) and earlier score analyses to select the failure first.
Compare the unchanged model, a size-aware combination, and a margin correction separately.
Test a combined correction only when those results justify it.

**Corrections:** the proposed sigmoid does not automatically produce a gate of 0.05 below the stated area threshold.
Its learned parameters determine that behavior. Small changed areas can also contain notifications or artwork changes.
A detail branch trained as an additive correction is not automatically a standalone focus score.
Replacing addition with a weighted average changes the meaning of both branches.

A squared hinge penalty is a soft penalty, not a hard guarantee.
Update projection provides only a local first-order condition; finite updates can still increase the preservation loss.
Use eligible training examples for preservation. Do not convert evaluation cases into constraints without changing their recorded role.
Preserve original crops, input views, initialization, and comparison thresholds.

**Decision:** prefer the simplest correction that improves the target failure without losing required previous successes.

## 8 Separate constrained fitting from boundary pooling

**Idea:** fit a linear head with explicit margins, using boundary-minus-interior features.

**Fit:** constrained fitting tests the fitting method. Boundary pooling tests the representation.
Combining them immediately prevents a clear explanation of any gain or loss.

**Recommendation:** first review earlier constrained fits using their unchanged feature vectors.
Then compare boundary pooling against those same controls if the evidence points to missing boundary information.
Audit the roles of the proposed 18 preservation crops before using them for training constraints.

**Corrections:** constrained logistic regression is not generally a quadratic program.
Generic L-BFGS does not enforce arbitrary linear margin constraints by itself.
Solver tolerance and exported decisions require independent checks.
An 8 × 8 outer feature band does not necessarily follow the control boundary after resizing and padding.

**Decision:** report whether the bottleneck is fitting, representation, or unavailable visual evidence.
Do not label this a zero-regression solution before measuring the complete comparison.

## 9 Qualify compression against the current release candidate

**Idea:** use 6-bit weight palettization to meet a package-size limit.

**Fit:** useful if the actual candidate still exceeds its applicable byte limit.

**Recommendation:** measure the current package first. Preserve the original and compare compression against it.
Check deployment support, package size, latency, numeric outputs, and decisions through the real Vision path.

**Correction:** the supplied global configuration does not explicitly exempt the first and final layers.
A size threshold does not reliably identify those layers.
Explicit operation overrides need inspection when preserving those layers matters.
Keeping some layers in FP16 cannot guarantee zero boundary drift.
Passing an unrelated Swift test filter does not establish parity for the newly compressed package.

The [earlier research review](ResearchIdeasReview20261014.md#10-palettize-model-weights) records the method's limits and Apple references.

## 10 Prioritize deployable proposal coverage

**Idea:** lower the detector threshold, add rectangle proposals, and compare candidate scores within a row or shelf.

**Fit:** this addresses a strong retained limitation: the detector localizes only 21 of 46 focused targets.
The [retained scorecard](Plans/RealModelScorecard36.md) reports 346 of 583 localized bodies and 4 correct selections across 7 complete frames.
These are retained measurements, not results of the proposed correction.

**Recommendation:** use separate controlled arms:

- Lower the detector threshold only.
- Add rectangle proposals with fixed duplicate handling.
- Change selection among the same fixed proposals.
- Combine only the changes that show useful effects.

Measure target recall, proposal count, incorrect selections, abstentions, and total cost.
Use fully labeled frames for complete selection claims. Treat partial annotations as partial evidence.

**Corrections:** the proposed highest-score test is not a z-score normalization.
Choosing one winner per container can still produce multiple winners across the screen.
IoU suppression can remove distinct nested controls.
The proposed 38-of-46 target is an aspiration, not an established feasible outcome.
Do not repeatedly tune these settings on a set described as frozen final evaluation.

## 11 Keep HCF distillation optional and controlled

**Idea:** use paired OS HCF images as teacher information while the student sees only Standard pixels.

**Fit:** potentially useful training assistance without requiring HCF during ordinary NUIAK use.

**Recommendation:** retain this as a separate P2 transfer experiment.
Compare Standard-only training against the same Standard examples plus qualified teacher information.
Keep initialization, labels, compute, and evaluation membership matched.
Require no loss of Standard successes before considering the result useful.

**Corrections:** teacher scores are predictions, not ground truth.
Matching a recipe seed and requested focus identity does not prove matching observed state.
Concentrated pixel differences do not independently prove correct labels or complete capture equivalence.
Check observed focus, geometry, timing, restoration, and repeated captures.
Measure family-specific behavior instead of adopting 98.5% concentration or zero noise as universal constants.

Do not reuse a copied Simulator identifier or historical TTR revision as current target qualification.
Use the approved capture producer and its recorded environment.

## 12 Batch evaluation without hiding missing evidence

**Idea:** replace repeated model loading across many small jobs with one bounded evaluation worker.

**Fit:** one of the strongest workflow improvements in this guide.

**Recommendation:** group compatible comparisons while preserving separate slice outputs and raw counts.
Cache only by complete identities for inputs, models, preprocessing, and settings.
Record incremental progress and restart checkpoints for the suite.
Require every declared slice or an explicit unsupported outcome before the final decision.

**Corrections:** matrix multiplication can batch compatible linear heads over fixed shared features.
It cannot replace arbitrary encoders or nonlinear model stacks.
A missing required slice cannot become a passing aggregate score.
Use a supported experiment job for the suite; do not invent an EvaluationSuite node kind.
Keep output and time budgets explicit when combining previously separate jobs.

**Decision:** adopt when outputs match separate execution and measured loading costs decrease.

## 13 Use appropriate verification rather than rigid timing claims

**Idea:** run focused tests, integrated Swift checks, and a final repository review.

**Fit:** necessary for code integration, with scope matched to the actual change.

**Recommendation:** preserve focused tests and required offline Swift checks for integrated code.
Use the approved project build location. The supplied `/tmp` command conflicts with the repository's output rule.
Do not impose an unsupported 5 s maximum on test correctness.
Do not interrupt running experiments to obtain a clean working tree.
Preserve unrelated changes and review the intended diff for private information and generated artifacts.

Documentation-only reviews need content, links, and diff checks; they do not require a new Swift build.

## Recommended next sequence

1. Use the existing Standard reports to identify the strongest remaining failure and eligible inputs.
2. Correct the operating examples and choose unused identifiers before creating any specifications.
3. Improve compatible evaluation reuse without changing measured results.
4. Compare proposal coverage and selection as separate causes of failure.
5. Select one justified score-combination or constrained-head test with complete regression consumers.
6. Keep boundary pooling, compression, and HCF transfer conditional on their measured need.

The proposed numeric suffixes overlap existing HCF388, HCF389, and STANDARD390 work.
Do not replace those jobs or reuse their identities for unrelated experiments.

This review adds no jobs, approvals, captures, or training runs. The background queue remains unchanged.
