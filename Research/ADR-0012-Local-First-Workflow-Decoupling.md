# ADR-0012: Local-First Workflow Decoupling and Governance Streamlining

- Date: 2026-09-30
- Status: Accepted workflow direction; reconciled by LOCAL-FIRST-01.
- Authority: [AGENTS.md](../AGENTS.md). Queue: [Tasks.md](../Tasks.md).

## Evidence and decision

Repeated peer coordination, storage failures and micro-handoffs interrupted local
work. The records establish friction, not the previously asserted 80–90% overhead.
Existing checks also caught genuine crop geometry and deployment-pixel defects.

1. Build, test, analyze retained data and execute approved model work locally using
   resident dependencies and versioned project-local inputs. Peer acknowledgments,
   network mounts and running TTR are not prerequisites for independent work.
   Missing resident dependencies are explicit prerequisites, not automatic downloads.
2. TTR archives are asynchronous inputs. Producer unavailability blocks only the
   capture/delivery or live-integration slice that needs it. Preserve the verified
   receipt flow; cancelled external-storage work stays cancelled.
3. Native synthetic generation still needs a qualified renderer/Simulator. Offline
   does not mean renderer-free. This ADR grants no standing runtime, capture,
   training, export or promotion authority.
4. Complete coherent assigned tranches end to end. Use one concise handoff with
   linked machine evidence. Tasks.md remains the only execution queue.
5. Remove routine prose-plan hashes, repeated manual per-crop approvals and separate
   helper dossiers. A clear assignment plus a bounded Tasks entry can define work;
   write a canonical plan only when scope or experimental design needs one.
6. Retain automated artifact identities, prediction accounting, label-source,
   split-isolation, geometry/crop and deployment-parity checks at their actual
   boundaries. Review batch exceptions, not every automatically checked rectangle.
   Diagnostic data does not become training-eligible automatically.
7. Run focused checks during edits and required offline Swift build/test at integrated
   code handoff. Prose-only edits need content/link/diff checks, not a build.
   Reuse unchanged evidence with its dependency scope.
8. Share only actionable producer/consumer consequences. Git remains read-only for
   agents; maintainer commits are not an agent acceptance prerequisite.

## Compatibility and limits

This supersedes older requirements for routine prose-plan hashing, helper dossiers
and repeated approval of steps already within an assignment. Historical machine-
enforced seals remain intact until a scoped compatibility change is tested; do not
edit a sealed input to bypass its validator. Data reservations, capture safety and
model gates remain unchanged. No pipeline implementation or model run is authorized
by workflow adoption.

See [WorkerWorkflow](WorkerWorkflow.md), [IterationEfficiency](IterationEfficiency.md)
and the [five-tranche contract](Plans/LocalFirstDelivery.md). Measure useful output
and elapsed work in existing reports rather than claiming an unmeasured speedup.
Asynchronous intake can delay hardware-only findings; live qualification remains required.
