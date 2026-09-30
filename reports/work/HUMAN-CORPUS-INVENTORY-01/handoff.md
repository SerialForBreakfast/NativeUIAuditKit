# Human corpus inventory — 2026-09-30

Recommendation: prepare explicit admission of the **whole eight-screen supplement
session**, then compare the existing eligible baseline with that baseline plus its
138 reviewed focus controls. No more annotation is needed for this experiment.
This is a development experiment, not a production qualification or training approval.

## What exists

| Latest human batch | Frames | Reviewed controls | Existing selection | Excluded |
|---|---:|---:|---:|---:|
| Initial Office/Home/Photos | 8 | 113 | 113 | 0 |
| Office trial batch 1 | 8 | 82 | 49 | 33 |
| Office trial batch 2 | 8 | 89 | 87 | 2 |
| Office trial batch 3 | 8 | 78 | 66 | 12 |
| Real-app supplement | 8 | 155 | 138 | 17 |
| Total | 40 | 517 | 453 | 64 |

Seven human revision files reconcile to five latest revisions; two superseded
revisions and nine software-test revisions are not additional human data. Legacy
PER-DATA (39 cases) and FOCUS-VISUAL-02 (6 cases) are explicitly agent-reviewed,
not independent human confirmations. Discovery covers retained supported revision
formats under reports/work, excluding received archives; unsaved editor work and
unconfirmed batches are not counted as finished review.

There are 40 distinct full-frame pixel hashes and 515 distinct crop pixel hashes.
Two duplicate crop pairs in the first batch have consistent unfocused collectionItem
labels; preserve lineage but do not count them as independent examples. The 453
selection controls contain 35 focused and 418 unfocused examples: 273 artwork,
125 rows, 24 tabs, 10 buttons and 21 other. No excluded labels were silently repaired.
Watch Now remains unfocused and the first Top Stories card remains focused.

The original complete/settled frame policy supports 13 frames. The separately pinned
human Photos completeness amendment supports 14. Historical 13-frame scores remain
unchanged; unknown completeness never becomes unique-focus accuracy.

## Relationships and actual previous use

Three recording sessions form two conservative connected groups: 32 frames linked
by session/known screen family, and the eight-frame supplement. Same-source frames,
crops and descendants must stay together. Eight near-frame matches from 21,220
comparisons all lie inside the 32-frame group. Method: full-frame RGB resized to
64×36 bilinearly, mean absolute difference at most 2/255. This detects near-identical
screens, not reused artwork at a different scale or a complete semantic relationship.
No cross-group near match at this cutoff is **not** proof of independence.

No exact human frame/crop overlap was found against the current 790 training and
18 retention crops. Protected-evidence metadata has no exact match. The broader
reserved-pixels inventory matches all 517 human controls, as expected: it includes
these existing development reservations. Reassignment therefore needs an explicit
versioned reservation amendment, not removal of a leakage check. Protected challenge
pixels were not opened, scored or mined; protected references remain unchanged.

FDR-015 and FDR-016 protocols each contain 726 training crops (363 pairs), including
80 nativeAX capture-interval crops (40 native Settings pairs). Their 453 human
controls were selection, not gradient-training members. The current additive
assembly contains 790 training crops (395 pairs), still including those 40 native
pairs, plus nine retention pairs. It has not itself been executed. Calling either
baseline “synthetic-only” would be wrong. Earlier-run ancestry beyond these pinned
protocols is not exhaustively reconstructed; no broader claim is made.

## Exact proposed roles, not admission

`final-results/membership-proposal.json` lists every ID. Default remains development.
The conditional alternative moves all eight frames of the supplement session
E93B12DA-9358-4FD6-91F2-1B42AD8C9329 together: recorded-479, 572, 614, 653, 742,
771, 839 and 875. Its 138 eligible controls comprise 8 focused/130 unfocused,
80 artwork/54 rows/4 buttons. Its 17 auxiliary controls remain excluded.
The other 315 selection controls on 32 frames remain development-only; the other
47 exclusions remain held. All source-session neighbors and derivatives inherit
the proposed training reservation, even when not listed for actual optimization.

No genuinely untouched human real-world test set exists here. The proposed
development group is already repeatedly evaluated and includes familiar OS families.
Artwork asset ancestry across apps/synthetic sources remains unknown. Neither
proposal nor absence of exact overlap establishes an independent transfer result.

Eligibility differs by task:

- Static focus: 453 existing reviewed selection controls; 138 are proposed for a
  separate human-label training lane. Existing native-pair admission cannot be bypassed.
- UI detection: not an exhaustive detector corpus. Auxiliary labels, unmapped focus
  roles, clipped competitors and incomplete screens prohibit blanket detector admission.
- Transition/pair learning: static human boxes do not prove ordered transitions,
  native focus identity or command success. Do not fabricate pairs from these crops.

## Bounded comparison proposal

This requires separate approval and implementation of human-label admission, not
another unchanged run. Freeze the exact 395-pair baseline for both arms; keep the
nine retention pairs and the remaining 315-control development membership identical.
Arm A uses the baseline; arm B adds the 138 static human controls. Do not compare
against historical 453-control scores as if the corpus were unchanged.

Use the same pinned ImageNet MobileNetV3-small frozen representation, normalization,
fresh linear-head initialization and optimizer, seed 42, learning rate 0.0003,
30 epochs maximum and 1,800-second cap per arm. Preserve original production crops
and threshold 0.85. Both arms use the same BCE and genuine-pair auxiliary loss;
human crops receive BCE only, never an invented pair loss. Keep native pair draws
identical; use an equal-size auxiliary slot schedule in both arms, baseline examples
in A and reviewed human examples in B, normalizing the two slots to 80%/20% loss mass.
This isolates replacement of the auxiliary examples, not additional compute.

Proposed auxiliary schedule: all 138 human crops once per epoch, fixed seeded order,
no within-epoch repeats, with each of the eight frames receiving equal total loss
weight. Apply the same slot weights and crop-forward count to A. Limit every human
crop to 30 lifetime presentations and its single session to 20% total loss mass;
do not oversample its eight positives. Baseline sampling remains the frozen assembly's
declared distribution. These are experiment controls, not qualification thresholds.
If a time cap truncates an arm, compare the common completed update budget and
report truncation; do not claim matched compute otherwise.

Keep the existing retention eligibility floor and minimum balanced development-BCE
checkpoint rule, earliest tie. No eligible epoch means no selected checkpoint.
Report false positives, misses, abstentions and recall by family/stratum, plus
unique/wrong/no/multiple focus only on the 14 complete settled frames. Show raw
denominators and per-family deltas. Family-cluster resampling may describe sensitivity,
but two remaining sessions and one connected development group cannot support a
credible broad-population confidence interval. No final-challenge scoring or export.

## Verification and handoff

Reproduction: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts .venv-review/bin/python
scripts/human_corpus_inventory.py --output <fresh-project-local-directory>`.
The actual CLI verifies revision/crop seals, image and crop hashes, exact membership,
prior protocols and source preservation. Outputs contain exact references, hashes,
bounds, states, exclusions, source IDs, relationships and proposal membership.
The similarity screen deliberately does not load a model.

Focused inventory/audit tests: 15 pass, including ambiguous revisions, unconfirmed
reviews, software-test exclusion, transitive grouping, changed/missing crop inputs,
membership and deterministic source-preserving audit. Offline Swift build and all
123 Swift tests pass (14 XCTest + 109 Swift Testing). Logs are retained locally.

- Software: audit and proposal tooling verified.
- Data: inventory reconciled; diagnostic/development eligibility preserved, no new admission.
- Integration: TTR response is metadata-only; artwork live proof remains separate.
- Model: unassessed; no inference, training, promotion or model changes.

Next assignment: approve this whole-session role change, then implement the explicit
static-human admission and matched-schedule trainer preflight. Training launch remains
a separate decision. No new capture or repeat human labeling is needed for that work.
