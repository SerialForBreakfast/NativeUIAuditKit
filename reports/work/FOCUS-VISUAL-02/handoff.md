# FOCUS-VISUAL-02 — Home appearance comparison

Completed for review, 2026-09-23 UTC. No capture, training, TTR operation or promotion.

## Evidence and findings

Reviewed seven existing Home-named PER-DATA screenshots before model inference.
Six contain reviewable Home focus; `office_home_top_right` is the app switcher and
is excluded. [Dispositions](dispositions.json) retain the reason. The immutable
[protocol](protocol.json) binds all source/review/model/runtime hashes. Original
PER-DATA evidence is unchanged. Unknown host/journey identity stays unknown; names
containing Office do not prove physical provenance.

Six frames, 72 fully visible tiles: six appearance-positive and 66 negative.
Dock-bottom fragments are excluded; blank placeholder artwork remains explicitly
represented. All six production contact sheets (72 crops) were visually inspected
in `.build/debug-output/focus-visual-02/`. Focused tile body bounds, enlargement,
neighbour context and labels agree with originals. These are manual appearance
labels, not native callback truth or detector localization measurements.

| Model | Positive recall at .85 | Negative false positives | Frame decisions at .85 |
|---|---|---|---|
| Shipped | 3/6 | 12/66 | 2 correct, 2 no-focus, 2 multiple-focus abstentions |
| FDR-007 FP16 | 0/6 | 0/66 | 6 no-focus |
| FDR-007 int8 | 0/6 | 0/66 | 6 no-focus |

Candidates' 91.7% tile accuracy is the all-negative baseline, not useful focus
selection. Shipped false positives occur in the full grids. Settings focus on the
dock is missed in both related frames. Preserve these correlated compositions as
development evidence, not six independent journeys or an untouched holdout.

Seven frozen box variants per tile produce 504 predictions/model (1,512 total),
not 504 new examples. Across the 36 non-base frame/variant decisions, shipped
has 8 correct/2 wrong/9 none/17 multiple; FP16 1/8/23/4; int8 1/5/25/5.
Maximum FP16/int8 probability drift is .052002 on base and .092529 across variants,
above the previously frozen .01 tolerance. One base sample crosses .70; ten
variant samples cross at least one fixed threshold. Base .85 decisions match;
variant decisions do not. Do not generalize the old 12-crop compression pass.

CPU helper inference warm medians are 1.304/1.307/1.309 ms (shipped/FP16/int8).
First prediction per process-batch medians are 4.533/4.305/4.268 ms; production
crop medians are 16.265/16.390/16.332 ms. Fourteen batches/model: first predictions
are excluded from warm summaries. These are not OS-cache-cold or navigation
latency benchmarks, and concurrent verification may affect timing. No speed win
established. Full workflow wall time was not instrumented; do not infer it from
per-item timings. There was no external producer wait.

Machine-readable [results](evaluation/report.json) and [summary](summary.json)
retain scores, confusion counts, decisions, latency, model identities and drift.

## Verification / acceptance

- `review.py`: six frames/72 boxes, source hashes/decoding and review validation pass.
- Real `focus_visual_comparison.py freeze` and `run` entrypoints: exit 0; frozen
  membership and artifacts validated before/after inference; unique outputs.
- `inspect_crops.py`: exit 0, all 72 production 16%-expanded 256px crops reviewed.
- Nine focused Python tests pass, including report support and non-Photos wording;
  existing negative-path tests retain corruption/collision/membership protection.
- Initial Swift build could not launch its nested manifest sandbox. Preserved
  failure log; scoped host execution succeeds: build exit 0, tests exit 0,
  14 XCTest and 93 Swift Testing tests. [Commands/times](host-verified/verification.json).
- Only shared comparison reporting changed; no cropper, model or library API change.
  Pre-existing iOS, producer-consumer, export and other worker changes preserved.

Outcomes: **software verified**; **data eligible for visual development inspection
only**, not training; **integration qualified only for this local CoreML/crop path**,
not TTR or live navigation; **model gates not passed/assessed as release gates**.
Coordination not applicable: no peer action changed, so no SMB noise. Existing
producer artifact request is preserved.

## Next bounded tranche

Implement OS-FOCUS-04 mixed-source assembly/preflight offline under its existing
canonical contract: immutable source membership, lineage/pixel separation, retention
of prior Settings data, source/style support, rejection of visual-only review data
as training, and actual trainer-preflight integration. No new trainer or run.
This can proceed without TTR or a new capture permission.

Before one subsequent training experiment, separately acquire and admit paired
Home tiles, Photos/button styles and qualified Fixture scenes with observed focus
and image/geometry agreement. Target Settings-dock misses, colorful/grid hard
negatives, placeholder tiles and focus enlargement; balance sources at training
time without treating repeated frames as independent. Preserve old Settings
validation as a forgetting diagnostic, and all existing Photos/Home cases as
development-only regression checks. Reserve new unrelated journeys/seeds for final
evaluation before capture; missing independent groups block qualification.

Freeze one mixed-style candidate protocol before launch: existing preprocessing
and baseline architecture, validation-only checkpoint selection, source-level recall,
false positives and unique/wrong/no/multiple-focus decisions, then separate export
parity on unsaturated examples. Thresholds and crop defaults remain unchanged.
Data eligibility and explicit training authority are prerequisites. Quotas and
six production gates remain intact; failed results do not trigger retraining.
