# ML researcher best practices: an experiment platform curriculum

Date: 2026-10-18. Owner: Maximum-mini-NUIAK.
Status: research guidance and proposed exercises, not execution approval.

## 1. Recommendation

Build a reliable research process first. Use a graph where dependencies and alternative decisions make it useful.
Keep simple investigations as simple jobs. Do not require a large graph for every question.

For NUIAK, keep the current queue and reusable adapters.
Use short descriptions to select tested operations, frozen inputs, comparison rules, and bounded follow-ups.
Keep Standard UI detection and focus primary. Treat HCF as an optional condition and experimental aid.
Keep the dashboard an internal research tool, not a public product commitment.

There is no single method used by all leading ML researchers.
This curriculum combines published research, official tool documentation, and our retained workflow evidence.
The recommendations below are engineering judgments for NUIAK, not a claim of universal best practice.
This review is representative, not exhaustive.

Google's engineering guidance emphasizes simple baselines, reliable pipelines, and tests independent of learning behavior.
These principles support improving our complete consumer path before adding more model complexity.
See [Rules of Machine Learning](https://developers.google.com/machine-learning/guides/rules-of-ml).

## 2. What effective research teams optimize

The useful output is a decision supported by evidence. A trained checkpoint alone is not that output.

1. Start with the consumer failure and the decision that could change it.
2. Establish a reproducible baseline through the actual consumer path.
3. Test competing explanations with inexpensive diagnostics.
4. Train only when a result supports a training intervention.
5. Compare gains, regressions, coverage, uncertainty, and cost.
6. Retain negative findings so later work does not repeat rejected ideas without new evidence.

Separate exploration from confirmation.
Exploration can use small samples and flexible analysis. Label its conclusions as provisional.
Confirmation freezes the candidate, preprocessing, thresholds, membership, and decision rules before evaluation.

Reproducibility guidance supports recording enough detail for another researcher to reconstruct a result.
It does not require a large platform for every experiment.
See [the NeurIPS reproducibility program report](https://jmlr.org/papers/v22/20-303.html).

## 3. Three layers, not one large scheduler

| Layer | Question it answers | NUIAK responsibility |
| --- | --- | --- |
| Research plan | What uncertainty matters, and what result changes our next action? | Researcher and maintainer |
| Execution graph | Which verified outputs and conditions does each job require? | Template compiler and existing queue |
| Evidence record | What actually ran, what changed, and what remains unknown? | Immutable attempts and comparison reports |

A graph does not establish causality. Its edges describe dependencies or approved decisions.
Research feedback creates a new graph revision. Do not turn one revision into an unlimited loop.
Use a state machine for side-effect operations such as capture, ownership, cleanup, and restoration.
Use a dependency graph for artifact processing. These approaches can coexist.

```text
Question + fixed comparison
          |
     Readiness checks
          |
 Qualified data -> Prepare once -> Candidate runs
          |                           |
          +---- retained baseline ----+
                                      |
                                Matched scoring
                                      |
                            Evidence and regression checks
                                      |
                       Supported / Contradicted / Inconclusive
                                      |
                         Approved bounded follow-up or stop
```

An execution failure is a separate outcome. It does not contradict the scientific hypothesis.
Model promotion and navigation authority remain separate decisions.

## 4. Curriculum

Work through these modules with retained data first.
An exercise is complete when its acceptance check passes, not when its script exists.
The exercises below are proposed work. This document does not add or approve queue jobs.

### Module 1 — Define the question and the cheapest useful test

**Learn:** distinguish a symptom, an explanation, and an intervention.

**Exercise:** investigate a missed focused control with 3 explanations:

- The proposal source does not find the control.
- The crop preprocessing removes the useful focus signal.
- The scorer ranks a competing control above the target.

Compare known boxes, fixed deployable proposals, and the same proposals with the candidate scorer.
Reuse predictions where their identities match.

**Acceptance:** each result selects a different next action.
Do not train the classifier when missing proposals explain the failure.
Do not call known-box performance deployable full-screen accuracy.

### Module 2 — Define trustworthy data units

**Learn:** frames, crops, capture events, and independent groups are different units.

**Exercise:** make a manifest with capture identity, source hashes, labels, profile, family, group, and role.
Keep related scenes, artwork derivatives, profile counterparts, and reversed transitions in the same group.
Preserve separate capture events even when their image bytes match.
Store identical payloads once when the storage contract supports this.

**Acceptance:** reject conflicting labels, changed bytes, role leakage, and unknown focus labels.
Keep no-focus truth separate from detector abstention and unknown scene state.

Fit learned preprocessing only on eligible training data.
Apply frozen preprocessing to later partitions.
See [scikit-learn's leakage guidance](https://scikit-learn.org/stable/common_pitfalls.html).

### Module 3 — Design comparisons that answer one question

**Learn:** hold nuisance factors constant when testing a specific intervention.

**Exercise:** compare original crops with measured-offset training crops.
Keep initialization, groups, scoring membership, thresholds, and the declared training budget fixed.
Report update counts as well as epochs when sampling changes.

**Acceptance:** describe what the comparison isolates and what remains confounded.
Equal epochs, equal examples, and equal compute answer different questions.

Use a small factorial design when interactions matter.
For example, compare balance on/off and duplicate removal on/off in 4 arms.
This can separate individual effects from their interaction better than unrelated sequential changes.
Do not add all combinations without a question and an approved budget.

### Module 4 — Measure uncertainty and preserve successes

**Learn:** a single seed or large frame count can overstate confidence.

**Exercise:** report paired case outcomes, group counts, family support, gains, losses, and new wrong selections.
Repeat promising candidates with additional approved seeds.
Use paired resampling of independent groups when a confidence interval is useful.
Report unstable or sparse slices explicitly.

**Acceptance:** the report distinguishes seed variation, group variation, and repeated observations.
It does not treat repeated frames as independent trials.

Benchmark research finds important variation from sampling, initialization, and hyperparameter choices.
This supports broader confirmation than repeating one favorable seed.
See [Accounting for Variance in Machine Learning Benchmarks](https://arxiv.org/abs/2103.03098).

Zero lost successes is our retained-suite gate. It is not proof of zero future regressions.
Zero observed no-focus mistakes also does not prove a zero population error rate.
Repeated inspection turns a benchmark into development evidence. Keep a separate, untouched final audit.
If many candidates use the same development set, confirm the selected candidate independently.

### Module 5 — Build adapters, not experiment-specific programs

**Learn:** separate scientific operations from experiment descriptions.

**Exercise:** express 2 useful comparisons through the same preparation, training, scoring, and reporting adapters.
Change only declared inputs or parameters in the second description.

**Acceptance:** the second experiment needs no new adapter script.
Unsupported parameters fail before dispatch. Missing inputs identify their owner and required producer.

Use this authoring contract:

| Field | Required meaning |
| --- | --- |
| Question | The uncertainty and observed failure |
| Control | The exact baseline and eligible membership |
| Change | The intervention or comparison factor |
| Inputs | Versioned artifacts, roles, and dependencies |
| Resources | Worker capabilities, time, storage, and total campaign budget |
| Measurements | Raw counts, case outcomes, timing, and support |
| Decision | Supported, contradicted, inconclusive, and stop rules |
| Authority | Approved action and exact job identities |

Resolve machine paths and hashes through tooling. Do not require agents to rewrite them manually for routine requests.
The resulting execution specifications remain immutable.

### Module 6 — Separate software tests from model evidence

**Learn:** a passing toy example qualifies software behavior, not model quality.

**Exercise:** test each adapter at 4 levels:

1. Validate the description and reject invalid fields.
2. Run a minimal positive case and a predictable negative case.
3. Exercise the real queue boundary, including restart and duplicate requests.
4. Run a bounded retained-data comparison through the actual implementation.

**Acceptance:** each report names which level passed.
Stubbed trainers do not establish training convergence or checkpoint correctness.
Simulated receipts do not qualify native capture or TTR integration.

### Module 7 — Make recovery and caching safe

**Learn:** job restart, step reuse, and training resume are different operations.

**Exercise:** interrupt after preparation, then during training, in isolated tests.
Verify that completed preparation is reused and that training resumes only from a qualified checkpoint contract.

**Acceptance:** resume checks model, optimizer, scheduler, random state, data order, and any mixed-precision scaler state.
Record the intended numerical tolerance. Test against uninterrupted execution.
Do not claim cross-platform bitwise equality without evidence.

Cache keys include relevant code, environment, preprocessing, inputs, model, parameters, and data roles.
Verify output hashes before reuse. A path or process exit code is insufficient.
Publish outputs atomically. Preserve incomplete attempts and explicit successors.
Do not promise exactly-once external effects merely because job IDs are unique.

### Module 8 — Automate bounded decisions

**Learn:** automate fixed decisions before attempting autonomous research design.

**Exercise:** define these branches before execution:

| Observation | Permitted next step | Stop condition |
| --- | --- | --- |
| Missing proposals explain errors | Run a fixed alternative proposal comparison | No qualified alternative exists |
| Candidate loses retained successes | Run case-linked regression analysis | Analysis completes |
| Gain is uncertain | Run an approved seed or independent comparison | Campaign budget or evidence target is reached |
| Training still improves at its limit | Review a qualified checkpoint continuation | Resume contract fails or budget is exhausted |
| Capture restoration fails | Preserve the guard and record an exact repair task | No approved recovery path exists |

**Acceptance:** only the selected approved branch runs.
Inconclusive evidence never becomes acceptance. A failed branch does not stop independent work.
Our current campaign compiler supports only its documented branch outcomes.
Additional examples here need implementation and approval before execution.

### Module 9 — Batch work without contaminating comparisons

**Learn:** share expensive preparation, not mutable scientific state.

**Exercise:** compare separate preparation with shared verified preparation using the same scoring inputs.
Measure setup, decode, inference, report time, peak storage, and output equality.
Measure first-read and repeated-read behavior separately.

**Acceptance:** outputs meet the declared parity rule and end-to-end time improves.
Randomize or alternate arm order when cache warmth could bias timings.
Reset seeds, model state, and mutable caches when reusing a worker.
Keep Simulator ownership and cleanup boundaries intact.

Use verified USB storage for bulk artifacts.
Preserve originals, labels, valuable checkpoints, and compact receipts.
Regenerable caches need a regeneration recipe, not an elaborate backup program.
Account for temporary space and pause producers before storage exhaustion.

### Module 10 — Close the consumer loop

**Learn:** offline model quality and consumer compatibility are separate gates.

**Exercise:** freeze a useful candidate, then compare PyTorch and Core ML on identical eligible inputs.
Test the actual Vision preprocessing and TTR box source.
Include no-focus scenes, overlapping controls, clipping, and decorative borders.

**Acceptance:** report output parity, selection changes, latency distribution, model size, and previous successes lost.
Use observation-only integration before navigation authority.
Keep Standard behavior unchanged when an optional HCF path fails or is unavailable.

## 5. Alternative approaches

These approaches solve different problems. They are not mutually exclusive.

| Approach | Best use | Main limitation | Recommendation |
| --- | --- | --- | --- |
| Script or notebook plus a fixed manifest | Explore an unfamiliar failure cheaply | Hidden state and manual repetition | Use for exploration; move repeated operations into tested adapters |
| Linear pipeline | One stable prepare/train/evaluate sequence | Awkward shared branches | Prefer it when there are no meaningful branches |
| Dependency graph | Shared producers, parallel comparisons, conditional follow-ups | More contracts and failure states | Use for our repeated campaigns |
| State machine | Capture, recovery, ownership, and cleanup | Poor fit for large artifact transformations | Use inside side-effect adapters |
| Hyperparameter search | Optimize a known objective within a fixed search space | Can optimize the wrong benchmark efficiently | Use only after metric and data qualification |
| Active data selection | Choose the next useful labels or Fixture cases | Can overfit known failure slices | Compare against balanced and random selection at equal budgets |
| Human-reviewed research loop | New hypotheses, ambiguous labels, consumer decisions | Manual latency | Keep it for decisions that lack safe predefined rules |

Hyperband allocates limited resources across candidate configurations and stops less promising trials early.
It addresses search efficiency, not label validity or product acceptance.
Ray Tune exposes several trial scheduling methods, including ASHA and Hyperband.
These are possible inner search tools, not replacements for our approval and regression checks.
See [Hyperband](https://jmlr.org/papers/v18/16-558.html) and [Ray Tune schedulers](https://docs.ray.io/en/latest/tune/api/schedulers.html).

Do not use aggressive early stopping until early measurements predict final rankings adequately for our task.
Do not call a stopped trial a completed fixed-epoch comparison.
An adaptive search can select candidates. A separate matched comparison must establish the claimed improvement.

## 6. Existing tools: what to borrow or adopt

| Tool | Documented contribution | Work it does not remove |
| --- | --- | --- |
| DVC | File dependencies, reproducible stages, and cached outputs | TTR ownership, labels, approvals, and acceptance rules |
| Snakemake | Input/output rules, resources, and dependency reevaluation through checkpoints | Native Apple adapters and scientific evidence checks |
| Metaflow | Python workflow abstractions | Qualification of our native tools, storage, and consumer behavior |
| MLflow Tracking | Parameters, metrics, artifacts, and run comparison | Execution ownership and trustworthy model decisions |

Sources: [DVC pipelines](https://doc.dvc.org/user-guide/pipelines/defining-pipelines),
[Snakemake rules](https://snakemake.readthedocs.io/en/stable/snakefiles/rules.html),
[Metaflow introduction](https://docs.metaflow.org/introduction/what-is-metaflow),
and [MLflow Tracking](https://mlflow.org/docs/latest/tracking/).

Our [DVC pilot](Workflow394Results.md) produces matching reports across both approaches.
Its timing boundaries differ. It does not establish a throughput or maintenance winner.
Keep [ADR-0029](ADR-0029-Workflow-Tools-Versus-Templates.md) as the framework review decision.
Do not treat its historical template inventory as the current implementation status.

Reconsider adoption when a measured maintenance problem maps directly to an existing tool.
Compare the same workflow, including authoring time, recovery, invalid inputs, storage, and operator effort.
Require separate installation approval. Do not migrate active jobs for a speculative benefit.
Defer Kubernetes-based orchestration unless a demonstrated scale requirement justifies its operation.

## 7. Recommended NUIAK sequence

1. Use WORKFLOW439 for the next complete Standard proposal comparison.
2. Produce the result and bounded follow-up from the same request.
3. Prove a second useful campaign needs no new adapter.
4. Measure authoring time and manual interventions across both campaigns.
5. Fix the largest measured preparation bottleneck.
6. Expand the independent reserve only with experiments that answer distinct questions.

Current [WORKFLOW439](Plans/WorkflowCampaign439.md) supports bounded branches and frozen preparation membership.
Its real audit jobs reuse retained evidence. They do not establish new training quality or overnight capacity.
[ADR-0027](ADR-0027-Evidence-Guided-Experiment-Graphs.md) defines the research graph model.
The next priority is using these mechanisms for consumer improvements, not building another general framework.

Maintain priority work, independent reserve work, and conditional follow-ups separately.
Report measured ready duration, not the sum of optimistic branch budgets.
An empty queue caused by unfinished preparation deserves repair.
An empty queue after valid stopping decisions does not justify filler work.

## 8. Graduation check

The platform meets this curriculum when an agent can submit a short supported description and obtain a complete, inspectable decision.

- A second description reuses the same adapters.
- Missing prerequisites produce exact blockers and owners.
- Restart and duplicate requests preserve completed attempts.
- Changed inputs invalidate the affected reuse.
- Reports include gains, losses, no-focus outcomes, support, and evidence limits.
- Bounded branches run without manual dispatch and stop at their declared limits.
- Consumer verification remains separate from scientific screening.
- Standard remains protected and HCF remains optional.

Track time from question to decision, manual interventions, avoidable idle time, and useful decisions per compute hour.
Do not prioritize token accounting unless it is inexpensive to collect.
Do not use completed-job count or hardware utilization as the main measure of research progress.

The objective is a small, reliable system that makes useful experiments easy to define and difficult to misinterpret.
