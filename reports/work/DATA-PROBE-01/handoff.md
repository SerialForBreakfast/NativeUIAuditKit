# DATA-PROBE-01 — offline checks pass; native build/run pending

2026-09-23, NUIAK architect, base b3f0546. Preserved existing dirty work and all
historical catalogs/captures. No app installation, Simulator input or training.

| Outcome | Evidence |
|---|---|
| Software verified | Shared config/selection/CLI checks pass; iOS-only adapter syntax checked, not typechecked/built |
| Data eligible | Not assessed; no new pixels; catalog is planning-only |
| Integration qualified | Native adapter and theme behavior unqualified until authorized native run |
| Model gate passed | Not assessed |

## Implemented path

- Catalog v2 preserves144 requested configs but fixes DynamicTypeOverflow to its
  source-required accessibilityExtraExtraExtraLarge. That renderer hard-codes53pt
  body fonts. Explicit unsupported-intersection metadata replaces the misleading
  multi-size coverage expectation for this family. V1 catalog remains retained but
  cannot pass the new canonical execution validation.
- `decodeFrozen` rejects unknown fields instead of silently discarding them through
  Codable. `validatedBatch` compares all known catalog fields/configs to deterministic
  regeneration, then rejects empty, duplicate, unknown or >48case selections.
- ChromeCoverageConfig.make accepts an optional effectiveColorScheme. Only the new
  adapter passes it; default source behavior and all frozen generation loops unchanged.
- New `VisualProbeBatchTest/testExplicitVisualProbeBatch` is opt-in and independent
  of GenerateDatasetTests.setUp and its legacy dataset tree. Checks environment target
  UUID against SIMULATOR_UDID, regular nonsymlink catalog<=1MiB, exact caller-pinned
  SHA, canonical catalog, bounded case IDs and safe new output basename before capture.
- Outputs go only to a new `Documents/visual-probes/<name>` in the authorized app
  container. Existing destination rejected; no shared dataset/manifest touched.
- Uses existing UIKit/SwiftUI capture mechanisms, verifies PNG hash/dimensions and
  sidecar readback, emits v1.2 state, and retains per-member hashes/groups. Terminal
  receipt says `captured_pending_visual_review`, always trainingEligible=false.
  Partial evidence is retained on failure; no mutation retry or automatic publication.
- Elapsed-time checks bound a responsive batch to120seconds using monotonic uptime.
  This is **not** a preemptive watchdog for a hung renderer; the future authorized
  host execution must also have a bounded process timeout and inspect cleanup before retry.
- Both capture paths now hide their own window in defer, covering cancellation/error
  paths in addition to their existing explicit success/error cleanup.

## Verification

- Shared catalog Swift tests cover unchanged repeatability, all declared intersections,
  fixed overflow type, exact48case admission,49rejection, unknown/duplicate IDs,
  changed partition, changed config seed and unknown top-level fields.
- `python-tests.log`:8tests pass,exit0; actual CLI and schema suite.
- `swift-test-verified.log`: final full offline suite;14XCTest+99SwiftTesting pass.
- `swift-build.log`: final offline build,exit0. Existing scoped host setup with project
  temp/module/cache/config/security paths; dependency resolution disabled.
- `xcrun swiftc -frontend -parse` on the native test and three modified template
  sources:exit0. Syntax only; not a native build or runtime pass.
- `catalog-v2.json` emitted by real planning CLI, SHA256
  `637a434c2c888641204709ce9c3712b8001ee289d1b79a0c38dd5cd794f61929`.
- `git diff --check`:exit0. Native-only runtime tests were not executed.

## Exact resume/qualification requirements

Authorize an iOS GeneratorRunner build/install if necessary and a specific freshly
verified iOS simulator, with standard app runtime/container storage permitted. First
native smoke should select at most6reviewed cases spanning the three families/themes;
not the144row catalog. Host process needs a120second operation limit; retain output
on timeout and do not automatically restart or reinstall.

Select only VisualProbeBatchTest/testExplicitVisualProbeBatch. Required environment:
NUA_PROBE_EXECUTION=approved-development-probe; NUA_PROBE_SIMULATOR_UUID exact UUID;
NUA_PROBE_CATALOG absolute nonsymlink path; NUA_PROBE_CATALOG_SHA256 exact bytes;
NUA_PROBE_CASE_IDS_JSON JSON array of selected canonical IDs; NUA_PROBE_OUTPUT_NAME
new safe basename. These environment values are execution interlocks, not authority
or authenticated device identity. No legacy orchestrator command is required.

After capture: strict sidecar validation, all member hashes/dimensions/geometry,
representative overlays, measured-state test and actual Chrome theme check. Requested
text sizes in other UIKit controls are not automatically effective font sizes; many
controls use fixed fonts. Report absent effects, don't count metadata as rendered
coverage or fabricate annotations. This issue keeps visual qualification open.

Native build/operation authority is the remaining gap for this packet, not a reason
to claim completion. Other offline work remains available under the active goal.
Worker/model skills guided immutable inputs and evidence separation. SMB not applicable.
