# Focus corpus generation readiness

**Decision:** automatic body annotations and production crops now work for delivered
artwork, configured buttons, rows, tabs and dialog actions. The full production
corpus is not yet assembled or qualified. TTR's new native-control repair arrived
during this tranche and passed unchanged consumer intake:16captured pairs across
six scenes,32frames and154/154crops. We no longer require that repair as future work.
The existing240training-pair target can now be prepared across all four families,
subject to actual recipe coverage and role binding; it is not production qualification.

**Latest delivery included:** palette/long-row follow-on also accepted: nine scenes,
26captured pairs,52frames,320/320production crops and174manifest members verified.
Across the three corrected body deliveries (including the earlier image delivery),
there are63captured pairs,126frame observations,77unique image files and624body
crops—not624independent examples. Four cross-recipe exact-image overlaps were
independently reproduced from local frame hashes and match the producer report.
See [palette QA](artifacts/palette-review/report.json) and
[visual scope](visual-acceptance.md). The release-readiness CLI report covers the
150image +154native-control observations; this later320crop report is its addendum.

Delivered `scripts/focus_generation_readiness.py`: joins the actual native body
batch, saved human revision, production crop receipts, retained baseline and exact
producer lineage/catalog. It outputs every candidate's disposition and all60
collection slots with verified recipe references; it never assigns roles or trains.

| Outcome | Evidence |
| --- | --- |
| Software |9new tests +25existing corpus tests pass; actual CLI replay passed; offline Swift build and120+14tests pass |
| Data |150candidate observations /81unique crop pixels;20individually human accepted;0exact retained pixel overlaps;0conflicting-focus crop hashes. No newly admitted training members |
| Integration |251lineage +195native-body +174palette archive member hashes verified unchanged;72recipes/30current/9current layout signatures; existing30recipe catalog/source hashes bind all60collection slots. New crops154+320 pass. No consumer live capture |
| Model gate | Not assessed; no inference, encoding, training or weights changed |

Use [generated readiness report](artifacts/release-readiness/readiness.md) and
[exact machine ledger](artifacts/release-readiness/readiness.json).
The earlier `artifacts/readiness` and `artifacts/final-readiness` reports are
superseded by `release-readiness`, adding the delivered native-body proof.
Source data and human edits
are unchanged. Bulky artifacts/logs are gitignored. No Git writes performed.

## What still has to happen

1. Resolve fresh **training** recipe/content membership before generation; preserve
   existing diagnostic and evaluation roles. Source/catalog matches are verified,
   but shared motifs/layouts and generated-manifest ancestry remain unresolved.
2. Qualify remaining artwork recipe combinations: contrast-neighbors, dense-grids,
   hero-neighbors, mixed-aspect light/high-contrast and selected-parent-child.
   High-contrast native controls and long/duplicate rows now pass delivered QA.
   Producer coverage represents16/30current recipes, not exhaustive target traversal.
   Keyboard and optional OCR remain separate lanes.
3. Generate the balanced wave through a bounded, exact-runtime campaign, not
   chat-per-control capture. Require actual variation, not repeated seeds.
4. Run existing intake/crop/random+exception QA, accept exact eligible members and
   connect native-body rows to existing training assembly/feature encoding.
5. Approve/run the changed-data comparison against preserved real development and
   retention sets. Broad production qualification still needs its coverage and
   independent/physical evaluation gates;240training targets are not those gates.

[Producer generation assignment](generation-assignment.md) specifies sources,
ownership, proposed bounds, partial/duplicate handling and acceptance; no new
runtime dispatch is implied. Exact receipt and scoped follow-up are recorded in
coordination.md. Human annotation is not the current blocker.

## Verification

The actual readiness CLI used SYN-06-BODY's `final-review/native-review/batch.json`,
saved human revision `20261001T060348Z-4076c5db`, its crop-QA receipt, the newly
received `source-lineage.json`, FOCUS-CORPUS-03's retained inventory and SYN-03's
verified semantic-proof-repair catalog/source root. Full invocation is in
`reproduce.sh` (offline reads plus new report output only).
Tests cover incomplete/duplicate crop membership, changed reviewed bounds/labels,
protected hashes, contradictory pixels, unknown/overlapping source roles, changed
recipe bytes, duplicate recipes and lineage-summary drift. No source eligibility
is inferred from a clean hash comparison. No model or capture was run.

The later palette QA is reproducible using the existing `fixture_batch_review.py`
CLI with each of the nine `coverage-export/splits/validation/*` bundle directories,
`--protected-metadata reports/work/APPEAR-B/protected-evidence.json`,
`--rendered-body --seed 42 --count 3 --exception-limit 1` and a new local output.
Use actual manifest roles; the directory name is producer diagnostic bookkeeping,
not independent validation admission. `fixture_offline_pipeline.geometry_review`
renders the resulting native-review batch. Retained receipts/report seals bind
the exact source members and output crop files.

**Next unblocked consumer tranche:** native-body-to-training assembly integration
with diagnostic/duplicate/protected-role rejection tests, dry-run only until exact
eligible data membership and experiment approval. No new annotation application,
OCR requirement, capture transport or repeated manual box tracing is needed.
