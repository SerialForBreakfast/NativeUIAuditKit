# Campaign intake — complete software tranche

October 1, 2026 PDT. Owner: Codex. No capture, training, admission, export or promotion.

## Delivered

`scripts/fixture_campaign_intake.py` now turns the exact coverage plan and all
completed native bundles into one prefilled annotation review. It verifies planned
recipe/target membership, protected-image exclusion, measured body/visibility,
production crops and family × focus sample coverage. Missing, duplicate, extra or
unresolved evidence blocks completion. No wrapper-bound fallback.

One command handles the campaign; one queue opens all selected frames together.
Default eight samples cover both target states across four families. Matching
duplicate pixels do not multiply review; conflicting annotations are excluded.
Per-stratum denominators/probabilities and all findings remain available. Eight
samples do not establish a high-confidence corpus-wide defect bound. Optional
targeted exceptions are separate from random-sample statistics.

Resume verifies pinned inputs, implementation, completion seal and immutable file
membership/hashes. Human editor changes survive. Interrupted attempts are retained
and cannot be mistaken for completed output; a new attempt is explicit.

[Commands and limits](../../../Research/Plans/FocusCampaignIntake19.md).

## Acceptance evidence

| Requirement | Result |
|---|---|
| Actual CLI plus invalid/partial/tampered/locked/resume cases | Included in103passing Python tests; [log](artifacts/integrated-tests.log) |
| Campaign-scale intake and production cropping | 48generated cases,96frames,192/192Swift crops,8selected frames; identical completed resume passes; [result](artifacts/scale48/final-verification.json) |
| Actual annotator integration | Qt offscreen opens/navigates all8 selected frames; Finish review lists8; no approval; [result](artifacts/qt-scale48.json) |
| Retained compatibility | Existing50frame batch and11selected IDs validate unchanged; [result](artifacts/legacy-replay.json) |
| Offline package checks | Build clean;134Swift tests pass (14XCTest+120Swift Testing); [build](artifacts/swift-build.log), [tests](artifacts/swift-test.log) |

Scale-test pixels are tiny generated software fixtures, not TTR-rendered originals,
training data or production throughput evidence. Offscreen Qt does not substitute
for Cocoa startup verification when the actual annotation window is opened.
The last change strengthened the completion marker; final48case replay includes it.

## Remaining boundary and next action

At04:17UTC, producer status remained the02:55UTC report of48appearance pairs and
16transitions locally verified; no new structural data archive was advertised.
Its expiry passed; it is historical evidence, not current device availability.
The exact running source revision and retained Vision file-access route remain
separate open requests. This tranche does not need optional Vision to prepare review.

Next: receive the already captured structural originals through the existing
size/hash receipt flow, run this full campaign intake, and show one real sampled
review. Preserve source/calibration ancestry; human confirmation and any subsequent
training-role decision remain explicit. No producer build request or unchanged
recapture is needed. Existing request `nuiak-20261002-local18-captured-data-export`
remains the delivery request; no duplicate request or background monitor added.
