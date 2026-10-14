# Background experiments and research review

> Historical research record. Results retain their stated scope and limits.
> Host names are public aliases. Local evidence and execution records remain private.
> This publication does not revalidate earlier results or approve a model.

Owner: research-host-NUIAK. Maintainer request: 2026-10-12.

## Boundary

The chat defines hypotheses, prepares inputs, analyzes results, and selects future experiments.
The existing background runner executes fixed jobs without an active chat turn.
The dashboard controls execution. Tasks.md remains the sole work queue.
Do not create another scheduler or an automatic promotion loop.

## Ready batch

Five jobs use 64 fixed cases and FOCUS329 weights.
Membership contains 16 native directed pairs, 32 authored neighbor pairs, and 16 retained content negatives.
Related cases are not independent final evaluation. No data role changes.

| Priority | Question | Decision supported |
|---|---|---|
| 01-branches | Which branch suppresses native changes? | Exact whole-frame and detail logit contributions identify the next branch investigation. |
| 02-detail-size | Do 16, 24, 32, or 48 px windows expose the thin effect? | Compare gains and lost successes with fixed centers and original pixels. |
| 03-context | What changes when whole-frame motion disappears but detail remains fixed? | Measure dependence on context. This is not a deployable accuracy claim. |
| 04-detail | What changes when detail motion disappears but context remains fixed? | Measure dependence on detail. Do not train from this intervention. |
| 05-features | Do native and authored activations differ before scalar compression? | Compare norms and nearest examples. Distance alone does not prove generalization. |

Use immutable IDs prefixed with `focus344-` and the priority above.
Numeric prefixes match the queue's existing lexical execution order.
Each job has 800 s, 100 MB, one attempt, and 2 CPU threads.
The runner uses existing images. It does not control the Simulator, download files, train, or promote models.
Original crops and production behavior remain unchanged.

## Replenishment

Keep 5 to 10 useful ready jobs when qualified inputs support distinct questions.
Do not inflate the count by splitting one measurement into many jobs.
Keep conditional experiments in Tasks.md until their inputs and hypotheses qualify.
Do not repeat completed jobs or silently retry failures to keep hardware busy.

At each research review:

1. Read results and failures from the previous batch.
2. Compare gains, lost successes, false changes, missed changes, and abstentions.
3. Resolve input problems before defining another run.
4. Register the next fixed batch with exact inputs and acceptance rules.
5. Refresh the runner's approved job set once. Confirm execution starts.
6. End the chat turn. The runner does not need chat polling.

Automatic mode freezes registered IDs when it starts.
New jobs require a refresh after review. Peer proposals do not enter execution automatically.
Completed attempts remain immutable. Stop controls remain available.
An empty ready queue is acceptable when results require analysis or evidence is missing.

## Conditional next batch

If detail size helps without losses, test that change against all retained previous-success sets.
If context suppresses native effects, compare feature contributions before selecting a correction.
If neither helps, prioritize matched native size and aspect-ratio captures.
Training requires a justified hypothesis and fixed budget. Do not launch another generic fit.
Upcoming LUMA tests remain separate from this ready batch.

## First background result

All 5 jobs complete through the detached dashboard runner.
The native movement examples receive negative whole-frame logits between approximately -9.94 and -13.98.
The detail correction adds approximately 1.81 to 4.99, which does not overcome that suppression.
These branch values are contributions, not separately calibrated probabilities.
The 16, 24, and 48 px windows recover no native movement decisions.
They lose 8, 4, and 4 authored movement successes respectively. Reject a crop-size correction from this evidence.
The original 32 px crop reproduces baseline predictions within 1e-6.

Next priority: compare native and authored branch contributions across the larger retained corpus.
Then test a correction only if training-only evidence supports it.
Do not choose coefficients from these inspected native development cases.
The runner waits safely after this finite batch. It does not manufacture more work.

## Second ready batch

The first results justify broader training-only branch measurements before a correction.
Jobs 06–10 separately cover movement, artwork-only changes, identical frames, matched content changes, and reversed movement.
Each job records exact whole-frame and detail contributions, probabilities, labels, and groups.
The jobs use the complete retained membership for their condition, with batches of 8 images.
They preserve source images and model weights. Reversed examples retain their original group.
The same 800 s, 100 MB, and single-attempt limits apply.
Review the group conflicts after completion. Do not automatically fit coefficients or select thresholds.

## Verification

Seven focused tests pass. The offline Swift build and 187 serial Swift tests pass.
The first 5 jobs complete through the actual detached runner, not an inline chat loop.
The dashboard accepts the second batch through its authenticated local controls.
The model workflow skill preserves model identities, original preprocessing, and data roles.
