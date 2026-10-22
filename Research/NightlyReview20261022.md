# Nightly research review — 2026-10-22 UTC

Owner: Maximum-mini-NUIAK.
Window: 2026-10-21 06:44:27 UTC through 2026-10-22 06:49:09 UTC.
The previous durable report defines the start. The heartbeat defines the cutoff.
Private attempt identities and result hashes are in `reports/work/NIGHTLY-20261022/review-window.json`.
The USB volume is mounted with about 1.6 TiB available.

## What improved

No verified model improvement this review period.
There is a useful consumer integration improvement, not a new trained model.
The optional TTR proposal correction improves HCF selection from 0/16 to 16/16 on 4 retained Fixture conditions, without lost successes.
Standard-profile selections remain 10/16. All 6 no-focus observations remain correct across 3 related scenes and 2 profiles.
FP32 conversion resolves parity failures. The retained replay verifies 38 observations and 264 crop hashes, with maximum error below 0.000003.
These are development and integration results. They do not establish independent application accuracy.
This review does not activate or promote anything. The previously activated observer and Standard remain unchanged.
See [HCF490 evidence](HCF490Results.md).

## What we learned

The latest native grid fails both proposal coverage and absolute crop selection.
Measured body geometry does not recover selection. The mixed model gives high scores to 2 negative crops.
The unique-selection rule abstains. Do not report those crop errors as executed wrong navigation.
The paired HCF arrival score rises and its departure score falls. The mixed departure score moves in the wrong direction.
FOCUS329 and notification candidates 42 and 44 detect the retained switch in both orders.
This is one training-source pair. Reversed order is not an independent native action.
Earlier 408-pair candidate gains remain historical evidence, not improvements earned again during this window.
No new iOS execution appears in the reviewed queue receipts. Do not describe tvOS no-focus tests as iOS work.

## What regressed

The window contains 15 failed attempts. Earlier FP16 and quantized conversions fail parity; their evidence remains preserved.
FP32 successors address conversion, not the native proposal and crop-scoring failures.
No new model replaces Standard. No previous successful artifact is removed.
All declared output hashes across the 146 reviewed attempt receipts verify.

## What runs next and what each test decides

1. Finish NIGHTLY489-READINESS in an implementation session. It restores accurate ready counts and queue planning.
2. Finish RECOVERY488 restoration qualification. It releases the already approved DEDUP486 continuation if parity passes.
3. Qualify REHEARSAL482-RESERVE detector settings. This tests retention after failed naive mixing and coverage changes.
4. Obtain existing native motion inputs for FOCUS355 P10/P12/P14 before new capture requests.
   Compare FOCUS329 and candidates 42/44 on matched static and moving backgrounds.
   Include fixed focus, moved focus, verified absence, arrival, and disappearance.
   Require no lost successes. Report selection and transition errors separately.

These are preparation requirements, not newly executable jobs. No jobs are admitted, released, or continued in this review.
Do not repeat the completed single-pair checks or static no-focus replay merely to occupy the runner.
The existing catalog identifies frozen-feature, teacher-consistency, and checkpoint-selection alternatives, but their qualification requirements remain open.
No new catalog outcome is justified. Preserve existing confirmed decisions instead of rewriting them.

## Queue health

The authenticated health check reports continuous execution enabled, no current job, and no error.
The runner says it waits for approved work that passes readiness checks. Do not restart this active runner.
The readiness command still fails on `jobs/.DS_Store/spec.json` with `NotADirectoryError`.
Running count is 0 in the health snapshot. Ready, dependent, and actionable blocked counts remain unavailable.
Estimated useful ready duration is unavailable. This review adds 0 s of ready work. The overnight target remains unmet.

The 24.08 h window contains 131 complete and 15 failed attempts, all in HCF490 variants.
Non-overlapping complete execution totals 477.28 s. Failed execution totals 31.29 s.
Recorded terminal execution occupies about 0.59% of the window: 0.55% complete and 0.04% failed.
The remaining time lacks terminal queue execution in this inventory. It is not a measurement of machine idleness.
Source builds, manual work, and attempts without terminal receipts are outside this metric. Scientific progress is not occupancy.

## Blockers and approvals

NIGHTLY489-READINESS remains unimplemented. Its existing acceptance checks cover metadata files beside valid job directories and CLI/dashboard recovery.
This planning-only review does not modify queue sources or delete metadata files.
RECOVERY488 has 30 additional approved minutes, conditional on verified restoration, within the original 30 epochs and 2 GiB limit.
A checkpoint alone does not satisfy that condition. Do not extend the budget or start from scratch.
Native motion inputs remain unverified. T75 consumes supplied offsets; its execution path does not measure motion from images.
T47 needs a verified absent-focus endpoint contract before temporal no-focus scoring. Static observer no-focus checks remain independent.
The enrolled coordinator reports no new messages after cursor 1189 and no unread attention.
The existing motion-capability request is stored. Forwarding and producer acceptance remain unconfirmed. No duplicate request is sent.

## Priority changes and reasons

Restore queue readiness and the approved continuation before more narrow crop diagnostics.
Restore independent Standard and iOS work through existing bounded implementation tasks.
Keep HCF motion qualification separate. Do not let its missing producer block unrelated detector work.
Lower further single-pair scoring because it no longer changes the decision.
Keep shipped models, original data roles, checkpoints, Standard behavior, and previous successes unchanged.

No code, services, schedules, Git history, runtime configuration, or models change in this review.
