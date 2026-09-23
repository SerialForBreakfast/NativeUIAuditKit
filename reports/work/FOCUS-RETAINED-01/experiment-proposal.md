# One mixed-appearance development experiment — frozen proposal

This is an approval-ready experimental scope, not launch authority or production
training admission. OS-FOCUS-04 owns the next implementation tranche. No run ID
has been allocated. TTR is not a prerequisite.

## Inputs and membership

- `audit/review.json` content hash:
  `b252570f635379ace8592eaff84231f3ba3137851c0378236b312fadb743b05f`.
- `dispositions.json` binds every reviewed pair to that audit: 86 distinct
  non-maze pairs proposed for experimental training, four exact pair duplicates
  excluded, 48 maze pairs retained as diagnostics. Six kitchen-sink recipes remain
  absent. This is not a complete 42-recipe pilot or a 6,000-pair corpus.
- Preserve native membership from OS-FOCUS-04-ASSEMBLY: 40 training pairs and nine
  validation pairs. Remotes six pairs remain challenge-only. Home and Photos
  remain development diagnostics, never checkpoint selectors or training labels.
- Both Fixture seeds, related variants and duplicated pixels form ONE group.
  Never assign seed 7 to training and seed 19 to validation. The new experiment
  proposes 126 training pairs / 252 examples and nine validation pairs / 18
  examples, subject to final cross-source duplicate and contradiction checks.
- Do not append the earlier two-pair dialog smoke as independent evidence. Its
  shared recipe lineage is already development-only. Preserve its old manifest;
  explicitly record supersession/exclusion in the new experiment manifest.

## Implementation needed before launch

Extend existing assembly/preflight/trainer entrypoints with a bounded, versioned
**development experiment** contract. Do not flip existing v1.4/v1.5 eligibility or
relax production preflight. Bind source bytes, disposition hash, reviewer decision,
crop runtime, source lineage and requested experimental roles. Require explicit
experiment approval; reject missing approval, altered artifacts, role conflicts,
duplicate content across partitions, and prediction-derived labels. Recheck every
raw/crop hash and production preprocessing. A failed source receipt may contribute
only separately reviewed complete recipe groups, never a fabricated completion.

Test actual preflight/trainer dry-run integration using positive and negative
fixtures, including production-mode rejection of the same development manifest.
Run focused tests and required offline Swift checks after integration. Deliver a
resolved configuration and command; no launch until separately authorized.

## Proposed single run

After implementation acceptance and explicit authorization, log the next run
before launch. Initialize from FDR-007 best checkpoint, SHA-256
`a5c7f2f44368feb4ec81477aab33f1e0f5e2f380c43fb5d9ebca3bd26c3499f0`, with fresh
optimizer state. Retain vendored MobileNetV4, 30 epochs, batch 64, learning rate
0.0003, seed 42 and production 16% expansion / 256×256 preprocessing. Resolve
remaining settings against the established baseline and record all deviations.
Use existing training-only source/scene/style/control balancing; log actual
sampling weights. Isolate outputs and impose a reviewed runtime limit before
launch. No automatic rerun, export, compression or promotion.

Select checkpoint by minimum native-validation BCE, earliest epoch on ties. This
tests native retention only: **there is no independent Fixture validation set**.
Compare the selected checkpoint with FDR-007 and shipped model on identical
memberships with existing frozen thresholds. Report per-source/theme/control
support, misses, false positives, abstentions and native challenge retention.
Fixture training accuracy is a learning diagnostic, NOT a generalization score.
Reuse compatible existing reference results; new inference needs execution scope.

## Decision and next action

Success is a reproducible learning/retention result, not a claimed model-quality
gate. Report negative results equally. Do not tune against Home/Photos or call
their reused results untouched evaluation. Before model qualification, acquire
and qualify genuinely independent Fixture groups plus broader native appearances;
new seed numbers alone are insufficient evidence of independence. Keep all six
production quality gates, hard-negative quotas and physical-device requirements.

Next dispatch: implement the experiment contract and integrated dry-run above.
This is unblocked local software. Then request authorization for exactly one
logged development run, or choose independent evaluation acquisition first if the
maintainer wants a generalization claim rather than a learning diagnostic.
