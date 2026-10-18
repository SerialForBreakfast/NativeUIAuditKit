# WORKFLOW394 — compare workflow preparation without delaying HCF

Owner: Maximum-mini-NUIAK.
Decision: [ADR-0029](../ADR-0029-Workflow-Tools-Versus-Templates.md).
Status: The approved isolated DVC comparison passes. See [measured results](../Workflow394Results.md).
This work is independent of HCF389. It does not block TEMPLATE393.

## One representative workflow

Use preparation → scoring → report on 16 retained development examples.
Select the first 16 eligible case IDs in sorted order from one verified manifest.
Pin that membership, labels, model, preprocessing, and adapter source before either arm runs.
Exclude final-audit data. Do not create new training data or run training.
Use the same underlying Python functions in both arms.

| Stage | Current approach | DVC alternative | Same required output |
| --- | --- | --- | --- |
| Prepare | TEMPLATE393 wrapper invokes existing preparation | DVC stage invokes the same preparation function | Membership and prepared-input hashes |
| Score | Approved queue adapter scores pinned inputs | DVC stage invokes the same scorer inside a bounded queue job | Case predictions and actual model/input hashes |
| Report | Existing comparison code reads verified predictions | DVC stage invokes the same reporting function | Counts, gains/losses, limitations, and decision |

The source-level mapping shows DVC can describe these dependencies and outputs.
Neither mapping proves the new template command exists or that DVC executes successfully here.
Do not replace this real scoring test with assigned accuracy values or synthetic timings.

## Execution contract after prerequisites pass

- Use an isolated workspace under project-local ignored work on verified USB storage.
- Install only an approved pinned DVC release into a separate environment; do not change training environments.
- Use local files, no remote storage, no new services, and no credentials.
- Run serially under the existing queue with 800 s and 100 MB per diagnostic job.
- Reserve at most 2 GiB temporary space for the complete pilot, including duplicated cached inputs.
- Run 3 matched repetitions per arm; alternate which arm runs first.
- Measure first-run and verified-reuse behavior separately. Do not claim a cold OS cache without controlling it.
- Preserve failed attempts. Use explicit replacement jobs, not automatic retries.

## Failure and recovery cases

1. Remove one required input from the isolated copy. Both arms must name the missing input and produce no accepted report.
2. Change one input byte. Both arms must invalidate or reject affected work rather than reuse stale evidence.
3. Stop after preparation. Restart must preserve verified preparation and finish downstream work correctly.
4. Repeat an identical request. The outer queue must avoid duplicate execution; record whether the inner tool reuses its outputs.
5. Fail scoring deliberately. Neither report may claim model acceptance or conceal the failed stage.

These failures affect test copies only. Do not mutate original retained data or active jobs.

## Measurements and decision

Record preparation wall time and manual steps for each arm.
Count adapter code, configuration, and domain-check code separately; do not hide relocated complexity.
Record setup, scoring, reporting, recovery time, peak memory, disk use, and operator actions.
Require identical membership and decisions. Use existing declared score tolerances where numerical identity is not guaranteed.
Report actual values and ranges. Leave unmeasured values unavailable.

Recommend adoption only when all correctness, ownership, recovery, and data boundaries pass.
Also require either 30% less experiment-specific code or 30% fewer manual preparation steps across 2 descriptions.
The second description changes only a supported setting or eligible input set; it adds no new adapter.
These are proposed engineering thresholds, not claims from research papers.
Report migration cost and new dependencies alongside gains. The maintainer reviews adoption separately.
If no meaningful reduction appears, retain templates and close the alternative without expanding the study.

## Tasks and blockers

Tasks.md owns live status. The following steps define acceptance, not another task queue.

- W394-01: Review sources and existing code. Complete with ADR-0029 and this mapping.
- W394-02: Complete. DVC 3.67.1 runs in the approved isolated USB environment; dependency checks pass.
- W394-03: Complete. Both arms use the same functions, frozen manifest, and model.
- W394-04: Complete for the bounded pilot. Matched runs, input failures, duplicate requests, and caller restart pass.
- W394-05: Measurements are published. Keep templates; maintenance savings and comparable authoring costs remain unmeasured.

The source-review tranche made no runtime changes. The subsequent approved pilot runs in separate test queues.
No framework adoption or active queue change occurs. Interrupted training resume remains outside this comparison.
