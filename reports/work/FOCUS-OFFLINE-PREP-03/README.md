# Matched-trial consumer

This is local diagnostic preparation, not capture authorization or admission.
Pinned producer proposal: `producer-proposal.json`, SHA256
`d0f88e22f28fdc97f627f6cbcdc2efacdd13654667d55a641fef87fb811c00e6`.
Read from producer archive7564bytes, SHA256
`851dd2895e553335f2b31820a3ce6a00b314dc5749f8fdce63d5e576beb88749`.
Only proposal JSON was retained; no copied-archive receipt or sender cleanup authority.

## Delivery and acceptance

Use existing named-file verified receipt and safe bounded archive extraction first.
Do not point this CLI at staging/partial directories. Keep originals immutable.
An extracted bundle per scene must contain its original dataset-index.json and
completed harvest-receipt.json. Build one local descriptor with this shape:

```json
{
  "version": "focus-trial-delivery-v1",
  "cases": [{
    "caseID": "icons-4-no-labels-standard",
    "index": {"path": "PROJECT_RELATIVE/dataset-index.json", "sha256": "EXACT_HASH"},
    "receipt": {"path": "PROJECT_RELATIVE/harvest-receipt.json", "sha256": "EXACT_HASH"}
  }]
}
```

Supply only delivered cases. Missing scenes stay missing; do not fabricate an empty
receipt. Receipt/index must share a directory. Existing validation checks indexed
file sizes/hashes, completed receipt, native brackets and protected splits. The
trial adapter adds exact recipe hashes, exhaustive targets, all visible competitors
and next-in-sweep competitor checks before crop generation.

```sh
PYTHONDONTWRITEBYTECODE=1 .venv-review/bin/python scripts/focus_matched_trial.py \
  --proposal reports/work/FOCUS-OFFLINE-PREP-03/producer-proposal.json \
  --proposal-sha256 d0f88e22f28fdc97f627f6cbcdc2efacdd13654667d55a641fef87fb811c00e6 \
  --delivery PROJECT_RELATIVE_DELIVERY.json \
  --output reports/work/FOCUS-OFFLINE-PREP-03/NEW_RECEIPT_REVIEW
```

Omit --delivery for plan/accounting only. Outputs must be new. Exit2 means at least
one case is missing/failed; review.json accounts for all eight cases and64expected
pairs. Each successful case contains unchanged test-only intake, wrapper/layout
production crops and numbered focused/unfocused sheets. Cyan frame boxes identify
wrapper geometry; magenta identifies nominal artwork layout. Actual geometry,
common-target membership and unmatched-competitor flags are retained in review.json.
Unavailable layout stays visibly blocked, with no wrapper fallback.

Exit0 means all cases were prepared, NOT that visual geometry passed. Every target
remains review=pending, liveQualified=false, trainingAdmission=false. Review body
enclosure, caption overlap, competitor intrusion and measured dimensions before
any later admission proposal.32common records are not32controlled experiments;
only8density comparisons share competitors, and size/position may still vary.

No archive transport, TTR dispatch, model inference, annotations or training are
performed by this CLI. Existing whole-bundle validation is reused, not replaced.
Native body/presentation bounds remain unavailable. background objects and new
producer schemas remain rejected until explicitly supported.

## Reproduction

`focus_duplicate_sensitivity.py --protocol ... --result ... --output NEW.json`
replays cached scores through existing metrics, validating actual crop hashes and
duplicate score/label consistency. Official denominators and frame policies stay
unchanged. `additions.py` regenerates the exact proposal from pinned source members;
it does not create training approval or an executable training assembly.
