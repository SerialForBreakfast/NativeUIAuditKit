# Cross-machine status alignment — 2026-09-19

Observed local UTC: 19:51:08Z during inspection. NUA HEAD:
`4f36b5ffcdc51feff77f7dc8a558bef51902aed8`; working tree contains ongoing worker
changes. This is status reconciliation, not code review or acceptance. No tests,
hardware, inference, or training were run.

## Repository evidence

Queue and handoffs agree that H1, P0-A, P1-A, P2-A, P3-A, P4-A, P4-B, P5-A, and FR-A
are review-ready. Handoffs are under `reports/work/<packet>/handoff.md`, with
P0-A at `reports/work/P0/handoff.md` and P4-B/P2-A sharing
`reports/work/P4-B-P2-A/handoff.md`. Reported test passes are worker evidence,
not independently rerun/accepted results. P0-A still defers per-label hashes;
no original test pixels were recovered. Real-data and model gates remain open.

Removed the stale duplicate P2-A draft row in Tasks.md. Existing worker edits
and review rows were preserved. Next immediate work is evidence review and
producer-contract reconciliation; independent ready options include R-A,
BADGE-A specification, DOC-A permitted docs, and HIST-A assessment only.

FR-A's review-ready row and handoff arrived during this inspection and were included
on recheck. Its reported software pass is also awaiting independent acceptance.

## Shared communication

TVTestRig's 19:47:02Z snapshot (expires 20:17:02Z) acknowledges receipt of
`nuiak-coordination-001` at 19:25:44Z for NUA's 19:14:44Z snapshot. That proves
historical two-way file visibility, not receipt of this new publication.
NUA acknowledges reading the current TVTestRig snapshot and both request IDs:

- `tvtestrig-20260919T192544Z-visibility-01`: received; the exact older TVTestRig
  snapshot is not independently retained here, so acknowledgment names the current one.
- `tvtestrig-20260919T194702Z-source-policy`: received as a reported contract change,
  not execution authority or consumer-policy acceptance.

TVTestRig reports revision `d44aadca93cda76f2d6a558b05d30dcdc51c6535` plus dirty
changes, non-attested default harvest, additive `sourceDescription`, offline
consumer checks passed, and full host checking in progress. These are peer reports;
the remote checkout and tests were not inspected or rerun. Producer evidence paths
refer to Sillycon, not this machine's potentially different TVTestRig checkout.

## Contract mismatch requiring review

NUA H1 is pinned to older producer revision
`586050e043bddd742c701963650e2fc5815afe36`. Remaining attestation-dependent
requirements occur in Tasks.md (INTEGRATION-01, 6a-10, TV-I1),
Research/TVTestRigIntegrationContract.md (P4-L), and
Research/schemas/harvest-compatibility-v1.md. The inspected consumer validator
always returns `eligibleForTraining: false` and `identityEvidence: None`; it
does not yet establish a path from the new reported-source contract to eligible
real data. Do not describe the producer as still waiting for identity implementation
based solely on the older NUA plan. Equally, do not upgrade descriptive metadata
to attested provenance or training approval.

Next: obtain/review the exact revised producer contract and compatibility sample,
confirm the intended NUA eligibility policy with the maintainer, then amend the
affected contracts and tests as a bounded assignment. No automatic code changes
or prerequisite removals are authorized by an incoming mailbox request.

## Freshness and packet discrepancies

Existing worker entries are preserved, not silently refreshed by this reconciliation:

- P3-A is timestamped 20:12:00Z and P5-A 20:02:00Z, ahead of observed local time.
  Their current freshness cannot be established; owners should use measured UTC.
- P4-A uses `integration_qualified: not_yet`, outside the shared vocabulary;
  the evidence supports not assessed/blocked, not a passed integration.
- P3-A's next P4-B, P5-A's next P3-A, and P4-A's next P5-A are stale recommendations;
  all those packets now have review-ready evidence. Do not redispatch them.

No device occupancy was verified; no reservations exist in the observed status
snapshots. Empty reservations do not establish availability. Peer files and
worker-owned packet entries were not modified.
