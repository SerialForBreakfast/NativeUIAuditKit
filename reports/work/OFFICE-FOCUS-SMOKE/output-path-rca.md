# RCA: Office smoke outputOutsideProject

2026-09-21 00:22 UTC. Root cause confirmed in the installed local Debug helper,
not inferred solely from source. No capture or device mutation occurred during RCA.

## Causal chain

1. Caller launches the matching TVTestRig app executable in stable CLI mode from NUIAK.
2. Inside that app process, FileManager.currentDirectoryPath is the app container's
   Data directory, not the caller's NUIAK directory.
3. StableCLIRunner.harvestProjectRoot first tries that cwd, then app workspace roots.
   A NUIAK destination matches none, so it returns cwd as the fallback.
4. FixtureBatchHarvestEngine.run compares destination against that container root.
   NUIAK is outside it, so validation throws outputOutsideProject before recipes,
   staging, preflight, recipe mutation or frame capture.

The helper's container-scoped execution and cwd-derived root selection conflict with
the caller's assumption that shell cwd makes NUIAK an approved output workspace.
Changing directory in the parent shell alone did not resolve it.

## Direct evidence

Installed executable:
`/Users/josephmccraw/Library/Developer/Xcode/DerivedData/TVTestRig-bfjtodidumtdyagsgxcmwrmheuxr/Build/Products/Debug/TVTestRig.app/Contents/MacOS/TVTestRig`.

LLDB launched disposable helper processes, not the occupied GUI, with explicit
working directory `/Users/josephmccraw/Documents/GitHub/NativeUIAuditKit`.
Both used a deliberately nonexistent recipe directory; capture was unreachable.
Processes were stopped at breakpoints and terminated without continuing into harvest.

- PID 45840, FixtureBatchHarvestEngine.swift:377:
  root/projectRoot = `file:///Users/josephmccraw/Library/Containers/com.showblender.TVTestRig/Data/`;
  destination = NUIAK/dataset/tvos_captures/office/rca-never-capture.
- PID 45918, StableCLIRunner.swift:498:
  cwd = the same container Data URL; output = the NUIAK destination.
- Non-debugger negative control, PID 45882: output under existing container .tvtr
  passed containment and failed at intentionally nonexistent recipes with
  recipesDirectoryInvalid, exit 64, request 7C759F2A-2A3E-4F7E-B451-A61F4BCDBB93.
  Source order checks recipe directory before creating staging or contacting devices.
- NUIAK root/destination resolve without symlink escape.
- Original office output parent was absent. This is a subsequent setup prerequisite,
  not the observed cause: outputParentUnavailable is checked after containment.

Source reference inspected: TVTestRig HEAD 686d80c74e4586dfeb095ddcbdc145e5fc86ee8e,
with pre-existing project.pbxproj modification left untouched. Debugger breakpoints
resolved in the installed dylib at the relevant source lines. No claim is made that
every other installed artifact is byte-identical to HEAD.

## Workaround — no producer feature required for containment

Use one explicitly authorized staging directory:
`/Users/josephmccraw/Library/Containers/com.showblender.TVTestRig/Data/.tvtr/nuiak-office-smoke-20260921/`.

Put the single recipe under recipes/, use a new nonexistent bundle/ destination,
and retain diagnostics there only if necessary. The parent .tvtr already exists;
the proposed staging directory must be checked for collision before creation.
On a separately authorized retry, recheck Office availability, source and ownership,
run exactly one bounded smoke and clean up only acquired resources.
Copy completed bytes to NUIAK's gitignored office corpus and verify hashes.
Retain originals/partials; no automatic deletion or broad container access.

Containment behavior is tested; recipe access, writes, actual capture and copying at
the proposed directory are NOT yet qualified. This option requires an explicit narrow
exception to NUIAK's outside-project output rule. No such writes were made during RCA.

## Durable TTR improvement proposal

No new capture capability is needed. A producer-owned task should:

- Add side-effect-free batch preflight that reports the effective workspace, requested
  destination, containment outcome, parent readiness and recipe readability before leases.
- Stop treating arbitrary process cwd as the implicit authority boundary. Resolve an
  explicit approved workspace consistent with signed app execution; preserve containment
  and symlink rejection, do not remove checks or broaden entitlements.
- Keep CLI connection-workspace selection separate from dataset export authorization.
  --project selects coordinator routing and needs a valid matching TVTestRig checkout;
  pointing it at NUIAK is not a valid export workaround.
- If direct NUIAK output is desired, provide explicit user-granted directory access or
  a supported export/copy operation; verify grants in the actual helper process.
- Test signed CLI launches from unrelated cwd, container output, denied external output,
  nonexistent parents, symlink escape and no device mutation on preflight failure.

No TTR source/build was edited, no restart/signing change was made and no device
operation was retried. App diagnostic-file persistence warnings remain a separate
issue; they did not prevent CLI JSON or explain this typed containment rejection.
