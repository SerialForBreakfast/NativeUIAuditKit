# TVGEN-01/02 admission review and remediation

2026-09-22. Scope: delivered direct-runner review, targeted software remediation,
offline entrypoint verification. No live capture, producer edits, training or promotion.
Existing dirty implementation/planning files and iOS reconstruction preserved.

## Findings corrected

1. Expected targets previously came from live plannedFocusIDs: an omitted target
   could produce a falsely complete sweep. The runner now uses a pinned source-derived
   expectation and rejects disagreement. Source hashes live in direct_tvos_targets.py.
   Hero has2 targets; maze4 recipe expands to8 enabled nodes; kitchen-sink has18
   button-trait targets among41 classes. Grid uses source SplitMix64 disabled-cell
   rules for the frozen seeds. These expectations are not ground-truth focus labels.
2. Completed receipt did not bind initial instance/runtime details or consistent
   taxonomy/target membership across frames. Validation now requires initial instance,
   source-plan hashes, genuine runtime/build fields, unique frame paths, stable element
   taxonomy and complete source-expected membership. Endpoint binding is rechecked
   around each capture; an instance change rejects before screenshot.
3. Visual review accepted any nonempty report string. Admission now requires an
   existing nonempty project-local report with matching SHA256, bound to capture hash.
   This verifies the review artifact, not reviewer honesty or authenticated pixels.
4. Settling's individual HTTP calls could extend beyond its own10-second deadline.
   Calls now share the settle deadline, restoring the recipe deadline afterward.
5. Execution tests covered failure but not completed publication. Added a successful
   actual CLI-dispatch/execute orchestration test with deterministic external-boundary
   doubles, plus collision, omitted-target, initial identity and changed-review tests.

No v1.2/v1.3 behavior changed. Direct v1.4 stays development-only. Existing failed
live artifacts remain unchanged, not repaired/reclassified. No new actual baseline.

## Outcomes

- Software verified:44 focused Python tests and92 Swift tests pass; logs below.
- Data eligible: blocked; zero newly qualified genuine pairs.
- Integration qualified: blocked on native non-view focus binding; no runtime retry.
- Model gate passed: not assessed.

## Next

Verification: `.venv-yolo/bin/python scripts/test_direct_tvos_capture.py` (16 tests,
0.762s), `test_focus_consumer_integration.py` (14,0.792s), `test_focus_launch.py`
(14,1.321s), all exit0. Tests retain test-only provenance; successful execute
orchestration uses external-boundary doubles, not a simulator. Actual runtime crop
and shipped-CoreML CLI round trip remains explicitly synthetic software evidence.
Swift's first restricted invocation failed before compilation (`sandbox_apply`);
scoped approved build/test succeeded with project-local temp/cache/config/security.
The initial approved run emitted only a deprecated skip-update option warning;
final logs use `--disable-automatic-resolution`. No package/compiler fix was needed.
Build/test logs and retained failed invocation are in this directory. Capture/intake
time0, no external wait loop or live operation. `git diff --check` passes.

Coordination: verified existing SMB mount; published and parsed/read back
`nuiak/status.yaml` entry `TVGEN-ADMISSION-20260922` at06:33:34Z. Only source-plan/
admission consequences shared; previous request and other packet entries preserved.
No fresh runtime health or peer acknowledgment asserted. No extra feature request.

Source planning expects246 pairs /288 frames across42 recipes. Frozen catalog
bytes remain unchanged; expected membership is pinned separately in the capture
receipt's targetPlanSourceHashes. A new producer recipe-plan change must be reviewed.

TVGEN-01 reuse/authority design is evidenced; TVGEN-02 software is ready for architect
review against these tests. Native smoke remains incomplete. Reconcile an actually
changed matching Fixture artifact with the native-binding repair, then separately
verify current operation authority and exact target before new-destination smoke.
Successful smoke unlocks the already-planned42-recipe pilot and genuine baseline.
Do not re-run the unchanged failure or replace observed focus with requested focus.
