# REVIEW488 — Completed comparisons and continuation requirement

## Verified findings

The reviewed terminal reports pass output-hash verification.

| Candidate | Comparison | Gains | Lost successes |
|---|---|---:|---:|
| IOS482 mixed controls | Matched original-data control | 10 | 36 |
| IOS482 mixed controls | Run013 | 16 | 44 |
| IOS483 mixed toggles | Matched original-data control | 30 | 41 |
| IOS483 mixed toggles | Run013 | 27 | 45 |

Neither mixed-data candidate replaces Run013. Do not increase native mixing without a justified correction.
These are inspected development detections, not release accuracy or focus-selection measurements.

DEDUP486 unique-crop training preserves Standard raw and mapped proposal selections but does not improve them.
It loses 1 Standard known-box success. Consumer crops gain 8 successes and lose 3.
Consumer-frame scoring adds 2 wrong selections. Reject replacement.
Optional HCF slices also regress. Do not combine these overlapping slices into one accuracy total.

## Exhaustion is not a model result

DEDUP486 exposure training stops at 1,800.53 s during epoch 17.
The saved checkpoint contains completed epoch 16, optimizer, scheduler, random states, history, and the original contract.
The contract includes repeat 9. Preserve the original attempt and every output.
The maintainer approves up to 30 additional minutes after restoration parity passes.
Keep the original 30-epoch endpoint and 2 GiB output limit.

The existing checkpoint qualification and restoration adapters hard-code repeat 1.
Their prior qualification does not cover this checkpoint. Do not bypass that mismatch or restart training from zero.
The continuation registry also limits each continuation chunk to 800 s.
Implement repeat-aware qualification and bounded continuation chunks before admission.
Preserve original controls, checkpoint identity, cumulative accounting, and regression comparisons.

## Next work

Prioritize the repeat-aware continuation requirement and the existing detector optimization-control task.
Do not add more naive mixed-data fits after these regressions.
The independent reserve and Standard seed graphs remain available to the runner.
At the reviewed snapshot, COVERAGE484 trains; reserve preparation and both seed fits remain pending.
Standard behavior, shipped models, and previous successes remain unchanged.

Evidence resides in the terminal reports for `ios482-matched-decision`, `ios483-matched-decision`, and `dedup486-unique-decision`.
The exhausted checkpoint resides in `dedup486-exposure-train/attempts/1/out/last.pt` under the local queue.
