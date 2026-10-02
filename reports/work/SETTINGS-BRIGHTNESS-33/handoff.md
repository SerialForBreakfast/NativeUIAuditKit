# Brightness33 — completed local experiment and coverage preparation

## Result and decision

| Method | Correct | Wrong | Abstained | Scorable |
| --- | --- | --- | --- | --- |
| Existing pixel rule | 33 | 0 | 15 | 48 |
| Simple brightness direction | 4 | 41 | 3 | 48 |
| Mean with existing guards | 33 | 0 | 15 | 48 |

Keep the existing rule. All methods found the2arrivals+2departures, but simple
brightness falsely changed41unchanged controls. Existing/guarded methods retain29
correct unchanged and15uncertain. Five action pairs are development data, not
independent evaluation. All full-screen outcomes remain incomplete; no whole-screen
navigation/no-op success claim is supported.

14generated stress cases:9exact sign versus12existing/guarded. Small noise, content,
neighbor and outline changes break sign. Neighbor-only remainsunknown and one
content-only fixture isunavailable with guards. These two are safe abstentions,
not wrong decisive answers. [Results](replay/result.md), [exact pins](replay/result.json).
11.397seconds; fixed thresholds, saved OpenCV tracking and native production crops.
No model fitting. Model-workflow skill kept truth out of predictions and separated
generated cases from recorded outcomes.

## Independent coverage work

[48case intent](coverage-intent/intent.md) and [machine-readable matrix](coverage-intent/intent.json):
16native artwork,16native wide-button,16native list-row pairs across theme/density/
content brightness/position.36training-candidate/12development roles are proposals
only. Measured native geometry, effect ancestry, profile, clipping and neighbor
context are required. Provider-neutral planning format is deliberately not runnable
TTR request syntax. Unsupported native families must remain explicit gaps.

## Source qualification boundary

Read-only local TTR checks: HEAD46dce7b, dirty checkout. `git cat-file -t dedfd613`
fails; scoped filename search finds no grid-density/CorpusCoverageRequest source.
Producer22:06:11Z status reports composition4/grid-density-v1 work,2appearance pairs
and6transitions, but source remains its working tree; no new archive published.
This is a source-availability blocker, not a failed local build or a device failure.
Resume when the maintainer publishes and synchronizes matching TTR/Fixture source.
Consumer builds locally; source commit/push is the request, not a packaged build.

Published packet SETTINGS-BRIGHTNESS-33 and source/mapping request
`nuiak-20261002-brightness33-source-mapping` at22:20:37Z to
`/Volumes/SharedStatusFile/nuiak/status.yaml`. Unique-key readback passed and unrelated
content hash stayed unchanged. Peer acknowledgment of this request is not observed.

## Verification

31Settings tests plus4coverage-intent tests pass; offline Swift build and
14XCTest+120SwiftTesting pass. Logs `.build/debug-output/brightness33/`.
Actual retained CLI and14generated cases executed. Software passed; retained
development scope unchanged; live integration/training admission remain pending.

## Next substantial tranche

1. Once matching source is local, build and verify the new density planning/import
   path, including stale-origin and incomplete-box rejection.
2. Map the48case intent to actual supported native controls, qualify a bounded
   generation batch under applicable target/storage scope and use grouped spot QA.
3. Compare targeted native coverage against FDR036 on frozen development inputs;
   add genuine no-op/content-change coverage and retain the existing guarded rule
   as a separate supporting signal. New data admission/training membership remain
   explicit decisions; the current real challenge remains development, not training.
