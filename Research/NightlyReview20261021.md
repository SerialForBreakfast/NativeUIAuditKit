# Nightly research review — 2026-10-21 UTC

Owner: Maximum-mini-NUIAK.
The window starts at the previous nightly cutoff, October 20 at 06:52:59 UTC.
The exact end and 430 attempt identities are recorded in `reports/work/NIGHTLY-20261021/review-window.json`.
The window contains 415 completed attempts and 15 failed attempts. These are not independent scientific observations.
The USB mount passes verification through the scoped system check. The sandboxed DiskManagement check fails first.

## What improved

No verified model improvement this review period.
Several development slices gain cases, but their candidates fail preservation gates.
No model receives release approval or navigation authority.

## What we learned

Increasing original iOS training coverage to 1,024 images does not solve retention.
It gains 36 detections and loses 36 against Run013.
Against the 128-image control, it gains 37 and loses 35.
Changing coverage also changes optimizer updates at fixed epochs. Do not infer a coverage-only causal effect.

Both Standard seed variants preserve fixed-proposal outcomes but alter known-box and consumer-crop results.
Seeds 372 and 373 gain 3 and 6 Standard known-box successes respectively.
They lose 4 and 3 consumer-crop successes respectively, with corresponding new wrong selections.
Small known-box gains therefore do not establish a better consumer model.

The confidence-tier fallback preserves no-focus abstention on one retained scene.
B405-257 closes as supported for that narrow question. Related profiles and arms do not increase independent support.

## What regressed

| Comparison | Gains | Lost successes |
|---|---:|---:|
| IOS482 mixed versus matched control | 10 | 36 |
| IOS483 toggle mixture versus matched control | 30 | 41 |
| Standard quarter corpus, consumer crops | 0 | 5 |
| Standard half corpus, consumer crops | 2 | 3 |
| Deduplicated Standard corpus, consumer crops | 8 | 3 |

Deduplicated training also adds 2 wrong consumer-frame selections and loses 1 Standard known-box success.
B405-122 closes as contradicted. Keep the full-corpus control rather than selecting smaller membership from aggregate scores.
All listed terminal output receipts pass content verification. Case identities remain in their decision JSON files.
Do not sum overlapping profiles, arms, or campaigns into one accuracy metric.

## What runs next and what each test decides

1. RECOVERY488 needs repeat-aware restoration qualification before the approved DEDUP486 continuation.
   It decides whether the original exposure-controlled experiment can finish without discarding checkpoint state.
2. REHEARSAL482-RESERVE needs one qualified detector optimization control.
   It should test retention after the failed coverage-only and naive-mixing approaches.
3. Reuse completed seed and corpus reports before proposing another crop fit.
   Prioritize consumer failures over further known-box-only gains.

These are preparation requirements, not newly ready experiments. No new fit is admitted during this review.
The current templates do not support the required continuation or detector optimization setting safely.
Do not create more failed-method repeats merely to occupy hardware.

## Queue health

The health endpoint reports continuous execution enabled, busy true, no current job, and no reported error.
This does not establish active training. The raw directory scan finds no running job.
Raw states contain 2,592 complete, 644 blocked, 120 exhausted, and 28 pending entries.
These historical totals do not establish ready work or actionable blocker counts.

The readiness command fails because `jobs/.DS_Store` is treated as a job directory.
Exact error: `NotADirectoryError` while opening `.DS_Store/spec.json`.
Ready count and estimated ready duration remain unavailable. Do not count all 28 pending entries as ready.
The reviewed reserve and seed graphs have finished their selected branches.
Four blocked success branches across those graphs are unselected, not repair failures.
The DEDUP486 exposure branch remains exhausted with dependent comparisons waiting.
The overnight reserve target is unmet. No filler work is added.

## Blockers and approvals

RECOVERY488 already has approval for 30 additional minutes after parity passes.
Its checkpoint preserves completed epoch 16. Existing restoration tools hard-code repeat 1, not repeat 9.
Keep the original 30 epochs, evidence, and 2 GiB limit. No new budget request is needed for this approved scope.

Maximum-mini-NUIAK must repair directory filtering in readiness enumeration at a safe source-update boundary.
Acceptance requires a mixed directory test, unchanged valid-job counts, and restored CLI/dashboard readiness without a runner restart during active work.
This nightly review does not modify runtime sources or remove the metadata file.

Live TTR and worker replies are not verified in this review.
The existing coordination guide is available, but the enrolled client/profile was not located during the bounded inspection.
No old reply is presented as current. No transfer or peer acknowledgment is claimed.
Complete the coordination check through the verified connection record during the next implementation session.

## Priority changes and reasons

Put readiness enumeration and repeat-aware restoration first because they obstruct accurate planning and approved continuation.
Next, qualify the detector optimization control. More original-data coverage alone still loses retained detections.
Lower naive mixing, corpus reduction, and further seed expansion because the completed comparisons reject replacement.
Keep Standard and iOS first. HCF remains optional.
Preserve shipped models, checkpoints, original captures, data roles, and previous successes.

No source code, services, scheduled tasks, Git history, or models change in this review.
The catalog records B405-122 as contradicted and B405-257 as supported through its established interface.

## Evidence references

- `ios484-coverage-decision`, attempt 1.
- `coverage485-1024-vs-128-decision`, attempt 1.
- `ios482-matched-decision` and `ios483-matched-decision`, attempt 1.
- `reserve483-quarter-decision` and `reserve483-half-decision`, attempt 1.
- `stability487-seed372-decision` and `stability487-seed373-decision`, attempt 1.
- `dedup486-unique-decision` and `native482-nofocus-nofocus`, attempt 1.
