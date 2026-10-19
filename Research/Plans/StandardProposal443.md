# STANDARD443 — Full-screen Standard focus through reusable graphs

Owner: Maximum-mini-NUIAK. Date: 2026-10-18.

## Question and controlled comparisons

Does the Standard-only crop model help full-screen selection when compatible detector proposals replace empty ring proposals?
Compare the retained mixed crop model with the completed Standard-only crop model.
Repeat this comparison with the retained detector and corrected experimental detector.
Keep captures, preprocessing, thresholds, mappings, and known-box reference scores unchanged.

Use 8 retained development sets: buttons, rows, tabs, diamond decoration, edge clearance, no-focus, small decoration, and tall controls.
Do not generate new images, change data roles, or train during this tranche.
HCF measurements remain separate optional slices. Standard remains the primary target.

## Graph

Each detector branch contains 8 T57 scoring jobs, 1 summary, and 2 conditional follow-ups.
The cross-detector report consumes both summaries. It performs no inference.
There are 23 jobs in total. Only the selected follow-up executes for each branch.
An inconclusive decision releases neither follow-up.

The summary preserves the earlier full-suite decision and its consumer regressions.
A better detector subset cannot erase previously lost successes.
Every report records model acceptance as false. No branch promotes models or authorizes navigation.

Report these measurements separately:

- Missing focused-control proposals.
- Correct selections, wrong selections, misses, and no-focus abstentions.
- Matched gains, lost successes, and new wrong selections.
- Counts above the frozen threshold and the gap between the 2 largest scores.
- Standard and optional HCF support, with independent group counts.
- Known-box results as diagnostics, not full-screen performance.

The cross-detector report requires identical frames, groups, models, and known-box decisions.
It measures proposal recovery and loss alongside the resulting selection changes.
No inspected cases become final-audit or training examples.

## Reusable authoring improvement

`proposal_campaign443.py --author` accepts existing reference jobs and candidate scoring jobs.
It matches inputs by capture identity and checks tool, mapping, and ring-proposal identities.
It reuses verified completed outputs instead of manually copying paths and hashes.
It compiles T57 jobs and reusable report branches through the current queue contracts.

Two short descriptions use the same author and report workers.
The report preserves all earlier consumer failures through a pinned decision dependency.
The command writes drafts only. Admission still requires explicit job IDs.
Use the qualified transaction option for groups of at most 10 exact approvals.
The background runner retains execution ownership.

## Runtime and budgets

Each job retains the 800 s and 100 MB diagnostic limits.
Eight comparable retained-detector jobs took 136.53 s in total.
Eight comparable experimental-detector jobs took 139.06 s in total.
These are planning comparisons, not exact-input ETA samples for the new candidate.
Reports have no comparable measured history yet. Do not claim overnight capacity from these jobs.
The implementation estimate is 60–90 min. Worker execution is separate.

## Decisions after execution

If focused proposals remain absent, prioritize detector coverage instead of another crop fit.
If proposals exist but several scores pass the threshold, investigate competing controls and training balance.
If proposals exist but all scores fail, inspect measured crop geometry and preserved positive crops.
If detector changes recover selections but add wrong selections, keep the detector experimental.
If an apparent gain loses earlier successes, preserve the failure and reject replacement.

Do not launch another training correction merely because these diagnostic jobs finish.
Use the case-linked findings to define the next bounded comparison.

## Delivery and verification

All 23 immutable jobs are registered and individually approved through transactions of at most 10 jobs.
The admission snapshot shows 1 running job, 15 ready scoring jobs, and 7 dependent reports or branches.
The existing runner starts execution without a restart.
Nine new tests cover valid graphs, changed inputs, invalid scores, duplicate cases, no-focus errors, and failed report handling.
The contrast worker also executes through an isolated queue without repeated scoring.
Existing campaign and transaction tests pass. Offline Swift checks pass 177 Swift Testing cases and 14 XCTest cases.
Local admission receipts and the snapshot remain under `reports/work/STANDARD443`.
Both campaign reports and the cross-detector report now complete.
Both supported branches remain unselected. The contradicted branches complete.
The Standard-only replacement fails preservation. See [SELECTION444](BoundedSelection444.md) for measured counts and the approved follow-ups.
