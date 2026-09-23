# Repaired Fixture setup and direct-pilot continuation

Observed 2026-09-23 UTC. Owner: NUIAK architect. Assignment: approved copy-only
metadata repair, existing-signature verification, exact-simulator installation,
then authorized frozen direct pilot. No Office, model training, scale collection,
producer source modification, signing change, or production promotion performed.

## Delivered

- Staged original candidate separately; all copied file hashes matched. Original
  producer artifact preserved. Removed only prohibited FinderInfo from staged root
  immediately before strict verification; no re-signing. See `stage-receipt.json`,
  initial failed `install-receipt.json`, and successful `install-receipt-2.json`.
- Exact simulator `9026ECA9-77DB-4AE6-8FE6-BB239E9571FA`; Fixture PID66851;
  dylib SHA256 `46011bb0a95cb007325a64baaab643ad913e0bf46c250a7198caab7b9f31a095`.
  Source reference `60936636cba3e71e203ee6988dfccad24401a875`; build bytes are
  recorded separately, not assumed identical to every producer-reported build.
- Reviewed source repair, bound installed process/HTTP endpoint, then captured one
  repaired media boundary: four pairs, exit0, healthy postflight. Inspected all five
  original frames. Continued remaining29 recipes; exit2 after23 completed recipes.
- Ordered immutable receipt chain: `dataset/tvos_captures/direct-pilot-20260922-2152/failed.json`
  (12 recipes/30 pairs), `direct-media-boundary-20260923-0044/segment.json` (1/4),
  `direct-pilot-rest-20260923/failed.json` (23/104). The latter two paths share
  the first path's `dataset/tvos_captures/` parent. Total36 recipes/138 retained
  pairs, not admitted training membership. Original failed receipts remain failed.
- Real resume planner/auditor revalidated the chain; `remaining-kitchen-plan.json`
  accounts for six remaining recipes and108 expected pairs. Full42 contract unchanged.

## Concrete blocker and source-backed diagnosis

First kitchen-sink recipe (zero-based36, light/seed7/count41) failed settling with
`unverified_native_state`: scene0×0, no elements, native `no_sample`, all18 targets
missing. No reference image was published for that recipe. One passive follow-up
confirmed the failure while HTTP remained responsive (`kitchen-passive.json`).
Diagnostic-only screenshot `kitchen-diagnostic.png` shows Components selected.

Producer `TVTestRig/TVTestRigFixture/Coordinators/FixtureCoordinator.swift:244`
routes `.kitchenSink` to `.componentShowcase`, whereas other recipes use
`.proceduralScene`. `ProceduralSceneView` contains both the native observation probe
and a kitchen-sink renderer. `ComponentShowcaseView` has no matching native probe
or `reportNativeObservation` call. `/recipe` and `/scene/load` invoke the same
coordinator method; inspected HTTP routes expose no scenario override. This
source/runtime agreement explains the missing observation path. Do not work around
it by inventing labels, manually switching tabs during a capture, or mutating the
frozen recipe identity. Producer must qualify the intended route/observation path.

## Visual review and retained-data caveats

Reviewed six family contact sheets covering all three themes, reference/first/last
focused states, plus all five media boundary originals. Nominal boxes and visible
focus changes agree on these reviewed examples; this is not exhaustive pair review
or production-crop acceptance. Bright white controls can be unfocused; brightness
alone must not supply labels. Container boxes can include labels/whitespace.

`overlay-index.json` identifies54 edge occurrences: `maze_2_2` at
`[1020,2080,884,80]` touches the2160px bottom edge, across nine frames in each of six
maze recipes. Contact sheets confirm clipped goal controls and overlapping footer
content. Keep this as explicit clipped-case evidence, not clean full-control coverage;
inspect remaining seed19 anomalies before any final admission. Ask producer whether
clipping is intentional and to supply visible/full geometry semantics or correct
layout. No annotations or images silently rewritten, dropped, or upgraded.

## Verification and outcomes

Existing production software unchanged this turn; reuse32 Python tests,14 XCTest
and93 Swift Testing checks plus Swift build from `../TVGEN-RESUME-02/handoff.md`.
New work exercised genuine setup/capture and read-only receipt auditing. Strict
signature/install/launch each exit0; boundary capture exit0; later capture exit2
at the expected no-retry guard. See receipts for command timings; capture duration
is recorded in raw observations, not estimated as test runtime. No external wait loop.

- Software verified: prior integrated checks retained; new diagnostic scripts are
  evidence tooling, not new public/library APIs.
- Data eligible: blocked for full pilot/training;138 pairs retained only.
- Integration: repaired media and six-family direct capture work; complete pilot
  blocked on kitchen-sink native observations. TTR exported sidecar-v2 intake remains
  a separate unresolved qualification, not tested by direct capture.
- Model gates: not assessed. No full-pilot shipped baseline or training started.

Fixture remains running; no capture process or controller lease retained. Responsiveness
passed, but kitchen-sink native readiness failed. No resets or unchanged retry.

## Next action

TTR supplies reviewed kitchen-sink route/native-label repair and addresses clipping
semantics. NUA validates changed artifact and authorized setup, resumes only six
missing groups, completes anomaly review/assembly and production-crop shipped-model
baseline. Preserve the first36 recipes; no redundant whole-pilot recapture. Any
intentional redesign of those recipes requires a new version, not edited history.
