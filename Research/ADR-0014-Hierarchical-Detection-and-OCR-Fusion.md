# ADR-0014: Hierarchical UI Detection and Vision OCR Fusion for Fine-Grained Classes

- Date: 2026-09-30
- Status: Proposed experiment; not an adopted replacement or execution approval.
- References: [Architecture](NativeUIElementDetection.md), [OCR policy](OCRFusionPolicy.md),
  [Run 013 evidence](../reports/work/IOS-R013-EVAL/handoff.md).

## Corrected baseline

Run 013 completed 106 epochs, selecting epoch 91. On identical 2,000-image,
13-supported-class withheld inputs and the same metric implementation, Run 009
scored 0.5549 mAP50 and Run 013 scored 0.6322. Historical Run 009 0.586 is not the
matched baseline. Run 013's supplementary 2,400-image/38-class result is 0.8790;
addon-family overlap prevents independent 41-class qualification. DS-G8 stays open.

These results establish insufficient coverage and transfer, not proof that flat
41-class detection is fundamentally impossible. Role ambiguity, imbalance, geometry,
label conventions and representation are hypotheses to distinguish.

## Proposed comparison

Compare coarse localization plus semantic refinement against the current flat
baseline. An 8–10-class consolidation is not a frozen taxonomy. Before training,
define mappings for every stable class, including unsupported cases and split
support. Preserve public raw values; do not invent roles such as backButton as API.

Reuse existing Vision OCR fusion. Text, symbols, appearance and optional verified
hierarchy are evidence, not guaranteed roles. Keep ambiguous assignments explicit.

Freeze identical cases and metric implementations. Report localization separately
from final stable-taxonomy performance, including OCR failures and missing classes.
Measure total latency, no-text/ambiguous cases and OS/style variation.

A coarse-class score of 0.90 does NOT pass DS-G8: evaluate the composed 41-class
system against the existing gate and independent coverage requirements.

## Non-claims and priority

OCR is not free, guaranteed ANE execution or a promise of 100% role precision.
Ellipses are not deterministic truncation defects. Improvements and style robustness
require measurement; additional stages introduce failure boundaries.

This research follows focus delivery. No training, gate change, public taxonomy
change or replacement is authorized by this ADR.
