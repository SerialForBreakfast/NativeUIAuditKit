# Shared publication receipt — metadata only

**Later transition:** approved artifact download and receiver receipt completed;
see [receipt.md](receipt.md) for the current packet/readback hashes and exact immutable
receipt path. The earlier `not_copied` state below is historical and superseded.

Request: user asked to check transfers/updates and update status.yaml.
Protocol: repository SharedStatusSkill.md and Instructions.md, matching shared copies.
Verified endpoint: smb://sillycon.local/SharedStatusFile (smbfs).

Published destination:
`/Volumes/SharedStatusFile/nuiak/status.yaml`, entry `packets.TTR-STATUS-20260927`.
Local entry: `reports/coordination/nuiak/status.yaml`, same packet.
Observed2026-09-27T15:26:26Z; valid until2026-09-27T15:56:26Z.

Publication **passed**, with scoped host approval. Immediately before the targeted
patch the shared hash still matched the fresh snapshot. Safe YAML parsing with
duplicate-key rejection and schema_version1 validation passed before and after.
Readback verified the exact new entry, matching local/shared entry values, and exact
semantic preservation of every preexisting packet and all top-level/unknown fields.
Only this worker's new packet was added; no peer or human-reservation file was edited.

Shared before SHA-256:
`2f4edbd2349f392bb342d0f527568389c00ab48c8bc2a6fa97e7220d8a9752c4`.
Shared after SHA-256:
`8f084ea561d8e32010a0d6a376f7bd8bd2fc9cd6fd0110e3b9dfd7bcca721419`.
Local after SHA-256:
`91480d8a856c2074531d16a083cb1aec391f1eceac98b8802479823b7c75b6fc`.
Local/shared whole-file hashes differ because their older owner-managed fields differ;
no stale whole-file synchronization was attempted. Older top-level summaries remain
expired and should not override the fresh packet. Readback is not a transactional lock.

Peer status inspected:23,495bytes, SHA-256
`dfb015d5ea636721a306a5c8f01882e15df80ec30801ef14e435dad1ed41ac9f`,
observed version2026-09-27T02:42Z, valid until2026-09-28T02:42Z.
Its acknowledgment of the earlier role freeze is confirmed. Peer acknowledgment of
**this new update** is not observed; no monitor/polling was installed.

Artifact facts: four source archives and2,478-byte manifest were hash/size verified
in place (see review.md). **No receiver copy, safe extraction, consumer acceptance,
training eligibility or sender cleanup** is claimed. Incoming transfer request was
acknowledged `received`, not completed. TTR must retain copies until a real receiver
copy receipt. File-transfer/intake execution awaits a separate current assignment
identifying exact names/sizes; publication approval reported by TTR is not an instruction
to execute it in this status-only turn.

Verification is metadata-only: bounded safe YAML parse, source hashes, ownership/
readback checks and git diff --check. No code changed and no build/test rerun is claimed.
