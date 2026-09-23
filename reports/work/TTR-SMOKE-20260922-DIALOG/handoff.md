# Changed Fixture dialog smoke — 2026-09-22

## Result

One authorized action_dialog/two elements/high_contrast/regular/seed7/step0 job,
`661FFE7C-26C8-4B78-9007-56E43DEA3995`, failed at the reference capture bracket:
`telemetry_bracket:identityMismatch`. Zero completed bundles; no export/intake,
eligible pairs, training, promotion, Office operation or unchanged retry.

The previous reference native-focus blocker is improved: generation2, verified
native view/identifier, referenceFocusedtrue, settledtrue, both planned button
IDs and no missing geometry. `focus_sweep_index=-1`: neither button's focused
capture is established. This does not qualify the broader shelf archetype.

## Runtime and operation evidence

- Exact simulator `9026ECA9-77DB-4AE6-8FE6-BB239E9571FA`, tvOS26.5.
- Fixture instance `D386D6EF-5298-4E56-B970-D0F55CB2C5B7`, run
  `1CDAAE97-AC6E-44A3-8273-1AF4312292BF`; listener8080 bound to selected process.
- Matching running app/bundled helper used; build identity inventory is in
  [preceding diagnostic](../TTR-CHECK-20260922-NEW/handoff.md).
- Canonical recipe SHA256
  `212f35c0395e8482756773652b238acc78ce000af18279370c21e2ea2999ea07`.
- File-based prepare failed `recipe_read:access_denied` before coordinator dispatch
  (exit64). Advertised `--recipe-json` route succeeded with the identical recipe;
  no folder-permission changes. See prepare/prepare-json/start JSON and stderr.
- `status-01.json` records terminal job failure and app-owned retained path; partial
  data were not manually published. `diagnostics.json` is the collector response,
  not an exported diagnostics directory or completed training bundle.
- Fresh postflight: HTTP/device/scene responsive, same instance/run,8 infrastructure
  checks ready, ownershipclear, coordinator idle/queue0 (`readiness-after.json`,
  `status-after.json`). Cached collector cleanup says unknown; fresh clear readiness
  is separate evidence, not a rewrite of that historical field. No reset/restart.

## Producer RCA and bounded requested repair

Read-only source: TVTestRig `SyntheticFactory/FixtureBatchHarvestEngine.swift`
declares `HarvestScenePayload: Codable, Equatable` at121, including
`observationDiagnostics` at123. Reference/focused capture compare full scene
equality at504/553. `HarvestObservationDiagnostics` in
`FixtureHarvestFailureDiagnostic.swift` includes changing sample counters/timers;
sanitization retains them. Thus a stable, fresh scene can fail full equality.

Two passive postflight snapshots (`scene-after.json`, `scene-after-second.json`)
have identical focus observation/ID, settled state, elements/geometry, recipe and
challenge state, but sampleCount511→1767, sampleAge65.442→87.696ms and
stableMilliseconds50997.359→176597.673. Exact failed capture-bracket samples were
not returned, so this proves the comparison defect, not exclusive attribution of
all differences in that particular bracket. No producer files were modified.

Requested producer-owned task:

1. Compare explicit stable capture identity, native observed focus, generation,
   recipe and geometry; do not compare volatile diagnostic counters/timers as identity.
2. Independently validate freshness/settling on both sides. Preserve target/source
   checks; never substitute requested focus or remove label safety to make it pass.
3. Test same valid scene with differing counters/timers passes; changed focus,
   generation, recipe, geometry or stale observations still fail. Return field-level
   mismatch evidence, not only generic identityMismatch.
4. Under producer execution authority qualify one reference plus both target states,
   completed bundle and postflight. NUA then rechecks the changed build and intake.

## Independent outcomes and next action

| Outcome | Result |
| --- | --- |
| Software verified | Prior offline evidence unchanged; producer comparator repair unimplemented |
| Data eligible | Blocked: zero completed bundles/pairs |
| Integration qualified | Failed for this exact job; reference-focus progress is not capture qualification |
| Model gate passed | Not assessed |

No broad Swift rerun for report-only diagnosis. JSON/readback/source comparisons
validate this finding; no new model metrics. Capture stopped on its typed failure
within the ten-minute bound; no external wait or background capture remains.
Continue independent NUA work; do not repeat this unchanged producer attempt.
Publication and peer acknowledgment are tracked separately in coordination.md.
