# HCF402 — Native coverage and simpler batch preparation

Owner: research-host-NUIAK. Date: 2026-10-14.

## Outcome

Test the frozen HCF401 mapping on new native development groups.
Keep Standard models, production crops, thresholds, and retained successes unchanged.
HCF remains optional. No job grants navigation authority.

## Why preparation takes too long

The queue already executes fixed jobs. Experiment-specific preparation scripts repeatedly bind inputs, dependencies, hashes, and approvals.
Several adapters also assume 4 focused controls. That assumption blocks valid no-focus experiments before capture begins.
Template availability does not mean every data shape is supported.

Use `scripts/experiment_batch402.py` to register descriptions from one batch file.
The command resolves file pins, verified completed outputs, and dependencies between jobs.
The command validates the whole batch before registration. Registration never starts a runner.
Approval remains an explicit list of job IDs. Existing specifications remain immutable.
If a source or input changes, use an explicit successor ID. Do not rewrite submitted jobs.

## Native comparison

Capture 18 frames from 3 cases in 2 related scene groups.
Use paired OS Standard and HCF settings. Restore the original setting and Fixture state.
The cases cover corner controls, a static decorative square, and an observed no-focus scene.
The square is a text glyph. It does not represent every decorative artwork border.
Keep the no-focus scene with its related decorated scene in the same group.
All new cases are development data. Do not call them an untouched audit.

The producer uses the existing native capture lifecycle and storage checks.
Require verified UIKit observations, matching capture brackets, exact image hashes, and successful restoration.
An absent border is not a no-focus label.
For no-focus cases, require verified null observed focus and no focused control flags.
Keep the measured control inventory complete. A requested null focus alone cannot qualify the label.
If that observation fails, retain the attempt and report the exact failed check.

The comparison uses the existing pinned TTR ring executable and frozen HCF401 offsets.
Report original and mapped overlap against native body bounds.
Report no-focus border proposals separately. A proposal is not a focus selection.
Reject a changed image size. The fixed pixel offsets apply only to 3840 × 2160 captures.
Keep full crop selection qualification separate until new evidence passes intake.

## Independent work

Produce 1 class-specific Standard report from retained Run 013 evaluation evidence.
Report all 13 supported classes, missed controls, false detections, and unavailable classes.
Do not claim per-case preservation from aggregate metrics.
Keep the existing 41-class release gate closed.

Qualify batch registration through the actual queue in isolated directories.
Test successful execution, expected failure, duplicate IDs, cycles, unsafe paths, changed inputs, and restart without duplicate execution.
Measure authoring and registration separately from worker time. Do not claim a speedup before a matched timing comparison.

## Authoring procedure

1. Choose an existing adapter and name the decision.
2. Name fixed inputs, the changed variable, and the required data role.
3. Use `file` references for local inputs.
4. Use `job`, `attempt`, and `output` for verified completed results.
5. Use `job` and `output` for dependencies in the batch.
6. Preview the batch before registration.
7. Approve only the reviewed job IDs.
8. Let the detached runner execute the jobs.
9. Review results as one batch and prepare the next decision.

Do not create a custom preparation script when a description can express the job.
If an adapter is missing, record a separate implementation task with positive and negative acceptance tests.
Do not label that experiment ready until the adapter and inputs pass checks.

## Prepared factor batch

Ten controlled captures each produce 8 frames. Each capture has a separate fixed-map report.
The jobs depend on the corrected focused pilot. A failed producer blocks its own report.
Related variants keep the original scene group. They do not count as independent audit groups.

| Factor | Question answered |
| --- | --- |
| 72-point controls | Does the fixed inset remove too much of a small body? |
| 180-point controls | Does the inset transfer to larger bodies? |
| Wide controls | Does aspect ratio change horizontal alignment? |
| Tall controls | Does aspect ratio change vertical alignment? |
| Bright background | Does reduced outer contrast create extra proposals? |
| Near-black background | Does stronger outer contrast improve proposal geometry? |
| 24-point edge clearance | Does proximity to the viewport change the measured border? |
| Close neighbors | Do adjacent effects merge into competing proposals? |
| Smaller square decoration | Does decoration size affect false proposals? |
| Diamond decoration | Does another closed shape confuse the ring rule? |

These are geometry diagnostics, not new trained models. Reuse their captures for later compatible crop comparisons.
The plan contains 25 successor steps, including 20 factor steps. Dependencies are not ready work until their requirements pass.
Capture approval also checks target ownership. Registration during an active capture does not bypass that check.
This exposes another preparation bottleneck: the runner can start the first capture before later capture approvals finish.
The batch command now holds the existing dispatch lock during approval. It refuses a busy runner without waiting or stopping it.
Registration remains resumable. Partial approvals remain recorded if a later approval fails.
This prevents dispatch during admission; it is not an all-or-nothing approval transaction.

## Recorded implementation findings

The first capture rejects an oversized font and mismatched item count. It preserves 4 frames and restores the target.
The next capture exposes the old assumption that all measured elements are focusable. Its cleanup also passes.
The correction permits declared text or artwork decorations while requiring all planned focusable controls.
It retains verified observed focus, complete control geometry, fresh observations, and matching capture brackets.
Failed captures now retain the failure observation. Settling errors include the failed check.
The corrected focused pilot completes 16 frames in 110.8 s.
The failed attempts remain immutable. Explicit successors replace their dependent comparisons.
The no-focus pilot also returns a verified reference-focus observation with no focused control flags.
Swift JSON omits its optional focus IDs. The current capture parser incorrectly requires those keys.
The failure observation preserves this evidence; it does not provide a completed paired capture.
Ten compatibility and batch tests pass for omitted IDs and explicit null IDs.
Unknown native focus and conflicting IDs still fail.
The queue rejects the proposed compatibility wrapper because its capture adapter is not on the permitted list.
The final fix uses the existing permitted capture adapter. No new capture entrypoint bypasses that list.
The runner reaches an idle boundary before the decoder changes. Tests pass before unstarted approvals are renewed.
The R4 no-focus producer and its report are registered. The background runner owns execution.
The native mapping report also needs both rectangle encodings: a 4-value array and a named object.
Positive and negative checks cover both encodings and reject invalid values.
Explicit report successors reuse captures. They do not repeat training or successful capture work.

The first native pilot returns no ring proposals on 8 HCF frames.
Its paired pixel report measures 96,028–100,344 changed pixels per pair.
This rejects exact pixel identity. It does not prove that every changed pixel comes from HCF.
The next diagnosis concerns proposal coverage and native effects, not another inset fit.
The small-control and wide-control captures report unavailable body geometry. Their dependent reports remain blocked.
Do not replace unavailable native geometry with requested bounds.

The default Swift test host stalls. The native serial path passes 14 XCTest and 174 Swift Testing checks.
The final focused Python suite passes 28 checks. No Standard weights or production thresholds change.

capture-host-TTR acknowledges the consumer request and human approval but has not accepted execution.
Its current priority is Autonav. Consumer verification remains unavailable, not failed.

## Handoff

At 19:05 UTC, the runner executes the neighbor-spacing capture and 7 useful jobs pass readiness checks.
The corrected no-focus capture remains pending. New factor reports reuse each producer's outputs.
Small and wide controls remain blocked by unavailable native body geometry.
Superseded report approvals are revoked. Their failed attempts remain preserved.
Thirty-four final Python checks pass. The offline native Swift check passes 14 XCTest and 174 Swift Testing checks.
The work takes about 48 min. The initial estimate is 30–45 min; the revised estimate adds 10 min for parser and report repairs.
This batch provides short diagnostic work, not 24 h of ready execution.
Next, use proposal coverage to select a correction. Do not refit offsets where the rule produces no candidates.
Keep consumer verification and Standard case-linked diagnosis as independent work.

## Limits and remaining requirements

Diagnostics use 800 s and 100 MB per job. The native pilot uses 18 frames and a 100 MB capture limit.
The existing bulk storage reserve and cleanup checks remain active.
capture-host-TTR consumer scores remain a separate dependency. Approval already covers 8 crops from 2 frames.
Public model downloads remain blocked by an unpublished reviewed release and the missing TTR download backend.
Neither issue blocks local native diagnostics.
