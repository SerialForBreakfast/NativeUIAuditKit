# PER-06 — screen/row identity under change

Status: implemented and verified, ready for architect review; not self-accepted.
Starting revision: `f9f3b876be165d6294533659ba8915c3691ec51a`; initial working tree clean.

## Independent outcomes

- Software verified: passed, including the real package anchor-matcher adapter.
- Data eligible: no; replay uses supplied synthetic observations, not a qualified capture corpus.
- Integration qualified: offline adapter verified; live TVTestRig integration not assessed.
- Model gate passed: not assessed. No capture, navigation, training, or promotion occurred.

## Delivered contract and implementation

[identity-benchmark-v1](../../../Research/schemas/identity-benchmark-v1.md) defines bounded,
versioned corpus/policy inputs, registered locale-specific screen references, row candidates,
abstention and route-invalidation evidence. `scripts/identity_benchmark.py` compares the
actual `TextAnchorVerifier` substring baseline with exact-title plus unique-row matching.
Mutable right-hand values are excluded; vertical movement does not redefine row identity.
Unknown, duplicate, stale, ambiguous, unsupported-locale and overlay observations fail closed.
Cached identity cannot choose a match, and candidate results never authorize navigation.

`Tools/AnchorTool/main.swift` calls the existing Swift matcher using supplied OCR observations.
The only library change makes that method package-accessible; its behavior and public API
are unchanged. `Package.swift` adds the diagnostic executable. The generator and Python tests
are new. Plans, packet catalog, roadmap, Tasks.md and BP-65 document the deliverable;
unrelated task states and existing runtime-blocker evidence remain preserved.

## Acceptance evidence

| Requirement | Evidence |
| --- | --- |
| Actual primitive integration; substring collision vs strict title | AnchorTool and test 1 |
| Values, scroll, hidden rows; no truth/split/cache leakage into decisions | Tests 2–3, 17 |
| Duplicate labels, ambiguous screens, geometry and confidence | Tests 4, 7 |
| Registered localization; unsupported locale abstention | Tests 5, 15 |
| Overlay, stale/future observations, failed recognition, changed epoch | Test 6 |
| Wrong-screen row scoring and unsupported slices | Test 8 |
| Versions, policy bounds, prediction labels and journey/content leakage | Tests 9–12 |
| CLI integration, deterministic fixture, collision rejection, bounded helper failure | Tests 13–16 |

Verification logs are under `.build/debug-output/per06/`:

- `tests-final2.log`: `PYTHONDONTWRITEBYTECODE=1 .venv-yolo/bin/python scripts/test_identity_benchmark.py`, exit 0, 17 tests, 0.547 s.
- `perception-regression.log`: existing perception suite, exit 0, 16 tests.
- `transition-regression.log`: adjacent transition suite using real Vision adapter, exit 0, 15 tests, 6.862 s.
- `build-host.log`: offline `swift build`, exit 0, no warnings, 3.73 s.
- `swift-tests.log`: offline `swift test`, exit 0, 92 Swift Testing tests plus 14 XCTest tests.

Swift commands used `--disable-automatic-resolution --manifest-cache local`, with
`--cache-path`, `--config-path`, `--security-path`, `TMPDIR` and module caches inside
this repository. Initial restricted build failed at `sandbox_apply` (`build.log`);
the approved host execution passed. No dependency downloads were required.

## Replay result and limits

[Final report](benchmark-final-v2.json), SHA-256
`02c094744aa376c7f5d1557d5adae827ae2014e33d1e0a5476caf2a5b735b894`.
All 15 cases evaluated, zero infrastructure failures, **one generated journey**.
The report binds corpus, policy, helper and implementation hashes; reproduction commands
are in the contract. Prior reports are retained as earlier source-bound trials.

- Anchor-only: 8/14 known-screen retrievals, one false match, 6/15 abstentions.
- Conservative: 7/14 known-screen retrievals, zero false matches, 8/15 abstentions.
- Conservative rows: 12/24 matchable rows correct, zero false row matches; 14/26 observed rows abstained.

This trades recall for caution; it is not evidence of general accuracy improvement.
Some known screens intentionally become unknown under freshness/locale/ambiguity gates.
Physical, simulator and held-out recorded-journey support remain zero. Latency measures
supplied-observation matching and adapter overhead, **not OCR, capture or navigation**.
No model was evaluated. Policy thresholds are test-only, not calibrated on real journeys.

Remaining limitations: registered locales only; left-label layout assumption; overlays must
be observed to trigger their gate; near-duplicate journeys still require curator review.
Descriptive provenance is not attestation. Unknown rows cannot establish a reusable route.
TTR resume logic and runtime cleanup are outside this consumer matcher.

## Handoff and next action

Review PER-06 alongside the delivered PER-02/04/05 tranches. If accepted, separately assign
a fake-backed TTR candidate/unknown adapter and evaluation on independently held-out recorded
journeys before relying on route reuse. This is a proposal, not a producer assignment.

The immediate training critical path remains the producer screenshot-output access repair,
then an authorized genuine smoke, intake, and shipped FocusRing baseline. This tranche does
not refresh runtime readiness or authorize another attempt. See [coordination](coordination.md)
for the limited cross-project interface publication and acknowledgment state.
