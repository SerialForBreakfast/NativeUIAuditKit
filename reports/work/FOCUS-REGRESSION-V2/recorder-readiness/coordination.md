# Recorder-start failure coordination

publication: published_and_read_back
observed_at: 2026-09-28T19:49:05Z
valid_until: 2026-09-28T20:19:05Z
destination: /Volumes/SharedStatusFile/nuiak/status.yaml
packet: FOCUS-HUMAN-OFFICE-01
request: nuiak-20260928T163500Z-action-linked-recorder
peer_acknowledgment: not_observed

OS mount verified smbfs on sillycon.local/SharedStatusFile. Fresh packet read before
minimal owned-entry patch; preserved earlier request and unrelated packets/top-level
fields. Safe YAML readback rejects duplicate keys; schema and intended timestamp,
failure summary and request state verified. No peer files, reservations, credentials,
raw media or general training status published. No new device operation this update.

Next owner: TTR capture/runtime implementation. Diagnose record.start capability
rejection on the actual local physical-device path, then provide supported setup
or matched repair and exact bundle contract for consumer acceptance.
