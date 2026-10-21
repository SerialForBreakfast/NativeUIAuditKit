# STABILITY487 — Standard training stability

## Question

Do retained focus decisions remain stable when only the training seed changes?
Current corpus comparisons use a single Standard control with seed 371.
Small differences need a measured stability baseline before they guide model changes.

## Two independent graphs

Train the full Standard membership with seeds 372 and 373 through the existing training compiler.
Reuse the completed PROFILE425 seed-371 control. Do not repeat that fit or its scoring.
Its output hashes pass verification. Its recorded trainer and factor-adapter hashes match the current sources.

Keep these settings fixed:

- Original Standard membership and all development exclusions.
- Retained initialization, crop preprocessing, and sampling rules.
- Deduplication disabled and repeat 1.
- 30 epochs and fixed-last selection.
- All 17 retained evaluation conditions and previous-success gates.

Each fit permits 1,800 s, 2 GiB, and 1 attempt.
Each graph includes scoring, comparisons, terminal reporting, and conditional decision audits.
Neither graph depends on IOS482, DEDUP486, new captures, or peer delivery.
Different training seeds do not create independent evaluation groups.

## Decisions

If retained cases change across seeds, mark small corpus effects as provisional.
Require matched-seed confirmation before adopting a corpus correction. Do not automatically launch further fits.
If decisions remain stable, use that evidence to interpret the pending corpus comparisons.
Three seeds do not establish statistical certainty or release qualification.
Any lost previous success prevents replacement. Keep shipped models unchanged.

## Duration and remaining preparation

The completed full Standard fit takes 1,719.93 s, or about 28.7 min.
The 2 new fits should add about 57 min plus scoring. Runtime can vary.
This adds useful reserve work but does not establish 8 hours of remaining work.
Do not sum per-job limits or conditional branches as estimated runtime.

The detector's current qualified adapter fixes its learning rate and does not expose a frozen-backbone setting.
The existing REHEARSAL482-RESERVE task covers that missing capability.
Do not use the unqualified novel adapters merely to fill execution time.
The next implementation tranche should qualify one optimization control and connect its full retained comparisons.
Select that control after the mixed-data and larger-coverage reports identify the remaining losses.

## Current result boundary

At this review, IOS482 has 21 completed jobs and still lacks its terminal mixed-data comparison.
DEDUP486 has completed the unique-crop fit. Its exposure fit runs, and retained scoring remains incomplete.
Neither training completion establishes a model improvement.
No shared source, runner setting, Standard behavior, or shipped model changes for this preparation.

Local requests and admission receipts reside under `reports/work/STABILITY487/`.

## Verified admission

Both graphs pass preflight. All 56 jobs receive exact approval in transactions of at most 8 jobs.
The 13 focused compiler tests pass. The documentation diff check passes.
Runner 17481 remains healthy and executes `dedup486-exposure-train` during admission.
Continuous execution remains enabled. No restart occurs.
