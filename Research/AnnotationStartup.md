# Annotation startup — one supported path

From the NativeUIAuditKit root:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv-review/bin/python scripts/human_review_editor.py BATCH --queue QUEUE --runtime PROJECT_RUNTIME
```

This launcher automatically checks Qt in a fresh child process, with a20-second
timeout, before the parent opens any annotation. It verifies plugin loading and
QApplication/widget construction without showing a probe window. A child native
abort, timeout or invalid receipt blocks launch with exit2 and a diagnostic path.
It never retries automatically. This does not guarantee later callbacks cannot fail.

Diagnosis without a batch or annotation window:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv-review/bin/python scripts/human_review_editor.py --doctor --runtime reports/work/HUMAN-REVIEW-01/runtime
```

All receipts/logs are under the selected runtime's`startup/<unique-id>/`.
The receipt includes interpreter/package versions, actual plugin paths, requested
platform, stage, elapsed time and exit code. Native GUI launches must report
`platform:cocoa`; offscreen tests do not establish Cocoa readiness. Leave an
already-running annotation window alone; saved/unsaved review edits are unrelated
to a new process's startup check.

## Existing repairs — do not rediscover or redo them

The shared project-local cache is `.build/human-review/qt-cache/qt-plugins/<hash>/`.
The launcher verifies copied plugin bytes, preserves`plugins/platforms`layout,
checks the`lib`link to the installed in-project Qt frameworks, and clears only
the hidden display bit on its owned plugin copies when needed. Installed wheel
files are never edited. Different review batches reuse this cache but retain their
own settings/logs. Cache success is not cached readiness: every launch probes again.

| Category | Next check |
| --- | --- |
| framework_lookup | Exact missing library and cache`lib`link; preserve relative layout |
| cache_integrity | Exact changed bytes/link; retain evidence, no automatic deletion |
| environment | Correct `.venv-review`interpreter and pinned installed dependencies |
| platform_configuration | Unexpected scoped QT_QPA_PLATFORM override; no silent fallback |
| timeout | Child stderr and dependency residency; no unchanged retry loop |
| native_exit / invalid_receipt | Child exit code/stderr; discovery alone is not loadability |
| qt_initialization / spawn | Exact recorded stage, process context and error |

Do not install another Qt, weaken permissions, alter global DYLD settings, restart
the active annotator, or launch bare `labelme` as a workaround. After a justified
scoped repair, rerun doctor once. A passing doctor is required before reopening.

## Regression checks

```sh
PYTHONDONTWRITEBYTECODE=1 TMPDIR="$PWD/.build/tmp" PYTHONPATH=scripts .venv-review/bin/python -m unittest scripts.test_review_startup scripts.test_review_plugin_cache scripts.test_human_review_editor_interactions
```

Tests cover cache layout/source preservation, corrupt bytes/wrong links, fresh
checks on repeat launch, native-abort/timeout/spawn/malformed responses, and
failure-before-annotation-loading. Real Cocoa qualification uses doctor in the
actual GUI launch context, plus the existing editor interaction suite. Repository
offline Swift build/test requirements still apply to code changes.

Internal `window()` is used by controlled offscreen tests; it is not an alternative
operator launch interface. No model, TTR, annotation, or data admission is authorized
by doctor or a startup receipt.
