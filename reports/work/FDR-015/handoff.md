# FDR-015 / FOCUS-RESET-01 — complete for review

| Outcome | State | Evidence |
|---|---|---|
| Software | Verified | 93focused Python tests, offline Swift build,14XCTest+109Swift Testing; actual trainer and replay CLIs |
| Data | Existing scoped development use verified | Exact same363train+9retention pairs/453real selection crops;64exclusions unchanged; no new admission |
| Integration | Verified for experimental frozen-feature training and cached comparison | Actual MPS PID75348, encoder frozen, ordered feature hashes,30epochs,14,601scores replayed |
| Model gate | Failed | 0eligible epochs; retention9/18, real0/35TP and1FP; no selected checkpoint/export/promotion |

Results and next assignment: [results.md](results.md). The useful finding is improved
final ranking, not a qualified model. Detailed cached comparison: `comparison.json`.

Acceptance mapping:

1. Reconcile ranking/runtime-style/strict metrics: reset `final-evidence/report.json`
   and this `diagnostics/report.json`, same13supported/27excluded frames.
2. Crop inspection: reset eight-page panel inspected; updated Home competitors
   inspected in005/006 here; labels and original pixels unmodified.
3. Pretrained baseline: verified named weight receipt, research-first adapter,
   `protocol-ready.json`, explicit `approval.json`, logged before owned launch,
   `backend.json`, `execution.json`, `artifact-verification.json`.
4. Evidence-backed stop/decision: no eligible checkpoint, no retry; targeted
   artwork/context and separate calibration design before any next training.

Verification: `verified-focused-tests.log` records93tests, zero skipped; includes
real CPU tensor mechanism checks plus legacy paths, changed hashes, bad scores,
membership/role rejection, runtime symlink regression and deterministic replay.
Actual MPS execution supplies integration evidence beyond test fixtures.
`swift-build.log`/`swift-test.log` pass offline; `git diff --check` passes.
Source/runtime hashes verified after execution; frozen source corpora untouched.

No active run/automatic monitor. Shipped artifacts unchanged. No Git writes.
Bulky weights/features/logs/reports stay project-local and gitignored; not backed
up by Git. TTR coordination not applicable: no producer action changes in this
local representation experiment; its existing data/geometry assignment remains.
