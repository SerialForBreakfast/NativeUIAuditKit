# DATA-PROBE-INTAKE — software complete for review

2026-09-23; NUIAK architect; preserves all existing dirty changes and reconstruction
artifacts. This tranche completes the offline consumer for DATA-PROBE-01 exports.

| Outcome | Evidence |
|---|---|
| Software verified |15 Python tests, actual CLI success/failure and required offline Swift checks. |
| Data eligible |Not assessed on native captures; generated test fixtures only. |
| Integration qualified |Offline export-shape-to-intake contract; genuine native runner execution pending. |
| Model gate passed |Not assessed; no inference/training/model changes. |

## Delivered

scripts/validate_visual_probe.py consumes the runner's existing capture.json,
catalog.json, PNGs and declared v1.2 sidecars. It requires an independently retained
expected catalog, ordered case IDs and exact UUID. No new producer schema or
automatic native command, trainer, cropper or file transfer was introduced.

Strict admission includes bounded file/member/pixel sizes, complete expected file
accounting, no symlinks/traversal/duplicate JSON keys, byte hashes, real PNG decode,
dimensions, declared annotation schema, requested config/traits/status, groups,
element IDs and pixel/point/Vision coordinate agreement including clipping flags.
Missing pixels, rehashed corrupt PNGs, partial receipts, altered membership and
false training claims fail. Unknown native enabled/selected values remain null.

Output separates requested joint coverage from actual rendering. Pixel-identical
members are reported together, not discarded or counted as new visual diversity.
Both development membership and trainingEligible=false are unconditional. Runtime
OS is producer-reported, not authenticated. Passing integrity does not establish
effective theme/typography/status painting or visual label alignment; review remains
pending. The existing OS sidecar unknown value is not silently backfilled.

## Tests and commands

`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts .venv-yolo/bin/python -m unittest
scripts.test_validate_visual_probe scripts.test_visual_probe_cli
scripts.test_annotation_schema_versions -v`: exit0,15 tests. python-tests-final.log.
The initial python-tests.log records a synthetic duplicate-case fixture with stale
status metadata correctly rejected; fixed the fixture, not the validator.
Seven new test methods cover real CLI success/failure, receipt/selection/version/
eligibility failures, schema/config/geometry/state failures, hashes/missing/symlink/
corrupt PNGs, duplicate keys/traversal, clipping, and duplicate pixels retained.

Offline swift build and swift test use --disable-automatic-resolution,
--manifest-cache local and .build/ios-retention-check/{cache,config,security}; TMPDIR
and both module caches point inside that project tree. Scoped host execution was
approved. Logs: swift-build.log, swift-test.log. No native simulator/Xcode invocation.
Build exit0 (0.20s incremental); tests exit0,14 XCTest and109 Swift Testing
(Swift Testing2.900s). Focused final Python checks0.385s before the final malformed-root
regression; final rerun is retained in python-tests-final.log. git diff --check passes.
All generated test files use owned TemporaryDirectory paths under .build and are
cleaned only by their test owner. No surviving dataset or other worker output touched.

## Next step and limits

Canonical invocation: Research/Plans/VisualStateCoverage.md, DATA-PROBE-INTAKE section.
After exact target/build/storage and first bounded native probe are authorized,
capture reviewed representative cases using DATA-PROBE-01; export by an approved
route to a new local directory; run this intake against the independently frozen
selection/catalog; inspect visual agreement and every duplicate before any new
eligibility decision. Software verification is not native qualification.

No shared-status publication: this local iOS consumer does not change TTR's next
action. No new experiment ID or training approval. No process remains active after
the recorded offline checks. No new learning entry needed: this implements existing
unknown-state, joint-coverage and provenance rules rather than discovering another
policy. The full assigned offline consumer tranche is complete for review.
