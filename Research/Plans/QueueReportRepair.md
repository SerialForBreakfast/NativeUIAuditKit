# Restore useful queue work

Owner: Maximum-mini-NUIAK. Date: 2026-10-17.

## Completed preparation

- T64 compares verified nested selection reports without repeating scoring or training.
- T65 compares pinned detector scorecards through the existing case matcher.
- Both adapters pass positive and negative tests through an isolated queue.
- The focused suite passes 25 tests. Integrated offline Swift checks pass.
- The original 30 failed T15 attempts remain unchanged. B405-210 supplies their corrected report.

## Approved batch

| Tasks | Test | Decision |
| --- | --- | --- |
| B405-210 | Compare 30 retained crop-model pairs. | Preserve case-linked gains and losses after the report repair. |
| B405-211–212 | Compare 960 px against 640 px detection across 6 retained sets. | Determine whether resolution recovers narrow controls without lost successes. |
| B405-213–214 | Compare thresholds of 0.25 and 0.5 across the same 6 sets. | Determine whether confidence filtering explains missed controls. |

The batch contains 25 jobs for 3 questions. It does not contain 25 independent experiments.
The 12 detector comparisons depend on their corresponding inference jobs.
Each job keeps the 800 s and 100 MB limits. No training, new capture, or promotion is included.
Run 013 weights, images, labels, membership, and NMS remain fixed.
Only resolution or confidence changes in each comparison. Standard runtime settings remain unchanged.

The retained 640 px inference jobs take 3.90–4.20 s each across 6 runs.
These timings suggest a short diagnostic batch, not an overnight workload.
The 960 px duration is not yet measured. Do not use the 800 s ceiling as its ETA.
Unmatched predictions remain unverified detections, not automatically false positives.

## Next preparation priorities

The first batch completes. Resolution produces 60 gains and 322 losses, so reject it.
The threshold comparison produces 21 gains and zero losses. It also adds 44 unmatched detections.
Incomplete labels prevent calling those detections false positives or claiming better precision.

B405-215–218 extend the measured threshold idea with 23 jobs through T56, T57, T58, and T42.
The tvOS jobs use the same production detector and unchanged crop models at detection confidence 0.25.
They cover buttons, rows, tabs, no-focus scenes, edges, decorative diamonds, small decoration, and tall controls.
Compare each new report with its retained 0.5 full-screen report. Both models and both profiles remain separate.
Reject new wrong selections, lost prior successes, or lost no-focus abstentions.
The iOS class-free comparison is a diagnostic upper bound, not a proposed runtime rule.

1. Review the paired detector results before selecting a resolution or confidence correction.
2. Qualify training-only proposal-error sampling for rows and tall controls.
3. Compare within-screen competing controls only after its reusable training adapter passes positive and negative tests.

Do not use inspected development boxes as training examples.
Keep the proposed 50% native-exposure arm blocked because the lower doses already add wrong selections.
Later TTR verification requires actual Core ML and mapping files after local preservation checks pass.
