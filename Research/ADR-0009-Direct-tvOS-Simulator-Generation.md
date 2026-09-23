# ADR-0009: Direct tvOS Simulator generation alongside TVTestRig

**Status:** Approved. Implementation and runtime execution remain separately
assigned.
**Date:** 2026-09-22  
**Decision owner:** NativeUIAuditKit maintainer  
**Scope:** Visual FocusRing data first, full-frame tvOS detector augmentation second.

## Context

TTR's capture/export integration has repeatedly blocked acquisition of eligible
training pixels. Its latest reported screenshot repair still needs consumer-host
qualification. These are real integration requirements, but they should not be the
only route to a tvOS development corpus. The iOS native generator demonstrates the
useful architectural pattern: deterministic native scenes, direct rendering/capture,
generator-owned labels and independent validation. It is not proof a tvOS port works.

The maintainer requests a parallel path using the Fixture and tvOS Simulator OS,
with TTR continuing independently and contributing additional qualified data later.

## Decision

### 1. Two independent acquisition lanes, one downstream validation contract

NUIAK owns a **direct native tvOS generator lane**. It uses the tvOS Fixture/native
controls and OS focus engine in an exact, explicitly selected simulator. A minimal
local runner controls deterministic recipes, observes focus/layout and captures
frames through a supported local simulator or native test mechanism. It does not
require the TTR desktop app, coordinator, capture leases, companion, workspace
bookmarks, batch job store or export service.

TTR's existing SIM-DATA packets remain active independently. Do not cancel, rewrite
or duplicate that integration project. Both producers feed a versioned normalized
dataset contract and the existing NUIAK validation, crop, coverage and training tools.
Direct output must declare its own source kind (proposed `tvos_native_generator`)
and receipt version; never fabricate a TTR receipt or mark TTR integration passed.

ADR-0008's simulator-first and later hardware-transfer principles remain. Its
requirement to repair TTR SIM-DATA-01 before **any** tvOS dataset/model development
is superseded: either qualified simulator lane can supply the development corpus.
Its app-owned job/export rules still apply when operating through TTR; the direct
runner is a different producer, not a workaround inside TTR's sandbox/container.

### 2. Reuse the Fixture without acquiring a hidden TTR dependency

First inspect and pin the Fixture's build/source, recipe and telemetry interfaces.
Prefer a standalone Fixture build/test entrypoint and existing deterministic recipes
and native focus callbacks. Prove that launch, recipe selection, observed focus,
capture and cleanup work while TTR is not part of the call path. Do not terminate a
user's running TTR to prove this; use an independently assigned simulator target.

If reuse requires producer edits, record an exact separately owned TTR proposal.
Do not edit that repository implicitly. If no independently usable Fixture target
exists, return a bounded NUIAK-owned tvOS runner/source-reuse design for review,
including license/source attribution and synchronization strategy. Do not let an
unanswered TTR change request silently become the new lane's permanent dependency.
Do not copy a second evolving Fixture wholesale or build another general-purpose rig.

Native UI code belongs in a tvOS-only target, outside the offline macOS Swift package
build, following the existing platform-boundary rule. No speculative public API,
taxonomy or shipped-model change is needed.

### 3. Native pixels with frame-bound ground truth

Generate seeded native scenes; capture a reference/unfocused state and each supported
element's actually observed focused state. Requested focus is a command, not a label.
Record recipe/seed, stable element IDs, observed focus callback/state, settled layout,
frame dimensions, scale, coordinate origin and frame-specific bounds. Correlate each
PNG with its telemetry generation and hashes; detect focus/layout changes during
capture and reject ambiguous pairs. Fixed delays alone do not establish settling.

Verify full-screen capture includes native focus effects and that measured bounds
align with actual images, including focused scaling/clipping. Do not substitute a
view-layer render that omits effects merely because its JSON is valid. If the chosen
capture mechanism cannot establish this, stop that mechanism and report the gap.

The Simulator OS supplies native rendering and focus behavior, **not automatic gold
labels for arbitrary OS screens**. Uninstrumented Settings/system UI screenshots are
inspection evidence until a separate trustworthy annotation method is approved.
No Settings traversal, preference mutation, navigation-defect or VoiceOver dataset
expansion is part of this lane. ADR-0007 keeps semantic alignment separate.

### 4. One split/lineage policy across both producers

Pin generator/Fixture source and builds, simulator UUID/runtime/profile, recipe
configuration and capture mechanism. Keep raw PNGs and annotations, complete/rejected
trial accounting, manifest hashes and derived crop lineage. Reuse existing 16%
expansion and 256×256 runtime crop behavior, verified against frame-specific geometry.

Freeze recipe-group splits before scale. Same recipes, related seeds, variants,
paired states and duplicate content stay in one partition **across both lanes**.
Different producer names do not make identical fixture scenes independent evidence.
Audit later TTR additions against existing direct-lane membership; version any merged
corpus and re-evaluate it, without silently changing a frozen evaluation set.

Follow [IterationEfficiency.md](IterationEfficiency.md): prioritize meaningful visual
states, validate actual pixels and metadata, test affected families, preserve valid
completed batches and perform full integrity/leakage checks at freeze. Comprehensive
controllable-state coverage is the long-term goal, not a full Cartesian-product gate.

### 5. Training progress without overstated qualification

A qualified direct pilot can support the shipped-model development baseline and a
qualified direct corpus can satisfy the data prerequisite of a separately authorized
FocusRing candidate. TTR readiness is not a prerequisite for those steps. Existing
≥6,000-pair scene/theme quotas, hard-negative support, six quality gates, crop/export
parity and package-size requirements remain unchanged; missing coverage stays open.

Full-frame detector augmentation is a separate secondary export with its own category
map and coverage report. tvOS data does not replace iOS reconstruction or satisfy DS-G8.
Simulator success establishes an experimental simulator candidate, not physical-device
performance or production promotion. Actual TTR model-decision/navigation comparison
still requires TTR; physical transfer validation still requires separately authorized
hardware. Preserve shipped models throughout.

## Implementation tranches

The approved execution plan is detailed in
[`Plans/RemainingDelivery.md`](Plans/RemainingDelivery.md#tvgen-01--reuse-and-runtime-design-review)
and operationally scoped by
[`Plans/ParallelTVOSAcquisition.md`](Plans/ParallelTVOSAcquisition.md). These are
future dispatch contracts, not operations authorized by this ADR.

| Packet | Bounded deliverable | Acceptance / next step |
|---|---|---|
| TVGEN-01 | Read-only Fixture reuse inventory and minimal direct-runner design: exact source/target/interfaces, capture alternatives, local output/runtime authority requirements and two-element recipe | Reviewable implementation plan proving dependency separation on paper, explicit unknowns and no unassigned external edits; dispatch TVGEN-02 |
| TVGEN-02 | Implement runner plus source-specific manifest adapter and deterministic consumer tests; then, under exact-target authority, one native two-element capture through validated crops | Actual observed labels, image/geometry alignment, byte accounting, clean owned-resource teardown; wrong target, stale focus, corrupt/partial data and output collisions rejected. Offline software and native qualification reported separately |
| TVGEN-03 | Qualified direct pilot, shipped-model baseline and frozen scale plan | Reuse the existing seven-family × three-theme × two-seed pilot contract where supported; report unsupported cells rather than count them. Protect final groups, rank visual errors, then dispatch authorized scale |
| TVGEN-04 | Resumable direct capture to existing FocusRing quotas, full audit and training handoff; optional separate full-frame export | Immutable qualified membership, zero cross-lane split leakage, retention/recovery evidence and truthful training preflight. Training remains a separate assignment |

TVGEN-02 offline implementation/tests need no TTR integration success. Live steps need
explicit target, installation/runtime-storage and capture authority; existing iOS
generator authority does not extend to tvOS. Keep data in new gitignored project-local
`dataset/tvos_captures/` and `dataset/focus_ring/` subtrees; logs/build outputs stay
project-local. Standard simulator runtime writes require an explicit setup exception.
No remote execution, Office operation, system reset, TTR session takeover or training
follows from this design approval.

## Alternatives and costs

- **Wait exclusively for TTR:** rejected; couples all dataset delivery to an unrelated
  desktop capture/export repair schedule.
- **Replace TTR with a second automation platform:** rejected; this runner only creates
  controlled training data. TTR remains the integration/navigation consumer and later
  data producer.
- **Hand-paint focus or label requested focus as observed:** rejected; weakens the
  native visual ground truth we need to improve navigation.

Cost: another small acquisition adapter and possible Fixture reuse maintenance.
Control that cost with a pinned source boundary and common downstream tools, not a
second cropper, taxonomy, training loop or validation policy. Share only cross-project
interface implications with TTR; local generation progress stays in NUIAK.

Report software verified, data eligible, integration qualified (name the producer),
and model gate passed separately. This ADR creates no successful runtime evidence.
