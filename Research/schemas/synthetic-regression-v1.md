# Synthetic regression suite v1

`synthetic-regression-v1` freezes an ordered diagnostic subset without using model
errors. Selection is deterministic from `seed: 42` and strata of family, class,
aspect bucket, and small-element presence. Every member records source split/platform/
family, image and label SHA-256, dimensions, and selector version. Missing pixels or
labels, source/content/family overlap with train/val, and membership changes fail;
coverage gaps are explicit rather than silently filled.
