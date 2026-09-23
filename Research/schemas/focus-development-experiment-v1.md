# Bounded mixed-appearance development experiment v1

OS-FOCUS-04 implementation assignment, 2026-09-23. This contract extends the
existing assembly CLI and trainer experiment-protocol boundary, not production
dataset admission. Original v1.4/v1.5 manifests and failed receipts stay unchanged.

Input `focus-development-input-v1` pins a native-only assembly input, retained
review, dispositions, baseline checkpoint and excluded previous dialog manifest.
The builder reconstructs native labels and direct receipt-chain pairs, verifies
all raw/crop bytes and production runtime parity, and recomputes disposition
membership and duplicate representatives. All retained Fixture seeds share one
experimental training group. Native screen splits remain root/general/apps train,
accessibility validation. Prior test-only or unknown-relationship sources reject.
No test partition is claimed. Review evidence is not cryptographic attestation.

Output `focus-development-experiment-v1` binds inputs, reconstructed samples,
sampling weights and configuration with `protocolSHA256`. It is development-only,
`trainingEligible:false`, `releaseEligible:false`. A production trainer invocation
rejects it even with production approval. No new cropper or training loop exists.

The experiment path accepts only warm-stretch, 30 epochs, batch64, lr0.0003,
seed42, current production256 crop preprocessing, fresh optimizer and no random
augmentation (matching the preceding native development baseline). Maximum runtime
is1800 seconds, checked between batches; a single in-flight kernel/import is not
preempted. Checkpoint selection is minimum native-validation BCE, earliest tie.
No independent Fixture validation or generalization claim is available.

Launch readiness additionally requires an external maintainer decision record
`focus-development-approval-v1`: approved=true, exact protocolSHA256, runName,
arm=warm-stretch, reviewer and reviewReference. Preflight never creates this record;
software-generated drafts must be approved=false. This is an audit/consent binding,
not authentication or permission to self-authorize. Execution still requires
--execute and an exact logged experiment/protocol/arm/output binding. Dry-run does
not import torch, download weights, create training outputs or allocate a run ID.

Tests must exercise assembly and trainer entrypoints, positive plumbing on clearly
test-only fixtures, missing/stale approval, source/crop tampering, label corruption,
split/pair leakage, unsupported versions, retained membership and output collisions.
Actual retained-data preflight must remain launch-blocked without approval. No
training, inference, capture, TTR mutation or production promotion in this tranche.
