# Standard detection and focus improvement plan

Date: 2026-10-14. Planning reference: STANDARD391.

## Outcome and scope

Improve Standard UI detection, classification, and focus using controlled comparisons and complete decision reports.
Reduce repeated evaluation work without weakening evidence checks.
Keep HCF separate and optional. Preserve existing execution, approvals, models, and evaluation exclusions.

This plan combines the technical audit review, [research ideas review](../ResearchIdeasReview20261014.md), and [execution guide review](../ExperimentGuideReview20261014.md).
The [supplied technical audit](../../docs/nuiak_technical_audit_and_action_plan.md) remains a proposal, not measured evidence for its projected improvements.
[Tasks.md](../../Tasks.md) holds ownership and current status. This document defines implementation and experiment contracts.
The experiment names below are planning identifiers, not submitted or approved queue jobs.

## 1 Prioritized work packages

research-host-NUIAK owns implementation and acceptance unless stated otherwise.
Reuse the mapped work rather than create duplicate experiments.

| Priority and task | Deliverable | Existing work to reuse | Acceptance |
| --- | --- | --- | --- |
| P0 S391-01 Evidence selection | Case-linked Standard failure inventory and role map | STANDARD390, PROGRAM384-E1, FOCUS373-LOSSES, PROGRAM384-D1 | Every selected failure names inputs, groups, baseline, domain, and next decision; unavailable results remain unavailable |
| P0 S391-02 Shared evaluation | Bounded suite adapter with per-slice resume and output checks | Existing queue, evidence checks, comparison adapters | Same decisions and denominators as separate execution; no omitted slices; measured time and memory |
| P1 S391-03 Proposal and selection baseline | Deployable proposal replay and actual fallback comparison | PROGRAM384-B1, VISION353, RealModelScorecard36 | Separate proposal recall, class accuracy, focus selection, abstention, and cost; no known-box claims as deployment evidence |
| P1 S391-04 Targeted Standard data | Qualified producer recipes and paired control manifests | FOCUS363-B, FOCUS355, PROGRAM384-E3 | Observed native focus, reviewed geometry, connected groups, duplicate accounting, and exact capture receipts |
| P1 S391-05 One justified correction | Matched training, full regressions, and decision report | Earlier constrained fits, FOCUS360-E01, FOCUS329 and compatible successors | Target improvement and zero lost required successes; failure remains a recorded result |
| P2 S391-06 Boundary representation | Separate boundary/context feature comparison | Original production crops and retained detail studies | Preserve original inputs; report benefit by family, size, contrast, and position |
| P2 S391-07 Runtime qualification | Profile then optimize one measured bottleneck | Existing preprocessing, export, and package checks | Qualified numeric and decision parity; actual runtime and artifact-size measurements |
| P2 S391-08 Detector alternative | One conversion and memory feasibility report | Existing detector scorecard and export tools | Exact code/checkpoint terms, resident dependency check, Apple operator support, and bounded cost estimate |
| P3 S391-09 Optional HCF transfer | Standard-only versus paired teacher-assisted comparison | Existing HCF capture and model evidence | Student inference uses Standard pixels only; no loss of Standard successes; no default dependency |

## 2 First implementation tranche

Implement S391-01 through S391-03 first. Prepare S391-04 while those comparisons run.
Do not wait for HCF results to complete this Standard work.

### Evidence selection

Read completed STANDARD390 reports when available. Preserve pending results as pending.
Join retained detector predictions to reviewed controls by exact image identity.
Separate missed proposals, wrong classes, wrong focus selections, and missed transitions.
Distinguish shared control failures from failures introduced by a candidate.
Use existing matched seed results to distinguish repeat variation from a specific correction.

Produce one inventory with case ID, input hashes, group, role, domain, OS profile, baseline decision, candidate decision, and failure category.
Keep unknown OS profiles explicit. Do not rename historical mixed evidence as Standard-qualified evidence.
If an earlier test answers a proposed question, reference that result and close the duplicate proposal.

### Shared evaluation adapter

Extend compatible evaluation adapters, not the scheduler or active worker modules.
Group work only when input identities, preprocessing, encoders, and task semantics match.
Load shared inputs once. Preserve separate output records for every model and condition.
Use batched matrix operations only for compatible linear heads over fixed features.

Write each completed slice atomically with input hashes and its comparison settings.
Resume only verified slices. Preserve failed attempts and require explicit successors or permitted retries.
Require all declared slices before producing a complete decision report.
Expose actual progress events; missing totals produce no invented percentage or ETA.

Keep new code isolated until qualification. Deploy shared changes only at a confirmed idle boundary.
Do not restart the current runner to deliver this planning tranche.

### Proposal and selection adapter

Add the missing bounded entrypoint for the actual Swift fallback before measuring it.
Use read-only inference with fixed inputs and no navigation authority.
Preserve known-box crop evaluation as a separate diagnostic upper bound.
Record proposal source, score, geometry, suppression decisions, selected control, and abstention reason.
Use fully labeled frames for complete selection claims. Partial labels cannot establish complete false-positive rates.

## 3 Actionable diagnostic experiments

All diagnostic jobs use 800 s and 100 MB unless an explicit successor budget is approved.
Run through the existing detached runner only after implementation, input qualification, and individual job admission.
Use batches of 5–10 when ready work supports them. Do not create duplicate jobs to reach a count.

| ID / priority | Test and matched control | Required inputs or preparation | What the result decides |
| --- | --- | --- | --- |
| E01 P0 | Separate evaluation versus one shared suite | Same pinned models, slices, and adapters; S391-02 implementation | Adopt batching only if outputs agree and total cost improves |
| E02 P0 | Original detector proposals versus one lower confidence setting | Scorecard images, original predictions, pinned detector, development-only membership | Whether focused-target recall improves enough to justify added candidates and cost |
| E03 P1 | Detector-only versus detector plus rectangle proposals | E02 candidate records; resident Vision adapter; fixed duplicate rule | Whether added proposals recover controls or mostly add false candidates |
| E04 P1 | Independent crop scores versus simple screen-level selection | Identical fixed proposals and crop scores; complete frame labels | Whether context reduces wrong selections without losing correct selections or masking absent focus |
| E05 P1 | Fixed proposals versus bounded box displacement and size error | E04 inputs; predefined geometric perturbations; original crops retained | Whether localization tolerance needs priority over classifier retraining |
| E06 P1 | Actual Swift fallback versus existing learned selection | PROGRAM384-B1 entrypoint and compatible complete native frames | Which baseline and failure conditions the next correction must address |
| E07 P1 | Existing head versus constrained head on unchanged features | Earlier fit review; eligible training features; separate development inputs | Whether fitting can solve the conflict or features remain inadequate |
| E08 P1 | Additive combination versus a size-aware combination | Preserved whole/detail features, changed-area metadata, matched negatives | Whether scale information improves small movement without increasing content-only errors |
| E09 P1 | Existing training loss versus one margin penalty | E07/E08 failure evidence and eligible preservation training examples | Whether margin drift causes losses and responds to a simple correction |
| E10 P2 | Compatible checkpoint endpoints versus fixed interpolation coefficients | Verified common initialization, tensor semantics, buffers, and preprocessing | Whether interpolation preserves gains without a new training run |
| E11 P2 | Original crop features versus added boundary features | Native-resolution originals, geometric masks, unchanged crop comparison | Whether boundaries add information beyond artwork and padding |
| E12 P2 | Raw crop scores versus simple peer features | Fixed proposals; white artwork, identical neighbors, and single-control cases | Whether peer context improves selection before considering a transformer |
| E13 P2 | Current preprocessing versus one optimized implementation | Recorded timing bottleneck and pixel reference | Whether faster preprocessing preserves pixels or declared tolerances and all decisions |
| E14 P2 | Uncompressed candidate versus 6-bit candidate | Current package exceeds its applicable size gate; resident export tools | Whether compression solves delivery cost without lost decisions or unacceptable runtime |

E02 freezes one alternative threshold during preparation; do not choose it from final audit performance.
E03 fixes its duplicate policy on development inputs before comparison.
E08 retrains any detail score that previously represented a residual; do not reinterpret it as an independent probability.
E09 uses a soft penalty, not a claimed guarantee. Hard constraints need separate solver and tolerance checks.
E10 first reviews completed interpolation work. Do not repeat an answered question with renamed coefficients.
E11 tests RGB plus boundary information without overwriting an RGB channel or changing the original comparison views.

## 4 Data producers and learning experiments

research-host-TTR supplies qualified native Fixture captures when available.
research-host-NUIAK owns recipes, group roles, intake, and acceptance.
Use headless authored data for controlled mechanics; do not describe it as native OS evidence.

| ID | Producer and controlled comparison | Initial bounded design | Decision |
| --- | --- | --- | --- |
| P01 Standard proposal gaps | Same control family across supported sizes, center/edges/corners, clipping, and decoration | Up to 120 scenes from at least 30 new groups; Standard OS setting; matched geometry records | Which detector misses repeat under controlled native variation? |
| P02 Movement versus content | Matched scene with focus movement versus content-only changes; preserve dimmed-corner cases | Up to 120 pairs from at least 30 new groups; unchanged control body and recorded focus identity | Does the model confuse appearance changes with focus movement? |
| P03 Artwork and peer context | Same layout/focus with ordinary, white, identical, and decorative artwork | Up to 120 scenes from at least 30 new groups; reviewed no-focus cases only where supported | Do boundary or peer features resist artwork shortcuts? |
| T01 Targeted data | Existing training versus equal-budget data selected from one measured failure | Fixed initialization, preprocessing, epochs, example exposure, and matched Standard-only control | Does targeted native coverage improve the selected failure without losing previous successes? |
| T02 Representation | Existing architecture versus one justified boundary or scale-aware change | Same images and groups; change only the representation under test | Does the new representation solve a failure that fitting cannot? |
| T03 Sampling | Uniform versus failure-targeted selection from the same qualified pool | Same number of examples and optimization steps; selection uses development evidence only | Does targeted selection improve useful gain per accepted example? |
| H01 Optional transfer | Standard-only versus Standard inputs with paired HCF teacher targets | Verified existing counterparts first; equal training budget; teacher errors reviewed | Can HCF assist training without becoming a Standard inference requirement? |

These counts are initial experiment designs, not claims of ready data or statistical independence.
Freeze recipe lists, supported factors, seeds, and training/development/calibration/audit groups before capture.
Use separate authored and native reports. Do not silently replace unsupported native conditions with authored images.
Keep descendants, artwork derivatives, profile counterparts, and repeated events in the same connected group.
Store identical payloads once where supported, but retain distinct capture-event records.

Producer jobs use resumable shards of at most 12 scenes or pairs.
Proposed per-shard limits are 600 s and 100 MB. Actual 4K output size requires a pilot before those limits become executable specifications.
If a pair or shard exceeds those limits, record a justified producer budget before dispatch. Do not truncate required captures.
Stage inputs on verified USB storage. Reserve temporary extraction space and maintain the existing free-space requirement.

Each selected training comparison initially permits 30 epochs, 1,800 s, and 2 GiB per arm.
Freeze the exact trainer, seed, eligible manifests, control identity, and early-stopping policy before registration.
These proposed limits do not change existing approved runs or authorize automatic continuations.
If a timed-out run still improves, review a bounded continuation with complete resume state and a matched comparison budget.
Select at most 3 justified comparisons from T01–T03 and E07–E12 for the first training tranche.
Do not start every branch. Reuse a completed control only when all relevant settings and membership match.

## 5 Graph and decision contract

Use the existing supported graph types and job schema.
Each selected branch follows this sequence:

1. Identify the failure and compatible retained control.
2. Produce or reuse named inputs.
3. Qualify labels, roles, hashes, geometry, and groups.
4. Run the fixed comparison.
5. Evaluate target cases and all required previous successes.
6. Record supported, contradicted, or inconclusive with exact evidence.
7. Prepare a successor only when that decision justifies it.

Register all required comparisons and the terminal report alongside a new training specification.
Keep original failed and completed attempts immutable. Never treat missing results as model acceptance.
Scientific outcomes do not approve new downloads, navigation, physical-device capture, or deployment.

Every report includes counts, denominators, group support, margins, abstentions, gains, losses, and cost.
Keep detection, classification, focus selection, transitions, and settling separate.
Report family, theme, size, position, and domain where metadata supports them. Mark other cells unavailable.
Use paired group comparisons for compatible candidates; do not treat related frames as independent trials.
Require target development improvement and zero lost required successes before a candidate advances.
Freeze the model and thresholds before final audit. Previously inspected evidence remains development or retained regression evidence.
Core ML parity and TTR shadow evaluation follow model qualification; no navigation authority follows from this plan.

## 6 Deferred recommendations and reasons

| Recommendation | Decision and return condition |
| --- | --- |
| Replace all scripts with 6 executors | Defer broad rewrite. Extract shared evaluation first; preserve old immutable entrypoints |
| Telemetry as proof of scientific truth | Reject. Use real outputs, independent checks, and reproducibility; telemetry only corroborates execution |
| Automatic architecture changes from a metric | Reject unapproved expansion. Allow only predeclared branches with valid inputs and budgets |
| D-FINE or another detector | S391-08 feasibility first; train only after current proposal limitations justify replacement |
| Large GUI models for labels | Low priority; require privacy, license, memory, and human-review cost checks |
| Contrastive learning or screen transformer | Defer until simpler boundary/context tests leave an identified gap |
| Global serialization of Vision | Diagnose the affected API and concurrent test first; do not serialize all product inference without evidence |
| Shard-format migration | Benchmark current USB decode and a bounded shard sample before migration; preserve capture identities and restore paths |
| Git cleanup from historical file counts | Recount current tracked files; use a separate authorized cleanup task, not model experiments |
| HCF as an annotation oracle | Reject automatic truth claims; verify observed focus and body geometry independently |

## 7 Worker boundaries and handoffs

research-host-NUIAK prepares and admits jobs. The background runner owns execution.
research-host-TTR owns approved native capture and settings restoration.
compute-host-NUIAK can run a separately qualified training assignment when local capacity or measured throughput justifies transfer.
LittleDog may prepare manifests or reports only through an already qualified preparation contract.
compute-host-coordinator tracks delivery and dependencies, not experiment acceptance or local queue ownership.

Each future handoff names immutable inputs, hashes, entrypoint, environment, budgets, outputs, acceptance, and stop conditions.
Peer advice remains a proposal. It does not alter current approvals.
No worker message or assignment is sent by publishing this plan.

## 8 Verification and efficiency measures

Required implementation tests cover missing slices, altered hashes, duplicate predictions, role leakage, interrupted writes, and resumed evaluation.
Test unknown totals, unsupported conditions, box perturbations, and multiple overlapping proposals.
Test that reporting failure cannot stop the runner and that no new adapter mutates existing specifications.
Run focused tests, then the required integrated offline Swift checks after code integration.
Use a separate approved build location and do not interfere with active capture or training.

Measure separate execution against shared execution on identical inputs.
Record loading, preprocessing, inference, reporting, peak memory, artifact size, and recovery time.
Measure approved hypothesis to decision time and manual interventions across the next 3 campaigns.
Count resolved questions, new successes, lost successes, and useful model decisions rather than completed jobs.
Do not claim a speedup before measurements support it.

## 9 Completion and readiness

S391-01 and S391-02 complete on 2026-10-14. See [measured results](../Standard391Results.md).
The shared adapter qualifies cached prediction comparisons only. No inference acceleration or new model gain is claimed.
S391-03 and the Standard producer preparations are the next implementation scope.

This planning delivery completes when Tasks.md and the roadmaps link this plan with clear preparation requirements.
It does not claim that new jobs are executable or that the queue has additional ready duration.
S391-01 can begin with retained files; its final selection waits for any unfinished STANDARD390 comparisons.
S391-02 and S391-03 require implementation and qualification before their experiments become ready.
Producer work requires frozen recipes, eligible groups, a current target check, and measured storage needs.
Training waits for the selected hypothesis and complete qualified inputs, not arbitrary queue-count goals.

Review ready work when fewer than 10 useful jobs remain. Target 25 only when distinct justified questions and inputs support them.
Report ready duration separately from blocked preparation. Never fill capacity with duplicate or fabricated experiments.
The first substantial next tranche is S391-01–03 plus preparation of the highest-value Standard producer.
