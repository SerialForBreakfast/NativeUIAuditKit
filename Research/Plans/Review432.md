# REVIEW432 — Retained comparisons and recovery gate

Date: 2026-10-18. Owner: Maximum-mini-NUIAK.

## Decision

Do not replace the retained model with the PROFILE425 joint-profile candidate.
It loses a Standard tab success and a retained TTR positive crop.
Keep Standard unchanged. Review the separate Standard-only candidate when its matched results finish.
Do not start another correction before that comparison.

## Completed comparison

The review compares verified outputs on identical inputs, boxes, and thresholds.
The 15 conditions contain 72 inspected frames per profile. Comparison arms reuse these frames.
These are development findings, not held-out accuracy or navigation qualification.

| Profile | Box source | Gained successes | Lost successes | New wrong selections |
| --- | --- | ---: | ---: | ---: |
| Standard | Known boxes | 0 | 1 | 0 |
| Standard | Raw proposals | 0 | 0 | 0 |
| Standard | Mapped proposals | 0 | 0 | 0 |
| HCF | Known boxes | 0 | 1 | 0 |
| HCF | Raw proposals | 1 | 1 | 0 |
| HCF | Mapped proposals | 0 | 0 | 0 |

The known-box losses share group `nctrl417-dev-tab-1`:

- Standard: `nctrl417-dev-tab-1-standard-item-1-0`.
- HCF: `nctrl417-dev-tab-1-hcf-item-1-0`.

The HCF raw-proposal loss is `hcf402-large-controls-hcf-item-0-0`.
The HCF raw-proposal gain is `hcf402-tall-controls-hcf-item-2-0`.
Each loss changes a correct selection into a miss.

## TTR crop comparison

The original crop set reduces false positives from 8 to 4, but reduces true positives from 2 to 1.
The lost positive is `stingray-catalog-breadthfirst-1-ref-6`.
The v5 crop set reduces false positives from 8 to 2 and retains both true positives.
It also reports 1 abstention.
Both sets share 1 inspected scene group, `retained-stingray-catalog-seed83`.
These known-crop results do not measure full-screen selection.

## Pending execution

At this review, Standard-only training runs. Recovery has no attempt yet.
The HCF-only fit exhausted its 1800 s limit. Do not treat it as completed training.
The 6 native drafts remain pending verified restoration.
No new TTR reply appears after coordinator cursor 882.

## Automatic recovery branch

Reuse existing typed graph conditions. Do not add a scheduler or change active worker modules.
The current recovery adapter does not emit a typed graph condition.
T03 also requires a qualified, pinned recipe before compilation.
GATE433 now bridges these gaps without changing existing execution modules.
It verifies recovery, then binds recipes and admits only the 6 named T03 jobs.
Final specification hashes become available after the verified recovery receipt exists.
This is bounded admission, not automatic experiment design or a new scheduler.

The implemented branch has these checks:

1. Verify the completed recovery receipt, Standard restoration, Fixture restoration, closed session, and input identities.
2. Emit a `research-condition-v1` receipt with hashed evidence.
3. Bind only the 6 frozen capture recipes to that verified receipt.
4. Preserve their target, helper, groups, data roles, budgets, and original drafts.
5. Release the approved branch only for a supported condition.
6. Reject missing evidence, failed restoration, inconclusive results, and changed input hashes.
7. Test restart recovery and duplicate delivery without duplicate capture dispatch.

Qualification must use isolated positive and negative queue tests before live admission.
Do not mark pending restoration as successful to prepare jobs early.
Reporting or qualification failure must not stop independent Standard work.

### GATE433 implementation and qualification

Job `native433-admit` is registered and approved behind `native431-recovery`.
Its pinned plan lists exactly 6 drafts and their capture IDs.
The adapter checks the completed producer, all output hashes, Standard restoration, Fixture identity, focus, closed ownership, and screenshot integrity.
It checks the current helper, Fixture binding, and recovery guard before admission.
Existing approval checks independently verify target ownership for each capture.

Only the qualification field changes in each derived recipe. Original drafts remain unchanged.
Every child depends on successful gate completion and its supported typed condition.
Partial admission cannot release a capture before the gate completes.
Repeated identical admission preserves specifications and approval events.
Conflicting IDs and revoked approvals fail. Revoked work is never approved again automatically.

No active module changes occur. The existing runner discovers admitted work on its next cycle.
A stopped runner stays stopped. Failed or interrupted gate attempts require explicit review; they do not retry automatically.
The isolated interruption test resumes admission from identical saved artifacts. It does not qualify arbitrary job resumption.

Validation passes:

- 32 focused recovery, admission, and graph tests pass in 10.581 s.
- Positive and failed restoration cases execute through an isolated queue.
- Duplicate dispatch, partial admission, conflicting IDs, revocation, missing outputs, changed evidence, and disk failure checks pass.
- The offline Swift check passes 177 tests in 25 suites in 56.046 s.

Evidence: `reports/work/GATE433/`. Software checks do not establish successful native restoration or captured data quality.

### Handoff status

Standard-only training completes in 1719.927 s. Its 17 matched comparisons remain pending at handoff.
Training completion alone does not establish improvement. Keep the retained baseline until matched regression results pass.
The runner reports continuous execution enabled, no stop request, and no error.
Recovery remains pending. The approved gate correctly reports `dependency_incomplete:native431-recovery`.
No capture successor runs before that dependency and the restoration checks pass.

## Evidence

Local evidence is in `reports/work/REVIEW432/`:

- `bundle.json`: pinned comparison inputs.
- `review.json`: case-linked selection changes.
- `consumer.json`: TTR crop outcomes and changed cases.

The review reuses completed outputs and existing comparison code. No training repeats occur.
No capture, model promotion, runner restart, or schedule occurs during this review.
