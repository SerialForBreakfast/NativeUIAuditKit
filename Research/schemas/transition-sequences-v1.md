# Transition sequences v1 — PER-05

Offline experimental evaluator, not an action policy or production readiness guarantee.
No public library API, capture or model changes. Reuse FrameSimilarity and
ChangeRegionLocalizer through a package-only TransitionTool. Keep complete journeys,
related captures and identical decoded pixels within a partition. Test-only synthetic
sequences prove software only. Source metadata is reported, not authenticated.

## Input

`transition-sequences-v1`: `corpusID`, `sequences` (1–64). Each sequence has `id`,
`group` (whole journey/related recipe group), `partition` (development/validation/test),
`sourceKind` (test-only/simulator/physical), `sourceReference`, `labelOrigin`
(synthetic-generator/reviewed-human/fixture-callback), `reviewReference`, `scenario`
(static/crossfade/focus-animation/scroll/background-carousel), `startMs`,
`foregroundRegions` (1–8 fixed top-left pixel xywh rectangles selected independently
of future frames/truth), `regionOrigin` (caller-configured), and 1–64 `frames`.
Frames: `id`, `observationID`, `capturedMs`, `observedMs`, `focus`
(present/none/unknown), `truth` (ready/unstable/unknown), `path`, `sha256`,
`width`, `height`. Focus is a separately supplied observation, not the truth label;
its source is `focusSource` (test-only/independent-observation) on the sequence.
Optional explicit `missing: true` omits path/hash/dimensions; unknown outcome, never
successful empty capture. Undeclared missing/corrupt images reject the corpus.
Frames remain in arrival order, never sorted to conceal stale/out-of-order capture.
observedMs must increase. Capture reordering/repeated observation IDs invalidate
continuity at runtime. Paths resolve inside the manifest directory, no symlinks.
PNG ≤32 MiB, ≤16 million pixels, common dimensions within sequence. Input JSON ≤8 MiB.

## Frozen policy

Separate `transition-policy-v1` JSON with `reference`, `frozenOn`
(development/validation/test-only), `distanceThreshold`, `noiseThreshold` (0–255),
`stableMs`, `minimumFrames` (2–8), `maxGapMs`, `maxAgeMs`, `timeoutMs`,
`toolTimeoutSeconds` (1–120). No defaults inferred from test labels or fitting here.
All time budgets positive/finite; stableMs < timeoutMs. Thresholds experimental,
not calibrated by this packet. Real sources cannot use a test-only policy or focus.

Two comparable policies: full-frame feature-print stability and foreground change
region stability. Both require fresh independently observed focus. Keep at most
minimumFrames frames of causal history, preserving the current stable-run anchor
and newest frames. Compare current with **every** retained prior frame, reset to
current on visual change. This catches cumulative slow drift while allowing high
cadence to reach stableMs without unbounded history. Future changes remain unknown.
Ready requires minimumFrames, window duration ≥stableMs, and all comparisons stable.
ROI baseline rejects any changed component intersecting any foreground rectangle;
full-frame baseline requires every feature distance ≤distanceThreshold. Full-frame
distance and change boxes remain diagnostics, not model decisions or labels.

Missing/old/future/repeated/out-of-order captures and excessive cadence gaps reset
history; none/unknown focus abstains and resets history. At/after timeoutMs return
timeout (terminal for this sequence), never ready; a consumer starts a new episode
only under its own policy. Ready can be revoked on a subsequent frame. These are
observation-time deadlines, not host execution deadlines. Each helper request has
a separate wall-clock timeout and bounded pair count. The offline adapter measures
all past/current pairs (at most 2,016 per 64-frame sequence); online policy consumes
only its causal retained history. This is a benchmark, not a proposed all-pairs
live implementation. At EOF before deadline,
report incomplete/no-ready rather than fabricate timeout. No future frame/truth
is accessible to the decision function. No automatic retry on tool failure.
The localizer uses its production 480×270 analysis and specified noise threshold;
more than 128 change components is conservatively represented as full-frame change
to bound reply size. Luma differencing can miss isoluminant changes and caller ROIs
can omit safety-relevant pixels; neither limitation is a new trained-model claim.

## Reports and metrics

Versioned report binds corpus/policy/helper/evaluator/primitive source hashes and
host/runtime. Frame decisions include reason and supporting observation IDs.
Truth is joined only after prediction. Report premature-ready per unstable frame,
false waits per ready frame, unknown-truth readiness (unscored), abstentions,
sequence timeouts, missing/invalid observations, first-ready delay for each labeled
ready interval (null if never detected), support and scenario/source/partition slices.
Rates with zero support are null. Sequences—not independent frames—are sampling
units; no significance/generalization claim from synthetic support.

Record actual cold-process invocation latency separately from per-pair primitive
measurement p50/p95 (first/subsequent). These are offline host measurements, not
TTR end-to-end navigation latency. Timing varies; deterministic replay compares
decisions/metrics excluding timing. No learned temporal model recommendation until
eligible held-out complete journeys demonstrate a measurable baseline deficit.

## TTR proposal (not implemented in producer)

One episode/target/version-bound observation: observationID, captured/observed
timestamps, state (ready/wait/unknown/timeout), reason, supporting frame IDs,
policy hash, source kind, focus-source context, primitive evidence and freshness.
`ready` is only a visual candidate; never grants Select or replaces TTR route,
dialog, identity, safety or timeout policy. Caller-defined foreground regions may
miss unexpected overlays outside them; compare full-frame diagnostics and use
fresh whole-screen safety checks. No current producer wire schema change assumed.
Fake-backed producer adapter then separately authorized recorded/live comparison
are the next integration steps, not part of this offline assignment.

## Reproduce offline

Build `TransitionTool` with the repository's offline Swift build workflow. From
the package root, choose a **new** project-local fixture/output directory:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv-yolo/bin/python scripts/generate_transition_fixture.py \
  --output .build/debug-output/my-transition-fixture
PYTHONDONTWRITEBYTECODE=1 .venv-yolo/bin/python scripts/transition_benchmark.py \
  --manifest .build/debug-output/my-transition-fixture/manifest.json \
  --policy .build/debug-output/my-transition-fixture/policy.json \
  --output .build/debug-output/my-transition-fixture/report.json
PYTHONDONTWRITEBYTECODE=1 .venv-yolo/bin/python -m unittest discover \
  -s scripts -p 'test_transition_benchmark.py'
```

The evaluator resolves `.build/debug/TransitionTool` unless `--helper` supplies a
different project-local binary. It never builds/downloads implicitly. JSON/PNG
validation precedes measurement. Exit0 is a complete evaluation (not passing
quality gates); exit1 retains a partial report for primitive failures/timeouts;
exit2 is invalid input/output and does not replace an existing report. Identical
replay decisions/metrics are tested; host timing fields naturally differ.

Retained examples: [final report](../../reports/work/PER-05/benchmark-final.json)
and [handoff](../../reports/work/PER-05/handoff.md). Never use the illustrative
test-only policy thresholds as a production default.
