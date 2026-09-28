# New build checked — destination contract still blocks qualification

2026-09-28T21:03:51Z. User has Office control; coordinator independently confirms
connected and selected approved Office. Recorder off,0 actions/frames. No start,
navigation, reconnect, audio, producer edits or app restart during this check.

DerivedData info.plist identifies the actual build checkout as
`/Users/josephmccraw/Developer/TVTestRig`, not the older Documents/GitHub checkout.
Latest commit:0d9389abe9d83098a8c9a4dc3b3d5d7302bafcef, NUIAK bug fixes,
2026-09-28T21:00:31Z. Working tree has Package.resolved changed; no source mutation
performed here. Shared status20:55:16Z describes the changes but still carries
older source_revision c45f3e73; that field is not the current local build identity.

Running PID99680 started21:01:17Z. Debug dylib modified21:01:17Z, SHA256
80ca134c0f2d6ba15f870534e7e1b2a80a2df972e2d267b22d10b0d759c2381a.
Binary includes ProjectEvidenceStorage.resolveDestination and repaired recorder
overload. Matching helper help now lists record start/status/stop; actual record
status succeeds. Producer reports32 passing tests and nine-card dock scaling;
neither producer tests nor fixture rendering rerun by this consumer.

## Blocking review finding

The commit's diagnosis describes a relative destination, but the retained consumer
record-start request used an **absolute** NUIAK project-local destination.
ProjectEvidenceStorage.swift:117 resolves absolute URLs outside TTR's configured
root by stripping the leading slash and appending the remaining path beneath that
root. Thus `/Users/.../NativeUIAuditKit/reports/...` may become
`<TTR-root>/Users/.../NativeUIAuditKit/reports/...`, not the requested output.
MCP, IPC and coordinator invoke this resolver. Coordinator also suppresses resolver
errors using try? and has nil-destination fallback to system temporary storage.
These are source-confirmed branches, not observed writes during this check.

Doctor runLogPath points into TTR app-managed storage, but its workspace summary
does not expose an authoritative current root or exact resolved recorder destination.
Do not infer a verified NUIAK folder grant from the connected device or writable shell.
Do not dispatch another start whose resolved output boundary cannot be verified.

Producer next action: preserve explicit absolute destination semantics or reject
with a typed actionable error; anchor only actual relative inputs; expose resolved
destination before writes and fail closed on storage/grant failure. Provide a
supported consumer export if recordings must reside in TTR-managed storage.
Test the original absolute consumer path, outside-root rejection, relative path,
missing grant and no-fallback cases through real IPC/MCP boundaries.

Software: new helper/status and fix symbols verified, destination-contract defect
identified. Data: none new. Integration: blocked before capture pending a supported
verified destination/export contract. Model gate: unassessed. Original failure
and user connection preserved. No claim that all requirements are fixed.
