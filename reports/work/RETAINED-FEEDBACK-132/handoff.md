# Retained feedback132 — October4

| Outcome | Result |
|---|---|
| Software verified |13focused Python tests pass. Xcode27 build passed in131; explicit serial native suite138/139, one reproducible ROI OCR failure. Full gate incomplete.|
| Data eligible |Integrity and inspection pass; existing exposed journey roles retained. No training/final admission or reviewed body bounds.|
| Integration qualified |All22retained model decisions reproduce on byte-exact encoded tensors. Live/runtime integration not attempted.|
| Model gate passed |Not assessed; DTM030regressions reproduced, no promotion.|

Prior131changes preserved. This tranche adds bounded intake/replay tooling and
standalone read-only ROI diagnostics, not another trainer or production policy.

## Intake and evidence

Existing `shared_transfer.py --action receive --execute` copied both named archives
to new ignored local artifacts. Exact transactions in `survey26.json`, `navbar29.json`.
Survey26:39,544,029bytes,22files,7PNGs. Navbar29:11,375,272bytes,16files,2PNGs.
Each archive SHA256 matches published metadata. Bounded extractor reuses existing
safe_members checks; disallows links/traversal/duplicates/collisions, checks capacity,
hashes each member, verifies PNG decoding/dimensions and hash-based filenames.
Expanded totals39,657,674 and11,405,523bytes. Complete manifest membership then
independently checked at replay; originals and private bindings remain local/ignored.

CLI: `scripts/retained_feedback132.py <transaction> <new-output>` and
`--review <extracted-root> <new-report>`, resident `.venv-yolo/bin/python`,
`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts TMPDIR="$PWD/.build"`; all exit0.
Reports `artifacts/{survey26,navbar29}-review-v2.json` pin script, manifest and
checkpoint hashes. Earlier review outputs preserved. Contact sheets inspected once
for semantic failure analysis, not used as labels or model inputs.

## Model/visual review

DTM025 and DTM030: all8Survey26 and3Navbar29 interval decisions reproduce.
Encoded SHA256 matches the original peer result for every model/pair. Maximum
probability deltas9.022e-10(Survey26) and1.747e-10(Navbar29). This establishes
input/output parity, not native-hint accuracy. Producer CoreML(cpuOnly) versus local
PyTorch checkpoints; no CoreML recompilation or new export needed for this check.

Survey26 operation21BC8868-A77A-47B1-929A-E55F4A0B3EB0:

-5→6: Accessibility/Subtitles row to Subtitles and Captioning screen, focused Closed
  Captions and SDH. A screen transition, not an isolated within-screen movement.
-7→8: Closed Captions and SDH → Style row; preview artwork also appears.
-8→9: Style row → Style screen, focused Transparent Background. Screen transition.
-DTM025changed/DTM030unchanged on all three.6→7identical bytes correctly unchanged.
-Other four intervals both changed;2→3and3→4native identity unavailable remain unknown
  despite visible Balance screen entry/return. No fabricated native label.

Navbar29 operation321D82A9-36FE-4259-8B2F-006F73160F4D:

-15→16: Hover Text row → top-right Edit button.17→18returns to row.
-DTM025changed/DTM030unchanged on both;16→17identical bytes unchanged for both.
-Two unique PNGs support three intervals, not three independent samples.

Keep both handoffs exposed/diagnostic and related journey variants grouped. Visual
inspection supports these descriptions only; no precise body boxes or final labels
were produced. Preserve DTM025/030passive use; don't replace on aggregate training fit.

## Native test diagnosis

`.build/feedback132-vision-isolated.log`:8FrameSimilarity tests pass(0.168s).
Default full comparison stalls again; only owned runner13228/helper13246 stopped.
`.build/feedback132-explicit-serial.log`: explicit `swift test --skip-build
--no-parallel --disable-sandbox --skip-update` with existing project-local cache,
config/security/module-cache paths finishes.14XCTest plus124/125Swift tests pass.
Failed TextAnchorVerifierTests.roiScopedOCRFindsAnchorInsideRegion atline169:
expected verified, got unverified. Same isolated suite9/10pass in0.450s; failure
persists without inter-test concurrency. Coordinate-conversion and full-frame OCR
tests pass. No assumption of service corruption; no reset/reinstall/test weakening.
Standalone `scripts/diagnose_roi132.swift` reproduces exact Vision request options
and test ROI for identifying actual text differences, with project-local output.
It exits0: full-frame target is `toggle slider stepperControl`; scoped OCR returns
`toggle ' slider • stepperControl`. The current literal substring matcher therefore
rejects the added punctuation. Evidence `.build/feedback132-ocr-reproduction.log`.
This explains the assertion failure without claiming the concurrency stall has the
same cause. Do not silently strip all punctuation: legitimate punctuation-sensitive
anchors need an explicit matching policy and adversarial tests before a fix.

Python: `-m unittest scripts/test_retained_feedback132.py scripts/test_shadow_peer121.py
scripts/test_diagnose131.py` passes13tests(0.201s); real two-archive CLI/replay passes.
`git diff --check` passes. No Git writes, capture, model training or promotion.

## Coordination and next

Published/read back exact receipts:
`nuiak/responses/nuiak-20261004-survey26-copied-receipt.yaml` and
`nuiak/responses/nuiak-20261004-navbar29-copied-receipt.yaml`.
Owned RETAINED-FEEDBACK-132 entry published/read back in `nuiak/status.yaml`.
Other semantic fields preserved(hash e41a6fddef123a74f3c312665aa09ed6cb33ab465220a8edb4d61dabd436f945).
Sender cleanup/peer acknowledgment not yet observed; receiver deleted nothing.
No recapture request. Reviewed private data not copied into SMB status.

Next substantial tranche: include retained11intervals as exposed regression checks,
evaluate DTM031 then one preregistered feature-conditioned candidate, and complete
scoped OCR discrepancy diagnosis. Keep screen-change and same-screen focus metrics
distinct, preserve207original/226identity gates and independent final restrictions.
