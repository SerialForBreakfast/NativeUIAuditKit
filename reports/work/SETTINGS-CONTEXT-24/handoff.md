# Settings context diagnosis — reject a blanket body-only change

October2,2026. Completed the fixed region comparison and reusable native-crop visual
diagnostic CLI. Base revision `f173694`; checkout was clean at entry.

| Outcome | Result |
|---|---|
|Software verified|111Python tests; clean offline Swift build;134Swift tests|
|Data eligible|Existing reviewed development membership preserved|
|Integration qualified|Local CLI and native crops verified; runtime control unqualified|
|Model gate passed|Not assessed; body-only candidate rejected for general use|

## Decision and measured results

**Keep the full-context guarded stability rule.** Body-only measurement improves this
small retained set but hides a focus-outline change in the generated counterexample.

| Fixed region | Correct | Wrong | Abstained among48 | Coverage of50 |
|---|---:|---:|---:|---:|
|Full production crop, previous guarded rule|33|0|15|66%|
|Tracked row-body mask, same thresholds|37|0|11|74%|

The four additional correct unchanged decisions are Screen Saver299, Speech Rate378,
Use Pitch378 and Display409. Both real focus moves remain correct. Two OCR-unmatched
controls remain separate; all full-screen outcomes remain incomplete. These are
development diagnostics on previously examined data, not independent accuracy.

The stress experiment gives a decisive reason not to select by that score alone:

| Generated case | Full context | Body-only |
|---|---|---|
|Neighbor changes|unknown|unchanged|
|Focus outline appears outside the body|unknown|**incorrect unchanged**|
|Internal content replacement|unavailable|unavailable|
|Broad highlight arrives|arrival|arrival|
|Row translates|unchanged|unchanged|

Exact expected-decision agreement is3/5for both arms. Content replacement safely
abstains as unavailable rather than the requested unknown; that is not a wrong focus
selection. Full context conservatively abstains for neighbor changes. Body-only makes
one unsafe unchanged claim. The adversarial test is retained explicitly rather than
rewritten to make the candidate pass.

## Visual diagnosis

The gallery shows four aligned panels: before, tracked after, amplified absolute
difference, and measurement mask. These are the exact production crops; the mask
changes measurement support, not preprocessing or stored annotations.

- Screen Saver has a bright neighboring row entering the expanded crop's lower edge.
  The body stays stable, explaining its improvement under masking.
- Navigation Style378→386 translates about79.825source pixels vertically. The crop
  shows a changed background above the row and differences around rendered text.
- Verbosity translates about79.646pixels; residual differences outline the text and
  body edges after tracking. Excluding neighbors alone does not remove them.
- Speech Rate and Use Pitch improve when context is excluded, but most378→386rows
  remain uncertain. The evidence supports both context contamination and residual
  rendering/alignment differences; it does not establish one universal cause or
  justify loosening thresholds.

## Evidence and verification

- [Retained comparison](retained-final/result.json):50controls, unchanged scoring,
  source/runtime/code pins;2.84seconds for measured crop replay after input validation.
- [Visual gallery](retained-final/gallery.md).
- [Stress cases and counterexample](stress/result.json).
- [111Python tests](tests.log), [Swift build](swift-build.log), [134Swift tests](swift-test.log).
- `scripts/settings_context_probe.py --previous <sealed-stability-result> --output <new-dir>`
  validates source pins and reproduces the prior guarded summary exactly before
  reporting the changed-region result. `--stress` runs the generated cases.
- Tests cover translated/clipped mask geometry, neighbor/internal changes, the
  outline counterexample, invalid support/bounds and CLI preservation of outputs.
- [Assigned scope](../../../Research/Plans/SettingsContext24.md). No peer-facing
  contract changed; shared coordination is not applicable to this local experiment.

## Next substantial tranche

1. Prioritize the prepared eight structural review frames and source-role decision,
   then exact admission, encoding and the matched model-training comparison. This
   remains the fastest route back to model-quality work; human review is required.
2. Once TTR repairs semantic IDs and clarifies off-screen membership, replay its16
   native transition cases against the retained full-context guard, including the
   new outline counterexample. Keep style coverage explicit.
3. If further local Settings work is chosen, investigate subpixel registration with
   edge-only evidence and a transform cap. Test that it cannot erase real scale or
   outline changes before comparing accuracy; a more permissive stability threshold
   is not supported by this experiment.
