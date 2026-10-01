# Verification

All commands from repository root with PYTHONDONTWRITEBYTECODE=1 and
PYTHONPATH=scripts. Output/caches remain project-local.

- Discovery actual CLI: `.venv-review/bin/python scripts/focus_retained_next.py
  --source dataset/tvos_captures/human-real10-20260929/ttr-human-focus-office-e93b12da-20260929/verified-export-final
  --output reports/work/FOCUS-RETAINED-NEXT-15/results`.
  Discovery completed. Initial audit exposed differing pixel-hash field locations;
  corrected audit accepts the explicit root/crop field contract and rejects missing
  hashes. Final direct `audit` output is results/training-audit-final.json.
- Existing `human_recording_review.py` CLI, `--include-unverified`, selection
  `598:paramount-poster-contrast,728:paramount-hero-button,811:paramount-news-artwork,895:paramount-profile-contrast`.
  Final batch validated; prepare_review and experiment_proposal called against its
  exact batch reference. Original candidate883 retained only in superseded preparation.
- `.venv-yolo/bin/python -m unittest scripts.test_focus_retained_next
  scripts.test_human_recording_review scripts.test_focus_full_fit_experiment`:
  exit0,21distinct tests, python-tests-unique.log. Earlier failure logs retained:
  review interpreter lacks Torch; one negative fixture initially tried exclusive
  creation instead of modifying its own fixture. Both addressed; no real labels edited.
- Existing trainer preflight with `--experiment-arm full-corpus-fit --name
  fdr020-full-corpus-fit --experiment-protocol
  reports/work/FOCUS-FULL-FIT-03/frozen/protocol.json --preflight` under .venv-yolo:
  exit2/output_collision, after input validation. No execution/output replacement.
- Same real CLI with experiment-proposal-final.json and proposal-preflight-only:
  exit2/changed_protocol. The proposal is deliberately not an executable protocol;
  this establishes rejection only, not changed-corpus qualification.
- Offline `swift build` and `swift test` with --disable-automatic-resolution and
  project-local cache/config/security/module/temp paths: exit0,14XCTest plus109Swift
  Testing tests. Final logs: swift-build-final.log, swift-test-final.log.
- `git diff --check`: pass. No git write commands.

No new model inference, corpus training, capture, device operation or production
crop regeneration. Existing CPU-generated unit-loop fixtures are software tests.
Preset registration uses existing human_review_presets.save under its project-local
namespace; four packet15 names, no old presets overwritten. No annotation UI launched.
Explicit caches are local; Swift host escalation uses the established offline setup.
