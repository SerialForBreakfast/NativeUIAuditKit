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
