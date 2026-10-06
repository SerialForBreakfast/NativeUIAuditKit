# Native scroll24 intake — October 6

## Source reconciliation and targeted adapter

Correction to the initial checkout-only blocker: read-only GitHub API resolves
published550a2d374801fb99120d3aed4168c1de9e7ef83d.13of20handoff source hashes match,
including FixtureAppearance, native widgets and FocusSweepController. Seven capture/
telemetry/helper files differ; full historical build binding remains unresolved.
Exact file comparison is retained in `artifacts/source55001/binding.json`.

Implement strict nativeTable-v3 recipe parsing/canonicalization from the matching
FixtureAppearance hash143e4da4fbef5119a2df41b8518a50db2561eab2bc128e6671f2428ec9908057:
required boolean richContent, integer viewport360–860 with existing screen bounds,
artwork city/orbit/collage/checkerboard (published FixtureComposition.Design),
selectedIndex0–5, six elements and all existing layout constraints. Preserve v1/v2
bytes and reject artwork on older versions. This is recipe compatibility only;
do not widen directional/scroll/callback admission until those contracts qualify.

Consumed the already-published TTR handoff while Big Dog's matched216 experiment
continues independently. No capture, inference, training or data-role change.

- Exact archive13,182,912bytes, SHA256
  71127ae9fc2e5bdc84aac034243ba3f22744083bc6740ebb8c9f54d98751b6ad.
- Verified SMB endpoint, sufficient local space, immutable copy and source/readback hashes.
- Existing bounded archive checker accepted432members/29,079,185expanded bytes;
  explicit256MiB/600member cap, no links/special files/traversal or overwrites.
- 395 inventory files match exact member set, sizes and hashes. Existing selection
  verifier reconciles completed4-case pilot and20-case remaining receipts, manifest
  hashes and all24case member inventories. All48endpoint PNGs decode.
- 8 scroll_moved,8 scroll_unchanged,8 content_only. These are producer condition names,
  not independently verified focus transitions. Shared procedural-renderer ancestry
  and calibration roles retained.

Actual `focus_corrected_transition_audit.validate_case` rejects24/24 at
`invalid_metadata: canvas_selectedIndex`. NativeTable version3 is outside the
source-pinned table1/2 contract, matching the existing RESIDUAL160 blocker. Local
TTR HEAD remains46dce7b3a79e4f17af49bc0324d4aeba3cc0958d. Do not strip fields,
change versions or substitute requested state for observed labels to pass intake.

Report `artifacts/native-scroll24-r1/intake01.json`, SHA256
e9a590a9c0e3653be71c91beed4f7b7f9a74994fb8f2d474ddf4a9e96b543780.
Software compatibility blocked; transfer/inventory checks passed; data admission,
native semantic qualification and model gates not assessed. No source code changed,
so prior integrated build evidence remains applicable; existing validators ran here.

Next substantial focus tranche: reconcile published producer source for both native24
handoffs, implement the narrowly versioned adapter and adversarial tests, verify
callbacks/scroll/crop geometry, then evaluate retained models on calibration-only
membership. Reuse received bytes; do not wait for another collection campaign.

Receipt and blocker published/read back at
`nuiak/responses/nuiak-20261006-signal95-scroll24-feedback.json`,1715bytes,
SHA2563d98954960155c176feb8df126c4a91c75c08f68579953bcc1d8b332f08a11d3.
Peer acknowledgment and sender cleanup pending; no peer file deleted.

## Superseding software result

Strict v3 adapter passes19focused tests, preserving v1/v2 null/canonical behavior.
All24actual scroll recipes reproduce their producer hash; existing transition audit
passes24/24 without changes to geometry, callbacks, cleanup or scroll checks.
Report `artifacts/native-scroll24-r1/recipe-v3-review02.json`, SHA256
e3953a66407458e919451ce39a6d76ffd4639ccf318944a4215bee921b2da116.
Companion retained appearance24:24recipe hashes reproduce,16unchanged/content cases
pass,8focus moves remain rejected by unchanged directional_source_contract.
That separate source gate was not broadened merely to obtain a pass.

Remaining binding differences: SyntheticCampaignModels, FixtureHarvestFailureDiagnostic,
FixtureBatchHarvestEngine, ProceduralSceneView, FixtureTelemetryServer, StableCLIHelp,
and native-focus-contract.rb. Request historical source/build reconciliation, not
another source download, new binary or recapture. Model gates remain unassessed.

Offline Swift build and140Swift Testing+14XCTest pass (`.build/native-v3-*`);
diff whitespace check passes. Corrected status published/read back at
`nuiak/responses/nuiak-20261006-signal95-source-reconciled.json`,1827bytes,
SHA256dbb438b0ae0f39cd05cca59cba9c2edcb7aa3b573f2cbb28286d952667b1b1cf.
Acknowledgment remains pending. No incoming or peer source executed.

Directional compatibility review: matching FixtureNativeWidgets source at550a2d37
retains UIKit didUpdateFocus callback recording with generation/timestamp/previous/
next identity, allows scrolling for versions>=2, and registers the same viewport.
Version3 adds seeded artwork and declared theme handling; requested focus remains
separate from UIFocusSystem observation. Extend the directional recipe-version gate
to3 only; retain all existing action, endpoint, identity, cleanup and focus checks.
Do not assert stationary navigation: observed scroll remains an independent dimension.
Historical executable binding and training admission are still separate prerequisites.

Directional adapter complete: all48cases across both handoffs now pass the existing
validator. Recorded observations independently separate8focus changes without scroll,
8with scroll,8scroll-only intervals,16content-only intervals and8boundary no-ops.
Do not interpret `scroll_unchanged` as stationary pixels: its eight intervals have
unchanged focus but observed scrolling. No requested condition was substituted for
the actual endpoint identity/offset comparison.
Report `artifacts/native48-validation03.json`, SHA256
60964dba36da3504b60a15aa9e3147c7fc923a256dcb1a68b8d3c1e4051049fa.
20focused tests include all8retained directional cases plus adverse cleanup/mutation
records; tests pass. Roles remain calibration, historical executable binding pending.
Offline build and140Swift Testing+14XCTest pass (`.build/native-directional-*`).
Combined status published/read back at
`nuiak/responses/nuiak-20261006-signal95-native48-compatible.json`,1466bytes,
SHA256096ed51b874eb335060da5d0b9dd4668f2d56d17292b5cd787906891b6019f3d.
Peer acknowledgment remains pending. Local queue now reflects current blockers,
not the superseded checkout/recipe/directional limitations.

## Input-signal diagnostic — no model execution

Reused the existing192×128 letterbox encoder on all48verified pairs, with no changes
to source pixels, labels or roles. All8boundary no-ops have identical encoded
endpoints; all40other pairs remain nonidentical. No exact duplicate pair encodings
or opposite-reported-label encoding collisions. This rules out total signal erasure
for these examples, not loss of useful subtle features or poor generalization.

| Recorded condition | Pairs | Median mean absolute RGB difference | Median changed pixel fraction |
|---|---:|---:|---:|
| Focus moved, no scroll |8|0.027668|0.092590|
| Focus moved with scroll |8|0.001679|0.026632|
| Same focus with scroll |8|0.024312|0.095093|
| Appearance content-only |8|0.000323|0.004028|
| Scroll-matrix content-only |8|0.000272|0.004049|
| Boundary no-op |8|0|0|

RGB differences use normalized0–1values; changed fraction counts exact nonzero
encoded pixels and includes letterbox area. Focus-changing scroll pairs retain equal
reported focus boxes; unchanged-focus scroll pairs move those boxes. Their median
difference magnitudes invert a simple more-change-means-focus-change heuristic by
about14.5×. No accuracy, threshold optimum or label authenticity follows from this.
Next qualified evaluation must report these strata separately; do not pool their
success rates or train a difference/box-motion rule from the condition names.

Report `artifacts/native48-signal04.json`, SHA256
8dc3fc58758b34a407717126281fae64c5882852fa51106d93a26d9cf26e06d6.
Existing encoder identity and per-case input hashes retained. No source changes or
new model run, so integrated build evidence reused. Prior model-training gates remain.

## Retained-model inspection

Separate preregistered CPU pass completed on48cases in4.661seconds, existing encoder,
two threads/batch8 and0.15/0.85decisions. DTM053/054checkpoint hashes verified before
and after, weights-only load, existing model/scorer, no training or geometry outputs.
Both models report identical decisions: no-change on8scroll_moved, change on
8scroll_unchanged, change on8appearance focus_moved, no-change on16content-only and
8boundary cases. No abstentions. Retained probability vectors and exact protocol in
`artifacts/native48-model-inspection05/`; result SHA256
3ed8466a01a9a1d79b493ba450ee522de7501959bfc11d7534a5cf055f149e35.

These are observations against producer conditions, not qualified accuracy. The
pattern supports testing motion/appearance shortcut learning once source identity
qualifies, not another photometric sweep or more generic artwork. Do not train
on these calibration cases without a separate evidence-backed role decision and
reserved connected groups. Shipped weights unchanged; no navigation authority.
Published/read back `nuiak/responses/nuiak-20261006-signal95-model-inspection.json`,
1667bytes,SHA2565fd3d8d29fb2ad27614464fb24a5d901c091b5a30c1d02f2bb1912a67f6169d2.
Acknowledgment pending; no duplicate generation or compute request created.
