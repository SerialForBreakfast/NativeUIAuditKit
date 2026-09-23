# DATA-STATE-01 — offline implementation verified; native qualification pending

2026-09-23. Owner NUIAK architect; base b3f0546. Existing dirty reconstruction,
appearance, temporal, retention and research changes preserved.

| Outcome | Result |
|---|---|
| Software verified | Passed offline writer, strict version/schema and package tests; UIKit source path not runtime-qualified |
| Data eligible | Not assessed; no new data, no existing sidecars rewritten |
| Integration qualified | Not assessed for native UIKit capture; simulator test added but not run |
| Model gate passed | Not assessed; no training/inference experiment |

## Delivered contract

- Complete v1.2 schema copied from v1.1 with exactly two validation deltas: required
  enabled/selected accept null. Structural parity test protects every other constraint.
- AnnotatedElement carries optional measured enabled/selected state. UIKit capture
  reads UIControl properties; non-control views remain unknown. Selected is native
  UIControl.isSelected, not inferred from toggle value or focus.
- AnnotationWriter.write accepts explicit schema:.measuredState and emits required
  null for unknown. Existing/default legacy path still emits v1.0 true/false defaults,
  even if capture types contain measured state. Preserved corpus output is not silently
  changed. This default is compatibility behavior, not approved state-training truth.
- Declared-version schema selection knows1.2; no fallback. Historical1.0/1.1 schemas
  unchanged. Existing fixture/tvos consumers are not automatically migrated to1.2.
- Dedicated offline generator test target exercises actual write-to-file/readback,
  nine boolean/unknown combinations, legacy roundtrip, required-key failure, clipping
  invariants. Native UIKit test exercises a selected disabled UIButton and unknown UILabel.

## Verification

Commands use project-local temp/module/cache/config/security paths under
`.build/ios-retention-check` and disable dependency resolution.

- Python `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts .venv-yolo/bin/python -m unittest
  scripts/test_annotation_schema_versions.py`:6tests pass,exit0,0.023s.
- Scoped host `swift test --disable-automatic-resolution --manifest-cache local
  --cache-path .build/ios-retention-check/cache --config-path .build/ios-retention-check/config
  --security-path .build/ios-retention-check/security`:14XCTest plus96SwiftTesting pass,
  exit0; SwiftTesting3.324s. New target adds3tests to prior93.
- Same configured `swift build`:exit0,0.23s,no new warnings.
- Full closed-subset schema validation of all10 actual emitted JSON files in
  `.build/annotation-state-tests`:exit0. Uses existing check_schema implementation,
  not just the lightweight schema selector. Unknown versions/extra state fields,
  missing required fields, integers and string booleans covered by tests.
- `git diff --check`:exit0.

First restricted Swift attempt failed before compilation (nested sandbox_apply).
Scoped normal-host execution resolved it. Initial focused test caught a wrong test
assumption (native pixel x=-4 was expected as0); source contract preserves raw native
boxes and clips normalized boxes. Test corrected, not production geometry. jsonschema
is not installed; no download performed, reused existing strict local schema evaluator.

## Remaining and next action

Native simulator test has not been built/run; it is not part of the offline SwiftPM
target. Resume its qualification with explicitly approved iOS runner/build/target
scope. No new build/installation/capture authority inferred from this software packet.
Do not use new labels for training until that native path is qualified.

VIS-A's broader effective-theme/runtime provenance remains open; this named packet
delivers enabled/selected state only and does not close the parent. Independent visual
scheduling can proceed offline, while runtime probes and captured addon membership
remain separately approved. P0-C count-allocation decision remains outstanding.

Research architecture updated before code. Worker-execution and model-workflow skills
guided frozen-data compatibility and distinct evidence outcomes. SMB not applicable:
local iOS generator extension does not change TTR's wire contract or next action.
No running processes, dataset mutations, public library API changes or git writes.
