# Native focus transfer28 — assigned October2

Outcome: determine usable real-pair coverage, measure FDR036 sensitivity to scale
and appearance, and exercise an offline advisory caller. User assigned the next
substantial tranche after Native26. No data-role changes or new model fitting.

## Fixed comparisons

Use exactly the500Native26 evaluation controls, existing labels/configuration split,
FDR036 final weights and frozen ImageNet prefix. Baseline is saved common-window
predictions, replayed through the new inference path for parity.

1. Equal-size body recrops: production Swift cropper with20%context around each
   state's own measured body. This removes enlargement occupancy but also changes
   context/resampling. It is not a pure shadow experiment.
2. Body-neutralized common crops: replace pixels inside each measured rectangular
   body with fixed midgray while leaving surrounding context intact. This removes
   artwork/interior shading and retains rectangle occupancy and external appearance.
   Rectangular masking also removes rounded-corner detail. After-geometry is used
   only in this diagnostic transformation, never in runtime reference acquisition.

Frozen scores at0.5/0.85, per-background confusion and both-correct pairs. Derived
images are out-of-distribution probes: sensitivity is evidence, not proof of learned
causality. No threshold tuning, new training or independent-test claim. Bound total
model execution to1,800s, new outputs2GiB; include new forward prefix computation
for these two comparisons in this assigned scope. Keep original pixels immutable.

## Real coverage and advisory integration

Third fixed inference-only stress comparison (declared after cue results, before
stress execution): all250unfocused evaluation inputs at global RGB gain0.8and1.2,
clipped to8-bit range, retaining the unfocused label as a diagnostic construction.
Also compare saved scores across same-configuration/background unfocused content
variants and identical no-ops. These are generated counterexamples, not real events.
Keep the same30-minute/2GiB envelope; no threshold changes based on results.

Recompute readiness from existing immutable human revisions and recording events;
account for all actions. Independently known unfocused reference, native-effect
applicability and correspondence are separate from bounding-box labels. If real
artwork pairs lack those inputs, report that exact gap rather than inferring them
from proximity or a model score. Existing real metadata stays private/project-local.

Offline advisory request includes pinned image/reference identity, known-unfocused
evidence, stable same-screen context, settled state, native-effect applicability,
observation ages, in-frame reference window and neighbor/occlusion qualification.
Unknown prerequisites yield unavailable before model execution. Caller assertions
are attributed, not verified runtime telemetry. Scores are experimental and never
authorize navigation. Integrate the actual FDR036 inference path and CLI, test
eligible and unavailable requests, hash changes, geometry, finite values and bounds.

Finish focused tests, offline Swift checks, results/interpretation, task/status update
and one handoff. Real transfer remains blocked if compatible reviewed pairs are absent;
finish diagnostic and software work regardless.
