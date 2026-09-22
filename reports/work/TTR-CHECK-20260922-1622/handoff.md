# Updated TTR diagnostic — 2026-09-22 16:24 UTC

Scope: requested read-only updated-build diagnosis and shared-status publication.
No navigation, remote-session creation, Fixture activation, capture, installation,
repair, reset, Office operation, training or producer edit.

## Findings

- Running local app PID69113, version1.0/build1, actual Debug app path recorded in
  `app-hashes.txt`; matching embedded stable CLI responds successfully. Local
  checkout is clean `022d53cc8e768056edfed9cb49ae08fd69e181f6` (persistent Simulator
  remote/workspace). Checkout identity and on-disk app hashes are separate evidence,
  not a claim that a commit hash authenticates every loaded process image.
- App launcher SHA256 `7b6330d1bcf0e34f477919f0f036f20e4d922c30ad406c78c1b978e49cd4c431`;
  debug module `2f8c732b29d128e8a79b0b7287cad35fff39a460a6abe3649a2f0ca8aea6f00c`;
  companion `ce455bb016cd40484d5f7bb817fecbe33e6d4a9cf6d58997be2c2765d873008f`.
- Help advertises persistent `simulator remote connect/status/snapshot/press/disconnect`
  and explicit-Simulator app-managed fixture jobs. Interface presence is not live
  control or capture qualification. Existing local operator skill is older than
  the packaged/source revision; runtime discovery, not old examples, guided checks.
- Exact-target readiness request `5E5E658F-EB50-4C04-9E50-92FAB76742FE` succeeds:
  coordinator, companion, evidence access, Xcode, runner, CoreSimulator, runtime,
  target all ready; `can_run=true`, ownership clear. Fixture explicitly not checked.
  Target `9026ECA9-77DB-4AE6-8FE6-BB239E9571FA` is Booted tvOS26.5; Xcode26.6/17F113.
  Packaged runner input digest `56046b14dc0560d2c87e1ef501259960b834c864fa0433dcf8e9e5c3918e1add`;
  advertised source digest `5364684cd71f6c04f7b0a2bf74252f21e09e0a6ee3789706cecceae3754791b4`.
- Coordinator status: no active command/observation, queue0, physical connection
  disconnected. This is not a claim about Office availability or permission.
- Passive GET `/device` and `/scene` at127.0.0.1:8080 each timeout after5s,
  curl28, zero response bytes. Listener PID7156 resolves to Fixture inside this
  exact simulator's application container. Settings PID70258 and Fixture both
  remain listed; no test runner listed. Presence/listener is not responsiveness.
  Prior native testing left Settings foreground; background/suspended Fixture is
  a plausible explanation, **not established by these process listings**. No new
  crash, storage regression or fresh native-focus failure is claimed.
- Installed Fixture launcher/debug SHA256s are unchanged from the failed06:03
  smoke: `28cb31b6c0f10a2c9aecec8979d5e3bdc7437f40b7496b83a39f9e9345f243c3` and
  `d9a7cf770d7deff35c11d004cd761112ff2742817520e4110de3ed01707a0427`.
  Latest commit does not change Fixture/ProceduralSceneView/FocusSweep files;
  producer Tasks still explicitly owns the non_view/unmapped_item repair.
- Producer crop correction source hash matches its published receipt:
  `512ea619f1f1e1def9e424941b1eec458f1b0e4fd2f05203d200f261bc3abd97`.
  Reported15 offline tests and corrected16% expansion are acknowledged as producer
  evidence, not rerun here. Exact NUA/TTR pixel/score parity remains unqualified.
- Nonblocking stale `--project required` help and optional
  `diagnostic_file_sink_failed/persistenceFailed` warnings remain. App-managed
  status/readiness succeed without `--project`; do not misdiagnose these as capture
  or storage failure or repeat permission/rebuild repairs.

## Disposition and next actions

1. Infrastructure is ready for a separately authorized persistent-remote test:
   fresh ownership, exact UUID, connect, snapshot, one safe directional input,
   snapshot, disconnect and confirmed cleanup. This test need not depend on
   Fixture and must not be represented as a training-bundle qualification.
2. Offline corrected-crop replay can proceed without a live session. Preserve
   common image/box/model identities and distinguish candidate geometry quality.
3. Keep existing producer request `nuiak-20260922T061302Z-fixture-nonview-focus`
   open/acknowledged. Obtain actual repaired Fixture source/build receipt before
   repeating that smoke. Then explicitly activate the matching Fixture, verify
   fresh endpoint health and perform one bounded capture/export/intake. A healthy
   listener alone does not fix the historical identity failure.

Software verification: not reassessed (no code change/build needed).
Infrastructure integration: passed for status/readiness only. Data eligible:
blocked for Fixture lane. Capture/native remote integration: unassessed on this
build. Model gates: not assessed. Independent NUA work remains unaffected; local
model-development details do not belong in the shared coordination summary.

`status.json`, `readiness.json`, `simulators.json`, separate stderr, app/Fixture
hash files preserve local diagnostic evidence. Shared status carries sanitized
metadata only. Peer packets last updated07:45Z or earlier are expired: historical
acknowledgments, not current runtime/availability assurances.
