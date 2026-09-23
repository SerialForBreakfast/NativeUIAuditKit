# Corrected producer focus replay

2026-09-23. Scope complete for review. No capture, simulator control, training,
producer edits, candidate promotion or model replacement.

## Acceptance evidence

- Actual TTR `FocusDetectorService.focusPatch` and scorer compiled from local
  revision `0e43ab369f7a1fae548e99274c8b7b0e822e325f`; scorer SHA256
  `512ea619f1f1e1def9e424941b1eec458f1b0e4fd2f05203d200f261bc3abd97`.
- Four hash-verified historical images and six synthetic probes: all ten crops
  decoded-pixel identical to production NUIAK cropping, including asymmetric,
  fractional, edge-clipped and color-boundary cases. Same CPU classifier scores
  identical on all ten. Preprocessing `ttr-focus-expanded-top-left-v3`.
- Same shipped model SHA256
  `9e5ba294e545b4ae0c54aa5d483b1a1f681b6c30477882700b4dbe139b9c66b7`.
  TTR `.all` versus NUIAK CPU maximum absolute probability difference 0.006226;
  no probability-0.85 decision changes. Repeated TTR results identical. No
  zero-error sentinel observed (edge probability zero has confidence one).
- Home now scores 1.0 on both paths. Settings 0.00709, fixture-tone 0.265625,
  fixture-record 0.00289 remain below threshold on NUIAK. Historical manually
  injected boxes are diagnostic evidence, not a new accuracy benchmark. Synthetic
  probe scores have no semantic label interpretation.
- `replay/report.json` records every source/model/input hash, score, compute mode
  and build scope. Runner exit0; reported replay elapsed3.669s (not entire Swift
  compilation wall time). `replay.log` retains command diagnostics.
- `tests.log`: seven focused tests pass, exit0,0.062s, covering declaration
  extraction, ambiguous/missing source, unsafe output/collision and real runtime
  batching integration. `swift-build.log`: exit0,2.96s; `swift-test.log`: offline
  package suite passed (14 XCTest +93 Swift Testing tests, latter2.489s).

## Integration and preservation

Updated existing replay and probe entrypoints, not a new cropper. Added six-probe
contract regression coverage. Existing prior replay and all other workers' dirty
changes preserved. Worker/model workflows kept source identity, runtime crop parity
and independent outcomes explicit. Scoped normal-host compile/CoreML cache authority
was used; configurable outputs remain in project. No external waits in replay.

Software verified: passed. Data eligible: not assessed/new training data absent.
Integration qualified: passed only for source-bound crop/scorer replay; OCR proposals,
app IPC and model-driven navigation excluded. Model gate passed: not assessed.

## Next action

Close the original preprocessing mismatch request with this bounded consumer evidence.
Continue APPEAR-C independent appearance-family intake: peer reports newer source
on Sillycon, but local checkout still has original three-preset contract and lacks
`Docs/Testing/2026-09-22-independent-appearance-families.md`. Request exact schema,
allowed values, family derivation, hash vectors and source/build identities before
consumer changes or purported holdout capture. Earlier ten-pair delivery is resolved.
No automatic capture/training follows publication. See coordination.md for readback.
