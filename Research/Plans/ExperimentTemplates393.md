# TEMPLATE393 — reusable tasks through HCF completion

Owner: research-host-NUIAK.
Priority: High. Improve preparation as part of HCF delivery; preserve Standard NUIAK and existing execution.
Decision: [ADR-0028](../ADR-0028-Reusable-Experiment-Templates.md).
This plan defines implementation work. It does not claim these templates are ready.
Tasks.md owns status. HCF389 remains the delivery plan; this work supplies its reusable implementation.

[ADR-0029](../ADR-0029-Workflow-Tools-Versus-Templates.md) compares existing workflow tools separately.
Its installation and benchmark requirements do not block this plan.
Adopt explicit dependencies, frozen configurations, verified caches, and clear recovery boundaries without waiting for framework selection.

## Work packages

| Task | Scope and dependencies | Acceptance | Next action |
| --- | --- | --- | --- |
| T393-01 | Extract T07/T08 contracts from one working retained comparison | Explicit inputs, settings, output schema, limits, and test fixtures; no invented executor | Implement the preparation command |
| T393-02 | Add registry, description validation, dry run, and registration journal | Two comparisons register through one template without custom Python; duplicates and interruption preserve identities | Qualify actual queue execution |
| T393-03 | Execute bounded template checks through an isolated queue | Actual worker results match the existing method; missing inputs fail clearly; completed outputs survive restart | Prepare approved real successors |
| T393-04 | Wrap T01/T02/T09 and HCF389 retained evidence | Resolve candidate and membership without repeated training; preserve original failed attempts | Prepare export and coverage branches |
| T393-05 | Add T10/T11/T12 and explicit queue export support | Offline conversion, actual Vision parity, and measured runtime receipts pass; tests reject unsupported architectures | Prepare delivery or diagnose conversion |
| T393-06 | Wrap T03/T04/T05 around qualified TTR tools | One bounded native shard has OS state, observed labels, data roles, geometry, and restoration evidence | Prepare only missing coverage |
| T393-07 | Wrap T06 crop and detector trainers | Fixed initialization and budgets; interrupted resume matches declared tolerances; previous successes appear in comparison | Train only justified successor candidates |
| T393-08 | Complete T08 audit and T13/T14 delivery variants | Frozen audit stays separate; optional package has hashes and rollback; real TTR receipt verifies inference | Close HCF389 or report exact unmet gate |
| T393-09 | Measure shared preparation and batch reuse | Matched outputs, repeated timings, bounded memory; report savings and setup cost without invented speed claims | Adopt measured improvements |
| T393-10 | Add version evolution and maintenance checks | Changed defaults create new versions; old submitted jobs remain valid; capability changes name affected branches | Reuse templates for Standard experiments |

## Implementation boundaries

T393-01 through T393-03 form the first spike. A simple retained comparison supplies useful evidence without new capture or training.
T393-04 and T393-05 supply the shortest route toward the existing HCF candidate's Core ML trial.
T393-06 supplies coverage in parallel when the target is qualified. It does not block export preparation.
T393-07 does not require retraining a candidate whose completed evidence already answers the question.
T393-09 first measures existing preparation. Persistent workers remain conditional on isolation tests and measured benefit.
Use current HCF389 budgets and aggregate study limits. Template implementation does not reset them.
Before implementation, estimate each selected package from its actual code and test requirements.
No reliable implementation duration is established by this planning document.

## HCF389 mapping

| Existing work | Templates | Implementation tasks |
| --- | --- | --- |
| HCF389-01 candidate | T01, T08, T09 | T393-01 through T393-04 |
| HCF389-02 adapters | T10, T11 | T393-05 |
| HCF389-03 proposals | T07, T08 | T393-01 through T393-04 |
| HCF389-04 coverage | T01, T02 | T393-04 |
| HCF389-05 capture | T03, T04, T05 | T393-06 |
| HCF389-06 methods | T07, T08; T06 only if justified | T393-03, T393-07 |
| HCF389-07 export | T09, T10 | T393-05 |
| HCF389-08 parity | T11 | T393-05 |
| HCF389-09 runtime | T12 | T393-05 |
| HCF389-10 audit | T08 with frozen-audit role | T393-08 |
| HCF389-11 package | T13 | T393-08 |
| HCF389-12 TTR verification | T14 | T393-08 |

## Definition of done

- A short validated description produces jobs through the existing queue.
- A second experiment reuses the template without another custom harness.
- The queue checks requirements before dispatch and identifies the responsible owner for each blocker.
- Job results distinguish execution, evidence validity, and model acceptance.
- Completed steps resume safely without duplicate execution or hidden retries.
- Reports show scientific results and measured workflow costs.
- All HCF389 delivery steps have tested adapters or explicit remaining requirements.
- TTR verifies an optional experimental package before HCF389 closes successfully.
- Standard NUIAK remains unchanged, and HCF adds no navigation authority.

Run focused adapter and queue tests during implementation. Run the required offline Swift checks after integrated code changes.
Planning verification requires link, content, and diff checks only.
