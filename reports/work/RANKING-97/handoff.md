# RANKING-97 — frozen ranking diagnosis and evaluation readiness

October 3, 2026; base 8b1f2f6, initially clean tree. No training, inference, capture,
data-role change, transfer or promotion. This completes the existing-score diagnosis
and independent evaluation-planning slice, not the full focus-reliability tranche.

## Findings

All 146 endpoint occurrences from NATIVE-87 were inspected numerically: 136 training
occurrences / 122 unique image hashes, 10 development occurrences / 9 unique hashes.
All training positives rank first. Five development occurrences rank second; these
are four distinct images, not five independent failures. The existing replay retains
per-occurrence scores and geometry; measurements below are derived without inference.

| Image | Occurrences | Selected region | Selected-minus-positive logit | Selected/positive area |
|---|---:|---|---:|---:|
| recorded-386 | 2 | 13.73×13.74 text-sized region, disjoint from focused row | 7.712399 | 0.003216 |
| recorded-391 | 1 | Same text-sized region, disjoint | 7.790432 | 0.003216 |
| recorded-409 | 1 | 8.44×12.67 text-sized region, disjoint | 5.223099 | 0.001864 |
| recorded-416 | 1 | 780×471 multi-row region | 0.526849 | 6.314575 |

Visual review of all four original images confirms the first two show VoiceOver
focused while the selected tiny region sits in the unfocused Voice row text. The
third selects a fragment in the unfocused Zoom row while Motion is focused. The
fourth selects a multi-row region while Audio Descriptions is focused. The larger
region intersects 93.01% of the positive candidate but only 14.73% of its own area;
it is not strict complete containment. These are observed associations, not a proven
causal attribution to any individual feature.

Positive-candidate largest extent across training is 666–3079.54px (median1524).
There are no sub100px positive candidates. More importantly, normalized positive
area spans 0.030651–0.096545 of the training image; Settings positives span
0.027663–0.029128. Training positive width spans0.1125–0.801963 and height
0.061111–0.494444, so some dimensions overlap even though area support does not.
Raw pixel comparisons alone mix1920×1080 and3840×2160 captures.

`focus_candidate_ranker.features` already appends normalized width/height to768
visual features for the active configuration. Simply adding size is not a new
hypothesis. Large logit margins are also not calibrated probabilities. Candidate
availability is sufficient on these examples; ranking is the immediate failure.

**Next testable hypothesis:** candidate-local appearance/scale does not adequately
distinguish complete focused controls from text fragments and multi-control regions.
Before a trained comparison, qualify small true controls and explicit fragment/
enclosing-region negatives, then predeclare a context/completeness comparison with
frozen proposals and change decisions. Score small positives separately so suppressing
all small regions cannot look like improvement. No Settings-tuned cutoff, largest-box
rule, or repeat of rejected NATIVE89 paired-logit subtraction is justified. The current
training set cannot establish safety for small positive controls; this is the concrete
missing-coverage finding rather than authorization for a new architecture/run.

## Evidence and preservation

- Replay SHA256: `ab18aa53cb5b56b8e5ca364aca7e60ab63af4ca4942b36240f8c0191d698e93f`.
- Corpus SHA256: `77321aab605746b924eab84395d1c79edb0bd8b39bc3836c6ad6d38435cbd6f4`.
- Frozen result reference independently SHA-verified against replay.
- All131 unique image byte hashes reverified:126 project-local,5 at the documented
  STORAGE-LIVE-01 SSD mirror. Direct shell paths initially missed the migrated files;
  no data were lost or restored. Use the existing storage resolver for execution.
- Compact machine-readable measurements: [measurements.json](measurements.json).
- Source scores: `reports/work/NATIVE-87/replay.json`; source membership:
  `reports/work/NATIVE-87/admitted/corpus.json`. Originals remain untouched.

Companion completed: EVAL90 now specifies prospective Home validation, Photos final,
and Settings development branches with action/label/role prerequisites. None are
actual reservations. TTR status read from verified SMB at02:55UTC: context60 producer
reports24appearance/12boundary/12content-only/12scrolling pairs, source v16/v17 still
unpublished locally. Layout28 receipt acknowledged and sender shared copy removed.
No new peer request is needed: source publication remains the existing next action.
No shared-status write or artifact receipt is claimed for context60.

## Verification and remaining work

Read-only Python aggregation/hash checks exit0; four original frames reviewed.
Documentation/JSON-only changes: JSON parsing and diff/link review, no redundant
Swift build or training. Software unchanged; existing data roles unchanged; fresh
producer integration not assessed; model gates not assessed. Elapsed capture,
training and external wait time: zero; interactive review was not benchmarked.

False-change training still needs the explicit122derived-negative role decision.
Source-backed v16/v17 intake requires published source available locally. Final
evaluation requires actual independent sources, capture scope and reviewed roles.
Next substantial tranche: approved false-change comparison plus source-backed
context60/layout28 intake and small-control coverage audit. Preserve frozen references
and development separation; do not spend another run merely increasing resolution.
