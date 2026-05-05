# OCR Fusion Policy

**Version:** 1.0  
**Governs:** Phase 7 implementation (`VNRecognizeTextRequest` fusion with CoreML element observations)  
**Authority:** This document defines the rules for associating OCR text to detected elements. The implementation must match these rules exactly.

---

## 1. Association Algorithm

After `VNRecognizeTextRequest` runs on the same image as the element detector, associate each OCR text observation to at most one element observation using the following procedure:

1. **Candidate filter:** For each OCR text observation O, collect the set of element observations E where:
   - IoU(O.boundingBox, E.boundingBox) ≥ 0.10 (Vision-normalized coordinates)
   - The centroid of O and the centroid of E fall in the same image quadrant (top-left, top-right, bottom-left, bottom-right). This prevents text from a nearby element bleeding into a distant one.

2. **Winner selection:** Among the candidates, select the element E* with the highest IoU with O. If two candidates have equal IoU (to 3 decimal places), break the tie by choosing the element whose centroid is closest (Euclidean distance in normalized coordinates) to O's centroid.

3. **One-to-many allowed, many-to-one allowed:** A single element may accumulate multiple text observations (multi-line text, label + subtitle). A text observation may match at most one element — it is assigned to the winner and not re-used.

4. **Unmatched text observations:** OCR observations that do not match any element (IoU < 0.10 with all elements) are discarded. They likely belong to background content, wallpaper, or web content — not native UI elements.

---

## 2. `visibleText` Field Construction

After association, the `visibleText` field of each observation is constructed as:

- **Aggregation:** Concatenate all associated OCR text strings with a single space separator.
- **Reading order:** Sort associated OCR observations top-to-bottom by their bounding box Y-coordinate (top-left origin). For RTL layouts (`layoutDirection == .rtl`), sort right-to-left within each horizontal band (observations within 10pt of the same Y are in the same band; sort those right-to-left by X).
- **Whitespace normalization:** Collapse consecutive spaces, strip leading/trailing whitespace from the final string.
- **Empty case:** If no text observations associate with an element, `visibleText` is `nil` (not an empty string).

---

## 3. Truncation Detection Rule

Emit `NativeUIIssue(kind: .truncatedText, ...)` for an element when **both** of the following are true:

**Condition A — Geometric:** The bounding box of the last associated OCR observation's width is less than `element.boundingBoxPixels.width × 0.85`. This indicates the text was not given its full natural width.

**Condition B — Textual:** The `visibleText` string ends with the ellipsis character U+2026 (`…`), OR the last word of `visibleText` is shorter than 3 characters AND does not appear to be a complete word (no terminal punctuation `.`, `!`, `?`, `,`, `:`, `)`, `"`, `'`). The second sub-condition catches mid-word truncation that does not use an ellipsis glyph.

**Confidence:** Set `confidence: 0.85` when both conditions hold. Set `confidence: 0.60` when only Condition B holds without geometric confirmation.

**Elements exempt from truncation detection:**
- `toggle`, `slider`, `imageView`, `mapView`, `activityIndicator`, `progressView`, `pageControl`, `scrollIndicator`, `colorWell` (see Section 5)

---

## 4. Conflict Resolution: Sidecar vs. OCR

When a sidecar is present and provides `visibleText` for an element:

1. **If OCR agrees** (Levenshtein distance ≤ 2 characters): use the sidecar value (it is ground truth).
2. **If OCR disagrees** (distance > 2 characters): **prefer the OCR value** — it reflects what is actually visible in pixels. This handles cases where the sidecar captured the accessibility label but the rendered text is different (e.g., truncated, formatted differently).
3. **Log both values** in the annotation's `visibleText` metadata when a conflict is resolved: include `ocrText`, `sidecarText`, and `conflictResolution: "ocr_preferred"` in the element's annotation JSON under an optional `_debug` key.
4. **Exception:** If the sidecar's `visibleText` matches the element's `accessibilityLabel` (exact or near-exact match) but the OCR result is the rendered label, both are valid — use the OCR text for the model and log the sidecar label as `accessibilityLabel`.

---

## 5. Elements That Must Not Have Associated Text

The following 9 element classes must not receive `visibleText` even if OCR observations spatially overlap them. Any OCR text that would associate with these classes is discarded:

1. `toggle` — state communicated by switch position, not text
2. `slider` — value communicated by position
3. `imageView` — visual-only content
4. `mapView` — map tiles; any text on the map is cartographic, not UI
5. `activityIndicator` — no text content
6. `progressView` — no text content (progress label is a separate `label` element)
7. `pageControl` — dot indicators, not text
8. `scrollIndicator` — position indicator, no text
9. `colorWell` — color swatch, no text

**Implementation note:** Check `elementType` against this list before running the association algorithm for any OCR observation. If the nearest element is in this list, skip association for that OCR observation entirely.

---

## Implementation Checklist (Phase 7)

- [ ] `OCRFusion.associate(elements:ocrObservations:layoutDirection:) -> [NativeUIElementObservation]`
- [ ] IoU ≥ 0.10 filter applied before winner selection
- [ ] Same-quadrant filter applied
- [ ] Tie-breaking by centroid distance implemented
- [ ] Reading-order sort handles both LTR and RTL
- [ ] Truncation rule: both Condition A and Condition B implemented with correct thresholds
- [ ] Exempt class list enforced at association entry point
- [ ] Sidecar conflict resolution: OCR wins at distance > 2; log both values under `_debug`
- [ ] Unit tests on known-truncated fixtures (Phase 5a produces these)
