# TTR-CATALOG-01 — new-feature/runtime reconciliation

Observed 2026-09-23 05:04–05:07 UTC. Scope: read-only local runtime checks,
existing v2 consumer regression tests and producer handoff review. No capture,
navigation, installation, restart, Top Shelf mutation, training or promotion.

## Independent results

### Authorized smoke continuation — completed

[Smoke handoff](smoke-0514/handoff.md): job48683F4D completed2/2 pairs; bundled
chunk exporter verified12 files after signed CLI export staging denial. Strict v2
intake, visual review and four production crops pass; v1.5 development-only manifest
published. Postflight settled/responsive, same instance, ownershipclear. The default
no_sample observation below no longer blocks this recipe path. No training run.

### Latest recheck — 2026-09-23 05:11–05:12 UTC

**Supersedes the missing-new-build diagnosis below.** AppPID42670 now runs from
DerivedData/TVTestRig-fssavpzkujakgqggjglqjvvrtyoo; FixturePID43156 is installed
under bundle4A37BDF4 on the same exact simulator. Its dylib now hashes to
5b697fb409e64a6187b60bd68d7ea38cf867c6620fdcefd1fd67cad9c7b5332a.
Matching helper advertises Top Shelf set/status/reset. Both HTTP GET and real CLI
`fixture top-shelf status --fixture-url http://127.0.0.1:8080` succeed, reporting
`static_fallback`; CLI duration23ms. No artwork mutation/rendering claim.
App-managed status passes100ms; eight readiness checks pass with ownership clear.

Current default media scene still has no_sample, zero measured elements/dimensions
and unsettled focus. This is not yet a recipe-admission failure: no recipe was
applied in this read-only check. Next bounded two-control smoke must establish
native observed labels and complete capture/export/intake. No further rebuild is
justified by current evidence. Retained Sillycon catalog delivery remains separate.
Evidence: `recheck-0511/`. No capture/input, training, restart or installation.

### Replacement-build recheck during this assignment

User relaunched new builds. Fresh process inventory confirms appPID41295 and
FixturePID41184 in a new installed bundleD37588A7. Helper SHA changed to
0303bbdbbecd5fab69825a59728764c6bd13d6146e1be1f03cadf28921ad270e,
but Fixture dylib remains exactly7453848091948d0b52b264118edfa71da2ddab26a714ab63671554ab1b283f8b.
New helper still omits Top Shelf, new endpoint still returns Not Found, and new
scene still has no_sample/zero geometry. App-managed status passes in74ms.
See new-*.json/txt/stderr. A changed process/install UUID is not changed code.

Local Developer checkout is4acf1dee31034cfd2c3d0195a467ff35965487a4; Documents/GitHub
checkout is46dce7b3a79e4f17af49bc0324d4aeba3cc0958d. The former contains the new
route; the latter does not. Wrong-checkout/stale-product build is a supported
hypothesis, not proof of the exact Xcode invocation. Resume by matching source,
build products and installed artifacts; no further blind relaunch, signing repair
or simulator restart. The following initial results are preserved as historical.

1. **Local runtime routing/readiness:** matching embedded helper, app-managed
   `status`, and exact-target `simulator readiness` pass. Target
   `9026ECA9-77DB-4AE6-8FE6-BB239E9571FA`, tvOS26.5, booted; ownership clear.
   Explicit routing to the old Documents checkout fails `serviceUnavailable`;
   app-managed routing succeeds. Do not repair bookmarks or restart services for
   this routing distinction. Infrastructure readiness does not qualify Fixture.
2. **New Top Shelf feature availability:** current helper help omits Top Shelf;
   live GET `/top-shelf` returns `{"error":"Not Found"}`. The newer Developer
   checkout at4acf1dee advertises that route and CLI. Current installed Fixture
   dylib74538480 differs from producer-qualified73c8d7a1. Source presence does not
   mean this Mac runs that build. No set/reset attempted or Home rendering verified.
3. **Fixture observation:** listener8080 belongs to FixturePID39546 under the
   exact simulator. `/device` responds with instanceDBB8337D-8453-41E3-94EC-E7A0FD3E0DE4;
   `/scene` reports media_shelf, zero dimensions/elements, `no_sample`, unsettled.
   This observation cannot label captures; it does not diagnose why sampling is absent.
4. **NUA v2 software:** existing `test_ttr_sidecar_v2.py` passes8/8 in0.531s,
   including real manifest/crop CLI, baseline preflight, changed geometry, corrupt
   brackets, versions, partials, false claims and collision cases. Synthetic fixtures
   only, not acceptance of the new genuine catalog. No code change or full rebuild.

Raw results: status.json (failed old-project route), app-status.json, readiness.json,
device.json, scene.json, top-shelf.json, binary-hashes.txt and consumer-tests.log.
Helpers ran in approved host execution; explicit evidence stays here. App-managed
readiness retains its own standard runtime diagnostics. No owned session was started.

## Producer evidence and intake boundary

Read the supplied catalog report and shared CATALOG-VISUAL-FIDELITY-20260922
entry dated04:56:58Z. Peer acknowledges both existing intake and appearance requests.
Corrected jobC531375D-E6B5-4A46-A3E0-CD36476F3DCC is on Sillycon's different
simulator2BAA6307. Producer reports4 pairs,18 files,57,903,555 bytes and export
manifest SHA256e9380e0f46440d40057d3408cca2c67ca45b736df8b5714d93a61de6583ce972.
Eight real controls/four focus targets are supported;33 placeholders are exclusions,
not class coverage. Blank-button trial and old17-pair generic catalog are not eligible.
The referenced export directory is absent in this Mac's Developer checkout; the
scoped local capture-root inventory does not show that corrected bundle. No independent
byte/visual intake claim, no remote execution and no dataset on the status share.

Destination for maintainer-mediated copy (new directory, preserve original):
`dataset/tvos_captures/ttr-catalog-c531375d/` in NUIAK. Include original export manifest,
receipt, index and all payload files. Identifying a destination is not an established
cross-machine transport; retain the producer source and never overwrite old evidence.

## Focus adoption decision

FDR-008 is experimental, not exported/promoted. On APPEAR-A2's related development
corpus it detects73/76 positives with0/76 false positives, versus shipped11/76 and9/76.
Six individual crops overlap training; oracle boxes are supplied. Conversely retained
Home/Photos unique-focus decisions remain0/8, with five Home negative false positives.
These different metrics cannot be combined into a general accuracy claim.

TTR should evaluate candidates in an isolated **shadow/report-only** comparison,
recording artifact hash, backend, candidate boxes, thresholds, abstentions and latency.
Do not replace native focus evidence or use FDR-008 as the sole pre-Select decision.
No change to TTR integration or shipped NUA fallback was made.

Next: deliver corrected bundle and match local installed artifacts to the reviewed
build; then independent byte/label/crop/visual intake and bounded Top Shelf rendering
qualification. Keep in-app artwork/bright-unfocused/dock appearance work separate.
Before another candidate: independent appearance validation and untouched challenge
groups, balanced native/Fixture replay, end-to-end focus-selection evaluation, then
CoreML parity/size/latency and physical gates. APPEAR-B1 remains unblocked offline.

| Outcome | Result |
|---|---|
| Software verified | Existing v2 consumer regression scope passed |
| Data eligible | Corrected genuine catalog intake blocked by transfer |
| Integration qualified | Local routing/readiness only; new catalog/Top Shelf not qualified |
| Model gate passed | Not assessed; known Home/Photos failure remains |

Worker, TTR, fixture and model guidance kept source/runtime, ground truth, crop parity,
test evidence and promotion authority separate. Shared publication is recorded in
coordination.md; peer acknowledgment of that new publication remains separate.
