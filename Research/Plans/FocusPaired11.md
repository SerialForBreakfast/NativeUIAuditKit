# FOCUS-PAIRED-11 — does before/after preserve useful focus evidence?

Assigned October1,2026: next LARGE tranche. Owner Codex. Complete the retained
evidence experiment, not just input preparation. No new captures, annotations,
source-role changes, downloads, protected tests, export or production replacement.

Reuse accepted1562training/333evaluation membership and original source frames.
Native same-control focused/unfocused pairs are static contrast probes, not
recorded actions. Reversed endpoints and identical-image no-ops are constructed
controls. Real reviewed same-family frames may support geometry-matched contrasts;
never treat per-image local annotation IDs as cross-frame stable IDs. Audit every
excluded/ambiguous case and preserve the genuine-action review gap separately.

Use the existing native makeCrop with one fixed **before-frame** rectangle for both
images (16%context/256square). This preserves relative growth within that window.
No after-frame truth box or focus label enters pixel prediction. Oracle measured
box ratios are a separately named upper-bound diagnostic, never the visual result.
Production per-state crops remain the normalization control. Starting geometry is
reviewed/native, so even pixel-only results are not end-to-end detector qualification.

Freeze a simple rectangular-edge probe before scoring: central-half row/column
mean gradient profiles; before edges searched24..48/208..232, after edges8..64/
192..248; mean edge strength>=.015; axis ratio agreement<=.06 and center drift
<=8pixels. Growth>=1.05both axes indicates arrival; shrink<=.95 indicates departure;
otherwise unknown. Brightness comparison keeps prior signed luma threshold.08.
Combine only agreeing signals or one signal with the other unknown; disagreement
abstains. Exact same image is unchanged, not an initial-focus answer. Perturbed
or changing imagery never gains a ground-truth label from the rule.

Compare frozen rules on native pairs (descriptive, in-training), separate real
development contrasts and9retention pairs. Match real candidates with same control
role and mutual unique center proximity, maximum.15of smaller box dimension;
require same-family, same viewport and equal visible control count for a frame
contrast. This is a scoped correspondence assumption to stress, not identity proof.
Use accepted annotation labels solely to score arrival/departure/unchanged.
Reuse retained FDR021before/after scores for an equivalent transition baseline:
both confident>=.85 or<=.15; mixed-confidence cases unknown. Frame-level target
selection requires exactly one arrival, never largest-change guessing.

Include label-blind software stress cases for uniform illumination, shift, content
replacement, contradictory axes, missing/stale/unstable/wrong-scene input and invalid
geometry. Preserve raw measured false results, then distinguish any externally
supplied safety gate from visual recognition. Do not deploy based on toy passes.

Decision: pursue paired visual learning only if contrast improves useful arrivals
without extra wrong selections/unchanged false moves against the matched baseline.
Report available coverage and abstention, per-family and frame-pair results, measured
costs and limitations. If ambiguity/matching/signal fail, complete the diagnosis and
give a narrow next collection/representation request instead of forcing another fit.
Neural training is conditional on credible paired support; no uninformative fit is
required to spend the experiment budget. Preserve unchanged333static evaluation.

Deliver: integrated offline CLI, inventory+source hashes, fixed-window native pixels,
matched comparison and failure examples, adversarial tests, offline build/tests,
updated docs/status and actionable peer consequence. Outputs<=2GiB; bounded replay
<=30minutes; no background monitor or live operation.
