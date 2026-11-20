# Maximum-mini-NUIAK nightly review — November 8, 2026

Window from November 8 at 07:46:24.717 UTC through November 9 at 07:47:40.449 UTC. The ledger records 82 finished attempts. [Attempt IDs and interval totals](../reports/work/NIGHTLY-20261108/attempts.json)

## What improved

No verified model improvement this review period. All measurements below use development inputs and remain provisional.

## What we learned

SWEEP602 compared 4 focus positions on 1 training-origin parallax layout. The shipped focus checkpoint selected 0/4 correctly under each neighbor brightness. It made 1 wrong selection with bright neighbors and 3 with dark neighbors. At threshold 0.85, Programme seed 371 selected 4/4 under each condition. Seed 372 selected none and produced 4 misses per condition. The 8 frames reuse 1 layout. These results use supplied boxes. They do not establish independent app accuracy. [Six scoring jobs](../reports/work/SWEEP602/admitted.json)

## What regressed

On the NewsTV positive panel, the wider crop recovered 1/10 at each seed. The recovered controls differed. On Photo Guessing Game, seed 371 gained 4 but lost 3 previous successes. Seed 372 gained 1 but lost 2. Both seeds lost the same previously correct control, photo-dev-when-focused. These paired joins use identical frame IDs, image hashes, and checkpoints within each seed. Positive-only panels cannot measure false selections. Retain the original crop. [Seed 371 margin results](../reports/work/research-queue/jobs/eval601-margin15-photo-s371/attempts/1/out/benchmark_summary.json) · [Original crop results](../reports/work/research-queue/jobs/comp600-positive-photo-programme-s371/attempts/1/out/benchmark_summary.json)

Both COMP600 training attempts timed out at their 1,800 s guards. Their last progress receipts show epoch 30 in progress and epoch 28 in progress. Output files alone cannot establish completion or restoration. Keep downstream competitor comparisons blocked until a verified continuation has an explicit remaining budget.

## What runs next

B405-294 has 4 definition-valid T63 diagnostics. Reuse both original control checkpoints on the same parallax positions, at each brightness. Compare against the 4 existing Programme arms. This tests whether the seed split precedes the Programme change. If both controls reproduce it, investigate seed sensitivity. If the treatment changes it, inspect the individual recovered and lost positions. If results depend on position, require another layout. Each job has an 800 s and 100 MB ceiling. [Exact batch](Experiments/batches/B405-294.json)

## Queue health

The dashboard supplied a cached readiness snapshot. The separate live health response showed an active runner waiting for work. Ready 0, running 0, dependent 440, otherwise blocked 10, awaiting approval 9, exhausted 129, unselected 29. Ready duration was 0 min. The 4 prepared diagnostics would take about 11 s together, based on the 6 preceding runs. Jobs released, admitted, and continued this pass: 0.

The runner completed 80 attempts and failed 2. Non-overlapping execution occupied 185 s on completed attempts and 3,602 s on failed attempts. The remaining 82,689 s had no recorded queue execution. [Snapshot](../reports/work/NIGHTLY-20261108/state.json)

## Blockers and approvals

Automatic approval review rejected registering and approving the 4 diagnostics together. Its stated reason was the user approval requirement for provisional results. Definitions and input checks succeeded separately. Admission remains open. This review authorizes no metric change.

The Office gallery contains 66 settled Kanopy frames in 1 recording. A frozen reviewer export is still needed before scoring. Keep suggestion-assisted annotations identifiable. Exclude private or unresolved frames as appropriate. Preserve related routes as groups. [Private blinded review](../reports/work/OFFICE603/office-blinded-gallery.html)

Sillycon-TTR supplied original color measurements for 3 suspected Store derivatives. All 3 differ from the retained regional measurements. This weakens the unchanged crop/resize hypothesis. Transformed ancestry remains unknown. BigDog-Coordinator stored the disposition at cursor 2062. Forwarding remains unverified.

## Priority changes and reasons

Prioritize blinded Office labels for Standard focus. The repeated synthetic layout cannot measure transfer to ordinary app screens. Detector precision also needs complete visible-control annotations. Keep extra margin experiments behind diagnosis of the control lost at both seeds. For independent iOS work, retain the secondary-text legibility question from the last review. No new iOS model comparison was verified this period. HCF remains optional and needs independent no-focus coverage.
