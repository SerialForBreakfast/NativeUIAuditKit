# COMPATIBILITY-72 — reuse producer session and wire contracts

Read-only source: /Users/josephmccraw/Developer/TVTestRig,
clean HEAD f933e2994ae07a967267dd00ed9d61d63b3cef7c. No source build or runtime
qualification performed, no external repository edits or device operations.

## Source findings

Paths relative to TVTestRig/TVTestRig/SyntheticFactory:

- TransitionCampaign.swift: CampaignTransition.validate admits focus_moved and
  boundary_unchanged; directional changed focus does not itself guarantee no scroll.
  SHA256 8f39e8cb1e1a5138422ca48d11fce0b1c2134063052f59cb06c9173924e1240f.
- InterruptionCampaign.swift: CampaignRunnerSession.acquire connects once then
  checks status for the same operation; finish disconnects the owned operation.
  Invocation-scoped, not serialized for resume. Reuse this rather than introducing
  another lifecycle controller. SHA256
  25c5d61c78b8d9a64b1062fc0d0ad0b009120c51e5d256aff598406236c81064.
- ReferenceCoverageRequest.swift: RichReferenceCoverageCompiler accepts appearance,
  scroll_unchanged and scroll_moved only. Artwork/backdrop variation is separate
  from recipe.theme. SHA256
  e08f20e43a3b770b219cf4cf51643bf445edc6ebdf5bd268947250f506d6ed34.
- NativeSpatialCoverageRequest.swift emits focus_moved for native table directional
  plans, but CLI/StableCLIHelp.swift declares table capture feasibility-only/refused.
  Source emission is not a qualified fallback or permission to capture.

The24-case guide/catalog stationary matrix cannot yet be bound to this reviewed
planner contract. No unsupported case is marked ready; native theme support remains
separate from light artwork backgrounds. Request supported explicit-manifest path or
the exact missing planner capability, not generic session reuse or condition renames.

## Consumer changes and checks

Strict stationary consumer maps focus_moved→interior_switch and
boundary_unchanged→boundary_noop. Original specification/receipt bytes remain intact;
inspection output retains wire condition plus normalizedCondition. Existing legacy
scroll intake unchanged. Equal native offsets, both visible owners, observed focus
relation, recipe/instance/capture/action binding and verified cleanup still required.
Campaign journal uses the same semantic mapping for exact-case binding.

74focused Python tests pass19.397s: real consumer, both moved/unchanged aliases,
unchanged producer bytes and changed-scroll rejection, journal and cache regressions.
Offline Swift build/test pass14XCTest+120Swift Testing; git diff --check passes.
Logs .build/compatibility72-*. No model execution, admission or new captures.
Consumer code changes correctly invalidate old validator-bound caches; no old seals
rewritten. Current input caches require new preparation before another assigned run.

## Coordination and next action

Verified smbfs mount at /Volumes/SharedStatusFile, endpoint sillycon.local/SharedStatusFile.
Published follow-up under nuiak/status.yaml packets.TRANSFER-62 at22:24:36UTC,
using existing nuiak-20261003-transfer62-stationary-compatibility request. Readback
and duplicate-key-safe YAML validation pass; canonical digest of unrelated fields
unchanged. No matching acknowledgment established. No images or model outputs shared.

Software verified; existing data roles unchanged; producer compatibility source-backed
only, live integration not assessed; model gates not assessed. Resume binding when
the supported stationary reference manifest contract is identified. New capture
also requires current exact target/build/endpoint readiness and explicit scope.

Next meaningful tranche: independently diagnose retained Settings localization errors
and quantify candidate-box coverage, while resolving the native stationary planner
gap asynchronously. Do not run unchanged epochs or delay local work for acknowledgment.
