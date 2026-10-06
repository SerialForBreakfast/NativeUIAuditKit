# ART191 source review — October 6

## Source-access blocker cleared, admission still pending

The GitHub connector returned404, but read-only `gh api` successfully resolved
both published87c514397f0878922d70dc5d4e916f6de6761467 and capture-era
550a2d374801fb99120d3aed4168c1de9e7ef83d. No checkout mutation, producer build,
source execution or capture was needed. Absence from the dirty local checkout is
no longer a reason to request a rebuild, new source archive or recapture.

Reviewed source at550a2d374801fb99120d3aed4168c1de9e7ef83d:

| File | Git blob identity | Review scope |
|---|---|---|
| Fixture/Views/ProceduralSceneView.swift |451981f3ad504901db54e7a9c2ea1cff40af3e69|Body measurement, button animation gate and image overlay measurement|
| Fixture/Telemetry/FixtureSceneTelemetry.swift |eaee6398587375d8e405bd110f743d8503bfabc6|Complete telemetry definitions and oracle fallback|
| Fixture/Models/FocusSweepController.swift |3e29a6679b3778fc5735a9afd7a1729a48e2cdc5|Complete focus observation monitor and geometry utilities|
| SyntheticFactory/FixtureBatchHarvestEngine.swift |8c9884b38800cc5d4a61efa7c25c19041ba1a6d4|Capture bracket, observed-focus admission and sidecar version encoding|
| Domain/FixtureAppearance.swift |2c33523f9dcc1a7ca26187b5be33774c063c4fc1|Complete rendered-body geometry definition, lines745–806|

Paths above abbreviate the producer's TVTestRig/TVTestRigFixture and
TVTestRig/TVTestRig source roots. Blob IDs identify source, not running binaries.

## Supported interpretation

- Body measurement uses presentation layers and selected solid-body views, with
  ancestor/window clipping and screen scale conversion. Full, visible, nominal
  and artwork bounds are different quantities. Normalized output is XYXY.
- Button/image measurements reject known in-progress body animation. Focused
  native images use the actual overlay content view, not a requested focus guide.
- `native_body_presentation_layer` can also describe measured custom authored
  surfaces. That string alone does not prove a native focus effect; retain recipe
  presentation/style identity separately.
- NativeObservationMonitor requires matching generation, resolved observed focus,
  required geometry and stable signature; gaps of at least one second reset the
  gate. Passive observations explicitly remain unverified. A minimum timer alone
  does not establish settled focus.
- Harvest validation compares before/after focus, recipe, geometry, semantic
  inventory and mutation state; checks fresh samples, matching generation and
  settled duration; and requires native observed identity. Reference absence needs
  the reference control attached and focused. Certain scrolling modes may exclude
  explicitly clipped non-targets, never the requested target.
- Schema4 is selected by a recipe-source-reference encoding context; competitor
  pairing remains separately recorded. Producer explicitly calls the capture
  bracket correlated across separate clocks, not atomic frame identity.
- SceneOracle can generate reference descriptors when measured geometry is absent.
  Consumers must retain the observed-focus/body gates rather than treating any
  nonempty element list as measured ground truth.

## Remaining acceptance work

This review clears source availability and explains key fields; it does not prove
the captured executable matches these blobs. Reconcile retained build/source
identity, complete body-contract definition and source-shaped negative vectors,
then inspect representative pixels and every anomaly. Preserve the20pairs' current
review/calibration roles,18clipped targets and28frames with missing tab-body data.
No whole-screen completeness, independent evaluation, training admission, native
shader fidelity or model-quality claim follows from source review alone.

Verification: successful read-only exact-ref GitHub API calls and source inspection.
No implementation changed; prior consumer tests are reused, not newly claimed.

Published/read back the material unblock at
`nuiak/responses/nuiak-20261006-art191-source-access-cleared.json`:1472bytes,
SHA256 `f0a0774beb89cd49755bc3836d0ea72023387bbcc6dd794d0e8fb4349b790466`.
Peer acknowledgment is separate and pending. TTR need not rebuild/retransfer for
source access; remaining consumer acceptance is NUIAK-owned.

## Binding audit follow-up

The retained subset README describes550a2d37 as the **current maintainer HEAD**,
not explicitly the capture build. Original source-review handoff names dirty
3e9e05d496a5904c15d6d6dc41714ce92fd512ab and its18-file inventory does not pin
these native Swift implementations. Signing evidence reports signatures only;
qualified-final-readiness explicitly says Fixture was not checked. These records
do not independently bind the captured executable to550a2d37. Request a retained
build/source mapping, not new binaries, artwork or recapture. If unavailable, say
unknown and retain review roles rather than manufacture historical identity.

Full body contract reviewed: version1, explicit role/coordinate space and matching
element/generation; finite positive full/visible rectangles; unavailable reasons
with no geometry; clipping consistent with a0.01pixel difference; normalized
projection agreement within0.01pixel. Planar corner tolerance is0.25 in projection
coordinates. Full clipping legitimately has no visible crop. This supports separate
rejection of unavailable targets rather than falling back to wrapper boxes.

Mapping request published/read back at
`nuiak/responses/nuiak-20261006-art191-capture-source-binding.json`,1479bytes,
SHA256 `e5793a3a1ac7c72d7e2a952b8b62057902c3edc2db06dc57b679bafe90e1a29b`.
No response observed yet. This narrows the old source blocker to historical build
binding and explicitly avoids an unnecessary rebuild/recapture cycle.

## Consumer consistency extension

Source review exposed a schema4 inspection gap: coordinate checks did not reject
a measured body carrying an unavailable reason or inconsistent clipping flag.
Reuse `fixture_rendered_body.validate` after the existing stricter coordinate
checks; preserve existing error categories and tolerances. Add synchronized-alias
negative cases so tests reach body validation rather than fail bracket equality.
This is structural rejection only, never a change of data role or build binding.

Implemented and verified:16 focused tests pass in0.634seconds, including the real
review entrypoint and synchronized measured/unavailable/clipping contradictions.
Fresh read-only review of the retained subset accepts20/20 structurally with
trainingEligible=false. No crop/inference repeat or new artifact admission.
Offline native Swift build passes3.55seconds; serialized full test suite passes
132tests/17suites in6.409seconds. Logs `.build/art191-body-contract-{build,test}.log`.
`git diff --check` passes. Existing source/build binding request remains the sole
peer action; no duplicate request or local-test noise published to SMB.
