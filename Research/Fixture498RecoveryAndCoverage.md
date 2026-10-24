# Fixture recovery and detector coverage

Owner: Maximum-mini-NUIAK. Date: October 24, 2026.

## Fixture and retained evidence

The supported launch succeeds on the approved tvOS Simulator.
The endpoint settles with 7 measured controls.
Process identity, installed binaries, Simulator identity, and endpoint binding verify.
Launch qualification does not make a capture or change settings.

The caller exporter verifies 9 existing files and 26,143 bytes.
The retained campaign has 2 failed cases and 6 unattempted cases.
The recovery successor preserves both failed records exactly.
It resumes only unattempted cases within the unchanged remaining cumulative budgets.
It does not restart the Simulator.

The adapter uses the source-pinned TTR caller exporter.
It checks exporter dependencies before dispatch and verifies exported file sizes and hashes.
It does not repeat capture when export fails.
Maximum-mini-TTR source remains unchanged.

## Qualification and admission

All 37 focused tests pass.
The isolated queue completes the valid recovery case.
It rejects changed failed evidence with `recovery_failed_case_replayed`.
The rejected case cannot release downstream work.

The offline Swift build passes after using a fresh cache in the active checkout.
The model digest test passes.
The broader Swift run stalls in Vision's task queue during frame similarity checks.
Its log and process sample remain preserved. Only those validation processes stop.
The broader Swift suite is incomplete. The detached experiment runner remains active.

The approved graph has these jobs:

1. `adr493-retained-six-resume-v4` resumes the retained campaign.
2. `adr493-session-1-r4` runs the first separate-session arm after recovery.
3. `adr493-session-2-r4` runs the first reused-session arm.
4. `adr493-session-3-r4` runs the second reused-session arm.
5. `adr493-session-4-r4` runs the second separate-session arm.
6. `adr493-session-report-r4` compares observed labels and timing.

The 4 session jobs have no previous attempts or dispatch markers.
They keep their original campaign identities and approved limits of 800 s and 250 MB each.
The sequence prevents concurrent use of the same target.
Original specifications, failures, and dispatch markers remain preserved.

The maintainer approves the required idle service restart.
The restart tool verifies no active job leases and stops dispatch before replacing the service process.
The new service starts with the same queue and priorities. Its process ID is 79401.
The background runner starts `adr493-retained-six-resume-v4`.
The 4 session comparisons remain gated on verified recovery. Recovery completion is not yet established.
No job is cancelled. Standard and previous successes remain unchanged.
Restart and admission evidence appears in `reports/work/FIXTURE498/approved-restart.log` and `restart-verification.json`.

## Independent coverage experiments

COVERAGE498 defines 32 jobs across 2 research questions through existing templates.
All 32 jobs receive exact approval. Admission checks show 14 ready jobs and 18 dependent jobs.
These jobs use retained images, models, labels, and completed scorecards.
They do not depend on TTR recovery.

The tvOS question tests confidence 0.25 against 0.5 at the same 1280-pixel input size.
PROPOSAL497 finds proposals for only 6 of 40 focused Standard observations.
Eight detection jobs test whether confidence filtering explains missing controls.
Eight matched reports compare recovery, class errors, localization, and lost successes.
Three focus comparisons and one combined report check the downstream selection effect.
The existing 640-pixel confidence test does not answer this fixed-resolution question.

The independent iOS question tests confidence-related losses in the frozen model.
Six detection jobs use confidence 0.25 against completed 0.5 controls.
Six matched reports compare correct detections and lost successes.
Related device conditions remain related observations, not independent trials.

The first iOS attempts stop before inference with `detector_baseline_settings`.
Their copied preparation input requires the old confidence setting.
The original iOS branch loses approval. Its specifications and failures remain preserved.
Twelve `-r2` successors remove that preparation input and retain the separate matched baseline report.
All 12 successors receive exact approval. This correction changes configuration only.
The handoff snapshot shows 1 completed job, 14 pending jobs, and 17 jobs waiting for producer outputs.
No corrected job reports a failure at that snapshot.

Unmatched predictions are not verified false positives when annotations are incomplete.
The tvOS focus reports retain their separate Standard and optional HCF profiles.
No result promotes a model automatically.
Standard, shipped models, and the optional observer remain unchanged.

The 14 preceding inference jobs total approximately 60.5 s.
The lower threshold can increase downstream scoring time.
This is useful short work. It does not provide an overnight training reserve.
Review the matched reports before choosing a training correction.

## Evidence

- `reports/work/FIXTURE498/`: launch, binding, export, isolated queue, admission, and coordination receipts.
- `reports/work/COVERAGE498/`: immutable batch, baseline durations, and admission receipts.
- `scripts/test_ttr_campaign_recovery493.py`: preservation and dispatch failure checks.
- `scripts/test_campaign_caller_export498.py`: caller export and hash checks.

BigDog-Coordinator stores the verified launch and export update at cursor 1307.
Storage does not confirm forwarding to Sillycon-TTR.
The SDK reply at cursor 1306 is read and acknowledged.
Its performance limitation and uncommitted source do not change model acceptance.
