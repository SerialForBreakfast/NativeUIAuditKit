# ADR 0027 Evidence guided experiment graphs

> Historical research record. Results retain their stated scope and limits.
> Host names are public aliases. Local evidence and execution records remain private.
> This publication does not revalidate earlier results or approve a model.

Status: accepted for the bounded FOCUS364–365 implementation, 2026-10-13. This ADR does not expand execution authority.
Owner: research-host-NUIAK.
Relates to [ADR-0026](ADR-0026-Queued-Research-Experiments.md) and [FOCUS363](Plans/FocusLearning363.md).

Implementation: [FOCUS364–365](Plans/FocusGraphs364.md) adds typed conditions to the existing queue.
It preserves immutable graph revisions and reuses completed producers.
Negative scientific outcomes block dependent work without failing independent branches.

## Context

Our repeated sequence is diagnose, change, train, evaluate, and choose another change.
That sequence is useful inside an experiment. It is insufficient for managing a research program.
It encourages one correction at a time, repeated setup, and manual decisions between dependent jobs.
It can also repeat rejected explanations without stating what new evidence makes another test useful.

The existing queue already supports producer dependencies, output hashes, and cycle checks.
It does not need replacement. A dependency proves that an input exists, not that a scientific condition passes.
We need an explicit connection between questions, measurements, decisions, and the experiments those decisions justify.

FOCUS355 already tests trainable whole-frame features. A new branch experiment must explain what changes beyond that completed test.
HCF362 shows why execution failure differs from a scientific result: an observation mismatch blocks capture before any training evidence exists.
The [FOCUS363 plan](Plans/FocusLearning363.md) supplies the first bounded program for this change.

## Decision

Organize each model-improvement campaign as a versioned graph of questions, evidence, jobs, and decisions.
Use the existing queue to execute jobs. Use the graph to explain why each job exists and what follows its result.
Keep `Tasks.md` as the only ownership and status queue.
Keep model training loops inside jobs. Graph engineering changes how experiments connect, not how gradients update weights.
This decision concerns research workflow graphs, not graph neural networks or a new agent platform.

Each campaign revision is a directed acyclic graph. Dependencies cannot point back to an earlier node in the same revision.
New findings can produce a successor revision that references prior evidence without changing it.
Feedback therefore creates new versions, not an endless execution cycle.

## What changes

| Sequential habit | Graph practice | Expected benefit |
| --- | --- | --- |
| Choose another adjustment after each failure | State competing explanations and their distinguishing tests first | Fewer repeated corrections without new evidence |
| Prepare each experiment separately | Share qualified producers, manifests, and cached outputs | Less repeated capture and preprocessing |
| Wait for chat after training | Register validation and comparison consumers with training | Shorter time to a complete decision |
| Treat every completed job as progress | Separate execution, evidence quality, and scientific outcome | Honest progress reporting |
| Block the whole campaign on one producer | Block only dependent branches | Independent work continues |
| Keep a queue full by task count | Prioritize questions that can change the next decision | More useful results per compute hour |

These are expected benefits. Measure them before claiming an efficiency improvement.

## Node and edge contracts

| Node type | Purpose | Required result |
| --- | --- | --- |
| Question | State an uncertainty and competing explanations | A named decision and its useful outcomes |
| Producer | Make captures, crops, features, or predictions | Verified outputs, data roles, and cleanup evidence |
| Qualification | Check whether evidence supports its intended use | Eligible, ineligible, or unknown, with exact reasons |
| Experiment | Run a fixed controlled comparison | Raw results, uncertainty, cost, and case-level changes |
| Decision | Apply a rule fixed before execution | Supported, contradicted, or inconclusive, with selected next work |
| Delivery | Qualify a candidate for its intended consumer | Existing model gates and consumer checks |

A question can map to several jobs. A completed job does not necessarily answer a question.
No-op bookkeeping does not count as an experiment.

Use 3 edge types:

- Data: the consumer needs named verified producer outputs.
- Condition: the consumer needs a stated qualification or decision outcome.
- Evidence: the node cites a prior result without requiring that work to run again.

Condition edges do not grant capture, training, downloads, export, or promotion authority.
Resource availability remains a scheduler check. Do not represent a busy GPU as failed scientific evidence.

Every executable node records its question, matched control, inputs, hashes, roles, owner, allowed action, limits, outputs, and acceptance rule.
Every decision records the evidence hashes and graph revision used to reach it.
Define required inputs with AND semantics. Declare alternatives explicitly; do not silently substitute another producer or dataset.
When multiple branches qualify, use the declared priority and remaining aggregate budget.
When no branch qualifies, record the missing evidence or close the question as inconclusive.

## First campaign

The FOCUS363 packages provide the graph without creating another HCF study.

```text
Retained evidence audit B ───────────────┐
                                       v
Native producer repair A → Cue checks → Qualified benchmark B
                                              |
                         ┌────────────────────┼──────────────────┐
                         v                    v                  v
                 HCF comparison C    Transition test D    Feature test E
                         |                    |                  |
                         └─────────── Matched reports ───────────┘
                                              |
                                     Recorded decision
                           ┌──────────────────┼──────────────────┐
                           v                  v                  v
                    More evidence      Useful candidate     Stop this idea
                           |                  |
                  Successor revision    Retention and audit
                                              |
                                     Core ML and TTR shadow
```

This diagram shows logical dependencies, not simultaneous execution approval.
HCF selection and transition detection keep separate metrics and eligible membership.
Package F follows only when reliable groups and a useful baseline justify group-aware training.
Package E also needs model, license, download authority where required, and memory qualification.

## Example decision branches

| Observation | Next justified work | Work not justified |
| --- | --- | --- |
| OS HCF state is unknown | Repair or qualify capture observations | Train on guessed HCF labels |
| Native HCF is verified but the control effect does not change | Check the native control family and repeated captures | Manufacture a border and call it native HCF |
| Known-box crops work but proposals miss the focused control | Improve proposals or compare full-screen detection | Reject HCF learning as impossible |
| Training examples fit but new families fail | Diagnose coverage and domain differences | Extend epochs without a learning-curve reason |
| Current features fail but frozen pretrained features separate cases | Consider a bounded representation correction | Immediately replace the deployed model |
| A correction reduces false changes but loses movement | Diagnose the tradeoff and training exposure | Accept a favorable aggregate score |
| A candidate improves development and preserves prior successes | Freeze candidate and thresholds for final audit | Tune repeatedly against the audit |
| A run times out or capture fails | Diagnose execution; consider an authorized new attempt | Mark the scientific hypothesis false |

These rules select investigations, not automatic architecture searches.
Freeze numerical thresholds and minimum support in the specific campaign before measuring candidate outcomes.

## Evidence reuse and invalidation

Reuse a completed result only when its task, input identities, preprocessing, settings, and intended data role remain compatible.
Cache keys include all relevant dependencies, not only filenames or model names.
Reversed pairs, artwork derivatives, repeated captures, and shared templates remain connected for split checks.
Do not treat shared controls as independent evidence in each branch.

If an input changes, mark only its affected descendants as requiring new qualification.
Preserve original results. Do not overwrite them or automatically rerun all descendants.
Create new immutable jobs for necessary recomputation under existing authority and budgets.
A revised label creates a new evidence version. Keep original model evaluations available for comparison.

Use development data for adaptive branch selection.
Freeze models, thresholds, and audit membership before final evaluation.
Repeatedly inspecting a final audit converts its practical use into development; it cannot remain an untouched confirmation set.
Report all predefined comparisons, including unfavorable outcomes. Do not select only the best branch after inspection.

## Minimal implementation

First represent the approved campaign in compact metadata that references existing job IDs and specification hashes.
Do not copy mutable task status into that metadata. Read execution state from queue receipts and ownership from `Tasks.md`.
Use a versioned decision artifact for scientific outcomes and their supporting evidence.

Extend existing readiness and report code in this order:

1. Validate graph references, unique IDs, cycles, budgets, and required decisions.
2. Render the question, current work, missing inputs, and next possible outcomes in the dashboard.
3. Produce decision reports from completed comparisons with verified evidence hashes.
4. Require a valid qualification result before dispatching its conditional consumer.
5. Add approved successors through the existing live-addition path without restarting the runner.

The current queue verifies successful producer outputs. Scientific outcome gating is proposed work, not an existing verified capability.
Before that capability passes tests, register conditional consumers only after their decision is reviewed.
Do not use failed process exits to encode a valid negative scientific result.
Do not implement conditions with arbitrary Python expressions, shell commands, or received chat instructions.
Use a small typed rule set and reject unknown versions or fields.

## Limits and coordination

Keep existing per-job and aggregate study budgets. A branch does not receive a fresh budget merely because it has a new ID.
Reserve compute, storage, and temporary transfer capacity before dispatch.
Bound branch count and campaign scope before execution. Do not expand automatically to keep hardware busy.
An unavailable input blocks only its dependents, not unrelated approved jobs.

research-host-NUIAK owns experiment design, admission, and model decisions.
worker-host-NUIAK receives complete bounded assignments for training or scoring.
TTR owners supply native producer behavior and target restoration.
Qualified LittleDog preparation can check inputs and assemble reports without changing labels or decisions.
worker-host-Coordinator records delivery, ownership, and dependencies. It does not infer execution approval from an edge or message.

Publish only cross-project dependencies and actionable results.
Require forwarded IDs and recipient acceptance before reporting a worker assignment as delivered and accepted.
Peer advice creates proposals, not executable branches.

## Validation and pilot acceptance

Test missing inputs, altered hashes, cycles, unsupported rule versions, false conditions, and unknown scientific outcomes.
Test valid negative results, interrupted producers, retries, duplicate dispatch, budget exhaustion, and stale decision artifacts.
Test shared-control reuse and exclusion of related groups from separate data roles.
Test that one blocked capture branch leaves an independent cached-data branch executable.
Test that a passing decision cannot bypass action permissions or final model gates.

The pilot uses FOCUS363 and the existing queue.
It must demonstrate one reused artifact, one independently completed branch, and one evidence-supported decision about subsequent work.
It must also show that an unsupported branch remains blocked without stopping unrelated work.
Completion does not require a model improvement. It requires an honest, reproducible decision and no duplicate execution.

Measure the next 3 campaigns against comparable retained campaigns:

- Time from approved question to usable decision.
- Manual interventions between producer, training, and comparison stages.
- Repeated capture, preprocessing, and transfer work.
- Compute hours per question answered.
- Idle time caused by missing prerequisites.
- Target improvements and previous successes lost.

Report model quality separately from workflow efficiency. Do not claim faster research solely from more completed jobs.

## Alternatives and consequences

Keep sequential chat-driven loops: simplest locally, but dependent work continues to need manual coordination.
Build a new orchestration platform: unnecessary duplication of the queue, authority checks, and recovery state.
Use unrestricted automatic search: risks expensive repetition, evaluation leakage, and selection of weak evidence.
Use a graph database immediately: unnecessary for one bounded campaign and compact metadata.

The selected approach adds explicit decision contracts to existing infrastructure.
It improves traceability and supports useful parallel work, but requires disciplined rules and versioned evidence.
Keep the first graph small. Add complexity only when a measured coordination or decision failure requires it.

## Rollout boundary

This ADR records a proposed design. No runner, dashboard, experiment, or model changes occur with this document.
FOCUS363 remains the program plan. Record implementation approval and open work in `Tasks.md` before changing runtime behavior.
