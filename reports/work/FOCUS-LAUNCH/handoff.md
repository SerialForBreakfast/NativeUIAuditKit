# FOCUS-LAUNCH — offline tranche handoff

2026-09-21. Base revision `012538a977c2defb6c6d0cb6f3daac465dcc5367`.
Delivered for review. Contract: `Research/Plans/FocusRingLaunchPreparation.md`.

## Outcome

Fixed a real production crop-coordinate defect and completed the runtime-backed
dataset/baseline path plus offline capture planning. No training, capture, new
weights, public API, producer wire change, external repository edit or git write.

The previous CGContext flip sampled and vertically inverted the wrong source
region. Known gradient experiments and a production Swift regression demonstrate
the correction. Expansion remains 16%, output 256×256. Historical runtime metrics
must be re-baselined: this is not evidence that model quality gates now pass.
The Python/CoreGraphics kernels still differ; new manifests use the actual Swift
implementation instead of pretending Pillow is pixel-identical.

## Acceptance evidence

| Criterion | Implemented integration / evidence |
|---|---|
| Production crop parity | `FocusRingTool` calls package-only `makeCrop`; Swift content-orientation test and six Python gradient cases cover fractional/edge/tiny/expanded boxes. Exact repeated runtime crops and forged-crop rejection pass. |
| Usable derived dataset | `focus_runtime.py` streams verified raw frames into exclusive v1.3 output; shared validator recomputes exact pixels and pins runtime/source identity. Historical v1.2 preserved but training-blocked. Review approval is removed on recrop. |
| Actual baseline adapter | Existing baseline CLI prepares frozen development protocol then `--infer` runs the bundled CPU CoreML model through production classifier. Two generated test-only images exercised real inference. Model/protocol/membership identity, per-slice errors/abstentions/coverage and load/first/warm timing recorded. |
| Deterministic preparation | `focus_capture_plan.py` freezes catalog hashes, explicit related-seed groups, exact 80/10/10 assignment and whole-group batches ≤100 recipes. Quota feasibility never establishes data eligibility. |
| Safe resume/accounting | Ledger reconciles every target accepted/rejected, requires completed receipt/clear cleanup, rejects duplicate pair/content/split drift/changed plans. Ambiguous attempts suppress resume; rejected targets remain deficits. |
| Review reconciliation | `review.md` accepts FOCUS-CONSUMER offline scope and records bounded PER-01/02/04 corrections with evidence; their implementations remain untouched. Queue/catalog/roadmap updated together. |

No real full-scale recipe catalog was invented. TTR templates do not necessarily
produce element_count focusable controls; source/observed target enumeration and
the genuine pilot must supply that catalog. Test quota catalogs explicitly contain
fabricated IDs/types and are not producer-compatible or dispatchable.

## Verification

All commands below exited 0. Logs retained under `.build/debug-output/focus-launch/`.
Python prefix: `PYTHONDONTWRITEBYTECODE=1 .venv-yolo/bin/python`.

- `-m unittest discover -s scripts -p 'test_*focus*.py'`: 45 tests, including 14 new launch tests and actual CoreML test-only roundtrip; `python-focus-all.log`.
- `-m unittest discover -s scripts -p 'test_perception_benchmark.py'`: 5 tests; `python-perception.log`.
- `-m unittest discover -s scripts -p 'test_physical_focus_readiness.py'`: 3 tests; `python-physical.log`.
- `-m unittest discover -s scripts -p 'test_harvest_bundle_validation.py'`: 9 tests; `python-bundle.log`.
- `scripts/test_ingest_fixture_batch.py`: all standalone checks pass; `python-ingest.log`.
- `-m unittest discover -s scripts -p 'test_integrated_offline_toolchain.py'`: 1 test; `python-toolchain.log`.
- Offline `swift build`: passes, no warnings. `swift test`: 92 tests / 9 suites pass, no warnings. `swift-build.log`, `swift-test.log`.
- `git diff --check`: passes. 123 local document links checked; zero missing files.

Swift commands used approved host execution after sandbox compiler restrictions,
with this environment and flags (substitute `build` or `test`):

```sh
TMPDIR="$PWD/.build/debug-output/focus-launch/tmp" \
CLANG_MODULE_CACHE_PATH="$PWD/.build/clang-module-cache" \
swift test --disable-automatic-resolution \
  --cache-path "$PWD/.build/debug-output/focus-launch/cache" \
  --config-path "$PWD/.build/debug-output/focus-launch/config" \
  --security-path "$PWD/.build/debug-output/focus-launch/security" \
  --manifest-cache local
```

The positive preflight integration test mocks quotas on a tiny real-byte fixture;
separate quota tests cover 6,000-row policy and planner feasibility. Neither is an
eligible corpus. CoreML timing is CPU-only on macOS 26.4.1 arm64, not tvOS deployment
latency or an authorized real-data benchmark. CoreML stdout diagnostics initially
broke JSON parsing; the helper now isolates its protocol descriptor from logging.

Hashes of final evidence (SHA-256):

- Crop source: `c40042b27f231d8d23b05e0025f60552f44f268036dece458f78b97316852a6f`.
- Built helper: `4057e91ea68b76863e44c4e34195e2333b857f1c753b9de7973f4c0d560534e7`.
- Bundled model canonical tree: `9e5ba294e545b4ae0c54aa5d483b1a1f681b6c30477882700b4dbe139b9c66b7` (algorithm `artifact_digest`).
- `crop-parity.json`: `fd44d15f7e38a56ca9e12ad3c142755c35b3ffa0b18c8ff8896a7b2bc81e3edd`.
- `inference-test-report.json`: `301cf0c1c1472cfa2fb4716e20fe2d362a3599dba8fe60e4ffa678530d20a426`.

The last two files are local test evidence in the log directory, not release data.
Rerunning tests regenerates timing/temporary membership and changes the inference
report hash; preserve this run's evidence before comparing future runs.

## Changed files and preservation

Code: Package.swift; package-only tool; FocusRingClassifier and Swift tests;
focus runtime/capture planner/new integration tests; shared dataset contract,
baseline and training preflight; legacy preflight test expectation updated.
Docs: launch plan, capture/runtime schemas, architecture note, BP-62, queue,
roadmap/catalog/current snapshot and this handoff/review/coordination.
No training run ID allocated; no ExperimentLog training entry required.

Preserved pre-existing Tasks/IterationRoadmap smoke updates and untracked
`reports/work/SIM-DATA-01-02/readiness-20260921-2252.md` and `smoke-20260921/`.
No unrelated worker files overwritten. SMB notice published/read back only for
the crop compatibility consequence; acknowledgment pending (see coordination.md).

## Independent outcomes and next action

- Software verified: passed for assigned offline scope, review-ready.
- Data eligible: not assessed; no genuine pilot/corpus accepted.
- Integration qualified: test-only producer-format → crop → CoreML path passed;
  genuine producer/native-focus path remains blocked.
- Model gate passed: not assessed. Shipped weights unchanged.

Next independent assignment: bounded PER-01/02/04 corrections in review.md.
Next data resume condition: matching updated TTR/Fixture deployed by an authorized
operator, fresh exact-target readiness, an authorized clean smoke with observed
frame-bound focus/geometry and healthy teardown, then byte-verified consumer intake.
Only after pilot baseline, reviewed ≥6,000-pair corpus and explicit training approval
can one candidate run. No automatic retry, training or promotion follows this handoff.
