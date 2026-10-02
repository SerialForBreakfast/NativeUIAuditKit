# SETTINGS-STABILITY-23

Assigned continuation, October2,2026. Finish two local outcomes: a conservative
near-identical-pixel unchanged-focus extension, and action-level accounting of
switch/unchanged/ambiguous/incomplete results. Existing brightness/growth remain fixed.

Hypothesis: after successful bidirectional tracking, low absolute pixel change can
resolve some unknown Settings decisions without treating cancellation of positive and
negative brightness as stability. Use production crops, before geometry and tracked
after geometry only. Human after-labels stay exclusively in scoring.

Before execution: fixed limits are RGB absolute mean<=.01,95th percentile<=.03,
fraction above.04<=.02, maximum<=.25. Every limit must pass; illumination warnings,
unavailable correspondence, growth/brightness changes and unsupported context retain
their original decisions. Compare the existing combined rule with this single
extension, no threshold search. Evaluate the same five same-screen retained pairs
and generated noise/content/illumination/highlight/motion cases. This is development
evidence, not an independent model benchmark.

Scope: at most100retained controls,24generated cases,300seconds per replay,512MiB
outputs; resident native crop runtime only. No new corpus admission or model training.
Action summaries distinguish partial reviewed membership from full-screen evidence.
Complete CLI integration, adversarial tests, offline Swift checks and diagnosis.
TTR's contract response is optional; unavailable producer repair does not block this.

After first fixed replay: stability resolves29additional unchanged controls without
new errors, but generated content replacement inherits a false arrival from the old
brightness rule. Add one third, fixed diagnostic arm: accept an arrival/departure
only if at least60%of pixels in each of four central-body quadrants change luminance
by .08 in that direction. This is a development-driven guard, not independent
confirmation. Reuse membership; report both earlier arms and this guard, preserving
the failed first stress result. No threshold search or new membership.
