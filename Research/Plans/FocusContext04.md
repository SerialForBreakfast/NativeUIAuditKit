# FOCUS-CONTEXT-04 — controlled representation diagnosis

Assigned2026-10-01; owner Codex. Maintainer approved whole experiment tranches and
asked why better annotations do not improve focus detection. Preserve FDR021.

Completed: all three arms executed and rejected; all training examples learned,
but no eligible checkpoint. [Results](../../reports/work/FOCUS-CONTEXT-04/handoff.md).

Use the exact FDR0231550training/315development/18retention membership, weights,
fixed.85threshold, optimizer(.01AdamW/.01decay), seed42 and existing selection policy.
No split changes, threshold sweep, final-challenge access, capture or export.

Three comparisons, at most1000updates/300training seconds each:

1. FDR024: nonlinear local-feature head. Is the577parameter linear head limiting
   separability? Input is the existing576frozen crop features only.
2. FDR025: same head plus current normalizedxywh and four clipping flags. Does
   growth-preserving geometry add information beyond capacity?
3. FDR026: same head plus geometry and frozen scene features: global mean and
   candidate-mask-weighted spatial mean from the same MobileNetV3-small encoder.
   Does visible context add information beyond geometry?

All arms use the same1736→64ReLU→1head. Unused columns are zeroed; all non-local
first-layer columns start at zero, giving identical initial predictions across arms.
No fit to evaluation data, feature standardization or label-derived peer/reference
size. Masks/geometry are prediction inputs; supervision remains in the original
protocol. Shape cues are relative within one screenshot, not measured motion.

One new encoding pass is included: at most693shared768x432scenes,1883candidate
masked pools, batches of8(2.65Mscene pixels),300encoder seconds,64MiBcache.
Resident pinned ImageNet encoder only, eval/no-grad, exact unchanged state check.
No model download/backbone updates. At most1800seconds total model execution and
2GiBnew outputs for the tranche; implementation/test time is separate from this
execution budget. Use scoped MPS runtime directly and a cumulative external deadline.

Integrate with the existing trainer and full-fit loop, not a second optimizer.
Context checkpoints use distinct context-mlp kinds and carry arm/feature references;
they must not be mislabeled as exportable frozen linear heads.
Verify original/crop/scene/mask binding and exact coverage before encoding; reject
protected roles, mismatched hashes/geometry/cache membership. Test masked pooling,
head ablations, approval boundaries and actual trainer dispatch. Run offline Swift
build/tests. Analyze all three results with unchanged existing metrics, including
training fit, real strata, complete-frame outcomes and retention. Retain failures.

Acceptance against FDR021: artworkTP>2,totalTP>=16,FP<=3,unique>=12/14,no wrong/
multiple,retention18/18,no other-stratum regressions. These are development results
on a small repeatedly exposed set, not independent generalization qualification.
If all fail, explain the narrowed hypothesis and specific next-data/architecture
decision instead of relaunching. Context inputs use annotation boxes; detector-box
sensitivity is diagnostic and must precede any deployment claim.
