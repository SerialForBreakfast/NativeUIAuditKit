# Nightly research review — October 31, 2026 UTC

Owner: Maximum-mini-NUIAK.
Review window: October 30, 06:41:17.635 UTC through October 31, 06:46:06.133 UTC.
The window starts at the last successful nightly cutoff. The verified USB volume has about 1.5 TiB free.
Exact attempt IDs, hashes, and intervals are in `reports/work/NIGHTLY-20261031/review-window.json`.

## What improved

No verified model improvement this review period.
No candidate qualifies as a replacement. Standard and shipped models remain unchanged.
Native-row gains were already established in the preceding review. This review does not count them again as a new improvement.

The runner completes 101 attempts, including 4 training fits. All recorded output inventories verify.
Execution completion, verified artifacts, and model acceptance remain separate outcomes.
NewsTV now has 1 captured pilot case from 2 trials. The draft has 23 SDK rectangles awaiting blinded human review.
This is collection progress, not an accuracy result or an independently qualified application.

## What we learned

Broader original-data coverage does not resolve iOS retention losses.
The original-only fit takes 98.3 min. The additive fit takes 102.2 min.
Their combined 200.4 min falls within the prior 3.5–4 h estimate.
The additive model detects 24/24 new development rows; the control detects 8/24.
These generated screens do not establish real-app accuracy.

Three retained tvOS Standard Fixture replays produce partial results and no final selection.
Registered-control geometry coverage is 5/12 at IoU 0.5, ignoring classes. This is not complete detection recall or mAP.
Ignoring partial suppression yields 1 correct selection, 1 wrong selection, and 1 abstention. Keep the existing gate.
NewsTV SDK state remains inactive despite XCTest foreground evidence. Focus remains unknown, not verified no-focus.

Sillycon-TTR reports published source ac85177b8c9d1185b8d20594e759134f5dc0dbd1 and 16 passing focused checks.
The change adds observed preprocessing, manifest identity, separate model digests, and a build-supplied base revision.
The base revision does not attest a clean source tree. Executed crop and tensor identities remain unavailable.
Maximum-mini-NUIAK has read this delivery but has not built or independently qualified the new revision.
Forwarded replies 1823, 1825, 1827, and 1829 confirm receipt of earlier requests and TTR ownership of the scoped correction.

## What regressed

Frozen-feature training loses 16 Run013 detections despite preserving 24/24 new rows.
The wider additive arm loses 8 Run013 detections. Its original-only control loses 9.
The retained checkpoint still loses 8. Targeted rehearsal loses 13 Run013 detections and 7 ROW545 detections.
These overlapping comparisons must not be added into one error count.
No replacement passes preservation. The catalog now records B405-269 as contradicted through its established review interface.
There are no failed terminal attempts within this window. Model regressions still reject successful execution results.

## What runs next and what each test decides

No new executable jobs are admitted, released, or continued during this review.
The queue has no useful ready duration. This review does not claim an overnight reserve.

1. REAL550-PROVENANCE: qualify the published TTR source and retained replay through the actual consumer path.
   This decides which runtime identities are observed and which remain unavailable. No new capture is required for replay qualification.
2. REAL543-REVIEW: review the captured NewsTV screen without model predictions.
   This establishes visible control coverage, semantic labels, and eligible detection metrics. Unknown focus excludes focus scoring only.
3. RETENTION547-OBJECTIVE: define and qualify class preservation using training-only anchors before another fit.
   Freeze matched controls, membership, budgets, and full retention gates. Existing failed configurations do not justify another run.
4. SDK539-APPS: continue Swiftfin and game integration independently of the SDK state discrepancy.
   These tasks add independent application coverage. WeatherFeels remains blocked by the missing Apple Metal toolchain.
5. QUEUE548: qualify optional HCF restoration against the original trainer with deduplication=False.
   Continue only after exact restoration parity and remaining cumulative budget are verified. Preserve the original 30-epoch endpoint.

These are preparation or implementation tasks, not admitted experiments.
The current nightly scope cannot build the missing integration or objective adapter.
Existing scoring and retained-report templates are available, but they cannot supply missing labels or runtime observations.
Completed conditional diagnostics remain reused evidence. No answered question is repeated to occupy hardware.

## Queue health

One health and readiness pass records 0 ready, 0 running, and 403 active blocked entries.
Of these, 391 have dependency blockers: 387 incomplete, 3 changed specifications, and 1 missing output.
The remaining 12 comprise 10 changed inputs, 1 unqualified restoration chain, and 1 Maximum-mini-TTR requirement.
There are 22 unselected branches, 105 exhausted attempts, 400 superseded entries, and 3,611 completed jobs.
Exhausted attempts are history, not automatic continuation authority. Dependent entries are not independent investigations.
The runner is active and waiting at port 8765. It needs no restart.
Useful ready duration is 0 min. Dependent duration is not qualified and is not counted as ready time.

Non-overlapping completed execution totals 14,373.432 s over an 86,688.498 s window: 16.58% occupancy.
Failed execution totals 0 s. The remaining 72,315.066 s has no recorded queue execution.
Historical idle versus stopped time is unavailable. Occupancy measures execution, not scientific progress.
Intervals use attempt start plus recorded wall time and are clipped to the review window.
Direct source builds and manual qualification checks are outside this detached-runner measure.

## Blockers and approvals

Maximum-mini-NUIAK owns source qualification, the consumer connection, and iOS objective preparation.
The maintainer or designated reviewer supplies blinded NewsTV labels. No predictions have been viewed for that pilot case.
Sillycon-TTR owns the lifecycle diagnosis and the requested executed crop contract.
The coordinator stores the retained-sample references and capability request at cursor 1830. Forwarding is not yet confirmed.
The approved shared volume is unmounted. References and hashes are sent; no raw bundle transfer is claimed.
No new download, budget, installation, service change, or promotion approval is requested in this review.
Source qualification is deferred to implementation work, not blocked on another peer acknowledgment.

## Priority changes and reasons

Move REAL550 from waiting for publication to exact-source qualification. Published source is now available according to TTR.
Keep Standard consumer measurement first. Keep NewsTV detection review independent of the unresolved focus state.
Stop wider-data and targeted-rehearsal repeats. Their retention failures support a changed objective, not more unchanged epochs.
Keep independent application preparation active. Keep HCF separate and optional.

Evidence: [Standard replay](Real550ConsumerReplay.md), [iOS coverage](Iteration549Results.md),
[training comparisons](Retention547Training.md), and [independent benchmark protocol](RealAppValidation543.md).
