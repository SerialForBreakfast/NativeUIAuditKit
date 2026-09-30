# Retained integration and validation readiness

2026-09-30UTC. Base c63bb30; previous annotation/geometry worktree changes preserved.

| Outcome | Evidence-backed result |
|---|---|
| Software |29focused Python/Qt tests;4negative amendment checks; offline build/123Swift tests pass |
| Data |1,947 admitted source/crop files hash/pixel checked; exact395training pairs preserved; one explicit human frame-completeness amendment |
| Integration |Retained TTR Vision preprocessing fails before sidecar delivery; geometry runtime unchanged |
| Model |No execution or promotion; cached FDR016 replay only, no eligible checkpoint |

## Validation gain without new annotation

Frozen baseline:453reviewed selection crops,40frame-policy records;13complete,
settled, unique-focus frames qualify for whole-frame decisions.27records do not;
5of those have no admitted candidates at all. All64prior selection exclusions remain.
Empty supported subsets are recorded, not indexed as though an image exists.

| Appearance | Training pairs | Real focused / unfocused crops | Baseline whole-frame cases | Amended cases |
|---|---:|---:|---:|---:|
| Buttons |133|3 / 7|0|1|
| Tabs |26|3 / 21|3|3|
| Artwork |150|18 / 255|2|2|
| Rows |86|9 / 116|6|6|
| Other |0|2 / 19|2|2|

User confirmed that exact photos:frame-004 contains only the two already-reviewed
focusable buttons, with a decorative Photos logo. `photos-confirmation.json` binds
that statement to original image hash and exact candidate IDs. `policy-amendment.json`
changes only that frame's completeness:14supported frames,26unavailable. No boxes,
focus labels, source images, crop membership or original protocol were changed.
This is development-exposed evidence, not a new independent source or final test.

Existing FDR016 final snapshot on the added case: correct Shared Albums ranks first,
score0.82638359, margin0.09536141; strict0.85 decision remains no_focus. It is not
a selected eligible checkpoint. Report original13frame results separately from the
amended14frame results; do not attribute a changed denominator to model improvement.
Button evidence now exists for full-frame regression, but one two-button screen
cannot establish broad production reliability.

## Actual TTR check

Shared producer snapshot remains01:50:12Z/expired02:20:12Z. Running GUI15122 and
Fixture15241 observed. On-disk helper and Fixture hashes match prior failed trial:
helper2ec0ea7110124746135edfec82ff9fad8f2bf4fb66d46bc280145bd828da6fc5;
Fixtureca554a6e568f1c4bc02024b811bc3f8e3833dc83ec8bf917348c8ad94ec3cdeb.
Disk identity is not loaded-image attestation. No new geometry delivery or capture.

Advertised `vision preprocess-pair` was attempted once on the original retained
job FBACA6BC-39CD-4774-9858-A0A60ED96431 synth-0 pair with repo-local output.
Request96037D91-6304-4557-B973-1DBF061848A2:exit69,serviceUnavailable,1ms,
nonretryable; no sidecar. Separate same-helper `status` succeeds18ms. Producer source
dispatches this command locally before coordinator IPC and maps untyped errors to
serviceUnavailable. Thus “open the app” is not a supported diagnosis. Actual underlying
file/provider failure remains unknown; do not claim a permissions cause or reset it.
Original18indexed export artifacts reverified unchanged (20delivery files including
index/receipt). No recapture, container workaround, security change or restart.

Optional import remains implemented/tested on source-shaped fixtures, but actual
producer delivery acceptance is blocked. New shared request asks for precise stage,
underlying error and supported retained-file path or hash-bound sidecar. This is
independent of missing artwork_geometry in the native capture brackets.

## Prioritized next work and experiment decision

1. **TTR geometry repair:** qualify one actual measured-artwork pair against wrapper
   and image-layout crops before remaining60captures. No unchanged retry. Existing
   geometry request retained. This is the main artwork-training data dependency.
2. **TTR optional import delivery:** resolve the retained-file failure or supply a
   sidecar for existing originals; then run the actual importer. No human recapture.
3. **Use the amended real baseline:**14complete frames across all four main strata,
   plus453crop diagnostics. Artwork still only2complete Home cases; richer retained
   media screens have explicit edge/competitor completeness gaps. Prefer targeted
   missing-box review on retained images, not another broad annotation batch. Keyboard
   glyph work remains a separate native/synthetic lane, not manual per-letter work.
4. **One changed-data proposal after geometry:** preserve395admitted pairs,9retention
   pairs, fixed0.85threshold and original membership; choose exact artwork additions/
   replacements only after measured crop QA. Keep encoder/loss changes separate.
   Bind the new features/cache and protocol to actual members and explicitly choose
   amended14frame development policy. No run ID or execution approval allocated now.
5. **Release testing remains conditional:** select only an eligible checkpoint with
   retention floor intact, show real-screen improvement, then separately authorize
   Core ML parity/export and TTR observer-mode testing.10independent-appearance/final-
   challenge blockers remain. No challenge images were inspected or scored.

No circular dependency: validation already exists and does not wait for a new model;
the next artwork experiment waits for actual geometry, not more benchmark tooling.
OCR import is optional and is not a prerequisite for training or evaluation.

## Reproduction, checks and remaining boundaries

Run from repository root with PYTHONPATH=scripts,PYTHONDONTWRITEBYTECODE=1 and the
existing project TMPDIR: `.venv-review/bin/python reports/work/FOCUS-INTEGRATION-03/audit.py`
then `amend.py`. Audit pins assembly/base/result/all admitted pixel inputs into
inputs.json; verifies unchanged selection, sealed membership,256px crops and no
exact cross-role pixel overlap. Exact pixel separation does not prove independence.
coverage.json accounts for every frame/stratum/blocker. Initial audit.log preserves
an empty-frame indexing failure; audit-final.log is the corrected successful run.
Amendment tests reject wrong image, wrong candidates, missing frame and unconfirmed
coverage and verify original policy unchanged. tests.log,swift-build.log,swift-test.log
retain passing checks. No package implementation changed this tranche.

Local offline scope complete for review. Actual sidecar/geometry acceptance blocked
on the exact producer deliverables above. No process or automatic monitoring remains.
Shared publication/readback documented in coordination.md; acknowledgment pending.
