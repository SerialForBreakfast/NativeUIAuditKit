# Appearance pilot launch/intake handoff

Run from the repository root using the approved focus-export Python environment.
These instructions do not authorize capture. Never overwrite existing evidence;
use new project-local output names. Angle-bracket values below are placeholders.

## Offline preparation

`scripts/direct_tvos_capture.py --plan --appearance --output <new-catalog.json>`

`scripts/direct_tvos_capture.py --preflight --catalog <catalog.json> --target <exact-UUID> --endpoint http://127.0.0.1:<port> --producer-source <Fixture-source-directory> --capture-output <new-capture-directory> --output <new-preflight.json>`

Preflight checks source/configuration only, not runtime identity, endpoint
availability, ownership or authority. Do not silently change pins or targets.

## Separately authorized execution

After fresh target/build/endpoint evidence and approval of this24-recipe scope:

`scripts/direct_tvos_capture.py --execute --catalog reports/work/APPEAR-A1/catalog.json --target 9026ECA9-77DB-4AE6-8FE6-BB239E9571FA --endpoint http://127.0.0.1:<verified-port> --producer-source <Fixture-source-directory> --output <new-capture-directory>`

Serialize Fixture access. No restart/install/Office fallback. Each recipe is
bounded to120 seconds, settling10 seconds and HTTP5 seconds. Failure ends the
attempt with preserved partials; do not automatically retry or publish them.
Expect100 frames for76 target pairs, then require postflight health.

## Review and intake

`scripts/direct_tvos_capture.py --validate <capture-directory>/direct-capture.json`

Inspect actual focus/geometry representatives for every family/theme and every
anomaly. Create the existing hash-bound visual-review record/report only after
review; requested focus must never become a ground-truth label.

`scripts/direct_focus_manifest.py --capture <capture-directory>/direct-capture.json --visual-review <review.json> --output <new-crop-directory>`

Reconcile expected/captured/accepted/rejected counts and duplicates. Keep related
seeds/variants in development; this is not an independent holdout or training
approval. Use existing baseline tools with fixed reference hashes/thresholds.
