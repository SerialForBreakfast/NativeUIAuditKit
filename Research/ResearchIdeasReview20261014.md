# Research ideas for Standard UI detection and focus

Date: 2026-10-14. Status: recommendations for discussion, not execution approval.

This review summarizes the supplied research survey and explains how each idea could serve NUIAK and TTR.
Standard UI detection, classification, and focus remain the main goals. HCF stays optional and separate.
The strongest near-term opportunities are reusable evaluation, constrained output-layer fitting, and better use of control boundaries.
Alternative detectors deserve a separate feasibility study after we measure the current proposal failures.

The supplied survey is a secondary source. Its runtime estimates and predicted accuracy gains are not NUIAK measurements.
Primary sources below establish methods and tooling, not successful transfer to our models.
No packages, models, jobs, or running processes change during this review.

## Priority overview

| Priority | Idea | Main question |
| --- | --- | --- |
| P0 | Batch compatible evaluation in the existing framework | Can we reduce repeated loading while preserving identical results? |
| P0 | Review previous constrained fits, then test a justified head constraint | Can existing features solve the failure without losing required training examples? |
| P1 | Boundary features and geometry-aware score combination | Does better use of visible detail fix measured Standard failures? |
| P1 | Small, fixed weight-interpolation comparison | Can compatible checkpoints combine useful behavior without training? |
| P1 | Profile preprocessing and compression | Which measured runtime or delivery cost is worth correcting? |
| P2 | Alternative detectors and screen-level selection | Can a different proposal or selection method improve the complete pipeline? |
| P2 | Contrastive training and targeted generation | Can carefully controlled examples improve transfer beyond existing methods? |
| P3 | Large-model annotation assistance and MLX migration | Do review savings or measured speed justify additional dependencies? |

These priorities rank investigations, not automatic deployment changes.
The [Standard roadmap](ProductRoadmap.md) and [STANDARD390](Plans/Standard390.md) provide the current scope and retained comparisons.

## Detector alternatives

### 1 D-FINE Nano and Small

**Idea:** refine predicted box distributions to improve localization.

**Fit:** better control-body boxes could improve both UI detection and downstream focus crops.
The official repository supplies custom-data training and identifies an Apache-2.0 license.
Its table reports about 4 million parameters for Nano, not evidence of a small Core ML package. [D-FINE source](https://github.com/Peterande/D-FINE)

**Recommendation:** P2 feasibility study. Test conversion and memory before a full training comparison.
Then use the same eligible UI groups, class mapping, and training budget as a retained detector control.
Measure focused-target recall, localization, classification, false selections, and Apple runtime cost.

**Limit:** COCO accuracy does not establish UI accuracy or eliminate box jitter.
A CNN backbone does not guarantee that every decoder operation runs efficiently on the ANE.
Do not assume ONNX export provides a supported direct Core ML conversion path.

### 2 RF-DETR Nano and LW-DETR

**Idea:** use transformer detection and set prediction to reduce reliance on hand-tuned suppression of overlapping boxes.

**Fit:** potentially useful for nested controls, cards, captions, and badges.
RF-DETR and LW-DETR are distinct implementations, not interchangeable Nano and Tiny variants.
The current RF-DETR table lists Nano at 30.5 million parameters with Apache-2.0 terms.
Other variants have different terms. [RF-DETR source](https://github.com/roboflow/rf-detr), [LW-DETR source](https://github.com/Atten4Vis/LW-DETR)

**Recommendation:** compare one selected candidate after the smaller detector feasibility check.
First establish supported operators, peak memory, export behavior, and inference cost.
An end-to-end detector still needs confidence selection and duplicate-error testing.

**Limit:** the name Nano does not establish suitability for our memory or package budgets.
Check the exact checkpoint license, not only the repository license.

### 3 OmniParser interactive-region proposals

**Idea:** use a detector trained on screenshots to propose small interactive regions.

**Fit:** useful as an offline proposal baseline or a source of review suggestions.
It does not supply NUIAK's full class taxonomy or native focus truth.

**Recommendation:** test proposal recall on retained UI screenshots before considering integration.
Measure unmatched proposals, duplicate boxes, class gaps, and review effort.

**License detail:** the current README describes `icon_detect_v3` as based on MIT-licensed YOLOv9.
It directs users to an inference-only checkpoint in Hugging Face PR 37.
Earlier Ultralytics detectors retain AGPL terms; the repository also identifies CC-BY-4.0 licensing.
Review each component and checkpoint separately. [OmniParser source](https://github.com/microsoft/OmniParser)

Changing future detectors does not remove obligations attached to existing code or weights.
No automatic model download or checkpoint deserialization follows from this recommendation.

## Visual detail and context

### 4 Ring and interior feature pooling

**Idea:** summarize boundary features separately from interior artwork, then compare both summaries.

**Fit:** directly addresses bright artwork that resembles focus and subtle boundary effects that global pooling can dilute.

**Recommendation:** P1 comparison against the unchanged crop model using identical training and evaluation groups.
Use geometry-aware masks or measured feature locations. Compare interior-only, boundary-only, and combined features.
Include white artwork, decorative borders, weak shadows, wide rows, clipping, and unfocused examples.

**Correction:** a fixed outer band on an 8 × 8 feature map does not necessarily align with the rendered control boundary.
Padding, aspect ratio, and receptive fields matter. The proposed change also expands the classifier input and needs retraining.
It is neither zero-cost nor guaranteed to remove artwork errors.

The supplied V2P title is not established by its cited identifier.
That identifier resolves to FocusUI, a different method. Treat ring pooling as our experiment, not a verified V2P result.

### 5 Position-preserving detail and scale-aware fusion

**Idea:** preserve location and scale when using high-resolution detail windows.

**Fit:** could help a transition model avoid letting a weak whole-frame representation dominate useful small-control detail.
FocusUI preserves positional information during token selection in a large grounding model.
It does not validate the proposed sigmoid gate for NUIAK. [FocusUI paper](https://arxiv.org/abs/2601.03928)

**Recommendation:** compare size-only, size-plus-position, and no-metadata combinations on matched views.
Include content-only changes with the same changed area as genuine focus movement.
Balance edges and corners; coordinates can introduce new location shortcuts.

**Limit:** a small difference region is not proof of focus change.
The attachment does not identify its separate MVP reference precisely enough to adopt paper-specific claims.

### 6 Large GUI models as annotation assistants

**Idea:** use UI-TARS, OS-Atlas, ShowUI, Aria-UI, or related vision-language models to suggest boxes and semantic labels.

**Fit:** optional offline support for difficult annotation cases, not the default NUIAK runtime.
OS-Atlas and ShowUI provide primary examples of GUI grounding and action models. MLX-VLM supports local vision-language workflows.
[OS-Atlas](https://github.com/OS-Copilot/OS-Atlas), [ShowUI](https://github.com/showlab/ShowUI), [MLX-VLM](https://github.com/Blaizzy/mlx-vlm)

**Recommendation:** P3 pilot on a small reviewed set. Measure reviewer time, corrected boxes, missed controls, and invented labels.
Keep every suggestion unverified until reviewed. Do not grant navigation authority or upload private captures.

**Limit:** the claimed 2.2 GB memory use and 0.8 s latency are not measurements on our hardware.
Quantized weights exclude image tokens, activations, and runtime overhead from their file-size estimate.
Exact UI-TARS, Aria-UI, and Qwen variants need separate checkpoint and license checks before selection.

## Training and checkpoint methods

### 7 Project the optimizer update instead of the raw gradient

**Idea:** adjust the proposed parameter update when it opposes a preservation objective.

**Fit:** could explain why a raw-gradient correction fails to preserve native behavior with an adaptive optimizer.
A-GEM supplies related continual-learning methods. The proposed Adam-update procedure is an adaptation, not the original method.
[A-GEM paper](https://arxiv.org/abs/1812.00420)

**Recommendation:** first measure the actual update against preservation gradients.
Compare a simple optimizer without momentum before adding custom projection and optimizer-state handling.
Use only eligible training examples for constraints. Preserve evaluation exclusions.

**Correction:** a nonpositive gradient dot product supplies a local first-order condition.
Finite updates, curvature, and numerical error can still increase loss. It does not guarantee unchanged decisions or unseen accuracy.
The attachment's example ratio is also wrong: 34.97163 divided by 0.06303 is about 555, not 139.

### 8 WiSE-FT weight interpolation

**Idea:** combine compatible checkpoint weights rather than their final probabilities.

**Fit:** our retained review identifies compatible model structures. Weight interpolation remains distinct from the already-rejected probability blending test.
[Local compatibility review](Focus360LocalAnswers.md), [WiSE-FT paper](https://arxiv.org/abs/2109.01903)

**Recommendation:** P1 bounded comparison with a few predeclared coefficients and both unchanged endpoints.
Require common initialization, matching tensor meanings, matching preprocessing, and correct handling of model buffers.
Select coefficients on development data only. Run every previous-success comparison for any candidate.

**Limit:** matching shapes alone do not prove compatible features.
Nonlinearity permits different behavior; it does not guarantee recovered movement or retained appearance gains.
Checkpoint arithmetic may be cheap, but complete evaluation still takes time.

### 9 Constrained fitting of a linear output layer

**Idea:** fit a fixed-feature classifier while imposing margin constraints on eligible preservation examples.

**Fit:** a useful way to distinguish inadequate features from an inadequate fitting method.
CVXPY supports convex objectives and constraints, with explicit solver status. [CVXPY documentation](https://www.cvxpy.org/tutorial/intro/index.html)

**Recommendation:** P0 review of previous constrained-head work before another fit.
Reuse its feature matrices and infeasibility evidence where compatible. Compare against the existing head on identical inputs.
Check solver tolerances, constraint residuals, exported decisions, and previous successes independently.

**Corrections:** guarantees apply only to enforced constraints on the fixed features within verified numerical tolerance.
Training against retained evaluation cases would consume their evaluation role.
With only preservation constraints, infeasibility does not automatically identify a conflicting new training example.
Solvers do not always return useful dual variables for infeasible problems. Use explicit slack or conflict analysis.
L-BFGS-B supports box bounds, not general example-level linear inequalities by itself.
Neither global solution quality nor a 0.4 s runtime follows merely from selecting a solver.

## Apple runtime and throughput

### 10 Palettize model weights

**Idea:** reduce weight storage with a small shared palette of values.

**Fit:** relevant when the exact candidate exceeds its delivery budget.
Apple documents palettization and measured performance tradeoffs. Some listed configurations reduce size without reducing latency.
[Apple overview](https://apple.github.io/coremltools/docs-guides/source/opt-palettization-overview.html), [Apple performance](https://apple.github.io/coremltools/docs-guides/source/opt-palettization-perf.html)

**Recommendation:** test 6-bit compression first when a candidate needs it, against its unchanged FP16 package.
Measure the actual artifact governed by the gate, runtime memory, cold/warm latency, output error, and changed decisions.
Check deployment support and resident tool compatibility before selecting compression options.

**Limit:** keeping the first and final layers in FP16 does not guarantee parity.
The 5,000,000-byte FocusRing gate is not a universal size limit for every NUIAK model.
The quoted 2.37× speedup and package size are not established for our candidate.

### 11 Faster image resizing and preprocessing

**Idea:** reuse resize coefficients and accelerate separable filtering.

**Fit:** valuable if current measurements still show preprocessing dominating inference.

**Recommendation:** profile decode, color conversion, crop, resize, and tensor packing separately.
Benchmark an optimized implementation against a pinned reference on fractional crops, clipping, odd dimensions, and extreme aspect ratios.
Test pixels and final decisions. Keep production preprocessing unchanged until parity qualifies.

**Corrections:** Pillow includes coefficient handling, rounding, and clipping; generic floating-point matrix multiplication does not establish bit-exact parity.
The proposed dense matrices for 4K-to-192 × 128 contain 1,013,760 coefficients, about 4.1 MB in float32, not 15 KB.
Sparse or separable tables can differ in size. A nonzero error of 2.868e-7 is not bit-identical output.
The claimed 200× speedup needs measurement. [Pillow resize implementation](https://github.com/python-pillow/Pillow/blob/main/src/libImaging/Resample.c)

### 12 Batched evaluation with cached features

**Idea:** score several compatible heads over shared features in one process.

**Fit:** high-value efficiency work within the current queue. It reduces repeated loading without changing the scientific question.

**Recommendation:** P0 implementation study using resident PyTorch first.
Compare measured runtime and all outputs against separate execution. Preserve per-condition results, resumability, and failure isolation.
Key caches by inputs, encoder weights, preprocessing, and settings. Use bounded batches from USB.

**Limit:** a matrix multiplication replaces only compatible linear heads over identical features.
It cannot replace changed encoders, nonlinear correction stacks, decoding, or full detector evaluation.
MLX migration is a separate comparison; the attachment does not establish a sub-0.3 s full-suite runtime.

## Larger experimental opportunities

### 13 Contrastive focus training

**Idea:** pull compatible focused examples together while separating focused and unfocused examples with matched artwork.

**Fit:** could reduce artwork dependence and strengthen transferable focus features.
Supervised contrastive learning supplies the general method, not a guarantee about learned focus geometry.
[SupCon paper](https://arxiv.org/abs/2004.11362)

**Recommendation:** P2 comparison against ordinary supervised training with the same groups, initialization, and compute budget.
Control artwork, family, profile, and repeated-image exposure. Include hard negatives from the same control.

**Correction:** the proposed positives use focus labels, so this is supervised contrastive learning, not training on unlabeled captures.
It cannot force every feature channel to represent focus geometry. Training time and memory need a measured pilot.
Keep Standard and HCF runs separate unless an explicit transfer comparison requires both.

### 14 Screen-level focus selection

**Idea:** compare all proposed controls jointly and choose a control or abstain.

**Fit:** addresses the limits of isolated crop scores and ambiguous neighboring controls.

**Recommendation:** test a simple peer-aware classifier before a transformer.
Compare raw scores, relative scores, geometry, and then a small set model if simpler methods fail.
Test missing proposals, decorative controls, single-control scenes, variable counts, and ordering changes.

**Corrections:** a singleton choice does not require Hungarian matching.
A rejection option should distinguish unknown focus from verified no-focus scenes.
The proposed projection from 580 inputs to 64 features already needs about 74 KB of FP16 weights, before transformer layers.
The 35 KB and 99.9% confidence claims are unsupported.

### 15 Search for difficult generation settings

**Idea:** use model failures to select rendering conditions rather than repeatedly generating broad grids.

**Fit:** a useful TTR feedback path after a producer and its labels qualify.
Optuna supplies bounded optimization tools, not evidence that generated difficulty transfers to real apps.
[Optuna source](https://github.com/optuna/optuna)

**Recommendation:** P2 comparison of targeted selection against uniform selection at equal generation and training budgets.
Start with existing deterministic selection before adding a search dependency.
Include confident errors as well as uncertain cases. Preserve diversity and duplicate checks.

**Limit:** uncertainty alone misses confidently wrong predictions and can select rendering defects.
Search only development conditions. Freeze an independent evaluation set and do not admit synthetic labels automatically.

### 16 Boundary gradients and frequency features

**Idea:** provide explicit edges or boundary gradients alongside RGB evidence.

**Fit:** a cheap diagnostic for whether Standard growth, shadows, and borders contain useful signals beyond interior appearance.

**Recommendation:** P1 diagnostic using fixed RGB, edge-only, and RGB-plus-edge comparisons.
Keep the original input unchanged. Test background textures and decorative borders as negatives.

**Corrections:** Sobel gradients and FFT features are different methods. Test them separately if both remain justified.
Do not replace the blue channel silently or use ground-truth bounds as deployable input.
Report known-box results separately from results using actual proposals. Any added channel needs a new preprocessing contract and Core ML parity check.

## Adoption order and safeguards

The supplied roadmap ranks solver, interpolation, compression, ring pooling, resizing, and detector replacement as immediate small changes.
Those line-count estimates omit qualification, data preparation, tests, and Apple integration.
Use this order instead:

1. Review STANDARD390 results and earlier constrained-fit results. Do not repeat questions they already answer.
2. Batch compatible evaluation and measure its actual benefit.
3. Select one justified fixed-feature or weight-interpolation comparison.
4. Test boundary features or scale-aware fusion against a measured Standard failure.
5. Optimize preprocessing or compression only against a current measured bottleneck.
6. Qualify one alternate detector before spending a full training budget.

Each accepted experiment needs fixed inputs, roles, a matched control, measured costs, and a next decision for either outcome.
Preserve previous successes and existing model gates. Report incorrect selections and abstentions, not only average accuracy.
Keep iOS and tvOS outcomes separate. Fixture accuracy does not establish real-app or physical-device accuracy.
Runtime budgets come from each approved job, not this attachment's assumed universal memory and storage limits.

The cited V2P title, MVP identity, Hacker News hardware claims, and some large-model variants remain insufficiently specified or unverified here.
Do not use them as implementation authority. The official method and tool sources above support bounded experiments instead.
This summary creates no execution assignments. Tasks.md remains the sole ownership queue.
