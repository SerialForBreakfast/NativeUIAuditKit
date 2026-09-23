# DATA-SCHEDULE-01 — planning software review

2026-09-23; NUIAK architect; base b3f0546. Preserved all pre-existing dirty work.

| Outcome | Evidence |
|---|---|
| Software verified | Eight Python integration/schema tests,14XCTest+98SwiftTesting and Swift build pass |
| Data eligible | Not assessed: catalog contains requested configs, not captures |
| Integration qualified | Planning CLI integrated; native renderer qualification not assessed |
| Model gate passed | Not assessed; no training or new inference experiment |

## Delivered

`NativeUIDatasetGenerator --plan-visual-addon --content-seed 19` exits before
the legacy runtime parser/pipeline. It prints JSON only; no device argument, process,
runtime, app install, file output or simulator mutation is invoked by planning.
Malformed/missing/overflow seed and attempted device arguments fail before the pipeline.
Do not invoke the legacy capture command as a substitute: it builds/installs and
changes simulator state, outside this packet's authority.

VisualProbeCatalog lives in the already shared GeneratorConfig.swift so the actual
GeneratorRunConfig contract is used without a second Python approximation. It produces
48 rows for each of UIKitControls,ChromeCoverage,DynamicTypeOverflow (144 total).
Each content seed/family owns all its variants, all development-only. Different seeds
are not independent source families. The catalog is not an admission manifest.

Verified intersections **per family**:

| Intersection | Covered/required |
|---|---|
| Theme × requested profile | 4/4 |
| Theme × six selected text sizes | 12/12 |
| Clock × charge level | 25/25 |
| Cellular bars × Wi-Fi bars | 12/12 |
| Charge level × charging state | 10/10 |
| Theme × charging state (extra regression) | 4/4 |

This is deliberately not all-pairs coverage across every axis. Content stays fixed
within each family; future native qualification needs contrastive pixel/label checks.
The first bounded native batch must select representative rows across families and
account for remaining cells; maximum48 captures is not permission to run all144.

## Source fidelity checks

The three families exist in the actual generator dispatch. Current frozen capture
loops were not changed. UIKitControl states now have the separately implemented
optional measured-state path, but default historical writer output remains unchanged.
Native capture of this catalog still needs an explicit execution adapter/assignment;
this packet is planning-only, not a completed capture runner.

Confirmed effective-theme issue: ChromeCoverageConfig.make uses seeded colorScheme;
ChromeCoverageTemplate applies it via .colorScheme, while AnnotationWriter records
GeneratorRunConfig.colorScheme. The generator dispatch passes status but not a theme
override. Therefore planned/recorded theme cannot qualify effective Chrome theme.
No historical relabeling performed. Resolve through an opt-in effective-config path
with native rendering evidence before counting those cells as captured coverage.
Configured profiles likewise are not actual simulator/runtime identities.

## Verification and immutable output

- `catalog.json` SHA256:
  `4063812b72c649953069561696b6eb500b00eea3c16ee54b6957b7107a1404c4`.
- `python-tests.log`: actual built CLI deterministic output and negative arguments,
  plus schema tests;8tests pass,exit0,0.505s.
- `swift-test.log`:14XCTest+98SwiftTesting pass,exit0; SwiftTesting3.162s.
- `swift-build.log`:exit0. Commands use established scoped host setup, disabled
  dependency resolution and project-local temp/module/cache/config/security paths.
- `git diff --check`:exit0. No simulator commands, downloads or model experiments.

First draft charging schedule reused theme parity; review caught this before capture.
Charging now steps separately, with an extra joint-coverage assertion. This illustrates
BP-94: named axes alone do not establish independence; test required intersections.

## Next work and boundaries

Planning tranche complete for review. VIS-B native probe qualification remains open;
DATA-STATE-01 native test is also unrun. Next software work is opt-in effective-theme
provenance and a bounded capture adapter, with immutable catalog validation before
any mutation. Actual rendering/build/install require explicit execution scope and
must not touch preserved P0-C corpus. The unresolved P0-C split decision still blocks
its continuation; this addon does not change those counts.

Worker-execution/model-workflow guidance informed scope and evidence distinctions.
No public detection API or TTR contract changed. SMB coordination not applicable.
No processes remain running; catalog does not authorize training or data admission.
