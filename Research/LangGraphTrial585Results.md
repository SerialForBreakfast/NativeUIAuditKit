# LangGraph trial — November 6, 2026

Owner: Maximum-mini-NUIAK. Results remain provisional for Joe.
Protocol: [LANGGRAPH585](Plans/LangGraphTrial585.md).

## Decision

Keep the tested prototype optional. This trial does not justify replacing the existing runner.
The trial establishes durable campaign review states and bounded recovery behavior.
It does not establish less routine manual work.

## Actual campaign connection

The existing detached runner completes `lg585-focus-review`, `lg585-ios-review`, and `lg585-comparison`.
The source campaigns are FOCUS583 and IOS582.
Both report paths agree with the control and reach separate pending-review states.
A pending focus review does not prevent the iOS report from completing.
The runner still executes jobs serially. Separate campaign state prevents a shared review barrier.

Both paths deliberately call the same deterministic report functions.
Agreement tests orchestration and source binding. It does not independently validate model metrics.
The trial repeats no training, capture, or campaign inference.
All model results remain provisional. No model promotion or headline accuracy update occurs.

## Observed measurements

| Measure | Direct report control | LangGraph |
| --- | --- | --- |
| Complete report outputs | 2 | 2 matching outputs |
| Routine recovery interventions during successful callbacks | 0 | 0 |
| Focus report function time | 1.5 ms | 507.5 ms |
| iOS report function time | 3.2 ms | 232.0 ms |
| Additional controller storage | Existing queue artifacts | 69,632 bytes of SQLite state |

These are 2 observations. They do not establish a general latency distribution.
LangGraph timing includes its imports, graph construction, persistence, and review interruption.
The complete queued job times are 1.28 s, 0.92 s, and 0.55 s.
No reduction from 0 interventions to 0 interventions is established.
Historical operator minutes, time saved preparing experiments, and overnight throughput gains remain unmeasured.

## Recovery and independent progress

Generated software records test a missing focus prerequisite while iOS reaches its review state.
A fresh process resumes after deliberate termination at a durable checkpoint.
The termination returns code 86. The resumed and duplicate-event calls return code 0.
The duplicate event preserves the report and the checkpoint count of 4.
These checks establish software behavior only. They do not establish model quality or exactly-once external actions.

The iOS campaign initially has one invalidated decision approval.
An exact optional T96 source change caused that invalidation.
The existing refresh tool verifies unchanged specifications, inputs, settings, and budgets.
It refreshes only that affected approval. The runner then finishes the existing decision graph.
This maintenance is separate from the LangGraph comparison.

## Verification and preservation

- Fourteen controller, authoring, recovery, and runtime-isolation checks pass.
- Twenty-two existing queue and approval checks pass.
- The offline Swift build passes.
- Serial validation passes 14 XCTest checks and 178 Swift Testing checks.
- The first parallel Swift attempt stalls in Vision waits. The serial retry resolves validation without source or service changes.
- All 31 shipped resource files retain identical bytes. Their total size is 21,352,458 bytes.
- The original scientific manifests and source checkpoints retain their hashes.
- The model environment still has no LangGraph installation.

The isolated environment uses LangGraph 1.2.20 and SQLite checkpoint support 3.1.3.
The dependency lock pins 41 packages and their wheel hashes.
Remote tracing stays disabled. The trial makes no model-provider calls and creates no service or schedule.
The runtime closure excludes campaign authoring code.

Preparation and verification take 26.8 min against the 60–120 min estimate.
Retained model outputs and immediate dependency approval reduce the expected waiting time.

## Next priorities

First, remove authoring dependencies from the iOS completion adapter before another large campaign.
This addresses the specific approval invalidation observed in this trial.
Keep runtime input and code checks strict. Preserve original specifications through explicit successors where required.

Then consider one active producer-to-experiment campaign if durable coordination remains a measured bottleneck.
Compare actual preparation interventions and elapsed handoff time against the existing runner.
Continue model experiments through the existing templates while review remains pending.

Private receipts, configurations, measurements, state readback, and validation logs remain in `reports/work/LANGGRAPH585`.
Those local evidence links do not imply that a fresh checkout includes the artifacts.

See [consolidated findings and workflow decisions](LangGraphFindings.md).
