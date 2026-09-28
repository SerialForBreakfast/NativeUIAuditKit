# Local action-linked recording start rejected

2026-09-28 approximately19:45–19:48UTC. User explicitly requested recording on the
new local TTR while operating its controls. No agent navigation or audio recording.

Actual process91802: matching DerivedData Debug TVTestRig.app on Maximum-mini.
Debug dylib modified2026-09-28 12:42:48PDT. CLI help omitted recorder controls;
MCP tools/list advertised record.start/status/stop. record.status returned Office
target, recording false,0 actions/frames/gaps. Control status independently confirmed
connected and selected Office, no active observation or queued commands.

One start requested with title, project-local destination
`reports/work/FOCUS-REGRESSION-V2/office-pilot-20260928-1947` and idempotency key
`nuiak-regression-v2-office-20260928-1947`. Actual response:
`isError=true`, `code=domainFailure`, `domain_code=unsupportedCapability`.
No retry, reconnect, fallback polling or session creation. Postfailure record.status
again confirms recording false,0 actions,0 frames. User control connection was not
modified. No recording/session ID was returned.

Evidence: mcp-tools.jsonl; record-status-before.jsonl; record-start.jsonl;
record-status-after.jsonl with matching stderr files. All retained locally.
No labels, crops, inference, training or model-gate outcome.

Resume condition: TTR producer identifies the exact failing record.start boundary
for the advertised local physical-device path and provides a supported setup or
matched-build repair. API advertisement/offline tests alone did not establish this
live capability. No inference that storage permission, NUIAK enablement, disconnected
video, target support or missing coordinator wiring caused the error without evidence.

Software: interface advertised, live start failed. Data: none captured. Integration:
blocked at start. Model: not assessed. No owned recording requires cleanup.
Coordination: published2026-09-28T19:49:05Z to verified SMB
`/Volumes/SharedStatusFile/nuiak/status.yaml`, packet FOCUS-HUMAN-OFFICE-01.
Follow-up preserves request nuiak-20260928T163500Z-action-linked-recorder and the
earlier supervised-external-control request. Minimal patch; schema1/unique-key YAML
validation and exact packet readback passed. Peer acknowledgment not yet observed.
