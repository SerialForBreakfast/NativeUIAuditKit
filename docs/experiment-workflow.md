# Experiment workflow and evidence

## Product boundaries

Standard detection, classification, and focus remain the primary goals.
Keep iOS work independent of tvOS producer availability.
HCF is optional. Experimental results do not change shipped models automatically.

## Define work through reusable batches

1. State the observed failure and the question.
2. Choose an existing template or campaign compiler.
3. Pin inputs, data roles, groups, models, preprocessing, and thresholds.
4. Change one factor against a matched control.
5. Define output checks, resource budgets, and the next decision.
6. Register immutable jobs with explicit dependencies.
7. Approve each exact specification within its authorized scope.
8. Let the detached runner execute the graph.

Use [batch descriptions](experiment-batches/README.md) instead of a new script for each experiment.
Use [research graphs](../Research/Plans/ResearchGraph451.md) for diagnosis, training, scoring, comparison, and reporting.
Missing capabilities need bounded implementation tasks. They are not ready experiments.

## Separate execution from conclusions

| State | Meaning |
| --- | --- |
| Ready | Required inputs and execution checks pass. |
| Dependent | A required producer or comparison has not finished. |
| Blocked | An exact input, capability, or authority is missing. |
| Exhausted | The attempt reaches its budget. Continuation needs a qualified checkpoint and approved limits. |
| Complete | The process finishes and its required outputs pass execution checks. |
| Evidence verified | Review confirms identities, matched conditions, and valid measurements. |
| Model accepted | Separate release and consumer gates pass. Job completion does not establish this state. |

Keep failures and original specifications immutable.
Use explicit successors when a repair changes inputs or execution.
Retire superseded work from the active view only after verified replacements finish.

## Evaluate the complete path

Report known-box classification separately from detector-based focus selection.
Measure missing proposals, class errors, localization, abstentions, and wrong selections.
Preserve no-focus cases and all previous successes.
Keep Standard and HCF results separate.
Do not count repeated frames or paired profiles as independent evidence.

The [DETECTOR469R review](../Research/Detector469RResults.md) shows why improved coverage can still lose focus selections.
The [REVIEW470 comparison](../Research/Review470Results.md) tests a fixed fallback without replacing the baseline.
CROP471 changes training crop geometry while preserving membership and development inputs.
Its result remains pending until matched scoring and regression checks complete.

## Recover without repeating captures

Separate capture failure, restoration failure, retention failure, and receipt publication failure.
If capture succeeds, preserve its original pixels and journal.
Verify restoration independently before publishing a derived recovery receipt.
Use explicit Standard restoration when cleanup requires Standard.
Do not repeat an HCF round trip merely to finish cleanup.
Verify content before storage offload or duplicate consolidation.
Preserve distinct capture events even when their pixels match.

## Admit producer metadata carefully

Declare coordinate origin, units, and box encoding.
Keep control bodies separate from focus decorations and text labels.
Keep requested focus separate from observed focus.
Unknown focus is not no-focus. Covered controls are not unfocused negatives.
Declared classes are not independently reviewed classes.
Partial enumeration cannot establish whole-screen detector completeness.
Unavailable capture profiles cannot enter Standard/HCF comparisons.

The current native interruption revision has verified hashes and geometry.
It still needs an unknown-preserving review adapter and independent class review.
Do not relabel it as an existing admitted training schema.

## Plan useful unattended work

Maintain priority work, independent reserve work, and bounded conditional follow-ups.
Report measured ready duration separately from job count and configured ceilings.
Do not claim overnight capacity from dependent jobs or maximum runtime limits.
Add longer runs only when they answer an unresolved question.
Additional seeds require a promising matched result. Repeated failures need diagnosis, not arbitrary extra epochs.

## Verify changes

Run focused positive and negative tests before committing shared tooling.
Run the offline Swift integration checks after code integration.
Run the local pre-commit and commit-message hooks without bypassing them.
Keep raw captures, credentials, queue receipts, checkpoints, and local coordination records outside public commits.
