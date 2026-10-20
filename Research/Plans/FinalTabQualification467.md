# RECOVERY467 — Final tab qualification

## Verified findings

The final tab producer records all 24 expected frames. It fails after 195.32 s during Standard restoration.
The capture error is null. The only cleanup error is `profile_restore:profile-standard:None`.
The native receipt reports exhausted HCF evidence storage. No input follows that failed storage check.
Preserve the original capture, failed attempt, and recovery guard. Do not repeat capture.

USB offload verifies 1,883 PNG paths and 78 unique payloads totaling 410,367,255 bytes.
It replaces 89 duplicate entries with verified hard links. It removes no evidence paths and changes no journals.

## Approved execution

- `native467-restore-tab` restores Standard and verifies the original Fixture against the exact failed guard.
- `native467-review-tab` validates and republishes the existing 24 frames only after verified restoration.

Each job permits 800 s, 100 MB of outputs, and 1 attempt.
The detached runner owns execution. Neither job trains a model or admits training data.

## Qualification already complete

Five available training shards pass native label mapping across 120 capture events.
They contain 192 button annotations, 192 row annotations, and 96 tab annotations.
Combined checks with retained native data and new development captures pass across 20 training groups and 10 development groups.
These checks cover 158 distinct decoded images. Related events do not count as independent evidence.
The final tab shard still requires its restoration review before admission.

## Remaining graph

1. Verify the final review receipt and original image hashes.
2. Add the final shard to the exact admission configuration.
3. Check retained development and audit exclusions, including group, layout, and decoded image overlap.
4. Use T53 for admission and T87 for training frame preparation.
5. Use the existing canonical native label mapper for complete observed control inventories.
6. Compile matched training and comparisons through DETECTOR457.

Freeze initialization, seed, preprocessing, scoring thresholds, and evaluation membership.
Use 30 epochs, the approved 2 h limit, and 2 GiB per training run.
Retain Standard row and tab failures in the comparison contract.
Include native family, edge, decoration, and no-focus comparisons.
Report HCF separately. Preserve Standard, iOS, and shipped models.

Training is not ready until these input gates pass. No training job is approved from partial evidence.

## Peer feedback

The coordinator stores the repeated storage failure report at cursor 1000. Recipient delivery remains unverified.
Sillycon-TTR's alert design handoff reports incomplete native proof. It does not qualify this training corpus.
Review that separate design proposal without changing capture or training authority.

Local evidence resides in `reports/work/RECOVERY467/`.

## RECOVERY468 — Remove the redundant round trip

RECOVERY467 fails after 163.41 s. It first verifies Standard, then starts another HCF round trip.
The round trip leaves HCF active when the storage guard refuses restoration.
Accounting records 873,809,384 used bytes, 68,157,440 next-operation bytes, and 134,217,728 reserved bytes against 1 GiB.

The explicit `standard-restoration-v1` mode now runs only the existing Standard ensure route.
It does not qualify a new HCF round trip. Legacy qualification remains unchanged.
The consumer requires the mode to match the pinned plan. Fixture and ownership checks remain strict.
58 focused tests pass, including an assertion that restoration never calls the round-trip route.
The runner receives `native468-restore-standard` and `native468-review-tab` as explicit successors.
Original attempts remain preserved. The last 24 frames are not captured again.

New offload verifies 1,976 PNG paths and 79 unique payloads. It changes no pixels or recovery journals.
Execution and final training admission remain separate gates.
