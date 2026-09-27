# TTR coordination review — 2026-09-27

**Superseded transfer state:** the maintainer subsequently confirmed prior size
approval and directed download. All four archives are now locally copied/hash-verified
and the receiver receipt is published. See [completed receipt](receipt.md); the
status-only observations below remain historical, not a current approval blocker.

Assignment: check transfer/peer updates and publish NUIAK status. Owner: current
TTR coordination worker. This assignment does not copy/extract archives, run intake,
capture, infer, train, promote, or operate/rebuild TTR.

## What changes next

1. **Existing captures are published.** Stop treating acquisition as awaiting another
   capture request. Producer snapshot2026-09-27T02:42Z reports four completed24/24
   surface sweeps, matching the already frozen seed7 groups. Next is an explicitly
   assigned NUIAK receive/receipt and bounded intake, not recapture.
2. **Partition conflict requires intake reconciliation.** Producer says three embedded
   export manifests use `split: training` from a recipe-hash default. Preserve the
   original bytes; validate provenance and the prior frozen role mapping before any
   consumer admission. Never feed these evaluation groups into training or silently
   relax the consumer validator. Final-challenge groups remain unscored/untouched for
   model selection. No content was extracted or inspected in this status check.
3. **The role-freeze acknowledgment is confirmed.** Peer pending request
   `tvtestrig-20260924T163500Z-freeze-evaluation-roles` is completed_by_peer and cites
   NUIAK's2026-09-26T03:10:28Z freeze. Old peer footers still waiting on that freeze
   are superseded by the explicit acknowledgment and later capture request.
4. **Focus provider adoption is reported complete, quality is not.** TTR retains the
   9ce483f package pin and reports43/43 vendored files unchanged at later NUIAK
   revisions; no new repin/rebuild is requested. A separate report-only Simulator
   trial found bright-unfocused artwork falsely focused with probability1.0 in3/3
   checks. These are producer claims, not a locally reproduced evaluation. Preserve
   bright-artwork negatives in the already frozen protocol; do not tune the final test.
5. **FR-A capability response removes uncertainty, not the FR-B blocker.** Native
   navigation focus is available; VoiceOver focus is not observed and no alignment
   object is emitted. Even `notAssessable` still needs producer emission. Keep
   semantic alignment work separate from appearance-only intake; do not infer cursor
   truth from a simulated VoiceOver style flag.
6. **Photos remains separate.** No Photos app route exists in the producer's installed
   Simulator. Existing local physical Photos imagery is development evidence, not
   paired native-focus ground truth. These four archives do not close Photos coverage.
7. **Run013 is no longer a training dependency.** Its local evaluation is complete;
   no model was promoted. TTR handoff need not wait for iOS training or DS-G8. Hardware
   availability remains unknown; completion grants no device or compute reservation.

## Publication identities, not receiver receipts

Request: `tvtestrig-20260927-frozen-surface-captures`.
Manifest ID: `tvtestrig-20260926-frozen-surface-captures` (different date, retained
explicitly rather than silently equated). Manifest share path:
`tvtestrig/frozen-surface-captures-20260926-manifest.json`,2,478bytes,
SHA-256 `89bd84bf7dde13361433376b267b9bdb1cf839122dc393bbf4dca962b608a322`.

All archive names below are relative to `tvtestrig/` on the verified share.

| Archive | Exact bytes | Frozen role | Expected SHA-256 |
| --- | --- | --- | --- |
| surface-v1-cinema_rows-seed7-e6295823-20260926.tar.gz | 172053102 | appearance-validation | 83123e5723d9f7501cf4a3e635e68f9a1b82558a5ba6299cd5a43746271151d1 |
| surface-v1-album_grid-seed7-4d635d19-20260926.tar.gz | 172156757 | appearance-validation | 8a33d73531cfb0b63eb0e14232b696f31627b4b2b6e46e7c2d2f33222db17253 |
| surface-v1-memory_mosaic-seed7-b8f511c6-20260926.tar.gz | 171478657 | final-challenge | b4bfb87d6827fd6001ee9f25e97339eaf52f558c8e7d8fcd0d7819e4949d2e41 |
| surface-v1-icon_shelf-seed7-df457dd3-20260926.tar.gz | 180531624 | final-challenge | 6c0862d9ac28f43245c3874660c06b5a5dacbfaae648b1ad6973593d67259836 |

Total696,220,140bytes. Every archive exceeds the10,000,000-byte channel limit.
All four actual shared files were streamed read-only for SHA-256 verification;
each matched its expected size/hash, with unchanged size/mtime across the read.
The manifest's size/hash also matched. This is source verification, not a copy receipt.
Peer reports prior user approval to publish these exact files; that statement is
not new receiver execution authority. This status-only assignment does not authorize
copying, intake or training. Next assignment must identify these exact files/sizes
and authorize receiving plus the desired intake scope. No `copied_and_verified`
receipt or sender-cleanup acknowledgment is issued here. Sender retains all files.

## Dependencies and priority

Highest immediate FocusRing step: receive the already produced frozen files under
an explicit assignment; verify local copies and acknowledge immutable transfer IDs;
then bounded archive admission, provenance/role reconciliation, crop/label and
independence validation. Source availability is not data eligibility. Keep the
existing221-pair candidate/9-pair retention selection unchanged until reviewed intake.

Avoid the coordination loop **NUIAK waits for capture while TTR waits for receipt**:
the capture publication is now observed. Also avoid gating appearance work on missing
Photos/VoiceOver coverage or completed iOS evaluation. Those remain independent lanes.
Exact-release/third-machine acceptance remains unrun and release builds remain paused
per peer status; neither is an automatic prerequisite for offline archive intake.

## Verification and ownership

Verified `smbfs` endpoint `sillycon.local/SharedStatusFile` at
`/Volumes/SharedStatusFile`. Shared/local guides match byte-for-byte. YAML was
bounded to262,144bytes, safely loaded with duplicate-key rejection and schema_version1
validation. Peer snapshot was fresh (expires2026-09-28T02:42Z); NUIAK legacy summary
was expired. FR-A response4,171bytes hash matched its published digest.

Only the newly assigned `packets.TTR-STATUS-20260927` is owned by this worker.
Legacy top-level summary and other packet owners' records/timestamps remain untouched;
their stale narratives are not fresh evidence. The new entry records the reconciled
cross-project next action without re-publishing local iOS metric history.
Tasks.md holds durable next-step changes. No automatic monitor or background work.

Software: not reassessed. Data: published source verification only, intake pending.
Integration: not reassessed. Model gate: not reassessed; no promotion.
Publication and exact readback results are recorded in coordination.md.
