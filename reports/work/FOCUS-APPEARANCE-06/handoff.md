# FOCUS-APPEARANCE-06 — composition intake and appearance coverage

Status: completed for review, October 1, 2026. Intake, production crop QA,
coverage audit and six prefilled review frames are complete. Human acceptance and
training admission are not claimed.

## Verified delivery and scope

Received the named D1 archive (1,049,944,976 bytes,
SHA256 `4c22a0da19b2037deee66ad61145c37b81a3478c546cf64422d9a986b7854159`)
and earlier composition-contract archive (490,739,584 bytes,
SHA256 `de690ec755f9574ea76497f2aa9218ce6c9b7a0459617af36599276892c343c2`).
Existing safe receiver rejected unsafe paths, links, duplicates and size overflows;
864/194 entries expanded to1,182,510,132/517,013,789 bytes respectively, with local
disk reserve checked. Originals remain immutable. No producer source was executed.
Receipt publication/readback is distinct from semantic intake and sender cleanup.
Final audit reverified all807 D1 and160 contract-archive manifest members by size
and hash, with no unlisted files. Earlier contract examples were not crop-qualified.

## Results and acceptance map

| Deliverable | Observable result |
| --- | --- |
| Native intake | All3 layout bundles accepted for diagnostic QA;26 matched pairs each |
| Production crop QA | 156 frame records ×26 controls =4,056/4,056 crops;78 target pairs |
| Exact capacity | 30 artwork,30 buttons,12 rows,6 tabs; producer recipe hashes and target membership match |
| Geometry | All30 artwork pairs retain measured enlargement: approximately10–16% width and10–16.24% height before production resizing |
| Exclusions | Per layout52 decorative scene observations and2,600 semantic child records explicitly accounted; none silently promoted into controls |
| Sampling | Per layout52 frame records,25 duplicate aliases excluded,27 eligible;2 random frames, seed42. Six prefilled frames total |
| Source role | Calibration preserved, common procedural ancestry; neither training admission nor independent evaluation eligibility |
| Software | 132 focused Python tests, offline Swift build and134 Swift tests pass |

The4,056 crops are repeated scene/control observations, **not4,056 independent
training examples**. Full evidence, exact sample IDs, recipe styles, exclusions and
hash references: [coverage.json](artifacts/coverage.json). The exact replay is
[audit.py](audit.py), run with `PYTHONPATH=scripts .venv-yolo/bin/python`.
It intentionally refuses to overwrite its existing report; select a fresh
project-local report destination in the replay before running it again.
[Six-frame review](review.md) contains the existing-editor launch commands.
Agent visual inspection of the first consumer overlay confirms visible enlargement
and the selected-but-unfocused parent tab are represented; this is not human approval.

## Consumer fixes implemented

- Closed composition-v1 recipe decoder validates references, budgets, layout
  containment, no region overlap, supported component/effect combinations, selected
  tabs, and producer canonical hashes. Native hierarchy is checked against resolved
  IDs; design rectangles are never substituted for measured body annotations.
- Complete declared semantic inventories require the exact controls, region and
  background identities, no truncation/exclusions, and matching focus/parent evidence.
  Native versus declared parent relationships remain distinct. This does not prove
  pixel-level occlusion or complete accessibility coverage.
- The native-review lane supports512MiB aggregate bundles; other harvest callers
  retain256MiB and every file remains bounded to32MiB. Budget excess now reports
  `bundle_size_limit`, not the misleading `integrity_failed`.
- Native `menuButton` composition tabs map to the existing diagnostic
  `focus:tabItem` annotation role. Producer taxonomy is retained. No detector class
  was added. The initial projection omitted these tabs; it is superseded, not a
  complete-focus review or admitted corpus.
- Review preparation is per layout, avoiding the combined11MiB manifest exceeding
  the ordinary8MiB annotation reader. No global reader limit was raised. Crop item
  construction verifies each frame hash once rather than once per control; the
  production runtime still validates its own inputs.

The final outputs use `artifacts/final-*`. Initial `initial-qa`, `qa` and `qa-*`
outputs are retained failure/superseded evidence and must not be used for admission.
The received contract's source supports the additive fields; no speculative schema
or altered source bytes were needed.

## Coverage decision and next assignment

D1 is a useful **alternative composition corpus**, not automatic completion of the
original78 style-specific collection slots. It declares30 artwork targets,6 tabs,
12 rows and30 buttons across three layouts; these names/counts alone do not bind
the original missing styles. All share `fixture_procedural_renderer_v1` ancestry
with existing training data. Producer calibration roles remain unchanged; do not
split siblings into an allegedly independent test set or silently admit them.

**Appearance gap remains open:** the retained descriptive white-body rule finds
0/1,530 unfocused artwork observations and0/30 focused artwork observations in D1.
There are92 distinct unfocused artwork crop-file hashes and30 focused hashes;
repeat observations must not inflate coverage. All artwork uses city/orbit/collage/
checkerboard procedural designs, not the requested white logo/blank tile bodies.
White focused buttons/rows/tabs are present, but are not substitutes for white
unfocused artwork. The pixel rule is descriptive, not a qualification threshold
or proof of the model's causal failure.

Producer common-window crops use the union of the two rendered bodies. We retain
them as descriptive paired-growth evidence; they do not replace the production
per-frame16%-expanded256×256 path or justify a preprocessing change.

The next producer proposal should target **actual artwork appearance**: mostly-white
and pale tile bodies with owned/original logos or icons, plus white blank placeholders,
each focused and unfocused with the same content/layout and visible competitors.
Use dark/light surrounding backgrounds without making the focus label predictable
from content. Native and custom focus should be separately identified. Existing
`blank_placeholder` source draws gray (`0x666666`), and `bright_unfocused` draws beige;
their names do not prove white-artwork coverage. Require a source/pixel inventory,
measured bodies and observed focus, not another undifferentiated large delivery.

A bounded follow-up proposal could target24 distinct artwork identities across two
surroundings (48 matched pairs), explicitly a **collection target, not a quality
gate or dispatch approval**. Choose exact quantities after the producer shows which
existing recipes/assets can supply those appearances. Keep source groups separate
from reserved real-world evaluation; no threshold relaxation. A matched data-only
experiment follows source-role/sample acceptance and exact admission, not this intake.

## Verification

132 focused Python tests passed; offline Swift build and14 XCTest+120 Swift Testing
tests passed. Cases include real generated intake/crop caller, tab preservation,
unsupported fields/versions/effects/references, changed hashes, over-budget rejection,
incomplete native inventory, wrong parents and protected data rejection.
Logs: `tests-final.log`, `swift-build.log`, `swift-test.log`.
One retained native-batch validation profiled at8.129seconds; repeated decoding is
the largest component. This is local diagnostic timing, not an annotation UI SLA.
No inference, training, encoding, model promotion, new capture or source admission.
FDR021 remains unchanged.

Software outcome: passed. Data outcome: diagnostic-compatible, unadmitted.
Integration outcome: existing archive→native importer→production crops→review queue
verified for D1, not a new live TTR runtime qualification. Model gate: not assessed.
The next useful producer action is a targeted appearance proposal under the existing
representative-results request; there is no reason to recapture D1 geometry or ask
the human to redraw these4,056 observations. Sample review is available but does not
block that producer proposal.

Shared receipt and final packet publication/readback verified; peer acknowledgment
not observed. Exact destinations and preservation check: [coordination](coordination.md).
