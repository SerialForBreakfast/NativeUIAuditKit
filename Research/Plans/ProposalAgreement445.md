# AGREEMENT445 — Require spatial agreement before supplemental focus selection

Owner: Maximum-mini-NUIAK. Date: 2026-10-18.

## Final result

All 10 jobs complete. The retained-model correction fails acceptance.
It gains 2 Standard selections, loses 0 successes, and adds 1 wrong selection across 43 frames and 13 case identifiers.
The later ancestry review maps these cases to 11 original capture groups. Preserve the original report without overstating independence.
All 3 no-focus abstentions remain correct. The small-decoration failure survives agreement.
The Standard-only candidate gains 6 against its own reference without new wrong selections, but earlier replacement regressions remain.
Use [CASCADE446](BaselineCascade446.md) to test candidate fallback while retaining baseline selections.
Do not promote either standalone policy from these results.

## Completed selection results

All 28 SELECTION444 jobs complete.
The geometry reports identify 16 retained-detector observations and 23 experimental-detector observations where known-box selection succeeds but detector-box selection fails.
These counts describe associations. They do not prove that geometry correction will recover selection.

The unrestricted fallback preserves existing selections but adds wrong selections.
With the retained crop model, it gains 2 Standard selections and adds 1 wrong selection.
With the Standard-only crop model, it gains 9 and adds 2 wrong selections.
Both preserve the 3 no-focus abstentions across the inspected development set.
Neither policy passes the preservation requirement.

The retained-model wrong selection occurs on small decoration.
Its primary detector already supplies 9 boxes. The fallback supplies 4 boxes and selects a different proposal set.
This supports testing agreement between proposals before accepting a fallback.
It does not justify a new confidence threshold, family-specific routing, or another training run.

## Fixed correction

Keep the primary detector's single selection unchanged, including its recorded wrong selections.
After primary abstention, consider the supplemental detector only under these conditions:

1. The primary detector has at least 1 proposal.
2. Exactly 1 primary proposal has the highest crop score. Ties remain abstentions.
3. The supplemental detector has exactly 1 crop score at or above 0.85.
4. The primary top-score box and supplemental selected box have IoU of at least 0.5.

Use the existing 0.85 score threshold and 0.5 overlap criterion. Do not sweep them.
Use scores and geometry for selection. Labels and control families never choose the path.
False selections on no-focus frames remain regressions.
HCF retains the primary decisions unchanged. It does not control Standard acceptance.

This is a post-hoc development experiment. Agreement between related detectors is not independent corroboration.
Do not infer calibrated confidence or release qualification from agreement.

## Execution graph

Use 1 gate, 8 cached comparisons, and 1 complete decision report.
The gate depends on the SELECTION444 supplemental summary.
It releases the fixed correction only when the retained-model fallback has both gains and new wrong selections.
Missing no-focus support or fewer than 3 groups produces an inconclusive gate.

Reuse the immutable supplemental bundles from SELECTION444.
Preserve frames, groups, crop models, proposal settings, scores, and previous attempts.
The new adapter wraps the existing input verification and supplemental comparison.
It performs no inference, capture, training, export, or runtime change.
The retained crop model controls the main decision. The rejected Standard-only model remains a separate diagnostic comparison.

Compare corrected outcomes against both retained decisions and unrestricted fallback outcomes.
Report gains, losses, new wrong selections, prevented wrong selections, and unrestricted gains lost.
Require complete membership across all 8 conditions. Missing comparisons cannot pass.
Carry earlier crop regressions into the final report. No model receives automatic acceptance.

Each job permits 800 s, 100 MB, and 1 attempt.
These are short cached diagnostics, not overnight training capacity.
The detached runner owns execution. Do not restart it or change shared execution modules.

## Next decision

If the correction keeps useful gains without regressions, require independent native groups before runtime review.
If it removes all gains, record that the conservative rule is inconclusive.
If it adds wrong selections, reject it. Do not tune thresholds repeatedly on these cases.
Any later training correction needs training-only geometry evidence and the complete retained regression suite.
No inspected development case becomes training data.

## Qualification and admission

All 15 focused tests pass. They include real cached reports through an isolated queue and failed-source blocking.
Tests cover location disagreement, ties, empty proposals, invalid values, no-focus regressions, unchanged HCF, and duplicate execution prevention.
Offline Swift checks pass 177 Swift Testing cases and 14 XCTest cases.
All 10 exact jobs are registered and approved. The existing runner remains active with no reported error.
No runner restart occurs. Admission does not establish a model improvement.
Local receipts remain under `reports/work/AGREEMENT445`.
