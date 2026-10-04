# CALIBRATION102 — genuine negatives expose remaining model failures

October3local / October4UTC. Frozen DTM024change +DTM020ranking, CPU, no training,
capture, Simulator, threshold change, export, promotion or Git writes. Existing
workers/dirty changes preserved. All40action pairs remain calibration-only.

| Condition | Pairs | Correct change | Both boxes correct | Joint correct |
|---|---:|---:|---:|---:|
| Boundary unchanged |12|12|2|2|
| Content-only change |12|0|2|0|
| Focus moved |16|16|0|0|
| Total |40|28|4|2|

No abstentions at the frozen0.85change confidence. All12content-only errors are
confident false changes; the successful identical-frame repair is not sufficient
for real changing-content negatives. No missed moves in this small correlated set.

Automatic proposals cover80/80native target endpoints. Ranking selects correct
boxes at IoU≥0.5on10/80;53of70wrong selections have less than half the target's
area,17do not,none exceed twice its area. This is descriptive, not permission for
a size cutoff. Best-positive rank ranges1–36;10endpoints' positive is rank2.
Dark endpoints10/40correct,light0/40. Both themes have6/6content-only false changes.
All40actions use sectioned collection layouts. The48appearance pairs stay outside
action replay; small_controls appearance coverage is not small-controls action proof.

## Integrated execution

- `evaluate_collection102.py --output .../proposal` verifies original receipts,
  hashes, native labels, geometry, observed condition and all40members; creates an
  unapproved proposal. Existing68/5roles are checked, original pixels rehashed.
  Zero decoded-pixel overlap with either existing split; same Fixture ancestry
  still prohibits claiming independence.
- Existing `prepare_proposal74.py --calibration-proposal .../proposal/proposal.json
  --probe .build/debug-output/proposal74/probe --output .../candidates` processes
  56distinct frames in2native batches,1,953image-only candidates.14.498s preparation.
  Reuses existing Vision/raster proposal mechanisms, no oracle boxes inserted.
- Existing production crop/derivative path produces256square crops with16percent
  expansion. Initial attempt populated caches then failed at a32MiB generic bound
  for the43MiB frozen73x6x128x192float32 parity tensor. Corrected to explicit64MiB
  plus exact shape/dtype/finite checks; preserved failure log. No capture repeated.
- Frozen replay validates original73change outputs within1e-6, then predicts new
  pairs before joining labels. Same production crop/ranking/encoder functions,
  fixed checkpoints and thresholds. Source/dependency/runtime/model hashes sealed.
- Final replay9.960s:56/56derivative cache hits,zero repeated native crop invocations.
  Distinct encode/crop/ranking/change timings retained; submillisecond resident
  change inference is NOT application latency and was warmed by parity.
- Missing candidates remain proposal misses; present-but-wrong selections remain
  ranking/geometry failures. Empty candidate sets never get truth boxes injected.

Commands use `.venv-yolo/bin/python`, `PYTHONPATH=scripts`,
`PYTHONDONTWRITEBYTECODE=1`. Outputs under `reports/work/CALIBRATION-102/`.
23focusedPython tests pass (collection102/native86/rank75/collection101),
offline Swift build and134tests pass. Logs `.build/calibration102-*`; failure
preserved in `calibration102-replay.log`, successful replay in `*-r2.log` and
`*-final.log`. Final Python-only provenance/empty-bank extension verified by real
replay; unchanged Swift evidence reused. No background jobs remain.

## Immutable evidence / role decision

Change checkpoint SHA256 `7a482e8b651f2b1354a4dd47f39fbcaa21fee4b0515ee0f56e0fa9d0ed0edf07`.
Ranker checkpoint SHA256 `3f90ba6bd8161c00057f36a307a205b3e03ba6801ef26e8974db652998184b75`.
Final report `replay-final/evaluation.json`,44081bytes,
SHA256 `eb4f6b3423a6dabe1860c095fbc0ca85dc36bb69a5caab06e9b03570af31a9cb`.
Proposal `proposal/proposal.json`,160783bytes,
SHA256 `86222943ee8bb0431ad5c31459c5b1955017f49e932fd4d3d2f44bcee7ee6c57`.
Exact member digest `28503f722f0e3ad6c245ea1b178f23fe22554c85116bd93f457b2aefe188fedb`.
Generated bulky records stay gitignored; compact evidence is retained here.

Requested decision: admit these40real action pairs (16moves,12boundary,
12content-only) into training,68→108real pairs; preserve5exposed Settings and keep
all renderer-related data out of final. Existing122training-derived self-pairs are
separate examples, not included in108. No admission or training approval fabricated.

## Next substantial tranche

After exact role approval: integrate admission with existing corpus/derivative
pipeline; run at most two justified fixed comparisons, genuine-negative change
adaptation and candidate-ranking coverage, preserving old68/5reporting and separate
new40reporting. Compare against these frozen outputs without claiming the newly
trained examples are unseen. Keep geometry/thresholds fixed in the change comparison
and fixed change scores in the ranker comparison; no automatic sweep. Log complete
configuration and initializer before launch under the standing training authority.
Failure yields diagnosis, not promotion. No additional capture required.

Priority parallel path: take TTR's actual shadow source/export when delivered,
validate four-record separation and replay the already-delivered FDR021 CPU observer.
Do not conflate that single-frame model with DTM024transition research. Shared
feedback asks for content-only negatives, fragment-vs-body mistakes and representative
successes; no repeat collection request or new producer feature asserted necessary.

Outcomes: software verified; data eligible for calibration only; offline model/
production-crop integration verified, live shadow not qualified; model improvement
and release gates not passed. Current models unchanged.
