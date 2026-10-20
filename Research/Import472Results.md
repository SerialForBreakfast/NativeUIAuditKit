# Native interruption review — IMPORT472

## Decision

Accept the supplied revision 2 records for scoped evidence review.
Do not admit these records for training or class accuracy evaluation.
Standard, iOS, shipped models, and previous successes remain unchanged.

The importer preserves 12 capture events, 7 image hashes, and 1 layout group.
It verifies image hashes, sidecar hashes, dimensions, geometry, scope, and observed focus consistency.
Repeated image bytes do not remove capture events.
Unknown underlay focus remains unknown.

## Class review

The producer declares 27 `primaryButton` objects and 9 `label` objects.
Another 9 objects have no declared taxonomy class.
These counts describe observations, not independent controls.

The records lack independent class review and capture profile evidence.
The importer therefore withholds every canonical class label.
In particular, a declared `label` on artwork does not establish that class.
Overlay geometry roles do not establish detector classes.

Further class evaluation needs reviewed control identities and canonical class mappings.
It does not need another coordinate clarification or repeated capture.
Unknown profiles cannot enter Standard/HCF comparisons.
The original capture brackets remain unavailable for independent verification.

## Verification

The separate importer does not change the existing training importer.
Unit tests cover valid input and 12 rejected mutations.
Additional tests reject changed file hashes and duplicate event identities.
An isolated queue completes the positive import.
The same queue rejects an unsupported configuration with `review_config`.
The failed attempt remains available.

This is consumer conversion evidence, not independent confirmation of native runtime behavior.
Sillycon-TTR separately reports a successful native interruption trial.
Maximum-mini-NUIAK verifies the received metadata hashes, not the untransferred runtime session.

## Next decisions

- Complete CROP471 full-screen comparisons before another crop training run.
- Keep known-box results separate from detector-proposal results.
- Admit another seed only after Standard gains preserve prior successes.
- Use interruption records for scoped review, not known-no-focus negatives.
- Keep missing class and profile evidence explicit in follow-up tasks.

## CROP471 retained results

Training completes in 1,217 s, about 20.3 min.
Measured crop training increases correct known-box selections from 65 to 68 among 68 focused Standard observations.
All 4 Standard no-focus abstentions remain correct.
HCF shows the same known-box counts.
Neither profile loses a previous success or adds a wrong selection in this retained comparison.

This improvement does not establish full-screen accuracy.
The older Standard ring proposals still miss all 68 focused observations.
The retained consumer comparison also remains unchanged.
The initial decision is therefore inconclusive.
The newly registered comparisons use DETECTOR469R proposals to test the relevant complete path.

A second seed remains conditional on useful Standard gains from that path.
Its proposed limit remains 30 epochs, 1,800 s, 2 GiB, and 1 attempt.
Do not count this conditional run as ready overnight work.

The controls report now completes.
With fixed detector proposals, Standard correct selections increase from 23 to 24 among 24 focused observations.
All 3 no-focus abstentions remain correct. This slice loses no successes and adds no wrong selections.
The report still rejects replacement because the declared prior row and tab failures remain unresolved.
Position and robustness decisions remain pending.
Do not remove those failure gates because the controls slice improves.
