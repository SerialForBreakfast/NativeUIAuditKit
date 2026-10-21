# GROOM476 — Separate obsolete attempts from actionable blockers

## Decision

The blocked count does not represent distinct research problems.
It includes failed historical attempts, dependency waits, and conditional branches that correctly do not run.
Maximum-mini-NUIAK must fix these categories separately.

## Verified cleanup

The initial snapshot contains 318 blocked entries and 69 exhausted entries.
It also contains 209 entries already marked superseded.
The review verifies 214 successor relationships against completed receipts and retained outputs.
Some relationships overlap earlier cleanup.
The net change removes 106 additional entries from the active blocked or exhausted view.
After reconciliation, the snapshot contains 225 blocked, 56 exhausted, and 315 superseded entries.

No attempt, checkpoint, receipt, or job specification is deleted.
The dashboard uses its existing reconciliation reader.
The runner and active worker sources remain unchanged.

Evidence remains in `reports/work/GROOM476/`.
Published mappings are `Experiments/reconciliation-groom476.json` and `Experiments/reconciliation-groom476-extra.json`.
Counts describe the reviewed snapshot, not a continuous status feed.

## Completed questions

CROP474 completes 82 jobs.
Its 6 remaining success-branch jobs correctly do not run.
Seed 372 loses the retained Standard consumer success `stingray-catalog-breadthfirst-1-ref-6`.
Its margin changes from 0.14965119 for the original control to -0.70985048.
The seed-371 margin is 0.14506617.
Reject seed 372 as a replacement. Do not repeat training solely to fill capacity.

NIGHTLY475 completes all 6 iOS geometry reports.
Of 165 residual class-agnostic misses, 103 have heights of 32–128 pixels and widths below half the screen.
This identifies a useful repair stratum. It does not qualify training labels or establish release accuracy.
B405-255 records this supported diagnostic result.

## Next actions by priority

| Priority | Owner | Missing requirement | Work affected | Acceptance |
|---|---|---|---|---|
| P0 | Maximum-mini-NUIAK | Fresh binding and restoration gate for the reserved native capture recipes | The tier chain contains 48 entries | Create immutable successors using the qualified TTR build, current storage checks, and preserved groups. Admit captures only after restoration passes. |
| P0 | Maximum-mini-NUIAK | Reviewed training membership for the measured iOS failure stratum | Independent iOS detector corrections | Keep inspected development cases excluded. Verify classes, groups, and training eligibility before matched training. |
| P1 | Maximum-mini-NUIAK | Consistent presentation of rejected conditional branches | Inflated dashboard counts | Show branches that were not selected separately from repairable blockers. Preserve execution receipts and dependency semantics. |
| P1 | Maximum-mini-NUIAK | Verified links for remaining older native and low-dose chains | Historical entries still in the active view | Hide only entries with independently verified replacements or explicit research closure. |
| P2 | Maximum-mini-NUIAK | Qualified checkpoint resume or a measured successor budget | Optional HCF profile training | Preserve the interrupted 26-epoch attempt. Do not describe it as completed 30-epoch training. |

## Queue limits

The runner is healthy but idle at the observed check.
This cleanup creates no executable work by itself.
No new job receives approval during this cleanup.
Native capture preparation and iOS training-label qualification remain the next useful admission work.
Do not bypass either requirement to raise the ready count.

Standard, iOS behavior, previous successes, and shipped models remain unchanged.
HCF remains optional.
