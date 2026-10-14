# Workflow improvements and HCF study

> Historical research record. Results retain their stated scope and limits.
> Host names are public aliases. Local evidence and execution records remain private.
> This publication does not revalidate earlier results or approve a model.

Owner: research-host-NUIAK. The user approves this study on October 12, 2026.

## Budgets and decisions

Use 48 GPU-hours, at most 50,000 accepted training frames, and 250 GiB of retained study artifacts.
Remote replicas require separate capacity reservations. Keep original data roles and previous-success gates.
Compare a one-class YOLO11n focused-control detector with an HCF FocusRing crop classifier.
Compare both against pinned TTR rules and existing NUIAK models on compatible tasks.
Do not use a mode classifier as a substitute for focused-control selection.

Allocate 4 GPU-hours to screening, 24 to data scaling, 12 to repeat seeds, and 8 to scoring and conversion preparation.
Each run permits 100 epochs and 4 GPU-hours. Freeze all settings before admission.
Use development-loss early stopping after 10 epochs without improvement.
Verified resume requires optimizer, scheduler, random-state, epoch, membership, and preprocessing identity.
Current queue trainers support restart only. Do not claim resume until that separate task passes equivalence tests.

## Workflow implementation

W1 extends the loopback server with authenticated POST `/api/add`.
The body contains `jobs`, with exact `id` and canonical `sha256` for each existing specification.
Persist additions separately. Repeated identical additions are idempotent; changed specifications fail.
The continuous runner reads additions at each dispatch boundary. Adding jobs never starts a stopped runner.
Keep normal batches at 5 jobs. Do not change running attempts.

W2 writes campaign reports after each batch using verified result identities and retained comparison fields.
Report execution completion separately from model acceptance. Missing results stay incomplete.
Task-specific reports remain authoritative for accuracy, regressions, and model selection.

W3 checks specifications, hashes, dependencies, training registration, and available output storage before dispatch.
Each failed requirement includes the responsible owner. Runtime ownership still requires the existing execution check.
Do not interpret file readiness as qualified live capture or permission to change a device.

## HCF graph and gates

1. Verify the diagnostic delivery and recipe references.
2. Qualify visible native HCF effects and bounded producer storage.
3. Freeze connected scene groups and data roles.
4. Generate immutable shards and verify all labels and images.
5. Score existing rules and models on identical membership.
6. Train both approaches with matched budgets.
7. Compare target gains and previous successes.
8. Expand useful data or diagnose the measured failure.
9. Verify Core ML conversion and Apple runtime behavior.
10. Return case-linked findings to TTR for shadow use.

Training stages contain 1,000, 5,000, 20,000, then 50,000 accepted HCF frames.
Count independent groups separately. Reserve at least 30 development groups and 30 final-audit groups initially.
These counts do not establish deployment safety. Preserve separate calibration membership.
Keep related artwork, profiles, seeds, repeated images, and derivatives in connected groups.
Cover qualified layout, control, position, size, spacing, clipping, artwork, theme, decoration, and no-focus conditions.
Report unsupported cells. Do not assign unknown focus as a negative label.

Use 1 seed for screening. Repeat selected configurations with 3 seeds total.
Expand only after useful gains or a specific unresolved coverage question.
After 2 unsuccessful data-growth stages, stop expansion and diagnose.
Improved target selection cannot increase wrong selections on matched development cases.
Replacement candidates must lose no retained previous successes.
Final audit follows frozen models and thresholds. Do not tune against the audit.

## Storage and future recovery

Use the verified `/Volumes/training-drive/data/NUIAK` volume for bulk artifacts.
Keep environments, source, and compact metadata local. Do not train over SMB.
Reserve packaging and extraction space. Preserve 20% free volume capacity.
Close producer shards before 70% of their enforced quota. Pause until verified offload frees space.
Keep one payload per content hash while preserving all capture-event records.

S1 qualifies a named worker host or LittleDog backup destination and retention owner.
S2 queues immutable backup with exact receiver receipts.
S3 restores named artifacts into new destinations and verifies every hash.
S4 restores a shard and checkpoint on another machine and reproduces evaluation.
S5 permits cleanup only after verified preservation and recorded restoration paths.
These remain stretch tasks. Execution copies are not automatically backups.

## Worker handoffs

worker-host-Coordinator owns delivery, resource claims, and cross-project dependencies.
worker-host-NUIAK owns GPU execution after qualified input delivery and storage reservation.
LittleDog prepares context, checks named inputs, and assembles deterministic reports after workflow qualification.
TTR workers own native generation and restoration. research-host-NUIAK owns data admission and Apple qualification.
Each handoff fixes input hashes, entrypoints, output limits, stop conditions, and acceptance checks.
Worker suggestions do not expand user approval.

## Efficiency and acceptance

Target 24 hours of estimated ready work when qualified inputs permit it.
Blocked reservations do not count as ready capacity. Do not repeat finished jobs for occupancy.
Keep 800 s and 100 MB diagnostic defaults. Larger jobs need explicit study budgets.
Measure 3 campaigns against retained baseline evidence.
Record time to decision, manual interventions, idle causes, accepted examples/hour, repeated bytes, GPU-hours, and available token usage.
Record backup throughput, restore time, and recoverable bytes once backup tasks qualify.
Target admission within 1 dispatch cycle, 50% fewer interventions, and no duplicate execution after reconnect.
Unknown historical metrics remain unavailable.

Test authentication, additions, restart, cancellation, changed hashes, missing inputs, storage exhaustion, and failed receipts.
Test label conflicts, identical profiles, ancestry leakage, resume equivalence, and incomplete result rejection.
Run focused tests and one integrated offline Swift pass after code integration.

## Current evidence

The named diagnostic passes its archive hash and all 56 manifest hashes.
All 3 pairs pass existing schema4 structural checks and recipe-reference hydration.
Matched button profiles have identical decoded pixels. The artwork pair has no Standard counterpart.
No positive visible HCF family qualifies from this delivery. All examples remain outside training.
The source report is `reports/work/HCF357/source-review.json`.
The archive contains a harmless root-directory entry; bounded extraction skips only that entry.
No incoming producer code executes.

The verified USB volume has approximately 1.7 TiB free.
A 4-image warm-cache smoke measures 14.48 images/s on USB and 15.02 images/s locally.
This does not qualify sustained training throughput. worker host capacity and backup retention remain unverified.

## Implementation handoff

Follow-up: [FOCUS358 and HCF358](Focus358.md) registers the complete study graph and measured duration tests.
peer-host-TTR confirms delivery, acknowledgment, and exact shared-copy cleanup at cursor 430.
This supersedes the earlier unconfirmed-forwarding snapshot below.
The 50,000-frame stage needs a new storage decision before execution; current sample sizes exceed the retained-artifact limit.
No storage limit changes or HCF training admission occurs.

All 188 focused checks pass. The native Swift build and 187 serial Swift tests pass.
The default Swift path fails on generated bundle metadata. The parallel native test attempt stalls and is stopped by exact owned PIDs.
No certificates, signing settings, system services, or unrelated test processes change.
The live addition endpoint accepts approved hashes. The server remains enabled after an idle-boundary reload.
Three decode jobs complete in 6.69 s of worker time. Three failed interpreter-only attempts remain preserved.
The corrected launcher keeps the project virtual environment. Readiness now detects an incorrect production interpreter.
No new model improves. HCF collection remains gated on visible-effect evidence and bounded producer offload.
The receipt is published with the existing SMB-safe move after hard-link publication fails.
Worker requests are stored at cursor 420. The precise follow-up is stored at cursor 426.
Forwarding, worker acceptance, backup capacity, and sustained I/O remain unverified.
The coordinator's automatic help works without inference, but its reply does not define the required structured event fields.
Preparation takes approximately 30 min against the 60–120 min estimate. Future capture and training time are separate.
