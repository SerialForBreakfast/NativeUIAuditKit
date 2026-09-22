# Native OS focus expansion — 2026-09-22

| Outcome | Evidence |
|---|---|
| Software verified | 14 Python intake tests; isolated runner builds; 92 offline Swift tests pass |
| Data eligible | 12 visually reviewed **development** pairs; no training/final-test approval |
| Integration qualified | Native XCTest → retained PNG/AX → production crop → shipped CoreML scoring, one Settings-root journey |
| Model gate passed | Not assessed; no training, export or promotion |

## Actual results

[Successful trial](root-sweep-02/execution.log): 25 single directions, three
observed boundaries, 26 observations, 22 unique decoded frames, 12 native identities.
XCTest 33.353 seconds; overall test execution 34.964 seconds. No Select, settings
mutation, Office, TTR or Fixture operation. Settings remains foreground; original
context restoration was not attempted. In-test postflight passed. After teardown
Settings PID22651 was present and no native runner was listed; this is not proof
of post-teardown responsiveness.

Source: exact simulator9026ECA9-77DB-4AE6-8FE6-BB239E9571FA, Apple TV 4K third
generation/4K profile, tvOS26.5 runtime23L470; PNG3840×2160, viewport1920×1080.
[Runner hashes](root-sweep-02/build-hashes.txt) bind the executed source/binary.
Labels are observed native AX, bracketed around captures, not requested input,
predictions, Fixture callbacks or atomic framebuffer attestation.

[Immutable manifest](root-sweep-02/dataset-02/manifest.json) content hash:
`17857e5e3bfd04857bb4c19199308b9190e8d15fabe19313b65fa9d283594825`.
Shipped model hash:
`9e5ba294e545b4ae0c54aa5d483b1a1f681b6c30477882700b4dbe139b9c66b7`.
Runtime/crop/source/image hashes and actual per-frame geometry are retained.

At threshold0.85: **TP1 FN11 FP3 TN9** on 24 crops. This small selected development
set is not a general accuracy estimate. Native boxes were injected; detector
proposal extraction and model-driven navigation were not tested. CPU-only CoreML.
Per-batch model-load timings are retained; per-prediction latency was not retained
by this adapter, so no deployment latency claim is made.

## Visual review bound to that manifest

Architect inspected all24 production crops in [contact sheet](root-sweep-02/review-crops.png)
and representative full frames at two scroll positions. Focused crops all contain
the corresponding white highlight; paired negatives are visibly unfocused. The
16%/256 production stretch is preserved, not a new crop policy. This is crop-level
development review, not exhaustive full-frame animation or outer-halo annotation.
Manifest's `visualReview: pending` remains immutable; this paragraph is its external
review receipt. No personal account detail was observed in inspected examples;
all raw screen evidence remains local.

Ranked gaps: native long-row positives (11misses), dark unfocused false positives
(General, Power Off, Video and Audio), adjacent-highlight/context sensitivity,
Home/custom-control appearances, independent screen/layout and style groups.
The four earlier root rows overlap this lineage; neither old nor new root examples
may become an independent final holdout. Repetition is not dataset diversity.

## Implementation and validation

- `NativeOSFocusTests.testSettingsRootSweep`: bounded root-only traversal,
  stable boundary handling, observation-only missing-focus settling, retained
  invalid diagnostics, fresh context checks and postflight.
- `scripts/native_os_focus_dataset.py`: actual CLI validates completion, target,
  versions, temporal brackets, PNGs, geometry, exact pixel identity and pair labels;
  uses existing production crop/inference tool; new output only, development-only.
- `scripts/test_native_os_focus_dataset.py`: 14 tests including separate actual
  helper crop/score response shapes, failed trials, wrong target, changed/corrupt
  bytes, partial completion, stale/conflicting observations, unsafe paths,
  duplicate identities, clipped pairs, contradictory pixels and output collision.
- [Focused tests](tests.log): exit0. [Swift build](swift-build-host.log): exit0,
  6.48seconds; [Swift tests](swift-test-host.log): exit0, 92tests/2.995seconds.
  SwiftPM emits its existing `--skip-update` deprecation warning. Restricted
  SwiftPM sandbox setup was denied; scoped host execution passed without disabling
  app sandboxing. No network package resolution.
- Live builds/execution/export/inference used scoped host approval and project-local
  explicit outputs. Standard Xcode/simulator storage was included in execution
  authority. No restart, signing repair or security weakening.
- First live attempt `root-sweep-01` failed missingFocus with zero inputs, retained.
  Confirmed runner exit, fixed bounded settling, then ran a new trial. Intake's
  first rejection identified decorative-AX duplicate handling; corrected without
  recapture. `dataset/` retains incomplete adapter output after a crop/score response
  mismatch; `dataset-02/` alone contains a completed manifest. Regression test added.

## Completion and continuation

The bounded root acquisition/intake/baseline tranche is complete for review.
No new weights were trained: only one correlated root layout has been admitted;
independent train/validation/test membership and broader coverage are missing.
Next: OS-FOCUS-03 Home coverage and reviewed deeper Settings acquisition, then
OS-FOCUS-04's source-aware incremental assembly/training adapter. The canonical plan
defines inputs, steps, tests, frozen evaluation and existing-trainer integration.
Native OS data cannot be counted as absent Fixture scene/theme quotas. A smaller
experimental run needs a separate explicit evaluation protocol, not weakened gates.

All previous dirty changes, iOS reconstruction, producer files and shipped models
were preserved. No background job remains from this tranche. Shared coordination
not applicable: this work adds local native data and changes no TTR interface or
peer request; existing crop-parity request remains separately owned/tracked.
