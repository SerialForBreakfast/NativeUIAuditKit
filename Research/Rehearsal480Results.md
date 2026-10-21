# REHEARSAL480 — Matched iOS rehearsal

Date: 2026-10-20. Owner: Maximum-mini-NUIAK.

## Diagnostic findings

All 12 IOS479R class-agnostic diagnostics complete and their output hashes verify.

| Candidate | Class-aware gains | Class-aware losses | Class-agnostic gains | Class-agnostic losses |
|---|---:|---:|---:|---:|
| Native controls | 13 | 69 | 11 | 73 |
| Native toggles | 8 | 316 | 11 | 299 |

Class-agnostic matching changes assignment among competing boxes. Its counts do not directly subtract from class-aware counts.
The losses remain large without class matching. Wrong class names alone do not explain the regression.
The controls candidate has 93 mislocalized and 159 missed labels under class-agnostic matching.
The toggles candidate has 286 mislocalized and 192 missed labels under the same matching rule.
These totals describe all candidate failures, not only lost successes.
Neither candidate replaces Run013. These are development observations, not independent release evidence.

## Controlled comparison

The control uses 64 original training images from 64 recorded family/seed groups.
The mixed arm shares 48 images and replaces 16 with qualified native controls images.
Original selection uses family round-robin and image-ID hash order. It does not use evaluation scores.
The preparation excludes 12 records with repaired content, invalid geometry, or empty labels.
Original image, label, and decoded-pixel hashes verify. Evaluation groups and pixels remain excluded.
Both memberships pass the actual trainer preparation function with 64 training frames and no calibration frames.
This small positive-example subset does not establish full-corpus preservation.

Both fits use Run013 initialization, 30 epochs, fixed-last selection, and unchanged resident training settings.
Each fit permits 1,800 s, 2 GiB, and 1 attempt.
Checkpoint retention keeps last, best, and final weights.
The native-only comparison remains secondary because its training volume differs.

## Executable graph

All 31 specifications pass admission and receive exact approvals in transactions of at most 10 jobs.

- 2 training jobs.
- 12 retained scoring jobs.
- 2 candidate decisions.
- 12 conditional class-agnostic diagnostics after regression.
- 2 cached matched-comparison jobs.
- 1 combined decision report.

The combined report compares the mixed arm with the matched control, native-only candidate, and Run013.
It checks all 6 retained conditions and rejects missing or duplicate reports.
Any lost Run013 success prevents replacement. No branch promotes a model or starts another fit.
The detached runner starts `ios480-control-train` without a restart.
The mixed arm remains approved behind it. These are 2 fits, not 31 independent experiments.
The fits reserve at most 60 min combined. Their new runtime remains unmeasured.
The previous 16-frame fit takes 165.77 s. This does not establish runtime for the larger sets.
Multi-day ready capacity remains unmet.

## Verification

All 16 focused tests pass.
The report caller reproduces 18 cached identity comparisons with no changed detections.
The aggregate rejects duplicate child reports.
Earlier offline Swift build and 177-test evidence remain applicable because no Swift source changes in this tranche.
No training starts from chat. Standard behavior and shipped models remain unchanged.

## Separate remaining blocker

`report479-review-nofocus` fails with `controls_version`.
Its final admission call uses a controls-only validator for a no-focus tier capture.
Maximum-mini-NUIAK must select the compatible development validator and test unknown-focus refusal.
Preserve the failed attempt, original frames, and successful restoration. Do not recapture.
This repair releases 8 native comparisons. It does not block iOS training.

Detailed specifications, qualification records, and approval receipts remain under `reports/work/REHEARSAL480/`.
