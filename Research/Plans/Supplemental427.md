# SUPPLEMENTAL427 — preserve baseline decisions while testing supplemental proposals

Owner: Maximum-mini-NUIAK. Date: 2026-10-18.

## Question and fixed rule

Can the scoped detector recover baseline abstentions without losing Standard successes or adding wrong selections?
Use the completed DETECTOR422 reports. Do not run new inference or train another model.

If the baseline has exactly 1 crop score at or above 0.85, retain its selection.
Otherwise, use the supplemental detector's existing selection rule with the same crop classifier and threshold.
Never use labels, known control families, or the correct answer to choose the detector.
This is a fallback between scored proposal sets, not a merged-box detector.
A single wrong baseline selection remains wrong. A correct no-focus abstention can become wrong; report that regression explicitly.

## Frozen comparisons

Run 8 jobs: buttons, rows, tabs, diamond decoration, edge clearance, no focus, small decoration, and tall controls.
Each job compares both retained crop classifiers, both profiles, and detector-only versus detector-plus-ring proposals separately.
Frames, labels, groups, thresholds, capture identities, and known-box references remain identical between detector reports.
Require equal inference settings, different detector weight identities, and verified completed T57 receipts.
Reject changed hashes, unmatched frames, different crop models, changed settings, and non-development data.

Use `scripts/supplemental_proposals427.py` with one pinned `supplemental-proposals-v1` bundle per job.
The bundle contains `baseline` and `supplemental` references, each with `report`, `result`, and `spec` file pins.
Each queue job stages that bundle as `bundle.json` and runs `supplemental_proposals427.run`.
The adapter reuses the tested score-only comparison from `proposal_tier_policy.py` without changing the T66 contract.
T66 still requires the same detector at different confidence thresholds. Do not use it to conceal a detector change.
No shared runtime module changes while training runs. The adapter has its own pinned source closure.

## Output and decision

Write case-linked outcomes, gains, lost successes, new wrong selections, profile support, and group support.
Write an artifact receipt. Keep `modelAccepted` false, even if diagnostic regression checks pass.
Reject replacement when any retained success is lost or any new wrong selection appears.
If it recovers useful selections without regressions, qualify the fixed rule on new native groups before runtime review.
If it fails, preserve the cases and diagnose ambiguity or box geometry before another training change.
Related models, profiles, and arms do not create independent trials.

Each job permits 800 s, 100 MB, and 1 attempt. These cached comparisons add seconds of work, not overnight capacity.
The detached runner owns execution. Standard and shipped models remain unchanged.

## Verification

Nine focused tests pass, including real retained reports through an isolated queue.
Negative checks cover changed receipts, mismatched producer specifications, changed settings, and false no-focus selection.
Single baseline successes remain selected. Tests also confirm that truth does not repair wrong baseline selections.
The positive test keeps model acceptance false.
Offline Swift checks pass with unchanged binaries: 177 Swift Testing checks and 14 XCTest checks.
All 8 live comparison jobs pass readiness checks. Measured-box training remains active during admission.
