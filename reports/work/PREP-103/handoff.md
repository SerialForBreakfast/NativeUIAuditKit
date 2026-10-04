# PREP103 — guarded admission and batched input reuse

October3local/October4UTC. Implemented both preparation and explicit-decision
admission entrypoints; no real admission, training, capture, export or promotion.
Code integrates into the existing corpus collector, encoders and production crop
cache. Existing dirty work preserved. No Git writes.

## Completed

- `prepare_collection103.py --proposal <CALIBRATION102proposal> --output <new>`
  prepares inputs only. New40pairs retain calibration labels; old68train/5development
  roles remain unchanged. No approval, training protocol or launch receipt emitted.
- `--decision <explicit matching decision>` is the separate admission path. It
  checks approval/version/reviewer/reference/exact member digest before source work
  or output creation; verifies source again; preserves old records, assignments,
  exclusions; applies the existing group/pixel leakage gate and exact108/5counts.
  This mode was tested on generated fixtures, not used to admit real data.
- Real preparation reuses73sealed192x128pair encodings and encodes40new pairs once.
  Combined tensor113x6x128x192float32,66,650,112payload bytes.187distinct-frame
  production crop derivative cache hits;zero misses/native invocations.
  Preparation26.211s, no model loaded. Explicit storage~80MiB, gitignored.
- Actual `focus_direct_transition.collect` with the new source key independently
  returned113records, old73prefix/exclusions unchanged, prepared IDs identical,
  `trainingEligible=false`. This verifies caller integration without a real-role change.

## Verification

19Python tests pass: collection103,collection102,native86,derived98.
Positive generated admission retains every old assignment. Missing/false/stale
approval, absent reviewer/reference, changed old records, development leakage and
output collision reject. Actual bad-decision entrypoint cannot invoke source
collection or create output. Missing proposal/invalid data also fail through existing
sealed-input validators. Tests are offline and use project-local temporary storage.

Offline Swift build and134tests pass. Logs `.build/prep103-tests.log`,
`prep103-swift-build.log`, `prep103-swift-test.log`; all exit0. Actual preparation
command log `.build/prep103-preparation.log`, exit0. No process remains running.
Final collector pin-list registration does not change the encoder; retained
preparation records its historical exact code hashes, while later experiment
protocols must freshly pin their actual implementation. No old model protocol is
silently resealed or rerun.

Artifacts under `reports/work/PREP-103/pending/`:

| File | Bytes | SHA256 |
|---|---:|---|
| preparation.json |18448|`4ef0b54a63fa79549afa426db94f6b563e0e25a646f3eb576042561449ecb704`|
| x.npy |66650240|`9b871b5258096581279d8737ee4f1df8e1719b1dbbb5fc8c2d36bbaf4b94416e`|
| derivatives/derivatives.json |928421|`62ead7f8ebdf45dd4f40e28cfaa5aeee633d236022d28b65a76082be95af550a`|

## Remaining gates and next tranche

The exact40pair role question is pending. Preparation is not an implicit yes.
After approval, use the existing admission entrypoint, verify108/5membership, and
bind the cached inputs to fresh model protocols. Finish two controlled comparisons:
change-only adaptation fromDTM024 with108real pairs plus existing122approved derived
negatives, then size-aware ranking adaptation fromDTM020 on178training/9development
frames. Fixed600epochs per comparison, existing encodings/thresholds, original/new/
exposed reports, no automatic sweep. Log actual experiment IDs/configs before launch;
no training-eligible protocol exists yet. Export/promotion remain separate gates.

Higher-priority shadow integration: TTR snapshot04:35:39Zreports25local validator
checks and96retained evidence-only intervals. Source remains uncommitted at that
snapshot; local consumer Git remains4f9273cc. Four-language-frame/three-interval
sample is explicitly not published, awaiting screenshot-data egress approval.
No transfer attempted or assumed authorized; no source archive/build requested.
Resume source-backed adapter work when exact Git revision and permitted immutable
export arrive. Existing observer/feedback response already asks for that handoff;
no duplicate request or status noise added for this local preparation.

Outcomes: software PASS; existing roles preserved/new training eligibility PENDING;
local preparation/collector integration PASS, live shadow NOT ASSESSED; model gate
NOT ASSESSED. Primary admission workflow and independent cache preparation both
finished; training, live consumer uptake and promotion are not claimed complete.
