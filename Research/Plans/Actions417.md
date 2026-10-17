# ACTIONS417 — close the HCF jitter comparison and remove its bottlenecks

Date: 2026-10-16. Plan: approved maintainer plan ACTIONS417.

## Completion condition

Establish whether jitter improves proposal-based HCF selection, preserve Standard behavior, and identify the next delivery blocker with measured evidence.
Also: approval proceeds during execution, qualification catches malformed reports before expensive work, every confirmed result has a next action or a closure, and no experiment loses its identity or authorization guarantees.

## Waiting causes, 2026-10-14 12:00 to 2026-10-16

Measured from spec registration times, approval events, attempt start times, result wall times, and confirmation times for 280 jobs registered in the window.

| Measure | Value |
| --- | --- |
| Window | 51.4 h |
| Runner busy (union of attempt intervals) | 2.8 h (5.4 %) |
| Attempts | 235, of which 8 failed |
| Failed-attempt time | 0.85 h |
| Approval wait after registration | median 0.4 min, 90th percentile 22.3 min |
| Dispatch wait after approval | median 2.2 min, 90th percentile 76.1 min |
| Result review wait (last job to confirmation, 47 records) | median 2.0 min, maximum 4.5 h |
| Registered jobs not started at measurement | 45 |

Failure causes: `process_failed` 3, `approval_or_code_changed_during_run` 2, `training_history_epoch_mismatch` 2, `evidence_not_read` 1.

Interpretation:

- Approval and review are not the main delay. Their medians are minutes.
- The dispatch tail (76 min at the 90th percentile) comes from short jobs queued behind training runs and the dispatch lock during approval.
- For most of the window the queue had no ready work. Preparation of templates and plans, not compute, limits throughput.
- Failed attempts used 30 % of busy time. Code-change and report-schema failures caused 4 of the 8 failures, all in long training runs.
- Human-review time cannot be separated from these timestamps. Decisions that are still open (quotas, CALIBRATION102, label reviews) have no recorded start time. The decision register in the plan's "Later" section supplies it.

Limits: spec modification time stands in for registration time. Records answered by reuse have no jobs and are excluded.

## Step 2 — approval during execution and named post-run checks

Applied at an idle runner boundary on 2026-10-16. The dashboard server was restarted to load the new queue code.

- `experiment_batch402.register_batch` no longer holds the dispatch lock for approval. Approval serializes on `approval.lock` with a bounded wait of 30 s. The runner rechecks the exact approval at dispatch.
- `research_queue.host_lock` takes an optional bounded wait. `research_queue.save` reports a lost registration race as `output_collision`, not a raw `FileExistsError`.
- `research_approval.post_run_authorization` replaces the post-run `is_approved` call. It returns a named reason:
  - `approval_revoked_during_run` or `approval_changed_during_run` (only this job's record matters);
  - `code_changed_during_run:<path>` (every approved pin stays strict, so adapter dependencies are not narrowed);
  - `closure_record_missing` or `closure_record_invalid`.
- `research_trust.check_training_report` holds the training report checks, so schema tests can call it without a run.

Tests: `scripts/test_actions417.py` (14 tests) covers:

- concurrent approvals and approval while the runner holds its locks;
- no dispatch lock in batch approval;
- concurrent registration of 1 ID and an interrupted approval;
- revocation before dispatch, and a new approval at the next boundary;
- revocation during a run, an unrelated approval during a run, a named changed file, and a missing or malformed closure;
- the T06 and T49 report schemas, and invalid `repeat` values.

347 tests across the queue, trust, batch, pipeline, dashboard, template, and training suites pass. 2 exceptions:

- `test_research_queue.test_summary_reports_each_job` fails once under full-suite load. It passes 3 of 3 times when run alone.
- The batch test for the old busy-dispatch refusal now asserts the new behavior.

The dashboard empty-state note moved out of the job table, which fixed a failing description test.

Not covered: T38 has no schema test in this step. Artifact templates (T41–T43, T47) already run `check_evidence` in their isolated queue tests.

## Step 3 — exposure control and the matched-exposure control

- `train_native_hcf` takes `repeat` (1–16). It is applied after deduplication: each epoch draws a permutation of `repeat × unique rows` and maps it back to the unique rows.
- The function returns an `exposure` record:
  - unique train images, `repeat`, samples presented, and optimizer updates;
  - batch size and final-batch handling;
  - learning-rate schedule;
  - class balance;
  - initialization hash, selection, and epochs run.
- T06 passes `repeat` from its configuration. If the key is absent, `repeat` is 1.
- **Byte-identity check.** On a fixed set of 14 real crops, the original trainer is deterministic (2 identical runs). The patched trainer with `repeat=1` reproduces the same `final.pt` and `history.json` hashes. With `repeat=2` it presents 600 samples in 60 updates, against 300 in 30.
- **Matched-exposure control (B405-138).** Job `actions417-train-matched` uses the JITTER413 control recipe with `repeat=5`: 615 unique crops presented 5 times, 3,075 samples per epoch, the same as `jitter413-train-jitter-r2`.
- **Scoring (B405-139).** The same 29 T41 arms as B405-132 and B405-133.

## Step 4 scope

B405-140 scores the jitter and matched-exposure models on the same raw and mapped ring proposals, through T41 `none` arms with a candidate model. Each row also records the retained model's outcome (`pinnedModelOutcome`), so recovered cases and lost previous successes come from the same frames.

Detector and combined detector-first proposals are not available for these 74 HCF402 frames. They need detector inference on these frames first, so they are a named gap, not substituted.

## Results — 2026-10-16

### Step 3: jitter, not exposure, explains the box tolerance (B405-138, B405-139)

All 3 models start from the same initialization (seed 371) and train for 30 epochs at batch 16, with fixed-last selection. All are scored on the same 74 retained development frames with the same 29 T41 box changes.

| Model | Samples per epoch | Updates | HCF correct, unchanged box | Arm losses within 2 px | Arm losses, all 28 changes |
| --- | ---: | ---: | ---: | ---: | ---: |
| Unmatched control (`jitter413-train-control`) | 615 | 1,170 | 35/36 | 58 | 327 |
| Matched-exposure control (`actions417-train-matched`) | 3,075 | 5,790 | 33/36 | 172 | 622 |
| Jitter (`jitter413-train-jitter-r2`) | 3,075 | 5,790 | 36/36 | 0 | 21 (only at +16 px growth) |

All 3 keep Standard at 36/36 on the unchanged box. More exposure without jitter makes the model more fragile, so jitter, not exposure, explains the tolerance.
The arms repeat tests on the same frames, so arm losses are correlated, not independent screens. The matched control trains in 1,221 s, against 529 s for jitter with the same sample count. The cause of that time difference was not measured.

### Step 4: proposal-based selection (B405-140)

Identical raw and mapped ring proposals on the 74 frames: 36 focused HCF frames, 1 no-focus HCF frame, and 37 Standard frames.

| Model | Proposal source | Correct | Recovered against retained | Lost previous successes | Wrong |
| --- | --- | ---: | ---: | ---: | ---: |
| Retained `hcf375c-70` | raw | 3 | — | — | 0 |
| Retained `hcf375c-70` | mapped | 5 | — | — | 0 |
| Jitter | raw | 8 | 5 | 0 | 0 |
| Jitter | mapped | 8 | 3 | 0 | 0 |
| Matched-exposure control | raw | 2 | 1 | 2 | 0 |
| Matched-exposure control | mapped | 4 | 1 | 2 | 0 |

28 of the 36 focused HCF frames get no proposal. Jitter is correct on all 8 frames that have one. The no-focus frame stays a correct abstention.
Standard is unchanged: ring proposals produce no Standard candidates.
Detector and combined detector-first proposals stay a named gap for these frames.

### Decision

- Jitter advances for HCF crop scoring. The crop classifier is no longer the limit on supplied proposals.
- **Proposal generation is the delivery blocker:** 28 of 36 focused HCF frames have no proposal. B405-119 shows that a relaxed kernel adds none, so measure the native ring pixels on the missed frames next.
- Step 5 (seeds 372 and 373 for jitter and the matched control) is justified to measure repeatability. It needs 4 more training runs, which exceeds the 3-run tranche, so it waits for maintainer approval.
- Model acceptance stays false. These are inspected development frames, not an independent audit.

### Time

- Agent work: about 5.5 h for Steps 1–4, against the 6–7.5 h estimate.
- Runner work: 1,221 s of training and 33 scoring jobs at a median of 80 s (fresh-model scoring is slower than cached scoring), about 1 h in total.

## Step 5 — paired seeds (approved by the user, 2026-10-16)

4 training runs (seeds 372 and 373 for each method) and 124 scoring jobs complete. Every run has the same exposure: 92,250 samples and 5,790 updates.

| Model | Train time (s) | Unchanged box, HCF/Standard | Arm losses within 2 px | Raw proposals: correct, lost | Mapped proposals: correct, lost |
| --- | ---: | --- | ---: | --- | --- |
| Jitter 371 | 529 | 36/36 | 0 | 8, 0 | 8, 0 |
| Jitter 372 | 1,596 | 36/36 | 0 | 8, 0 | 8, 0 |
| Jitter 373 | 516 | 36/36 | 0 | 1, 3 | 8, 0 |
| Matched 371 | 1,221 | 33/36 | 172 | 2, 2 | 4, 2 |
| Matched 372 | 511 | 36/36 | 120 | 0, 3 | 8, 0 |
| Matched 373 | 512 | 36/36 | 10 | 4, 2 | 8, 0 |

The proposal columns compare each model with the retained `hcf375c-70` model on 36 focused HCF frames, 8 of which have a proposal. No model makes a wrong selection or loses a Standard success.

### Revised decision

- **Jitter's box tolerance is repeatable:** 0 losses within 2 px at all 3 seeds. The matched control varies from 172 to 10. Use jitter for the next HCF crop candidate.
- **The proposal advantage at seed 371 does not repeat.** On mapped proposals, 5 of the 6 models reach 8/8, so the result is not specific to jitter. On raw proposals, both methods vary by seed. B405-141 and B405-146 are confirmed contradicted, and the B405-140 conclusion is provisional.
- **Prefer mapped proposals over raw outer-ring proposals.** Raw proposals make selection seed-sensitive.
- **Proposal recall stays the delivery blocker:** 28 of 36 focused HCF frames have no proposal at any seed.
- Training times vary from 511 to 1,596 s for identical exposure. Runner load is a possible cause; it was not measured.

## Proposal repair, step 1: native ring pixels on missed frames (B405-147, T52)

T52 (`scripts/ring_pixels420.py`) ports the outer-ring-v2 component, geometry, side-support, and side-contrast gates. It applies them to the bright component around each known focused body, on the kernel's 960 px grayscale analysis image. Each focused HCF frame is measured together with its Standard pair.

| Measure | Result |
| --- | --- |
| Self-check: frames with a kernel proposal that pass the ported gates | 8 of 8 |
| Missed frames with a bright ring next to the body (peak 255) | 28 of 28 |
| Missed frames that fail side support | 26 |
| Missed frames that pass the port at support 0.652 (just above 0.65) | 2 |
| Failing sides on missed frames | left 26, right 26, top 2 |
| Median side support, missed frames (left / right / top / bottom) | 0.46 / 0.52 / 0.81 / 0.89 |
| Median side support, frames with a proposal | 1.00 / 1.00 / 1.00 / 0.98 |
| Standard frames that pass the ring gates | 0 of 36 |

**Finding.** The HCF ring is present and bright on every missed frame. The kernel rejects it because its short vertical sides fail side support.

**Likely cause (hypothesis).** The missed controls form ring components of about 58 × 37 analysis pixels. The kernel samples the middle 60% of each side with a peak band of 3 px. On these short rounded sides, the corner arcs fill much of the sampled range.

The 2 frames at support 0.652 probably fall below 0.65 in the real kernel, because its grayscale drawing differs slightly.

**Next action (B405-148).** Test 1 predefined short-side sampling setting in T25. The test must also check Standard and no-focus frames for new proposals, and the 8 current passes for losses. If it recovers proposals safely, score the jitter crop model on them.

## Proposal repair, step 2: short-side sampling (B405-148, B405-149)

`short-side-v1` is a T25 kernel setting. For sides shorter than 48 analysis px, it samples the middle third instead of the middle 60%. It changes 2 source lines, and every gate stays the same.

| Check | Frozen kernel | short-side-v1 |
| --- | ---: | ---: |
| HCF398 synthetic frames with candidates | 52 of 264 | 52 of 264 (14,446 rejected components, identical) |
| Focused HCF frames with a proposal, 9 HCF402 captures | 8 of 36 | 8 of 36 |
| Recovered missed frames | — | 0 of 28 |
| Lost frozen proposals | — | 0 (all 8 keep raw IoU >= 0.5) |
| Standard frames with a proposal | 0 of 36 | 0 of 36 |
| No-focus frames with a proposal | 0 of 2 | 0 of 2 |

B405-148 is contradicted, and B405-149 (the build and synthetic regression) is supported.

**Diagnosis with a debug build.** A local debug copy of the frozen kernel prints each component's side values. On missed frame `hcf402-case-0-hcf-item-1-0`, it sees the same ring component as T52 (704, 70, 58 × 37), with different side support:

| Side | Real kernel | T52 port |
| --- | ---: | ---: |
| Top | 0.83 | 0.92 |
| Bottom | 0.00 | 0.67 |
| Left | 0.00 | 0.35 |
| Right | 0.43 | 0.61 |

On found frame `hcf402-large-controls-hcf-item-0-0`, the real kernel sees 1.0 on all 4 sides.

**Corrected interpretation of B405-147.** The kernel draws each 4K frame into a 960 px buffer with low-quality interpolation. The thin HCF ring line then disappears completely on some sides of small controls. The T52 port uses bilinear drawing and keeps part of that line, so it overstates side support on these frames.

The earlier corner-geometry hypothesis is not supported. The T52 self-check passed only on frames where the ring is thick enough to survive both drawings.

**Next action (B405-150).** Test 1 kernel setting that draws with high-quality interpolation, with all gates unchanged, against the same frozen arms. If that fails, test a higher analysis resolution. T52 needs a CoreGraphics-faithful drawing before its per-side values can guide repairs on thin rings.

## Proposal repair, step 3: high-quality drawing (B405-150, B405-151)

`interpolation-high-v1` draws the 960 px analysis buffer with high-quality interpolation. It changes 2 source lines, and every gate stays the same.

| Check | Frozen kernel | interpolation-high-v1 |
| --- | ---: | ---: |
| HCF398 synthetic frames with candidates | 52 of 264 | 51 of 264 (rejected components 14,446 to 14,943) |
| Focused HCF frames with a proposal | 8 of 36 | 8 of 36 |
| Recovered missed frames | — | 0 of 28 |
| Lost frozen proposals | — | 0 |
| Standard and no-focus frames with a proposal | 0 | 0 |

Both records are confirmed contradicted. B405-151 loses 1 synthetic frame.

The debug build on missed frame `hcf402-case-0-hcf-item-1-0` shows partial recovery:

| Side | Low-quality drawing | High-quality drawing |
| --- | ---: | ---: |
| Top | 0.83 | 0.83 |
| Bottom | 0.00 | 0.78 |
| Left | 0.00 | 0.39 |
| Right | 0.43 | 0.48 |

High-quality drawing returns the horizontal sides, but the short vertical sides stay below the 0.65 gate.
Each change alone fails, because each addresses only part of the problem.

**Next action (B405-152).** Test the conjunction of the 2 specified settings, with no new parameters. The acceptance checks are the same, plus 0 synthetic losses. If it fails, test a higher analysis resolution.

## Proposal repair, step 4: combined drawing and sampling (B405-152, B405-153)

`interpolation-high-short-side-v1` applies exactly the 2 changes of `interpolation-high-v1` and `short-side-v1`.
It changes 3 source lines, including the version string. Every gate stays the same.
A test in `scripts/test_kernel_settings119.py` checks that the combined changes equal the 2 single settings.

| Check | Frozen kernel | Combined setting |
| --- | ---: | ---: |
| HCF398 synthetic frames with candidates | 52 of 264 | 56 of 264 (5 gained, 1 lost) |
| Focused HCF frames with a proposal | 8 of 36 | 19 of 36 |
| Recovered missed frames | — | 11 of 28 |
| Lost frozen proposals | — | 0 |
| Standard and no-focus frames with a proposal | 0 | 0 |

Recovered frames per capture:

- dark-background: 4.
- focused-r3: 3.
- neighbor-spacing: 2.
- small-decoration: 1.
- diamond-decoration: 1.
- edge-clearance, large-controls, and tall-controls: 0.

All 11 recovered proposals map to the focused body with mapped IoU 0.92 to 0.99.
Their raw ring IoU is 0.46 to 0.49, because the ring is larger than a small body.
The 8 frozen proposals keep mapped IoU 0.95 to 0.98.

The lost synthetic proposal is `hcf368-small-light-capture-hcf-item-0-0`.
`interpolation-high-v1` alone loses the same frame.
Its frozen proposal scored wrong (IoU 0.464) in `hcf398-outer-ring-crop-v2`, so the combined setting loses no previous success.
The pre-registered rule allows no lost synthetic proposal. Both records are confirmed contradicted for this reason only.

The debug build on missed frame `hcf402-case-0-hcf-item-1-0` gives side support 0.83, 0.78, 0.69, and 0.85 (top, bottom, left, right).
All 4 sides now pass the 0.65 gate.

**Next action (recommended, needs a decision).** The native checks all pass. The maintainer decides whether 1 lost synthetic proposal that was already wrong blocks the setting.

- If it does not block: score the jitter crop model on the 19 combined proposals through T37, against the frozen proposals.
- If it blocks: diagnose the lost frame first. Do not start the higher-resolution test, because the combined setting already recovers 11 frames.
- In both cases, 17 focused frames still have no proposal. Measure them with the combined debug build before a new kernel setting.

## Proposal repair, step 5: jitter scoring on combined proposals (B405-154)

The maintainer accepted the 1 lost synthetic proposal of B405-153 on 2026-10-17, because its frozen proposal was already wrong.
B405-154 scores crop models through T37 on the 74 frames of the 9 HCF402 captures. It uses selection threshold 0.85 and correct IoU 0.5.

| Model | Proposals | Source | Focused correct | Focused wrong | Focused miss |
| --- | --- | --- | ---: | ---: | ---: |
| Retained `hcf375c-70` | frozen | raw | 3 | 0 | 33 |
| Retained `hcf375c-70` | frozen | mapped | 5 | 0 | 31 |
| Retained `hcf375c-70` | combined | mapped | 16 | 0 | 20 |
| Jitter | frozen | raw | 8 | 0 | 28 |
| Jitter | frozen | mapped | 8 | 0 | 28 |
| Jitter | combined | raw | 8 | 11 | 17 |
| Jitter | combined | mapped | 19 | 0 | 17 |

- Jitter on mapped combined proposals recovers 11 frames and loses 0 frozen successes.
- The no-focus frame stays a correct abstention in every arm.
- Standard rows are identical between jitter on frozen and combined proposals.
- The 11 raw wrong selections are the recovered frames. Jitter selects the ring, but the raw ring box has IoU 0.46 to 0.49 with the body. The mapped box has IoU 0.92 to 0.99.
- Jitter beats the retained model on the same combined proposals: 19 against 16 mapped correct.

The pre-registered rule requires 0 wrong selections but does not name the proposal source.
The mapped source meets every check. The raw source fails only on box geometry.
The record stays unconfirmed until the maintainer decides which source the rule applies to.

17 focused HCF frames still have no proposal. Large-controls and tall-controls had 0 missed frames; edge-clearance has 4 missed frames and recovers 0.
Model acceptance stays false. These are inspected development frames, not an independent audit.

The maintainer confirmed B405-154 supported on the mapped proposal source on 2026-10-17. The 11 raw wrong selections stay recorded as box geometry failures.

## Proposal repair, step 6: the 17 frames without a proposal

The combined debug build (`.build/debug-output/kernel-debug/missed17/summary.json`) runs the real kernel on each frame. It matches each component to the focused body.

- All 17 frames find a ring component about 7 px outside the body. No frame fails brightness or geometry.
- All 17 frames fail the side support gate on 1 or 2 sides.
- Every failing sample fails the inner test. 0 samples are too dim, and 0 samples fail the outer test.

Mean inward profile across a side, from the component edge (gray values, offsets 0 to 9 px):

| Side | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Failing left, `case-0-hcf-item-0-0` | 130 | 254 | 255 | 241 | 59 | 9 | 10 | 65 | 108 |
| Passing right, same frame | 250 | 255 | 254 | 96 | 7 | 10 | 48 | 143 | 149 |

The ring covers offsets 0 to 3 and the dark moat covers 4 to 6. On failing sides the ring falls 1 px further inward, so offset 3 stays at 220 to 241.
With band 3 px, the inner test reads only offsets 1 to 4. It takes the larger of 2 adjacent samples, so it never sees 2 dark samples in a row.

A debug build that searches offsets 1 to band + 2 recovers 17 of 17 frames. This is a prediction from the real kernel code. Standard, no-focus, and synthetic frames are not checked yet.

**Next action (B405-155).** Add the T25 setting `interpolation-high-short-side-inner-v1` with a test. Plan it like B405-152 against the combined kernel. Then score jitter on mapped proposals through T37.

## Proposal repair, step 7: wider inner search (B405-155, B405-156, B405-157)

`interpolation-high-short-side-inner-v1` is the combined setting plus 1 change: the inner moat search reads offsets 1 to band + 2.
It changes 4 source lines, including the version string. A test in `scripts/test_kernel_settings119.py` checks the exact changes.

| Check | Frozen kernel | Combined kernel | Inner kernel |
| --- | ---: | ---: | ---: |
| HCF398 synthetic frames with candidates | 52 of 264 | 56 of 264 | 72 of 264 |
| Focused HCF frames with a proposal | 8 of 36 | 19 of 36 | 36 of 36 |
| Lost proposals against the combined kernel | — | — | 0 |
| Standard and no-focus frames with a proposal | 0 | 0 | 0 |
| Jitter, mapped source: focused correct | 8 | 19 | 36 |
| Jitter, mapped source: wrong or false selections | 0 | 0 | 0 |

- The 17 recovered proposals have mapped IoU 0.92 to 0.99. Each frame has exactly 1 proposal.
- The synthetic set gains 16 frames and loses 0 against either kernel. The frame lost in B405-153 returns.
- Standard rows are identical in the jitter T37 arms. The no-focus frame stays a correct abstention.
- On the raw source, jitter gets 8 correct, 22 wrong, and 6 miss. Raw ring bounds are not body bounds, so these are geometry failures only.

All 3 records are confirmed supported.

**Limits.**

- The setting comes from the same 17 development frames that it recovers. This result is not independent evidence.
- The gained synthetic proposals are counted, not scored for correctness.
- The 9 HCF402 captures share 1 Fixture layout family. 3 factor captures repeat the case-1 geometry.
- Model acceptance stays false.

**Next action (recommended).** Check the inner kernel and jitter on frames that did not shape the setting:

1. Score the 16 gained synthetic proposals for correctness against HCF398 truth.
2. Run the inner kernel and jitter on a new HCF capture with layouts outside HCF402, as an independent development check.
3. If both pass, propose the 3 kernel changes to Maximum-mini-TTR with this evidence. The TTR owner decides about the TTR source.

## Independent check, step 1: synthetic gains and the unused light capture

### The 16 gained synthetic proposals (B405-156)

The check maps each proposal with the fixed HCF401 offsets and compares it with every control box in the HCF398 catalog (`.build/debug-output/synthetic156.json`).

- All 16 gained proposals surround the focused control. The mapped IoU with the focused body is 0.65 to 0.98.
- 15 gained proposals are on 5 `development-diamond` scenes (items 0 to 2). 1 is `hcf368-small-light-capture-hcf-item-0-0`, with mapped IoU 0.65.
- All 72 inner-kernel synthetic proposals are on HCF frames and map to the focused control. 0 proposals map to another control.
- Raw ring IoU is 0.46 for these proposals, so T18 and T20 would score them as wrong. The mapped boxes are correct.

### The unused light-background capture (B405-158, B405-159)

`hcf402-factor-light-background` has the same corner layout as HCF402 on a light background. No setting was derived from it.

- The frozen, combined, and inner kernels all give 0 proposals on its 8 frames.
- Jitter is correct on all 8 known boxes, so the crop model is not the limit here.
- The debug build shows the cause. The background is gray 244, and 77% of the frame is at or above the 160 brightness threshold.
- The ring merges into 1 background component that covers 79% of the frame. The geometry gate rejects it.

Both records are confirmed inconclusive. This capture cannot test the inner setting, because the fixed threshold assumes a dark background.
B405-161 records the light-background limit as its own question.

### Plan for new layouts (B405-160)

`reports/work/B405-160/layout-draft.json` holds 2 draft cases on a dark background:

| Case | Layout | Control size (pt) | Targets | Frames |
| --- | --- | --- | ---: | ---: |
| `b405-160-shelf-row` | 1 row of 5 posters, 48 pt gap | 160 × 240 | 5 | 10 |
| `b405-160-square-grid` | 2 rows of 4 tiles, 64 pt gap | 200 × 200 | 8 | 16 |

The sizes stay inside the tested range and avoid the 180 × 80 shape that failed body geometry. The close neighbors test whether the wider inner search makes proposals on adjacent controls.

Steps:

1. The maintainer approves 2 local development captures (26 frames, about 65 MB, 800 s and 100 MB per job).
2. Maximum-mini-NUIAK checks that the Fixture runs on Maximum-mini. Then it writes T03 recipes with a fresh binding and qualification.
3. The runner captures, then runs frozen, combined, and inner T34 arms and jitter T37 arms like B405-158 and B405-159.
4. If B405-160 is supported, Maximum-mini-NUIAK proposes the 3 kernel changes to Maximum-mini-TTR with the evidence.
