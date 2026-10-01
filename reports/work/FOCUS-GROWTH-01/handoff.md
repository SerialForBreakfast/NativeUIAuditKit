# Growth-cue analysis — October 1, 2026 PDT

**Conclusion:** the current per-control proportional crop removes almost all
absolute body-growth information. Accurate enlarged bounds remain correct labels;
the model input needs additional scale/context, not deliberately incorrect boxes.
Analysis complete. No production preprocessing, model, cache or annotation changed.

## Measured retained evidence

Used112same-source/same-element focused/unfocused comparisons from the admitted
corpus,116unique source images. Image hashes verified and dimensions read; all
comparisons share a3840×2160viewport. These are first-available state comparisons,
not112qualified temporal transitions. No final-challenge inputs were examined.

32comparisons grow by more than8%on both axes; all32expanded crops are interior,
so viewport clipping does not explain the result. The8%cut is an explanatory
subset definition, not a new focus threshold, label rule or qualification gate.

| Size signal in32growth comparisons | Median width ratio | Median height ratio |
|---|---:|---:|
| Original body bounds |1.166667|1.180952|
| Current256×256crop (analytic raster geometry) |1.000902|1.000462|
| Common full-frame scale |1.166667|1.180952|

Maximum residual proportional-crop size difference is0.115%, explained by source
canvas rounding. This is geometric projection, not measured segmentation of rendered
pixels or a newly rendered preprocessing parity test. Shadows, color, edges and
neighbor positions can still differ and provide focus evidence.

Exact IDs, original ratios, projected ratios and source-input hashes:
[geometry-analysis.json](geometry-analysis.json). Shared full-frame scaling preserves
ratios across all112comparisons to floating-point tolerance (max error2.22e-16).
For a hypothetical768×432scene branch, the32growing bodies are104–169.6pixels wide
when focused. This resolution is an analysis reference, not a qualified model default.

## Where the information is lost

`FocusRingClassifier.expandedCropRect` expands each side by16%of the current box.
`redrawCrop` rounds that crop's canvas and scales it to256×256. Ignoring clipping
and rounding, a body of widthw has output width `256*w/(1.32*w)=193.94`, independent
ofw. A10%,17%or20%enlargement scales its crop along with it.

`NativeUIDetectionRequest.resolveTVOSFocusWithEvidence` has the original screenshot
and all candidate boxes, but supplies each candidate's crop alone to the scorer.
`FocusRingClassifier.classify` supplies only that image to CoreML; no original
width/height, viewport, siblings or previous-frame geometry reach the model.
Winner selection occurs after independent scoring and cannot recover discarded
size information. This is an input limitation, not proof the encoder cannot use
other cues or proof of the cause of every FDR022error.

The new annotations correctly include the larger rendered body. Reverting them to
an unfocused wrapper to create an apparent scale change would reintroduce a geometry
error and mismatch production detector boxes. Also, changing16%to35%or applying
aspect-fit to each dynamically sized crop does not preserve uniform absolute growth:
the target still determines the normalization scale.

## Recommended single-screenshot input design

Keep the existing detailed local crop, **add a shared scene-context representation
whose scale depends on the viewport, not the candidate**, and identify the candidate
inside that context:

1. Local branch: current256×256crop for edges, glow, text and shading.
2. Scene branch: one aspect-preserving full-frame resize/letterbox shared by every
   candidate in that screenshot. Candidate mask or spatial box encoding identifies
   the target without rescaling it to a standard size. Scene features can be reused
   across candidates; latency savings must be measured, not assumed.
3. Geometry: normalized current box `(x/W,y/H,w/W,h/H)`, clipping/availability flags,
   and optional geometry of comparable visible neighbors. Preserve target position,
   aspect ratio and size relationships; do not feed focus labels, requested focus,
   native focus callbacks or known unfocused size into the prediction inputs.
4. Fuse local appearance, context and geometry to score each candidate. Keep the
   current selection/abstention policy until a separately approved policy experiment.

A large naturally unfocused hero can exceed a small focused control. Size is evidence
to combine with comparable neighbors and appearance, not a largest-box rule. Mixed
aspect ratios, singleton controls, zoom, scroll, clipping and selected-but-unfocused
parents must be represented. Do not infer a peer group from the focus label.

This design **preserves available size evidence**; it does not demonstrate that an
untrained fusion model will use it correctly. A single screenshot cannot prove a
temporal size change without a baseline; it supports relative/contextual inference.

## Optional later temporal lane

For an actual tracked before/after sequence, retain a common spatial scale and
aligned region, stable target correspondence, viewport/scene identity, timestamps,
action receipt and settled/no-op cases. Then width/height/area change can be explicit
features alongside appearance. Never use a union of known focused/unfocused training
boxes as though it were available to a single-frame deployment. Current112state
comparisons do not qualify action causality, motion tracking or a temporal model.

## TTR and consumer responsibilities

Existing deliveries preserve the original screenshots, viewport dimensions,
per-frame rendered-body bounds, source element IDs, native observation provenance
and wrapper/body distinction in raw review records. That is sufficient to prepare
the proposed **static** growth-preserving input experiment locally. No new capture
or TTR build is required for this analysis. Optional wrapper/reference size is audit
or privileged supervision unless independently available at runtime; it is not a
required prediction feature. No additional TTR request was published.

NUiAK must carry the scene scale and target geometry into the model and export path.
Human/native ground-truth boxes remain supervision; deployment uses detector boxes.
Evaluate box localization error and jitter explicitly so oracle annotation geometry
does not masquerade as end-to-end performance.

## Implementation and acceptance path (not executed)

1. Repair the SYN-13weighting discontinuity and freeze a comparable baseline first.
   Do not mix that repair with a representation change and call it one-factor testing.
2. Implement a versioned experimental local+scene+geometry input builder. Preserve
   original files and current production16%/256path. Emit transform/candidate mapping
   and missing/clipped states; never synthesize geometry from labels.
3. Verify growth preservation with positive and negative input tests: equal/10%/20%
   scale changes; globally resized screenshots with invariant normalized geometry;
   aspect changes; edge padding; mixed-size neighbors; no-growth focused controls;
   same-size different focus appearance; unavailable history. Compare actual pixels
   and model-bound geometry in Python and Swift/CoreML, not just analytic formulas.
4. Freeze identical membership, source budgets, initializations and decision metrics
   for current-input versus growth-preserving-input experiments. New feature encoding
   and training need exact approved budgets. Leave protected tests untouched.
5. Demonstrate real artwork gains without higher FP or worse frame selection/retention.
   Report growth/no-growth strata and detector-box sensitivity. Only a passing
   candidate proceeds to export parity and observer-only TTR testing.

## Outcome

Software: input limitation traced; no implementation changed. Data: retained geometry
and116source-image identities checked, labels/roles unchanged. Integration: analytic
size-preservation proof, not a new pixel-path or CoreML qualification. Model: no new
inference/training or learning claim. Analysis was local; no device/producer action.
