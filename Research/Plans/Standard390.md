# STANDARD390 — prepare Standard corrections from retained evidence

Date: 2026-10-13. Owner: research-host-NUIAK.

## Question and scope

Which Standard failures justify the next data correction without losing previous successes?
This batch uses cached predictions. It does not capture images, train weights, change thresholds, or promote a model.
HCF remains separate and optional. Current queue execution remains unchanged.

The retained FOCUS373 decision reports 342 correct notification cases versus 301 for its matched control, from 392 authored pairs.
It reports 18 false changes versus 42. The wider regression comparisons report 6 lost successes versus 22.
The earlier follow-up checks only the notification subset. It cannot explain losses in the wider retained suite.
The detector scorecard reports 346 localized controls from 583 reviewed controls. Localization does not establish correct classification or focus selection.
These are retained findings, not newly measured outcomes.

## Executable batch

| Job | What does it test? | What does it decide? |
| --- | --- | --- |
| standard390-01-retained-appearance | Compare control and notification predictions on original views, with roles kept separate. | Identify losses specific to the correction and losses shared with the control. |
| standard390-02-native-transfer | Compare retained native and replay predictions without changing input views. | Determine whether authored gains preserve native movement evidence. |
| standard390-03-context-regression | Compare existing global, left, and center input views. | Use margins to distinguish strong errors from weak decisions. View names do not prove focus position. |
| standard390-04-identical-neighbors | Compare movement between identical neighboring controls. | Determine whether the next data recipe needs movement examples without artwork changes. |
| standard390-05-data-priorities | Combine all 4 reviews with pinned detector evidence and reviewed body bounds. | Select case-linked data needs for detection, classification, and focus separately. |

The first 4 jobs depend on completed producer comparisons. The final job waits for all 4 reviews.
Each job permits 800 s, 100 MB, and 1 attempt. The combined maximum is 4,000 s and 500 MB.
These are ceilings, not expected runtime. Comparable measured runtime is unavailable; do not call this an overnight workload.
The existing runner owns execution. Do not start a second runner or change current approvals.

## Evidence and acceptance

- Pin specifications, code, configurations, and external reports. Queue dependencies bind producer specifications and verified output hashes.
- Compare identical rows, labels, groups, and baseline scores. Fail on duplicates, missing predictions, changed hashes, or invalid probabilities.
- Preserve the existing 0.15 stable threshold and 0.85 changed threshold. Abstentions are not correct selections.
- Report every gain and loss by case, with scores, margins, source domain, and recorded role.
- Keep training rows separate from development and retained evaluation. These inspected cases cannot become untouched final evaluation.
- Do not count repeated views as independent trials. Record group identities without claiming statistical independence.
- Keep raw predictions and reviewed controls unchanged. Unmatched detector proposals do not automatically become false positives.
- Keep unknown OS profile and taxonomy compatibility explicit. The old real-app report does not verify the OS Focus Style setting.
- All outputs keep model acceptance false. Shared control errors do not relax the previous-success gate.

The final report verifies the old detector inputs and raw prediction hashes without rerunning inference.
It includes original body bounds for review. It does not convert external records into training data.
This read-only reporting path does not change the queue engine's general input contract.

## Next conditional work

1. Use completed PROGRAM384-D1 seeds to assess variation before another notification correction.
2. Prepare Standard Fixture recipes for supported detector class, size, position, and decoration gaps.
3. Preserve listed losses and existing successes as fixed comparison cases for any candidate.
4. Implement PROGRAM384-B1's missing fallback adapter before claiming deployable focus selection results.
5. Choose 1 matched data correction only after the reports identify its target failure and eligible training inputs.

New capture needs a qualified target and frozen data groups. New training needs a fixed recipe and all dependent regression jobs.
Do not repeat completed comparisons or add arbitrary experiments to fill the queue.

## Preparation receipt

- All 5 specifications pass validation and receive individual approvals.
- The first 4 jobs have complete, hash-verified producer outputs. The final report waits for those 4 jobs.
- The focused suite passes 119 tests in 47.6 s, including isolated queue and approval tests.
- The offline Swift check passes 173 Swift Testing tests and 14 XCTest tests using the existing build.
- The new adapter passes a staged input/output test and rejects an altered producer file.
- Original worker modules, submitted jobs, thresholds, and running processes remain unchanged.

No experiment outcome follows from these software checks. The background runner owns execution and stores the measured reports.
