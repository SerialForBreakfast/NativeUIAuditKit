# TTR-DIALOG-01 — consumer software compatible with pinned dialog contract

2026-09-23. NUIAK architect, base b3f0546; prior dirty work preserved.

| Outcome | Result |
|---|---|
| Software verified |28Python regressions including144style cases;14XCTest+99SwiftTesting and build pass |
| Data eligible |Not assessed: generated cases remain explicitly test-only |
| Integration qualified |Not assessed live: no new producer bundle or runtime operation |
| Model gate passed |Not assessed; no training or model-quality claim |

## Contract and receipt

Read fresh peer status17:30:52Z: producer reports a long-label width repair, signed
Fixture21f4424e, not installed/live-qualified. Prior failed trial remains quarantined.
This change binds the shared source contract's closed fields and documented hash
suffix, not an independently tested newer runtime.

Exact metadata retained at `producer-contract-original.json`:41,539bytes, SHA256
`c25fa8fa2ad9c46694f38ccf8c5ce2b950415af6c492dadaf0e878775854cf20`.
Shared name `tvtestrig/visual-style-contract-c25fa8fa-20260923.json`.
All six embedded source lengths/hashes independently verified. The initial
`producer-contract.json` text transcript adds one newline (41,540bytes,different
SHA); it is explicitly not the exact transfer receipt. Neither file contains images.
Source revision12105bc796e6cc3645b4c769e6dd96310dcd68f3, dirty source declared.

## Implementation and acceptance

- Closed dialog_style v1: five required fields, strict integer version, known
  size/shape/palette/content values, action_dialog only; unknown extra keys reject.
- Absent/null preserves legacy digest. Source-described canonical suffix follows
  appearance.144combinations have unique hashes, checked against the documented
  canonical strings. These are contract-derived expectations, not144producer-captured
  golden vectors or proof of cross-language runtime parity.
- Sidecar-v2 brackets required. Existing bracket/alias/generation/hash checks apply
  before normalization. Changed style aliases, old hashes and legacy sidecar downgrade
  reject. Existing appearance vectors remain unchanged and pass.
- Actual validate_bundle and simulator manifest build run on every combination;
  full raw style survives observationBinding. Existing output schema remains v1.5.
- Actual ttr_focus_manifest CLI produces production-path crops from a test-only style
  bundle and validate_manifest succeeds. It remains test-only, not genuine data.
- Style siblings retain seed:7group; moving a sibling to held-out rejects leakage.
  Style diversity does not create untouched evaluation families or Photos buttons.

## Checks

`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts .venv-yolo/bin/python -m unittest
scripts/test_ttr_dialog_style.py scripts/test_ttr_appearance.py
scripts/test_ttr_sidecar_v2.py scripts/test_annotation_schema_versions.py`:
28tests,exit0,1.333s (`regression-tests.log`). Focused5tests also pass.

Offline Swift build/test use disabled dependency resolution, project-local
temp/module/cache/config/security paths and approved scoped host execution:
`swift-build.log`, `swift-test.log`;exit0. No new warnings. `git diff --check` passes.

## Next action

Producer independently qualifies its repaired long-label rendering and supplies a
completed source-pinned bundle when authorized. NUIAK then checks genuine bytes,
visible labels/geometry and overlaps with existing development groups. No recapture,
runtime change or training was requested/executed here. APPEAR-EVAL-RESERVE remains
blocked on untouched source allocation; this extension does not close those slots.

Public focus-backend provenance/report-only verification acceptance is a separate
producer request; this receipt does not claim that part of the package is accepted.
Original corrected-catalog image archive likewise remains separate from this metadata
receipt. No peer file was deleted and no new cleanup action was executed.

Worker/model/fixture guidance kept integrity, test-only software and genuine
qualification separate. See coordination.md for exact publication/readback state.
