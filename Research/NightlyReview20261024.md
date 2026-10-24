# Nightly research review — 2026-10-24 UTC

Owner: Maximum-mini-NUIAK.
Window: 2026-10-23 06:41:04 UTC through 2026-10-24 06:40:07.545 UTC.
The preceding successful report defines the start. The heartbeat defines the cutoff.
Attempt IDs and result hashes are in `reports/work/NIGHTLY-20261024/review-window.json`.
The verified USB volume has about 1.6 TiB available.

## What improved

No verified model improvement this review period.
The teacher adapter executes and reports regressions through the existing queue. Neither candidate passes model acceptance.
Supported TTR export verifies all 9 retained files without another capture. Runtime readiness recovers after opening the existing source build.
These are execution improvements, not accuracy claims.

## What we learned

PROPOSAL497 completes all 8 matched detector-box comparisons. Their output hashes verify.
Standard has 43 observations: 40 focused and 3 no-focus, with 13 recorded scene groups.
Both teachers select 6 focused controls correctly with detector boxes. Both miss 33 and make 1 wrong selection.
Both preserve all 3 no-focus outcomes. Known boxes give 40 correct selections and 3 correct abstentions.
The detector proposes the focused control in only 6 of 40 focused observations. Adding ring proposals changes no Standard outcomes.
This makes proposal coverage the next Standard priority, not another teacher weight or seed.
Related frames and paired profiles are not independent evidence.

Optional HCF detector scoring rises from 14 to 16 correct selections for the changed teacher on these 40 focused observations.
This slice has no lost success or new wrong selection. It retains 1 wrong selection and does not qualify the candidate.
The broader teacher comparison still fails Standard retention and adds 2 wrong HCF raw-proposal selections.

Standard CPU batch sizes 4 and 8 preserve all decisions across 6 runs on 16 crops from 3 groups.
Maximum score difference is 4.45e-16. This workload does not establish a general throughput benefit.

## What regressed

TEACHER496 restores 1 consumer true positive against TEACHER495 but retains all 16 consumer false positives.
Both teachers lose 6 negative successes against retained Standard. Reject both replacements.
NATIVE494 frozen training loses 24 Standard known-box successes and adds 1 wrong selection against its matched control.
IOS494 original-only frozen training gains 25 detections and loses 22 against its recorded baseline. Reject replacement.
iOS detection findings do not establish tvOS focus performance. Incomplete native labels prevent broad false-positive claims.

The recorded execution window has 198 completed attempts and 1 failed recovery attempt.
Completed execution does not imply verified evidence or model acceptance.
PROPOSAL497's original summary references `report.json`; its producers emit `benchmark_summary.json`.
This authoring error prevents summary dispatch after all 8 producers finish.
The review registers and approves immutable successor `proposal497-native-report-r2` with the correct output references.
It reuses completed evidence. No inference, capture, or training repeats.

## What runs next

1. The corrected native report compares button, row, and tab outcomes from completed PROPOSAL497 jobs.
2. Maximum-mini-NUIAK must qualify one existing Fixture Simulator launch, then verify the scene identity through TTR.
   Sillycon-TTR confirms that no dedicated input-free Fixture launch command exists in the current CLI.
   Its supported setup uses `simctl launch` for the exact approved Simulator and installed Fixture app.
   This nightly review does not perform target setup or navigation. An implementation session must check ownership first.
   Preserve the 2 failed cases, 6 unattempted cases, remaining budgets, and retained export.
3. After valid recovery evidence exists, release the 4 approved session comparisons and their report through existing guards.
4. Qualify detector training annotations that address the missing Standard proposals before another matched fit.
   Keep iOS semantic completeness independent from this tvOS producer requirement.

No training continuation or new capture job is admitted. One reporting successor is admitted.
The catalog confirms B405-259 as contradicted: earlier consumer scoring gains 4 but loses 1 and adds 1 wrong selection.
B405-258 remains inconclusive. Its known-box gain does not establish complete-path retention.

## Queue health

The maintenance snapshot shows a healthy continuous runner, 0 running jobs, 0 ready jobs, and 0 awaiting approval.
Useful ready duration is 0 s before the reporting repair. The admitted report supplies seconds, not overnight work.
Five session-chain jobs remain dependent on Fixture recovery. One current recovery failure requires implementation work.
The global view combines 465 blocked or exhausted entries. This is not a count of independent actionable blockers.
The catalog contains 94 unresolved records without plans. Missing Fixture data affects 21 records through dependencies.
Native transition evidence affects another listed group of 9 dependent records; these totals can overlap.

Non-overlapping completed execution totals 5,576.12 s. Failed execution totals 9.48 s.
Total recorded execution is 6.47 percent of the 86,343.545 s window. The remaining 93.53 percent has no recorded execution.
These figures measure recorded occupancy, not useful outcomes or verified runner availability throughout the window.
The overnight reserve target remains unmet. Do not extend rejected fits or repeat answered diagnostics to improve occupancy.

## Blockers and approvals

TTR messages through cursor 1304 are read and acknowledged.
Reply 1302 answers the Fixture launch request. No peer files require transfer or cleanup.
The independent SDK follow-up remains local and uncommitted on Sillycon-TTR. It is not a source revision for ingestion.
Its full callback latency misses the stated 0.2 ms goal. Recorder-hook timing does not substitute for full latency.
Do not use those SDK claims as training annotations or new execution authority.

## Priority changes and reasons

Raise Standard proposal coverage and qualified annotation production above further crop-teacher tuning.
Restore the Fixture producer through supported setup because it releases multiple independent research questions.
Keep iOS label completeness as a separate high-priority preparation task.
Keep optional HCF separate. Preserve Standard, shipped models, captures, checkpoints, and all previous successes.
