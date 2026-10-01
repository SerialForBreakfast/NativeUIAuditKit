# REVIEW-QT-01 — persistent startup mitigation

Completed for review. The current five-image annotator remains running (PID57665);
it was not closed/restarted or automated. No annotation files were opened by the
doctor or negative startup test.

| Outcome | Result |
| --- | --- |
| Software verified |33Python tests, offline Swift build and120Swift Testing+14XCTest pass |
| Data eligible | Not applicable; annotations/admission unchanged |
| Integration qualified | Real Cocoa doctor passed; invalid-platform ordinary CLI refused before annotation loading |
| Model gate passed | Not applicable; no model activity |

## Durable change

- Existing editor CLI invokes `human_review_startup.preflight` before importing Qt
  in the parent/opening a batch. Same interpreter, platform and plugin configuration
  run in a child with20second timeout. Qt library load and QApplication/widget
  construction are checked without showing a probe window.
- Child aborts/timeouts/inconsistent/missing receipts fail closed with exit2 and
  unique project-local logs. No automatic retry/reinstall or silent platform fallback.
- Every launch rechecks readiness; batches reuse the shared verified cache under
  `.build/human-review/qt-cache`, preserving Cocoa framework-relative lookup.
- `--doctor` requires no batch and exposes the same check. One
  [canonical runbook](../../../Research/AnnotationStartup.md) and operational-lessons
  entry replace ad-hoc launch instructions. Low-level `window()` remains available
  for controlled offscreen tests, not an operator bypass.

## Verification

`PYTHONDONTWRITEBYTECODE=1 TMPDIR="$PWD/.build/tmp" PYTHONPATH=scripts
.venv-review/bin/python -m unittest scripts.test_review_startup
scripts.test_review_plugin_cache scripts.test_human_review_editor_interactions`
→33pass ([log](tests-final.log)):7new guard tests,3cache tests,23editor tests.
Includes no annotation/Qt initialization in the parent after failure, fresh checks
on repeated launch, malformed/native-abort/timeout/spawn handling and cache identity.

Actual `.venv-review/bin/python scripts/human_review_editor.py --doctor --runtime
reports/work/REVIEW-QT-01/runtime` passes with Cocoa, Labelme5.2.1, PyQt5 5.15.11,
Qt5 5.15.19, QtPy2.4.3 ([receipt output](doctor-final.log)). Initial measured doctor
elapsed0.367seconds; no latency SLA claimed. Scoped invalid `QT_QPA_PLATFORM` ordinary
launch exits2 with `platform_configuration`, before trying the deliberately nonexistent
batch ([negative output](failed-launch-final.log)). No global environment changes.

Required offline Swift [build](swift-build.log)/[tests](swift-test.log) pass with
in-project caches, automatic resolution disabled, no warnings/errors. Diff check
passes. No wheel changes, settings resets, downloads, TTR or shared-status work.

Limits: startup checks cannot guarantee later Qt callbacks or eliminate a race
between probe and parent initialization. Detailed native crash reports remain
platform-managed; this tool retains its explicit output locally. The guard stops
known failures from reaching the annotator and preserves evidence for genuinely new
ones, rather than promising Qt will never fail. Next user action remains the open
sample review; no restart is required to continue it.
