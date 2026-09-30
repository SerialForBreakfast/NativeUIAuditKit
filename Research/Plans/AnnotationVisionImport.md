# Optional TTR annotation suggestions

User requested supplied OCR and box detection as optional annotation imports during
FOCUS-GEOMETRY-LIVE-02. Use the existing Labelme editor and batch-preview path.
Source contract inspected from the running build's VisionPairPreprocessor.swift:
schemaVersion1, kind vision_pair_preprocessing, before/after frame SHA256,
dimensions, top-left normalized xywh, OCR regions and rectangle proposals.

Explicit file chooser only; no automatic preprocessing, capture or default import.
Match the current image by exact original-byte hash and dimensions, not filename
or before/after role. Reject changed/unsupported/bad bounds/confidence inputs.
Preview rectangle suggestions and OCR regions separately; OCR starts unchecked
and is described as text bounds, not full control bounds. Preserve existing labels,
suppress duplicate boxes, cap additions to100total, allow subset selection/cancel,
batch undo and save/reload. Imported shapes stay unconfirmed and unfocused;
clear reviewed on addition. Preserve sidecar provenance and OCR text as an optional
note, never semantic class/focus truth. No automatic correction or model gate.

Verify isolated schema fixtures and actual Qt import/cancel/add/undo/roundtrip,
including missing image match, corrupt reports, invalid geometry and empty results.
Run offline Swift checks for code changes. Do not reopen an occupied editor or
lose user annotations. Real supplied sidecar integration remains explicit if only
source-shaped test fixtures are available.

Implementation complete2026-09-30UTC. Existing editor action imports only on request;
71combined Python/Qt tests pass, including preview cancellation, selected additions,
batch undo with original labels preserved, and save/reload. Offline Swift build and
123tests pass. Real producer sidecar receipt remains a separate integration check.
