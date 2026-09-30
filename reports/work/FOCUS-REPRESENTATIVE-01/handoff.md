# FOCUS-REPRESENTATIVE-01 — complete for review

2026-09-29. Representative validation and offline production-campaign readiness
delivered. **FDR-010 stays unexported; shipped unchanged.** No training, capture,
device operation or challenge scoring occurred.

## What changed our decision

New native-fixture comparison: candidate finds18/18 button/tab/row positives but
**0/32 artwork positives**, yielding18/50 unique-correct complete frames. Shipped
finds7/50 unique-correct, with4 wrong selections; candidate has32 no-focus frames.
On the retained real screens, candidate finds0/3 buttons,0/3 tabs,1/12 artwork and
2/7 rows. Synthetic success does not transfer. Therefore the next assignment is
matched artwork/effect/background/geometry collection and genuine OS transfer
coverage, not another unchanged training run or a large repetition of easy controls.

[Full metrics](report/metrics.md) separates pair classification, frame selection,
per-stratum support and real transfer. Missing/ambiguous coverage is not a zero
score or silently complete frame. Raw data and all original labels remain intact.

## Acceptance evidence

| Requirement | Observable evidence |
|---|---|
| Freeze before inference | `validation/protocol.json`, SHA256 `77f417eeb83598ca72a2103b52cbf5cc0e215fd8027a4925b93fd33f67df76d2`;312 exact IDs,50 pairs,50 complete frames, models/runtime/code/source hashes |
| New fixed comparison | `validation/comparison/{shipped,fdr010,comparison}.json`;312/312 each,0 failures; original bounds,0.85, production16%/256 crops; actual loaded identities in receipts |
| Reuse compatible real results | `real-transfer.json`: four retained benchmarks,32 reviewed frames,362 scores per model;315 supported settled candidate crops,47 excluded from that population; original metric reproduction exact |
| Repeatable metrics/errors | `scripts/focus_representative_report.py`, `report.log`; exact recomputation of both paired/complete-frame metrics; deterministic `report/errors.json` with92 shipped/64 candidate error entries across the two correlated populations |
| Candidate corpus inventory | `campaign/campaign.json`:313train+9retention originals/crops byte and decoded hashes checked;273 canonical scene pairs+40 genuine Settings; membership/sampling/selection preserved |
| Next selection contract | `report/next-selection.json`: sealed proposal, source-balanced four-stratum selection, retained18/18 floor; needs separate approval, not an implemented trainer change |
| Production collection spec | `scripts/focus_production_campaign.py`,696 exact source-hashed recipes,5727 canonical additional target pairs; `production-assignment.md` ranks96-pair matched contrast target, genuine transfer coverage, then volume |
| Coverage/roles | Exact existing member reservations, ten unchanged independent appearance gaps, legacy1500 metadata inventory with0 newly admitted; protected challenge untouched |
| Verification |70 focused Python tests; offline Swift build,14 XCTest+109 Swift Testing tests pass; `focused-tests-final.log`, `swift-build.log`, `swift-test.log` |
| Producer handoff | Sanitized `ttr-response.yaml` answers current `tvtestrig-20260929-focus-corpus-production`; publication/readback is recorded in `coordination.md` |

The production scheduler uses the retained afc948ca source-defined archetype recipe
contract; it does **not** claim the newer ccc2d3a6 build is integrated or its runtime
qualified. Existing artifacts remain diagnostic; the full production corpus has
**not** been collected or admitted. The scheduling envelope is not a corpus-quality
pass and does not satisfy the missing photographic/source-independence requirements.

## Four separate outcomes

- **Software:** implemented and verified CLI preparation/inference/reuse/reporting
  plus offline corpus planner; no public API, taxonomy or evaluator policy changes.
- **Data:**50 synthetic diagnostic pairs and32 real reviewed frames represented;
  existing313+9 preserved. Full production eligibility/independent coverage not met.
- **Integration:** actual retained producer evidence consumed with production crops;
  failure and preprocessing feedback prepared for TTR. New producer code and live
  capture qualification are separate, not claimed by offline checks.
- **Model:** FDR-010 unsuitable for export/testing promotion. New data shows narrower
  synthetic strengths, not broader qualification. No new run allocated.

## Exact next action / remaining gates

TTR can use the delivered IDs/hashes and crop contract now to reconcile native-image
versus native-button behavior and revise its held matrix. NUIAK can recover legacy
source provenance and bind prospective asset/source roles without device access.
Capture resumes only with a source-bound revised recipe pack, exact target/runtime
and bounded exclusive window, and adequate capacity. Current33.4GiB free does not
cover estimated new data plus10GiB work reserve, before archive duplicates. No
destructive cleanup is authorized. See [assignment](production-assignment.md).

Training then needs the admitted corpus and separately approved representative
selection contract; no requirement to wait for a new model to collect or evaluate
data. TTR acknowledgment is not a blocker for this completed local tranche.

## Reproduction

Use the established resident `focus-export-01` Python3.12.9 environment, with
PYTHONDONTWRITEBYTECODE=1 and all caches/temp inside this project. Dependencies and
versions are frozen in the protocol. From repository root:

```sh
python scripts/focus_representative_report.py \
  --protocol reports/work/FOCUS-REPRESENTATIVE-01/validation/protocol.json \
  --comparison reports/work/FOCUS-REPRESENTATIVE-01/validation/comparison/comparison.json \
  --real reports/work/FOCUS-REPRESENTATIVE-01/real-transfer.json \
  --output reports/work/FOCUS-REPRESENTATIVE-01/report-replay
```

Replay consumes existing scores only; output must be new. `real-reuse` validates the
retained FDR-010 adapter/reference artifacts rather than silently rerunning models.
`prepare` binds the exact new synthetic population; `run` is separately authorized
model execution and its already-created one-run marker prevents accidental replay.
Campaign CLI requires explicit candidate/protocol/comparison/real/producer-contract
paths and a new output; its actual invocation and result are in `campaign.log` and
the six frozen `campaign.json` references (including code). No planner CLI dispatches
TTR or admits training data.
