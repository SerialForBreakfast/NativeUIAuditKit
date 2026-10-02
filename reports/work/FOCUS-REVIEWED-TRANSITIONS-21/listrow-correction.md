# Approved Settings row-type correction — October 2, 2026 PDT

Maintainer instruction: “Ok. you may make the data uniform for listrow with human
approval for this correction.” Applies to the20`focus:otherFocusable` controls in
recorded-378 and recorded-391 of the seven-frame Settings batch. All become
`listRow`. Preserve every rectangle, ID, focus flag and other review flag.

Source human revision:
`reports/work/FOCUS-CAMPAIGN-09/artifacts/settings-review/review-revisions/20261002T070352Z-b8e0e019/revision/revision.json`.
Retain that revision unchanged. Verify the working files match its snapshots before
editing. Save a new revision through the existing review writer, attribute the
correction to this explicit human instruction, and preserve prior completeness only
after checking that frame membership, geometry and focus are unchanged. Run existing
revision validation and production crop QA on the corrected revision.

## Completed

- Working editor was closed; all seven JSON files matched the original immutable
  human snapshots before editing. Exactly20labels changed across the two frames.
- New revision: `reports/work/FOCUS-CAMPAIGN-09/artifacts/settings-review/review-revisions/20261002-listrow-approved/revision/revision.json`.
  Source revision remains byte-valid. All72controls now use`listRow`; bounds,
  IDs, focus states and other review flags match the prior approved revision.
- Existing seven-frame completeness approval carried forward after verifying the
  label-only difference; provenance is in the adjacent`correction-receipt.json`.
- [Production crop QA](artifacts/listrow-crop-qa/crop-qa.json):72/72pass.
- [Reviewed readiness](artifacts/listrow-reviewed-readiness.json):7of14timing-ready
  actions now have both endpoints annotated, up from0. Screen correspondence and
  geometric matching remain the next evaluation steps.
