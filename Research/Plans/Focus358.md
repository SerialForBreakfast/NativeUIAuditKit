# FOCUS358 and HCF358 — useful duration tests and the HCF graph

> Historical research record. Results retain their stated scope and limits.
> Host names are public aliases. Local evidence and execution records remain private.
> This publication does not revalidate earlier results or approve a model.

Owner: research-host-NUIAK. The background runner owns execution.

## Findings and selected work

FOCUS355 position and branch candidates lose 20 and 23 previous successes. Neither improves native movement detection.
HCF358 checks their training histories. The control and position loss still improve at epoch 10.
The branch loss reaches its minimum at epoch 8, then worsens. Do not extend that arm.

FOCUS358 tests 30 epochs for the control and position arms.
Both start from the original FOCUS329 checkpoint with seed 42 and unchanged membership.
Preserve the 1,820 original views and the existing authored auxiliary data.
Keep the original crops, thresholds, loss weights, and position transform.
Only the epoch budget changes against each retained 10-epoch arm.
These are fresh runs, not exact continuations. Existing trainers do not save full resume state.

Each run permits 1,800 s and 2 GiB. The runner executes serially.
Expected training time is approximately 15–22 min per arm, based on retained preparation and epoch timings.
The full batch includes 2 training jobs, 48 comparisons, 6 partial reports, and 2 final reports.
Each comparison retains the existing baseline and previous-success checks.
The final report requires 24 comparisons per arm, native movement gains, and zero lost previous successes.
No automatic model promotion occurs. Related cases do not become independent trials.
The last report compares both complete 30-epoch outcomes with their retained 10-epoch outcomes.

## HCF diagnostics and graph

Six HCF358 diagnostics measure effects at 3 resolutions, scalar score overlap, training trends, and storage needs.
They reuse pinned inputs. They do not change labels, thresholds, models, or data roles.

The 22 blocked entries cover these required stages:

- Qualify a visible native HCF family.
- Qualify producer offload and storage limits.
- Freeze connected groups and data roles.
- Verify full training resume.
- Qualify worker-host-NUIAK storage and throughput.
- Compare pinned rules and existing models.
- Generate validated stages of 1,000, 5,000, 20,000, and 50,000 HCF frames.
- Train both detector and crop classifier at each eligible stage.
- Repeat useful configurations with 3 total seeds.
- Run the frozen final audit.
- Test Core ML conversion and runtime behavior.
- Deliver optional shadow candidates to TTR.

Blocked entries name the missing evidence and owner. They cannot run or produce invented scores.
Create immutable executable successors when their inputs qualify. Do not remove requirements from existing specifications.
Do not count these entries as ready execution time.

## Storage finding

The largest retained PNG uses 6,202,862 bytes.
At this sample size, 50,000 HCF frames and matched Standard frames need about 578 GiB for images alone.
The 20,000-frame stage needs about 231 GiB before labels, derivatives, and checkpoints.
These are estimates from a small sample, not guaranteed upper bounds.
The 250 GiB study limit therefore needs measured storage preparation before either large stage.
Test lossless compression, exact-payload reuse, and staged retention before proposing lossy encoding or a larger budget.
Preserve distinct capture events even when payloads match.

## Failed-job review

The 7 exhausted attempts are process, input, or capture failures. None reports an outer queue timeout.
Three interpreter failures have completed replacements. The progress-file race also has a completed replacement.
Longer limits do not fix these failures. Preserve them without automatic retry.
Use measured learning curves, unresolved questions, and regression checks to select longer training tests.

## Verification and handoff

The runner completes all 6 HCF358 diagnostics. It accepts all 58 FOCUS358 jobs through live additions.
The control starts. The position arm waits behind it. Comparisons start only after their required outputs pass verification.
Focused checks pass: 124 workflow checks, 15 study/model checks, and 2 duration-report checks.
Some suites reuse inherited checks; these counts are not independent scientific experiments.
The native offline Swift build passes. All 14 XCTest tests and 173 Swift Testing tests pass.
The first sandboxed Swift attempt cannot write its default module cache. The scoped retry uses project-local module caches.
No signing, service, certificate, or production model changes occur.
The new TTR clarification is stored at cursor 435. Its forwarding remains unconfirmed at handoff.
The earlier HCF357 requests are confirmed delivered; do not confuse them with this later clarification.
The background runner remains responsible for execution. No chat monitoring loop is started.
Preparation takes approximately 30 min against the 30–60 min estimate. Background training time remains separate.
