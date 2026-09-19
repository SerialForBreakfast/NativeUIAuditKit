---
name: nativeui-worker-execution
description: Execute or review an assigned NativeUIAuditKit implementation packet with bounded scope, evidence-based handoff, and project-specific learning capture. Use for packet work, not general status questions or unassigned training/hardware operations.
---

# NativeUIAuditKit packet execution

Read [WorkerWorkflow.md](../WorkerWorkflow.md), resolve your assigned packet through the [ImplementationPlans.md catalog](../ImplementationPlans.md), and read only its canonical contract and named knowledge/context. Do not load every packet document. AGENTS.md's mandatory reading and safety rules still apply. This skill lives under Research so its canonical source can be maintained without modifying the protected `.agents` directory; AGENTS.md explicitly routes workers here.

1. Establish the assignment's authorization, dependencies, and current Tasks.md state. Inspect read-only git status/diff and preserve unrelated changes. Do not assume another worker's plan status proves its artifacts exist.
2. Record ownership of the packet. If an overlapping file is owned by another active worker, coordinate through the architect before editing it. Do not spawn workers implicitly.
3. Follow the packet's file scope and acceptance criteria. Record research decisions before implementation. Use the existing model/navigation skills only when their operations are actually in scope.
4. Before execution, check outputs and caches stay in-project, input corpora remain unmodified, and the command does not introduce network, hardware, or training activity beyond assignment. An option called dry-run is not evidence of read-only behavior: K-02 applies.
5. Validate the actual behavior, record acceptance evidence, and prepare `reports/work/<packet-id>/handoff.md` using the workflow's handoff format. Mark review or blocked, never accepted.
6. Add confirmed non-obvious learnings to BestPractices.md; put unresolved contradictions in WorkerKnowledge.md. Give the architect the evidence path and the next actionable decision.

Revision-4 packets are independently acceptable; do not reintroduce combined parent-packet full-data prerequisites. Hand off to `reports/work/<packet-id>/handoff.md` and report software verified, data eligible, integration qualified, and model gate passed separately with pass/fail/not-run/not-applicable evidence. Synthetic evidence can complete software; it cannot qualify live data or a model. External workers use their own authorized evidence location. Read IterationRoadmap.md only when resolving dependencies or cross-project contract changes.

For review assignments, inspect the diff and evidence against the packet; do not implement unrelated fixes. Return concrete findings with file/symbol, effect, and required correction. Passing synthetic tests must never be reported as live harvest compatibility or a production model gate.
