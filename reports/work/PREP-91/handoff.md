# PREP-91 — preparation optimization and change-error review

Scope complete for review. Existing uncommitted NATIVE84–90 changes preserved.
No capture, training, role changes, external writes or historical seal rewrites.

## Software and timing

`focus_transition_learning.decoded_identity` returns dimensions and the historical
RGBA hash from one verified PNG decode. `decoded_hash` delegates; direct record
construction consumes both. New direct execution pins include this shared module.
No persistent cache, skipped source check or RGB/alpha conversion change.

Generated regressions cover exact RGBA hash including alpha, one open per endpoint,
changed source bytes, corrupt/non-PNG input and viewport mismatch. Commands:

```
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts .venv-yolo/bin/python -m unittest scripts.test_preparation_identity scripts.test_native86 scripts.test_native88 scripts.test_pair89
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts .venv-yolo/bin/python -m unittest scripts.test_focus_direct53 scripts.test_focus_transition_learning scripts.test_preparation_identity
```

Exit0:11 and29 tests respectively,36distinct tests (4overlap). Final focused rerun
4/4 after tightening the corrupt-image assertion. Offline Swift build/test exit0:
14XCTest+120SwiftTesting, logs `.build/prep91-{build,test}.log`. Diff check clean.

Real `collect(corpus['sources'])` exactly equals the retained NATIVE87 corpus,
all73records, both before and after. Corpus file SHA256:
`77321aab605746b924eab84395d1c79edb0bd8b39bc3836c6ad6d38435cbd6f4`.
Instrumented full collection36.952s before,36.746s after; these single observations
are noisy (the second overlaps Swift checks), not an established end-to-end gain.
Before profile: record construction11.959s; recorded-semantic inputs20.092s;
9177 source `checked` calls. Provenance traversal is a larger remaining cost.

Isolated146-endpoint benchmark, same retained refs, sequential single/legacy/single:
7.210s /11.879s /7.016s. Legacy performs the prior RGB decode followed by the same
RGBA identity check; optimized performs only the latter. About40%less stage time,
not40%less full preparation time. No new model inference or corpus writes.

## Independent companion: three remaining change misses

Inspected frozen NATIVE88 results and hash-verified transition-case telemetry.
All four rich-table p2 cases change `grid_cell_0_2` to `grid_cell_1_0`.

| Case | Changed probability | Focus-box displacement |
|---|---:|---:|
| compact dark |0.999452 (correct)|24px down|
| compact light |0.014503 (wrong)|24px down|
| wide dark |0.00003134 (wrong)|0px|
| wide light |0.00003606 (wrong)|0px|

Images3840×2160;24pixels is0.6pixels at the existing96pixel-wide encoding.
Wide boxes are identical despite different observed element IDs. This is evidence
of an identity-versus-position challenge, not proof that resolution alone causes
the failures. Compact dark succeeds with the same displacement. Do not relabel
these examples unchanged, tune thresholds on them, or treat action delivery alone
as truth. They remain admitted training examples, not independent evaluation.

## Outcomes and next substantial tranche

- Software verified; actual73-record reconstruction parity verified.
- Data eligibility unchanged:68train/5exposed development.
- Producer integration not reassessed; no device operation.
- Model gates not assessed; shipped artifacts unchanged.

Next combine a bounded change-head comparison on already admitted68/5membership
(preserve old44/no-op performance, compare the three p2misses without changing
labels) with invocation-scoped provenance reuse design. Profile the repeated
semantic/readiness traversal first; preserve byte verification and immutable input
contracts rather than introducing a stale path-only cache. Final cross-source
evaluation remains blocked on EVAL90 source/role/runtime prerequisites. New source
capture is not needed for the local comparison. SMB not applicable: these local
findings do not request a producer change or alter its next assigned action.
