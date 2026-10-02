# Native-focus spike: historical qualification and execution checkpoints

Current checkpoint,17:43UTC:500verified pairs/2,000crops,5.80GB received to USB;
serial generation and crop preparation continue. [Machine-readable progress](progress-500/summary.json)
and [optional random review](progress-500/review.md). Earlier
Fixture/delivery blockers in the historical record are resolved.

## Superseding check — October2, 09:13 PDT

User installed/restarted both applications. Helper hash now
`e19be3b0704beda737aa9f44a2d1562ce5f5d257d7f6143fdfeea257ac5deaf9`;
Fixture debug hash `e576de47ed820450c1e51ca47a5d6b8b7adedf60df586613e789fd1e89de8e64`.
Approved one-pair campaignEBFD748D-8318-4126-8621-A175E9000026 completed the formerly
failing structural home_icon case:1accepted,0rejected,5.69378s,16,236,934retained bytes.
Fresh settled scene reports measured rendered_body_geometry from
uikit_focused_frame_guide. All3bodies pass existing consumer geometry validation;
focused533.333×458.667 versus unfocused462.222×398.222pixels. Legacy artwork_geometry
still reports unmeasured layout bounds; consumers must use the additive rendered-body
field. The obsolete Fixture/structural-validation blocker is resolved for this case.

External export still fails persistenceFailed; the exact request
is recorded in [export envelope](runtime/updated-check/export.json). No exported
originals/paired crop or visual QA is claimed. Postflight ready/ownership clear;
no capture or training remains running. Next: qualify the existing retained-pair
delivery path, verify original/crop geometry, then resume scale-up. Exact Git build
provenance remains unverified; this result binds actual binaries and runtime fields.
[Updated check evidence](runtime/updated-check/).

October2,2026. ADR-0017 is accepted and linked into the dataset and retention policies.
The approved1,000training/250evaluation-pair experiment remains incomplete.

## Actual execution

- Verified running TTR PID36579 and its own bundled helper, SHA256
  `6ec7b851e7d741a76cf7323727b7bd7effdd99df81923d368fdf4b097455a87a`.
- Exact booted Simulator9026ECA9-77DB-4AE6-8FE6-BB239E9571FA, tvOS26.5,
  Xcode26.6. Readiness/companion/storage pass and ownership clear. Fixture endpoint
  responds, settled; VoiceOver/ReduceMotion/BoldText/darker-colors all reported false.
- Local USB is mounted APFS, approximately1.8TiB free; internal disk22GiB free.
  Large corpus directory already exists. No large dataset copied to internal storage.
- Structural-native campaign4D117D0A-7448-4AEC-92AB-3117F8000026: planner accepted;
  independently verified recipe hash; one case rejected at validation in0.00975s,
  `commandRejected/unclassified`. Zero accepted pairs. Preserve this failure.
- Compatibility campaignAD6860E4-0B60-4791-A1E3-7F43C8000026: one previously
  qualified canvas-v2/native_image recipe, explicit one-target limit,120s/128MiB
  cap. Completed1pair,0rejected,6.14908s case time,3,499,525retained bytes. Diagnostic
  repeat of existing recipe, not a new independent training/evaluation sample.
- Crucial post-capture telemetry: artwork_geometry is version1 layout bounds;
  `presentation_bounds_status=unavailable_native_effect_not_measured` and
  `source=artwork_layout_view_bounds`. Focused and unfocused cards both640×400.
  Current labels do not satisfy the repaired rendered-body contract. Native capture
  succeeds, but training-data geometry acceptance is blocked.
- Installed Fixture debug library SHA256
  `d4a037b7f46101e3f013bd3b39aac4a1acfbefc43cd7f5be53e31524429e76c8`, datedSep30.
  The adjacent local built Fixture has the same old build date. Date is supporting
  context, not proof of exact source revision. Configured TTR Git HEAD46dce7b lacks
  current campaign source. Newer structural source excerpt is not a complete build.

## Export boundary

Direct `campaign export` to USB and project destinations both return
`persistenceFailed`. TTR-owned exports succeed for both campaigns:

- `.tvtr/Evidence/nuiak-native26-4d117d0a`
- `.tvtr/Evidence/nuiak-native26-ad6860e4`

These are supported app-returned paths, not consumer receipts. A read of the supported
logs-path result and a directory listing of the failed diagnostic export did not
return; owned readers were interrupted. Consumer pixels/hash/crop QA remain unavailable.
No claim that USB permissions, TCC or filesystem type is the root cause. This matches
the independently tracked direct-writer failure, which is still open with TTR.

Postflight reports ready and persisted ownership clear; fresh Fixture scene is settled.
No background capture/training remains running. No files deleted or models changed.

## Resume conditions and useful next tranche

1. Obtain the published corrected host/Fixture source revision through Git and build
   locally; install the matching Fixture on this exact Simulator. Maintainer owns Git
   writes. Request commit/push/revision only, never a TTR-produced consumer build.
2. Verify measured rendered-body fields on one actual native pair and qualify a
   supported export/caller-copy path to the USB directory. Preserve these captures.
3. Resolve scoped external artifact references in the consumer (existing local-only
   manifests must not be silently symlinked or rewritten), freeze related-group split
   membership, then generate1,000training/250evaluation pairs with per-stage timings.
4. Automated full-batch integrity/geometry/crop checks, optional small sampled review,
   approved encoding and bounded matched training, then root-cause analysis of results.

The native structural recipe rejection and missing measured-body telemetry are distinct
observations; an exact producer error/compatible build is needed before claiming one
caused the other. Bulk generation cannot safely proceed using the legacy annotations.

## Evidence / outcome separation

Runtime envelopes and stderr are retained in [runtime](runtime/). In particular:
[structural failure](runtime/status-01.json),
[accepted compatibility capture](runtime/compatibility-status.json),
[explicit unmeasured geometry](runtime/post-scene.json),
[postflight](runtime/postflight.json).

Documentation links/diff and actual recipe hash checked; no implementation changed,
so no new Swift build/test result is claimed. Software: existing path exercised;
data: blocked on measured geometry/consumer original receipt; integration: legacy
capture/app-owned export passed, external delivery blocked; model: not run.
# Active execution checkpoint — October 2, 17:06 UTC

The earlier delivery blocker is resolved through app-owned export plus verified USB
receipt. Approved serial capture is running from `plan-storage-v2.json`; membership
is unchanged from `plan.json` (1,000 train +250 evaluation pairs). First200pairs
are received and observed-body/focus validated;800crops pass. No model run yet.

Large images/crops are under
`/Volumes/training-drive/data/NUIAK/NATIVE-FOCUS-EFFECT-SPIKE-26`.
Metadata lives here in `batch/chunk-*`. Crop preparation follows capture in a
separate owned process. Keep completed receipts and source captures intact.

Chunk007 hit `xcode_probe_timeout` in coordinator preflight before capture of
`n26-g01-v054`. Fresh readiness passed/ownership clear. Producer resume preserved
four successes and completed20unattempted cases, leaving the failed case unchanged.
One separately recorded recovery campaign73f7c3b6-62de-49e3-ad5a-dbffdc47863d captured
that missing case. `chunk-007/accepted.json` binds both verified receipts:24+1,
not a false claim that the original campaign completed25. Poller now recognizes
`completed_with_failures` as terminal. No uncertain action was replayed.

Initial35%context windows included neighbour bodies in17/50first-chunk frames.
Fixed20%before-anchored windows pass all checked frames and preserve enlargement.
Production16%per-body crops remain the comparison arm. Fixed legacy pixel-rule
diagnostic on175training contrasts: brightness88arrival/87unknown; growth profile
175unknown (vertical edge/center-drift guard). This is not a model evaluation or
an assertion that the visually/mechanically observed growth is absent.

Consumer software: explicit USB root in the existing Swift crop tool; serial campaign
plan/receipt/body intake and two representation crops; matched partial-tail experiment
adapter in the existing trainer.69focused Python and134offline Swift checks pass.
CORPUS-LIFECYCLE-27 companion is implemented and tested, with no existing data roles
changed. Training awaits all1,250pairs and complete pinned encoding protocols.

Continuation: finish capture/crops, validate full corpus, encode each arm with resident
weights, log FDR035/FDR036 exact protocol hashes, execute at most300seconds each,
evaluate once at fixed final weights, then report matched results and error examples.
