# Run027/028 matched native-style comparison — October 6

Both registered ten-epoch runs completed with245optimizer updates: control4691.52s,
treatment4596.36s. Fixed-last hashes:

- Run027: `0cd43172ba947576e30d48007b1da939dee51c713b63dd40cb1cb9828d323243`
- Run028: `df8e8f18a2d124ebc6207e5c482c81c37c9aed22e7bd87e60fba20f314af8db8`

The treatment replaces336balanced repeats of old crops with336new qualified native
style crops; both retain1509training slots, initialization, epochs and optimizer
schedule. No evaluation membership or thresholds changed. One seed, not a statistical
generalization claim; MPS nondeterminism remains documented.

## Same-backend results

Existing scripts completed exit0 in session41011: each arm's `train_style210 infer`,
`report`, and `evaluate_style210_extra`. All2,306crop prediction records succeeded;
zero empty/failed. Original full-frame inputs are reused, not inferred again. Metrics
are the existing custom implementation, not newly claimed official COCO results.
Fit is training diagnostic; page is development; combined is retained evaluation,
not a newly independent final corpus. TP/FP use the frozen operating point.

| Path / population | Page TP control→treatment | FP | Page AP50 | Page AP50:95 |
|---|---:|---:|---:|---:|
| Refinement / fit216 |199→199|24→24|.91570→.91570|.80375→.79263|
| Refinement / development96 |58→58|14→14|.61926→.61926|.45043→.45407|
| Refinement / retained600 |249→249|24→24|.85840→.85840|.54160→.52962|
| Extra proposal / fit216 |202→202|38→38|.92080→.92080|.54547→.54694|
| Extra proposal / development96 |72→75|16→14|.73818→.76448|.43317→.46503|
| Extra proposal / retained600 |533→543|24→24|.93196→.93877|.61794→.62505|

All non-page per-class rows, operating points and metric implementations exactly
match between arms in both paths. Thus this is a bounded page-control intervention,
not evidence of improvements to other classes.

Refinement-only still fails8existing gates. Extra proposal still fails7:
trailing, pageFP, sheetAP, scrollIndicatorAP, sheetFP, cancelActionFP, mapViewFP.
Trailing fit support remains58/72hits with14localization misses in both extra arms.
No promotion, DS-G8 pass or automatic additional training. The useful gain is modest
extra-proposal recall/precision; more of the same style data has not solved trailing
localization or broader inherited detector failures.

## Reproducibility and worker feedback

Report SHA256s under `artifacts/training01/<arm>/<path>/evaluation.json`:

- control/candidate: `1966e00f8095549471280988503ecaa2403e6496b24662ecfcbdddc9819b7422`
- treatment/candidate: `5ac8cd49879d19eec761b88e9d811d0355f494372de24664dd164088f27975cd`
- control/extra-proposal: `549df7ebe9cbe02edfd3b8b2b57b4afa75c0c4c33d4f798c0e8567b165038082`
- treatment/extra-proposal: `1a379a4963e1eb148c2c14bf1b28b1161c4a455c4288d37104955ecfe9ed657d`

Refinement inference32.75/31.90s; extra-path execution including report47.21/47.49s.
Logs `.build/style210-evaluation.log`. Existing strict report entrypoints verified
checkpoint, source, membership, bounds and unchanged non-page outputs. No code change
required for scoring; reuse verified offline software tests.

Big Dog received a published checkpoint-only request, not another image bundle;
receiver acknowledgment/results pending. Compared its retained Run027 CUDA artifacts
to local MPS on all585inputs: same image IDs/statuses/counts, but none byte-exact.
Class-order aligned583/585rows have maximum coordinate difference.001953125pixels
and score difference.0000211895. Two combined rows reorder class entries, so they are
not included in those numeric maxima. Do not declare universal backend parity from
this check. Resulting frozen page metrics match for control; future paired worker
results still need independent validation.

## Next substantial work

Complete Run028 worker intake and matched CUDA report without repeating control.
Then diagnose the14persistent trailing localization misses using retained crops,
geometry and predictions before selecting a different training hypothesis. Keep
the native-focus capture-source request open and prioritize its admission when
evidence arrives; no label/provenance gate is relaxed to fill worker idle time.

Software verified; existing data roles unchanged; local comparison integrated;
model gates failed. Shipped models and rollback artifacts remain intact.
