---
name: nativeui-worker-execution
description: Complete an assigned NativeUIAuditKit implementation packet or multi-packet tranche through integration, verification, and evidence-backed handoff, or review its deliverables. Use for assigned work, not unassigned training/hardware operations.
---

# NativeUIAuditKit packet execution

Read [WorkerWorkflow.md](../WorkerWorkflow.md), resolve your assigned packet through the [ImplementationPlans.md catalog](../ImplementationPlans.md), and read only its canonical contract and named knowledge/context. Do not load every packet document. AGENTS.md's mandatory reading and safety rules still apply. This skill lives under Research so its canonical source can be maintained without modifying the protected `.agents` directory; AGENTS.md explicitly routes workers here.

1. Establish the full assignment's authorization, dependencies, current Tasks.md state, and completion boundary. For an authorized larger tranche, list included packets and integrated deliverables up front; do not silently reduce scope to a helper. Inspect read-only git status/diff and preserve unrelated changes. Do not assume another worker's plan status proves its artifacts exist.
2. Record ownership of the packet. If an overlapping file is owned by another active worker, coordinate through the architect before editing it. Do not spawn workers implicitly.
3. Follow the packet's file scope and acceptance criteria. Record research decisions before implementation. Use the existing model/navigation skills only when their operations are actually in scope.
4. Before execution, check outputs and caches stay in-project, input corpora remain unmodified, and the command does not introduce network, hardware, or training activity beyond assignment. An option called dry-run is not evidence of read-only behavior: K-02 applies.
5. Implement and wire the real entrypoints required by the contract. Validate actual behavior, inspect failures, repair in-scope defects, and rerun affected checks. Continue across every included packet; a passing helper test is only a checkpoint. Record acceptance evidence and prepare `reports/work/<packet-id>/handoff.md` using the workflow's handoff format. Mark review only when all assigned criteria are evidenced; mark blocked/incomplete otherwise, never accepted.
6. Add confirmed non-obvious learnings to BestPractices.md; put unresolved contradictions in WorkerKnowledge.md. Give the architect the evidence path and the next actionable decision.

Revision-4 packets are independently acceptable; do not reintroduce combined parent-packet full-data prerequisites. Hand off to `reports/work/<packet-id>/handoff.md` and report software verified, data eligible, integration qualified, and model gate passed separately with pass/fail/not-run/not-applicable evidence. Synthetic evidence can complete software; it cannot qualify live data or a model. External workers use their own authorized evidence location. Read IterationRoadmap.md only when resolving dependencies or cross-project contract changes.

For review assignments, inspect the diff and evidence against the packet; do not implement unrelated fixes. Return concrete findings with file/symbol, effect, and required correction. Passing synthetic tests must never be reported as live harvest compatibility or a production model gate.

## Before ending the turn

During iteration, follow [change-scoped verification](../IterationEfficiency.md):
test the changed mechanism first; run required full offline checks at the integrated
code handoff, not after each helper. Preserve evidence for unchanged dependencies.
For producer repairs, seek actual failed-boundary and completed-artifact evidence;
readiness alone is not capture success. This never waives fresh operational safety
checks, final data/model gates, or separate execution authority.

Apply AGENTS.md's execution contract. Check the entire assigned tranche, not only the last
file edited. If any safe, authorized implementation, integration, test, failure repair,
or handoff work remains, do it now. Send commentary for progress and continue working;
do not send a final promise to continue later. A packet reaching review does not stop
other included packets unless their declared dependency actually requires acceptance.

For each remaining criterion, give a concrete blocker and resume condition, or finish it.
Missing real data blocks real qualification, not fixture-based software checks. Missing
SMB access blocks status publication, not local implementation. Genuine authority gaps
stop the affected action; finish other authorized work without broadening scope.

Final handoff states: scope completed for review, or incomplete/blocked with evidence.
Include verification commands/results, the four independent outcomes, and what remains.
User interruption or a real runtime limit is a truthful checkpoint, never a fabricated pass.
