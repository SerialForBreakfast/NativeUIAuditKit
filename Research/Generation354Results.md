# Controlled native results

> Historical research record. Results retain their stated scope and limits.
> Host names are public aliases. Local evidence and execution records remain private.
> This publication does not revalidate earlier results or approve a model.

research-host-NUIAK completes 36 queued jobs using the existing runner.
These jobs cover 5 matched comparisons, 1 rendering audit, 5 crop audits, and 5 branch audits.
They are not 36 independent experiments.

## Captures

The 5 producers retain 50 frames and 30 endpoint pairs.
Exact decoded-pixel checks find 24 unique pairs: 8 movement, 8 content-change, and 8 repeated-frame pairs.
The matched comparisons intentionally reuse control conditions. All cases belong to 1 related development group.
All producers restore the original recipe and focus.
The batch covers 1 layout and 1 theme. Other layout and theme cells remain unsupported.
No HCF state changes occur.

## Model results

Counts below include the repeated control conditions.
The existing thresholds and original crops remain unchanged.

| Model | Missed movements | False content changes | Content abstentions | Correct repeated frames |
|---|---:|---:|---:|---:|
| FOCUS329 | 10/10 | 1/10 | 0/10 | 10/10 |
| gamma348 | 10/10 | 0/10 | 1/10 | 10/10 |
| movement349 | 10/10 | 0/10 | 1/10 | 10/10 |

The false change and abstentions occur in the centered content case.
No model improves. No training or promotion occurs.
Previous successful model decisions remain unchanged because weights and preprocessing remain unchanged.

## What the measurements establish

- All 5 requested factors change rendered pixels.
- Increasing growth from 1.03 to 1.15 increases changed pixels from 10,588 to 46,787 for movement.
- Adding shadow increases changed pixels from 26,090 to 133,594 for movement.
- Every repeated capture has 0 changed pixels.
- The original detail windows retain essentially 100% of encoded movement-change energy.
- The detail windows retain approximately 55%–58% of content-change energy.

These values do not establish native-effect fidelity or real-app accuracy.
Floating-point rounding produces tiny deviations around 100% retained energy.

## Why this guides the next correction

The whole-frame branch strongly suppresses these movements. The detail correction usually cannot overcome that suppression.
For FOCUS329, corner movement produces contributions of -10.10 and +1.64 before the sigmoid.
Centered movement produces -6.38 and -0.06. Both remain missed movements.
Corner content change produces -14.45 and +8.20.
Centered content change produces -0.03 and +1.97, which crosses the existing positive threshold.
The branch sums match the full output within the checked tolerance.

The next correction should target position-sensitive context and branch balance.
Do not enlarge crops as the first response: current crops retain the measured movement evidence.
Do not lower the threshold: content scores overlap or exceed movement scores.
Use position-balanced, eligible training examples and an equal-budget control.
Keep this inspected native set in development. Test any candidate against all retained previous successes.
Do not claim improved generalization from these related examples alone.

## Verification and limits

The focused suite passes 42 tests.
The offline Swift build passes. Host-authorized Swift tests pass: 173 Swift Testing tests and 14 XCTest tests.
The sandboxed Swift attempt fails on access to compiled Core ML resources. Its log remains preserved.
The first capture attempt fails before screenshots because reload does not expose a requested focus ID.
The corrected sequence waits for fresh geometry, then applies full observed-focus checks after its focus request.
The failed attempt remains preserved. It does not explain the older GENERATION352 timeout retrospectively.

Installed binary hashes identify this runtime. Matching those binaries to a capture-era source revision remains unverified.
The data stays outside training. Model qualification and real-app qualification remain unchanged.

Capture execution takes 80.73 s. All 36 jobs use 130.80 s of worker time.
These durations exclude preparation, tests, and coordinator requests.
The summary records 15.05 min from the first retained preflight to result collection.
The initial tranche estimate is 45–90 min; that measurement excludes earlier context review and later handoff work.

Evidence: `reports/work/GENERATION354/summary.json` and `reports/work/research-queue/jobs/generation354b-*`.
The summary pins every completed result. Raw captures and logs remain local.
TTR's harness reply is stored at coordinator cursor 397 and verified by request ID.
The final findings are stored and read back at cursor 400.
Recipient forwarding and acknowledgment remain separate pending states.
The queue now records 210 complete jobs, 41 blocked jobs, and 4 exhausted attempts.
The background runner remains enabled. This finite batch has no remaining ready jobs.
Blocked entries are not counted as capacity. Completed jobs do not run again automatically.
