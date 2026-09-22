# PER-05 — offline transition readiness

2026-09-22. Complete for review. Base `7d056eaaeac697b301f57b01d2380b4496530f88`.
Contract: [sequence/policy/report v1](../../../Research/schemas/transition-sequences-v1.md).

| Outcome | Evidence |
|---|---|
| Software verified | Pass: actual Swift primitives, Python CLI integration, adversarial tests, offline Swift build/test |
| Data eligible | Not established: nine generated test-only sequences; no supplied real journeys evaluated |
| Integration qualified | Offline executable boundary verified; producer/live TTR integration not assessed |
| Model gate passed | Not assessed; no learned model, training, capture or promotion |

## Delivered

- `Tools/TransitionTool/main.swift` and package executable target: production
  FrameSimilarity/ChangeRegionLocalizer measurements, hash-bound images, bounded
  inputs/components, isolated protocol output; no production API changes.
- `scripts/transition_benchmark.py`: strict versioned corpus/policy validation,
  whole-group and decoded-pixel split isolation, causal bounded anchor/recent-frame
  policy, independent full-frame/foreground comparison, failure accounting and
  per-source/scenario/partition metrics. Truth joins only after prediction.
- `scripts/generate_transition_fixture.py`: deterministic explicitly test-only
  replay corpus; no downloads/capture. Refuses existing output directories.
- `scripts/test_transition_benchmark.py`: 15 policy/contract/real-primitive tests.
- Canonical contract includes reproducible commands and TTR observation proposal.
  Plans/catalog/roadmap/queue and BP-64 updated. Existing files/dirty changes from
  PERCEPTION-INTAKE and the TTR smoke reports were preserved; no other workers used.

## Acceptance map

| Criterion | Evidence |
|---|---|
| Stable/unstable/unknown timing contract | Explicit arrival/capture times, cadence/freshness, labels and source context; separate frozen development policy |
| Existing primitives, not fake algorithm | Actual packaged Swift helper called by Python CLI and integration tests |
| Causal, bounded history | Prefix/future-truth independence, cumulative-drift and high-cadence anchor tests; at most minimumFrames policy history |
| Moving background vs foreground motion | Asymmetric bottom-right change test, crossfade/focus-animation/scroll fixtures; real primitive output |
| No focus, missing, stale, reorder, cadence | Policy tests reset/abstain; no false ready from missing observations |
| Deadline/memory/failure bounds | 64 sequences ×64 frames, ≤2,016 comparisons/sequence, two decoded images per comparison, capped change components, subprocess timeout with no retry; timeout injection test |
| Rates/delay/abstentions/support/latency | Versioned final report, null unsupported strata, per-reason counts, ready-interval delay, explicit cold-process and first/subsequent pair timing |
| Fail closed on artifact errors | Hash/dimension/path/version/provenance/leakage tests, real helper hash/dimension rejection, CLI collision preservation and partial-execution report |
| Determinism | Generator byte-identical manifests; repeat real-primitives decision/metric equality; timing excluded from replay equality |
| TTR handoff | Versioned observation proposal; producer retains action/timeout/safety policy; no live wire/API change asserted |

## Replayed results — not real-world quality

[Final report](benchmark-final.json): 9/9 sequences, 54 frame observations, no
execution failures. Both policies produced zero premature-ready decisions on
the **nine generated unstable frame labels only**. Unsupported physical/simulator
and test-partition strata have zero support and null rates.

For the animated-background case, foreground ROI becomes ready after200ms;
full-frame similarity never becomes ready during the six-frame sequence. Both
abstain on missing/unknown focus; the timeout fixture reaches its explicit deadline.
These are software demonstrations, not calibrated thresholds or a navigation win
on genuine held-out journeys. No temporal model is recommended from these examples.

The earlier `benchmark.json` is retained, bound to its earlier source hash. Use
`benchmark-final.json` for the final implementation. Fixture pixels/manifests stay
under `.build/debug-output/per05/replay-v1/` and can be regenerated with the checked-in
generator into a new directory. No corpus files are added to the package release.

## Verification

Final exits0:

- Offline `swift build`: `.build/debug-output/per05/build-final.log`, no warnings.
- `PYTHONDONTWRITEBYTECODE=1 .venv-yolo/bin/python -m unittest discover -s scripts -p 'test_transition_benchmark.py'`: **15 pass**, `tests-final2.log`.
- Same unittest discovery with `test_perception*.py`: **16 pass**, `perception-regression.log`.
- Offline `swift test`: **92 Swift Testing tests/9 suites plus14 XCTest tests**, `swift-tests-final.log`, no failures.
- Actual generator and CLI replay: `benchmark-final-cli.log`, complete report with implementation hashes verified.
- Final syntax/JSON/link/diff checks recorded at handoff.

Logs above are in `.build/debug-output/per05/`. Swift commands used
`--disable-automatic-resolution --manifest-cache local` and project-local
TMPDIR/cache/config/security/module-cache paths. Initial sandbox build failed at
sandbox_apply; approved identical host build passed. Restricted Vision tests failed
CVPixelBufferPool creation; identical host tests passed. Final timeout regression
exposed platform.platform()'s incidental subprocess lookup; removed it, reran all
15 tests and retained `tests-complete.log` failure evidence. No threshold weakened.

## Limitations and next work

Offline adapter precomputes all past/current pairs within a bounded sequence;
the decision function uses only past retained history. It is not the proposed
live all-pairs implementation. Luma change may miss isoluminant motion; feature
similarity can absorb subtle UI changes. Fixed caller-selected ROIs can omit
unexpected dialogs outside them. Focus observations are supplied evidence, not a
new focus detector. A ready candidate never authorizes Select or clears safety.

Next: review this contract/software, then a separately assigned producer fake-backed
adapter and eligible recorded-journey comparison before live use. TTR screenshot
output repair remains the FocusRing critical path; no capture retry occurred here.
If still blocked, PER-06 screen/row identity benchmarking is the next independent
software tranche after contract review. No automatic backlog sweep or monitoring.

Coordination: [publication record](coordination.md). Only the proposed consumer
observation interface is shared; local test progress is not a peer assignment.
All assigned offline implementation/integration/verification/handoff criteria are
covered; no background work or pending process remains.
