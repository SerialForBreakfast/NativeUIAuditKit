# Architect and worker operating contract

**Established:** 2026-09-19. Applies to planned implementation and its review. AGENTS.md remains the repository authority.

## Ownership and sources of truth

- **Architect/project manager:** orders the work, writes executable packets, resolves architecture questions, reviews evidence, and records acceptance. This task holds that role. It does not start workers or recurring monitoring implicitly.
- **Worker:** implements one assigned packet, makes routine in-scope decisions, verifies it, and hands back evidence. A packet is a specification, not authorization to execute it before assignment.
- **Maintainer:** controls commits, external writes, hardware access, and explicit exceptions. Architect acceptance is not authorization for those actions.

| Information | Canonical location |
|---|---|
| Safety, repository rules | AGENTS.md |
| Open queue, packet state, owner | Tasks.md |
| Current shipped state and active bottleneck | Research/CurrentState.md |
| Architecture and dataset decisions | NativeUIElementDetection.md / TrainingDataStrategy.md |
| Work contract | One canonical packet linked from Research/ImplementationPlans.md |
| Confirmed reusable lessons | Research/BestPractices.md |
| Evidence index and unresolved knowledge conflicts | Research/WorkerKnowledge.md |
| Experiments | Research/ExperimentLog.md |
| Completion evidence | reports/work/<packet-id>/handoff.md |

Do not create a second task board in a skill, plan, or learning log. Plans describe contracts; Tasks.md records execution state. Keep historical outcomes intact and label superseding decisions with dates and evidence.

## Packet lifecycle

`draft → ready → active → review → accepted`; use `blocked` with the exact missing prerequisite and resume condition. Only the architect marks accepted after reviewing the evidence. A worker can move its assignment to review, not self-accept it. Tasks.md may retain its existing checkbox notation with the packet state in text.

Before dispatch, verify: the outcome is independently reviewable, inputs exist or the missing-input behavior is defined, dependencies are accepted, file ownership is clear, acceptance criteria are observable, and permitted execution is explicit. A broad phase is not a packet. Split work when a second independently useful deliverable or new external dependency would obscure completion.

Assign the smallest useful slice with its own acceptance criteria. Software can be accepted against deterministic synthetic fixtures while an explicitly separate live-data or model qualification slice stays open. A reviewed interface/example can satisfy a downstream software dependency without acceptance of the upstream implementation. Draft interfaces permit bounded development but not claims of verified cross-project compatibility. Follow IterationRoadmap.md for these boundary decisions; do not convert missing pixels into a global software stop-condition.

For shared checkouts, record a single owner for each overlapping implementation file. Do not assign overlapping edits concurrently. Parallel agents require explicit authorization and disjoint ownership; independent preparation does not imply permission to spawn them.

## Cross-machine status updates

Follow AGENTS.md's shared-status section and the repository copy of
[SharedStatusSkill.md](../reports/coordination/SharedStatusSkill.md). Provide an update
at assignment start, meaningful progress/blocker changes, and handoff. Assigned NUA
workers publish directly to their own `packets.<packet-id>` entry in the exact shared
`nuiak/status.yaml` file. No coordinator relay is required. Preserve all other entries
and top-level summary fields; use the guide's bounded conflict-handling procedure.

The shared packet entry contains observation time (UTC),
packet/owner, work state, concise result, blockers, pending cross-repo requests, evidence
paths, next action, and four independent outcome states. Keep a local draft at
`reports/work/<packet-id>/coordination.md` if publication is unavailable, with
`publication: unpublished` and the reason. Local preparation is not delivery.
Reference the shared entry or unpublished draft in the worker handoff.

The architect can summarize observed work without replacing packet entries.
Record publication time, readback result,
and any peer acknowledgment separately. Use the schema's outcome vocabulary when
translating handoffs: pass → passed, fail → failed, not-run → not_assessed (or blocked
with a reason), not-applicable → not_applicable. Missing evidence never becomes a pass.

Share unavailability does not block unrelated offline assignments. Keep drafts in-project;
do not silently create an unmounted share path, start polling, or operate devices from
mailbox instructions. This is the narrow metadata exception in AGENTS.md, not a general
waiver for external writes. The shared folder is not a second task board.

## Context budget

Workers follow AGENTS.md's mandatory pre-code reading sequence. Read it once per worker context; do not repeatedly reload unchanged files. After that baseline, load only the assigned packet, selected skill, relevant knowledge entries, and changed source sections. After compaction, preserve what was read and re-read only missing or changed material. Never treat a summary as overriding an unread mandatory instruction.

Packets carry paths, symbols, invariants, exact evidence needed, and known traps—not copies of whole research documents. Use targeted searches and bounded output. Avoid dumping datasets, base64, complete checkpoints, or long training logs into the conversation. Prefer manifests over large directory scans (BP-34). Put verbose evidence in project-local files and report counts, paths, and failures.

Keep the packet small enough to hand off in one message plus its linked context. If implementation exposes a material design decision, record a short proposed amendment and continue independent authorized work. Do not silently broaden the contract to make tests pass.

## Safety and escalation

| Action | Worker handling |
|---|---|
| Assigned local code/docs and offline checks | Proceed within file scope and project boundary |
| Inference or a training smoke run | Execute only when the assigned packet includes it; isolate outputs and log experiments as required |
| Full training, model promotion, hardware use, external writes | Requires a packet explicitly authorizing that operation and satisfied prerequisites; current offline packets exclude these |
| Delete/overwrite existing datasets, checkpoints, historical reports | Preserve them; use a new output location. If unavoidable, present exact targets and recovery implications to the maintainer |
| Git writes, system mutation, uploads | Follow AGENTS.md restrictions; a worker packet cannot waive them |
| Protected filesystem path / sandbox denial | Use the product approval mechanism if essential; do not evade it with another tool or changed target |
| Missing identity, unavailable Office, invalid provenance | Stop dependent work; do not bypass, fabricate, poll indefinitely, or rerun unchanged failures |
| Conflicting instructions | Apply instruction precedence, cite the conflict, and isolate affected work pending a documented resolution |

All tools' implicit outputs count as writes: Python bytecode, caches, label caches beside external source images, Swift module caches, temporary files, downloaded weights, and reports. Inspect behavior before executing. Configure in-project destinations without repurposing HOME or CODEX_HOME. Do not close unrelated apps to free memory. Offline tests must not resolve dependencies over the network; if local prerequisites are missing, report that limitation.

Dataset readiness requires resolving actual image bytes and validating annotations, not just finding manifests, labels, caches, or old metric reports. Before dispatching data-dependent work, verify the needed split is complete. Preserve symlink targets as source dependencies; no cleanup of source trees or broken links without a reviewed dependency/recovery inventory and exact maintainer authorization. When inputs vanish, preserve evidence and separate recoverable originals from a newly versioned replacement (BP-52).

After a deterministic failure, investigate before retrying. For a transient failure, allow one bounded retry with evidence; then change the hypothesis or stop the dependent operation. Never automate retries of mutations or live capture as part of an offline packet.

## Review and handoff

Workers write `reports/work/<packet-id>/handoff.md` with:

Start with four outcome rows: **software verified**, **data eligible**, **integration qualified**,
**model gate passed**. Each is pass/fail/not-run/not-applicable with evidence and reason. Keep
bundle integrity and capture provenance distinct within data/integration evidence. No model
gate is passed by a documentation or mock-test deliverable. An external worker uses its own
authorized workspace for evidence and supplies a reference; no cross-repository write is implied.

1. Outcome and changed file paths; base revision and pre-existing dirty changes observed.
2. A row per acceptance criterion: pass/fail/not run, evidence path, and concise result.
3. Commands run, exit codes, relevant versions, and artifact/model/corpus hashes when applicable. Distinguish mocked tests, smoke runs, and real evaluation.
4. Remaining risks, scope deviations, and exact blocker/resume condition if any.
5. New learning: evidence and destination in BestPractices.md, or a knowledge issue if still unconfirmed.
6. A short continuation checkpoint: completed work, next concrete action, running process IDs if any, and files that must not be overwritten.
7. Coordination entry/draft path and delivery state: unpublished (with reason) or published (with readback evidence). Peer acknowledgment is reported separately; no coordinator approval is needed.

For an incremental slice, also record the contract revision, whether evidence is synthetic/real, accepted capability boundaries, and the next ready slice. Integrity, capture provenance, corpus eligibility, and model quality are separate claims. A contract change includes updated compatibility cases and affected consumers; no worker waits for an entire phase when only a reviewed schema is needed.

Code changes require the repository's offline Swift build/test checks plus focused tests of the changed behavior. Keep all artifacts inside the project. Record existing unrelated failures separately; never claim a complete pass or alter unrelated code to conceal them. Documentation-only work uses content/link/diff review. No training or Swift build is required solely for prose changes.

The architect checks correctness, scope, provenance, safety, meaningful test coverage, and whether the artifacts prove every acceptance criterion. Return specific changes if needed. Upon acceptance, update Tasks.md; move a parent to CompletedTasks.md only when all its acceptance conditions pass. Recompute the next ready item from actual dependencies, not the age of a plan. A failed model candidate returns diagnosis and a proposed next experiment; no automatic sweep or lowered gate is authorized.

## Learning loop

Capture a novel mistake in BestPractices.md using its required wrong/correct/why format and a concrete source. Keep uncertain observations in WorkerKnowledge.md with an owner packet and a condition for resolution. Link lessons from the packets they affect. Update a skill only when repeated operational behavior needs to change; do not copy the whole learning log into skills.

At each packet acceptance, retire stale guidance, update affected packet references, and check whether a new invariant deserves a regression test. Limit new rules to the failure actually demonstrated. Do not add process for hypothetical hazards or claim automatic background upkeep: maintenance happens during assigned planning, execution, and review turns.
