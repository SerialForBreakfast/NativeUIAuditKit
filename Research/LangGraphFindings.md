# LangGraph findings and workflow decisions

Owner: Maximum-mini-NUIAK. Updated November 7, 2026.
All findings remain provisional for Joe. No model accuracy or promotion claim follows from these trials.

## Current decision

Keep LangGraph optional. Keep the existing detached runner as the execution owner.
The trials verify durable campaign state and bounded recovery. They do not establish less manual work or better throughput.
Reuse the verified workflow patterns without making LangGraph a prerequisite for model experiments.

The evidence comes from [LANGGRAPH585](LangGraphTrial585Results.md) and [LANGGRAPH586](LangGraphPreparation586Results.md).
Those reports retain their original scope and measurements. This document consolidates their findings.

## Measured observations

| Measure | Existing direct path | LangGraph path | Limit |
|---|---:|---:|---|
| Completed campaign reports | 2 | 2 matching reports | Both paths call the same deterministic report functions. |
| Recovery interventions during successful callbacks | 0 | 0 | No reduction is established. |
| Focus callback time | 1.5 ms | 507.5 ms | One observation; LangGraph includes startup, persistence, and interruption. |
| iOS callback time | 3.2 ms | 232.0 ms | One observation; these values do not define a latency distribution. |
| Additional checkpoint storage | Existing queue records | 69,632 bytes | This measures the retained trial database only. |
| Historical hands-on time | Unavailable | Unavailable | Do not substitute agent elapsed time or queue execution time. |
| Overnight throughput improvement | Unmeasured | Unmeasured | No measured improvement claim. |

The completed queued report jobs take 1.28 s, 0.92 s, and 0.55 s.
These short reports do not supply an overnight workload.
Report agreement verifies orchestration and input binding. It does not independently verify model metrics.

## Verified behavior

- A stable campaign identity persists across immutable observation events.
- A fresh process resumes from the retained checkpoint after deliberate termination.
- A duplicate event preserves the existing report and checkpoint count.
- A missing focus prerequisite does not prevent the separate iOS campaign from reaching review.
- The common preparation command compiles existing diagnostic descriptions and admits exact jobs.
- Partial admission recovery checks existing specifications and approvals before another action.
- Changed inputs, stale events, revoked jobs, and expanded budgets fail validation.
- Runtime changes invalidate approval. Unrelated authoring changes do not invalidate the isolated completion adapter.

LANGGRAPH586 completes 10 jobs covering 2 campaign reviews and a runtime comparison.
Two original terminal audits fail publication. Their failures remain preserved.
Explicit successors repair request validation without repeating capture, training, or inference.
The isolated completion successor produces byte-identical decision and report outputs on the retained iOS inputs.
Independent iOS progress also occurs while a focus audit needs repair.
The existing runner already supports that progress. The trial does not establish LangGraph as its cause.

## Current boundaries

The preparation frontend supports diagnostic artifact jobs within 800 s and 100 MB.
It does not admit capture, training, export, or promotion jobs.
The existing compilers and approval tools continue to handle those operations within their recorded authority.
The controller advances when invoked. It has no producer-arrival watcher or new schedule.
The runner still executes jobs serially. Separate campaign state does not create concurrent hardware execution.

LangGraph checkpoint recovery is separate from training checkpoint restoration.
A saved controller state does not prove exactly-once capture, input delivery, training, or publication.
A producer report does not establish valid labels. A successful job does not establish model acceptance.
Keep unknown labels, profile applicability, and missing coverage explicit.

The isolated environment contains LangGraph 1.2.20 and SQLite checkpoint support 3.1.3.
The trial lock records 41 packages and wheel hashes.
The model environment has no LangGraph installation. Remote tracing stays disabled.
The trials create no model-provider calls, service, or schedule.

## Patterns to retain in NUIAK

| Pattern | Concrete use | Required boundary |
|---|---|---|
| Explicit states and prerequisites | Name which data product waits, its owner, and the exact release evidence. | Missing profile evidence blocks affected training, not independent iOS work. |
| Immutable specifications and successors | Keep a failed attempt and bind a tested correction to a new job. | Do not rewrite submitted scientific intent. |
| Durable observation events | Resume a campaign review after process loss. | Recheck source hashes and actual job state before an external action. |
| Recovery after partial admission | Skip exact jobs already registered or approved. | A lost response requires reconciliation, not blind replay. |
| Scoped runtime dependencies | Keep report and trainer execution separate from authoring code. | Preserve selected runtime, data, model, and output checks. |
| Separate review from execution | Keep findings provisional while unrelated approved work continues. | Joe approves accepted metrics and promotion separately. |
| Separate work products | Qualify crops and temporal labels through their own requirements. | Do not require action timing for valid single-frame crops. |

## Lessons from the next real campaigns

IOS588 uses the common preparation command to admit 5 diagnostics on 6 retained screenshots.
Those diagnostics identify low-confidence boxes for the 7 prior losses.
A separate existing compiler admits the geometry-only fit and full retention graph.
The first diagnostic preparation also exposes an internal dependency-hash error.
The tested compiler correction binds each child to the final parent specification.
Checkpoint persistence does not repair a compiler defect.
This shows a reusable diagnostic connection. It does not show automatic training admission through LangGraph.

NATIVE587 exposes 2 different blockers: exporter compatibility and profile applicability.
A tested exporter correction resolves the first blocker. Joe's explicit research decision defines the second scope.
LangGraph does not replace either repair or evidence decision.
The runner also keeps 2 captures queued behind the iOS fit.
That wait comes from serial execution. It is not a campaign-state failure.
NATIVE589 also encounters a conflicting interpretation of training budgets during automatic approval review.
The data checks continue. The model graph waits for an explicit budget decision.
Keep this authority boundary separate from graph recovery and operator-effort measurements.
See [NATIVE587 and IOS588](Plans/NativeAndIOS587588.md) and [NATIVE589](Plans/NativeProfile589.md).

## Next measurement

Observe the existing iOS and focus campaigns. Do not repeat experiments to measure orchestration.
Record each actual preparation command, repair, approval boundary, and repeated intervention.
Record when required producer evidence arrives and when the downstream job becomes ready.
Separate avoidable preparation delay from execution time, busy resources, human review, and missing evidence.
Keep unavailable hands-on minutes unavailable.

Use identical source receipts, requirements, branch rules, and queue APIs for both controller paths.
Compare independent progress, duplicate actions, rejected stale inputs, operator interventions, and recovery effort.
Require measured lower manual effort or shorter avoidable delay before broader adoption.
If the direct path provides the same result with less maintenance, keep it as the default.
Keep the optional controller only where durable campaign state provides demonstrated value.

Private configurations, journals, database state, and raw receipts remain in the ignored work folders.
A fresh checkout might not contain those artifacts. Public reports do not imply their distribution.
