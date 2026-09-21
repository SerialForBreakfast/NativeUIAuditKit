# FOCUS-CONSUMER — integrated offline handoff

2026-09-21. Base revision `e9d4260d751817770c4cfbc8fab1829686477618`.
Status: review. Contract: `Research/Plans/FocusRingConsumerReadiness.md`.

## Acceptance evidence

| Deliverable | Evidence |
|---|---|
| Byte-backed frame/crop validation | New `focus_dataset_contract.py`; corrupt/missing PNG, changed hash, forged crop, stale callback, untrusted labels, unsafe paths and source/version rejection tests |
| Group and hard-negative safety | Repeated seed within partition accepted; duplicate pairs and cross-partition content/groups rejected; actual-total theme quota and held-out unfocused support tests |
| Actual extraction integration | Real-format test-only bundle → extraction CLI → shared validator → baseline prepare → trainer preflight; missing review evidence fails; new destination required; membership published only after derived-byte validation |
| Candidate preflight | `focus_training_preflight.py` wired into actual trainer; no imports of Torch, cache creation or training in dry-run; fixed configuration/output collision checks; no silent missing-image skip or train-to-validation fallback |
| Evaluation isolation | No test loading/evaluation per epoch; development-only baseline protocol binds artifact/membership/preprocessing/implementation hashes; exact score membership, per-theme/control/family support and error reports |
| Crop geometry | Independent focused/unfocused boxes, 16% expansion, fractional origins and 256-square output; new Swift fractional-geometry regression |

The positive quota preflight fixture mocks quota validation to exercise launch
configuration on a tiny byte-backed corpus. Separate 6,000-row quota unit tests
mock PNG reading. The CLI integration validates real test PNGs and correctly
rejects their insufficient quota. None of these fixtures constitutes real data.

## Verification

Commands use `PYTHONDONTWRITEBYTECODE=1 .venv-yolo/bin/python` and retained logs
under `.build/debug-output/focus-consumer/`:

- `-m unittest discover -s scripts -p 'test_*focus*.py'`: exit 0, 31 tests.
- `-m unittest discover -s scripts -p 'test_harvest_bundle_validation.py'`: exit 0, 9 tests.
- `scripts/test_ingest_fixture_batch.py`: exit 0, all self-checks passed.
- `-m unittest discover -s scripts -p 'test_integrated_offline_toolchain.py'`: exit 0, 1 test.
- Offline `swift build`: exit 0; `swift test`: exit 0, 91 tests / 9 suites.

Swift used project-local TMPDIR, module cache, cache/config/security paths,
`--manifest-cache local --disable-automatic-resolution`. Initial sandbox build
failed `sandbox_apply: Operation not permitted`; approved host retry passed.
An initial unittest-discovery invocation for the standalone ingest self-test ran
zero tests/exit 5; rerun using its documented script entrypoint passed. A new
integer-seed check exposed extraction's string seed; corrected and rerun passed.
Swift package tests include existing bundled-model smoke inference; no training
or new model-quality benchmark was run.

## Changed scope and preservation

Added shared contract/preflight modules and integrated consumer tests; updated
harvest extraction, simulator grouping, readiness, trainer, baseline and their
focused tests; one Swift geometry test; architecture, contract/schema/catalog,
lessons, no-run log entry and this task row. No public API or producer wire edit.
Preserved pre-existing TTR skill/interface changes, Office plan/local-attempt,
other queue rows and SIM readiness reports. PER-04 files remain untouched.

## Independent outcomes and next action

- Software verified: passed for this offline tranche.
- Data eligible: not established; no genuine corpus accepted.
- Integration qualified: deterministic CLI path passed; genuine producer path blocked.
- Model gate passed: not assessed; shipped models unchanged.

Known remaining gates: TTR runtime/export readiness and observed frame-bound
ground-truth request; genuine pilot; actual Swift/CoreML crop comparison (Pillow
interpolation is not proven equivalent); reviewed full quotas and immutable
membership; explicit training authority. Supplied review/score metadata is not
authenticated execution evidence. Physical PER-04 and semantic alignment are
separate. Resume with one authorized genuine pilot after producer readiness;
then baseline, corpus scale-up and one separately authorized candidate. Do not
fabricate evidence fields or migrate old heuristic labels into approved data.

## Coordination

Verified `sillycon.local/SharedStatusFile` SMB mount; published only the consumer
interface consequence to `/Volumes/SharedStatusFile/nuiak/status.yaml`, own
`packets.FOCUS-CONSUMER` entry, and safely parsed/read back version-1 YAML.
Preserved other packets and existing requests. References the existing
`nuiak-20260921T213559Z-focus-ground-truth-contract` request rather than creating
a duplicate. Publication/readback passed; peer acknowledgment of this update is
not established. No runtime recheck or hardware action in this tranche.
