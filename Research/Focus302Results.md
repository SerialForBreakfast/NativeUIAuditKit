# Small native focus changes — FOCUS302

Maximum-mini-NUIAK runs this batch on `codex/focus-improvement-301` from `fd9139e`.
The batch uses Maximum-mini-TTR and simulator `9026ECA9-77DB-4AE6-8FE6-BB239E9571FA`.
No Office operation, model training, or promotion occurs.

## Capture and intake

The frozen campaign requests 2 recipes with 4 corner targets each.
Requested control sizes are 40 and 80 points. Actual artwork bounds differ from requested layout bounds.
Both jobs report completion. NUIAK checks all 36 indexed files by size and hash.

- The 40-point recipe lacks body measurements for all 4 pairs. Telemetry reports `not_rendered`.
- Intake rejects these 4 pairs. They provide no qualified model result.
- The 80-point recipe passes strict checks for all 4 pairs.
- Production preprocessing creates 8 crops from these pairs.
- Visual review confirms missing artwork in the smaller recipe and visible focus growth in the larger recipe.
- All related frames remain development evidence within the existing training ancestry. They are not independent final evaluation.

Native observations identify the focused elements. Capture brackets connect observations with images.
These checks do not authenticate framebuffer identity or establish real-app performance.

## Fixed-model results

| Condition | DTM083 correct | DTM085 correct | Support |
| --- | ---: | ---: | --- |
| Forward focus change | 0/4 | 0/4 | 4 related native pairs |
| Reversed focus change | 0/4 | 0/4 | Same 4 pairs |
| Same reference image | 4/4 | 4/4 | Derived controls |
| Same focused image | 4/4 | 4/4 | Derived controls |

Neither model abstains. Both models confidently report no change for the changed pairs.
Image-only proposals find all 4 forward changes. The smallest rendered dimension becomes 2.93 pixels at the model input.
The changed-only abstention rule does not correct these misses because both models report no change.
This result supports testing detail preservation. It does not prove the exact cause of each error.

The reporting tool also supports changed-only abstention as a diagnostic option.
No production decision or threshold changes.

## Recovery and verification

The first prepare call cannot read the recipe file. TTR reports that it sends no coordinator request.
The next attempt supplies inline JSON in a new output directory.
Direct export fails with `export_staging_create` and `access_denied`.
The supported chunk exporter recovers the completed job without recapture.
Final readiness reports `can_run: true` and clear ownership. Fixture responds after both captures.
Maximum-mini-NUIAK preserves failed attempts and originals.

The offline native Swift build passes. All 171 Swift tests and 37 focused Python tests pass.
Focused tests cover fixed recipe membership, output collisions, missing attempts, abstention semantics, and evidence counts.

## Evidence and next action

Local evidence lives in `reports/work/FOCUS-302/capture-r2/`.
`analysis/evaluation.json` links model hashes, input records, pair decisions, and exact scores.
`campaign-v3.json`, `attempt.json`, and job files retain target, runtime, recipe, and build records.
`analysis/crop-review.json` records production crop results.
Bulk evidence remains ignored. This summary does not replace those records.

Maximum-mini-NUIAK next compares detail-preserving regions against whole-frame inputs on these failures and retained successes.
The comparison must include center and left distractions. Oracle boxes cannot count as deployable proposals.
TTR should review completed jobs that lack body measurements and report unsupported targets clearly.
Missing small-control measurements block that subset, not further NUIAK diagnostics.

The coordinator stores request `nuiak-focus302-small-controls-01` at cursor 123. Exact-ID readback confirms storage.
Forwarding, reading, and acceptance remain unconfirmed. The request names Sillycon-TTR as the source review recipient.
Compact attention reports no unread messages before publication. The separate history request fails without changing chat state.
