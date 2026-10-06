# BADGE-A Apple integration — October 6

Worker correction02 received: 43,924 bytes, SHA256
`bf665d87af821db1870a38fc55a8cb61540dfbd5a5c78d8d3e75c9b6530e615e`;
23 regular files / 179,938 expanded bytes. Reviewed scoped changes from the retained
return01 plus each integration hunk against the current tree. All affected production
source/test files were clean before integration; unrelated dirty files preserved.

Adopted opt-in taxonomy binding, legacy observation-label boundary, badge enum,
annotation1.3 and public-writer guards. Old category maps, annotation1.0–1.2 and
shipped model manifests/weights are unchanged. The two digest constants independently
match documented canonical complete-category records; subsets are explicitly permitted,
not misrepresented as complete taxonomy coverage. Added local whole-schema parity
and changed-ID/label/order digest checks beyond the returned tests. Canonical contract:
`Research/schemas/badge-category-binding-v1.md`.

## Verified

- Ten Python compatibility tests pass, 0.003s after local parity additions.
- Offline native `swift build` exit0, 4.09s.
- Offline native `swift test --no-parallel` rebuilt new tests: exit0,
  **139 tests / 19 suites**, 6.899s. No skip-build or test exclusions.
- New strict/legacy manifest tests, detector label-conversion caller and public
  writer no-output-on-old-schema tests explicitly appear as passing in the log.
- Logs `.build/badge-runtime02-{build,test}.log`; `git diff --check` passes.

No simulator, training, CoreML conversion, dependency installation or Git writes.
Run028 remains live and its pinned scripts/inputs were not edited. Raw return stays
ignored; source changes are reviewable in the working tree.

Software verified; annotation contract exercised on fixtures only; Apple software
integration passed. Native badge model inference and model gates not assessed.
Minor release and BADGE-B data/candidate remain separate; no41-class gate waiver.

Acceptance/receipt published and read back at
`nuiak/responses/nuiak-20261006-badge-runtime-acceptance02.json`, 1,906 bytes,
SHA256 `e38a8b829f5da92763943588437dd2fbdd43f226b7f2c6555f41861a9d7a828a`.
Peer acknowledgment received in `joe-big-dog/worker-badge-accepted1111.json`
(11:12:42UTC), matching the correction02 receipt and Apple acceptance. Sender
cleanup remains unobserved. Worker reports zero active GPU jobs and no ready inputs;
Run028 checkpoint is the next NUIAK-owned handoff, not another benchmark request.
