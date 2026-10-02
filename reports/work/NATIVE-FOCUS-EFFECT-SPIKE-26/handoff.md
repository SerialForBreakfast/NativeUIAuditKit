# Native-focus spike: started, incompatible Fixture identified

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
