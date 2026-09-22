# Updated build diagnostic — 2026-09-22 05:49 UTC

Read-only runtime checks; no capture, app launch, restart, workspace repair,
navigation, inference or training. Used running app's stable CLI, not an unrelated
helper. GUI PID97632, started 05:02:50Z; version label 1.0 is not a source identity.

## Observations

- Help, status, simulator list and exact-target readiness exit 0. Status/list/
  readiness return success=true. Coordinator idle; physical connection disconnected
  is not a simulator failure.
- Exact target 9026ECA9-77DB-4AE6-8FE6-BB239E9571FA: booted tvOS26.5, Xcode26.6
  build17F113. Eight infrastructure checks ready; can_run=true, persisted ownership
  clear. Fixture explicitly not_checked by this readiness API.
- No listener found on prior port8080; one GET http://127.0.0.1:8080/scene exits7
  (connection refused). This establishes prior endpoint unavailable, not that no
  Fixture could be running at another endpoint or a diagnosed Fixture crash.
- Checkout HEAD0dfb373ad0341e9f36fa9bf32d92afafa1318750, Screenshot repair.
  CompanionMain source SHA matches producer's reported repaired source exactly.
  Checkout identity is not proof of loaded build provenance; on-disk binaries are
  pinned below, and the end-to-end screenshot repair remains locally untested.

## Identities

- App/stable CLI SHA256: c2dd24b2e2b591c121ff0d41769f5797f1b6b0831f6618fcaddadfef5884428d
- App debug dylib SHA256: 22573dfceb3b7dc4bdc9a9e5019de24dc53c2fa35a7eb06477e1e4e7989121ae
- Companion SHA256: 6f47d797952ee55e767c9ea3b97b09b868ac2efbdb17d403c56e9daabbccf68e
- CompanionMain source SHA256: 08937d144aeced77659e1ea9be6ed0ad740f80ff6935763168ccee1147af5402
- Bundled skill revision10; repository-local copy revision7. Runtime documentation
  read for current interfaces, no protected skill edits made.

## Diagnostic feedback

1. CLI help says --project is mandatory, but all three app-managed commands work
   without it. Correct help to match supported app-managed mode; do not change roots.
2. Each CLI emits diagnostic_file_sink_failed / persistenceFailed code23 on stderr,
   then succeeds. This is nonfatal logging degradation, not screenshot EPERM evidence.
   Producer should clarify/support the intended diagnostic sink without permission
   weakening. Retained stderr is sufficient for this check; no rebuild requested.
3. Readiness correctly leaves Fixture not_checked. Do not present can_run as full
   dataset readiness. The immediate missing input is a responsive exact-target Fixture
   endpoint, then separately authorized complete capture/export/intake.

Software: existing acceptance preserved; no new test-suite claim. Data: not assessed,
no new pixels. Integration: infrastructure ready, capture/intake unqualified.
Model gates: not assessed. Old screenshot failure retained as historical, not rerun.

Next: launch/identify matching Fixture on the exact target under explicit authority,
verify endpoint and observed labels, then run the bounded two-element smoke through
export/intake. Do not repeat generic readiness/signing repairs. Direct TVGEN lane
remains independent. Raw JSON/stderr adjacent; all outputs project-local.
