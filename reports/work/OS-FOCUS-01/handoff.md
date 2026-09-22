# OS-FOCUS-01 preparation checkpoint

Superseded by [approved live recording and replay](live-20260922-0712/handoff.md):
six inputs completed, seven observations retained. Original preparation evidence
and approval-pending statements below are historical.

2026-09-22 UTC. Owner: NUIAK architect. Native OS focus is an independent lane;
TTR/Fixture repair is not its prerequisite. The assigned live outcome is not complete.

## Delivered

- NUIAK-owned standalone XCTest target, native Settings AX focus/geometry and
  screenshots, at most six single Up/Down inputs, cooperative bounds and stop on
  ambiguity/context change. No Select, TTR/Fixture API, trainer or public API changes.
- Before/after observations, point viewport, pixel dimensions, screenshot interval,
  SHA-256, retained attachments and terminal context. Labels remain review-required.
- Canonical plan, queue entries, roadmap/catalog links and build instructions.

## Verification

- `xcodebuild build-for-testing`, simulator-only `CODE_SIGNING_ALLOWED=NO`: exit 0,
  `build-final.log`. Swift source compiled; Xcode emits the no-AppIntents metadata
  extraction warning. No claim of warning-free Xcode integration or successful install.
- `swift build` offline: exit 0, `swift-build.log`, no warnings.
- `swift test` offline: exit 0, 92 tests in 9 suites, `swift-test.log`.
- `git diff --check`: exit 0.
- Initial signed builds: exit 65 due generated-bundle Finder metadata, retained
  `build.log` and `build-r2.log`. No certificates changed. The unsigned target is
  simulator-only and does not alter production signing requirements.

## Actual outcomes and resume

Software: build verified, live XCTest behavior not verified. Data eligibility:
not assessed, zero captures. Integration: not qualified. Model gates: not assessed.
No new runner installed, no Settings activation or remote inputs, no training.

Pending user answer to scoped approval: install/run this test runner on exact
9026ECA9-77DB-4AE6-8FE6-BB239E9571FA with standard simulator runtime writes,
Settings activation and six Up/Down inputs. Before execution verify exact target
and no competing interaction, bind build/runtime identities, disable parallel
clones, enable XCTest timeouts, use a new xcresult destination. Then inspect native
focus-to-pixel alignment before admitting any same-element pairs. Do not substitute
Fixture labels or model predictions if OS AX focus is missing.

Unrelated changes and active iOS reconstruction preserved. No TTR repository or
runtime changes. Shared coordination: not applicable to preparation; local OS
development does not change the peer's producer repair request.
