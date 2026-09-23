# iOS platform delivery plan

Established 2026-09-19. This is a platform-oriented dispatch guide over the existing
revision-4 packets, not a second status queue. State and ownership remain in
[Tasks.md](../../Tasks.md#ios-platform-tasks). Follow the
[execution contract](../ImplementationPlans.md#common-execution-contract) and
[worker workflow](../WorkerWorkflow.md): finish the whole assigned tranche through
integration, verification, and handoff. Planning grants no execution authority.

## Product boundary

The shipped iOS detector is five-class `nativeui-ios-v2.0`. The next deliverable is
a qualified 41-class full-frame iOS detector, not FocusRing or a unified-platform model.
Keep class IDs 0–40 frozen and existing production resources unchanged. Badge is a
later milestone. tvOS fixture examples are auxiliary data in the planned experiment;
they cannot replace iOS withheld-template evaluation or establish iOS performance.

Separate platform, corpus, and provenance in every report. Do not describe simulator
examples as physical iPhone captures. No new physical-iPhone qualification claim or
capture requirement is introduced by reorganizing these tasks.

## 1. iOS corpus recovery and preservation

**Current dispatch amendment, 2026-09-22:** P0-C is already assigned and underway;
preserve its owner and r5 configuration. Do not replay original-recovery searches
or reopen accepted offline toolchain work merely because the historical sequence
below describes them. DATA-RET prepares retention; IOS-COV resolves absent class
support and gate implications. Their [contracts](RemainingDelivery.md) do not
change the16,940-image reconstruction target or authorize generator edits.

**Packets:** P0-A review, then P0-B or P0-C under separate execution authority.
**Canonical contract:** [DatasetRecoveryPlan.md](../DatasetRecoveryPlan.md).
**Inputs:** original manifests/labels, existing P0 inventory and handoff, documented
source locations, historical Run 009 report. No Office dependency.

Complete the assessment review against all 17,040 manifest entries. Resolve missing
label-hash/provenance evidence explicitly; do not call the assessment complete simply
because an inventory exists. Produce a bounded recovery decision with exact sources,
new destinations, space requirements, uncertainties, and preservation/backup owner.
If known-source recovery is exhausted, prepare a pinned reconstruction configuration
and obtain the required generator/rendering authority before execution.

The separately assigned data tranche validates fresh staged image/annotation pairs,
hashes, split/family isolation, class/style coverage, and retention. Preserve old
symlinks, labels, and historical metrics. Recovering only test pixels can unblock
baseline work without claiming training readiness. A reconstructed corpus gets a
new identity and new Run 009 baseline; the historical 0.586 remains non-comparable.

**Exit evidence:** reviewed decision; for executed recovery/generation, immutable
train/validation/test manifests and independent split-readiness results. Exact original
test recovery requires all 2,000 members, not a silently reduced test set.
**Blocked work:** data execution waits on its actual source/rendering authority;
software tranche 2 continues independently.

## 2. Integrated offline iOS toolchain

**Packets:** review P1-A, P2-A, P3-A, P4-B, P5-A together; retain separate acceptance.
**Canonical contracts:** [EvaluationAndTraining.md](EvaluationAndTraining.md).
**Inputs:** existing implementations, schema documents, worker handoffs, deterministic
toy images/labels and fake predictions; reviewed P4-A normalization interface as needed.
**File scope:** each included packet's implementation/tests/docs and additive reports;
do not overwrite another active worker's files or broaden into producer code.

First inspect actual behavior against the original acceptance criteria. A review-only
assignment returns specific gaps without changing code. An explicitly assigned
review-and-remediation tranche fixes those gaps and proceeds through final verification.
Do not redispatch delivered packets as greenfield helper implementations.

Exercise the contracts together, using adapters only where the canonical contracts
require them: normalized source manifests → split-safe assembly → configuration-only
readiness; deterministic request/result artifacts → export serialization → compatible
reference comparison; metadata → frozen regression membership. Verify required caller
or CLI entrypoints, not merely standalone helper functions. No model inference is
needed to test these software boundaries.

Cover missing/corrupt pixels, changed hashes, unsupported versions/taxonomy, empty vs
failed inference, settings mismatches, cross-split family/content leakage, output
collisions, training-only weights, and falsely eligible test data. Verify validation-only
execution cannot train or download weights. Use focused tests plus the required offline
Swift build/test checks for code changes; report unrelated failures separately.

**Exit evidence:** per-criterion findings/results, actual entrypoint and cross-interface
tests, commands/exit codes, stable artifact examples, and any exact blockers. Green toy
tests can establish software behavior but not eligible data or live/model gates.
**Next:** accept individual software contracts; data readiness determines real execution.

## 3. Real iOS baseline and regression qualification

**Packets:** P1-B → P2-B, with P3-B using compatible accepted artifacts.
**Inputs:** eligible original or replacement iOS test corpus; explicitly selected and
hashed Run 009 checkpoint; accepted exporter/comparator/selector; inference authority.
No fixture bundle, Office access, or new candidate is required for this tranche.

Account for every manifest member before inference; fail on missing/corrupt members.
Export complete original-image predictions with checkpoint/corpus/settings identities,
including successful empty results separately from failures. Tie reported metrics to
the actual inference path; distinguish official and custom metrics.

Freeze metadata-driven regression membership without selecting Run 009 failures.
Target 200–300 cases where coverage permits and report gaps. Reuse compatible verified
full-holdout predictions when exact subset evaluation supports it; do not invent metrics
from labels alone. Preserve historical reports and mark incompatible comparisons.

**Exit evidence:** full iOS baseline, compatible reference report, immutable diagnostic
suite and baseline, exact hashes and support counts. The compact suite never replaces
full withheld-template DS-G8. The report must include the architecture-required
per-class AP and mean AP table at IoU 0.50, 0.70 and 0.90 on the same frozen cases;
legacy 0.50-only evidence remains historical context, not a substitute. Missing pixels
block this tranche, not tranche 2.

## 4. iOS candidate readiness and controlled execution

**Packets:** P5-B, then separately authorized TRAIN-S and TRAIN-F.
**Canonical contracts:** [EvaluationAndTraining.md](EvaluationAndTraining.md) and
[ModelsAndHardware.md](ModelsAndHardware.md).

Freeze eligible synthetic and fixture manifests, platform-specific coverage and split
roles, training-only class weights, and resolved blend/configuration. Describe why tvOS
examples are included in an iOS candidate; do not silently relabel them as iOS. Complete
configuration validity and launch eligibility separately. Current fixture availability
and approved source-provenance policy are explicit inputs, not assumptions.

Use Run 009 `best.pt` with fresh optimizer/schedule state, the accepted 150-epoch target,
cosine/warmup/early-stop settings, full-frame augmentation, and isolated outputs. Allocate
each run ID and log immediately before its separately authorized launch. The existing
dry-run is actual training and cannot substitute for configuration-only preflight.

**Exit evidence:** readiness has zero unresolved launch blockers; smoke reports exactly
what it exercised; the full run produces a readable hashed candidate and experiment
record. A failed run ends in diagnosis and a reviewed proposal, not automatic retraining.
Office remains released until explicit new user authorization. This iOS plan does not
reinstate the withdrawn Sillycon smoke or authorize SSH/remote execution.

## 5. iOS qualification and release evidence

**Packets:** TRAIN-Q → REL-A; REL-B is maintainer-only.
Evaluate the candidate and reference on compatible frozen corpora. Report independently:

- iOS synthetic withheld-template DS-G8 mAP@0.5 ≥0.85.
- Fixture mAP@0.5 ≥0.94 and mAP@0.5:0.95 ≥0.78.
- Fixture toggle and stepperControl AP50 ≥0.88 with nonzero applicable support.
- Per-class AP and mean AP at IoU 0.50, 0.70 and 0.90, with per-threshold support
  and the exact frozen evaluation membership recorded. These geometry reports add
  evidence; they do not silently weaken or replace the existing release gates.

Preserve per-class support, platform-specific results, settings hashes, and diagnostic
regressions. No pooled mean, test-only provenance, or missing-class metric passes a gate.
Badge has no metric in the frozen 41-class model. Produce the required package/API,
conversion/reference, provenance and release evidence under REL-A; do not bundle raw
weights/data or machine-specific paths. Only the maintainer promotes/tags after approval.
Current shipped models remain in place on failure or incomplete evidence.

## Later iOS-affecting work

- **TASK-6a-12 / CROP-A/B:** separate crop configuration/holdout after the accepted
  full-frame baseline; ≥15% relative crop mAP50 improvement, ≤1 percentage-point
  full-frame loss on identical comparison corpora. No automatic promotion.
- **TASK-BADGE-01 / BADGE-A/B:** shared append-only ID 41 and versioned model-category
  mapping; distinct later 42-class dataset/model, not an expansion of this tranche.
- **Phase 6b-U / UNI-A/B:** shared platform-balanced experiment with independent iOS
  reference/gates; retain separate shipped models. Neither this nor FocusRing blocks
  release of an otherwise qualified 41-class candidate.

## Dispatch and handoff

Dispatch names the selected tranche and included packet IDs, owner, operation authority,
file ownership, required evidence, and exact stopping conditions. The five headings are
not blanket authorization to execute all later phases. Finish all safe authorized work
within the dispatched tranche; use commentary for progress, not final promises to continue.

Preserve existing per-packet handoffs under `reports/work/`; add an integrated summary
linking them when reviewing a tranche. Report software verified, data eligible,
integration qualified, and model gate passed separately. Update only actual execution
state in Tasks.md. Publish shared status only if a specific result affects TVTestRig–NUA
interaction; ordinary local iOS progress is not applicable and stays in this repository.
