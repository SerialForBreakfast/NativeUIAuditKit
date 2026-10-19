# CASCADE446 — Preserve baseline selections before candidate fallback

Owner: Maximum-mini-NUIAK. Date: 2026-10-18.

## Measured reason

AGREEMENT445 completes all 10 jobs across 8 conditions and 13 case identifiers.
The later ancestry review identifies 11 original capture groups.
The retained-model agreement rule gains 2 Standard selections but adds 1 wrong selection.
It loses no previous successes. It preserves all 3 no-focus abstentions.
The small-decoration failure survives spatial agreement. Agreement does not establish correctness.
Reject this rule as a replacement.

The Standard-only candidate gains 6 selections against its own reference without new wrong selections in this comparison.
This does not erase its earlier losses against the retained model.
The next test combines these complementary results without replacing baseline selections.

## Frozen comparison

Use the existing retained and supplemental proposal bundles from SELECTION444.
Keep frames, hashes, groups, scores, crop preprocessing, and thresholds unchanged.
Do not train or collect images.

1. Keep every retained baseline single selection, including its existing wrong selections.
2. After baseline abstention, test the Standard-only candidate's spatial agreement rule.
3. Require a unique primary maximum and exactly 1 supplemental candidate score at or above 0.85.
4. Require IoU of at least 0.5 between those candidate boxes.
5. Otherwise retain the baseline outcome.

Use scores and geometry only for routing. Labels and family names never choose the path.
Keep HCF primary decisions unchanged. Candidate-only rows remain diagnostic, not the combined policy.
No-focus false selections count as regressions. Baseline abstention is not proof of no focus.

## Execution and decisions

Reuse the agreement compiler, report verification, membership checks, and summary implementation.
The small cascade adapter changes only model routing and the evidence gate.
Compile 1 gate, 8 cached comparisons, and 1 decision report.
The gate verifies the completed agreement result before releasing comparisons.
Each job permits 800 s, 100 MB, and 1 attempt.
The detached runner owns execution. Do not restart it.

Require gains without lost baseline successes or new wrong selections.
Carry earlier crop regressions into the report. Never treat the candidate as a qualified standalone replacement.
If supported, require separate native development groups before consumer qualification.
If contradicted or inconclusive, stop this policy branch. Do not sweep thresholds on inspected cases.
These are post-hoc development comparisons, not held-out accuracy or release evidence.

## Software qualification

Test baseline preservation, optional HCF isolation, and no-focus regression accounting.
Test real cached inputs through an isolated execution queue.
Test invalid upstream evidence and restart duplicate prevention.
Run the focused tests and integrated offline Swift checks before admission.
Keep local admission receipts under `reports/work/CASCADE446`.

All 17 focused tests pass, including isolated positive and invalid-source execution.
The integrated Swift check passes 177 Swift Testing cases and 14 XCTest cases.
The first test exposed a missing gate evidence link. The adapter now supplies that link.
The previous 10 agreement jobs used 4.55 s of worker time, excluding dispatch and approval overhead.
This batch supplies a useful short decision, not overnight capacity. No model improvement is claimed before its results.
All 10 exact jobs are registered and approved. No runner restart occurs.
