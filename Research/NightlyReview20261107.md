# Maximum-mini-NUIAK nightly review — November 7, 2026

Window: November 7 07:42:58.722 through November 8 07:46:24.717 UTC. [119 attempt IDs and verified inventories](../reports/work/NIGHTLY-20261107/attempts.json). 108 completed, 11 failed. Measured completed execution 23,950 s, failed execution 29 s, uncovered time 62,627 s. Occupancy 27.7% by interval union. This measures queue execution only.

## What improved
No verified model improvement this review period. Provisional development result: teacher preservation improves legacy crop retention from 259/270 to 268/270 against the matched native control, with 5 new wrong real-app selections and 1 lost native selection. The shipped baseline retains 270/270. [Native comparison](../reports/work/research-queue/jobs/native593-comparison/attempts/1/out/benchmark_summary.json).

## What we learned
The native arm without teacher recovered 4 supplied-box observations across 2 related groups. Temporal pairs gave 5/6 movements for all 3 models; removing the before frame erased all 5 successes. Departure and moving backgrounds remain open. [Matched experiments](Parallel590592Results.md).
The shelf and eligibility development baseline returned 0/8 correct. Northstar reproduced the Alex/Sam ambiguity. Local crop scores match the runtime scores; executed pixels still need producer hashes. [Visual review](../reports/work/ARTPARITY595/shelf-pair-report.md).
On 24 Standard observations in the button, row and tab development panels, the raw proposals yielded 24 misses per model for controls, mixed hard negatives and Programme at both seeds. Candidate-specific scoring on shelf, eligibility and Northstar remains necessary before judging artwork training. [Fixed decision rule](Plans/HardNeg596.md).

## What regressed
The teacher also lost a calibration case. Stop the coefficient path. iOS foreground-only geometry training gained 5 detections and lost 2 against the matched control. Against Run013 it gained 21 and lost 8. Reject replacement. Test secondary-text legibility separately from row geometry. [Matched iOS report](../reports/work/research-queue/jobs/ios594-foreground-geometry-retention-decision/attempts/1/out/report.md).
The 11 failed attempts include native589 admission and 10 initial hard-negative training or publication attempts. Completed successors preserve their original records.

## What runs next and priorities
P0 remains testing artwork transfer on existing checkpoints. Maximum-mini-NUIAK needs a runner comparison that accepts a selected focus checkpoint on the pinned shelf, eligibility, and Northstar inputs. The existing artwork CLI selects detector checkpoints and fixes the focus classifier. Reuse production crops, record candidate hashes, reproduce shipped scores first, then count unique selections, wrong selections and abstentions at 0.85. Use existing diagnostic budgets. Implementation belongs to a separate work tranche.
Keep detector training behind complete annotations. Keep HCF optional. Prioritize iOS row-label review above another geometry-only fit.

## Queue health and blockers
Ready 0 (0 min), running 0, dependency-blocked 402, other blocked 10, awaiting approval 9, exhausted 127, unselected 29. Runner active and waiting. No jobs released, admitted or continued. Both Programme fits and their 6 evaluations already executed. [Readiness](../reports/work/NIGHTLY-20261107/readiness.json).

## TTR delivery
Maximum-mini-NUIAK received and hash-verified the 360-frame archive. Its 363 checksums passed. Its label files identify 90 scenes. All 304 training frames and 56 sports holdout frames retain separate roles. Supplied pixel identities do not cross splits. This verifies transfer and membership, not training admission or label accuracy. TTR provided observed focused bounds. Obtain same-frame competitor evidence before preparing binary training pairs. Receipt sent through BigDog-Coordinator. [Intake](../reports/work/NIGHTLY-20261107/intake-check.json).
