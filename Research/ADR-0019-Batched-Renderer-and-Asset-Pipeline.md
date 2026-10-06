# ADR-0019 — batch rendering independent of the TTR desktop runtime

Date: October 5, 2026 (Pacific).
Status: proposed architecture; implementation and runtime qualification not performed.
Scope: artwork-backed UI datasets for detection and focus-transition experiments.
Extends [ADR-0009](ADR-0009-Direct-tvOS-Simulator-Generation.md), not a second rig.

## Decision

Separate asset production, scene planning, rendering and dataset admission. Prefer
one persistent native Fixture session per bounded campaign, driven from a command
line without the TTR desktop coordinator. Add a portable procedural backend only
as a separately labelled augmentation experiment, not a substitute for native focus
ground truth. Reuse TTR's supported recipe/assets/rendering contracts and NUIAK's
existing capture, validation, crop and export tools; do not fork the whole Fixture.

“Headless” must name the omitted dependency: no desktop interaction or coordinator
does not mean no Simulator, app process, graphics runtime or platform permissions.
The desired CLI is an orchestration boundary, not proof an arbitrary SwiftUI view
can render native tvOS focus on Linux or outside its native runtime.

## Evidence and current limitations

- NUIAK already has `scripts/direct_tvos_capture.py`: explicit UUID and endpoint,
  Fixture HTTP observations, exact-target `simctl` screenshots, before/after state
  brackets, PNG validation and separate planning/execution. This is an existing
  independent path, not a request to invent one. Its catalog and target/source pins
  in `scripts/direct_tvos_targets.py` are frozen historical contracts; notably the
  kitchen-sink target assumptions must not be reused as current class coverage.
- Local TTR source inspected at `46dce7b3a79e4f17af49bc0324d4aeba3cc0958d`:
  `TVTestRig/TVTestRigFixture/Telemetry/FixtureTelemetryServer.swift` exposes scene,
  device and focus observations. Native recipe code is in that target's
  `Models/FixtureRecipe.swift`. Presence is not current runtime qualification.
- TTR shared status at `2026-10-06T02:01:16Z` reports published revision
  `550a2d374801fb99120d3aed4168c1de9e7ef83d`, newer custom-art presentation measurements
  still uncommitted, pixel qualification pending, and selected-tab/coherent-route gaps.
  These are peer reports, not independently checked source/build equivalence.
- The local `FocusPairHarvester.writeSyntheticFixtureBatch` draws coloured rectangles
  with CoreGraphics for unit tests/self-test. It is not a rich native renderer or
  eligible training corpus. Its manufactured `isSettled` value is not an observation.
- TTR's historical SYNTH-PERF-01 report: 12 pairs in 268.50 seconds, export 3.46s;
  per-case median/p95 22.345/43.265s and startup 16.324/37.253s. Timing scopes overlap;
  isolated PNG/render cost is unavailable. This supports testing session reuse,
  not promising a numerical speedup or assuming every current path repeats startup.
- Big Dog LOCAL-IMAGE-201 reports 24 artwork outputs in 142.5s, warm median 4.44s,
  16 agent-review candidates and 8 flags. NUIAK has inspected metadata only. That is
  artwork-generation throughput, not screenshots/hour, native rendering or acceptance.
  Approval records, source bytes and review remain separate intake requirements.

## Three rendering options

| Backend | What it can contribute | Constraint / label authority |
|---|---|---|
| Direct native Fixture on Mac/Simulator | Authentic instrumented controls, full screenshots, observed native focus and geometry; no TTR desktop capture/export dependency | Still needs exact target, running Fixture, supported contracts and capture/observation consistency; preferred focus lane |
| Offscreen Apple renderer | Potentially faster static view/layout snapshots with measured boxes | Experimental only: clipping, effects, compositing, focus, animation and window-dependent behaviour need comparison against native screen capture; do not assume `ImageRenderer`/layer snapshots preserve them |
| Portable scene compositor on Big Dog | Seeded layouts, artwork, text, masks, exact designed geometry; scalable procedural detection/transition augmentation | Not UIKit/SwiftUI/tvOS native pixels; focus is authored, not observed. Source kind and evaluation claims must remain distinct |

Do not make offscreen rendering a prerequisite. First amortize setup in the existing
native path. Use Big Dog immediately for independently approved artwork, decoding,
duplicate/lineage audits and PyTorch work. A new portable compositor is conditional
on a measured need and model-utility experiment, not idle-GPU busywork.

## Pipeline and ownership

`Big Dog artwork → reviewed hash-addressed asset pack → frozen scene campaign →
native or explicitly procedural renderer → validated shards → NUIAK admission/export`

- Big Dog owns generation/cache and bounded worker outputs, not Apple UI capture.
- TTR owns reusable Fixture rendering code, supported native interfaces and any
  producer extraction/refactor. Request source revisions/interfaces, not build binaries.
- NUIAK owns corpus design, direct adapter, admission, split accounting and evaluation.
- Reuse GEN-PARITY-199's resource inventory and missing-hash planner, IOS-ASSET-200's
  native artwork binding and LOCAL-IMAGE-201's review pack. Do not duplicate them.
- A shared renderer module/standalone batch host is a TTR-owned proposal if coupling
  prevents reuse. Avoid a second divergent implementation of native focus effects.

## Contract: recipes produce annotations, artwork does not

Freeze each campaign's source/build/runtime, renderer backend/version, taxonomy,
asset hashes and ancestry, seeds, intended roles, expected elements and partitions.
Record original licences/provenance and review decisions; a generated or screened
image is not automatically cleared for all downstream uses. No model downloads or
new generation are authorized by this ADR.

For every frame retain raw PNG hash, decoded dimensions, coordinate origin/scale,
stable element IDs, semantic classes, parent/child relationships, visible/clipped
and excluded elements, nominal layout and measured rendered-body geometry separately.
Record text/layout/theme/state settings and actual observations; missing classes
stay unsupported, not fabricated. Full annotation means all supported visible elements
are accounted for, not that every catalogue label exists as a working native control.

For native transitions retain the action, both frames and their own geometry,
observed focus IDs/callbacks, timing and fresh stable observation brackets. Requested
focus never supplies the label. Bracket correlation is not atomic framebuffer identity.
Keep unchanged-focus, content-only changes, scrolling and uncertain transitions
distinct. Reject ambiguous native samples without promoting procedural predictions
to labels. Procedural scenes explicitly mark authored focus and designed geometry.

Asset masks are not UI-control masks. Rounded avatar masks, clipping and focus effects
are applied by the renderer; optional segmentation output must come from that renderer
with defined visible/amodal semantics. It is not inferred from generated artwork.
Reuse production `FocusRingClassifier.makeCrop` (16% expansion, 256×256); no new cropper.

Output adapters preserve native capture formats and producer identity. Any common
envelope is a versioned NUIAK manifest extension, reviewed against existing consumers;
never forge TTR receipts or silently alter its wire schema. Suggested backend labels
are conceptual until schema work: native-simulator, apple-offscreen, procedural.

## Efficiency and failure handling

1. Plan offline, inventory inputs once, reserve splits and hash the machine-readable
   campaign. Use coverage-driven combinations rather than all parameter permutations.
2. Verify target/endpoint, build, storage and ownership once per session; revalidate
   freshness/identity at each capture. Reuse the process, decoded assets and qualified
   resources while bounded health checks pass. Do not launch XCTest per frame.
3. Execute resumable shards, initially at most 100 recipes each, with explicit per-case
   and operation bounds. Keep recipes ordered/serialized on a shared Fixture. Separate
   targets/endpoints/output ownership are prerequisites for any later parallel trial.
4. Journal planned/succeeded/rejected/missing cases. Resume only missing cases after
   resolving prior cleanup; never replay an uncertain mutation automatically. Publish
   shard completion only after exact file and annotation verification.
5. Put bulk pixels/cache/output on verified authorized storage; keep code/environments
   and compact manifests local. Mac internal space was approximately17GiB at03:47UTC:
   qualify USB output support before capture rather than inventing symlink substitutions.
6. Decode/hash once per immutable ingestion stage; reuse sealed outputs in subsequent
   experiments. Transfer only missing hashes through existing SMB receipt flow.
   No new HTTP/SSH service, continuous monitor or unbounded collection follows.

## Data quality and experiment design

Partition connected recipe/template, artwork-derivative and journey families before
capture. Cross-backend renderings of a scene are related data, not independent tests.
Reused asset hashes alone are not the entire leakage policy: layout, source family,
derived crops and human-reviewed test exposure also matter. Keep cross-backend matched
comparisons in development groups; untouched native/app holdouts remain independent.

Use diverse whole-screen compositions: hero backdrop plus shelves, dense grids,
detail pages and overlays; varied luminance/texture/type and focus treatment. Native
controls retain ground truth. Artwork-only changes should not create false focus labels.
First render approved assets in a small representative campaign, then measure benefit.
Do not claim more images necessarily improve detection or that procedural success proves
native/physical generalization. tvOS still cannot satisfy the iOS DS-G8 milestone.

## Bounded next tranche (proposal, no execution in this ADR)

RENDER-202 owns integration, reusing the earlier asset tasks rather than replacing them:

1. Reconcile exact published Fixture source and asset contract. Inventory actual supported
   controls, independent entrypoint, asset loading and output/storage support. Document
   producer-owned gaps without editing TTR or requiring its desktop runtime unnecessarily.
2. Extend the existing direct planner/runner for a frozen artwork-backed development
   campaign: 24 scenes (three supported compositions × two themes × four seeds), reference
   plus each observed reachable focus state. Precompute supported target counts and reject
   gaps explicitly. Reuse one session; no scale corpus or model run in this tranche.
3. Compare a small matched subset with the existing qualified TTR path if available,
   otherwise record that comparison blocked without blocking direct software. Measure
   setup, recipe/load, settle, capture, encode/validate/export, total elapsed, accepted
   frames/pairs per hour, peak memory, bytes and operator interventions. Keep timings
   disjoint where possible; do not subtract nested timings as independent costs.
4. Deliver complete accounting, representative overlays, native label/geometry audit,
   deterministic resume evidence and a measured scale decision. No universal performance
   threshold yet: establish the baseline before setting one. No model-quality gain claimed.

Tests: missing/changed assets, unknown schemas/classes, output collision, bad dimensions,
clipping and transformed bounds, stale focus/instance, interrupted shards, wrong target,
failed cleanup, resume duplication and cross-backend leakage. Test actual CLI adapters
with deterministic fixtures; one integrated offline Swift build/test pass for code changes.
Native qualification needs a freshly authorized target/build and storage setup.

Only if native-session reuse leaves a significant renderer bottleneck: propose an
offscreen/procedural parity spike with known geometry and focus-effect comparisons.
Then run a separately registered fixed-budget native-only versus augmented training
comparison on untouched native evaluation groups. No automatic training sweep.

## Consequences and non-goals

This can remove desktop coordinator/workspace/export friction and amortize setup while
retaining native truth. It cannot remove the native OS dependency for native tvOS pixels.
TTR remains valuable for real app journeys, physical captures and shadow-model feedback.
Big Dog can own most reusable artwork/CPU audits/training without owning a Simulator.
Risks are source drift, domain-gap shortcuts, annotation/pixel disagreement, split leakage
and storage growth; the contract above explicitly checks each.

No source changes, capture, training, installation, external handoff or promotion occurred
in this documentation task. Software runtime, data eligibility, integration qualification
and model gates remain not assessed by this ADR. Source review and document/link validation
are the delivered evidence. Tasks.md remains the only execution queue.
