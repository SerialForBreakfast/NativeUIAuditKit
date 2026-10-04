# Grouped generation workflow — 2026-10-03

SYNTH-01/02/05/06, [G1–G5 plan](../Plans/2026-10-03-grouped-campaign-workflow.md).
Producer workflow implemented and locally qualified. Consumer source uptake and
training admission remain separate. No NUIAK binary, Git write, physical operation,
settings change, restart or release package.

## Implementation and acceptance

- **G1:** `Scripts/plan-campaign-packets.rb` and `lib/campaign-packets.rb` prepare
  compatible packets offline, preserve exact input hashes and case/split identities,
  and require an explicit aggregate budget. Environment values are declarations;
  they are never advertised as observed runtime truth. Negative checks cover
  mismatched environment/target/contracts, duplicate identities, empty packets,
  insufficient budgets and nontransition reuse.
- **G2:** optional manifest `packets` uniquely partition all cases in order.
  Existing production CLI/MCP status exposes per-packet progress. No second owner,
  budget reset or scene-check bypass. Existing resume skips attempted work and
  acquires a fresh session. Actual MCP status returned two completed packets;
  invalid CLI partition was refused; completed resume preserved all source case
  file hashes. Cancellation/fresh-session behavior passed offline regressions;
  no new live mid-case cancellation claim.
- **G3:** first acquisition-to-ready is measured warmup, including its cost.
  Native scene setup and focus settling remain per case; no guessed warmup sleep.
  Runner startup/cleanup receipts were preserved separately. Separate-campaign
  trials exercise startup each time, but are not cache-flushed OS cold-start tests.
- **G4:** `Scripts/run-campaign-packets.rb --overlap-export` overlaps at most one
  **terminal**, checkpoint-pinned export with the next collection. Backpressure,
  export deadlines/owned process cleanup, resource snapshots, readiness and evidence
  reserves remain in place. Active checkpoints never become exportable. Serial
  export stays the default: this comparison does not establish an overlap gain.
- **G5:** 47 focused host tests passed, 3 opt-in skips, 0 failures. One final
  signed normal Debug candidate passed signing/portable gate and retained App
  Sandbox without test-only read exceptions. Portable interface resource parity,
  actual CLI/MCP, source hashes, PNG dimensions, native focus/capture bracket and
  common crop-window audits passed. Skill/planning/export validators passed.

## Same-specification comparison

Exact local tvOS26.5 Simulator, one signed host candidate and unchanged matched
Fixture. Two packets of two cases; same four focus-change × scroll-change
specifications in all six arms. 24 accepted attempts,
4 distinct specifications, 1 scene,
1 ancestry group. These repetitions are timing evidence,
not 24 independent new training examples. No case failures or cleanup failures.

| Arm | Pairs | Collection s | Export sum s | Full wall s | Runner startup s | Runner cleanup s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| grouped-repeat-run | 4 | 44.32 | 51.22 | 100.02 | 18.27 | 1.78 |
| grouped-run | 4 | 44.04 | 24.09 | 81.24 | 16.0 | 1.25 |
| overlap-repeat-run | 4 | 95.0 | 61.36 | 122.93 | 60.29 | 3.69 |
| overlap-run | 4 | 90.79 | 66.84 | 125.87 | 55.17 | 3.29 |
| separate-run | 4 | 48.47 | 19.88 | 75.16 | 19.87 | 2.48 |
| serial-run | 4 | 77.57 | 36.96 | 122.61 | 42.15 | 3.38 |

Full wall includes validation, readiness, capture, export and cleanup. Export sums
can overlap collection; do not add overlapping stage durations. Capture timings
include runner lifecycle; nested scene stages are not additive either. Startup
varied substantially, including before concurrent export began. This is a small,
sequential local comparison, not a randomized throughput guarantee. Grouping is
qualified operationally; choose batch size from representative workload measures.
The earlier larger reuse benchmark remains separate evidence and its gains must
not be multiplied by these measurements.

538504150 bytes retained source/export/review evidence,
within the 2GiB tranche envelope; 24/32 attempts and less than 30 minutes collection.
All final readiness reports show can_run=true and ownership clear. The macOS
NUIAK test helper was observed at zero CPU during preflight and was left untouched;
no Simulator test owner or threshold-level host load was present. Memory snapshots
and contention receipts are retained; they do not constitute peak-resource profiling.

## Evidence and limits

Project-local lane: `.local-work/grouped-campaign-20261003/`:
`tests-01.xcresult`, `test-summary-01.json`, `portable-gate-01.json`,
`entitlements.plist`, six `*-run/result.json` records, original CLI replies,
checkpoint-pinned exports, native overlay/crop reviews, runner timing receipts,
`summary.json`, `audit-summary.json`, `mcp-packet-status.json`,
`invalid-packet-cli.json`, `completed-resume-02.json`, and `completed-resume-preserved.json`.

The baseline/grouped/first overlap were already running when optional schedule
candidate-hash/runtime guards were added; remaining arms exercise those guards.
Compiled runtime and recipe contents remained identical. Export timestamp fields
are present for overlap arms. Scripts use repository CLI/MCP rather than introducing
new service endpoints. Large JSON still obeys existing MCP envelope limits.

No cross-campaign persistent runner, mutable export, appearance/interruption reuse,
physical qualification or consumer admission. Lessons N-010 and N-016 apply:
cleanup/requested state cannot substitute for observed readiness/native state.

## Next substantial tranche

Core SYNTH-01/02/05/06: apply compatible packet planning to native collection/poster
cells and mixed catalog layouts; generate a balanced multi-scene batch with measured
body/child/artwork bounds, scroll/context coverage, crop review and same-candidate
throughput evidence. Preserve independent scene/ancestry counts and let NUIAK select
coverage through source-owned requests. Consumer intake still needs maintainer Git
publication and NUIAK's schema/role review; no producer binary is required.

Optional DBG-LOG-03: repair helper diagnostic persistence and route-preparation
errors with retained evidence and one bounded exact-operation regression. Do not
let that independent repair block renderer/corpus work.

Caller-check correction: the first resume invocation omitted the required
`--expect-manifest-sha` option and was rejected before execution. Its original
`completed-resume.json`/stderr are retained; the corrected hash-guarded check
passed and preserved59source case files. No Simulator retry/restart was needed.

Measured means: grouped90.63s, separate serial98.88s, overlap124.40s per four
attempts. Grouping was8.35%faster on these two-run means; overlap25.80%slower
than serial. Startup variation and small sequential sample prevent a general
performance promise. Keep serial export as default; use packet grouping for
compatible work and measure larger representative batches before tuning further.

Reporting correction: use xcresult top-level47passed/3skipped/0failed, not
the per-device aggregate77. The first sanitized status report quoted the latter;
revision2corrects the test count without changing runtime or corpus evidence.
