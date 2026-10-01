# SYN-06-BODY — corrected geometry consumer handoff

## Result and limits

The consumer now maps TTR's measured rendered-body geometry into versioned v2
annotation proposals. Legacy v1 review batches retain their wrapper projection.
No public API, taxonomy, model weights, crop policy or training role changed.

- Delivery: `ttr-rendered-body-geometry-20261001-r1.tar.gz`,161357448bytes,
  SHA256 `8923781a65d128800148a998a6a1ef0460b4f76b830a5df236b3ce0acca7d09c`.
  All231listed members verified and rechecked unchanged after replay.
- Eight scene bundles /21original captured pairs /42original frames accepted for
  diagnostic intake.150measured body observations mapped;60unavailable observations
  retained as explicit exclusions/unresolved evidence. Two measured bodies clipped.
- Production crop QA:150/150 via the unchanged16%-expanded256×256 path.
  Twenty-one derived focus relationships are not additional captures.
- Original competitor: wrapper `[824,280,440,420]`, body `[784,242,520,496]`.
  Wrapper/full/visible/source/identity/generation retained; raw source not edited.
- Unsupported rows/dialog controls have no body proposals. Tab-artwork children
  are mapped, but parent button bodies remain unavailable; these are not complete
  frame training examples. No fallback geometry or focus inferred from selection.

## Visual QA (reviewer observations, not automated proof)

Inspected original-image overlays for native growth, custom scale-only, no-growth
border-only, mixed aspect cards, selected parent/focused artwork child and clipping,
plus the production256×256 crop of the originally reported focused competitor.
Observed body rectangles encompass the enlarged solid image and omit external
captions/shadows; no-growth geometry stays unchanged. Parent selection remains
separate from focus. Clipping examples overlap: do not interpret a clipped rectangle
as occlusion segmentation. Rounded/antialiased edges remain an enclosure, not a mask.

The first `artifacts/body-review` attempt predates the explicit clipped-body review
finding and is superseded. Use **`artifacts/final-review`** only for current review.
Original archives and prior human edits remain untouched.

## Reproduce

Use `.venv-yolo/bin/python scripts/fixture_batch_review.py --rendered-body`,
passing each of the eight `dataset-index.json` parent directories beneath
`artifacts/received/ttr-rendered-body-geometry-20261001-r1` as `--bundle`;
`--protected-metadata reports/work/APPEAR-B/protected-evidence.json`,
`--seed 42 --count 4 --exception-limit 2`, and a **new** project-local `--output`.
Existing output collisions deliberately reject. Then use
`fixture_offline_pipeline.geometry_review(batch_path, new_output)` for Markdown
side-by-side wrapper/body overlays. Producer executable scripts were not run.

## Acceptance and outcomes

| Criterion | Evidence / outcome |
| --- | --- |
| Exact delivery, originals preserved | `artifacts/received/receipt.json`;231member verification |
| Native-body schema and bracket integration | `fixture_rendered_body.py`, native sidecar validation; strict identity/geometry/moving checks |
| Legacy compatibility and no fallback | v1/v2 dispatch; absent bodies excluded; sealed reprojection checked |
| Real consumer entrypoint | `artifacts/final-review/report.json`,8accepted bundles |
| Production crop QA | `artifacts/final-review/crops/crop-qa.json`,150/150 |
| Human-ready sampled review | `artifacts/final-review/audit/combined-queue.json`; independent editor copies, approvals false |
| Actual annotation UI | `editor-smoke.log`: all5selected images loaded in installed offscreen editor; annotation JSON hashes unchanged |
| Visual comparison | `artifacts/final-review/geometry/review.md`; observations above |
| Offline software verification |44fixture,46TTR,136human tests; Swift build;120Swift Testing+14XCTest passed |
| Data eligibility | Diagnostic-only; human verification, unsupported families, corpus coverage and source-role reservation remain open |
| Integration | Measured image-body mapping/crops verified on this delivered stationary Simulator evidence, not universal renderer qualification |
| Model gate | Not assessed; no inference, training, promotion or weight changes |

## Next action

Prepared queue has5images (4seeded-random plus exception selection, deduplicated):
frames041/017/005/002/040 spanning native images, mixed aspect, no-growth and clipping.
Twenty-oneof42frames are eligible for sampling; other frames are explicitly excluded
for duplicate identity, unavailable bodies or unresolved controls, not silently lost.
The prior annotator has not been forcibly closed or replaced. Save/close confirmation
was requested before opening this new batch.

Verified receipt and consumer result published/read back to the owned shared packet
and response; peer acknowledgment/cleanup remain unobserved. See [coordination](coordination.md).

Human: review the small prefilled queue; verify rectangles and focus rather than
redraw them. Do not confirm completeness where unsupported parent controls are absent.
TTR: continue explicit public/native button, row and dialog body measurement and
representative proof; do not expand their unsupported growth corpus. Existing image
repair does not need another capture. NUIAK: incorporate human dispositions, then
complete coverage/source-role acceptance before corpus assembly or a changed-data run.
