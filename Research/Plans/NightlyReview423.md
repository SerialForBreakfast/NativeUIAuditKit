# NIGHTLY423 — research review and queue refill

Date: 2026-10-18. Owner: Maximum-mini-NUIAK.
Scope: 1 nightly-review rehearsal. Standard detection and focus remain primary. HCF remains optional.
No model, threshold, worker module, or runner setting changes.

## What improved

No new replacement model passes qualification in this review.
The retained conservative proposal policy recovers 4 Standard selections without lost successes or new wrong selections on inspected development cases.
This is a policy result, not a qualified model release. Independent groups and the TTR artwork comparison remain required.
Evidence: [B405-219](../Experiments/results/B405-219.json).

## What the crop and detector work establishes

| Work | Verified state | Decision |
| --- | --- | --- |
| OFFSET421 jitter fit | Attempt 1 completes 30 epochs in 1415 s. Output hashes pass verification. | Wait for matched scoring before choosing another fit. |
| OFFSET421 measured-offset comparison | Preparation completes. Candidate scoring remains pending at the review cutoff. | Keep the approved comparison unchanged. |
| DETECTOR422 baseline | All 16 baseline jobs complete. Button, row, and tab focus output hashes pass verification. | Compare the candidate against these exact outputs. |
| DETECTOR422-v2 candidate | Candidate training and dependent comparisons remain pending. | Do not claim detector improvement from annotation readiness. |
| Detector annotations | 21 unique training images span 5 source groups but only 3 layouts. | Report layout support. Do not claim broad generalization. |

The crop comparison changes the same 231 training rows in both treatments.
It preserves existing jitter, labels, exposure, development groups, and original crops.
The detector targets 3 control classes. It does not replace the general UI detector.
Resident detector validation uses training data. Those metrics do not estimate held-out accuracy.
See [the canonical comparison plan](Offset421AndRefinementReview.md).

## Regressions and rejected directions

- Lower native exposure improves tabs but loses row and tall-control successes. Keep that candidate rejected.
- A global tvOS confidence reduction adds wrong no-focus selections. Keep Standard thresholds unchanged.
- iOS cross-class suppression removes 17 unmatched boxes but loses 41 labeled matches and gains none. Reject it.
- Higher iOS resolution gains 60 matches but loses 322. Do not adopt it from these results.

The iOS confidence comparison recovers 21 labeled controls without losses.
Its unmatched predictions increase from 197 to 241. These extra boxes lack sufficient review for a precision claim.
Evidence: [B405-214](../Experiments/results/B405-214.json), [B405-229](../Experiments/results/B405-229.json), and [CurrentState](../CurrentState.md).

## Useful work added

The review adds 2 investigation records and 12 approved jobs through existing T42.
Each job uses retained predictions, 800 s, and 100 MB. No capture, model inference, or training repeats.

| Record | Test | What it decides |
| --- | --- | --- |
| B405-230 | Group the matched iOS confidence comparison by screen region across 6 retained sets. | Which regions need annotation review before a threshold change can be considered. |
| B405-231 | Group the same comparison by control size across those sets. | Whether recovery reaches small controls or only larger controls. |

These jobs change report grouping, not predictions. They are diagnostic analyses, not 12 independent scientific replications.
Use supported-case denominators and case links. Do not sum related frames as independent groups.
Do not promote a threshold from these reports. Review unmatched boxes before estimating precision.

Registration reports no blocked arms. The catalog validates 131 plans.
The detached runner owns execution. This review does not dispatch jobs directly or wait for their completion.

## Next priorities

1. Qualify the delivered TTR repair on Maximum-mini. This unblocks independent native captures and dependent policy tests.
2. Finish the already approved crop and detector comparisons. Separate missing boxes, box geometry, classification, and abstention.
3. Use B405-230 and B405-231 to select a bounded iOS annotation batch.
4. Prepare a new correction only when the matched evidence identifies its target and preserves previous successes.

Sillycon-TTR supplies source revision `4b2f49c0b1c62f07090cd1acec47bea3bfa824ac` through forwarded message 854.
Its message reports retained-pair checks and host regressions. These are peer claims until Maximum-mini verifies the consumer.
Maximum-mini-NUIAK must verify the revision, helper, retained observations 16/17, and native restoration before capture successors.
Keep the recovery guard until that receipt passes. Do not repeat a capability inquiry or retry the old route.
Messages 852 and 854 are read and acknowledged. Response 855 is stored; forwarding is not verified.
No manual setting change is currently required from the maintainer.

## Efficiency and effectiveness review

The review uses 1 existing template and adds 0 adapters, dependencies, or training runs.
It reuses predictions from 6 completed comparisons. This avoids repeated image decoding and model inference.
The first registration rejects identical comparison descriptions. Distinct region and size descriptions pass the existing validator.
The review also corrects the stale B405-196 blocker: preparation exists; matched scoring and interpretation remain pending.

The initial queue snapshot shows 19 ready jobs and 112 s of estimated ready work.
That duration excludes waiting training and dependent work. It is not an overnight capacity estimate.
Adding 12 fast analyses improves breadth but does not solve long-duration starvation.
The final snapshot reports 30 ready jobs and 145 s of estimated ready work, with no jobs awaiting approval.
The snapshot still reports 153 blocked jobs. This includes historical attempts and must not be interpreted as 153 unresolved scientific questions.
Do not repeat successful experiments or create arbitrary sweeps to inflate that duration.

The receipt inventory covers the 24 h ending 2026-10-18 16:58:20 UTC.
Completion time uses attempt start plus recorded wall time, not file modification time.
It finds 310 completed attempts and 43 failed attempts. These are execution counts, not improvements or independent trials.
The failures include 30 obsolete comparison reports, 3 replaced crop preparations, 5 earlier detector checks, and 5 failed captures.
Keep original failures visible in history. Do not count a repaired predecessor as a new current blocker.

The review does not establish a measured efficiency gain. Total review time and token use lack a complete instrumented baseline.
The next 3 reviews should record preparation time, ready duration by track, resolved questions, and manual interventions.
Add a compact receipt index and explicit successor reconciliation as engineering tasks, not new research frameworks.
Cache the inventory between reviews. Read only new receipts and changed dependencies.
The nightly review should end after publication and admission. It should not remain active while jobs run.

## Validation

- The catalog validator passes all 131 plans.
- Both new records register and approve all 12 jobs without blocked arms.
- Selected completed crop and detector outputs pass content-hash verification.
- The task table regenerates through the existing pipeline.
- No executable source changes occur. No Swift rebuild is required for these planning and specification edits.

Model acceptance remains false. Standard behavior and previous artifacts remain unchanged.
