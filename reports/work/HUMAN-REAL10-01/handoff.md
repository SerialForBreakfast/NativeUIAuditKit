# HUMAN-REAL10-01 — supplemental review; broad diversity incomplete

Latest revision192241Z:155/155 crops and structural audit pass,8 focused/147
unfocused. Two state-only corrections, no changed crop pixels. Maintainer confirms
frame3 first Top Stories item focused, Watch Now unfocused; clarification resolved. See
[corrected QA](qa-supplement-02/handoff.md). Earlier results below are historical.

## Human completion and crop QA — 19:10Z revision

Revision20260929T191036Z-583a5cf2 confirms8 frames/155 controls. Production crops
155/155 passed; structural audit passed,155 distinct crop pixels.6 focused and149
unfocused annotations; no candidate-completeness attestation. Two zero-focused
frames require targeted confirmation, not wholesale redraw. See
[QA handoff](qa-supplement-01/handoff.md). No model execution or training admission.
The earlier human-review-pending text below describes preparation history.

## Selection correction — supersedes initial ten-screen assignment

User correctly rejected the original selection as repetitive. Comparison with
four existing completed batches (32 reviewed frames) confirms prior Home, Photos,
Settings and App Store coverage. Exact pixel uniqueness was insufficient.
Initial batches remain intact, including any saved edits; do not continue them
merely to meet a count. The table below is historical, not the current assignment.

Current batch: `coverage-supplement-01/batch.json`,8 frames validated by the existing
importer and cross-checked for decoded uniqueness against all32 prior imported frames.
Audit: `coverage-correction.json`. Seven screens are Paramount+, one is OS Search;
this is a useful control/context supplement, not a diverse production corpus.

| Sequence | Incremental annotation value |
|---|---|
|875|Circular profile selectors and separate edit action|
|839|Expanded sidebar with dimmed underlying content|
|742|Outlined hero action and secondary icon control|
|614|Tall artwork shelf with partially visible neighbors|
|653|Ranked poster cards/numeric visual clutter|
|572|Landscape continue-watching cards with hero context|
|771|Text-only channel tiles among artwork shelves|
|479|OS Search category grid, without per-character review burden|

Profile names are visible in875; content approval remains the human's decision.
Selection is a visual assessment, not focus truth. Human bounds/states/settlement
still pending. After user saved/closed the old window, the documented runtime
opened this batch (tool session57202) using coverage-supplement-runtime-01.
No source code changed; importer validation passed. No model/capture execution.

Broader collection gaps: other app design systems, Control Center overlays,
player transport controls and non-account modal dialogs. Do not manufacture
diversity by filling ten slots with more cards from one app. A further capture
session needs its own approved scope; none was started here.

2026-09-29. Maintainer confirmed prior approval and removed repeated per-file
size approval and the10MB threshold from AGENTS.md and local/shared Instructions.
Named scope, capacity, bounded extraction, integrity and privacy checks remain.
Shared/local Instructions byte comparison passed.

## Verified receipt

Office archive895563805bytes:
SHA256 5b90331e3912e10a966b2407dac93d68cae5a028ef42a5841e9d766b69b5a552.
Verified18:33:25Z; receipt:
dataset/tvos_captures/human-real10-20260929/receipt.json.
Original archive retained. Initial1424 members exceeded pilot cap1000.
All paths/types/sizes validated under2000-member/4GB bound;712 AppleDouble
entries excluded with ledger,712 payload entries safely extracted.
All702 inventory image byte counts/hashes verified;739 unique frame records
matched Office source and inventory hashes.39GiB free after intake.

Source602380bytes and audit15939bytes also received/verified, not installed:
dataset/tvos_captures/real10-handoff-20260929/receipt.json.

## Human review ready

Ten distinct decoded pixel hashes, both batches passed existing importer validation.
Contact sheets/inventory under contact/. Existing8-frame cap preserved; two batches
of5, not a speculative editor change. Selected by visual diversity, not model output.

| Batch | Sequence | Context |
|---|---:|---|
|1|47|Home app grid|
|1|121|Settings developer rows/toggle|
|1|187|Settings reset-action rows — screenshot only|
|1|249|Screensaver selected/checkmark rows|
|1|314|Photos welcome buttons|
|2|479|Search artwork results|
|2|599|Paramount My List|
|2|742|Paramount news hero/button|
|2|786|Paramount news episode cards|
|2|839|Paramount sidebar/context|

Account-confirmation and visibly transitional sampled screens were not selected.
These are ten screens, not ten apps or ten focused/unfocused pairs. Settlement,
bounds, focus and content approval remain human-reviewed. No automatic labels.
Next: confirmed revisions → production crop QA; no automatic training admission.

Batch1 launched with documented runtime (tool session98045), separate local settings:
```sh
PYTHONDONTWRITEBYTECODE=1 reports/work/HUMAN-REVIEW-01/runtime/venv/bin/python \
 scripts/human_review_editor.py reports/work/HUMAN-REAL10-01/review-batch-01/batch.json \
 --runtime reports/work/HUMAN-REAL10-01/editor-runtime-01
```
For batch2 replace both01 suffixes with02. Initial .venv-review launch failed
Qt cocoa discovery; documented runtime launched without reinstall or source changes.

## Separate outcomes

Software: existing importer validation passes; documented editor launched.
Data:702 images verified,10 distinct screens ready; human annotation pending.
Integration: verified delivery, not a new TTR runtime qualification.
Model: unassessed; no inference, training, export or promotion.
No source changes in this tranche; Swift build/test not required for data/docs only.

Owned HUMAN-REAL10-01 packet published to /Volumes/SharedStatusFile/nuiak/status.yaml
with exact receipts and maintainer policy amendment. Sender owns cleanup; peer
acknowledgment remains unknown. Tasks/current state updated; no repeat capture needed.
