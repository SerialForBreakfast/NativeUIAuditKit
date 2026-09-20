# FocusRing producer compatibility request

publication: unpublished

Owner: architect, this documentation/coordination assignment.
Observed 2026-09-20: mount inventory contains no SMB/SharedStatus mount.
Destination when verified: smb://sillycon.local/SharedStatusFile, NUA-owned
`nuiak/requests/`, referenced from `nuiak/status.yaml`.
Local draft: [request.yaml](request.yaml). No remote write/readback or peer acknowledgment.

Resume publication after the share is mounted through the normal authorized path.
Re-read current peer/status data, verify mount ownership, check for duplicate requests,
refresh draft observation/expiry times, publish a unique request and targeted NUA status
reference, validate YAML and read back. Preserve other entries and all unknown fields.
Do not renew another worker's timestamps or claim receipt without acknowledgment.
No automatic polling, mounting, SSH or device operation is requested.

This request is for TTR-owned compatibility review and assignment, not local dataset
progress. Missing share does not block NUA offline software work.
