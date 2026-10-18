# Preserve focus decisions before using extra boxes

Owner: Maximum-mini-NUIAK. Date: 2026-10-17.

## Evidence

Lower detector confidence recovers buttons and Standard edge controls.
It also introduces competing boxes, lost row selections, and false selections on no-focus scenes.
Do not replace the global threshold based on detection recall alone.

## Fixed comparison

T66 reads 2 verified T57 reports for the same frames, models, crop tool, and mapping.
The reports differ only in detector confidence: 0.5 versus 0.25.

1. If the 0.5 report has exactly 1 crop score at or above 0.85, keep its selection.
2. Otherwise, use the selection from the 0.25 report.
3. Evaluate the result against the recorded native labels.

The selection rule does not read labels. It preserves confident wrong selections as well as confident correct selections.
An abstention on a no-focus scene can become a false selection. Record that failure explicitly.
Evaluate the 25% and 12.5% crop models separately. Neither model is the delivered production baseline.
Evaluate Standard and HCF separately. Optional ring boxes remain restricted to HCF.

## Qualification and scope

- Unit tests cover preservation, recovery, wrong selections, no-focus failures, input changes, and invalid scores.
- The isolated queue passes unchanged replay and the fixed policy.
- The isolated queue rejects an unsupported policy.
- B405-219 registers 8 independent condition jobs using retained reports.
- Each job uses at most 800 s and 100 MB. No inference, training, capture, or runtime change is required.

Conditions include buttons, rows, tabs, edges, no-focus scenes, decorative diamonds, small decoration, and tall controls.
Report case-linked gains, lost successes, and new wrong selections for each model and profile.
Related profiles and repeated model comparisons are not independent trials.

## Decision

Advance only combinations with gains, zero lost successes, and zero new wrong selections.
Advancement means separate qualification on new groups, not deployment or model promotion.
Preservation of existing confident selections follows from the policy design. It is not proof of general accuracy.
If no-focus failures remain, prioritize training-only competing negatives and abstention before another threshold change.
Do not train on these inspected development cases.

## Completed result

All 8 condition jobs complete. Focused software checks and integrated offline Swift checks pass.

| Model and path | Gains | Lost successes | New wrong selections |
| --- | ---: | ---: | ---: |
| 25% model, Standard detector | 4 | 0 | 0 |
| 25% model, HCF detector plus ring | 1 | 0 | 0 |
| 25% model, HCF detector only | 1 | 0 | 1 |
| 12.5% model, Standard detector | 4 | 1 | 1 |
| 12.5% model, HCF detector plus ring | 1 | 1 | 1 |

Do not sum these rows. They reuse related scenes and model comparisons.
Only the first 2 combinations qualify for further testing on independent groups.
Neither model qualifies for replacement. The 25% model still fails the separate TTR artwork cases.
The next task needs independent native groups with no-focus scenes and decorative distractors.
Maximum-mini-NUIAK owns their preparation through qualified Maximum-mini-TTR capture tasks.
No new capture is started in this tranche.

## New-group follow-up

B405-220 through B405-228 define 45 jobs through existing templates.
The 5 capture plans contain 34 frames across 4 development groups.
The cases cover buttons, rows, tabs, decorative artwork, and matched null-focus artwork.
Related Standard/HCF frames and focused/null-focus counterparts retain the same group.
These are new layouts within known families, not an unseen-family or physical-device audit.

- T03 captures native OS profiles and verifies restoration.
- T59 checks observed body labels, image hashes, and duplicate conflicts.
- T34 measures ring proposals without using them as focus labels.
- T56 compares detector confidence 0.5 with 0.25 on identical frames.
- T37 scores known boxes with the retained 25% and 12.5% models.
- T57 scores detector boxes with those same models and checks known-box replay.
- T66 follows after verified T57 reports and receipts exist.

Only the 25% Standard detector path and optional HCF ring path can advance from the previous result.
The 12.5% model remains a rejected comparison, not another candidate for promotion.
The separate TTR artwork failure still blocks replacement.
No-focus means no planned control has observed focus. It does not establish every possible app state has no focus.
The decorative shape is a text glyph, not an authored native border.

Maximum-mini-TTR reports clear ownership before registration. The helper and Fixture binaries match the qualified capture path.
The background runner starts the first capture during registration.
The remaining capture approvals encounter its active ownership and remain pending until the target becomes clear.
Do not stop the running capture or bypass ownership to approve them.
This exposes an admission race: capture-batch approval needs a safe boundary before dispatch, not weaker ownership checks.

Each job retains the 800 s and 100 MB limits. Their sum is a ceiling, not an execution estimate.
No production module, Standard default, model weight, or runner setting changes.

### Capture failure and recovery boundary

The first button capture stops after 38.9 s with `profile-standard:None` and zero captured frames.
The underlying TTR receipt reports `stopped`, `ambiguous`, and `desiredVerified: false` after 3 inputs.
Postflight reports clear ownership. This does not prove restoration of the original setting.
The remaining captures are revoked after the failure is inspected. Preserve any intervening failed attempts.
The 40 analysis jobs remain approved, with capture dependencies preventing premature execution.

The existing recovery adapter uses a legacy v1 specification. The current gate correctly refuses its approval.
A successor needs the current capture evidence contract and positive and negative qualification before execution.
Do not weaken that gate or remove the recovery guard manually.
Maximum-mini-TTR receives the exact operation through coordinator request `nuiak-ttr-native-recovery-20261017-v1`.
The request is stored at cursor 825. Forwarding and acceptance are not verified.

Fourteen focused template checks pass. The full 45-job dependency graph compiles before registration.
No production code changes require another integrated Swift run in this follow-up.
The earlier integrated Swift result remains unchanged evidence, not a newly executed check.

### Root cause from retained observations

Observations 16 and 17 agree on Display, Bold Text focus, Standard value, and session generation.
Each contains 12 rows. Only the last clipped label differs: `Alhita Dni` versus `Alhita D`.
The full prefix through Focus Style matches.
TTR's `HCFRecipe.Observation.agrees` rejects the pair before the value-verification branch.
Its existing suffix exception applies only when Focus Style itself has focus.
This is a route observation-matching defect, not evidence that the setting toggle is unavailable.

Sillycon-TTR owns the route correction. Maximum-mini-NUIAK owns consumer qualification and queued recovery.
Require a replay of the retained pair and rejection tests for changed focus, value, session, duplicate targets, and relevant row order.
Limit any tolerance to information that cannot change the next allowed action.
Keep choice-page and uncertain-input checks strict. Do not ignore all OCR differences.
Test the supported starting pages and verify Standard/HCF restoration before resuming capture.
The diagnosis is sent under `nuiak-ttr-native-recovery-diagnosis-20261017-v1`, stored at cursor 827.
Forwarding and acceptance remain unverified. No route retry occurs during diagnosis.

### Recovery adapter repair

`native_capture_recovery.py` adds the v2 evidence contract through the existing allowed recovery entrypoint.
Legacy job specifications and failed attempts remain unchanged.
The successor pins the plan, helper, Fixture binding, staging location, and exact failed guard.
It rejects a live prior process before native execution.
It requires verified Standard restoration, closed ownership, and the original Fixture state.
It writes and checks the restored screenshot and receipts before removing the preserved guard.
It does not label the screenshot as training data or accept a model.

Eight software checks pass, including failure retention and current queue evidence validation.
The isolated queue completes `recovery-check-pass` and rejects `recovery-check-invalid` with `recovery_check_version`.
These mocked software checks do not establish native recovery.
`tier-native-recovery-v2` remains blocked on Sillycon-TTR's delivered repair and the qualified consumer helper identity.
After that repair, pin a fresh immutable successor. Let the background runner perform the native recovery.
Approve replacement capture jobs only after independently checking the successful recovery receipt.

The integrated offline Swift check passes 177 tests in 25 suites.
The first check fails because a migrated module cache retains the internal-drive path.
A fresh project-local module cache resolves that check without deleting the old cache.
Logs remain under `reports/work/RECOVERY-V2-20261017`.
TTR has no new reply at handoff. The adapter update is stored at cursor 829; delivery remains unconfirmed.
