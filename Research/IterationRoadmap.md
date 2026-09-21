# Concurrent development roadmap

**Revision:** 2, 2026-09-19. Full-backlog roadmap implementing the maintainer's accepted [DeliveryDecisions.md](DeliveryDecisions.md). Current ownership/state lives only in Tasks.md. This defines dependencies, not a second queue. Dispatch uses revision-4 ImplementationPlans.md; production phase gates remain binding.

## Next offline dispatch: chevrons, dialogs and visual focus

The 2026-09-21 [failure-driven perception contracts](Plans/TTRPerception.md) refine
the TTR goal. Preserve active assignments. Dispatch PER-01 + PER-02 as one integrated
offline tranche: inventory/labels/split contract → chevron/dialog benchmark → measured
gap and training decision. Missing captures block a real baseline, not test-backed
software and honest evidence inventory. PER-04 physical-source focus readiness can
proceed independently; do not reopen accepted packets wholesale.

PER-02 evidence → reviewed data/output contract and numeric gates → separately
authorized PER-03 targeted data/candidate → external TTR-PER comparison → separate
promotion. A FocusRing candidate reuses FR-B/FR-C, not a second training lane.
PER-05 benchmarks existing temporal primitives before any sequence model;
PER-06 evaluates identity after the higher-priority work. Whole journeys/related
content stay in one split; known failure examples do not become an unbiased test.
Producer resume/teardown defects remain separate. TTR requests are proposals only,
not published assignments. Simulator pause and Office storage blockers still apply.

## Physical model delivery: Office FocusRing

[Office delivery contracts](Plans/OfficeFocusRing.md) supersede the simulator-first
sequence below while simulator execution is user-paused. Highest available path:
P4-L one-bundle smoke/intake → FR-B physical development pilot and shipped baseline →
qualified corpus → FR-C one candidate/export → separately authorized TTR comparison.
Only the smoke request is authorized now. Broader capture, inference/training and model
promotion retain their assignment gates. Preserve unrelated workers and simulator evidence.
The semantic VoiceOver alignment matrix is separate from visual readiness.

## Delivery model

**Goal: usable perception, including FocusRing detection, for TTR.** The 2026-09-21
benchmark-first amendment above orders new offline work. [Follow-on contracts](Plans/FocusRingSimulator.md) connect datasets
to baseline → one candidate → TTR behavior. Preserve active workers; do not interrupt
unrelated authorized work. Historical numeric priorities below do not override this lane.

The [iOS platform plan](Plans/iOSPlatform.md) makes the five-class → 41-class delivery
path explicit: corpus preservation and offline toolchain work proceed independently;
eligible iOS pixels then enable Run 009 baseline/regression qualification without Office.
Only the planned mixed-data candidate needs the separate fixture-corpus prerequisite.
See [iOS tasks](../Tasks.md#ios-platform-tasks) for the grouped work and the single queue
for current state. Packet checkpoints are not turn boundaries within an assigned tranche.

Accept small software increments with their own evidence. Keep separate integration, data, and model qualification tasks open. A missing dataset or hardware slot blocks the relevant experiment, not completion of a serializer, validator, regression selector, or configuration preflight.

| Lane | Useful work now | Required later | Independent completion evidence |
|---|---|---|---|
| Producer/consumer compatibility | H1 contract snapshot; P4-A consumer validation against small offline bundles | Genuine producer bundle for P4-L | Versioned compatibility cases, explicit unsupported-version errors, lossless split/provenance handling |
| Evaluation software | P1-A export/preflight; P2-A comparisons; P3-A suite builder | P0 usable pixels for P1-B/P2-B/P3-B | Deterministic test artifacts, missing-data behavior, compatibility tests |
| Dataset recovery | P0-A read-only assessment | Approved P0-B recovery or separately planned reconstruction | Evidence inventory and recovery decision; corpus readiness measured separately |
| Training orchestration | P5-A config-only preflight; P4-B assembly engine | Eligible recovered training data and trusted real fixture corpus for launch | No-training validation tests, partition isolation, precise launch blockers |
| TVTestRig development (external owner) | Identity adapter implementation/tests, producer fixture exports, existing shipped-model integration | Hardware qualification when Office is available | Producer-side tests and candidate contract artifacts; no dependence on new 41-class weights |

No worker is assigned to another repository by this document. TVTestRig items are coordination proposals until accepted in that project's own queue. Do not send messages, write that repository, or run its build scripts from this task without an explicit assignment.

## Independent simulator dataset lane

The [simulator dataset contracts](Plans/SimulatorDatasets.md) add a local NUIAK-Mac
lane independent of Sillycon and Office. See [tvOS Simulator tasks](../Tasks.md#tvos-simulator-datasets)
for ownership/state. This milestone ends at validated datasets, not trained models.

1. SIM-DATA-01 read-only runtime inventory and SIM-DATA-02 offline consumer extensions
   can proceed independently. Runtime setup/storage and minimal capture need explicit authority.
2. Accepted runtime and consumer evidence unlock an explicitly authorized SIM-DATA-03
   42-recipe genuine pilot. Source inspection or mock fixtures cannot substitute for it.
3. Accepted pilot evidence enables FR-SIM-BASE: benchmark the shipped model and freeze
   the evaluation protocol before SIM-DATA-04 scale-up. Pilot errors guide training data,
   never selection or tuning of the final holdout.
4. Qualified SIM-DATA-04 data enables separately authorized FR-SIM-CAND, then FR-SIM-TTR
   compares the candidate with shipped behavior. Physical promotion remains separate.
5. SIM-DATA-05 is secondary and nonblocking; reuse shared frozen membership without
   delaying FocusRing. Its dataset scope still requires accepted pilot/interfaces.

Keep physical FR-B/FR-C, real-device holdouts and model gates separate. Simulator data
does not repair iOS data or satisfy DS-G8. Navigation-defect/VoiceOver datasets are deferred;
optional semantic alignment metadata is not a prerequisite for visual-only data.
Office remains released; no SSH, Sillycon operation or automatic simulator launch follows.

## Interfaces instead of phase handoffs

1. **Harvest wire contract:** producer-owned. H1 records the exact implemented revision, versions, receipt/index layout, coordinate contract, split semantics, and validation behavior. NUA adapts at its ingest boundary. Do not force TVTestRig to adopt an internal NUA annotation schema.
2. **Consumer normalized corpus:** NUA-owned. P4 preserves source/platform/identity evidence and transforms only validated fields; its internal schema evolves with documented compatibility.
3. **Prediction/report contract:** NUA-owned. P1-A records a draft v1 before implementation. P2-A/P3-A can develop against the reviewed sample contract without waiting for Run 009 inference. Breaking changes update the sample and affected contract tests together.
4. **Training readiness:** NUA-owned. P5-A accepts a versioned corpus description and reports configuration validity separately from data eligibility. It can be tested with incomplete or explicitly synthetic inputs without claiming launch readiness.

A contract review is a small boundary decision, not acceptance of the whole upstream feature. Workers may develop against a labeled draft; integration requires a reviewed compatible revision. Source/version mismatch blocks only that integration case, not all work on either side.

## Incremental compatibility loop

For each producer format change, the producer owner can publish a small local candidate bundle plus source revision, format version, expected result, and a focused change note. The NUA owner runs its consumer contract tests and returns structured accept/reject reasons. This exchange does not need a trained model or live hardware.

Use the current revision's artifacts until a new revision passes; support an explicit version range and fail closed outside it. Preserve negative cases for partial publication, unverified identity, malformed metadata, mismatched splits, and changed bytes. A mocked positive case proves parser/validator behavior only. Receipt/hash integrity never upgrades provenance or model quality.

Review compatibility whenever a candidate artifact or interface change exists; no standing meeting, idle polling, or hidden recurring automation is required. Give feedback as failing case + expected behavior + evidence path, not a broad request to finish a phase. Record new information once in the canonical contract/knowledge note and link it from affected packets.

## Readiness dimensions

Every packet reports four outcomes: **software verified**, **data eligible**, **integration qualified**, **model gate passed**. Use pass/fail/not-run/not-applicable with supporting evidence. The checks below explain those outcomes; a pass in one is not a pass in another:

| Dimension | Sufficient evidence |
|---|---|
| Software behavior | Focused offline tests and repository-required checks |
| Bundle integrity | Supported completed receipt/index, byte/hash/path/image/annotation checks |
| Capture provenance | Actual producer identity/run/generation evidence validated under the agreed contract; never inferred from offline success |
| Corpus eligibility | Complete pixels/labels, trusted provenance where required, class coverage and leakage-free split membership |
| Model quality | Documented comparable holdout results and unchanged shipping gates |

Where the producer currently returns `provenance: unverified` / `approvedForTraining: false`, retain that fact. Consumer ingestion for inspection/quarantine is distinct from assembling an eligible training corpus.

## Scheduling and ownership

With one worker, take the highest-ready software slice or P0-A; do not wait on a blocked full experiment. With authorized parallel workers, keep one owner per file group: evaluator, reference comparator, ingest/assembly, trainer, and read-only recovery. Shared schemas and Tasks.md updates are coordinated by the architect to avoid concurrent edits. Minimize work in progress; finish a reviewable slice before opening another unrelated change.

The architect accepts software slices individually and immediately makes their tested contracts available. Integration evidence is filed under a distinct suffix (`-B` or `-L`) so absent pixels/Office never masquerade as passed checks. Each slice handoff lists the next unblocked action and the exact remaining external prerequisite.

## Qualification convergence

- P0 establishes an eligible test corpus → P1-B actual baseline inference → P2-B reference integration; P3-B freezes/evaluates the real suite. Software slices may already be complete.
- Producer identity works + Office authorized/available + compliant export workflow → P4-L verifies a small genuine bundle. This does not require recovery of the iOS holdout.
- Eligible synthetic training corpus + trusted fixture corpus + P4-B + P5-A + resolved taxonomy/platform gate questions → separately assigned smoke/full training.
- Candidate plus both required holdouts → model gate review. Crop fork, macOS, release and model promotion dependencies remain unchanged.

TVTestRig can continue against the already shipped iOS/tvOS detectors and optional focus behavior under existing APIs throughout. New 41-class model availability is a later model-delivery event, not a prerequisite for application or harvest-engine development.

## Entire backlog and priorities

| Workstream | Independently useful delivery sequence | Gate that actually blocks execution |
|---|---|---|
| Recovery | P0-A → P0-B if recoverable, otherwise P0-C → new real baseline | Exact recovery/generation authority and proven corpus identity; no effect on toy-fixture software acceptance |
| TVTestRig integration | H1 and proposed TV-I1/TV-I2 → P4-A → P4-L | Genuine identity/bundle and hardware/export authority only for live qualification |
| Evaluation | P1-A interface → P2-A; P3-A independent → P1-B/P2-B/P3-B | Real pixels block B packets, not A software |
| Assembly/readiness | P4-A interface → P4-B; P5-A independent → P5-B | Eligible complete real corpora and resolved effective config |
| 41-class milestone | TRAIN-S → TRAIN-F → TRAIN-Q → REL-A/REL-B | All full-frame gates; badge deferred to its own model |
| FocusRing (first later-model priority) | FR-A → FR-B → FR-C → selected release evidence | Office/ground truth/coverage for harvest; six quality gates for replacement |
| Real tvOS holdout | R-A → R-B → R-C | Authorized matrix/devices; screenshots alone cannot qualify mAP |
| macOS (next platform priority) | MAC-A → MAC-B → MAC-C | DS-G8 before implementation, then coordinate/data/model gates |
| Badge (separate milestone) | BADGE-A specification/compatibility → BADGE-B | 41-class milestone before 42-class candidate; append-only map and new data |
| Crop (lower priority) | CROP-A → CROP-B | Accepted 6a-10 baseline; independent crop/full-frame gates |
| Unified (lower priority) | UNI-A → UNI-B | Comparable platform corpora/baselines and explicit deployment budgets |
| ScreenAuditKit (external) | SA-A → SA-B, fake-backed tests independent of new models | Assignment/dependency policy in consumer repo, not DS-G8 |
| Maintenance/release | DOC-A and HIST-A assessment independent; REL-A → maintainer REL-B | Protected-file authority, selected-model quality, and explicit maintainer git/promotion authority |

First assignments remain H1, P1-A, P0-A, P4-A and P5-A. P3-A and externally assigned SA-A offer independent software work. Publish reviewed example interfaces early; do not wait for entire upstream features before starting P2-A/P4-B.

Allocate an available authorized hardware window in this order: one genuine compatibility batch, FocusRing data/qualification, real-device holdout scale, larger fixture corpus. Do not reserve hardware or begin capture from this schedule alone. Missing data triggers bounded recovery then versioned reconstruction; it never silently lowers acceptance gates.

After DS-G8 prioritize macOS implementation. Badge specification may proceed earlier, but badge training is a later model. The 41-class release is not held for all later branches. Every failed experiment ends with diagnosis and a reviewed next experiment rather than automatic retraining.
