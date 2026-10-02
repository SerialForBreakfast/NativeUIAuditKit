# Alignment12 isolated follow-up: equal visible support

Recorded after the frozen translation-only replay, before follow-up execution.
Primary found the161pxscroll (estimate158.44px) but rejected63cases at unequal
viewport clipping, including seven forward retention rows. Do not change matching,
correlation, reciprocal or focus thresholds. Preserve original receipts/results.

Replace only clipping-footprint rejection with a common-support window: compute
the maximum missing context on each side across before and translated windows;
trim that same amount from BOTH windows. Convert the remaining expanded rectangle
back into a native makeCrop request. Equal dimensions/relative offsets preserve
scale; this is not independent per-state fitting. Reject if trimming removes any
of the nominal control body, or if native rounded dimensions differ. Edge-growth
remains unavailable for these clipped contexts; brightness remains the same rule.
Use translation from pixels only, never after truth bounds. Preserve original
before/translated control bounds separately from adjusted crop-request bounds.

Expose this as a separate opt-in diagnostic flag. Repeat all retained cases,
actual CLI examples, stress/negative checks and pixel-scale invariants. No training,
capture, parameter search or production promotion. If source templates scale enough
to defeat translation matching (Home artwork), remain uncertain; no hidden fallback.
