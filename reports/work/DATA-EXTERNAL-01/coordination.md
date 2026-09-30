# Unpublished storage update

**Superseded2026-09-30: cancelled by user.** Close the existing storage request as
cancelled on next verified publication; do not perform pending authentication,
mount or migration steps below. Original share remains unmounted. See
../FOCUS-GEOMETRY-RESUME-03/coordination.md for current unpublished cancellation.

publication: unpublished
observed_at: 2026-09-30T16:05:08Z
destination: smb://sillycon.local/SharedStatusFile, nuiak/status.yaml, packets.DATA-EXTERNAL-01

OS mount inspection found no expected coordination SMB mount; historical
`/Volumes/SharedStatusFile/nuiak/status.yaml` is absent. No lookalike directory,
automatic remount, alternative transport or permission change attempted.

Draft delta for existing request nuiak-20260930-external-training-storage:
Same external volume UUID now mounted as training, folder `/Volumes/training/data_training`,
about1.8TiB free; fresh disk query and Max share registration verify the rename.
SMB share name remains data_training. No consumer rerouting or migration performed.
Latest human-supplied Sillycon share-listing
attempt rejects SMB authentication. Do not redirect producer jobs or infer shared
write readiness. Operator must verify Max SMB account enablement/authentication;
successful listing/mount and bounded write-readback remain prerequisites.

Peer acknowledgment of this delta unavailable. Resume publication after verified
coordination mount returns; reread and patch only owned entry, preserving concurrent
changes. This draft does not refresh the previous shared snapshot or install polling.
