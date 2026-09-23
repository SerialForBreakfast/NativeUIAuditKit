# Parallel tvOS acquisition — assigned 2026-09-22

Owner: NUIAK architect. Implements ADR-0009 TVGEN-01/02/03 plus one independent
TTR compatibility smoke. User explicitly authorized existing Fixture launch,
exact-target simulator runtime storage, direct capture, 42-recipe development pilot
and shipped-model baseline. No install/build of producer artifacts, training,
Office, resets, promotion or external source edits. Target:
9026ECA9-77DB-4AE6-8FE6-BB239E9571FA. Operations serialized.

Use the existing Fixture target and HTTP /device, /scene, /recipe, /focus/set.
Direct acquisition uses exact-UUID simctl screenshots; no TTR acquisition dependency.
Five-second HTTP calls, ten-second settling, two-minute recipe deadline. Failures
retain partial output; never retry a dispatched mutation automatically. Bind endpoint
PID to exact installed simulator bundle and pin its executable/dylib hashes.

Source contract: `direct-tvos-capture-v1` records frozen catalog, target/build identity,
per-frame image hash/dimensions, timestamped scene/device observations bracketing
capture, completion counts and health. Require same instance/run/recipe, observed
focus and geometry; native verified/settled/fresh samples. Temporal bracketing is
not an atomic framebuffer or authenticated hardware claim. No synthetic callback
frame IDs. Reference focus is observed null corpus target, not inferred from pixels.

Derived v1.4 manifests use `tvos_native_generator`, development-only membership,
production runtime crops and explicit direct interval evidence. Existing v1.2/v1.3
stay unchanged. Full training preflight rejects v1.4 until a later scale contract.
Shared crop/baseline tooling is extended, not copied. Exact decoded pixel checks
and seed grouping apply across sources; intentional positive/negative pairs remain.

Pilot: all seven archetypes, light/dark/high_contrast, seeds7/19, regular density,
step0. Counts: 2 for dialog, 4 for grid/media/settings/hero/maze, 41 for kitchen_sink
(producer enum actually has 41 cases; verify catalog pin before execution).
Smoke is the two-element high_contrast seed7 dialog. Pilot unsupported cells are
explicit failures, not successful coverage. Baseline uses oracle-box crops, not
end-to-end TTR navigation performance. All pilot seeds/variants remain development.

Acceptance: offline adversarial/entrypoint tests; direct smoke visual geometry and
native focus; 42 recipe accounting and all family/theme overlays; shipped baseline;
TTR completed intake or concrete first-failure report. Focused tests during edits,
full offline Swift build/test once at handoff. Report four independent outcomes.

Implementation evidence: [handoff](../../reports/work/TVGEN/handoff.md),
[frozen pilot accounting](../../reports/work/TVGEN/pilot-gaps.md).
The direct screenshot transport is exercised; native focused-item binding remains
a shared Fixture prerequisite. Never substitute requested focus to unblock a pilot.
Tasks.md remains the sole queue; these links are evidence, not duplicate acceptance.

## Failed-pilot resumption preparation —2026-09-22

NUA-owned continuation: retain the specific last settling predicate in failures,
including the element for coordinate conflicts. Settling still allows transient
layout changes within its original bounded deadline; no mutation retry is added.
Add read-only `--resume-plan FAILED_RECEIPT --output NEW_JSON` to the existing runner.
It audits a healthy-postflight failed run's complete ordered recipe prefix through
the same byte/interval/runtime/membership checks as completed capture. A non-complete
last recipe, changed source plan, corrupt bytes, unhealthy postflight or inconsistent
counts rejects planning rather than silently accepting work. Produce the frozen
catalog identity, retained-receipt hash, verified-prefix counts and exact remaining
indices/targets. The result is non-executable, training-ineligible planning evidence:
never change failed state, create a completed receipt, shrink the original catalog,
or automatically rerun anything. Actual multi-run merge/resume execution requires
a separately reviewed contract retaining each run's build/instance lineage.

Acceptance: actual CLI on retained evidence; deterministic output; corruption,
membership/health/count changes and output collisions fail closed; actual consumer
still rejects failed capture. Focused tests and one integrated offline package check.

## Reviewed continuation contract — 2026-09-22

Architect decision for this continuation: implement the missing execution/assembly
path offline now; actual capture still waits for the repaired Fixture. No change to
the frozen42 recipes/246 targets or original failure state. Own runner, adapter,
regression tests and this plan; preserve other workers' model/iOS files.

- A bounded ordered chain begins with an audited original failed complete prefix.
  Subsequent `direct-tvos-segment-v1` receipts retain the full catalog, explicit
  start/end indices, hashes of every predecessor receipt, their own build/instance,
  native observations and healthy postflight. Only complete recipe prefixes may be
  reused. Gaps, overlaps, partial recipes, zero-progress segments, incompatible
  runtime/profile/target/source plan, or mixed test-only/genuine evidence reject.
- Resume execution re-audits all predecessor bytes, requires an explicit target,
  endpoint and new output, and never consumes the planning-only resume JSON. After
  a failed predecessor, require a hash-bound human/architect repair review naming
  that receipt and the replacement binaries plus a retained report. The installed
  binary must differ and match the review; that is a prerequisite, not proof of
  correct geometry. Native per-frame validation still decides admission. No retry
  loop or producer installation is added. Recipe limit bounds one segment.
- A new `direct-tvos-capture-set-v1` receipt can be completed only when the ordered
  chain covers all42 recipes. Assembly copies verified indexed PNGs, original
  sidecars and unchanged raw receipts into isolated per-run subdirectories. It
  projects only paths into the combined view; original scene/label evidence stays
  unchanged. Revalidation reopens every raw receipt, verifies its hash and chain,
  and reconstructs the view rather than trusting flattened metadata. Failed source
  receipts remain failed. Partial assembly has no completed receipt.
- Existing v1.4 extraction and baseline entrypoints consume the validated set via
  the existing validator and production crop path; no new cropper, trainer or
  training eligibility. Visual review binds the complete set hash, so the old
  two-pair smoke review cannot qualify it. Each run's identities remain inspectable.
- Test real CLI planning/assembly and resumed execution with deterministic doubles:
  exact next recipe, wrong target, unchanged/unreviewed build, bad predecessor/hash,
  range drift, mixed provenance, corrupted copies, collisions, incomplete sweep,
  no mutation retry, consumer membership/crop parity and training rejection.

Acceptance is software-only until genuine remaining groups, family/theme/anomaly
overlays and the full shipped-model baseline pass. Direct work does not depend on
the independently requested TTR sidecar repair. No scale or training authorization.
