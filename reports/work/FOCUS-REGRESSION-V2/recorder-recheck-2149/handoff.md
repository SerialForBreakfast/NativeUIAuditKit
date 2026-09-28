# Capture preflight ready via app-owned storage; approval pending

2026-09-28. Actual build checkout Developer/TVTestRig HEAD7ddd182b (More bugfixes),
running PID3876 started21:49:02Z. Producer shared status21:47:52Z describes repair
delta over0d9389ab; local commit includes30 changed files matching that scope.
Matching running helper advertises prepare/export and answers coordinator status:
Office selected and connected. No restart, navigation or capture performed.

Source review confirms relative markers preserved across IPC, explicit absolute
paths retained or rejected, no old re-anchoring or temporary start fallback.
prepareActionRecording resolves/validates without creating a bundle or capturing.
New documented export verifies/copies a finalized bundle without recapture.

Actual prepare of absolute NUIAK project output returns persistenceFailed: the
current TTR storage grant does not establish direct delivery there. Default prepare
succeeds and returns:
`/Users/josephmccraw/Library/Containers/com.showblender.TVTestRig/Data/.tvtr/.local-work/recordings/96de1844-9f56-4b28-8578-6574c6cdac48`.
isRecording=false,0 frames/actions. This is a prepared path, not created data.
Evidence: help.txt, status.json, prepare.json, prepare-default.json and stderr.

Previous path-contract code blocker resolved at review/preflight level. Remaining
consumer boundary is explicit user authorization to let TTR record in its own
container, outside NUIAK's normal project-only output rule, then export into a fresh
NUIAK project-local destination. No automatic exception inferred. Once approved,
one short human-operated trial can test actual capture, action/frame association,
Stop/cleanup, export integrity and schema2 intake. Full end-to-end qualification
and schema2 importer compatibility remain pending, not prerequisites to recording
an approved diagnostic trial. No new training/evaluation eligibility implied.

Software: new storage preflight and documented export verified/read. Data: none new.
Integration: preflight passed for app-owned storage, live/export/intake pending.
Model gate: unassessed. No claim that producer's121 tests were rerun by NUIAK.
