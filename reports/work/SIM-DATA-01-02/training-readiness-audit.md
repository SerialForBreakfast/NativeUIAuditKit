# Training-readiness audit — 2026-09-21

## Runtime evidence

Matching helper SHA256 25fc417aac660d4df9d5d5531c0bcc213c669d05911007e1d4d3605c5cb0dd6e;
simulator 9026ECA9-77DB-4AE6-8FE6-BB239E9571FA, tvOS26.5/Xcode26.6.
Fixture installed but initially not running/no8080 listener. One supported
`simulator teardown-check --variant session_only` completed in13.9s at21:06:37,
operation B55B5825-A2A1-420C-9832-8EA67EB63553. Input count0, runner stopped,
control_verified=false, built-in post_teardown_health=not_verified.

Independent postflight: PID37989 owns8080 and executable is in this exact simulator's
Fixture bundle. Fresh helper env/scene at21:07:27 succeeded:9 elements, settled,
1920×1080 reported bounds, scale2, Fixture1.0/build1. This proves observed responsiveness,
not indefinite crash-free operation. Metadata remains reported/not-authenticated.
Fresh readiness21:07:09 ready/ownership clear, request DBBB911A-EEED-4C39-8054-FBCF201A52B8.

One two-element high_contrast/action_dialog/seed7 batch attempted against verified
http://127.0.0.1:8080 and explicit UUID; recipe directory
reports/work/OFFICE-FOCUS-SMOKE/recipes; new gitignored destination
dataset/tvos_captures/simulator/smoke-20260921T2108 with existing parent.
At21:07:48 validation rejected outputOutsideProject, exit64, retryable=false,
request78A4739C-0CD9-4229-A21B-D17B91F53565, duration6ms. No capture/recipe mutation.
No retry or manual container staging. App-managed diagnostics access does not grant
NUIAK export access. Source harvestProjectRoot selects the helper workspace unless
explicit granted project mode exists; changing --project also changes routing.
Need a supported simulator job/export path or deliberately approved project/grant
setup. Office-only prepare/run-job cannot substitute. No SSH or permission bypass.
Fixture remains running; no simulator shutdown or unrelated session stop sent.

## Corpus inventory

Read-only dataset/focus_ring/focus_dataset_manifest.json inventory: version1.0,
1500 complete pairs, train1201/val164/test135, all dark, scene=TVTestRigFixture.
Classes: collectionItem1055, secondaryButton215, primaryButton225, segmentedControl5.
Crop paths exist; hashes/labels not requalified. sourceKind/labelSource absent.
Preserve historical corpus. It does not establish ≥6000 pairs, six scene quotas,
20% light/highContrast each, or ≥100 verified held-out negatives across four strata.

## Launch-path findings (not production edits)

1. harvest_focus_pairs.extract_fixture_bundle uses the focused box for BOTH frames.
   File/hash-only validatedUnfocusedEvidence does not prove per-frame element focus.
   Require actual focused/unfocused geometry and callback-ground-truth regression cases.
2. focus_ring_readiness.validate rejects every repeated seed, even distinct pairs in
   one partition. CLI normalization does not preserve meaningful partition validation.
3. Theme thresholds use20% of MIN, not actual totals. An in-memory probe accepted
   4000 gridMatrix pairs with400 light/400 highContrast (10% each).
4. Probe also accepted6000 all-training rows with100 flagged negatives across four
   strata and nonexistent image paths. This metadata validator cannot establish launch
   eligibility; require actual bytes/hash/truth and held-out membership checks upstream.
5. Simulator manifest emits validation; trainer loads val then silently falls back to
   training samples. Require explicit partition mapping and independent nonempty validation.
6. Trainer silently omits missing crop paths, permits existing run destinations, lacks
   mandatory corpus-eligibility preflight and evaluates test hard negatives each epoch.
   Preserve complete membership/output isolation and untouched test until final evaluation.
7. Trainer --dry-run performs one training epoch when data exists; empty data says
   Script OK. Do not execute as config validation; separate non-training preflight.

Verification: source inspection, read-only manifest count and in-memory validate probes.
Existing test_focus_ring_readiness7/7 pass; those green tests do not cover these defects.
First probe construction underfilled a theme and correctly failed; corrected construction
preserved required minimum coverage and demonstrated the false passes above.
No training, inference or implementation code edits; Swift checks not applicable.

Concurrent PER-04 physical-only readiness delivery discovered during audit; preserve
its owner/files and review separately. Its handoff does not claim to integrate these
simulator extraction/trainer paths. Do not overwrite another worker's implementation.

## Gate and next action

Runtime/Fixture response evidenced; capture/export blocked. No eligible new corpus,
control benchmark or model gate established. Corrective software scope needs architect
integration review alongside PER-04, not acceptance based on passing metadata tests.
After supported export: genuine smoke intake → authorized42-recipe pilot → shipped
baseline → separately authorized qualified≥6000 corpus → logged30-epoch candidate.
All six FocusRing gates and≤5MB export remain; no automatic capture scale-up/training.
Producer/export authority and complete reviewed data remain concrete launch blockers.
