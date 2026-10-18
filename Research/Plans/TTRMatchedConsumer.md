# Matched consumer comparison and lower native exposure

Owner: Maximum-mini-NUIAK. Date: 2026-10-17.

## Finding

TTR supplies 20 Standard crops from 4 related frames. These remain development evidence.
The archive supplies observed focus records, but no raw native scene brackets. Label verification remains limited.
T62 verifies archive membership, hashes, geometry, and label consistency. T63 reproduces production cropping and records crop hashes.
All 20 RGB hashes match the producer records.

On matched PyTorch inputs, the delivered checkpoint misses 4 focused crops and produces 7 false positives.
The mixed candidate detects all 4 focused crops but produces 16 false positives. It marks every crop as focused.
Neither model selects the correct control on these 4 frames under the single-candidate rule.
These results do not support replacement. Standard remains unchanged.

Vision replay remains separate from PyTorch comparisons. Backend differences cannot establish model improvement.
The first Vision cohort matches RGB bytes and has a maximum score difference of 0.0024414 against TTR.
The second cohort also matches RGB bytes. Its maximum score difference is 0.00439454.

## Next controlled test

Use B405-189 and existing templates T54, T06, T37, T63, and T15.
Train 1 candidate with 12.5% native exposure. Reuse the completed 0% and 25% matched training controls.
Keep 7200 samples per epoch, 3600 per label, seed 371, initialization, preprocessing, and development membership unchanged.
Preserve every unique artwork example. Do not train on the inspected TTR cases.
Use 30 epochs, 1800 s, and 2 GiB. Do not retry automatically.

Compare native buttons, rows, tabs, retained artwork, no-focus scenes, and the 2 TTR cohorts.
Report Standard separately from HCF. Require zero lost previous successes and zero added wrong selections.
Use crop false positives as well as frame decisions. Abstention from many positive crops is not a model gain.
If lower exposure removes native gains, diagnose the representation before another dose change.
Keep the proposed 50% arm blocked. Current false positives do not justify increased exposure.

## Execution and feedback

The detached runner executes immutable jobs. Membership verification precedes training registration.
Each report preserves case IDs, groups, model hashes, input hashes, thresholds, and known evidence limits.
Send the matched findings to Sillycon-TTR through the existing coordinator conversation.
Request only missing evidence that changes a decision. Do not request another capture of these same cases.
No candidate receives navigation authority or production promotion.

## Full-screen follow-up

Do not stop at known-box scoring when the lower-exposure model finishes.
Use T57 to compare 12.5% and 25% candidates on identical retained detector boxes.
Cover buttons, rows, tabs, no-focus scenes, edge clearance, decorative diamonds, small decoration, and tall controls.
Reuse completed detector outputs. Do not repeat detection or capture.
Preserve the original known-box checks and HCF-only ring additions.
Report missing proposals separately from classifier errors. Require zero lost successes and no added wrong selections for each profile.

If known-box scoring improves but full-screen selection fails, prioritize proposal geometry or coverage.
If both paths lose successes, reject the dose correction before export or consumer integration.
If both improve without losses, prepare repeatability and consumer qualification. Do not change Standard automatically.
