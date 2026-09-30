# Repair receipt and consumer checks

2026-09-30; base c63bb30. Existing dirty annotation/harvest/research changes preserved.
No implementation or producer-repository files changed.

| Outcome | Result |
|---|---|
| Software |64focused tests pass; additional real-sidecar editor test finds blank-image first-import Undo failure. Not all-green editor acceptance.|
| Data |Both archives/13declared payload members verified; original images unchanged. No label approval or training admission.|
| Integration |Actual supplied Vision sidecar imports against retained originals; exact failed helper retry/live artwork delivery remain unqualified.|
| Model |Not run; weights, membership, thresholds and gates unchanged.|

## Receipt

Existing `synth05_receive.receive` used with exactly the two assigned entries,
bounded member validation/fresh extraction and5GB reserve. Actual local free45GiB.
No peer deletion or TTR source execution.

| Archive | Bytes | SHA256 | Extraction |
|---|---:|---|---|
| ttr-campaign-artwork-policy-dabe82d7-20260930-r1.tar.gz |106509|5b5a8cf0eeac060c137f7c6ff864157dda76913ca644bd1024b2469fc0fccf82|20members,379216expanded bytes;7declared files verified|
| ttr-vision-retained-repair-20260930-r1.tar.gz |13878|5125353a7f17e0141adb7848ad2effcfd862610693b4da2c1734bace5ac59d52|15members,69695expanded bytes;6declared files verified|

`received/receipt.json` records immutable paths/time; `member-audit.json` records
payload identities. Directories/manifests/AppleDouble entries are not additional
declared payload files. Archives preserved in ignored storage.

## Real sample integration

Sample is album_grid synth-15, NOT the originally failed FBACA6BC job. Matching
3840×2160 originals already exist under
`dataset/tvos_captures/frozen-surface-intake-20260927/album_grid/export/`.
No new inference/transfer of images; no challenge inspection.

- Sidecar:51ff2f9116c4e4ab56e43f37a2a142892e01993e165c9a36b39838f94e1f24cd.
- Before:ad85ccecfc8ea337a70acd51d54cf463374f5299a9acbd93747d97de1b1a6883.
- After:be92a403c70a697fe1abfd15a7acfb67624b650e1a5227c0a581c3fd2026dcfd.

Existing `human_vision_import.load` accepts both hashes/dimensions/schema/revisions/
scores/geometry. After dedupe:18rectangles+25OCR before,19rectangles+25OCR after.
These measure compatibility, not accuracy. `sidecar-import.json` retains results.
Actual offscreen editor on a disposable original-byte copy previews44regions with
19rectangles checked and25OCR unchecked. Cancel preserves zero shapes. Accept adds
19unconfirmed/unfocused rectangles with provenance; save/reload preserves19.
Original pixels and human annotations unchanged (`real-editor.json`).

**Finding:** on an unannotated image, first batch import leaves canvas backups
`[19]`, without an empty starting snapshot. Undo leaves19rather than0. Existing
prefilled-frame undo tests pass. Consumer-owned fix: preserve empty baseline at
batch add and test blank/prefilled paths, then required offline build/tests.
This is not a producer schema defect and does not block receipt acceptance.

Exploratory UI harness first stalled in a save-file dialog; only owned offscreen
PID16883 was terminated. Corrected harness supplies a disposable save destination
and20s deadline. Another attempt incorrectly expected undo history after reload;
that expectation was removed. Final test measures undo before reload and reports
the genuine missing-empty-snapshot failure. Failed logs retained; no user editor touched.

## Source compatibility and remaining gates

Delivered HarvestRecipeHeader preserves optional boolean `evidence_requirements`
through campaign decode/encode/initializer, independently of visual recipe hash.
Included tests cover legacy absence, malformed value, roundtrip policy and required
geometry failure through staging before screenshots. Existing NUIAK nominal-artwork
geometry contract is compatible; no consumer schema change needed. Nominal image
layout is not native animated/glow bounds. Producer58passes/3skips are reported,
not rerun here. Four-pair proof remains unrun at peer16:52:15Z due9.58GiB versus10GiB
reserve.64artwork pairs held;395admitted pairs unchanged.

Vision patch improves local routing and stage/cause diagnostics; it does not prove
the original Max failure cause. Applying/building it belongs to a separately assigned
TTR source-integration lane. Do not retry unchanged helper or recapture images.

## Verification and next work

`.venv-review/bin/python -m unittest test_human_vision_import
test_human_review_editor_interactions test_harvest_derived_views
test_focus_offline_preparation test_focus_geometry_diagnostic` with PYTHONPATH=scripts,
PYTHONDONTWRITEBYTECODE=1, QT_QPA_PLATFORM=offscreen and project TMPDIR:
64tests pass in11.015s (`focused-tests-final.log`). Initial command named a nonexistent
module; corrected after discovery, failed log retained. Real sample test is separate.
No implementation changed; full Swift checks not required for receipt/review.

Assigned receipt/extraction/compatibility/testing complete with findings, not full
integration qualification. Next local implementation: blank-frame Undo repair.
Next producer-dependent work: exact failed-pair repaired-helper test and four-pair
artwork delivery, then consumer crop QA. No background process remains. Shared exact
receipts/findings published; acknowledgment/cleanup pending. Preserve all source bytes.
