# Offline FocusRing capture-plan contract

Canonical implementation: `scripts/focus_capture_plan.py`. This is NUIAK planning
metadata, not a new TTR wire schema, capture command or execution authorization.

## Reviewed catalog → frozen plan

Catalog fields: `version: focus-recipe-catalog-v1`, `producerReference`,
`reviewReference`, `evidenceKind: test-only|source-reviewed`, `developmentSeeds`,
`seedGroups` (decimal seed string → related-group ID), optional `developmentGroups`
and `splitSalt`, and `recipes`. Each recipe entry contains the producer `recipe`
and `expectedTargets: [{id, type}]`. Example entry shape (illustrative, not qualified):

```json
{"recipe":{"schema_version":1,"archetype":"action_dialog","element_count":2,
 "theme":"high_contrast","density":"regular","seed":100,"step_index":0},
 "expectedTargets":[{"id":"REVIEW_PRODUCER_ID","type":"primaryButton"}]}
```

Supply exact source/observed target IDs and types; never turn element_count into
an assumed pair count. TTR 562bd3a's source bounds are encoded explicitly. Its grid
may disable seeded cells and its hero uses a fixed button layout; generated labels
do not necessarily supply every required hard-negative type. The test catalog is
deliberately test-only, not a dispatchable or quota-qualified TTR catalog. A real
catalog still needs producer enumeration and pilot reconciliation. Unknown names,
development-group overlap, duplicate recipes/targets and unsupported limits fail.

Require at least ten related groups, in multiples of ten, for exact 80/10/10 group
allocation. All families/themes/variants of each group stay together. Exclude pilot
groups before freezing. Stable hash ordering plus splitSalt assigns partitions;
never change salt or groups to move already captured examples. Batches preserve whole
groups, contain ≤100 recipes and declare 600-second limits; oversized groups fail.
No executable capture instructions are emitted.

```sh
.venv-yolo/bin/python scripts/focus_capture_plan.py \
  --catalog reports/focus-reviewed-catalog.json --output reports/focus-plan.json
```

The plan binds canonical catalog and plan hashes, normalized/original recipes,
expected targets, frozen partitions, batch IDs, planned quota/theme/negative gaps.
These counts are expectations, never verified captured pairs. The six scene minima,
actual-denominator 20% theme shares, and all four held-out negative strata remain
unchanged. `captureAuthorized` and `trainingEligible` are always false.

## Completion ledger → resume report

Ledger fields: `version: focus-capture-ledger-v1`, `planSHA256`, `attempts`.
Each attempt has `batchID`, `state`, `cleanup`; only `completed` plus `clear` can
be counted. Also require `receiptSHA256` and one `recipes` entry for each batch
member. Each member contains `recipeID`, frozen `split`, `acceptedPairs` and
`rejectedTargetIDs`. Accepted pairs require `pairID`, `targetID`, `labelSource:
fixtureCallback`, `unfocusedVerified: true`, `focusedSHA256`, `unfocusedSHA256`.
Every expected target occurs exactly once as accepted or rejected. The hashes and
callback claims must subsequently be verified against real intake bytes/telemetry.

```sh
.venv-yolo/bin/python scripts/focus_capture_plan.py \
  --plan reports/focus-plan.json --ledger reports/focus-ledger.json \
  --output reports/focus-resume-report.json
```

Changed plans, split drift, repeated attempts/pairs, duplicate pair content and
cross-partition image hashes fail. Partial/failed/unknown-cleanup attempts block
all automatic resumption. Review them before creating any separately approved
recovery plan; this tool does not retry. Completed rejected targets remain deficits,
not silently recaptured or moved between partitions. Only never-attempted batches
are listed as resumable after all recorded cleanup is clear. Accepted coverage is
still ledger evidence, not byte validation or corpus approval. Outputs never overwrite.
