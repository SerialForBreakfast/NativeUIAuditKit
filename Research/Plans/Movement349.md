# FOCUS349 — retain movement during appearance training

> Historical research record. Results retain their stated scope and limits.
> Host names are public aliases. Local evidence and execution records remain private.
> This publication does not revalidate earlier results or approve a model.

Owner: research-host-NUIAK.

FOCUS348 completes 35 comparisons. Gamma reduces target false changes but loses 56 retained successful decisions.
Its original training weights give unchanged cases 849.94 units and changed cases 810.06 units.
The difference is small. Do not describe this failure as proven class imbalance.

## Fixed correction

Test stronger movement influence in the augmented loss only.
Give changed auxiliary examples weight 2 and unchanged examples weight 1.
Normalize these weights against the scheduled training weights to keep total influence unchanged.
Keep original images, crops, primary weights, membership, initialization, and thresholds unchanged.
Reuse the FOCUS348 gamma run as the equal-budget control.
Use FOCUS329 initialization, 10 epochs, batch 16, seed 42, and learning rate 0.0001.
Use 2 CPU threads, 1,800 s, and 2 GiB of output.
Train only the existing detail and correction layers. Keep the existing preservation loss.
Use the last checkpoint. Do not retry or select an intermediate checkpoint.

## Acceptance

- Reduce false changes against unchanged-image training on the matched gamma cases.
- Recover movement decisions against FOCUS348 gamma.
- Lose no previous successful decision against FOCUS329.
- Report all retained appearances, frame orders, nuisance strengths, neighbors, and placeholders.
- Preserve native development exclusions and unknown source evidence.

## Office capture companion

Receive the 3 sanitized Office summaries with exact transfer checks.
Extend the existing recording audit with a summary-only input mode.
Check counts, duplicate identities, frame roles, command outcomes, and missing evidence.
Produce a case-linked review list without inventing focus labels or screen identities.
Request reviewed images and original event metadata through the existing handoff.
Verify the received raw archive with bounded extraction and exact image checks.
Survey real screen categories before selecting model review cases.
Score 21 selected visual pairs with FOCUS329, FOCUS348 gamma, and FOCUS349.
Keep these scores separate from accuracy. Prepare 8 frames with the existing annotation review tool.
Keep this session and related images in development. Keep HCF unknown without setting evidence.
No device operation or recapture belongs to this task.

## Queue

Register the correction once. Then register the 35 matched comparisons with fixed input hashes.
Run 5 jobs per cycle. Diagnostic limits remain 800 s and 100 MB.
Completed jobs do not repeat. Missing native inputs remain blocked.
Report useful work duration, not an artificial minimum number of ready jobs.
