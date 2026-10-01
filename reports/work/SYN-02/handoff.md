# SYN-02 — semantic intake and source-catalog review

Offline implementation complete for review. TTR's new native inventory now passes
through the existing harvest importer instead of being silently ignored. The newer
eight-recipe catalog was received during this tranche and included in the review.

## Acceptance evidence

| Acceptance | Evidence |
| --- | --- |
| Named immutable receipt and safe extraction | `artifacts/received/receipt.json`, `artifacts/source-catalog/receipt.json`; three archives, all 36 listed member hashes verified |
| Exact producer examples through real CLI | `contract-verification.json`: six checks; valid/partial accepted, duplicate rejected; fabricated only |
| Integrated optional scene semantics | `scripts/fixture_semantic_inventory.py`, existing `harvest_sidecar_v2.py` and `harvest_bundle_validation.py`; raw inventories preserved in normalized observation bindings |
| Real caller tests and adversarial cases | 11 semantic tests: sidecar2/3, legacy, projection tolerance, unknown focus, bounds, accounting, hierarchy, exposure, changes/disappearance, alias conflict and downgrade guard |
| No legacy regression | 43 TTR contract tests, 12 bundle tests; three retained native pairs pass with all source files unchanged (`catalog-and-legacy-verification.json`) |
| Recipe coverage and source mapping | `source-catalog-review.json`: eight original recipe files and ten sources verified, all 60 slots/480 targets accounted; zero roles reserved; four mapping tests include missing/duplicate slots and changed identities |
| Offline repository checks | `swift-build.log`: success; `swift-test.log`: 120 Swift Testing +14 XCTest pass, using macOS service access and project-local caches |

The old four-family mapping is retained as `recipe-coverage.json`. It is superseded
where the newer exact catalog supplies original recipes. Recipe file bytes and
resolved capture recipe hashes remain different identities. No challenge images
were opened or scored; no models loaded or runs allocated.

## Outcomes and next action

- **Software:** verified optional inventory checks and source-catalog mapping.
- **Data:** zero new captured/admitted examples. Partial semantic coverage is not
  exhaustive annotation. Prior crop QA remains unchanged; no redundant crops generated.
- **Integration:** fabricated contract compatibility passed; current emitted-image
  proof remains pending TTR delivery. Source tests are not live runtime evidence.
- **Model:** unchanged; no training, export, gate pass or promotion.

Next useful work is importing the emitted pack into the existing audit/review flow,
then rendered crop acceptance and source-separated corpus reservation. No human
rectangle work is needed to complete the current source review. Producer findings
and exact receipts: [producer-response.md](producer-response.md).
Published to NUIAK's shared response and own SYN-02 status entry; readback and
preservation of other entries verified. Peer acknowledgment not yet observed.
See [coordination.md](coordination.md) for exact destinations.

## Reproduction

Run with `PYTHONDONTWRITEBYTECODE=1 .venv-yolo/bin/python`:

```text
-m unittest discover -s scripts -p test_fixture_semantic_inventory.py
-m unittest discover -s scripts -p test_fixture_recipe_coverage.py
-m unittest discover -s scripts -p test_ttr_*.py
-m unittest discover -s scripts -p test_harvest_bundle_validation.py
scripts/fixture_semantic_inventory.py --input <inventory.json> --output <new-project-report.json>
scripts/fixture_recipe_coverage.py --membership <syn04-membership.json> --catalog-root <received-root> --output <new-project-report.json>
```

Quote wildcard test patterns in a shell. Standalone report CLIs require an existing
project-local parent directory and refuse output collisions. `verify_contracts.py`
and `verify_catalog_and_legacy.py` retain exact receipt/example/replay procedures;
their fixed output names intentionally refuse overwriting this evidence.
