# Run013: measured failures and next assignment

Evidence: [full class/family tables and deltas](metrics.md), [machine-readable
metrics/confusions/examples](evaluation.json). All AP values are custom all-point
interpolated AP on unchanged, hash-verified cases. Counts below use confidence0.25,
IoU0.50. No training, threshold tuning or data modification followed these results.

## Decision

Keep the epoch91 candidate and this baseline for development; do not promote or
resume training merely because the combined score exceeds0.85. Withheld-family
mAP50=0.6322 remains0.2178 below the0.85 threshold, with only13 supported classes.
Four supported classes remain below the historical0.65 per-class floor. Addon
mAP50=0.9785 is mostly interpolation inside four training families, not coverage
of independent layouts. Combined0.8790 is supplementary only.

## Ranked failure work

| Priority | Measured evidence | Proposed work before another training decision |
| --- | --- | --- |
| 1 | secondaryButton AP50=0;341/341 misses. pageControl AP50=0.0012;600/600 misses. | Review button-role labels across families, especially secondaryButton versus cancelAction. Add independently composed button-role contrasts and page-dot groups with varied count, scale, placement and surrounding chrome. Keep evaluation cases out of training. |
| 2 | listRow AP50=0.0721;594/700 misses and1,172 FP. imageView AP50=0.1936;1,580/1,900 misses. Both score1.0 on addon cases. | Audit enclosing-container versus child boxes and diversify training/development compositions across card, notification, gallery and row contexts. This is a strong family-transfer gap; do not add more copies of the same addon layout. |
| 3 | toggle AP50 drops0.8085→0.7531 (−5.54points);303 toggle→listRow diagnostic confusions. GalleryPage family mAP50 drops0.7872→0.7473 (−3.99points). | Preserve these regressions as development guards; inspect neighboring row/chrome contexts and class competition before changing sampling or loss. |
| 4 | scrollIndicator addon AP50=0.2900, AP70=AP90=0,50 FP and50 misses across100 boxes. | Diagnose thin-object localization and device-scale sensitivity, not just class presence. Propose bounded resolution/localization experiments only after documenting source geometry; no resolution change was made here. |
| 5 | Withheld labels have2,759 misses versus2,373 baseline (+386), despite AP50 rising0.7004→0.7602; imageView AP90 falls0.1088→0.0683. | Track operating-point recall and tight-box regressions alongside macro AP; a better ranking score does not guarantee fewer misses at the fixed threshold. |

Other AP50 regressions: progressView −1.08points, navigationBar −0.55points,
primaryButton −0.06points. Largest gains: stepperControl +40.60points, textField
+24.70points, picker +19.47points. Family gains are largest for NotificationCenter
(+18.41points) and MultiSectionForm (+9.81points). Every supported class/family
and all four AP deltas are retained, not only selected improvements.

## Inspected examples and hypotheses

Three original images were visually inspected, with boxes read from the frozen
labels/predictions; no overlays or source images were edited.

- `test/images/img_002002.png`, CardDetail: the visible secondary "Preview" button
  is predicted as cancelAction with0.883 confidence and0.988 IoU against its
  secondaryButton box. This is a class-role error despite excellent localization.
  Across withheld cases,245 secondaryButton→cancelAction associations occur at the
  operating point. Inconsistent semantics versus appearance overfitting needs a
  source-label review; these observations do not prove an annotation defect.
- `test/images/img_003921.png`, GalleryPage: the visible four-dot page group has
  a165×30px GT box. The best-overlap pageControl prediction has IoU0.337 and
  confidence0.029; higher-scored alternatives are much too wide. The failure
  includes localization, not just inability to name a page control.
- `test/images/img_018941.png`, RichContentFeed: the visible vertical indicator
  has a9×180px GT box. A0.563-confidence prediction has IoU0.440 and approximately
  19.38px width. At the unchanged640 letterbox scale, the GT width is about2.25px.
  A second device-size example (`img_018942.png`) reaches IoU0.566. Thin-object
  geometry/scale is a plausible failure mechanism, not a proven causal diagnosis.

Images remain at `NativeUITrainer/yolo_dataset_41class_r7/test/images/`, identities
in [preflight.json](preflight.json). Complete predictions make these examples
replayable without another inference run. The class-agnostic confusion association
is diagnostic and differs from class-specific AP/FP/FN matching.

## Independent coverage work — mandatory, can proceed in parallel

The original withheld set supports13/41 classes. The addon set supports33/41;
their union supports38/41, adding25 classes but no independent family evidence for
those25. Train supports40/41 and validation35/41. Validation lacks pageControl,
progressView, secureField, textField, unknown and webContent, so epoch selection
could not directly measure those classes.

Prepare a reviewed family/role/scale coverage contract for all41 stable IDs, with
separate development and untouched final-challenge families, and decoded-content
plus family/near-duplicate isolation. Establish truthful examples and labeling policy
for homeIndicator, unknown and webContent; do not remap the taxonomy or silently
waive unavailable classes. The proposed webContent milestone exception is not a
complete41-class release qualification. Keep these reused r6 cases as diagnostics.

**Recommended next assignment:** one bounded IOS-COV follow-up delivering (1) a
source-backed label/geometry audit of the failures above, (2) a full independent
coverage matrix including validation gaps, and (3) a frozen development/final-test
data specification plus measured candidate experiment proposal. Any new rendering,
capture, training, alternate-resolution inference or promotion requires its own
explicit authority. Data source review can precede such execution approval.

## Dependencies and circularity

No TTR/Photos dependency is needed for this iOS work. Waiting for Photos acquisition
before iOS diagnosis would create an unnecessary coordination loop; do not add it.
The real one-way release dependency remains independent coverage and quality evidence
→ DS-G8 acceptance → later macOS/promotion work. Avoid a second loop in which test
failures are trained on and the same test is then declared untouched: retain diagnostic
status and reserve the final challenge before the next learning iteration. FocusRing's
separate product priority and hardware authorization are unchanged.
