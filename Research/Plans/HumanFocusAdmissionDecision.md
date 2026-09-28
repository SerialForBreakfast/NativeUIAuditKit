# Human focus development-evaluation lane — approved

2026-09-28. Maintainer explicitly approved this proposal (“I approve it”).
HUMAN-REVIEW-04 implements the separate development-only lane and one fixed comparison;
the earlier crop/audit tranche itself did not authorize model execution.
Evidence: [HUMAN-REVIEW-02](../../reports/work/HUMAN-REVIEW-02/handoff.md).

## Recommended decision

Reserve all8 reviewed Office frames/113 controls as one correlated **development
regression set**, excluded from training. Permit a new versioned human-reviewed
development-evaluation adapter and one frozen comparison of the shipped FocusRing
model with selected FDR-009. This is not an independent generalization exam,
training approval or release qualification.

Do not flip eligibility flags on diagnostic manifests. The new lane must reference
the frozen human revision, raw/crop hashes, explicit approval, reviewer and source
group assignment. Existing training/independent-evaluation consumers must continue
rejecting the diagnostic format. Future training needs a separate role policy and
different source groups; using this batch for both training and its own regression
score would conceal overfitting.

## Admission checks before any model execution

1. Reverify the Joe revision/hash, all snapshots, original frames, class/state/box
   consistency and actual production crops. Zero unresolved hard audit errors.
2. Freeze all113 sample IDs,8 positives/105 negatives and2 explicit Photos pairs.
   Retain the two duplicate-crop groups; report full support and duplicate-group
   sensitivity without silently reducing the population. No automatic extra Home pairs.
3. Bind device/session/layout ancestry and check against actual training, retention
   and protected evaluation manifests. Unknown relationships remain explicitly
   diagnostic; any proven overlap is reported and cannot be described as transfer.
   No existing selection/retention corpus is changed.
4. Keep candidate completeness unknown under the current v1 review contract.
   Crop-level focus metrics and the two paired-control outcomes are supported;
   complete-frame unique-selection accuracy is not. User-supplied boxes do not
   measure detector recall or qualify autonomous navigation.
5. Test new admission/caller integration with missing/changed pixels, contradictory
   flags, wrong roles, unsupported completeness, missing predictions and duplicate
   identities. Offline Swift build/test and focused tests remain required.

## One proposed comparison, not a training loop

- Shipped model: `NativeUIAuditKitModels/Sources/NativeUIAuditKitModels/Resources/FocusRingDetector.mlmodelc`;
  current artifact digest `9e5ba294e545b4ae0c54aa5d483b1a1f681b6c30477882700b4dbe139b9c66b7`.
- FDR-009 epoch3: `NativeUITrainer/focus_ring_runs/fdr009-simulator-retention/weights/best.pt`;
  SHA256 `e6e37ddc32c173ddf13e1e52756995a53cbbe1e1af18aa0e6da58b5767e47584`.
- Reverify those exact identities and pin the runtime at execution; artifact bytes
  were inspected, neither model was loaded during the audit tranche.
- Fixed0.85 threshold, existing16%/256×256 production crops and original boxes only.
  Shipped CoreML CPU and candidate PyTorch CPU via established components; no
  threshold/margin sweep, export or claim of equivalent backend latency/parity.
- Report recall, precision, false positives, misses, per-screen/class support,
  pair outcomes, every failed/missing score and numbered failure sheets.8 positives
  is narrow support. Raw accuracy alone is misleading with105 negatives.
- End with measured next-data priorities. No training, capture, public API/taxonomy
  changes, promotion, final-challenge scoring or autonomous navigation.

## What approval would authorize

Implement and verify this development-only human-label lane, then execute that
single two-model comparison once its checks pass. It would **not** authorize any
training use of this batch, a new training run, expanded capture or relaxed gates.

If the maintainer prefers using these examples for training instead, choose that
role explicitly and collect a separate real-world benchmark first. Recommendation:
keep this small, already-reviewed batch as the stable regression reference.
