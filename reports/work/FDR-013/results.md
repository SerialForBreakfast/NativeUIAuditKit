# FDR-013 — no eligible checkpoint

All30 epochs completed on verified MPS.124.34seconds in the trainer,
217.41seconds including startup/input validation. Exit2 is the intentional
no-eligible-checkpoint outcome, not an interrupted run. No best.pt exists.

| Diagnostic snapshot, not a selected model | Real TP /35 | Real FP /418 | Retention /18 |
|---|---:|---:|---:|
| Epoch1 |23|209|18|
| Epoch19 (lowest FP) |2|21|18|
| Epoch20 |5|24|18|
| Epoch30 (last, not selected) |7|39|18|

The fixed experiment requires TP>3 and FP<=9, per-stratum floors, at least two
unique-correct complete frames with zero wrong/multiple, and18/18retention.
Every epoch failed real-improvement, artwork and complete-frame guards. Retention
passed29/30epochs; epoch24 scored16/18. Tabs detected0/3focused examples at every
epoch. More detections early in training came with many false positives, not
usable focus selection. These are MPS training-time development measurements,
not a fresh CPU/CoreML comparison or independent generalization claim.

The terminal message says “retention floor,” but that generic text is incomplete:
the detailed checks show the persistent failures were real artwork/selection.
No threshold was lowered and last.pt was not substituted for a selected checkpoint.
The planned selected-checkpoint CPU/related-synthetic comparison is not applicable
because there is no eligible selected checkpoint. No export or promotion.

## Evidence and next assignment

`selection-verification.json` reproduces every selection metric for initialization
and all30epochs:14,601 stored predictions checked, with all frozen source-code
hashes unchanged. False-positive and miss IDs retain exact image/crop references.
Repeated false positives concentrate in Home artwork and media/search collections;
six listed controls are false positives in every epoch. Those counts are repeated
observations of development examples, not independent samples or a proven cause.

Next: audit the already-published native100-r2 and canvas-v2 coverage against these
specific failures before another training run. Prioritize same-artwork/same-background
focused/unfocused contrasts and visible hard-negative competitors; separately verify
selected-but-unfocused tabs and genuinely focused tabs. Use grouped native-label/crop
review, not per-image human redraw. Preserve the three geometry holds and all current
selection/protected members. If this delivery does not cover the contrast gaps,
specify a small targeted collection rather than another unchanged training run.
New receipt/capture/training remains a separate assignment; nothing was downloaded.
