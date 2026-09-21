# TTR training suitability: storage-independent review

Observed 2026-09-21, approximately 21:35 UTC. Read-only producer inspection at
`c2b1bc4c19dd5406ba95f8f356edcbbce2dee103`; `git status --short` was empty.
This identifies source, not the running app/Fixture build. No inputs, recipe
changes, captures, training, producer edits or new runtime qualification occurred.

## Result

Storage is not the only remaining gate. Source supports useful deterministic
generation and paired capture, but the reviewed batch contract does not yet
establish observed focus and per-frame geometry for trusted FocusRing labels.
Preserve the one-smoke scope; do not scale or train from parser success alone.

All producer paths below are relative to the TVTestRig repository.

| Requirement | Source evidence | Disposition |
| --- | --- | --- |
| Deterministic variation | `TVTestRig/TVTestRigFixture/Models/FixtureRecipe.swift`: seven archetypes, explicit light/dark/high_contrast, three densities, seed/step/configuration hash | Available in source; matrix coverage still needs genuine pilot |
| Actual observed focus | `TVTestRig/TVTestRigFixture/Telemetry/FixtureTelemetryServer.swift:482` emits `focusSweep.requestedFocusID`; coordinator `refreshFocusedFlags` at 295 also derives flags from requested ID | Blocking label-source gap; requested success is not observed focus |
| Focus settling | `FocusSweepController` defines settled as elapsed configured delay; `FixtureCoordinator.swift:425` sleeps then marks settled | Timer alone is not callback/animation confirmation. Stable pixels plus matching requested telemetry do not prove native focus |
| Callback path | `Views/ProceduralSceneView.swift:154` records `procedural_focus_changed` and reports geometry on FocusState change | Useful existing mechanism; batch sidecar must preserve separately observed result rather than promote requested ID |
| Per-frame boxes | `TVTestRig/TVTestRig/SyntheticFactory/FixtureBatchHarvestEngine.swift:470` retains baseline scene in memory, but `makePairedSample` at 874 receives only focused scene; sidecar at 1009 emits only that scene | Baseline geometry is lost at serialization; frame provenance contains hashes/dimensions/timestamps, not boxes |
| Split isolation | Same engine at 952 assigns 60/20/20 using recipe hash; recipe hash includes theme/density/step | Not the planned 80/10/10 related-seed grouping. Do not silently relabel existing producer partitions; negotiate/freeze central group assignment before collection |
| Exact target coverage | Engine at 496 excludes four taxonomy classes to infer focus candidates; Fixture sweep uses isButton traits | Candidate derivations differ; precompute supported target IDs from authoritative Fixture capability and account for rejected/unreachable targets |

Geometry nuance: the view has geometry preference reporting, but also emits
reference rectangles on focus changes. A rendered-image test must establish
which boxes describe focused scaling/clipping. Do not claim all boxes are wrong;
do not claim measured transformed geometry from source presence alone.

## Bounded producer compatibility request

Alongside the existing storage/export repair, request a separately assigned TTR
contract task (not a NUIAK edit to the producer):

1. Preserve requested and observed focus separately, observation provenance and
   sequence/time; reject missing/mismatched/stale observations for training.
2. Retain baseline and focused scene geometry bound to each PNG hash and pair ID,
   with documented coordinate units and clipping/transform semantics. Additive
   versioning/backward compatibility must be reviewed; do not invent wire fields
   in NUIAK first.
3. Expose authoritative supported sweep targets; report expected/captured/rejected
   counts. Agree how frozen related-seed groups map to partitions without silently
   converting 60/20/20 into 80/10/10 or splitting related variations.
4. Tests: requested A/observed B, delayed or absent callback, stale callback,
   unfocused baseline, focused scaling/clipping, wrong frame/hash binding,
   unsupported target, related variants across partitions. Follow with the already
   authorized tiny genuine smoke after storage and target checks pass.

## Consumer-owned work remains separate

The earlier [training-readiness audit](training-readiness-audit.md) records
same-box extraction, quota/split admission and training-launch gaps. These are
not fixed by producer storage repair. Preserve the existing PER-04 worker's
physical-only deliverable; integrate changes under the assigned consumer packet.

No VoiceOver alignment requirement is introduced. This is visual focus only.
No simulator success qualifies physical shader behavior, iOS DS-G8 or a model.

## Acceptance ledger and resume condition

- Source audit: completed; evidence above, no executable tests claimed.
- Software verified: not assessed for revised producer contract.
- Data eligible: blocked; no genuine completed intake or reliable revised labels.
- Integration qualified: blocked on supported export plus contract/intake evidence.
- Model gate passed: not assessed; no model execution.

Next safe work: targeted consumer contract tests using explicit test-only fixtures.
Next runtime work: one previously authorized smoke only after producer export path
and fresh exact-target readiness are established. Broader pilot/harvest and training
remain separately authorized stages, not automatic follow-ons.

## Coordination handoff

Published request `nuiak-20260921T213559Z-focus-ground-truth-contract` in
`/Volumes/SharedStatusFile/nuiak/status.yaml`, packet `SIM-READINESS-20260921`,
at 21:35:59 UTC after verifying the sillycon.local SMB mount. Safe YAML readback
passed and existing export/readiness requests were preserved. Peer acknowledgment
of this new request has not been observed. The read peer snapshot expired at
21:29:24; it does not establish current producer progress. Historical runtime
observations were explicitly not refreshed by this source audit.
