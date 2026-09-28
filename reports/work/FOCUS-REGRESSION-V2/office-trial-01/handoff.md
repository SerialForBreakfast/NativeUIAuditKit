# Office recorder start: persistence failure

2026-09-28. User confirmed connected controls and a safe screen, authorizing the
short human-operated recording trial. No agent navigation or audio recording.

Initial device.list incorrectly reported Office disconnected. No mutation occurred
in that preflight. Matching CLI coordinator status then confirmed connected control,
selected Office and controlConnection.deviceID matching the approved target. A fresh
coordinator check immediately before start confirmed the same. Discovery inventory
must not override that live coordinator evidence. Prior recheck's disconnected
conclusion was based on inventory and is superseded by this stronger observation.

Capture resource available; recorder off; provider idle; audio inactive. One actual
record.start used project-local destination
`reports/work/FOCUS-REGRESSION-V2/office-trial-01/bundle`, title NUIAK Office bounded
human trial and idempotency key `nuiak-office-trial-20260928-01`.
Response: isError=true, domainFailure/persistenceFailed. Immediate record.status:
isRecording=false,0 actions,0 frames,0 gaps; no recording ID returned. No repeated
start or default-storage fallback. User control was not disconnected.

The repaired overload is present and unsupportedCapability no longer occurs at
this call; storage/export remains unqualified. Persistence failure alone does not
prove a permissions cause. TTR must identify the exact failing write/operation and
supported project-local delivery path, or a documented app-owned recording plus
consumer export contract. Do not prescribe permissions weakening, reinstalling,
re-pairing or manually writing app storage.

Evidence: start.jsonl/stderr (inventory-only preflight), coordinator-status.json,
record-start.jsonl/stderr (fresh coordinator, preflight, single start, postflight).
Software: start method reachable, failure retained. Data: no frames. Integration:
blocked at persistence. Model: unassessed. No owned recording needs stopping.
