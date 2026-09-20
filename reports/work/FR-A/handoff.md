# FR-A review-and-remediation handoff — FocusRing readiness

**State:** Review-ready; architect acceptance pending.
**Scope:** FR-A, including ADR-0007's offline FocusRing alignment-contract amendment.
**Date:** 2026-09-19.

## Outcome separation

| Outcome | Result | Evidence |
|---|---|---|
| Software verified | Passed | The readiness CLI and unit tests validate quotas, pair/split integrity, 16%-expanded 256×256 crop geometry, and every ADR-0007 alignment matrix row. |
| Data eligible | Failed / not established | No new FocusRing corpus was captured; existing v0.1 data remains dark-only and lacks the required hard-negative/alignment coverage. |
| Integration qualified | Not assessed | The additive producer metadata contract is published for future fixture output, but no genuine TVTestRig output carrying it was received or validated. |
| Model gate passed | Not applicable | No training, evaluation, export, or bundled model replacement occurred. |

## Delivered behavior

- `scripts/focus_ring_readiness.py` now validates the ADR-0007 v1.0 envelope and fails closed on untrusted source, unsupported version, missing target, invalid expected relation, malformed `notAssessable`, or a missing required matrix row.
- `scripts/validate_focus_ring_readiness.py` is the actual no-side-effect manifest entry point. FR-B must invoke it with `--require-alignment-matrix` before accepting capture counts.
- `Research/schemas/focus-ring-alignment.v1.json` defines the additive, source-backed envelope. It keeps visual labels separate from alignment semantics.
- The matrix requires normal directional alignment, VoiceOver exploration, VoiceOver traversal, intentional fixture fault, and absent producer state. Exploration/traversal decoupling is an expected policy-negative control; no visual-model false positive or accessibility issue follows from it.
- `scripts/test_harvest_focus_pairs.py` verifies the existing crop implementation remains 16% per side, clamped, and resized to 256×256.

## Acceptance evidence

| Criterion | Result | Evidence |
|---|---|---|
| Pair/quota/theme/hard-negative validation | Passed | `scripts/test_focus_ring_readiness.py` validates the 6,000-pair recipe and rejects all existing required failures. |
| Seed split isolation and model-prediction labels | Passed | Same test suite rejects duplicate seeds and retains rejection of `modelPrediction` labels. |
| Source-backed ADR-0007 matrix | Passed | Same test suite validates all five rows and rejects guessed/untrusted sources, equal exploration targets, bad `notAssessable`, and absent matrix rows. |
| Crop geometry | Passed | `scripts/test_harvest_focus_pairs.py` asserts 16% expansion/clamping and 256×256 output. |
| Actual caller | Passed | `validate_focus_ring_readiness.py` normalizes `focus_dataset_manifest.json` pair shape and exposes `--require-alignment-matrix`. |
| Documentation and schema | Passed | `Research/FocusRingDetectorSpec.md`, `Research/Plans/ModelsAndHardware.md`, `Research/ADR-0007-VoiceOver-Navigation-Focus-Alignment.md`, and `Research/schemas/focus-ring-alignment.v1.json`. |

## Commands

```text
PYTHONDONTWRITEBYTECODE=1 .venv-yolo/bin/python scripts/test_focus_ring_readiness.py  # 6 passed
PYTHONDONTWRITEBYTECODE=1 .venv-yolo/bin/python scripts/test_harvest_focus_pairs.py # 2 passed
swift build                                                                          # passed
swift test                                                                           # 14 XCTest + 90 Swift Testing passed
git diff --check                                                                     # passed
```

The first sandboxed Swift attempt could not write Xcode's normal clang module cache.
The required build/test was rerun through the approved scoped `swift` permission and passed;
no cache location or system configuration was changed.

## Remaining boundary and next action

FR-B remains blocked on separately authorized Office fixture capture. Before any capture
is accepted, TVTestRig must emit source-backed `alignment` metadata matching the v1.0
schema and NUIAK must run the readiness CLI against the prospective manifest. The existing
v0.1 corpus is not retroactively relabeled and does not satisfy the matrix.

No novel implementation mistake was discovered; `BestPractices.md` needs no update.
Coordination publication/readback is recorded in [`coordination.md`](coordination.md);
peer acknowledgment remains distinct from publication.
