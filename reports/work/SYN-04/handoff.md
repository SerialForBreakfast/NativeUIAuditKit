# SYN-04 — coverage-driven corpus planner

Completed for review: local planner, integrated retained audit, source-conflict tests,
collection requests and producer handoff. Actual recipe binding remains pending;
the planner does not fabricate it or dispatch capture.

| Outcome | Result |
| --- | --- |
| Software verified | Pass: CLI, deterministic requests, lineage graph, negative tests and retained input verification |
| Data eligible | No new admission; 1,319 retained crops/395 native pairs rechecked with unchanged membership |
| Integration qualified | Local inventory→planner path passed. Actual new TTR recipe binding not yet available |
| Model gate passed | Not assessed; no training, model experiment, threshold change or promotion |

## Delivered result

`scripts/focus_corpus_planner.py` extends the existing offline inventory workflow,
not the producer API or trainer. It produces machine-readable collection slots,
an actionable Markdown matrix and an empty lineage-catalog template. No automatic
generation or runtime dependency is introduced. [Usage/schema](usage.md).

Default first-wave collection targets, each spanning dark/light/highContrast:

| Priority | Family | Training pairs | Validation pairs | Requested structure |
| --- | --- | ---: | ---: | --- |
| 1 | Artwork | 96 | 96 | Mixed-aspect shelf, dense grid, hero/neighbors, placeholder/bright contrast |
| 2 | Tabs | 48 | 48 | Selected-parent/child, strip/content |
| 3 | Rows | 48 | 48 | Accessories, long labels/mixed widths |
| 4 | Buttons | 48 | 48 | Dialog actions, wide/compact controls |

480 proposed pairs across60 slots; a slot may use multiple actual recipes. Targets
are configurable, not new qualification gates or a claim of Fixture support.
The existing6,000-pair production requirement and all additional gates are unchanged.
This first wave is a coverage intervention, not a finished production corpus.

An optional consumer-local catalog binds exact recipe hashes and reviewed ancestry.
Unioned source/layout/component/asset, exact content, declared near-duplicate and
explicit member relationships are evaluated transitively. Conflicting or unknown
components are held together. Corrupt evidence cannot erase known relationship
bridges. Retention/protected/held examples cannot become new training reservations.
Matched24 remains validation, not a training fill source. Separate IDs alone never
produce an independence or admission claim. No perceptual similarity search occurs.

## Retained evidence and accounting

Actual output: `artifacts/verified-plan/plan.json` and `collection.md`.
Compact source/code reference receipt: `verification-final.json` (the initial
`verification.json` records the retained run before the additional prior-use guard).

- 986training,315development,18retention crops, all original roles preserved.
- 395 complete native pairs;28 exact duplicate-crop groups remain reported.
- 64held pairs and64excluded selection controls remain unchanged.
- 315 normalized samples lack source IDs; no independent-validation claim.
- 23 baseline relationship components,0 detected cross-role components; absence of
  detected overlap is not proof of independence.
- 355pairs occupy existing six scene buckets;40 keep settings/apps/general/root
  identities. No silent reclassification to reduce the5,645 arithmetic shortfall.
- Tab-looking primaryButtons remain their original labels. Earlier hash-bound
  producer recipe review identified12 tab/nested-tab pairs; explicit label coverage
  still differs from visual coverage. Selected-parent/hard-negative counts stay unknown.
- All60 new collection slots are unbound. No real recipe reservations have been
  established and no request counts are added to retained counts.

Protected/held comparison uses metadata; no protected challenge images viewed,
scored or selected. Pixel verification is confined to the retained development
protocol. No original labels, files, weights or source-role records were modified.

## Verification

| Criterion | Evidence |
| --- | --- |
| Real CLI and deterministic planning | `tests.log`:25 passed (13planner,12existing inventory) |
| Negative cases | Duplicate IDs, role drift, protected/held content, unknown ancestry, cross-role exact/near-duplicate/transitive links, corrupt bridge, changed image/hash/inventory, wrong catalog binding, output collision |
| Actual recipe-catalog path | Generated exact recipe/review references exercise complete CLI run; synthetic proof, not TTR qualification |
| Retained corpus run | `planner-verified.log`:60slots/480targets,0invented proposals; every baseline record and coverage count reproduced |
| Source preservation | References in `verification-final.json` rechecked; tests verify every fixture source byte unchanged |
| Offline build | `swift-build.log`:passed, no warnings |
| Full offline tests | `swift-test.log`:120Swift Testing +14XCTest passed |
| Diff hygiene | git diff --check passed; no Git writes |

Commands use `.venv-yolo/bin/python`, PYTHONDONTWRITEBYTECODE=1 and project-local
output. Swift uses `.build` cache/config/security/temp paths and CFFIXED_USER_HOME;
full tests requested scoped access for existing macOS Vision/CoreML service tests.
No new model experiment, capture, device control, encoding or crop generation ran.
Existing unrelated dirty work was preserved. Worker-execution guidance was used to
test actual callers and finish the integrated handoff, not add per-frame paperwork.

## Coordination and next step

[Producer request](producer-request.md) extends existing corpus-source-layout and
semantic-export requests. Published/read back on verified SharedStatusFile:
`nuiak/requests/nuiak-20261001-syn04-coverage.md` and own `packets.SYN-04` entry in
`nuiak/status.yaml`. Duplicate-key YAML validation passed; unrelated packets preserved.
Peer acknowledgment not observed. These are planning requests, not capture authority.

Next: receive exact producer recipes/ancestry with emitted semantic examples, map
supported coverage slots, review source reservations, then use the existing bounded
capture/intake/crop and random-plus-exception audit flow. Keyboard remains optional.
No further human rectangle annotation is needed to complete this planner assignment.
