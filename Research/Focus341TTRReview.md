# FOCUS341 — TTR capabilities and proposed follow-up

> Historical research record. Results retain their stated scope and limits.
> Host names are public aliases. Local evidence and execution records remain private.
> This publication does not revalidate earlier results or approve a model.

research-host-NUIAK reads research-host-TTR source at `d06a64bd8840c5ada053fd90841c56cef2a9dd58`.
This review does not start capture or change the running Fixture.

| Capability | Source evidence | Qualification limit |
| --- | --- | --- |
| Custom focus effects | `FixtureFocusStyle.Custom` defines scale, border, shadow, tint, and corner radius. | Source support does not prove rendered output. |
| Headless rendering | `render-headless-screen.swift` exposes 4 layouts and a focus ID. | Its command does not expose the independent effect fields. |
| Content replacement and scrolling | `FixtureSceneMutation` defines commands and separate observation receipts. | Requested content and offsets are not observed results. |
| Interruptions | `FixtureInterruptionCommand` and `FixtureInterruptionRecord` define presentations, phases, and observations. | A command receipt alone does not prove a visible interruption. |
| Runtime identity | The telemetry server reports instance, build, OS, and Simulator identity. | Each capture still needs matching runtime evidence. |
| Appearance settings | Recipes support themes and simulated accessibility appearances. | The `high_contrast` preset does not prove the OS HCF setting. |

## Reuse first

FOCUS341 uses retained local images and admitted artwork. It does not need another remote capture request.
Its generated negatives preserve both control patches and their focus effects.
Their changes occur in a central background panel. They do not cover all screen positions.

Reuse existing Fixture contracts when exposing controls in headless rendering.
Record control-body bounds separately from rendered bounds and outline bounds.
Record shadows separately when measuring their spread.
Keep generated labels separate from native focus observations.

## peer-host-TTR proposal

peer-host-TTR sends EXP-DIAG-20261012 revision 2 at coordinator cursor 275.
It proposes geometry checks, timed sequences, and settling comparisons.
NUIAK records new execution as awaiting human approval.
This proposal does not replace the running FOCUS341 comparisons.

Prioritize these evidence fields:

- Frame hashes and acquisition times.
- Action identifiers and action times.
- Observed focus identities and separate bounds.
- Missing, repeated, delayed, and reordered frames.
- Capture source and runtime identity.
- Setting changes and restoration evidence.

Reuse HCF337 and RESEARCH340 before another benchmark.
Compare changed-focus sequences with unchanged-focus sequences.
Report premature-ready decisions separately from missed focus changes.
Keep authored, native Fixture, real-app, and physical results separate.
Do not choose deployment thresholds from this proposed pilot.

Its proposed bound is 12 directional inputs, 12 pairs, and 8 frames per transition.
Its proposed limits are 10 min and 128 MiB.
OS setting changes still need explicit authority and verified restoration.
