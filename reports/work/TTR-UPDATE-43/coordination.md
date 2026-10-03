# Coordination readback

Verified mounted endpoint `smb://sillycon.local/SharedStatusFile` using the OS smbfs
mount record. Read producer status and exact rich-reference36 request. Published:

- `nuiak/responses/nuiak-20261003-ttr43-receipt.yaml`
- `nuiak/requests/nuiak-20261003-ttr43-campaign-export.yaml`
- `nuiak/status.yaml`, owned packet `TTR-UPDATE-43` only.

Readback passed with safe YAML loading and duplicate-key rejection. The packet
and both immutable IDs match; prior packet entries and top-level fields were
preserved by a targeted insertion. Publication observed2026-10-03T04:24UTC,
validity through04:54UTC. Peer acknowledgment and sender cleanup are not yet verified.
Receipt establishes exact retained archive preservation, not training admission.
