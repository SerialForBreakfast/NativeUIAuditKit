# EXT-CAP-02 coordination

Observed producer status: 2026-09-28T15:32:34Z; schema1, valid-until2026-09-29T15:32:34Z.
Verified expected SMB endpoint and plan/runbook/response metadata hashes. See [handoff](handoff.md).

Publication: **published and read back**, destination `/Volumes/SharedStatusFile/nuiak/status.yaml`, owned `packets.EXT-CAP-02` only, updated2026-09-28T15:45:23Z/valid-until16:15:23Z. Safe schema1/duplicate-key validation passed. Removing only the new packet reproduced the pre-publication SHA256 `c8f2d48249f73b45b3193b80d3ada97ee5d873a2726fba75af5b84f8b03aad8f`, confirming every other byte was preserved at readback. No peer-owned files changed; this best-effort check is not a future-write lock.

Feedback: local signed remote client discovered; CLI and MCP initialization/tool listing passed. CLI state unpaired; LAN discovery returned zero candidates. Custom state directory missing from printed registration. Exact local binary/source match unverified despite new helpers present; do not infer a rebuild requirement from the old adjacent checkout. Need Sillycon service/host-port, running candidate binding and fresh booted tvOS simulator UUID. Operator fingerprint comparison and exact grant confirmation remain required.

Peer acknowledgment: not observed. No device grant, capture or artifact receipt created. No original Photos transfer requested or performed here. Native input/frame recording remains separate from still-only transport.
