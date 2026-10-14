# FOCUS330 — detector-centered regions

## Decision

Reject the tested crop rule before training. It reduces useful boundary coverage in the main conflicting training families.
No candidate starts. No model, label, threshold, data role, or production behavior changes.
The approved experiment includes a conditional run. Its evidence requirement fails; more epochs cannot repair missing image evidence.

## Measurement

The existing nativeui-audit executable scores 138 unique images through its existing MCP interface.
Use tvOS confidence 0.25 with OCR off. Ignore predicted focus states and classes when proposing regions.
Keep the detector's top-left pixel coordinates. Clip boxes to image bounds before conversion to the existing letterbox.
Rank 32 × 32 windows by absolute image change. Select at most 2 nonoverlapping windows centered on detected controls.
Known measured boxes use the same selection rule for diagnosis only.
The audit uses 548 training pairs from 17 groups. All source hashes and encoded pixels pass their checks.

| Measurement | Existing windows | Detector-centered windows | Known-box diagnostic |
| --- | ---: | ---: | ---: |
| Median boundary coverage, 485 nonzero cases | 51.64% | 51.72% | 62.81% |
| Mean boundary coverage, 485 nonzero cases | 54.47% | 51.21% | 69.48% |
| Median boundary coverage, 279 content cases | 44.97% | 20.20% | 59.82% |
| Median boundary fraction inside crops, content cases | 21.29% | 7.31% | Not reported |

The existing windows capture more boundary change on 283 cases. Detector-centered windows improve coverage on 180 cases.
The remaining cases have equal or unavailable coverage. Zero boundary change has no coverage ratio.
The raw detector rule selects no positive window on 78 pairs. This includes unchanged images; it does not establish detector failure alone.
The content subset has no empty proposals. Therefore, an empty-proposal fallback cannot repair its observed loss.

At IoU 0.5, detector boxes match 1,789 of 4,652 measured control occurrences: 38.46%.
These counts repeat frames across pairs. After exact frame-and-box deduplication, 302 of 675 controls match: 44.74%.
Neither count represents independent trials. Geometry matching ignores predicted classes and does not establish correct semantics.
Content families have only 19.13% occurrence-weighted recall. Both families lose boundary coverage independently.
Known-box centering is not universally better: the style-first group loses coverage even with known boxes.

## Previous successes

Reuse cached FOCUS327 and FOCUS329 predictions. Do not rerun inference for unchanged models.
Both retain 503 correct decisions on these 548 training rows.
FOCUS327 has 4 false changes. All 4 belong to the subset where detector-centered coverage gets worse.
FOCUS329 has no false changes here, but 45 abstentions. Its total correctness remains unchanged.
These comparisons locate existing errors. They do not predict a trained result for the rejected crop rule.
Development and reserved images do not enter region selection. Previously inspected sets remain inspected sets, not untouched final evaluation.

## Execution and verification

Unique-frame inference takes 15.92 s. The complete boundary audit takes 85.86 s.
These timings exclude setup, tests, and report preparation. No training time is spent.
The first MCP attempt omits its initialized notification. The server rejects every scan before inference.
The corrected entrypoint sends the notification. A deterministic entrypoint test covers initialization, duplicate images, and altered hashes.
A registration collision also stops safely. Both failed logs remain preserved; no partial result becomes completed evidence.

The focused suite passes 43 tests. The offline Swift build, 14 XCTest tests, and 173 serial Swift Testing tests pass.
The final handoff records the coordinator receipt.
The coordinator stores result `nuiak-focus330-result-01` at cursor 177. Exact-ID readback passes; forwarding and TTR acknowledgment remain unconfirmed.
Raw results, exact model identity, binary hash, source hashes, and cached comparisons remain in ignored FOCUS-330 output.

- Software: focused checks and real detector execution pass.
- Data: existing training roles remain unchanged. Native-derived images do not establish real-app generalization.
- Integration: the resident inference CLI works. TTR integration is not retested.
- Model: no candidate is trained or promoted.

## Next substantial tranche

FOCUS331 should test boundary-aware image regions without making the current detector a required input.
Use the same retained training images. Compare boundary-change ranking with the current absolute-change ranking at the same crop budget.
Measure boundary coverage and distracting artwork by family. Keep known boxes for diagnosis only.
Include a control that keeps the first existing window and changes only the second window.
If training evidence supports 1 rule, use 1 fixed 30-epoch comparison with unchanged roles, initialization, and thresholds.
Test all previous-success sets before any replacement. Do not collect more images or change TTR models for this experiment.
This follow-on remains proposed. It does not start another run.
