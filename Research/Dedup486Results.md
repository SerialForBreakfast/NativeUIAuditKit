# DEDUP486 — Independent Standard exposure comparisons

## Findings that motivate this batch

COVERAGE485 verifies 30 gains and 25 losses for the 128-image iOS control against the 64-image control.
Against Run013, the 128-image control gains 28 detections and loses 30. Neither control replaces Run013.
Mixed-data and larger-coverage comparisons remain pending at this review.

The Standard crop corpus has 8,192 training rows but only 925 distinct RGB pixel hashes.
The pixel check finds no conflicting labels. Unique crops contain 808 positives and 117 negatives.
Some repeated exposure is deliberate family balancing. Duplication is not automatically a data defect.
This independent comparison tests whether that weighting helps or harms retained focus selection.

## Two bounded graphs

Both graphs reuse the completed PROFILE425 Standard control and its 17 retained evaluation conditions.
Both preserve original membership, development rows, initialization, seed 371, and fixed-last selection.

- Unique arm: enable existing pixel deduplication and use repeat 1.
- Exposure arm: enable pixel deduplication and use repeat 9.

Repeat 9 presents 8,325 samples per epoch, versus 8,192 in the control.
This approximates exposure. It does not match optimizer updates exactly.
Deduplication changes family weighting and the trainer's positive-class weight.
Do not attribute any result to duplicate removal alone without these limitations.

Each fit uses 30 epochs, 1,800 s, 2 GiB, and 1 attempt.
Each graph includes retained scoring, comparisons, terminal reporting, and conditional decision audits.
Any lost previous success prevents replacement. No branch promotes a model or launches further training.
If both arms regress, retain the original weighting and stop this branch.
If either arm preserves successes, inspect case-level gains before proposing independent qualification.

## Capacity and safety

These graphs do not depend on IOS482 or new captures.
They use existing adapters without changing pinned source files or restarting the runner.
The completed full-corpus fit takes about 28.7 min.
The new fits should add roughly 30–40 min combined, plus retained scoring. This is an estimate.
The reserve still does not establish a full 8-hour night.
Do not count conditional branches or diagnostic limits as measured runtime.

Standard behavior, shipped models, previous successes, and original evidence remain unchanged.
All local requests, preflight checks, and admission receipts reside under `reports/work/DEDUP486/`.

## Admission verification

Both graphs pass preflight. All 56 jobs receive exact approval through transactions of at most 8 jobs.
The existing runner starts `dedup486-unique-train`. Continuous execution remains enabled with no reported error.
The 13 focused compiler tests pass. The documentation diff check passes.
No shared source file changes. No runner restart occurs.
