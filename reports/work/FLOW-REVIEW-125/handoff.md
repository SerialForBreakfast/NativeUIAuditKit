# FLOW-REVIEW-125 — read-only workflow review

Software verified; data eligibility not applicable; peer integration and model
gates not assessed. No capture, training, promotion, Git writes or transfer attempt.

## Delivered

`scripts/workflow_review.py status PATH` reads version-1 status with bounded,
duplicate-key-rejecting parsing. It retains every nonempty blocker/request
collection with its source pointer, even expired or nested under unknown fields.
Packet freshness, evidence and independent outcomes stay separate. Unknown fields
remain in the untouched pinned source. It rejects a changed input during read;
this is snapshot consistency checking, not a lock or authoritative device state.

`scripts/workflow_review.py git --intended PATH --message TEXT --uptake TEXT`
emits exact current-HEAD and dirty inventory, rename origins, untracked files,
explicit intended subset and unassigned paths. Repeat `--intended` and `--evidence`
as needed. Evidence arguments are labeled reported assertions. No broad staging
command or Git mutation. Source inventory excludes Git-ignored data; it is not a
security scan or a claim that every remaining file should be committed.

Both commands output JSON to stdout. Redirect only to approved project storage.
No automatic status rewrite, history deletion, source publication or peer execution.
The current-view tool preserves rather than auto-archives resolved history; archival
still needs a reviewed exact subset and durable references.

Companion: conformance tests now construct isolated local fixture/exposure inputs,
not depend on saved reports or skip when a checkout lacks them. Production build
still defaults to the pinned 282-image exposure audit. Historical pack retained;
new source-pinned pack is `../FLOW-CONFORMANCE-124/artifacts/attempt02/`:
54,763 bytes, 103 members, SHA-256
`a286ec244697f634606be7f6a77a96f7b0be950ae6e45baee3436c9f798aeb34`.
Both are test-only; neither delivered or training-eligible.

## Verification and actual caller evidence

- 33 focused Python tests pass: workflow review, self-contained conformance,
  sidecar-v2 and H1 validation. Covers expired unresolved requests, unknown fields,
  new unrelated entries, changed/missing sources, duplicate keys, versions,
  rename/space/newline paths, absent/duplicate intended paths, and no Git writes.
- Offline Swift build and all 139 tests pass; `.build/workflow125-{build,test}.log`.
- Real status CLI: 129 packets / 180 nonempty actionable collections retained.
  `.build/workflow125-status.json` (local only; no raw board republished).
- Real Git CLI: 134 changed/untracked paths at observed HEAD
  `8b1f2f6058b3832d8db272bbc7b734a430803800`; only four owned script paths selected
  in the sample. `.build/workflow125-git.json`. This is not the entire commit scope.
- New conformance builder: 11 expected outcomes, 282 exposure hashes, exact archive
  membership/hash readback. `.build/workflow125-pack.json`. All commands exit 0.
- `git diff --check` passes. Pre-existing dirty changes preserved.

## Remaining work

Published/read back NUA-owned `FLOW-REVIEW-125` in verified shared `nuiak/status.yaml`.
Before/after semantic hashes of all other fields match. Peer acknowledgment of this
update remains pending. Metadata publication is not archive delivery.

FLOW123 outbound exclusive publication still unsupported; no repeated failing
attempt or overwrite fallback. TTR survey26 original captures remain undelivered;
metadata alone cannot resolve the three apparent regression decisions.

Next substantial tranche: qualify agreed immutable publication and peer vector
replay, intake retained survey26 originals, reproduce both models and separate
native-hint error from genuine regression before choosing new training. No model
improvement or throughput gain is claimed for this workflow-only tranche.
