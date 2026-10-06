# Retained focus pixel review — October 6

Inspection only, no admission or threshold tuning. Read existing production crops
and original screenshots directly; no new image generation or alternate cropper.

## Reviewed cases

1. `streaming-detail-growth-r2`: both full3840×2160screens and both256×256
   production crops reviewed. In the reference frame the neighboring second card
   visibly has the enlarged/light treatment; after transition the first card does.
   The cards share mountain-bike artwork. The target's unfocused crop includes
   part of the focused neighbor at its right edge. The focused target has rounded,
   lighter treatment and blur near the image edge. Per-endpoint resizing makes
   the target artwork occupy a similar crop area despite the original growth.
2. `news-frontpage-growth-r2`: both production crops reviewed, not its full screens.
   Same bike artwork and analogous lighter/rounded target appearance in the
   focused crop, with neighboring-card content at the right edge. This is not
   independent artwork diversity or full-screen semantic qualification.

Existing shipped-model diagnostic assigns probabilities0.1899414→0.0031356812
and0.3256836→0.045440674 respectively (reported unfocused→focused). Both orderings
are inverted relative to producer roles and the inspected visual treatment.
This identifies concrete challenge cases, not aggregate accuracy: historical build
binding remains unresolved and these are selected review/calibration examples.

## Implication for the next controlled experiment

Separate three hypotheses: neighbor focus contaminates the expanded context;
independent resizing reduces scale-change evidence; unseen artwork/style shifts
the classifier. These observations do not distinguish their causal contributions.
More generated artwork alone cannot test them. Reuse qualified retained pairs
first, with explicit target/competitor geometry and unchanged production-crop
baseline. A future context/paired-input arm must be separately registered, use
eligible training membership and retain independent evaluation ancestry. Do not
mask neighbors or change expansion in the shipped preprocessing as an untested fix.

The selected captures remain in existing review/calibration roles; no new training
role or final holdout is created. Remaining18pairs and full news screens are not
visually reviewed by this note. Exact crop/source hashes remain in
`artifacts/schema4-crops01/review-crops.json`; probabilities in
`artifacts/schema4-shipped-diagnostic01/review-scores.json`.

## Appearance contrast reviewed next

Also inspected both crops for `streaming-detail-light-r2` and
`streaming-detail-dark-r2`. Both show the same visible bread artwork and target
focus treatment, with different surrounding artwork/background and light/dark
card fill. Their recorded baseline and focused visible rectangles are identical:
`[853.3333,1577.7778,533.3333,206.2222]` and
`[816.5517,1563.5556,606.8966,234.6667]`. Both report1.155full-width growth and
focused clipping. Nevertheless focused-minus-unfocused model probability is
**-0.334473** for light and **+0.414062** for dark. This is a joint appearance
contrast, not an isolated theme intervention: surrounding artwork also differs.

Read-only reconciliation across all20pairs confirms growth1.06–1.17 and both
positive and negative score differences among clipped examples; the two unclipped
examples give0 and+0.021484. Growth/clipping alone cannot explain the score pattern.
No statistical generalization is inferred from this selected small set.

Updated visual scope:8crops across4pairs, plus2fullscreens for the initial detail
pair. The other16pairs and other fullscreens remain visually unreviewed. Prefer a
future factorial comparison holding target artwork, layout and transitions fixed
while changing card fill, backdrop and neighbor state separately. Use qualified
training-role siblings, not these reviewed calibration frames as new training data.
Keep existing production crop/model as the reference. No new capture requested here.

## Complete crop review checkpoint

Reviewed the remaining32existing crops directly: all40production crops/all20pairs
have now been visually inspected. Only the original detail pair's two fullscreens
have been inspected here; crop review is not complete full-frame box validation.
No new image derivatives, inference or capture were needed.

| Cases | Observed crop evidence | Qualification limit |
|---|---|---|
| Eight growth-r2 cases | Target image retained; focused crop has rounded/light overlay treatment; competitor enters right crop edge in multiple cases. Bike and abstract artwork recur across scene names. | Scene-name variety is not independent artwork variety; captions enter some crops differently. |
| Catalog dark | Thin bright outline appears on target in focused crop; neighbor outline visible in reference context. | Both shipped probabilities saturate at1; correct geometry does not imply useful classifier discrimination. |
| Catalog light | Near-identical jellyfish content/card shape after resize; change is visually subtle. | Crop-only visual confidence is insufficient; retain uncertainty and inspect full-frame/native evidence before label acceptance. |
| Avatar light/dark | Portrait remains; focused treatment changes translucent surround, upper edge and lower shadow. | Surface treatment extends beyond subject pixels; portrait segmentation is not the control-body label. |
| Plant/bird alpha light | Focused examples show rounded translucent surround and shadow on a pale field. | Light-on-light effect; do not use subject silhouette as the control box. |
| Plant/bird dark detailed | Focused surround becomes lighter against detailed background. | Background and alpha are confounded with style in this selected corpus. |
| Detail light/dark | Bread artwork, same measured geometry, opposite score ordering. | Joint appearance contrast, not isolated causal theme test. |
| Library light/dark | Bright yellow bird artwork and neighboring card; focused resize includes caption region differently. | Bright unfocused artwork and caption/context differences need distinct error accounting. |

No crop is visibly blank or an unrelated target in this review. This does not
establish pixel-perfect bounds, historical binary identity, label certainty for
every pair, or an independent model gate. Preserve the18clipped cases as clipped;
do not discard useful difficult examples solely because the shipped model fails.

Next acceptance work is now specific: resolve retained build mapping; inspect the
remaining fullframes against measured-body bounds (especially catalog-light and
cutout clipping); then decide stated data roles. Do not rerun crop generation or
the shipped baseline just to repeat these observations.

## Catalog-light full-frame check

Inspected both original3840×2160catalog-light frames. The first bottom-row card
grows while its second-card competitor shrinks; first-card top/left edges shift
outward. The target positions agree visually with the reported rectangles
`[853.3333,1186.6667,480,693.3333]`→
`[838.9333,1165.8667,508.8,734.9333]`, a1.06growth ratio. Neither is clipped.
This is visual consistency, not subpixel measurement validation or independent
proof of UIKit focus identity. It reduces the crop-only ambiguity: relative scale
is apparent in the full pair but weak after independent256square normalization.

A paired fixed-coordinate context experiment is therefore justified once eligible
inputs exist, alongside—not replacing—the existing production crop baseline.
Keep temporal order, both boxes, competitor state and no-change controls; no model
should infer a transition merely from a requested action. Do not silently reuse
these repeatedly inspected calibration pairs as training or final evaluation.
Current visual scope is40crops and4fullframes; remaining fullframe review is open.
