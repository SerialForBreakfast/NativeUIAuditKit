# Measured retention and recovery without repeated capture

Owner: Maximum-mini-NUIAK. Standard stays unchanged. HCF remains optional.

## Accounting

Count each device and inode once for input storage. Report logical path bytes separately.
Keep content hashes separate from file identity. Distinct files can contain identical content.
Archive only missing content hashes. Verify existing archive payloads before replacing duplicate entries.

The campaign contains 12 approved captures. Each producer retains its 1 GiB policy.
Reserve 13 GiB of unique input bytes for the existing evidence and 12 producer allocations.
The first completed capture leaves 192,737,077 unique archive bytes.
Reserve that measured cumulative amount for each of 12 further captures, plus the existing archive.
The archive ceiling is therefore 2,505,582,001 bytes. This is a conservative campaign reservation, not a throughput estimate.
These ceilings replace the 2 GiB logical-path check and 512 MiB archive limit.
The 20% free-space check remains unchanged. The existing study and producer policies remain unchanged.
The reservation does not authorize additional captures or automatic expansion.

## Recovery

### Explicit Standard preparation

Recovery first uses TTR's existing `ensure` operation with desired profile `standard`.
It verifies the returned profile before starting the existing HCF round trip.
Both operations use the same owned session and recovery journal directory.
A failed or uncertain preparation stops the sequence. It does not retry input or release the guard.
The final round trip still requires original Standard, observed Standard, and verified restoration.
Use an explicit successor. Preserve the failed recovery and all completed capture artifacts.

RECOVERY462 registers the recovery successor and 40 dependent capture/comparison successors.
Capture approval remains blocked while the target is occupied.
A reusable gate extension approves the four pinned captures after the established recovery verifier passes.
It preserves duplicate, revocation, changed-input, target identity, and already-started checks.
The gate does not run capture. The existing runner executes approved work.

The received TTR report names a binary hash. Do not treat that identifier as a source revision.
Both manifests and four payload files pass transfer verification. Receiving-host deployment remains unqualified.
The installed, pinned helper supplies the existing ensure and round-trip operations for this recovery.

The completed legacy capture has no TTR campaign identifier. Do not invent one to use campaign resume or export retry.
Use the qualified retention-only recovery for its existing bytes.
The training producer has incomplete capture and cleanup evidence. Export cannot make that attempt eligible for training.

Verification: 43 capture/retention tests and 31 admission checks pass.
The offline build and 191 Swift tests pass with a fresh project-local cache.
The first build log preserves the old-cache path failure.
Evidence: `reports/work/RECOVERY462/`.

Native restoration passes in the 155 s attempt. Standard preparation observes HCF and explicitly sets Standard.
The next round trip starts and ends in Standard with verified restoration. Fixture and ownership checks pass.
The queue rejects an unread retention dependency after native success. Preserve this failed receipt.
The evidence-only review requires that exact failure, the unchanged result and outputs, and successful restoration checks.
It reads the missing retention receipt and republishes the existing evidence. It does not navigate or capture.
Explicit graph successors use this reviewed receipt. The automatic gate retains fresh target and ownership checks.
All 40 downstream successors preserve their original training settings, templates, staging, capture contracts, and limits.
Nine review and dispatcher checks pass. The final offline build and 191 Swift tests pass after integration.
The evidence-only review completes in 0.91 s without navigation or capture.
The first admission extension rejects serial successors because it expects a direct recovery dependency on each capture.
Its explicit successor verifies the pinned retention chain back to recovery. Changed parent hashes and cycles remain rejected.
Four targeted admission checks pass. The failed gate remains preserved.
The corrected gate completes and approves all four capture successors.
The final graph has 42 approved jobs: two complete, one running, and 39 dependent at the handoff snapshot.
The running job captures the row-top slice. Completed captures are not repeated.
All 112 focused tests pass. Standard and iOS models remain unchanged.

`retention_recovery461` verifies the failed specification, result, every recorded output, source frames, and cleanup evidence.
It accepts only named retention budget or space failures after completed capture.
It runs retention without invoking capture. It publishes exact existing image bytes and their original capture artifact.
The original failed attempt remains immutable. Missing cleanup, changed bytes, and capture failures remain rejected.

The runner completes `native461-retain-button-bottom` without repeating its 24 captured frames.
A separate training capture fails with `profile-hcf:None` and leaves a recovery guard.
`native461-restore-training-failure` uses the existing restoration check after retention.
This attempt fails after 36.11 s with `standard_restoration_unverified`.
The retained route reports original HCF, observed HCF, and restoration not required.
The current normalization adapter resets navigation only. It does not set Standard.
The next repair must explicitly verify Standard before the round trip. Do not weaken the existing final-state check.
The four remaining development captures depend on that restoration and sequential retention.
Their downstream comparisons use explicit successor jobs. Completed button-top comparisons are reused.
The failed training capture is not retried or treated as complete.

## Checks and next decisions

35 focused tests pass. The offline Swift build and 191 tests pass.
Tests cover hard links, unique storage limits, archive limits, free space, changed evidence, missing cleanup, and retention-only recovery.
No images, checkpoints, or journals are deleted. No model or threshold changes.

All 12 independent iOS diagnostics complete.
Across 2,030 labeled controls, class-aware candidate misses total 190.
Class-agnostic matching gives 165 misses. Grouped button roles give 182 misses.
These are development diagnostics with incomplete labels, not deployment accuracy.
Review button-role annotations and the 44 extra unmatched boxes before training or threshold changes.

Next: repair Standard-setting preparation and inspect the native comparisons as a batch. Diagnose the training profile failure separately.
Do not repeat completed captures to repair reporting, retention, or downstream dependency failures.
