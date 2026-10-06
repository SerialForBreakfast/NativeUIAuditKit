# DETECTOR207 proposal-support decision

2026-10-06. Reused96 development frames and Run022 predictions. Existing evaluator
validated manifest/content/label/settings/checkpoint binding before read-only analysis.
Exit0,1.227s. No inference, capture, training, role change or production modification.

Per-target same-class diagnostic, confidence0.25 / IoU0.5:

| Grid condition | Operating match | Low-confidence match | No imageView anywhere | ImageView elsewhere, zero overlap | Positive overlap below0.5 |
|---|---:|---:|---:|---:|---:|
| Procedural |80|0|0|0|0|
| Lower detail |12|28|32|8|0|
| Busy |3|21|20|34|2|

All16hero targets match in each condition. Median letterboxed target sizes:
grid72.36×54.27pixels, hero295.21×195.31. Layout/content/size remain confounded;
this is not a causal resolution experiment.

Of40lower-detail targets without exported same-class IoU matches,37 overlap an
operating collectionItem atIoU>=0.5; of56busy targets,40 do. This is enclosing-class
evidence, not proof of misclassification: legitimate child/parent labels overlap.
Test nested-image recognition within detected cards rather than repeating the thin
pageControl intervention or lowering thresholds. Best-candidate counts are not AP's
one-to-one accounting. Exported absence does not prove absent internal proposals.

## Next bounded diagnostic and data decision

Before training, compare one fixed collectionItem-derived crop rule with full-frame
Run022 on these development frames. Select crops only from predictions, never labels;
truth scores containment/recovery only. Reuse existing crop/export/restoration code.
Freeze window rule, membership and output budget before execution. Report coverage,
imageView recovery, duplicate/false positives, parent retention and added inference
cost. No threshold/window search. Success supports a scale/context study; failure
supports richer nested-label training examples. No crop inference launched here.

204already provides16thumbnail originals in eight connected subject families, two
treatments each. Drama/comedy/animation/sports/news have proposed development roles;
nature/architecture reserved validation; abstract reserved unseen-content diagnostic.
Actual roles remain unassigned and rights/review pending. NUIAK must review complete
connected families before assignment. No new worker generation or transfer is needed.
Never move reserved siblings into training. Future training uses eligible families
in training-compatible native grids, not CardDetail or IMAGE201development frames;
preserve enclosing collectionItem and child imageView annotations.

NUIAK owns review, native labels, admission and candidate design. Big Dog's paired
report correction is separate. TTR binding blocks205/206, not this iOS work.

## Reproduction and identities

Inputs `artifacts/campaign-evaluation01/`; existing `eval_run013.validated_artifact`
and `iou_xyxy`, YOLO labels converted to original pixels. Classify operating match,
low confidence, absent class, zero/sub0.5overlap in that order. Cross-class counts
require score>=0.25 / IoU>=0.5, count each target once per overlapping class.

- Manifest: `ec89ec88b872379971a56908ca053b80a71125fd898a84adc663a73843f15849`
- Predictions: `6a8f59de97a3dbdefea480c0c66f3fcc4bd817c91468ba8a42617f73151b8c92`
- Protocol: `2767a1c3f0121557baa147726dcfe8bc3196738cf776b039bba26998cbb2447e`
-204selected manifest: `56fad54bc0236e219b4d3f82367b28ba72ecf4324358a6b64b4658e00ba6d816`

Software unchanged; validation passed; development-only roles unchanged; native
integration evidence reused; model gates not assessed. No full rebuild needed.
