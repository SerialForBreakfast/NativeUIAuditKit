# Structural corpus intake and Settings comparison

October 2, 2026. The local intake and fixed-signal comparison are complete. Human
sample acceptance and producer transition-contract repair are the next dependencies.

## Useful results

- Received DATA64r1: **865,332,309 bytes**, archive hash verified before extraction
  and retained locally. All **838 manifest-listed files plus the manifest** verified.
- All **48 appearance cases / 96 frames / 264 production crops** passed diagnostic
  intake and crop QA. Four layout families each contribute 12 cases. Actual pixels
  supply **48 unique target pairs / 96 proposed target controls**, with zero blocked
  target pairs. This replaces the earlier software-fixture-only readiness evidence.
- Prepared **one eight-frame review batch**, balanced across four layout families
  and focused/unfocused targets. Rectangles are prefilled. Producer validation role
  is preserved until the maintainer chooses its use; these related synthetic layouts
  are not an independent real-app test set.
- Native OCR resolved seven reviewed recorded actions: five same-screen pairs and
  two genuine page changes. The page changes are excluded from same-screen scoring.

## What the Settings experiment tells us

The fixed brightness rule correctly found both actual moves:

| Frames | Lost focus | Gained focus |
|---|---|---|
|299 → 303|Notifications|AirPlay and Apple Home|
|409 → 416|Motion|Audio Descriptions|

Across the five same-screen pairs, 50 controls were considered; 48 had unique OCR
correspondence and two did not. Brightness and combined each made four correct
control-change decisions, zero wrong decisions and 44 abstentions. Growth made no
decisions: the wide Settings rows have clipped crop context, which suppresses that
signal. The 44 abstentions are unchanged-focus controls, including three tracking
failures; the rule does not reliably certify unchanged focus yet.

This is a useful narrow result, **not 100% overall accuracy**: coverage is 4/50=8%,
and only two real focus moves were exercised. OCR matches were derived without focus
labels; human labels supplied separate scoring. Repeatedly examined development
screens and incomplete endpoint coverage prevent independent or whole-screen claims.

## Native transition findings for TTR

The separate 16 native transition pairs fail the existing strict scene contract:

1. All inspected endpoint inventories repeat child ID `film` three times, under
   different parents. Emit stable scene-unique IDs, for example parent-scoped IDs,
   preserving references. Identical decorative content still needs distinct identity.
2. Eight scroll pairs contain planned IDs absent from visible `elements` (for example
   `item-2` before scrolling, `item-0` afterward). This may be intentional full-plan
   versus visible-inventory semantics, not bad focus. Clarify that contract and provide
   explicit off-screen membership/exclusions so our transition validator can support
   it without silently dropping the current membership check.

Eight first fail on duplicate IDs; eight first fail on planned membership. All 16
remain unscored. Original bytes are preserved. Repair/clarification can be delivered
through source commit/push and a corrected data handoff; local builds remain ours.
Capture receipts also lack an independent rendered-image digest, so current evidence
is producer-indexed hashes plus host brackets, not independent image attestation.

## Evidence

- [Exact receipt](artifacts/transfer-receipt.json), [manifest check](artifacts/manifest-verification.json).
- [Campaign completion](artifacts/campaign-intake/completed.json),
  [264 crops](artifacts/campaign-intake/attempt-001/crops/crop-qa.json),
  [structural readiness](artifacts/structural-readiness.json).
- [Eight-frame queue](artifacts/campaign-intake/attempt-001/audit/combined-queue.json).
- [Review instructions](review.md), [eight-frame annotator check](artifacts/review-ui/result.json),
  [published TTR receipt/request](coordination.md).
- [Settings comparison](artifacts/settings-comparison/comparison.md),
  [source-bound OCR](artifacts/settings-ocr/semantics.json).
- [Native transition contract audit](artifacts/native-transition-contract-audit/audit.json).
- [98 regression tests](artifacts/regression-tests-final.log); offline
  [Swift build](artifacts/swift-build.log) and [134 Swift tests](artifacts/swift-test.log).

Initial test invocation used four nonexistent module names; the corrected discovered
suite passes. Earlier audit output is retained; the final audit adds source-level
observations without qualifying rejected records. Model quality/export is unchanged.

## Next substantial tranche

1. Review the eight prefilled frames together and choose whether these 48 target pairs
   may become development-training data. Then exact admission, encoding and a matched
   changed-data comparison can proceed under an explicitly assigned execution scope.
2. Develop and test an unchanged-focus decision for Settings, with motion/content-change
   negatives and the same before/after identity separation. Measure wrong decisions as
   well as coverage; use these records for development, not an independent benchmark.
3. Consume TTR's semantic-ID repair and clarify visible versus planned membership,
   replay all 16 native pairs, then compare brightness/growth/combined on that broader
   transition set. Source delivery and annotation review can proceed independently.
