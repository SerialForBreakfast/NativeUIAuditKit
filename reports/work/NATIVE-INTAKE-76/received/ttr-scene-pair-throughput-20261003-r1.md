# Independent scene-pair throughput qualification

SYNTH-01/02/05/06. Completed for scoped producer review; consumer schema compatibility, human review and training admission remain separate. Scope and budget: [assessment and approved execution](../Plans/2026-10-03-scene-pair-throughput-assessment.md). Local evidence root: `.local-work/scene-throughput-20261003/`. Source baseline: `f933e2994ae07a967267dd00ed9d61d63b3cef7c` plus the recorded working changes; no Git writes.

## Implementation and evidence boundaries

- Controlled transition exports now carry a versioned scene-pair index with original image hashes, endpoint geometry, stable recipe/transition identity, native focus provenance, observed focus/scroll truth and evidence references. Missing telemetry remains unknown. Repeated attempts share pair identity and are not new independent examples.
- Setup-to-ready and action/observation timings supplement existing settle, snapshot, PNG persistence, startup and cleanup measurements. These nested stages overlap and must not be summed into a second elapsed total.
- `sparse_context` removes surrounding regions while preserving main-strip geometry and artwork. Dense scenes add context without reducing target resolution.
- Persistent MCP export reuses one helper process; checkpoint pinning, bounded chunks, source hashes, destination readback and no-overwrite publication stay intact. `--one-shot` retains the original transport for controlled comparisons.
- Fixture repairs dismiss the native table presenter when the active recipe changes renderer, and refresh the uncovered composition from the coordinator. Prior failures showed table views holding composition identifiers. The two-pair table→composition regression passed; corrected dense four-condition pilot passed.

The index supplements original capture brackets. `source_id`/`renderer_id` currently carry the producer ancestry identifier, not an exact source revision; build provenance is retained separately in this report/lane. Model transforms and consumer admission remain external. This does not establish byte-for-byte compatibility with NUIAK's independent intake schema.

## Live method

Exact assigned tvOS 26.5 Simulator, signed local TTR candidate01 and corrected Fixture candidate01; no physical device, settings changes or restart. Check contention, readiness and ownership before every arm. Four conditions × two backgrounds × two seeds make 16 scene-pair specifications; three per-case/reused-runner repetitions measure throughput without counting repeats as diversity. A1 is split into its four-case pilot and remaining twelve; record that startup distinction.

The first 16-case MCP request exceeded the existing 64-KiB envelope and was rejected by the proxy before IPC. No campaign existed afterward and readiness stayed clear. Subsequent arms use the supported CLI exact-JSON manifest import; keep this startup difference visible. All exports use one-shot transport during the runner/density comparison. Persistent export is measured separately on retained images, with no capture.

Runner reuse also persists campaign-scoped startup/cleanup in `runner-cleanup-*.json` under the source campaign directory. Those receipts are preserved separately in the benchmark's `runner-timing` folders; per-case timing alone omits the shared runner's initial acquisition. Count caller wall time for throughput, including this overhead. N-010 and N-016 apply: fresh readiness is checked separately from recorded input/focus/scroll evidence, and scroll context is measured per endpoint.

Initial incorrect-renderer failures remain in `benchmark/a1-pilot` and `a1-sparse-pilot-02`. The failed MCP start remains in `benchmark/b1`; its zero capture-attempt budget charge is supported by proxy rejection and absent campaign status. The separate renderer-switch route-prepare probe failed before input with helper `persistenceFailed`; the campaign renderer regression succeeded, but does not fix that route-preparation diagnostic-storage issue.

## Atlas disposition

Retained originals examined across three corpus lanes are 3840×2160. A 3840×2160 atlas therefore fits one full-resolution scene, not four. The retained-image tool correctly refused these inputs instead of resizing them. No positive four-tile round trip, packing throughput benefit or offscreen native equivalence is claimed. Keep native full-resolution capture; an 8K atlas or a separately qualified 1080p source would be a different experiment.

## Measured results

| Arm | Accepted | Collection s | Export s | Collection pairs/h | Through export pairs/h |
| --- | ---: | ---: | ---: | ---: | ---: |
| A1 | 16 | 114.3 | 67.0 | 504 | 318 |
| B1 | 16 | 79.6 | 95.9 | 724 | 328 |
| B2 | 16 | 100.0 | 93.0 | 576 | 298 |
| A2 | 16 | 309.1 | 96.3 | 186 | 142 |
| A3 | 16 | 308.7 | 98.9 | 187 | 141 |
| B3 | 16 | 93.1 | 96.2 | 619 | 304 |
| sparse | 8 | 53.3 | 54.2 | 540 | 268 |
| dense | 8 | 55.5 | 48.0 | 519 | 278 |

A = per-case runner; B = campaign runner reuse. Aggregate collection time: 732.1 s versus 272.7 s for 48 accepted attempts each (62.8% less time). Including the fixed one-shot export: 994.3 s versus 557.8 s (43.9% less time; about 174 versus 310 accepted attempts/hour). Startup variability is substantial: the first baseline is much faster than the later two. These are local repeated measurements, not a production capacity promise or a direct comparison with the supplied 1,250-pair baseline.

Retained four-pair export, counterbalanced P/O/O/P/P/O: persistent mean 18.95 s (18.66–19.28), one-shot mean 25.85 s (24.05–28.49), 26.7% less time. All six materialized exports contain identical path/byte/hash lists and checkpoint; 44,709,206 source bytes each. No recapture, hardlinks or deferred integrity checks. Do not multiply the isolated benefits and call that a measured combined throughput result.

Density: sparse 53.3 s versus dense 55.5 s collection, eight cases each, one seed and two backgrounds. This small difference establishes no useful speed advantage. Keep context for training value, not as a way to inflate independent pair counts.

114 accepted attempts = 112 comparisons plus two renderer-regression cases. There are **25 distinct pair specifications, seven scene recipes and one retained ancestry/journey group**, not 114 independent training examples. Two initial incorrect-renderer cases failed and were excluded; the oversized MCP request produced no campaign or input. The conservative attempt ledger charges 122 of 128 (including six planned but unattempted pilot cases). Collection used 1,165.6 of 3,600 seconds. Capture/export/review evidence uses 2,782,190,518 bytes (2.59 GiB) of 4 GiB; builds/caches/test results are separate.

Every exported index passed evidence/image SHA-256, endpoint ordering, dimensions, four-condition observed truth and journey/split consistency checks. Grouped review folders: `review-dense/index.html` (16 cases, 100 measured common windows, 32 explicit unavailable exclusions), `review-sparse/index.html` (eight cases, 10 measured windows, 16 exclusions), and `renderer-switch-review/index.html` (two cases, 11 measured windows, three exclusions). Crops are previews; full frames and clipping evidence remain authoritative. Sample original inspection confirmed the sparse scene and focused destination, including intended viewport clipping.

## Validation checkpoint

- Focused host XCTest: 14 passed, 2 opt-in skips, 0 failed (`test-summary-04.json`). Earlier compile failures retained and repaired. A nonexistent reuse-suite selector did not run; do not count it as coverage.
- Corrected selection ran the actual `InterruptionCampaignTests`: 10 passed, one opt-in skip, zero failures (`test-summary-05.json`), including runner ownership, cleanup failure, cancellation and fresh resume ownership. Combined: 24 passed, three skips, zero failures.
- Signed host build, Fixture build and portable Simulator bundle gate passed; App Sandbox remains enabled.
- Offline export tests reject corrupt chunks, wrong checkpoints/identity, nonterminal campaigns, invalid reserve and malformed persistent responses.
- Offline benchmark summary tests verify repeat deduplication, unknown truth, elapsed-rate calculation, split leakage and image corruption rejection.
- Final normal signed candidate02 and portable Simulator gate passed. Bundled `export-campaign.rb` and operator interface guidance match source bytes. The benchmark used candidate01 with the same host Swift implementation and corrected Fixture candidate01; candidate02 updates portable resources. No release DMG or consumer build was produced.
- Skill/package validation, export/summary/crop regressions and planning/task checks passed after regenerating their documentation indexes. Final caller readiness is retained separately; consumer intake remains unrun.
- Candidate02's actual CLI readiness returned `can_run=true`, ownership clear (`final-readiness.json`). Helper diagnostic-file persistence still reports its retained stderr warning; that did not invalidate this successful structured readiness response and remains the optional DBG-LOG-03 repair.

## Acceptance and disposition

| Criterion | Evidence / result |
| --- | --- |
| Stable scene-pair identity and original evidence | `benchmark-summary.json`: 114 verified indexed attempts, 25 stable specifications; repeated attempts deduplicated; all remain validation/calibration evidence. |
| Four observed focus/scroll combinations | Production CLI/MCP pilot and subsequent CLI arms pass all four cells. Native observations, mutation/action receipts and per-endpoint bounds remain linked; request labels are checked against observed outcomes. |
| Runner lifecycle and elapsed throughput | Counterbalanced six-arm table above; source campaign startup/cleanup receipts copied to each run. Every completed arm has verified cleanup and fresh `can_run=true` postflight. No restart. |
| Density isolated from target shrinkage | `sparse_context` unit check preserves main-strip recipe geometry; matched eight-case arms pass. Surrounding context changes, not target size or frame resolution. |
| Transfer correctness and useful optimization | Six retained exports use the same checkpoint and complete file/hash list. Persistent transport is measured faster locally; malformed responses and corrupt chunks fail closed. |
| Atlas/offscreen feasibility | 4K atlas rejected for retained 4K originals; no resizing. Offscreen native equivalence remains unqualified and outside implementation scope. |
| Failure preservation | Two wrong-renderer failures, pre-input MCP size rejection and separate route-prepare persistence failure retained. No admitted images overwritten or guards cleared from inventory alone. |
| NUIAK interoperability | Existing transition bundles and source/annotation evidence retained; new index is supplemental. Exact NUIAK intake compatibility and training admission **not run**; consumer owns those checks after maintainer Git publication. No NUIAK binary or training delivered. |

The next recommended core remains SYNTH-01/02/05/06: instrument native poster/collection cells, add mixed realistic layouts and scrolling, and qualify their self-service campaigns using runner reuse and verified persistent export. Include native/body/child/viewport evidence, failure/cancellation tests and consumer-schema examples. The current benchmark does not prove equivalent throughput for appearance-only campaigns, physical devices, absent-focus scenes or interruptions. Optional DBG-LOG-03: repair and qualify helper diagnostic persistence/route-prepare failure reporting. This is independent of the completed campaign renderer proof. No new physical/settings authority is inferred.
