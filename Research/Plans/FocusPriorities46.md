# FOCUS-PRIORITIES-46 — controlled inference experiments

User assigned experiments to rank likely failure sources after repeated clean human
annotation reviews. Annotation error is a low-priority hypothesis; retain occasional
sampling and investigate only concrete disagreements. Owner: Codex.

Use the12approved reference sample images and18previously exposed native26development
images, six per focused item ID, selected deterministically by image hash. Pin exact
membership before inference. Data roles and annotations remain unchanged.

Three comparisons, resident fixed checkpoints, single MPS worker, at most240image
inferences initially and128MiB new outputs, no fitting or downloads:

1. Detail sensitivity: FSF001 at640versus1280, same30source images, fixed.25operating
   confidence/.001retained candidates/.7NMS. Compare focused-body IoU.50, known-unfocused
   overlaps, contained focus/competitor scores and latency. Larger input also changes
   object scale and cost; it does not isolate shadow visibility alone.
2. Position sensitivity: resize each source once to width640 and paste identical
   pixels at top/center/bottom in a640square114-gray canvas. Translate labels exactly.
   Score FSF001 at640. This preserves content scale and appearance across positions,
   while deliberately changing padding placement; it is a diagnostic intervention,
   not a new native capture or independent evaluation. Compare center-square versus
   ordinary rectangular inference separately so padding/shape effects are visible.
3. Training sensitivity: repeat the identical three-position inputs with FSF002's
   fixed ten-epoch checkpoint. Compare against FSF001 on exactly matching images,
   not aggregate numbers from different samples. This can implicate increasing
   positional sensitivity, not prove a unique causal training mechanism.

Retain raw predictions, transformed geometry, content hashes, timing, model/runtime
pins and tests for transforms/selection/scoring. Summarize per family and native focus
slot. Rank next training changes from results; no threshold tuning, data reassignment
or new annotation gate. Required offline build/test at integrated handoff. Local-only
model diagnosis does not require shared-status publication.

In-scope position confound control, after initial results: centered content uses
140px top padding; moving to0/280also changes phase modulo the detector's32px maximum
stride. Rectangular640inference uses12px padding, which shares centered phase modulo32.
Before attributing failure to position, add60FSF001inferences on the same30images with
top padding12/268(center±128). This preserves content and stride phase. Total300
inferences, same128MiB cap, same three comparisons; retain the original240-pass protocol
and results separately. This control tests translation/padding versus phase sensitivity.
