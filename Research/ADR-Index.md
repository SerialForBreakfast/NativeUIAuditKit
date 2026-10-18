# Architecture decisions — review and priorities

Review date: 2026-10-18. Owner: Maximum-mini-NUIAK.
Tasks.md owns execution status. An accepted design does not prove implementation or model qualification.
Standard detection and focus remain primary. HCF remains optional.

## Quick wins

| Priority | Decision | Next useful action |
| --- | --- | --- |
| 1 | [0028: reusable templates](ADR-0028-Reusable-Experiment-Templates.md) | Turn qualified backlog items into descriptions with producer, scoring, and report dependencies. Do not build another harness. |
| 2 | [0027: experiment graphs](ADR-0027-Evidence-Guided-Experiment-Graphs.md) | Use existing typed conditions for fixed scientific decisions. Test each branch before unattended use. |
| 3 | [0011: measured efficiency](ADR-0011-Measured-Training-Efficiency.md) | Measure preparation, execution, and review separately. Report queue duration rather than job count alone. |
| 4 | [0024: optional feedback](ADR-0024-Opt-In-Model-Feedback.md) | Reuse TTR receipts for case-linked failures. Confirm consent and data roles before collecting new examples. |
| 5 | [0014: detection and OCR](ADR-0014-Hierarchical-Detection-and-OCR-Fusion.md) | Separate missing boxes from wrong classes first. Add OCR only where retained errors justify its cost. |

These priorities are recommendations, not claims that all variants are ready.

## Keep, but do not expand now

| Decision | Recommendation and revisit condition |
| --- | --- |
| [0029: workflow tools](ADR-0029-Workflow-Tools-Versus-Templates.md) | Keep the current queue. Revisit migration only after measured maintenance savings justify it. |
| [0015: context and unified focus](ADR-0015-Context-Aware-Focus-Detection.md) | Preserve negative results. Do not repeat the failed context recipe unchanged. A unified detector needs a matched full-screen test. |
| [0016: foundation-model semantics](ADR-0016-Evidence-Bound-Foundation-Model-Semantics.md) | Defer broad integration until detection evidence exposes a specific semantic gap. |
| [0020: prompt-rendered focus](ADR-0020-Procedural-Focus-Rendering-Feasibility.md) | Keep as a stretch proposal. Do not substitute generated effects for native HCF evidence. Do not cancel peer work implicitly. |
| [0022: screen context](ADR-0022-Screen-Context-for-Focus-and-Navigation.md) | Require a measured context failure and qualified labels before implementation. |
| [0019: batch rendering](ADR-0019-Batched-Renderer-and-Asset-Pipeline.md) | Reconcile current TTR capabilities before building anything. Do not start a second renderer from an old proposal. |

## Historical and partially superseded records

See the [archive index](Archive/ADRs/README.md).
Original paths remain stable because existing plans and evidence link to them.
Archive status does not delete results or revoke valid safety requirements.
Do not archive an accepted design merely because its implementation is complete.

## Retained decisions

Keep ADR-0007 through ADR-0010 for focus semantics, native capture, and data diversity.
Keep ADR-0012 and ADR-0013 for local workflow and tool delivery.
Keep ADR-0017 and ADR-0018 for corpus lifecycle and scoped Settings evidence.
Keep ADR-0021, ADR-0023, ADR-0025, and ADR-0026 for qualification, distribution, portability, and queue contracts.
Their implementation status needs separate source and receipt checks before changing any status label.

## Rejected shortcuts

- Do not treat unmeasured speed estimates as established gains.
- Do not migrate frameworks merely because another tool supports graphs or caching.
- Do not repeat rejected context experiments without a changed hypothesis.
- Do not replace native evidence with synthetic placeholders.
- Do not add larger architectures before separating proposal, classification, and data errors.

No ADR is rejected solely because it is old. Rejection requires a scoped reason and preserved evidence.
