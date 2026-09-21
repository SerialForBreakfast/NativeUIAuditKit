# Office smoke coordination

publication: published

Latest update 2026-09-21T00:28:21Z: approved local staging attempt blocked before
directory creation; owned processes canceled, no lease/capture started. Maintainer
is remote; no access bypass attempted. See [staging-attempt.md](staging-attempt.md).
Published minimally to `/Volumes/SharedStatusFile/nuiak/status.yaml`, verified
smbfs mount to sillycon.local, safe YAML v1 parse and packet readback passed.
Peer acknowledgment of this update is not observed. Earlier updates below are history.

Latest update 2026-09-20T23:59:01Z: user directed local execution. Sillycon request
closed/withdrawn to avoid duplicate operators. Local preflight succeeded; batch rejected
NUIAK output with validation/outputOutsideProject before capture. Owned lease released
and fresh Fixture scene healthy. Shared packet updated; see [local-attempt.md](local-attempt.md).
Earlier continuation/receipt notes below are historical, not current dispatch authority.

## Continuation observed 2026-09-20T23:46:53Z

TTR's 23:43:23Z acknowledgment explicitly says coordination-only: no operation,
reservation, preflight, capture or transfer was started. The original request is now
marked acknowledged, not completed. Its packet was refreshed with the user's
continuation and a request for an owning TTR task plus preflight evidence or the exact
direct-local approval requirement. No second smoke was requested.

The shared-status guide requires this receipt/execution distinction. Minimal changes
were published to the same verified destination; safe YAML readback confirmed the
acknowledged state, continuation and local-authority caveat. Other worker entries were
preserved. Peer receipt of this newer continuation has not been observed.

Next: TTR must dispatch within its local authority or name its exact blocker. NUIAK has
no bundle/location/hash handoff yet. See [intake-readiness.md](intake-readiness.md).
The older publication snapshot below remains historical evidence.

- Request: `nuiak-20260920T233713Z-office-focus-smoke`.
- Verified endpoint: `smb://sillycon.local/SharedStatusFile`, mounted with smbfs.
- Exact destination: `/Volumes/SharedStatusFile/nuiak/status.yaml`,
  `packets.OFFICE-FOCUS-SMOKE.pending_requests`.
- Published packet observed at 2026-09-20T23:37:13Z; advisory validity ends
  2026-09-21T00:07:13Z. Staleness requires rechecking, never an automatic retry.
- Readback: safe YAML v1 parse and full packet equality with
  [status-draft.yaml](status-draft.yaml) passed. The architect summary now points
  to this narrowly scoped exception; its historical timestamps were not refreshed.
- Readback file SHA256: `ccb2d8fdfb3da4c2d18737989fb7efc6e514a8b9cc5cc46920a903e405047cfa`.
  This is a snapshot, not a lock or guarantee against later writers.
- Peer acknowledgment: not observed; TTR status did not reference this request ID.
- Shared guides matched the repository copies by hash. No reservations file was
  present. No exclusive reservation is claimed.

The user authorized exactly one physical Office fixture smoke. Prior Office release
is superseded only for that request; broader capture and training remain unauthorized.
Simulator execution remains paused until further notice. Existing worker packets and
the coordinator-repair request were preserved. Peer status has a future timestamp
relative to this host's observation; it was not treated as fresh readiness evidence.
The request requires actual Office target/control/capture checks before mutation.

Await peer acceptance and producer-owned execution evidence. Then confirm transfer
before NUIAK intake; no dataset bytes belong on the status share. No polling or
background monitoring was installed, and no capture was performed by this task.
