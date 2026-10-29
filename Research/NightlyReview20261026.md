# Nightly research review — 2026-10-26 UTC

Owner: Maximum-mini-NUIAK.
Window: 2026-10-25 06:49:54.030 UTC through 2026-10-26 06:46:11.200 UTC.
The previous successful report defines the start. The heartbeat defines the cutoff.
Attempt identities and hashes are recorded in reports/work/NIGHTLY-20261026/review-window.json.
The mounted USB volume passes verification. Approximately 1.6 TiB remains available.
This review uses the backlog-grooming and experiment-task-authoring skills. No implementation code changes occur.

## What improved

No verified model improvement this review period.
Native row annotations now distinguish row bodies from their text. This is annotation progress, not a model gain.
All 22 measured row/text pairs have distinct bounds and containment. Four pairs extend outside their frames and remain excluded.
The diagnostic subset contains 18 visible pairs, 36 annotations, 4 frames, and 1 related group.
Two additional button-bound failures prevent complete RTLMirror training admission.
See [verified results](Advance537ResultsAndProducer.md).

## What we learned

The iOS 960-pixel comparison gains 59 detections and loses 294 against the matched 640-pixel control.
Class-agnostic matching still loses 266 detections. Stop this resolution branch; another unchanged fit is not justified.
Native SDK preparation produces 6 review-only crops. Profile and ancestry requirements still prevent training admission.
TTR producer source 337b6f7 passes 21 offline checks. These checks do not establish native runtime qualification.
Sillycon-TTR reply 1513 supplies the existing Settings inspection entry and cleanup sequence.
The collector deliberately requires test roles. Existing intake tools do not make it a native training producer.
See [workflow findings](Workflow533CampaignsAndResults.md).

## What regressed

IOS534 control quarantine gains 3 detections and loses 4 against its matched control.
IOS534 additive quarantine gains 6 and loses 10 against its matched control.
Against Run013, the control gains 13 and loses 7; the additive candidate gains 14 and loses 12.
Reject both replacements. Reduced image membership also changes exposure, so this does not isolate annotation quality.
Standard, shipped models, and the optional HCF observer remain unchanged.

All 3 ROW537 inference attempts fail during reporting because labelReview is missing.
Their raw predictions and scorecards survive. Preflight also finds missing frame screen metadata.
The originally selected T65 comparison requires identical model weights. It cannot compare these trained candidates against Run013.
These are preparation defects in Maximum-mini-NUIAK, not TTR failures or uncertain model labels.

## What runs next and what each test decides

This review admits and approves exactly 2 T42 comparisons:

- row537-retained-control-comparison: compare the original-only quarantine candidate with Run013 on measured native rows and text.
- row537-retained-additive-comparison: compare the additive quarantine candidate with Run013 on the same annotations.

Both use retained predictions. No capture, training, or inference repeats.
Successor manifests add reviewed metadata and screen identity from existing frame IDs.
Derived scorecards change only the label reference. Raw prediction hashes, models, controls, coordinates, groups, and roles remain unchanged.
The existing matcher validates 4 frames and 36 annotations before registration.
Original failed attempts and labels remain preserved. The old dependent comparisons are not reported as runnable.
The reports distinguish wrong class, misplaced boxes, and missing controls before a corrected training recipe is selected.
Partial labels cannot establish full-screen precision. Neither job promotes a model.
Each job retains 800 s and 100 MB limits. These are limits, not duration estimates.
Expected execution is seconds to minutes; exact duration is unmeasured for these successor configurations.
No training continuation or longer fit is admitted without a new supported hypothesis and qualified inputs.

## Queue health

The single maintenance snapshot finds a healthy continuous runner, 0 running jobs, and 0 ready jobs.
Ready duration at that snapshot is 0 s. The review subsequently admits the 2 comparisons above. Both belong to the same row investigation.
No post-admission queue poll is performed. Their execution remains with the existing runner.
The snapshot contains 401 active blocked rows: 389 have dependency failures and 12 have other readiness failures.
It separately identifies 102 exhausted rows, 22 unselected rows, and 400 superseded rows.
These historical row counts are not independent research questions.
Snapshot construction takes 62.78 s. Reporting overhead is not experiment execution.
The overnight reserve target remains unmet. No arbitrary sweeps or filler jobs are added.

The window records 149 completed attempts and 10 failed attempts.
All 147 recorded benchmark and decision summaries checked in this window match their receipt sizes and hashes.
Non-overlapping completed execution totals 3985.18 s. Failed execution totals 85.91 s.
Recorded occupancy is 4.72% of 86177.17 s. No execution is recorded for 95.28% of the window.
Occupancy does not establish scientific progress or continuous runner availability.
The snapshot confirms no restart is needed. No service change occurs.

## Blockers and approvals

TTR replies through cursor 1513 are read and acknowledged. No new artifact transfer is offered.
Maximum-mini-NUIAK must connect owned-session entry, profile collection, restoration, and queue publication for PIPELINE538.
Its active/project workspace mismatch remains an integration prerequisite. Earlier workspace consent exists; this review does not change services or workspaces.
Sillycon-TTR needs the requested training/development contract, separate from runtime qualification of its test-only collector.
This review sends that minimum contract through BigDog-Coordinator. Storage is confirmed at cursor 1514; forwarding and acceptance are not confirmed.
The contract requires explicit split ownership, construction identity, independent ancestry, observed focus, aligned bounds, profile continuity, and cleanup.
Existing review/test pairs remain excluded from training.
No new human approval is required for the admitted retained comparisons.

## Priority changes and reasons

1. Finish TVOS515 exact consumer qualification. It tests the existing Standard fallback through TTR without another training campaign.
2. Finish PIPELINE538 and the separate eligible native producer contract. This supplies training inputs for focus and temporal work.
3. Review the 2 recovered iOS row comparisons. Then repair eligible membership rather than repeat failed quarantine recipes.
4. Fix T56 metadata preflight and comparison-template selection during the next implementation tranche.
   Acceptance requires rejection of missing metadata before inference and a different-weights comparison through T42.
5. Keep timeline, navigation-map, and portable app work planned. Record baseline costs during integration; defer the full observation benchmark until collection improves.

These priorities advance separate goals. Missing native data does not block retained iOS comparisons or Standard consumer qualification.
Detailed private records remain in reports/work/NIGHTLY-20261026. No commit, push, install, model promotion, or direct model execution occurs.
