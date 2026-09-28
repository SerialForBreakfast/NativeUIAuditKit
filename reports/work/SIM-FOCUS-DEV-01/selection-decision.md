# Human decision needed: bounded learning versus full qualification

**Approved2026-09-27:** the maintainer answered "yes" to the explicit one-run,
retention-selected development proposal. This is execution authority for that
bounded run after verified integration/preflight, not authority for a second run,
new capture, export, promotion or final-challenge scoring. Runtime/data/model and
the concrete FDR-009 launch protocol are bound under `reports/work/FDR-009/`.
The text below preserves the exact decision reviewed; its pending labels are historical.

The current assignment authorizes usable Simulator training data. That work does
not require pretending Fixture sources are independent. The remaining decision is
which evidence may select a checkpoint: the existing full appearance policy cannot
run without its required independent validation/challenge coverage.

## Proposed narrower development experiment — not yet approved or implemented

Use the admitted, immutable extension's training members only. Keep all original
221 candidate pairs and nine native retention pairs; no validation, challenge or
Photos diagnostic member becomes training. All new Fixture recipes remain one
conservative related group. Do not make a random train/validation split of them.

Retain FDR-007 initialization, fresh optimizer, native/Fixture 50/50 sampling,
30 epochs, batch64, learning rate0.0003, seed42, no augmentation, production16%
expanded256×256 crops and1,800-second training cap. Threshold stays0.85.

**Material change requiring approval:** use the existing nine native retention
pairs (18 crops) as the only development checkpoint-selection set. An epoch must
retain the frozen18/18 reference accuracy at0.85; among eligible epochs choose
minimum retention BCE, earliest tie. No eligible epoch means no selected checkpoint.
Implement this as a separate versioned development protocol, never by deleting
the full appearance protocol's blockers. Bind actual data/runtime/model identities
and this decision, test real trainer integration and record the run before launch.

This small, repeatedly used retention set detects certain regressions, not broad
Fixture/Photos generalization. Selecting on it further exposes it to development.
Loss reduction is not a qualification pass. After the one bounded run, a separately
specified same-input diagnostic comparison on the already exposed48 validation
frames may test transfer; never score or mine protected final-challenge members.
No automatic second run, export, promotion or threshold/crop sweep.

Approval wording: "Approve one retention-selected development experiment with
the admitted Simulator extension and unchanged full qualification gates."

## Alternative: keep the current full selection policy

Complete source-relationship review and acquire independently eligible appearance
validation/challenge, including genuine Photos buttons, before training. Existing
data and preparation remain reusable. This choice preserves stronger selection
evidence but does not allow a model run now. TTR's nine-control geometry repair
and remote EXT-CAP qualification remain separate producer assignments; neither
blocks the completed four-control training-data admission.

Neither choice makes seed changes, palette variants, repeated sessions or the
`photos_like` preset independent sources or native Photos coverage.
