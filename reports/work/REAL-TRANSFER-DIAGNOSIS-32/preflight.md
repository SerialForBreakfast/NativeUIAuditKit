# Initial preflight

First invocation stopped before model construction with reference_context_clipped
on review1. Four of six new pairs have wide rows whose20%window exceeds the image.
The original `scored/authorization.json` is preserved; no predictions were emitted.
Correction: explicitly record production-clamped context as offline diagnostic;
live gate unchanged. Valid fully contained versus clipped results are separated.
The completed run uses `scored-clipping-aware/`, not an overwrite/retry of model training.
