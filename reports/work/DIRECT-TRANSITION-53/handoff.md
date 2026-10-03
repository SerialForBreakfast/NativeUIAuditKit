# Direct paired-image53 — implemented, real fit awaiting admission

October3,2026. All prior49–52dirty changes and pixels preserved. No real-data fit,
capture, export, promotion, dependency installation or Git writes.

| Outcome | Evidence |
|---|---|
| Software verified |117Python and134Swift tests pass; actual prediction CLI and trainer preflight exercised|
| Data eligible |29structurally valid known-focus pairs; exact training role proposal remains unapproved|
| Integration qualified |Retained source→paired-image path verified; no live TTR reassessment|
| Model gate passed |Not assessed; no real trained model or accuracy claim|

## Delivered

`scripts/focus_direct_transition.py` supplies source reconstruction, deterministic
full-frame letterboxing, six-channel CNN, explicit admission/preflight, fixed30epoch
training arm, terminal development metrics and prediction CLI. Existing experiment
dispatcher and `train_focus_ring_detector.py` route the new `transition-direct-pixels`
arm. Ordinary FocusRing paths and shipped weights are unchanged.

Inputs are ordered before/after pixels only. Targets are two known-focus boxes plus
semantic focus change; native after geometry/identity never enters inference. Fixed
96×64full-frame input is an experimental baseline, not a claim that this resolution
is sufficient. The model does not cover absent focus, unknown scenes, multiple-focus
cases or persistent control identity. Invalid predicted boxes abstain, not clamp to
invented valid regions. Confidence0.85is fixed and uncalibrated.

## Actual inventory and proposed experiment

| Group | Pairs | Changed | Unchanged | Existing role | Proposed role |
|---|---:|---:|---:|---|---|
| Whole Fixture renderer |24|12|12|Calibration|Train, only after approval|
| Reviewed Settings journey |5|2|3|Development|Development|

No source pair excluded; zero decoded-pixel overlap across groups. Full known-focus
labels exist even where tracking failed. This does not mean every control in each
screen has complete annotation. Retained guarded measurement decisions resolve just
1/29reviewed subsets under the strict all-controls check; this is not whole-screen
accuracy. Direct model results are unavailable until actual training.

Exact assignments: `qualified-inventory/admission-proposal.json`, `approved:false`.
The proposal accounts for all29member IDs and preserves source roles in the corpus.
Any approval needs a new bound protocol/admission/execution record and logged run,
not editing raw source sidecars. No further TTR capture is necessary for this small
development proof. Five repeatedly examined Settings pairs cannot establish broad
generalization or final model qualification.

## Verification

- Real inventory CLI: `.venv-yolo/bin/python scripts/focus_direct_transition.py
  --sources reports/work/DIRECT-TRANSITION-53/sources.json --output
  reports/work/DIRECT-TRANSITION-53/qualified-inventory` — exit0,29pairs.
- Real trainer CLI: `scripts/train_focus_ring_detector.py --experiment-protocol
  reports/work/DIRECT-TRANSITION-53/qualified-inventory/protocol.json --experiment-arm
  transition-direct-pixels --name direct53-proposed --preflight` — exit2, correctly
  blocked by missing admission/assignments/derived execution record; configuration valid.
  `.build/direct53-real-preflight.log` retains exact output. No output run created.
-117Python tests3.555s; `.build/direct53-integrated-tests.log`. Nine new tests cover
  geometry/order, source corruption, missing labels, split/pixel leakage, proposal
  authority, code/configuration pins, collisions, label-input rejection, context
  gating, metrics, numerical training and actual checkpoint→prediction CLI.
  A30epoch fit on two generated color-image fixtures is software verification only;
  temporary fixture weights removed with the test-owned directory. No real run ID.
- Offline Swift build2.11s,14XCTest+120SwiftTesting pass. Project-local49caches reused;
  `.build/direct53-swift-{build,test}.log`. Full pass run once after integration.

Pins:

- corpus identity `9735108bf5ae011dfb17c07f7d49c4b42dfba4c9e1e027459a2b377047f589aa`
- inventory file `baa7f8ab0f3619878ebd1aaf8872228c0a19caf34b039ae283647bdd7dde5dc6`
- protocol identity `6febdd788f5a2454cd4b6f0734fce0ec8b460b7f41526a2ad1c1c8ee9b098c45`
- protocol file `04f063495ee3522afbd41d62078c2d6b8e767b42613fd334dcfa3eecc9d8bda2`
- unapproved proposal file `a19dcad4e441314bdab116bca6cc8998c6cd59022bd066707145aa424cc5705e`

## Exact next decision and tranche

Approve or decline using these24Fixture pairs for one experimental training run,
with the5Settings pairs solely for development evaluation. If approved: bind that
decision, log one30epoch CPU run, train fixed-last, report both box IoUs and semantic
change accuracy/abstentions/latency by changed versus unchanged, compare retained
measurement decisions, and diagnose failures. No threshold sweep or production
promotion. New independent final evaluation and TTR cleanup remain separate work.

Shared coordination: verified expected SMB mount, published/read back
`nuiak/status.yaml` packet `DIRECT-TRANSITION-53` at16:16:44UTC. Only the peer-relevant
consequence was shared: existing24labels suffice for a direct-image development
proposal, no replacement capture requested. Other parsed entries preserved at SHA256
`59ce68a48a0a69e7e0b06cc76e58c60735cafc2ad6d0339c1c08f169ccac24ec`.
Peer acknowledgment not verified; no live repair or availability claim.
