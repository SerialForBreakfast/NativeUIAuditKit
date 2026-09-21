# Failure-driven perception for TVTestRig

Revision 1, 2026-09-21. Canonical implementation contracts; status and ownership live
only in [Tasks.md](../../Tasks.md). This is a planning deliverable, not an assignment
to capture, infer, train, operate devices, publish peer requests, or modify TTR.
Use [WorkerWorkflow.md](../WorkerWorkflow.md) for execution and handoff.

## Intended outcome and priority

Improve TTR's perception of disclosure rows, interruptions and focus using measured
traversal failures. First dispatch a substantial **PER-01 + PER-02 offline benchmark
tranche**. P0 chevrons/dialogs precede new P1 focus and temporal extensions, then P2
identity work. Preserve active assignments and the existing usable-FocusRing goal;
these are complementary perceptual capabilities, not replacement model experiments.
No arbitrary new model is assumed: benchmark shipped behavior, geometry/OCR and
existing perception primitives before deciding which deficit needs learned weights.

User-reported examples (About → Name missed disclosure; Delete Siri History
interruption) are evidence requests, not independently verified captures or labels.
Record absent files as unavailable. Do not create training truth from this narrative.
TTR resume logic and teardown crashes remain producer software defects: model quality
cannot fix or waive them. Current Office staging access and simulator pause remain.

## Shared data and evaluation contract

- Proposed `perception-benchmark-v1` is a separate evaluation manifest, not a change
  to production annotation schemas, the frozen 41-class map, or public Swift API.
  A chevron relation can be auxiliary evaluation truth without adding a detector class.
  Any trained new output/category requires a separately reviewed mapping/metadata contract.
- Each case records ID, source kind (physical/simulator/test-only), capture/producer
  revision, artifact hashes, dimensions/coordinate convention, journey/run, screen,
  timestamps/frame order, recipe family/seed when applicable, label origin/reviewer,
  uncertainty, split group, partition and eligibility. Preserve original source fields.
- Relations include visible chevron → row, dialog → buttons, observed visual focus,
  transition intervals and screen/row correspondence. Distinguish visible/occluded/
  clipped/absent/unknown; never require detection of invisible pixels. Preserve disabled
  state separately from disclosure evidence. Accessibility omissions are missing evidence.
- Requested focus is intent, not truth. Fixture labels require observed callbacks and
  capture-correlated settled telemetry; stale/conflicting callbacks invalidate the label.
  Native captures need reviewed visual labels; AX is supporting evidence, not an oracle
  for visually omitted chevrons. Model/OCR predictions must never become automatic labels.
- Quarantine unreviewed inputs. Verify bytes and consent/retention scope before use;
  filenames, hashes and successful parsing alone cannot establish source or training eligibility.
- Keep complete journeys, related frames/retries, recipe families/seed variants and
  duplicate/near-duplicate content in one partition. Freeze the grouping algorithm and
  membership before fitting. Known failure examples are development/regression cases,
  not an unbiased final test. Reserve independent journeys and report unseen-screen/
  localization generalization only when the actual held-out grouping supports it.
- Freeze thresholds on development/validation only. Report counts, misses, false
  positives, abstentions, invalid inference, support and group-aware uncertainty;
  missing strata or zero support are unavailable, never passes. Separate physical,
  simulator and synthetic-test results. No aggregate may conceal a safety-relevant stratum.
- Version reports with corpus/model/evaluator/preprocessing/settings hashes. Record
  warm/cold latency, p50/p95, machine/OS and inference vs end-to-end scope. Fake timing
  is not a hardware benchmark. Confidence is not a calibrated probability by default.

## PER-01 — Evidence inventory, labels and split-safe benchmark contract

**Inputs:** user-reported failures, explicitly supplied existing local evidence,
current consumer contracts, taxonomy and TTR metadata definitions at a pinned revision.
**Authority/files:** NUA research schemas, a scoped inventory/validation CLI under
`scripts/`, tests and `reports/work/PER-01/`; read existing supplied evidence only.
No broad external scan, new capture, external copy or producer changes.

1. Inventory exact accessible captures and omissions; hash without modifying originals.
   Separate successful/failed/invalid trials and document which reported incidents exist.
2. Write the v1 manifest and labeling rubric, reviewed positive/negative examples and
   explicit mappings for coordinates and source kinds. Define ambiguous adjudication.
3. Implement the actual validation entrypoint and deterministic split-group checks.
   Preserve journeys and related content; do not split adjacent frames independently.
4. Freeze a coverage matrix: focused/unfocused, clipped/disabled rows, chevron-like
   icons/text, nested rows; dialogs/informational overlays/destructive confirmations,
   localized/ambiguous text, multiple/no focused buttons. Inventory support, not quotas
   invented from available screenshots. Identify precise missing evidence for TTR.

**Tests:** unsupported versions, corrupt/missing images, hash changes, out-of-frame
boxes, ambiguous relation targets, stale focus, prediction labels, duplicate content,
cross-journey leakage, output collision and deterministic manifest replay.
**Acceptance:** runnable validator, versioned examples/rubric, every supplied member
accounted for, coverage and leakage reports. Software can pass using explicit test-only
fixtures; real benchmark eligibility requires reviewed captures. Missing evidence does
not block completion of the software/inventory tranche or imply an eligible benchmark.
**Next:** PER-02 uses the reviewed interface immediately; real baseline needs eligible
inputs and an inference assignment. Keep any TTR evidence request local until authorized.

## PER-02 — Chevron-and-dialog benchmark and targeted training decision

**Inputs:** PER-01 reviewed contract/examples, existing detection/OCR observations,
shipped artifact metadata and explicitly assigned eligible captures for real inference.
**Authority/files:** isolated evaluation CLI, report schema and tests under `scripts/`,
research and `reports/work/PER-02/`. Offline fake-backed implementation first; no training,
capture, public API or default model changes. Reuse `reference_comparison.py` semantics
where compatible, but do not mislabel custom relation metrics as official YOLO mAP.

1. Integrate manifest validation → predictions → scored relations → versioned report.
   Pin box matching/IoU, row association, abstention and semantic-label rules before eval.
2. Compare available shipped detections plus geometry/OCR with a deterministic simple
   baseline and, if separately supplied, TTR's raster-chevron baseline. Mark unavailable
   TTR artifacts explicitly. Do not rebuild or run TTR to obtain them in this packet.
3. Score chevron localization separately from correct-row association and end-to-end
   disclosure recall. Count wrong-row links, decorative-arrow false positives and
   abstentions; include focused/clipped/disabled cases and localization strata.
4. Score dialog localization, button membership, focus selection and interruption type
   separately. Classify destructive/informational/unknown from reviewed semantics;
   ambiguous or unsupported language must allow unknown. Report destructive-as-benign
   errors explicitly. Never turn an informational label into permission to select.
5. Report both oracle-box component tests and actual proposed-box end-to-end behavior;
   telemetry can score outcomes but cannot populate model inputs or select predictions.
6. Produce a development error analysis: data gap, labeling issue, proposal/geometry,
   OCR/semantics, classifier, or producer runtime failure. Recommend the smallest change
   (software rule, targeted data, or one model), including no-training if appropriate.

**Tests:** exact/shifted/duplicate boxes, wrong adjacent row, clipped arrow, disabled
row, nested dialog, ambiguous localized confirmation, no/multiple focus, missing model,
inference failure vs empty success, abstentions, zero support and identical-run equality.
**Acceptance:** integrated CLI and reproducible fake-backed reports; real report only
when data/inference authority exists. A training recommendation names held-out support,
latency budget and proposed numeric acceptance thresholds for review BEFORE training.
Do not invent a model pass or universal threshold from screenshot counts.
**Next:** review PER-03; independently dispatch PER-04 software while real data is blocked.

## PER-03 — Targeted data and one perception candidate

**Inputs:** accepted PER-02 gap decision, reviewed numeric quality/latency gates and
output contract, eligible labeled corpus and explicit per-stage capture/training authority.
**Authority/files:** NUA data configuration, relevant trainer/evaluator tests and
isolated run artifacts. Producer capture is separately assigned to TTR. No new shared
class IDs, training stack or production artifact replacement by default.

1. Freeze a targeted capture/annotation matrix addressing development errors, including
   ordinary negatives and confusing chevron/dialog/focus cases, not just known failures.
   TTR supplies reviewed original captures and Fixture callbacks/geometry. Never activate
   destructive native actions to collect confirmations; use existing approved evidence
   or separately authorized inert Fixture replicas, labeled synthetic.
2. Freeze train/validation/test groups and eligibility before capture/training; retain
   failure regression cases separately. Validate each batch and raw-to-derived lineage.
   New collection needs its own bounded operation, health and resource-cleanup contract.
3. Log one candidate before launch, pin initialization/config/local weights, prohibit
   downloads and automatic sweeps. Select checkpoint on validation only. If a new head or
   auxiliary output is needed, accept its versioned consumer compatibility first.
4. Evaluate against PER-02 baseline on identical untouched test membership. Report all
   slices and regressions, abstention/coverage tradeoff and real deployment latency.
   CoreML export needs preprocessing/output parity and the reviewed deployment budget.

**Tests:** ineligible labels, leakage, corrupt members, unsupported map, wrong checkpoint,
output collisions, isolated export and failure accounting; required offline package checks.
**Acceptance:** reviewed data report then separately logged candidate/report against
predeclared gates. Failure yields diagnosis, not retraining. If FocusRing is the selected
change, use existing FR-B/FR-C ownership, quotas, six gates, 30-epoch baseline and ≤5 MB
limit instead of launching a duplicate PER-03 FocusRing experiment.
**Next:** external TTR-PER comparison and separate promotion decision; shipped models stay.

## PER-04 — Visual-focus robustness and physical consumer readiness

**Inputs:** SIM-DATA-02 review evidence, FR-A and existing crop/evaluation code,
PER-01 label/split contract; genuine physical pairs only for real qualification.
**Authority/files:** targeted extensions to `harvest_focus_pairs.py`, readiness/eval
scripts and tests, `FocusRingClassifier.swift` tests when needed, local reports.
No simulator/device execution, training or wholesale reimplementation of accepted packets.

1. Review delivered frame-specific extraction and isolate reusable behavior without
   relabeling physical sources as simulatorFixture. Preserve 16% expansion and 256×256
   preprocessing; test focused scaling, clipping and actual focused/unfocused geometry.
2. Validate observed callback/capture alignment, multiple distinct pairs per recipe in
   one split, unknown/no/multiple focus and verified hard negatives.
3. Integrate offline benchmark reports for lists/custom controls, light/dark/high-contrast
   and differing focus treatments. Score oracle crops and actual proposals separately;
   record crop parity, selection errors, abstentions and missing artifact failures.
4. Feed reviewed development deficits into existing FR-B pilot/corpus planning; extend
   the existing baseline tools rather than creating a competing FR-SIM-BASE pipeline.

**Tests/acceptance:** actual ingest/extraction/evaluation entrypoints, deterministic
fixtures for each edge case, physical/simulator provenance isolation, no prediction truth,
repository offline checks, complete criterion report. Software acceptance is independent
of Office export and does not close FR-B/FR-C data/model gates.
**Next:** assigned genuine P4-L/FR-B qualification when storage/operation gates permit.

## PER-05 — Bounded transition-readiness evaluation

**Inputs:** reviewed sequence manifest extension, existing `FrameSimilarity` and
change-ROI primitives; reviewed recorded sequences or deterministic test sequences.
**Authority/files:** offline evaluator and scoped perception tests; no live navigation.

1. Define labeled unstable/ready/unknown intervals with capture cadence and timestamps;
   distinguish crossfade, focus animation, scrolling, background carousel and static scene.
2. Benchmark current primitives before proposing a temporal model. Use task-relevant
   foreground/focus regions and bounded history; no future frames in online predictions.
3. Report premature-ready rate, readiness delay, false waits/timeouts, abstentions,
   support and latency. Missing/stale frames cannot prove settling. Freeze timeout and
   validation thresholds before test; endless background motion must not cause endless waits.
4. Produce a proposed TTR readiness observation contract; TTR retains timeout/action policy.

**Tests/acceptance:** stable foreground with moving background, crossfade, no focus,
missing/out-of-order frames, cadence changes, stale cache, bounded memory/time and
deterministic replay. Real usefulness requires held-out complete sequences; no learned
temporal training is authorized here. Propose one only if baselines demonstrate a gap.
**Next:** producer-owned fake-backed integration, then separately authorized live comparison.

## PER-06 — Screen and row identity under change

**Inputs:** PER-01 journey groups and reviewed identity labels, current
`TextAnchorVerifier`, OCR/detection observations; P0/P1 evidence has dispatch precedence.
**Authority/files:** offline matching/evaluation scripts, research contract and tests.

1. Define logical screen/row identity separately from text, scroll position and mutable
   values. Use journey-scoped ground-truth IDs; never infer globally stable IDs from pixels.
2. Benchmark existing text/geometry anchors against scrolling, repeated labels, changed
   values, localization, hidden rows and overlays. Return candidate/unknown, not certainty.
3. Freeze matching thresholds on validation; evaluate false matches, missed matches,
   abstentions, retrieval accuracy and latency on held-out journeys/screens/locales.
4. Define stale-route invalidation evidence for TTR; this does not implement route storage,
   resumable traversal or backtracking authorization in NUA.

**Tests/acceptance:** identical rows, localization without training examples, changed
values, missing anchors, ambiguous match and stale observation; bounded deterministic
candidate matching and slice reports. Unsupported locales remain explicit gaps.
**Next:** TTR-owned route/resume integration; model proposal only if measurements warrant.

## TTR-PER — Producer evidence and isolated comparison proposal

External proposal only, not published or assigned by this plan. Owner: TTR under its
own instructions. Inputs: reviewed PER-01/02 interface and exact permitted evidence list.

- Inventory and provide reviewed successful/failed/invalid captures with journey IDs,
  timestamps, source/build context, actual focus callbacks and AX metadata where present.
  Identify missing fields rather than fabricating them; requested focus stays separate.
- Verify existing artifacts and capture capabilities first. Add only evidenced contract
  gaps. App-owned preparation/export is a separate storage prerequisite, not a model fix.
- Provide fake-backed observation-consumer tests for relations, unknown/abstention,
  stale timestamps, missing models and artifact hashes. Candidate selection is isolated,
  default shipping behavior unchanged, oracle labels invisible to decision logic.
- Once explicitly authorized, compare models on identical held-out inputs and bounded
  safe scenarios: wrong/no-focus decisions, target-reaching, action count and latency.
  No destructive selection, broad Settings crawl or simulator operation is implied.
  Preserve invalid trials and require actual post-teardown health, not process presence.

Acceptance: revision-pinned evidence/interface compatibility and comparison report,
with runtime/software/data/model outcomes separate. NUA can implement software against
reviewed mocks while peer artifacts are missing. Publishing a future request, peer receipt,
assignment, execution and acceptance must each be reported separately.

## Verification and handoff for every tranche

Use focused positive/adversarial tests plus repository-required offline build/test checks
for code; docs use links/content/diff review. All outputs/caches stay in approved paths.
Handoff under `reports/work/<packet-id>/` records owned files/pre-existing changes,
contract revision, commands/exit codes, hashes, acceptance checklist, four independent
outcomes, blockers and next unblocked action. No single done checkbox combines software,
eligible data, genuine integration and model gates. Do not end a multi-packet assignment
at its first helper or fixture; integrate the complete assigned offline tranche.

This planning change makes no peer request and grants no hardware, inference, training,
filesystem exception, public API, deployment, remote execution or Git-write authority.
