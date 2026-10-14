# ADR-0028 — Reusable experiment templates

Date: 2026-10-14
Status: Proposed implementation; maintainer requests this design.
Owner: research-host-NUIAK.
Related: [graph design](ADR-0027-Evidence-Guided-Experiment-Graphs.md), [HCF completion](Plans/HCF389.md), and [implementation tasks](Plans/ExperimentTemplates393.md).

## Decision

Build a small preparation layer over the existing queue. Do not build another scheduler.
Use HCF completion to develop reusable templates. Keep HCF separate and optional for Standard NUIAK.
An agent supplies an experiment description. Tested templates generate immutable job specifications and their dependency graph.
Preparation does not approve or execute jobs. The existing approval checks and detached runner retain those responsibilities.

## What exists

The queue validates specifications, input hashes, dependencies, limits, and approvals.
`research_readiness.py` reports requirements and verifies available inputs without execution.
`research_graph.py` supports producer, qualification, experiment, and decision nodes.
`evaluation_suite391.py` supplies shared cached comparison work.
HCF389 supplies specialized preparation code and an ordered delivery plan.

No general template registry or description-to-job compiler exists yet.
Existing exporters do not establish a qualified queue export path.
The inspected HCF389 plan records that export support needs an engine change at an idle boundary.
This ADR describes new work, not an available command or completed feature.

## Template contract

Each template defines these fields:

- Identifier, schema version, implementation revision, and source hashes.
- Purpose, supported task, and graph node kind.
- Required inputs, output schemas, and compatible data roles.
- Allowed parameters, defaults, ranges, and forbidden combinations.
- Required tools, versions, device capabilities, ownership, and allowed actions.
- Resource limits, storage requirements, and temporary space requirements.
- Progress events, output validation, retry policy, and resume behavior.
- Acceptance checks and next decisions for success, failure, and inconclusive evidence.

Templates call reviewed adapters. They do not accept arbitrary shell commands or agent-generated Python.
A new scientific method can require a new adapter. A different dataset should usually require only different settings.
Environment requirements name the interpreter and required packages. A readiness failure never installs packages automatically.

## Experiment description

The author supplies the question, template versions, named inputs, changed factor, fixed controls, budgets, and decision rules.
The description also names the owner, data groups, data roles, retained successes, and dependent steps.
Named artifacts resolve through verified storage records, not machine-specific paths copied into new descriptions.
Future producer outputs use typed dependency references. Preparation never invents their hashes before they exist.
Dispatch verifies actual output hashes and role eligibility through the existing dependency checks.

The compiler validates the whole description before registration. It shows expected jobs, requirements, budgets, and unavailable capabilities.
Registration uses stable identities and a journal. A repeated request reuses matching registrations and rejects conflicting content.
An interruption resumes registration without duplicating jobs. Do not claim atomic registration until tests prove it.
Existing graph validation requires referenced jobs. The compiler checks the draft first, then validates the registered graph.

## Required HCF template inventory

These are proposed template contracts, not implemented executors.

| Template | Required inputs and outputs | Existing work to reuse | HCF purpose |
| --- | --- | --- | --- |
| T01 Evidence inventory | Manifests and receipts → coverage, integrity, duplicate exposure, and unresolved labels | HCF389 coverage and intake checks | Reuse accepted data; identify exact missing cases |
| T02 Dataset definition | Eligible records and group policy → frozen membership, roles, and exclusions | Existing group and ancestry checks | Separate development, calibration, and audit before generation |
| T03 Native capture | Qualified recipe, target, OS setting, storage → closed capture shards and restoration receipts | Existing TTR and Fixture capture adapters | Make only missing native HCF and Standard counterparts |
| T04 Data qualification | Capture shards and observations → accepted manifest or case-linked rejection | Existing native evidence and label checks | Check visible effects, labels, duplicates, and geometry |
| T05 Data preparation | Accepted manifest and preprocessing contract → crops, detector labels, or cached tensors | Existing crop and detector preparation | Preserve original views and production preprocessing |
| T06 PyTorch training | Prepared data, initialization, fixed settings → checkpoint, resume state, and training receipt | Existing FocusRing and YOLO trainers | Train only justified successors; reuse completed candidates |
| T07 Inference | Pinned model or rules, inputs, proposals → case predictions, timing, and hashes | Existing HCF scoring and rules adapters | Keep known-box and deployable-proposal results separate |
| T08 Comparison and decision | Matched predictions, labels, groups → gains, losses, coverage, and decision | Shared evaluation and HCF388 reports | Compare rules, classifier, and detector without hiding losses |
| T09 Candidate freeze | Reviewed comparisons and checkpoints → fixed candidate and inference settings | HCF389 candidate selection | Select before export or final audit; do not choose by audit score |
| T10 Core ML export | Frozen checkpoint and qualified exporter → package and input/output contract | Existing FocusRing and YOLO exporters | Convert without replacing original weights |
| T11 Vision parity | Package, PyTorch predictions, frozen cases → score, decision, and geometry differences | Existing parity tools; actual Vision adapter needs qualification | Verify the consumer path, including clipped crops |
| T12 Runtime benchmark | Qualified package and host → cold load, warm latency, memory, and size | Existing Apple runtime tools where compatible | Measure proposal and preprocessing costs separately |
| T13 Delivery package | Accepted evidence, package, license → optional bundle, model card, hashes, and rollback | Existing optional model distribution | Prepare TTR shadow use; public publication remains separate |
| T14 Consumer verification | Exact bundle and TTR receipt → independent integration decision | Existing coordination and receipt flow | Verify real TTR loading and inference; no navigation authority |

T06 has separate crop-classifier and full-screen-detector variants. T10 also has architecture-specific variants.
T08 supports both development comparisons and frozen audits. Their role checks differ and cannot silently substitute for each other.
T14 can prepare a request locally. It cannot claim remote execution or verification without a returned receipt.

## HCF completion graph

Reuse qualified completed nodes instead of repeating training.

1. Inventory retained results and check the chosen checkpoint.
2. Freeze the candidate and repair stale input references through explicit successor jobs.
3. Prepare export support and the actual Vision inference adapter.
4. Export the candidate and check PyTorch/Vision agreement.
5. Measure runtime costs on the qualified Apple host.
6. In parallel, define missing coverage and reserve groups before capture.
7. Capture bounded native shards and qualify their labels and visible HCF effects.
8. Compare rules, crop selection, and detector selection on compatible membership.
9. If findings justify correction, prepare data and train a bounded successor.
10. Repeat qualification only for artifacts affected by that successor.
11. Freeze settings and run the untouched audit plus retained regression checks.
12. Package the optional model and verify TTR shadow inference from its returned evidence.

Export preparation does not wait for new capture. Missing coverage still limits model claims and delivery qualification.
An inspection-only package can carry restricted claims, but cannot be reported as a completed HCF389 prototype.
No-focus performance, proposal recall, physical-device evidence, and known-box accuracy remain separate measurements.
The final result can be a rejected candidate with a precise reason. A failed model is not a successful delivery.

## Batching and resume

Share immutable decoded data and features when complete input identities match.
Group capture jobs only when target ownership, OS profile, restoration, and recipe contracts permit session reuse.
Reset model, optimizer, random state, and data order before independent training comparisons.
Do not introduce persistent training workers until isolation tests pass.
Each job keeps its own specification, progress, limits, outputs, and acceptance result.
Save verified outputs at meaningful boundaries. Completed output checks permit reuse; elapsed time does not.
Training resume requires verified optimizer, scheduler, random-state, and data-order support.
Preserve failed attempts. Explicit successor attempts identify what changes and why.

Use the verified USB volume for bulk data. Check mount identity, retained limits, and temporary space before dispatch.
Do not assume USB speed or cache benefit. Measure both with bounded workloads.

## Requirements and escalation

Report requirement states as satisfied, waiting for producer, blocked, or unsupported.
Each blocker names its owner, exact missing item, evidence, next action, and affected descendants.
Missing tools require an approved setup task or human decision, not an installation hidden inside training.
Missing TTR features produce a scoped proposal. Peer agreement does not expand execution authority.
Independent branches remain ready. Rejected or obsolete work keeps its reason rather than disappearing.

## Future versions

Pin template versions and generated specifications. Never change submitted jobs when a template changes.
Create a new template version for changed inputs, defaults, scientific meaning, or acceptance behavior.
Retain old adapters while approved jobs depend on them.
Use explicit successor jobs for migrations. Record old and new identities and the reason for replacement.
Add a capability only after a tested adapter supports it. Unsupported settings fail validation.
Keep hardware paths and credentials outside portable descriptions.

## Validation and efficiency

The first proof uses an existing scoring task, not an expensive new training run.
Prepare a second comparison through the same template without new experiment-specific Python.
Test unknown versions, invalid parameters, stale hashes, role leakage, and missing capabilities.
Test duplicate registration, interrupted registration, restart, output reuse, and failed dependencies.
Test isolated interrupted training against uninterrupted training before advertising resume support.
Compare separate and shared preparation with identical inputs and predictions.
Measure description-to-ready time, custom code, manual interventions, setup time, useful execution, and review time.
Record queue duration separately from job count. Do not repeat completed experiments to occupy hardware.

## Scope and rollout

Deliver templates incrementally within HCF work. Do not delay all HCF delivery until every template exists.
Start with T07 and T08, then the candidate/export/parity path, then capture and training variants.
Reuse specialized adapters behind typed wrappers before attempting broad internal rewrites.
Test engine changes in isolation. Qualify them between jobs without changing active approvals or worker ownership.
This design makes no runtime changes and launches no experiments.
