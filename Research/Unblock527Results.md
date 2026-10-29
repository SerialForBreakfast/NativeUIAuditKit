# UNBLOCK527 — Independent training and supported SDK capture

Date: October 25, 2026. Owner: Maximum-mini-NUIAK.

## Decisions

Lower detector confidence does not improve retained focus selection. Reject this correction.
Across 56 retained images in 8 related groups, both arms select 2 focused controls correctly.
Wrong selections increase from 6 to 7. Correct abstentions decrease from 10 to 9.
Both arms miss 38 focused endpoints. The candidate loses 1 previous success and adds no gains.
The comparison fixes crop weights and changes proposal confidence from 0.25 to 0.10.
Related frames do not count as independent observations. These are development results.
The 8 scoring jobs and replacement aggregate report complete with verified outputs.
The original aggregate attempt remains preserved after a dependency mismatch.

## Independent iOS correction

IOS518 requests a base learning rate of 0.0001, but its default bias warmup starts much higher.
The recorded first-epoch bias rates are approximately 0.0686. This repeats the documented IOS-REPAIR165 failure pattern.
The training adapter now accepts an explicit bias warmup rate equal to the base rate.
It checks effective settings before training and checks recorded rates after training.
Omitted settings preserve historical behavior. No existing model changes.

Two matched experiments are registered and approved:

- IOS527-ADDITIVE uses the same 144 qualified images as IOS518 unfrozen training.
- IOS527-CONTROL uses the same 128 original images as IOS518 control training.

Both preserve Run013 initialization, seed 371, membership, full-backbone training, 30 epochs, and base rate 0.0001.
Each fit has a 30 min limit and 2 GiB output limit.
Recorded comparable fits total 1,783 s. Expected training duration is approximately 30 min, plus comparisons.
The 34 jobs contain 2 fits, 12 scoring jobs, 8 decisions or reports, and 12 conditional diagnoses.
These are 2 investigations, not 34 independent experiments.
Reports compare matched predecessors and retain Run013 checks. Any lost previous success rejects replacement.
The runner starts the additive fit. The control fit waits independently.
The other 32 jobs depend on their parent outputs or scientific conditions. They are not missing-input repair tasks.
No iOS model improvement is claimed before these comparisons finish.

## SDK producer

The source-built NavigationConsumer sample is installed and launched under explicit approval.
Its authenticated snapshot reports 2 native buttons, observed focus, and stable process identity.
The new capture adapter uses a versioned request instead of a campaign-name allowlist.
It preserves exact approvals, target ownership, byte limits, immutable inputs, and source identities.
The approved idle dashboard restart loads this contract. The background runner remains responsible for capture.

The first attempt exposes a logging collision. The correction preserves separate readiness and capture logs.
The second attempt fails because the installed TTR helper rejects the documented packet arguments.
Neither attempt creates a packet directory. Both attempts remain preserved.

A fresh TTR build from Git revision e4c693c5237b8498a23e60d51c104ee5f7600a16 passes package verification.
The approved idle replacement passes the passive runtime check and preserves the selected workspace.
Job sdk527-native-packet-r3 is approved with a 700 s limit and 100 MB output limit.
It waits behind active training. It does not send navigation input.
Its pending status does not prove successful capture or training eligibility.

Observed profile and reviewed group membership remain required for profile-specific training.
Unknown profile stays unknown. Inter-frame timing is required only for temporal products.
The sample enrollment expires. If expiry blocks execution, preserve the attempt and refresh enrollment before a named successor.
Do not repeat an unchanged failed command or classify app contrast as observed HCF state.

## Verification

The combined focused suite passes 45 tests, including realistic positive and negative queue paths.
The capture gate suite passes 44 tests, including legacy campaign behavior.
All 177 Swift tests pass in 54.28 s.
Coordinator request 1466 is stored. Forwarding to Sillycon-TTR is not confirmed.

## Next decisions

1. Review the 2 iOS comparisons for retained losses and class recovery.
2. Verify the queued SDK packet and identify the exact remaining training fields.
3. Use observed profile evidence to release native crop preparation through existing templates.
4. Keep proposal geometry and focus scoring separate when diagnosing the 8 detector misses.

Standard, shipped models, and previous success evidence remain unchanged.
No model is promoted. No new schedule is created.

## Evidence

- [Proposal findings](../reports/work/UNBLOCK527/proposal-findings.json)
- [Training admission](../reports/work/UNBLOCK527/training/admitted.json)
- [Batch state](../reports/work/UNBLOCK527/batch-state.json)
- [Focused tests](../reports/work/UNBLOCK527/final-tests.log)
- [Swift tests](../reports/work/UNBLOCK527/swift-tests.log)
