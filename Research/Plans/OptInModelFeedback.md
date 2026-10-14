# Optional model feedback — implementation plan

Decision: [ADR-0024](../ADR-0024-Opt-In-Model-Feedback.md). Tasks.md remains the sole queue.
Use existing observer and feedback tools. Check TTR's current implementation before assigning duplicate work.

## FEEDBACK298-A — Confirm existing features and freeze the contract

Owners: Maximum-mini-NUIAK review; Sillycon-TTR source inventory.
Inputs: existing transition observer, feedback validator, CLI receipts, ADR-0024, and TTR's exact source references.
Identify current capture hooks, consent controls, local retention, result schemas, and missing features.
Define a versioned case schema and sampling policy. Keep detector, focus, transition, and settling tasks distinct.
Test valid records, missing evidence, unknown versions, model mismatch, sensitive fields, and conflicting labels.
Acceptance: both owners identify reused code, exact gaps, label authority, and pilot limits.
Next: implement only the agreed adapter gaps. No capture or remote service starts during contract review.

## FEEDBACK298-B — NUIAK review and ranking

Owner: Maximum-mini-NUIAK. BigDog-NUIAK can score an exact immutable batch after dispatch.
Inputs: accepted contract and synthetic test fixtures, followed by approved retained cases.
Extend existing feedback intake with selection reasons, denominators, related groups, review states, and exclusion reasons.
Cache scores by exact model/input/settings identity. Keep model consensus separate from reviewed correctness.
Rank supported categories by severity, frequency, uncertainty, and missing coverage. Preserve random audit samples separately.
Test duplicate and cross-role groups, interrupted intake, uncertain labels, absent predictions, and inconsistent counts.
Acceptance: one reproducible report identifies useful failures without automatically relabeling or admitting data.
Next: return exact case IDs and bounded generation proposals to TTR.

## FEEDBACK298-C — TTR opt-in capture adapter

Owner: Sillycon-TTR under its own assignment. Maximum-mini-TTR later validates its local build.
Inputs: agreed case contract, current TTR hooks, approved application scope, and bounded session limits.
Implement only missing off/local/review/transfer modes. Preserve existing navigation policy.
Add bounded queues, explicit model identity, consent checks, privacy review, deterministic sampling, and exact transfer manifests.
Test missing model, full queue, revoked consent, unavailable folder, offline operation, and duplicate delivery.
Acceptance: off mode creates no extra scoring or retention; active mode respects limits and reports every dropped case.
Next: request one explicit bounded real-app collection window if existing authority does not cover it.

## FEEDBACK298-D — One complete improvement cycle

Owners: TTR collection; NUIAK admission and comparison; BigDog-NUIAK assigned batch scoring.
Inputs: reviewed case pack, frozen roles, exact baseline artifact, and approved training contract.
Review selected failures and random samples. Select one supported failure category and qualified targeted examples.
Train one bounded candidate only after admission. Preserve old successes and separate reserved groups.
Acceptance: exact receipts, case-linked results, throughput measurements, and an evidence-backed model decision.
Stop on uncertain labels or missing consent. Continue software work that does not need those cases.
No navigation authority or production replacement follows from a successful transfer or parser check.
