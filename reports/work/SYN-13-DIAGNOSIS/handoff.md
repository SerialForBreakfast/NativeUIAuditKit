# FDR022 offline diagnosis — October 1, 2026 PDT

**Finding: the experiment changed its source-weighting policy, not merely its
corpus. Correct this confound before declaring the new annotations ineffective or
replacing the backbone.** No training, inference, recropping, relabeling, device
operation or model promotion was performed in this diagnosis. PyTorch was used
only to deserialize and compare existing CPU feature tensors.

## 1. Confirmed weighting-policy discontinuity

| Training population | FDR021 controls / total loss mass | FDR022 controls / total loss mass |
|---|---:|---:|
| Existing fixture |710 /70.6977%|710 /27%|
| Existing OS-native |80 /9.3023%|80 /40%|
| Human-reviewed |196 /20%|196 /20%|
| Added fixture |0 /0%|564 /13%|

[Exact totals](weights.json). “Native80%/human20%unchanged” was true only for the
outer buckets. It concealed a4.3×increase in OS-native mass and a61.8%reduction in
old-fixture mass. New controls receive13%, not564/1550of the objective.

Mechanism: `focus_review_continuation.weights` preserves baseline native weights.
`focus_native_body_assembly.weighting` preserves them when additions are empty,
but for nonempty additions calls `focus_appearance_experiment.weights`, which
maps source kinds to fixture/native and balances those sources equally through
`focus_appearance_proposal.balanced_weights`. This is not the baseline's effective
policy. On the **same old790native controls with no new controls**, calling that
recomputation produces40%fixture/40%OS-native and changes all790old weights.
Therefore the discontinuity cannot be explained solely by adding564examples.

FDR022 remains a valid recorded run of its sealed objective, but is not a clean
test of the intended data-only hypothesis. Existing tests/preflight verified
normalization and outer label/source masses, not baseline sub-source continuity.
The earlier approval summary should have exposed this change. This is a confirmed
experimental confound, not proof that weighting alone caused every regression.

## 2. Cache alignment passed; real-artwork feature separation remains weak

Loaded only the pinned original928, reviewed58 and new564cached feature tensors on
CPU. Verified all three file hashes, finite1550×576training and333×576evaluation
tensors, and exact ordered labels. No encoder/head was loaded or scored.

Terminal saved training predictions at0.85:

| Group | Focused hits | False positives |
|---|---:|---:|
| Existing fixture |293/355|1/355|
| OS-native |40/40|0/40|
| Human-reviewed |12/12|0/184|
| Added fixture |125/137|0/427|

The added synthetic examples are largely fit, while retained real artwork remains
2/12hits with6false positives. Training fit and real transfer are different results.
This supports a domain/representation concern but does not isolate it from weighting.

Descriptive cosine-neighbor check on retained576-dimensional features: for8/12real
focused artwork controls, the closest unfocused training vector is closer than the
closest focused one. Same-control synthetic focused/unfocused comparisons cover112
source-element groups; these are deterministic first-available comparisons, **not112
captured temporal pairs or independent tests**.32have >8%growth on both axes.
See [feature findings and exact IDs](features.json). Cosine proximity is not model
accuracy, linear-separability proof, an alternative selector or a threshold policy.

## 3. Correct body bounds normalize away absolute growth

Production `FocusRingClassifier.expandedCropRect` expands each side by16%of the
current box and stretches the crop to256×256. Away from clipping, the body occupies
1/1.32≈75.76%of each input axis regardless of original control size. Growing the
body and its crop together therefore removes the direct absolute-size cue; it does
not remove every focus cue. Fractional rounding, shadows and neighboring content
can still differ. Wider proportional margins alone do not restore absolute scale.

Inspected existing tab-content-light/control004 crops: focused bounds832×515,
unfocused752×464.8. Both display approximately194pixel-wide bodies after resize;
focus rim, shading and neighbor position differ. Cached cosine similarity0.96721.
Correct enlarged annotations should **not** be replaced with wrong wrapper bounds.

Focused:
![Focused native card](</Users/josephmccraw/Documents/GitHub/NativeUIAuditKit/reports/work/SYN-07-READINESS/artifacts/palette-review/crops/frame-fce72d54d188b7979a55e794--control-004.png>)

Unfocused:
![Unfocused native card](</Users/josephmccraw/Documents/GitHub/NativeUIAuditKit/reports/work/SYN-07-READINESS/artifacts/palette-review/crops/frame-0c50f348ca6e96125801f483--control-004.png>)

Reviewer observation: these simple moon cards differ materially from the inspected
real Prime Video hero and FOX sports card crops, which contain dense text/photos.
Only these four crops were visually inspected in this diagnosis; no exhaustive
visual or label-correctness claim is made. Native bounds preserve geometry in the
dataset, but current model input has no explicit original-size or sibling-size channel.

## Ranked next action

1. **First: repair/version weighting continuity.** Explicitly preserve baseline
   OS-native9.3023%, total fixture70.6977%, human20%budgets for a controlled data
   comparison. Keep OS/human members' exact weights; distribute only the fixture
   budget across old+new fixture members under a documented policy. Add no-addition
   identity and per-source/per-label mass regression tests, inspect exact old/new
   weight deltas, then approve one reweighted cached-feature run. No new images or
   feature encoding needed. These budgets are a comparability control, not claimed
   optimal weights. Do not silently apply this proposal to existing protocols.
2. **If that controlled result still fails:** design one context/geometry-aware or
   partial-backbone experiment. Use a stable frame/neighborhood context or explicit
   relative geometry to retain scale; compare on identical membership and keep
   deployment parity in scope. Do not jump directly to a35%margin or assume it fixes
   growth. Frozen generic features remain a plausible limitation, not proven cause.
3. **Retain the improved data flow.** Human acceptance, native geometry, cache
   integrity and fast model execution worked. Do not request more manual annotation
   or duplicate corpus generation as a substitute for isolating the failed variable.

## Verification and boundaries

Read-only diagnostic calculations; no implementation edits, so no new Swift build or
test claim. Existing metrics/predictions and pinned caches only. Source grouping
and threshold unchanged. No final-challenge analysis. Outputs are descriptive and
local, not model admission or promotion. FDR021and rejected FDR022preserved.

Software: identified policy mismatch, no fix implemented. Data: no labels or roles
changed. Integration: cache hash/shape/label checks pass. Model: no new execution;
FDR022failure stands with weighting confound explicitly recorded. TTR coordination
not applicable: this local finding changes no producer next action. Next repair
and controlled training require a separately assigned tranche.
