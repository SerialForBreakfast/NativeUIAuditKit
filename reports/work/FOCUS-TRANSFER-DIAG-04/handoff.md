# Retained transfer diagnosis — 2026-09-30

## Decision

Do not repeat FDR020 or replace the encoder yet. Propose one **matched appearance
contrast pilot** before producing a large corpus: vary content/background independently
of focus, with verified same-control focused/unfocused pairs. This is a proposal,
not capture, training, admission or release authorization.

The training problem is substantially learned; transfer remains inadequate. FDR020
classifies928/928training crops correctly at0.5 and orders all395native pairs correctly,
including150/150artwork pairs. The stricter training-confidence test still fails27
crops. Development artwork recall is1/12 at the unchanged0.85threshold. Training
accuracy does not establish generalization.

## Evidence and limits

`analysis.json` freezes source references/hashes and records20development cases,
395native pair contrasts and training support. `sheets-final/01.png` through `20.png`
show retained production crops, three nearest training crops and original frame context.
Visual inspection in this tranche covered sheets01,06,08,10,12,14,15 plus original
Photos frame004 and its upper-button crop. Other sheets are generated, not claimed
individually reviewed. Feature similarity is explanatory, not a prediction policy.

1. **Coverage/style mismatch is the leading hypothesis, not a proven cause.**
   Human training contains only6focused artwork controls versus74unfocused, and
   2focused rows versus52unfocused. Its4primary buttons are all negative, from
   Paramount profile/sidebar/hero screens; none are Photos button examples.
   Native artwork supplies150pairs, but reviewed nearest examples include glossy
   moon/gradient fixture cards unlike Home icons and real app cards. Sheet12's
   focused Music icon scores approximately0 despite nearby focused fixture examples.
2. **Crop contamination does not explain the inspected Photos false positive.**
   Sheet14's gray, unfocused “View All iCloud Photos” button scores0.983845.
   Its exact production crop retains the button and excludes the focused button below.
   Bounds500×66 yield a strongly stretched256×256representation; causal impact is
   untested. Closest stored examples are focused Settings rows (cosine0.918) and an
   unfocused row (0.895). This suggests an appearance contrast gap, not label proof.
   Keep production16%expansion and resizing unchanged for the proposed pilot.
3. **Important counterexamples prevent a simplistic explanation.** Sheet08's missed
   Fubo card has three nearest focused training neighbors. Sheet10's false-positive
   Paramount card has three nearest unfocused human neighbors. Nearest-label voting
   is therefore not justified. Sheet06's Prime Video card succeeds, so complex artwork
   itself is not universally unsupported. These findings cannot distinguish frozen
   representation limits from the learned head's unsupported decision regions.

Explicitly identified Photos controls provide a useful retained contrast: upper button
scores0.983845unfocused versus0.9954focused; lower button scores0.3313unfocused versus
0.994751focused. Both upper states clear0.85, whereas lower states separate. These
are human-reviewed state identities, not native telemetry or new training admission.

## Proposed next assignment: matched appearance contrast pilot

Prepare a producer capability/recipe specification, then obtain separate execution
approval. Target24genuine pairs:3control families (Home artwork tile, content card,
wide Photos-like button) ×2content variants ×2background contexts ×2selected-state
conditions. These are collection targets, not qualification thresholds. Separate
selected-parent appearance from actual focus; use valid selected-state semantics only.
Where a recipe cannot express that distinction, report unsupported rather than fake it.

For each condition, freeze layout/content while moving native focus to and from the
same control, retain competitors and native geometry/identity, and verify settled
image/observation correlation. Preserve focused/unfocused state changes rather than
substituting recolored duplicates. Check actual pixels and production crop context
on a small proof before completing the matrix. No per-letter or repeated human
rectangle annotation is needed for trustworthy Fixture telemetry.

Reserve whole recipe/content families before any experiment; never move the existing
development screenshots into training. A later separately approved controlled test
should keep the encoder, cropper, loss, optimizer budget and0.85threshold fixed and
change only the admitted pilot data. Evaluate on unchanged development/retention and
newly reserved independent sources. Repeatedly exposed development improvements are
diagnostic evidence, not untouched qualification. If the pilot fits but transfer
does not improve, that supports investigating representation/crop design next; it
does not justify scaling the same synthetic distribution indefinitely.

Remaining60TTRartwork pairs are a separate scope: quantity alone does not establish
this coverage or solve Photos buttons. No new producer runtime action was dispatched.

## Outcomes and verification

- Software: offline analysis uses saved predictions and cached tensors only; no model
  instantiated. Two focused tests pass (deterministic neighbor ties; malformed,
  nonfinite, duplicate-membership and zero-norm rejection). Actual retained membership,
  scores, tensor identities and source hashes verified. Native790-row prefix verified
  so pair indices resolve against the correct full training rows.
  Offline Swift build and test commands both exit0; logs are `swift-build.log` and
  `swift-test.log`. Existing Swift tests remain passing; library code was not changed.
- Data:928training and315development membership unchanged;20diagnostic cases rendered.
  No labels, roles or eligibility changed. Protected challenge not inspected.
- Integration: no new TTR capture or transport needed for this diagnosis. Existing
  crop-parity receipt and producer clamp-metadata correction remain separate.
- Model gate: unchanged; no eligible FDR020checkpoint, no export or promotion.

Reproduce in a fresh output directory by copying the packet's analysis/test scripts
there and running with `PYTHONPATH=scripts` using `.venv-yolo/bin/python`. Existing
`analysis.json` and `sheets-final` are deliberately not overwritten. The initial
`analysis.log` records a strict reference-shape error, fixed before successful
`analysis-final.log`; it was not a corrupt source image.

Coordination: not applicable to this completed local diagnosis. Proposed future
producer recipe scope requires a separately assigned handoff; no shared status claim
or peer acknowledgment is implied.
