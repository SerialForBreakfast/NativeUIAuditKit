# TTR coordination — paired-window findings

Verified existing smbfs mount from sillycon.local/SharedStatusFile at
/Volumes/SharedStatusFile; no mount/reconnection/external-storage work.

Read producer23:02:21UTC snapshot, valid until00:02:21UTC: reports signed recovery
passed locally and remaining42pairs underway in sevenbounded batches. This is
producer-reported work, not consumer delivery or current hardware readiness.
No acknowledgment of `nuiak-20261001-transfer10-coverage` observed in that snapshot.

At23:29UTC published own `packets.FOCUS-PAIRED-11` in
`/Volumes/SharedStatusFile/nuiak/status.yaml`, referencing the same request rather
than creating a duplicate. Added concrete requirement for movement/scroll evidence
and unchanged/content-only controls. No new capture dispatched or existing campaign
cancelled. Existing accepted sixpairs need no redraw/recapture.

Schema1 and duplicate-key validation passed; readback confirms intended packet.
Canonical digest of all unrelated packet/top-level content stayed
`2a6fb64307f7b905cd9994733b257e8bc8227d4fd89805a44e6417e3d4acef11`.
Peer acknowledgment of this follow-up remains unobserved. Native/runtime integration
unqualified; passed data outcome refers only to retained already-accepted membership.
