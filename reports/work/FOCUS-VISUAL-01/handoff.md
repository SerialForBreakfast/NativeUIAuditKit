# FOCUS-VISUAL-01 — different-appearance regression evidence

2026-09-22. Assigned local comparison tranche complete for review. No model promoted.

| Outcome | Evidence |
| --- | --- |
| Software verified | Nine targeted regressions and87 Focus tests pass; offline Swift build,93 Swift Testing and14 XCTest tests pass |
| Data eligible | Two legacy Photos frames/four visual-review boxes, development-only;28 correlated box variants, not28 new examples or training pairs |
| Integration qualified | Three real CoreML models exercised through production `FocusRingTool`,16% expansion/256×256 crop, bounded CPU inference; no TTR/device integration |
| Model gate passed | Not assessed for release; experimental candidates fail appearance detection here, and expanded compression probability tolerance fails one sensitivity case |

## Frozen comparison

[Protocol](protocol.json) binds the PER-DATA review, exact images, runtime and three
compiled model hashes **before inference**. [Full result](evaluation/report.json)
retains84 predictions:28 crops per model, generated from four reviewed boxes using
base and six ±4px translations/padding variants. No threshold tuning or weight change.
[Summary](summary.json) retains per-model probabilities, frame decisions, latency,
box sensitivity and compression differences. The two Photos frames stay in their
unknown-journey development group; they were not moved to a final test set.

| Base, threshold0.85 | Shipped | FDR-007 FP16 | FDR-007 int8 |
| --- | --- | --- | --- |
| Reviewed focused buttons recognized |1/2 |0/2 |0/2 |
| Reviewed unfocused buttons falsely positive |0/2 |0/2 |0/2 |
| Correct unique frame focus / no-focus |1/1 |0/2 |0/2 |
| Crop classification correct |3/4 |2/4 |2/4 |

These tiny support counts are descriptive, not generalized quality estimates.
For frame scoring, exactly one probability≥0.85 is required; multiple positives
abstain and zero positives produce no-focus. This diagnostic policy does not change
production navigation or authorization behavior. Candidate ambiguity-band count is
zero on base boxes: these misses are confidently low scores, not useful abstentions.

## Ranked findings and next action

1. **Appearance generalization gap.** Both candidates assign very low probability
   to visibly white/enlarged Photos buttons (FP16 approximately0.000564/0.00528).
   Shipped recognizes one. Frozen Settings success does not transfer here. This is
   consistent with narrow training support, not proof of a particular causal
   forgetting mechanism. Add mixed appearance support before another same-style run.
2. **Box sensitivity.** Both candidates flip all four controls across0.85 somewhere
   in the seven variants. Inset4 yields two positive buttons in both frames, triggering
   multiple-focus abstention. Shipped focused scores also cross0.85 under perturbation.
   Preserve these cases; future training-only box jitter should be a separately
   frozen ablation with untouched appearance groups—not post-hoc crop tuning here.
3. **Compression parity is limited.** Base max FP16/int8 drift0.000179291, zero decision
   changes. All-variant max drift**0.04345706**, exceeding the previously frozen0.01
   tolerance at `office_pluto_loaded:all:up4`. Zero threshold changes does not make
   that probability check pass. The old12-crop pass remains valid for its old scope.
4. **Runtime timing.** CPU warm medians shipped/FP16/int8:1.382/1.351/1.334ms;
   crop medians12.134/11.790/11.895ms. First predictions17.374/12.115/10.993ms;
   loads21.775/15.620/20.316ms. Single sequential host trials, not speedup claims.
   Crop cost remains material; this1080p result is not directly comparable to prior4K
   crop timing. No device/ANE/network/end-to-end traversal measurement.

Production base crops were rendered using `focus_runtime.invoke` and visually
inspected at `.build/debug-output/focus-visual-01/base-crops.png`: correct button,
fill/shadow context and expected stretch. No alternate cropper or preprocessing
change; hand-reviewed boxes exclude shadows. This rules out an obvious wrong-region
error, not every possible cause of model failure.

**Next unblocked tranche:** extend the existing-image visual-review challenge to
clearly focused Home tiles and competing tiles, retaining unknowns/privacy exclusions.
Compare all three models with the same fixed protocol and production cropper. This
needs no TTR capture. Then propose one mixed-style training experiment only after
eligible, separate training examples exist; keep these discovered failures in
development regression membership, not an untouched final test. No training is
authorized or launched by this handoff.

## Verification and implementation

New `scripts/focus_visual_comparison.py` exposes explicit `freeze` and `run` commands,
using existing perception validation, byte checks, model contract, pixel-budgeted
inference and production crops. No public API, model file, producer schema or trainer
changed. It rejects changed review/protocol/pixels/runtime/models, missing competing
boxes, invalid probabilities/order, collision/symlink/outside-report output and false
callback claims. Completed per-model results remain available if a later stage fails.

`scripts/test_focus_visual_comparison.py`: nine deterministic tests,0.028s; actual
freeze/run integration uses fakes in ordinary tests, never model inference. Full
`test_focus*.py`:87 pass/2.566s (`tests.log`). Actual production evaluation is separate
(`evaluation.log`, exit0); all84 crops scored. `inspect_crops.py` and `summarize.py`
exit0, refuse existing outputs. No external wait/capture time; real evaluation was
one bounded helper call per model (120s bound each), not an automatic retry loop.

Commands use PYTHONDONTWRITEBYTECODE=1 and the approved isolated focus-export-01
Python interpreter. Exact invocations:

```text
scripts/focus_visual_comparison.py freeze --manifest reports/work/PER-DATA/manifest.json --models reports/work/FOCUS-VISUAL-01/models.json --output reports/work/FOCUS-VISUAL-01/protocol.json
scripts/focus_visual_comparison.py run --protocol reports/work/FOCUS-VISUAL-01/protocol.json --output reports/work/FOCUS-VISUAL-01/evaluation
-m unittest discover -s scripts -p 'test_focus_visual_comparison.py'
-m unittest discover -s scripts -p 'test_focus*.py'
```

Offline Swift build/test use `--disable-automatic-resolution --manifest-cache local`
and project-local cache/config/security/module/TMPDIR locations; logs in this folder.
Build2.54s; Swift Testing2.494s. `final-checks.json` confirms all84 predictions,
unchanged source review/images/models/runtime and records protocol/code hashes.
Host execution approved solely for CoreML/compiler runtime. No simulator/Office
operation, TTR modification, training, download or Git write. Source images/reviews,
FP16/int8 and shipped artifacts preserved. Existing iOS reconstruction/temporal
planning changes and their ownership untouched. Coordination not applicable: no
peer request/action changed, so no SMB progress noise.

The assigned implementation, real comparison, failure diagnosis and handoff are
complete. Broader acquisition/model qualification remains separate; no running
capture, training or background process is implied.
