# OS-FOCUS-04 — development-experiment integration

| Outcome | Result |
|---|---|
| Software verified | 63 focused Python tests; offline Swift build and 14 XCTest / 93 Swift Testing tests passed. |
| Data eligible | Retained bytes/crops and membership verified for a development proposal. Execution approval absent; no production admission. |
| Integration qualified | Local assembly and trainer preflight path; no new TTR/runtime qualification. |
| Model gate passed | Not assessed. No inference, training, export or promotion. |

## Delivered

Existing assembly CLI dispatches `focus-development-input-v1` to a strict adapter.
It reconstructs native and retained direct labels, checks receipts and raw/crop
hashes, production crop pixels, split isolation, duplicate dispositions and reviewed
membership. Original partial receipts and v1.4/v1.5 restrictions remain unchanged.

The existing trainer accepts the separate development protocol only through its
explicit experiment interface. It binds maintainer approval to protocol/arm/run
name, enforces the logged-run requirement before model imports, uses frozen
training-only weights, warm weights with fresh optimizer, cooperative compute bound,
and earliest-tie native-validation checkpoint selection. Production preflight
rejects the same protocol. No separate trainer, cropper or public API was added.

Real frozen protocol: **126 training pairs / nine native validation pairs**,
270 samples total. Hash:
`fa1c7cffa8e42aac511353c9ccd99cf091dbf25a05cb3f5deba52e1ac458fca2`.
All 86 distinct reviewed Fixture candidates remain together in training. Four
duplicate pairs, 48 maze pairs and overlapping historical dialog smoke are excluded.
Missing kitchen-sink data remains missing. No independent Fixture evaluation is
available, so a future run can establish learning/retention diagnostics only.

## Acceptance evidence

| Criterion | Evidence |
|---|---|
| Real assembly entrypoint and source reconstruction | `prepare.py`, `assembly.log`, `input.json`, `dataset/focus_dataset_manifest.json` |
| Actual trainer dry-run and production rejection | `preflight.log`, `production-rejection.log`, `execution.json` (expected blocked exit2) |
| Positive approval plumbing without executing models | `test_focus_development_experiment.py`: actual `main()` with deterministic mocks and test-only approval |
| Missing/stale approval, no logged run | New negative tests prove no model import or output creation |
| Changed bytes, prediction labels, geometry, source kind, partitions | New adapter tests plus existing assembly/consumer suites; synthetic evidence only |
| Duplicate/leakage, training-only weights, retained membership | Reused assembly mechanisms, their regressions, and full real assembly |
| Unsupported versions, collision, earliest checkpoint tie | New entrypoint/helper tests; existing unsafe-path tests |
| Offline package checks | `verification.json`, Python and Swift logs; all exit0 |

Focused verification took 2.85s; Swift build0.93s; Swift tests3.52s. Actual assembly
took146.29s. Independent real preflight timing and exact commands are recorded in
`execution.json`; it deliberately revalidates pixels instead of trusting cached
membership. No live capture or external producer wait occurred.

## Scope and continuation

Base revision `11ce83e6829d7845bd95dea8f4fe15cc1f815a6b`; checkout already had extensive
parallel changes. This tranche added the development adapter/tests/schema and report
directory, targeted existing assembly/protocol/preflight/trainer changes, and updated
research/queue links. Existing datasets, models, reports and unrelated edits retained.
No Git writes. Approved host execution was used for existing offline crop helper and
package checks; explicit outputs and caches stayed project-local.

See [launch review](launch-review.md) for exact configuration, read-only command,
approval draft and the sampling caveat (11.11% native / 88.89% Fixture expected mass).
No approval or run ID was fabricated. Next decision: approve this one bounded
development run, or revise the source sampling balance first. A changed balance
must produce a new frozen protocol before authorization. TTR is not a dependency.

Worker-execution guided end-to-end verification; model-workflow guided crop/split
and launch safeguards. Current repository policy and the established isolated
environment take precedence over stale skill Create ML/.venv examples. BP-81 records
the measured sampling lesson. SMB coordination is not applicable: no peer action
changed. This software tranche is complete for review; actual training remains
separately authorized. No background work is implied.
