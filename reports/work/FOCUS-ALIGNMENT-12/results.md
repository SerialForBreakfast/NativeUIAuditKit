# Translation-aware focus: useful Settings recovery, not a universal detector

October 1, 2026. **Keep the opt-in diagnostic; do not replace FDR021 or deploy it
as an autonomous action gate.** The experiment recovers the real scrolling failure
without removing scale, but sacrifices artwork coverage and still fails content-only
counterexamples. No new model training, capture, admission or promotion occurred.

## Concrete improvement

The retained Accessibility Shortcut row moves upward161source pixels. Fixed-window
comparison looked at empty background and wrongly reported loss of focus. Texture
tracking estimates158.44pixels upward and now correctly reports gained focus.
No after-frame truth box or label is passed into the tracker.

![Original frames, before crop, fixed after crop, aligned after crop](artifacts/common-support/example-0.png)

The first implementation rejected near-edge rows because translation changed the
amount of clipped context. The isolated follow-up trims **the same amount from both
windows**, retaining equal dimensions and scale. It does not resize each control
to its own after-state bounds. Original control bounds and adjusted crop-request
bounds remain separately identified; annotation files are never changed.

## Matched results

All methods share the retained images/labels. Whole-screen comparison uses six
eligible frame pairs/nine distinct frames in both directions, not12independent
trials. Retention uses nine static pairs in both directions. Home contrasts reuse
four captures/two focused icons and remain control-level diagnostics.

| Method | Eligible new-target directions /12 | Retention directions /18 | Home arrivals /6 |
|---|---:|---:|---:|
| FDR021 confident endpoint scores | 7correct,5abstain | 18correct | 0correct,6abstain |
| Previous fixed-window brightness+growth follow-up | 12correct | 17correct,1wrong | 6correct |
| Translation, reject unequal clipping | 9correct,3abstain | 4correct,14abstain | 0correct,6abstain |
| Translation plus common visible support | 11correct,1abstain | 18correct | 0correct,6abstain |

The remaining eligible-screen abstention is Purchased tab arrival: competing
texture matches do not clear the frozen uniqueness margin. Home icon enlargement
changes the internal artwork enough to fail rigid translation correlation. We did
not loosen matching thresholds or silently fall back to the unsafe fixed window.

On all454real-control contrasts, final method produces20/27correct arrivals,
21/27correct departures and no measured false changes among400unchanged controls
(396abstentions,4identical-window confirmations). It has no wrong directional
answers on this retained set, but lower coverage than the previous method. These
totals include incomplete/partially matched contexts and are **not deployment
accuracy**. Starting bounds are reviewed/native, not detector-produced.

Native training contrasts:151/513arrivals and149/513departures correct; remaining
cases abstain. They are existing training data, not independent evaluation. The
tracker does not solve general artwork focus.

## Adversarial findings

Eleven generated end-to-end CLI cases:5correct (no-op, translation only, enlargement,
scroll+highlight, translation+enlargement),4abstentions (duplicate, disappearance,
global illumination, viewport change), **2wrong changes** (replacement artwork and
highlight-looking color change without actual focus change). These failures remain
in the report and tests. One visual color transition can be identical whether caused
by focus or content; a scalar brightness signal cannot establish its cause.

Caller-supplied context/identity/settlement/freshness flags are not runtime detection.
False/missing flags do not get silently filled. The tool never sends controls, loads
weights, labels a corpus, or declares live navigation successful.

## Implementation and verification

- `focus_transition_verifier.py`: actual opt-in offline CLI, translation matching,
  reciprocal/ambiguity checks, equal-support geometry, existing native cropper,
  separate raw/gated output. Default disabled. [Usage](../../../Research/FocusTransitionDiagnostic.md).
- `focus_alignment_experiment.py`: both complete2,996case replays, same membership,
  comparisons, timings, source snapshots and visual examples.
- `audit_focus_alignment.py`: generated stress and caller-boundary checks.
-34focused Python tests;21generated CLI cases (11stress+10boundary cases), two
  actual retained-image CLI requests and four edge-geometry checks. Five malformed
  boundary inputs fail without output; four false context flags return unavailable;
  disabled path performs no image work. After-box/truth fields and boolean versions
  also have rejection unit tests.
-1,045matched final pixel decisions replay exactly after final schema hardening;
  all scientific core functions are AST-identical to the evaluated source snapshot.
  Both pre-hardening source snapshots match their recorded hashes.
-Offline Swift build and134Swift tests pass; no warnings observed. Swift/native
  cropper code was not changed. `git diff --check` passes.

Native equal-support geometry check: four translated edge examples preserve scale
and emit no false change. Initial strict byte-equality assertion failed at a single
8-bit code value along256border pixels (mean0.00390625/255). Follow-up records that
rounding difference explicitly; it is not claimed as pixel-exact equality. Both
windows retain equal native rounded dimensions. Retained decision replay is exact.

## Cost and boundaries

Primary replay182.84s; common-support185.92s (approximately sixminutes combined).
New native crops222and347 respectively; the latter crop pass22.33s. Final tracker
median14.6ms/p95 218.2ms per case, including identical-image controls; this is not
full-frame end-to-end latency. Inputs reused; all outputs approximately40MiB.
No GPU, new weights, dependency installation, device input or human review required.

Evidence: [primary](artifacts/replay/result.json),
[common support](artifacts/common-support/result.json),
[stress](artifacts/stress-final/audit.json),
[final replay](artifacts/final-check/audit.json),
[native geometry](artifacts/geometry-qa/geometry.json).

## Next substantial work

1. Receive/verify TTR's newly reported25-pair delivery and inspect its included
   structural-coverage proposal. Do not turn producer calibration into training
   automatically. Check actual new coverage before spending training time.
2. For a deployable transition verifier, use whole-screen evidence: match persistent
   controls, corroborate focus gain/loss, and reject scrolling/content ambiguity.
   Test with action-linked focus switches and no-ops, not only reversed static pairs.
3. Keep text-row tracking and artwork enlargement as distinct evidence paths. Any
   combination must be tested against the retained Home losses and the two content
   false-change cases; do not assume agreement establishes causality.

TTR reports25newpairs/50frames delivered (31/48with the previous six),17remaining
runtime-blocked, and a proposed48pair structural successor. That is a producer
snapshot, not a receiver receipt, new admission or capture authorization.
