# <packet ID>: <one reviewable outcome>

Parent task: <Tasks.md ID>. Plan revision/date: <value>. Execution state/owner: Tasks.md.
Owning repository: <value>. Canonical catalog link: <ImplementationPlans entry>.

## Assignment contract

- Outcome and why now:
- Dependencies and evidence required to start:
- Slice boundary: software / real-data integration / live qualification; which reviewed interface is sufficient instead of a whole upstream feature:
- In scope / explicit non-goals:
- Allowed implementation files and additive outputs:
- Authorized operations (local edits, tests, inference, smoke run):
- Coordination: worker update at `reports/work/<packet-id>/coordination.md`; designated publisher per AGENTS.md; relevant peer requests/device needs (not authorization):
- Relevant Research sections, skill paths, BP and knowledge IDs:
- Known current behavior, verified from <source/date>:

## Implementation decisions

Specify interfaces, schemas, compatibility, error behavior, invariants, and deterministic selection rules that matter. Label unresolved choices and the work they block. Give ordered steps; distinguish commands that already exist from interfaces to implement. Do not include unsafe copy/paste commands or guessed flags.

## Acceptance evidence

| Criterion | Verification | Expected artifact/result |
|---|---|---|
| <observable behavior> | <meaningful test or inspection> | <path/result> |

Include required repository checks, output/cache locations, treatment of absent data, and preservation of existing artifacts. Define the stop condition and exact escalation target for materially new authority or architecture.

Declare expected outcome coverage for software verified / data eligible / integration qualified /
model gate passed. Use pass/fail/not-run/not-applicable only when evidence supports it; a plan
records intended coverage, not a pass. Define the next independently useful assignment.

Keep software acceptance separate from real-data/model gates. State what synthetic fixtures prove, what remains unverified, and the next independently useful slice. For cross-project changes, record source revision, support range, compatibility examples and who owns each side; a proposal is not bilateral agreement.

## Handoff

Use Research/WorkerWorkflow.md's evidence format at `reports/work/<packet-id>/handoff.md`. Record deviations, blockers, learnings, and next action. Worker marks review; architect accepts after evidence review.

Include the coordination update path and truthful publication state. Follow AGENTS.md's
start/change/handoff cadence and single-publisher rule; workers do not overwrite shared
repository status. An unavailable share does not block independent offline work.
