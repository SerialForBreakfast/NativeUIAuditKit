# One future balanced appearance candidate — not launch-ready

## Decision

Use the76 new pairs as **development/training candidates**, not a new holdout.
All162 Fixture pairs (86 old +76 new) form one connected component through
explicit lineage and pixel overlap. Seeds7/19/101/211 must stay together.
Keep native40 training pairs, Accessibility9 retention-validation pairs and
Remotes6 known challenge pairs in their original roles. Preserve Home72 and
Photos4 reviewer boxes as visual-only known-failure diagnostics, never labels for
training or untouched test evidence. Full memberships and bytes are frozen in
[proposal.json](proposal.json) and [protected-evidence.json](protected-evidence.json).

Candidate pool:202 pairs/404 samples, with no duplicate complete crop pairs or
contradictory labels. Six new individual crops overlap old training; partial-pair
duplicates remain traceable in one component, not counted as independent support.
Original source manifests remain development-only; this proposal does not approve
their use by a trainer.

## Sampling hypothesis

Propose50% native /50% Fixture expected sampling mass. Within each source,
divide equally among source/scene/style/control strata, then equally by label.
Use frozen per-sample probabilities; validation/challenge rows have no weight.
Previous actual masses were11.11% native /88.89% Fixture. Retain every accepted
old pair and all76 new pairs; do not select just the three misses.

This increases native replay without claiming50/50 is optimal. The weight-vector
effective sample size is129.79 out of404; that describes sampling concentration,
not visual independence. Repeated individual crops can still receive repeated
mass. Show both per-source and per-stratum results rather than aggregate accuracy.
Adding data and changing source weights together is a candidate-development
choice, not an ablation capable of identifying which caused any improvement.

## Configuration proposal and selection blocker

One30-epoch MobileNetV4 candidate, batch64, lr0.0003, seed42, no new augmentation,
production16%/256 crops, warm FDR-007 weights with fresh AdamW state. Preserve
FDR-008 as comparison. This keeps initialization comparable to FDR-008 instead
of carrying its known Home false positives forward by default. No experiment ID
allocated, no weights loaded and no run logged as started.

The JSON retains the old configuration as a reference; its native-only checkpoint
selection is **not an approved next-run policy**. Resolve selection only after
independent appearance validation exists. Proposed policy: minimize equal-source
validation BCE among checkpoints meeting a frozen native-retention floor; earliest
tie wins. Set the retention floor from reference scores on the frozen new protocol
before training, not after seeing candidate epochs. No eligible checkpoint means
failed experiment, not a relaxed floor. Final challenge is read once after selection.
Threshold0.85 remains fixed for comparable development reporting.

## Independent evaluation reservation (before acquisition)

The following are requirements, not existing captures or executable recipes.
Reserve separate validation and final-challenge groups in each stratum:

| Stratum | Required distinction from current training | Current support |
|---|---|---|
| Dense dark media/thin outlines | New artwork/layout families, not seed-only text changes | Missing |
| Bright unfocused artwork | Varied actual artwork with observed non-focus | Missing |
| Gray/blank placeholders | Explicit rendered placeholder family and negatives | Missing |
| Dock and neighboring focus | Independent layout/context and observed target identity | Missing |
| Photos-like primary/secondary buttons | Native focus binding or qualified distinct Fixture preset | Missing |

Reserve at least two unrelated recipe/journey groups per stratum **per partition**
as a minimum diagnostic floor, not a production qualification quota. Include
positives and negatives in each. Assign whole template/artwork/journey families,
all focus states and related variants together; hash-check raw frames and crops
against old/new training before admission. Unknown lineage stays quarantined.
Numeric seeds are chosen only after a source actually exposes these capabilities;
do not invent unavailable preset IDs. Exact duplicate rejection is necessary but
not proof of semantic independence. Record remaining coverage rather than reducing it.

Known APPEAR-A2 errors are development-only. The six Remotes pairs have already
been scored and are native retention diagnostics, not a fresh appearance challenge.
Home/Photos box sensitivity evidence remains useful but not independent truth.

## Execution gates and next implementable slice

1. Review this proposal and source-balance hypothesis.
2. Independently prepare a versioned adapter accepting approved v1.4 development
   evidence and these weights through the existing trainer; never relabel it as
   production eligibility. Test missing independent evaluation and stale approval
   as truthful launch blockers. No trainer fork or new cropper.
3. Qualify the reserved appearance sources and freeze actual validation/challenge
   memberships plus reference scores. Existing TTR rendering request covers gaps;
   a separately authorized native route can substitute only with observed labels.
4. Freeze the resolved protocol, sampling, checkpoint selection and decision limits;
   request one exact training authorization. Log the run immediately before execution.
5. Compare retention, new appearance and known Home/Photos failures separately.
   Failed gates produce diagnosis; no automatic retry, export or promotion.

The current proposal deliberately has an unsupported training-protocol version and
`launchEligible=false`. Full6,000-pair quotas, six FocusRing gates, CoreML parity/size,
physical-device qualification and a separate promotion decision remain unchanged.
