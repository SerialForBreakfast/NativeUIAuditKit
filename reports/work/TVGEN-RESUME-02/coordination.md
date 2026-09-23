# Coordination delivery

Superseding readback2026-09-23 00:27Z: after maintainer reconnection, the23:06Z
entry was present on the verified share. Delivery is now confirmed by readback.
The latest entry/report is TTR-CHECK-20260923-0022/coordination.md. The failure
record below describes the original attempt, not the current connection state.

Publication: **write reported successful; readback unavailable**. Verified smbfs mount at
`sillycon.local/SharedStatusFile`; exact destination
`/Volumes/SharedStatusFile/nuiak/status.yaml`, own packet
`TTR-SMOKE-20260922-2119`, observation update23:06:42Z.

Published only the cross-project consequence: NUA continuation/assembly software
is ready; repaired geometry can unlock the direct pilot independently of TTR's
sidecar work. Last runtime check was22:57Z, explicitly not renewed by publication.
Before editing,28 packet entries and three existing request IDs were present.
The minimal targeted patch reported success, but subsequent readback failed with
FileNotFoundError for the exact destination. Delivery/integrity is therefore
unverified, not a claimed readback pass. No local lookalike was created or stale
whole-file snapshot republished. The intended update is retained in this handoff;
reconcile against a fresh shared file after access returns.

Bounded follow-up: mount remains smbfs and `ls` sees the file, but both restricted
and approved-host Python opens return ENOENT. Cause is unresolved; do not call the
share disconnected or weaken permissions. No further retry or rewrite performed.

Producer's22:00:22Z acknowledgments remain historical receipt evidence, not fresh
status or repair completion. No new acknowledgment of this update observed.
No datasets, images, model artifacts or broad local development logs published.
