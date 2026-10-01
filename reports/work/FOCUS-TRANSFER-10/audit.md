# What the model is getting wrong

This is a development-set diagnosis of FDR032, not an independent test.
Retained predictions and actual production input pixels are in
[audit.json](artifacts/audit/audit.json); reproducible with `audit.py`.

There are34artwork mistakes:25false focus detections and9missed focused items.
The other3of12focused items are correct.
22/25 false positives are mostly white by a fixed diagnostic rule: more than65%
of the central192-square pixels have all RGB channels above220 and channel spread
below25. Three of9 misses also meet that rule. Brightness alone cannot decide focus.

The 12 new training crops are three simple artwork designs in light/dark contexts.
They are already classified confidently in training, but do not cover all of the
real failure structures below. Counts of training source IDs are not counts of
independent layout families.

| Observed failure | Why the new examples do not fully cover it | Next useful coverage |
|---|---|---|
| Composite hero with a title panel and artwork | Focus belongs to the whole composite, not just a poster bitmap | Native hero/card containers, varying header/footer and content proportions |
| Artwork plus text/detail footer | Internal brightness and focus appearance can disagree | Bright/dark artwork independently crossed with focus and footer style |
| Horizontal ranked rows | Expanded crops around4:1 are stretched to1:1 | Wide row containers with icon, title and metadata; preserve aspect in experimental input |
| Home icons on different backgrounds | White tiles are difficult negatives, but the enclosing scene and focus position also vary | Native icon grids, varied background contrast and actual focused slot |

![Missed composite hero: screen, neighborhood, actual input](artifacts/audit/01.png)

![Missed wide row: the rightmost model input is stretched](artifacts/audit/04.png)

![False focus on a wide row](artifacts/audit/07.png)

![New synthetic focused example](artifacts/audit/09.png)

## Tests selected before execution

1. FDR033: increase the twelve new controls' relative emphasis10×, preserving each
   fixture label budget and every nonfixture weight. Tests insufficient influence.
2. FDR034: use the existing native aspect-fit branch instead of stretching, keeping
   original FDR032 weights. Tests shape distortion, **not absolute enlargement**.

Both retain the same1562training/333evaluation members, labels, initialization,
optimizer,100update limit and fixed.85 decision threshold. Production stays unchanged.
Matched FDR032 comparisons distinguish experiment effects; FDR021 remains the
actual acceptance bar. No evaluation failure becomes a training example here.

## Existing producer plan

Read-only inspection of48retained recipe JSONs in the FOCUS-ARTWORK-08 owned-artwork
delivery found the same grid_matrix archetype, regular density,27elements and
catalog-poster-0 target content. The appearance families are16pale marks,
16white marks,8blank placeholders and8faint placeholders. These are useful appearance
variants; they are not48independent layouts. The remaining42 should not be treated
as an automatic remedy for the composite/wide-row gap. No new capture dispatched.
