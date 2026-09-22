# Perception/intake offline completion

2026-09-22. Base `7d056eaaeac697b301f57b01d2380b4496530f88`.
Scope: [assigned contract](../../../Research/Plans/PerceptionIntakeCompletion.md).
**Complete for review**, not a trained model or genuine capture qualification.

| Outcome | Result |
|---|---|
| Software verified | Pass: real CLI paths, deterministic positive/adversarial fixtures, offline package checks |
| Data eligible | Not established: every new integration fixture is generated test-only; legacy data remains unqualified |
| Integration qualified | Offline consumer pipeline passes; genuine TTR capture/intake remains blocked by unresolved native focus |
| Model gate passed | Not assessed; no real-data inference, training, new weights, or promotion |

## Delivered end-to-end behavior

PER-02 extends the existing manifest/scorer CLI, not a new competing benchmark:
independent detector/OCR observations → deterministic relation baseline → actual
vs oracle-box/role comparison → source/style/partition slices → bound report.
No truth labels enter the actual baseline. Oracle component inputs never substitute
reviewed semantics or focus for predictions. Imported predictions/timing are not
claimed as execution here; missing TTR raster artifacts remain unavailable.

PER-04 extends completed-bundle extraction with physical-source review bindings,
native frame observations, actual geometry and decoded-pixel isolation. The
existing production Swift v1.3 recrop path preserves physical identity. Its real
readiness CLI calls existing baseline preparation/scoring and separately scores
independent proposals, with no implicit inference or training. Legacy metadata
inspection stays ineligible. A diagnostic pilot without hard negatives reports
null FPR, never passes a model gate.

## Acceptance map

| Criterion | Evidence |
|---|---|
| Independent geometry/OCR baseline; truth separation | `test_perception_completion`: changed truth leaves actual predictions unchanged; oracle semantics remain observation-derived |
| Row association and localization | Exact independent row IDs matched geometrically; wrong-row prior tests, ambiguous adjacent/nested rows, clipped visible pixels and duplicate proposals |
| Dialog/button/focus/semantics | Multiple-dialog and multiple-focus abstention; unknown locale; destructive-as-benign distinct from unknown; no-focus/error counts |
| Failure vs empty success | Per-case failed/unavailable reasons and accounting vs successful empty observations; absent artifacts not fabricated |
| Slices/replay/identity/latency | Stable manifest/input/settings/evaluator hashes; source/partition/theme/control/locale/treatment/row-state support; group bootstrap; fake/import timing explicitly unqualified |
| Development decision | Per-case triage; no-training while independent eligible support, numeric gates, latency budget and run authority are absent |
| Actual physical intake/extraction | `test_physical_focus_integration`: completed wire-format test bundle → real harvest CLI → production recrop → real readiness/baseline CLI → independent proposal CLI |
| Ground truth/geometry | Bound raw bytes/frame IDs/native observations, missing/stale/multiple/requested-only rejection; distinct focused/resting boxes; pixel/normalized disagreement rejected |
| Provenance/eligibility isolation | Physical review binds index/receipt; contradictory simulator source rejected; test-only source preserved through protocol/report; no eligibility upgrade |
| Corruption/leakage/collision | Shared existing tests plus physical failures, forged crops, distinct elements within one group, split leakage and differently encoded identical pixels |
| Model/protocol safety | Explicit model metadata/identity, exact score membership; final holdout excluded by development protocol; diagnostic zero-hard-negative support cannot pass gates |

## Verification

All final commands below exit0. Prefix: `PYTHONDONTWRITEBYTECODE=1 .venv-yolo/bin/python`.
Logs under `.build/debug-output/perception-intake/`:

- `-m unittest discover -s scripts -p 'test_perception*.py'`: **16 tests**, `python-perception-final.log`.
- `-m unittest discover -s scripts -p 'test_*focus*.py'`: **56 tests**, `python-focus-final2.log`.
- `-m unittest discover -s scripts -p 'test_evidence_audit.py'`: **14 tests**, `python-audit.log`.
- `-m unittest discover -s scripts -p 'test_harvest_bundle_validation.py'`: **9 tests**, `python-bundle.log`.
- `scripts/test_ingest_fixture_batch.py`: standalone ingest checks, `python-ingest.log`.
- `-m unittest discover -s scripts -p 'test_integrated_offline_toolchain.py'`: **1 test**, `python-toolchain.log`.
- Offline `swift build`: pass, no warnings; `swift-build-host.log`.
- Offline `swift test`: **92 tests / 9 suites**, pass, no warnings; `swift-test-host.log`.
- `git diff --check`, local links, syntax and JSON/YAML checks: pass.

Swift used project-local TMPDIR/cache/config/security paths and
`--disable-automatic-resolution --manifest-cache local`; exact pattern is in the
FOCUS-LAUNCH handoff. Initial restricted build failed `sandbox_apply`, retained
in `swift-build.log`; approved identical host build passed. Initial FocusRing suite
found one expected-report shape change, fixed with explicit unavailable/no-gate
assertions; initial log retained separately. No hidden failures called passes.

Existing suites exercise the real CoreML artifact on generated test-only images;
new baseline integration uses explicit fake scores. Neither is real-data inference
or a physical deployment benchmark. No experiment ID was allocated.

## Existing deliverable review

**FOCUS-LAUNCH: accepted for its original offline scope.** Inspected production
crop/tool/validation/baseline/planner integration and reran its tests, including
production crop content and generated-image CoreML checks. No public API/new weights.
The old interpolation and historical runtime-metric caveats remain binding.

**EVIDENCE-AUDIT: accepted for its original offline scope.** Inspected audit,
readiness and evaluator gate corrections, verified retained audit file SHA256
`f29997b9311a2bec5a03c49265e788a3778fa8238c56e7ce321feb6538f33cf6`, and reran its
14 tests. No new broad corpus scan or inference. Its findings still prohibit treating
the legacy1,500 pairs as independently qualified data. PER-01's broader real label
coverage review is not silently closed.

## Files, preservation and limits

Changed implementation: existing perception scorer, new observation adapters;
shared FocusRing contract, bundle extractor/normalizer, physical readiness,
baseline reporter and new independent proposal scorer. Added perception/physical
integration tests and updated one baseline expectation. Contracts/rubrics,
catalog/roadmap/queue/knowledge and this evidence updated. Shipped Swift/model
implementations unchanged by this tranche.

Preserved pre-existing dirty Tasks/BestPractices/CurrentState smoke updates and
untracked `readiness-20260922-0024/` and `smoke-20260922-0031/` reports. Existing
worker turns were completed/not loaded; no active overlapping worker was found.
The architect took only the assigned correction files. No Git writes, producer
edits, simulator/Office operations, real-data inference, training or promotion.

Physical native-observation fields are a NUA-owned review artifact with explicit
admission bounds, not a new TTR wire format or authenticated identity. Actual
source evidence must support them; do not fill gaps with requested focus.
Pair-target proposals do not prove exhaustive screen/navigation accuracy. Imported
timing does not prove latency. Near-duplicate journey independence still needs review.

Coordination: publish only the changed consumer acceptance requirements under
NUA's shared packet; see `coordination.md`. Local test progress is not peer noise.

## Next concrete work

1. Architect review this new PER-02/PER-04 tranche; no need to redispatch foundations.
2. Once the maintainer's TTR fix is ready: an authorized clean smoke, byte-backed
   intake, then a separately assigned development pilot and shipped-model baseline.
   Preserve final evaluation groups before scaling to ≥6,000 pairs.
3. If capture is still blocked, the next independent tranche is PER-05: review its
   sequence contract and benchmark existing frame/change-ROI primitives on offline
   sequences. No temporal model training is needed to start that software work.

Whole assignment stops here because implementation, CLI integration, verification,
existing-deliverable review and handoff are complete. Genuine data/model gates are
explicitly outside this offline assignment; no background work is implied.
