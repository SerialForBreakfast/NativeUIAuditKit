# Evaluation, corpus and training-readiness packets

**Revision:** 4, 2026-09-19. Each heading is a separate assignment. Read [common execution contract](../ImplementationPlans.md#common-execution-contract) and only the assigned packet. All packets are NUA-owned. Software assignments allow scoped edits/offline checks only; real inference and corpus use are explicitly identified below. Status/owner stays in Tasks.md.

## P1-A — Prediction export software

**Parent:** TASK-6a-11. **Inputs/context:** existing evaluator; architecture §8.3/8.5/9.2; BP-10/27/34/37/50/52; K-01/07/11. No real test corpus required.
**File scope:** `scripts/eval_phase6a.py`, additive serializer/tests, `Research/schemas/prediction-artifact-v1.md`, P1-A reports. No comparator changes.

1. Document a versioned format: original-image top-left pixel xyxy boxes, frozen integer class IDs, finite scores [0,1], dimensions, corpus-relative image IDs, explicit empty/failed results, completeness, model/category-map/corpus/settings hashes and evaluator versions. Publish a reviewed small example before completing code, unblocking P2-A.
2. Add an isolated mode with explicit checkpoint/output arguments; preserve existing callers. Resolve/decode all required images and validate labels before real inference. Missing members fail readiness; never shrink the requested corpus silently.
3. Export from the inference used for metrics, or prove/record settings equivalence between existing `run_val`/`run_predict`. Distinguish official Ultralytics from custom AP. Optional blur/quantization/CoreML work must not run in this mode.
4. Prevent stale label reuse and output collisions; use manifests rather than large directory globs. Explicit weights avoid the current Run 007 default. Preserve historical report files.

**Tests/acceptance:** rectangular-image coordinate recovery, empty detections, failed/corrupt image, invalid IDs/scores, duplicate image IDs, missing target of a symlink, incomplete corpus, and output collision. Exactly one result record per input in a completed test run. Synthetic tests do not claim real metrics. Required offline repository checks pass or are reported as blockers.
**Deliverable/next:** schema, serializer/evaluation mode and evidence in P1-A handoff; early interface to P2-A; accepted software to P1-B.

## P1-B — Run 009 real baseline inference

**Parent:** TASK-6a-11. **Inputs:** P1-A; eligible complete P0 test corpus; Run 009 best.pt; installed local dependencies. **Scope:** one actual PyTorch holdout evaluation and additive P1-B artifacts; no training/export.

1. Record checkpoint/corpus hashes, taxonomy, completeness and original-versus-replacement identity. If historical original is recovered, verify all 2,000 members; a replacement uses its independently reviewed membership/version.
2. Run the accepted evaluator with effective settings recorded; account for every image. Keep original reports intact and measure elapsed time.
3. Report per-class support and explain discrepancies from historical 0.585669 only where corpus/settings are comparable. Otherwise label a new baseline and suppress direct historical deltas.

**Acceptance:** complete predictions/metrics manifest, no silently failed members, correct identity labels and settings. An unexplained difference blocks baseline acceptance, not unrelated software. **Next:** P2-B; make P3-B evaluation possible.

## P2-A — Reference-comparison software

**Parent:** TASK-6a-11. **Inputs:** reviewed P1-A schema/example, not P1-B. **Files:** `scripts/eval_reference_metrics.py`, additive tests and comparison-contract notes. **Context:** BP-27/32/52; K-11.

1. Require equal corpus content/labels/taxonomy and equivalent preprocessing/NMS/threshold/metric-version settings for numerical comparisons; different model hashes are expected and allowed.
2. Validate referenced prediction paths/hashes/completeness; report historical metrics, present images, present predictions, and reproducibility separately.
3. Produce aggregate/per-class deltas with sample counts; zero, undefined and unavailable are distinct. Hash canonical stable content separately from timestamps and self-hash fields.
4. Support explicit inputs/isolated outputs; preserve existing historical artifacts and unavailable real-world corpora.

**Tests/acceptance:** same inputs give zero deltas; changed labels/images/settings/taxonomy reject comparison; missing/corrupt referenced files reject qualification; unchanged stable content hashes equally despite timestamps; surviving labels/old metrics with broken pixels cannot imply a runnable corpus. **Next:** P2-B.

## P2-B — Real reference integration

**Parent:** TASK-6a-11. **Inputs:** accepted P2-A and P1-B artifacts. **Scope:** aggregation/validation only, no extra inference required.

Verify source hashes/configurations; produce a new reference report and the actual supported corpus entries. Leave absent real-device/production corpora unavailable. Document compatible and incompatible historical comparisons and the exact report hash.

**Acceptance:** all metrics trace to P1-B; no fake coverage or cross-corpus deltas; historical reference preserved. **Next:** candidate evaluations consume the same comparison contract.

## P3-A — Deterministic regression-selector software

**Parent:** TASK-6a-11. **Inputs:** synthetic image/label fixtures; TrainingDataStrategy §12.1, BP-27/32/34/52. No inference dependency. **Files:** additive builder/tests; `Research/schemas/synthetic-regression-v1.md`.

1. Specify deterministic seed, ordering and strata based on available family/class/aspect/small-element metadata; target 200–300 images with explicit coverage exceptions. Never use Run 009 errors as selection criteria.
2. Manifest records source split/platform/family, image/label hashes, dimensions and algorithm/version. Validate all pixels and annotations; labels-only output is incomplete.
3. Check content/source/family leakage against supplied train/val manifests, freeze membership, and require a new version for changes. Do not modify source splits.

**Tests/acceptance:** repeatable ordered membership; coverage gaps explicit; changed/missing images or labels invalidate; overlap rejected; unsupported classes visible. **Next:** P3-B; software can be accepted while pixels remain absent.

## P3-B — Freeze and evaluate real regression suite

**Parent:** TASK-6a-11. **Inputs:** P3-A, eligible P0 corpus, compatible P1-A/P2-A interfaces and Run 009 weights. **Scope:** freeze real manifest and run baseline inference only as needed; reuse verified complete P1-B per-image results when the metric path supports exact subset evaluation.

Freeze selection before candidate evaluation. Validate byte/annotation hashes and split isolation; evaluate Run 009 on that exact suite and report class counts/gaps. Describe it as a diagnostic subset of the full holdout, not independent evidence or DS-G8 replacement.

**Acceptance:** immutable manifest plus traceable baseline; any changed suite version re-evaluates both compared models. **Next:** regression checks for subsequent candidates; full holdout gates stay open.

## P4-A — Consumer bundle validation and normalization

**Parent:** TASK-INTEGRATION-01 / TASK-6a-10. **Inputs:** H1 source-pinned contract (draft allowed during development); existing ingest tests. **Files:** ingest script/tests, additive validator, FixtureBatchIngest.md, versioned schema and architecture §6 updates. **Context:** BP-10/28/52; K-05/08/09/12.

1. Validate receipt/index/publication/version and bounded safe paths before normalization. Reject partial output, altered bytes, missing pairs, malformed images, dimensions/boxes mismatch, nonfinite coordinates, stale focus and conflicting splits. Never follow artifact symlinks to evade the bundle boundary.
2. Preserve source revision, platform, split and identity evidence. Unknown classes follow BP-28 with explicit counts; no remapping. Empty usable annotations are ineligible for training.
3. Keep integrity and provenance independent: unverified bundles may be inspected/quarantined but never become eligible by normalization. Do not fabricate an attestation format.
4. Publish normalized corpus interface early for P4-B. Deduplicate baseline frames with unfocused labels without hiding cross-split conflicts.
5. Document and implement a new annotation-schema version permitting scale 1; retain the old schema/version for existing scale 2/3 artifacts. Validate each artifact by its declared version. Do not add badge in this change.

**Tests/acceptance:** H1 cases plus paths/symlinks, bounds, deduplication, unknown/empty labels, schema backward compatibility and untrusted-positive eligibility. Confirm source bytes unchanged. Required offline checks apply. Live compatibility is not part of software acceptance. **Next:** P4-B, P4-L.

## P4-B — Split-safe assembly software

**Parent:** TASK-6a-10. **Inputs:** reviewed P4-A normalized interface; toy corpora with all split types. **Files:** additive assembly/tests, corpus-interface notes; no live capture or real-data rewrite.

1. Produce deterministic membership with source/platform provenance and parameterized blend. Preserve synthetic train/val/test and fixture training/calibration/held-out; calibration never becomes training.
2. Reject cross-split duplicate content/related recipe groups. Compute coverage and class-weight inputs from training only; prevent exporter/OHEM from reintroducing held-out samples.
3. Publish assembly summary and readiness interface for P5. Do not choose real blend proportions from toy data; record the calculation/selection in P5-B using actual coverage.

**Acceptance:** identical inputs yield identical memberships; tests prove leakage rejection, train-only weighting, provenance retention, output isolation and explicit uncovered classes. If downstream isolation needs file changes outside this scope, return that exact expansion before claiming safety. **Next:** P5-B once real data is eligible.

## P5-A — Validation-only training preflight

**Parent:** TASK-6a-10. **Inputs:** trainer source, minimal documented corpus-readiness interface and fixtures; no live dataset needed. **Files:** train_ios_model.py, additive preflight/config tests, architecture §8 / TrainingDataStrategy decision, launch runbook. **Context:** ADR-0006; BP-29/30/33/37/51/52.

1. Separate explicit initial weights, interrupted-run resume, and validation-only execution. Reject initialization+resume together. Validation-only must not construct a trainer, initialize MPS, download weights or run inference.
2. Resolve paths/hashes/taxonomy, source pixel/label availability, split eligibility, class-weight provenance and unique outputs. Report configuration validity separately from real launch eligibility; test-only provenance cannot authorize launch.
3. Specify fresh Run 009 best.pt initialization, 150-epoch target/max, cosine scheduling, warmup, patience, seed, batch, and full-frame augmentation. Record research decisions before changing defaults; keep the gated crop experiment separate.
4. Use a readiness adapter so the final P4 assembly path can be bound later. Publish commands matching implemented flags; prohibit accidental overwrite of prior runs.

**Acceptance:** tests prove no training/download side effects, fresh/resume separation, missing-pixel/ineligible-corpus rejection, stale weights/config rejection and output collisions. No two-epoch smoke run is included. **Next:** P5-B.

## P5-B — Actual candidate readiness

**Parent:** TASK-6a-10. **Inputs:** P5-A, P4-B, eligible synthetic train/val/test, trusted fixture training/calibration/held-out, and accepted evaluation interfaces. **Scope:** actual configuration/coverage validation, no training.

1. Bind real manifests and freeze their hashes and per-platform coverage. Document the scientific role of tvOS fixtures in the iOS candidate; select and record blend based on measured class/style coverage, without changing taxonomy or leaking holdouts.
2. Resolve exact batch/seed/schedule/early-stopping/augmentation values and test the complete effective configuration. Emit all unresolved launch blockers as failures, not warnings hiding eligibility.
3. Record separate evaluation commands/gates; reserve no run number now. The launching worker allocates from the current experiment log immediately before execution.

**Acceptance:** immutable reviewable configuration, complete eligible corpus descriptions and zero unresolved launch blockers. A necessary design change returns to architect review rather than auto-launch. **Next:** TRAIN-S.
