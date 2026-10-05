# IOS-DIAG-171 — residual diagnosis and batch plan

Completed October5,2026. No capture, inference, training, promotion or Git writes.

## Findings

All96page probes and both class operational counts across2400retained images were
validated against170's sealed artifacts. Matching uses confidence≥.25andIoU≥.5.
Run018 left-position48:38absent candidates,5localization misses,5correct boxes
below threshold,0operating hits. Centered non-native24:24hits; centered native24:
10hits,12absent,2low-confidence matches. “Absent” means absent from the retained
prediction export, not proof of no internal model activation.

CancelAction:80/80truth matched in both arms; false positives171→304.
MapView:100/100truth matched in both arms; false positives1→30.
Thus these operational regressions are false positives, not recall loss. This does
not attribute the entire AP delta to the single operating point or identify its
causal visual feature. Per-image identities/counts remain in the diagnosis artifact.

## Independent companion

Frozen288-frame native plan:48existing training parent groups×threeplacements×two
tints. No development probe reuse; requires full-frame annotations. Source recipes
only contain scale2/light and scale3/dark for each family; plan records this coupling
instead of claiming an eight-cell crossed design. Plan is explicitly non-executable,
not training eligible, and not independent evaluation evidence.

## Evidence and checks

- `artifacts/diagnosis.json` SHA256:04d1dffd8c7b7bed594c90111a687ed9702c38d01ff237913e819e5d99e020a7.
- `artifacts/native-batch-plan.json` SHA256:3c393c6963a7d3f62f3a02fe942397f854b972d273ab412ba7d29359ab33e390.
- Actual `scripts/diagnostic171.py` exit0; `.build/diagnostic171.log`.
-13focused tests pass; `.build/diagnostic171-tests.log`. Includes one-to-one matching,
  threshold/empty results, deterministic ancestry, invalid source roles/metadata,
  collision, changed report seal and missing prediction rejection at the entrypoint.
- Offline Swift build/test exit0; `.build/diagnostic171-{build,swift-tests}.log`.
- No repeated model inference or full image decoding. This is retained-evidence work;
  no external wait or capture time. No timing speedup claim is made.

Software verified; new data eligibility pending; no new native integration; model
gates not assessed. Broad pre-existing changes preserved. Failed initial planner
assumed nonexistent joint coverage; no artifacts were published by that attempt.

TTR local source remains46dce7b3a79e4f17af49bc0324d4aeba3cc0958d; native24 intake
still awaits source-backed v3 compatibility. Local iOS findings do not change its
next action; no redundant SMB publication. Next substantial tranche:IOS-NATIVE-172
renderer extension, qualification and single-session288-frame acquisition/audit,
followed by one pinned candidate only after admission. No blind epoch extension.
