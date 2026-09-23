# Appearance-v1 consumer continuation

2026-09-23 06:06 UTC. Software scope completed for review; new genuine artifact
intake is blocked on delivery, not a TTR rebuild or another capture.

| Outcome | Evidence |
|---|---|
| Software verified | Pass:43 focused/integration tests, offline Swift build,14 XCTest and93 Swift Testing tests |
| Data eligible | New10-pair archive not assessed: absent locally. Prior12 catalog development pairs still validate unchanged |
| Integration qualified | Offline appearance-v1 intake → production crops → manifest/preflight verified; genuine new appearance intake not assessed |
| Model gate passed | Not assessed; no capture, inference experiment, training, export or promotion |

## Implementation and acceptance

Owned continuation: `scripts/harvest_sidecar_v2.py`, the version-dispatch guard in
`scripts/harvest_bundle_validation.py`, new `scripts/test_ttr_appearance.py`, and
associated contract/queue/evidence documents. Base9012c1f351c408897348f791b5355553725f15b8.
Preserved all pre-existing dirty changes in Research, Tasks, harvest_focus_pairs.py,
test_ttr_sidecar_v2.py, APPEAR-C and TTR-CATALOG-01. No external producer edits.

- **Canonical identity:**3/3 literal producer vectors now match (previously0/3).
  Source vector file SHA256584f7662ba2a02a7fbbc2aa34edc264b6d8b88f88b03003d2d714b091803c584.
  Appearance suffix follows randomization; absent/null retains the pinned legacy hash.
- **Closed extension:** all nine supported archetype/preset/layout combinations pass.
  Bad shapes, missing/extra keys, invalid versions including bool/float, unknown values
  and unsupported archetype/layout combinations fail with typed reasons.
- **Observation binding:** dropped/changed appearance at all seven serialized recipe
  locations, rehashed individual endpoints, whole-pair drift, stale legacy hash and
  missing sidecar version reject. Native focus/geometry/hash gates are unchanged.
- **Caller integration:** actual build_simulator_focus_manifest.py and
  harvest_focus_pairs.py CLI paths preserve complete appearance in existing brackets;
  production makeCrop still uses16%/256×256 and each frame's measured geometry.
  Derived binding tampering fails source revalidation. No schema/API change.
- **Isolation:** preset/layout siblings keep seed:7 grouping, crossing partitions
  rejects; test-only remains test-only and actual trainer preflight cannot launch.
- **Legacy:** all12 real retained catalog pairs pass read-only bundle validation;
  byte sources, existing crops and reservations were not rewritten.

## Commands and timing

Python is the approved focus-export-01 interpreter under user Library/Application
Support/NativeUIAuditKit/Environments (read-only dependencies). All Python invocations
use PYTHONDONTWRITEBYTECODE=1, PYTHONPATH=scripts; test temporary files stay in .build.

```
python -m unittest test_ttr_appearance test_ttr_sidecar_v2 test_harvest_bundle_validation -v
python -m unittest test_ttr_appearance test_ttr_sidecar_v2 test_harvest_bundle_validation test_harvest_focus_pairs test_focus_consumer_integration -v
swift build --disable-automatic-resolution --cache-path .build/swift-cache --config-path .build/swift-config --security-path .build/swift-security
swift test --disable-automatic-resolution --cache-path .build/swift-cache --config-path .build/swift-config --security-path .build/swift-security
```

First focused pass:27 tests/1.064s/exit0. Integrated final pass:43/1.887s/exit0.
Build6.51s/exit0; test build0.73s, XCTest0.364s, Swift Testing2.501s/exit0.
TMPDIR, CLANG_MODULE_CACHE_PATH and SWIFTPM_MODULECACHE_OVERRIDE point inside .build.
Initial restricted build failed nested sandbox_apply, exit1; preserved swift-build.log.
Scoped normal-host build/test approval resolved that execution layer, explicitly
including normal CoreML test caches for the test command. No sandbox settings,
entitlements, HOME, app runtime or signing changed. No warnings in successful logs.
This supersedes the previous tranche's restricted-context full-test blocker.
Evidence: integrated-tests.log, swift-build-host.log, swift-test-host.log,
compatibility.json. No new capture/intake time or external wait; no polling loop.

## Remaining criterion and next action

Read-only checks found neither the proposed NUIAK delivery directory nor the exact
archive at the corresponding local TVTestRig project path. SMB APPEAR-VISUAL reports
producer-local evidence, not transfer; user delivery is explicitly its next step.
Resume genuine intake when `nuiak-appearance-visual.tar.gz` is provided inside NUIAK:
116122181 bytes, SHA256
`d80f14887c399e85c738ba3705096fc4ad6d116d37a38c5ca36d872919b5764a`.
Suggested directory: `dataset/tvos_captures/ttr-appearance-v1-delivery/`.
Verify archive identity and safe members before extraction into a fresh directory;
then validate all three completed bundles,10 pairs/48 exported files, review every
focus pair through production crops and audit related/duplicate membership before
issuing a scoped intake receipt. Do not put images on SMB or recapture these jobs.

Independent high-contrast/Photos-like/final-challenge coverage remains a separate
producer request. No new field or seed demonstrates independent rendered coverage.
All currently authorized software is complete; missing image bytes block remaining
real-data acceptance. No owned processes remain. BP-85 records the tested learning.
Worker, fixture-training and shared-status skills preserved the completion boundary,
native labels, preprocessing, eligibility separation and metadata-only coordination.
Publication/readback and peer acknowledgment: ../coordination.md.
