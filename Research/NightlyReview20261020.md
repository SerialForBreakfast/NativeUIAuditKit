# Nightly research review — 2026-10-20 UTC

Owner: Maximum-mini-NUIAK.
This review follows the previous durable nightly ledger.
The exact window and attempt identities are in `reports/work/NIGHTLY-20261020/review-window.json`.
The window runs from October 19 at 06:57:19 UTC through October 20 at 06:52:59 UTC.
Completion time uses attempt start plus recorded duration.
The window contains 308 completed attempts and 27 failed attempts.
Execution counts are not scientific results or independent trials.

## What improved

Measured-proposal crop training improves Standard correct selections from 48 to 49 across 91 development observations, without lost successes or new wrong selections.
All 3 no-focus abstentions remain correct.
The observations span 25 recorded groups. These identifiers do not establish independent evaluation.
The policy selects CROP471 on all observations. Its fallback adds no recovery.
No model qualifies for release or navigation authority.

Evidence: `policy473-final/attempts/1/out/decision.json` under the local queue.
Its output receipt passes content verification.
The gained case is `nctrl417-dev-tab-1-standard-item-0-0`.

## What we learned

CROP471 improves known-box selections, but missing proposals and retained consumer failures remain unresolved.
Better bottom-row coverage does not explain the crop failures.
Coverage rises from 94/96 to 96/96 matched controls, while 3 lost cases also fail known-box scoring.
B405-251 closes as contradicted. Another geometry-only rerun is not useful.

The completed iOS class-agnostic analysis leaves 165 misses among 2,030 label observations.
It identifies 68 mislocalized labels within those misses.
These are cached development diagnostics, not new independent accuracy measurements.
Six new geometry reports will identify the sizes and widths that need repair.

## What regressed

DETECTOR469R loses 3 prior Standard position successes.
Position selections fall from 26/48 to 24/48.
Robustness rises from 8/16 to 9/16, but loses 1 previous success.
The replacement remains rejected despite aggregate gains.
Standard, iOS, checkpoints, and shipped models remain unchanged.

Most historical failed attempts report process failures.
More runtime cannot repair missing evidence, source drift, or malformed inputs.
No additional exhausted run qualifies for automatic continuation in this review.
Preserve original failures and completed successors.

## What runs next

1. CROP474 repeats seed 371 with seed 372.
   Its 88 approved jobs include 1 fit and comparisons against both retained controls.
   It decides whether the development gain repeats without losing successes.
2. B405-255 adds 6 approved T42 reports using retained iOS predictions.
   It groups residual class-agnostic failures by geometry.
   It decides whether small-control or broader coverage repair has higher value.
3. Existing conditional CROP474 reports identify regressions or independent verification requirements.
   They do not start additional training or promote models.

The new iOS jobs permit 800 s and 100 MB each.
The combined ceiling is 4,800 s and 600 MB, not an execution estimate.
They do not rerun inference, change labels, or fit models.

## Queue health

The runner reports healthy continuous execution with CROP474 training active.
CROP474 contains 1 running job and 87 dependent jobs at the review snapshot.
The refill adds 6 approved independent diagnostics. All 6 pass readiness checks.
The catalog initially reports 0 ready jobs and 468 blocked jobs.
That blocked count includes dependency waits and historical records; it is not 468 unresolved research questions.
The raw attempt inventory includes 2,177 completed attempts and 105 failed latest attempts.
It also contains 578 unattempted jobs and 1 unfinished attempt.
These raw counts do not establish readiness or current scientific blockers.

The prior comparable fit takes about 20 min.
The 12 comparable iOS reports have a median duration of 0.287 s.
The 6 new reports therefore estimate about 2 s of execution, excluding queue overhead.
CROP474 scoring duration remains unmeasured for this exact batch.
The 25-ready-job and overnight-duration targets remain unmet.
No arbitrary sweep or redundant fit is added to fill time.

## TTR handoff and blockers

Replies through cursor 1058 are read and acknowledged.
Sillycon-TTR accepts IMPORT472 for review only.
The exact requested converter, tests, and result are published for independent inspection.
The share does not support hard links. Verified copies complete the metadata publication instead.
No conversion or capture repeats.

Two new metadata offers pass exact size and hash checks.
The action review contains 35 agent-reviewed records from 10 development images.
TTR reports paired OCR phrase matches of 39/40 versus 22/40, without lost baseline phrases.
The binaries differ, so this is not a mode-only comparison.
These findings do not establish image-risk accuracy, independent human labels, detector classes, or training eligibility.
The clipped “Not Now” failure remains preserved.
Local review accepts the material as attributed research evidence only.

Canonical interruption classes remain unreviewed. Profiles remain unavailable.
Maximum-mini-NUIAK needs independent class evidence before detector training admission.
BigDog-Coordinator still owns the reported cross-project routing mismatch.
The response is stored at cursor 1060. Storage does not prove recipient execution.
No new human approval is needed for the 6 diagnostics.

## Priority changes

Keep Standard repeatability and complete-path preservation first.
Use independent iOS geometry analysis while that fit runs.
Keep HCF optional.
Lower repeated fallback and geometry-only work because the latest evidence does not justify another identical comparison.
Prioritize reviewed repair membership and class labels before another detector fit.
Do not repeat the 10-image action review or treat development exposure as held-out evidence.

The catalog validates all 150 plans.
No executable source changes occur. No Swift rebuild is required.
No runner restart, direct training, installation, deletion, commit, or model promotion occurs.
