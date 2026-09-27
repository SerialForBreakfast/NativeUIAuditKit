# Frozen surface transfer — received and verified

2026-09-27. Maintainer confirmed the existing per-file size approval and explicitly
directed download/receipt unless local space threatened current work. No repeat size
approval was needed. Scope completed: download, local integrity verification, bounded
archive/role preflight and metadata receipt. No training, inference or device work.

## Local copies

Directory: `dataset/tvos_captures/frozen-surface-receipt-20260927/` (gitignored).
The producer manifest is retained byte-for-byte alongside all four original archives.
No existing destination was overwritten; no source/shared file was changed or deleted.

| File group | Local verified bytes | Frozen role |
| --- | --- | --- |
| cinema_rows | 172053102 | appearance-validation |
| album_grid | 172156757 | appearance-validation |
| memory_mosaic | 171478657 | final-challenge |
| icon_shelf | 180531624 | final-challenge |

Total archive bytes696,220,140; manifest2,478bytes. Every local SHA-256 and exact
size matches the pinned producer manifest. See [full immutable identities](transfer-receipt.json).
Verification time2026-09-27T15:45:33Z. Approximately44.4GB was available before;
43,680,043,008bytes (43.68GB) remained after. No storage cleanup was needed.

## Bounded preflight

[Archive checks](archive-preflight.json) passed without extraction. Each archive
has164 members:82 payload/directory members matching the producer count, plus82
AppleDouble metadata members. No absolute/traversal paths, links, special files or
case-folded duplicate destinations were found. Limits were1,000members/4GB expanded
per archive and2MB per parsed metadata file. Actual total expanded size728,518,925bytes.

All four export-manifest hashes match the producer's pinned hashes; each contains24
rows. Embedded provenance matches the exact group, role, job, seed7 and NUIAK freeze
timestamp2026-09-26T03:10:28Z. cinema_rows exports24 `held-out` rows; the other three
export24 `training` defaults each. Those raw defaults are preserved, not adopted:
the frozen evaluation roles remain authoritative for prospective consumer intake.
No data was added to a training or evaluation manifest, and final-challenge images
remain unscored. Crop/native-label/semantic and independence acceptance remains pending.

## Published receiver receipt

Request: `tvtestrig-20260927-frozen-surface-captures`.
Manifest ID: `tvtestrig-20260926-frozen-surface-captures` (preserved separately).
Receipt: `nuiak-20260927T154533Z-frozen-surface-receipt`.
Shared immutable path:
`/Volumes/SharedStatusFile/nuiak/responses/nuiak-20260927T154533Z-frozen-surface-receipt.yaml`.
Receipt SHA-256:
`cda058c3d839fd71be69dc19163478208dbe11070bc9f0752cd4d0add352e023`.

Published and read back with scoped host approval. Bounded safe YAML parsing,
duplicate-key rejection, schema_version1 and exact receipt equality passed.
`/Volumes/SharedStatusFile/nuiak/status.yaml` packet `TTR-STATUS-20260927` now reports
`copied_and_verified`, removing the receipt-authority blocker. Packet observation
2026-09-27T15:47:16Z, validity to16:17:16Z. All other packets/top-level/unknown fields
were preserved; matching local packet verified. Shared status SHA-256 after publication:
`77fb769b1a797b3005f431200862264c56e5e30ada3be7033cf7f12763e2d44b`.

Peer acknowledgment and sender cleanup have not been observed. TTR owns cleanup
of only the matching shared copies after checking this receipt; receiver deleted
nothing. This successful transfer is not consumer/model acceptance. Software and
model gates were not reassessed. No code changes or build/test rerun; verification
was copy/hash/size, bounded archive/provenance checks, YAML readback and diff checks.

Next: use these retained local originals for consumer crop/label/independence intake,
without recapture or another size-approval loop. Photos and semantic VoiceOver
alignment remain distinct coverage lanes, not blockers to the completed download.
