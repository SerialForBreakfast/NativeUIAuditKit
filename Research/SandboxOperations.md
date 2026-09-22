# macOS permissions: diagnose the layer, preserve the boundary

Reviewed 2026-09-22. Guidance only: no authority to alter entitlements, privacy
consent, certificates, output roots or producer code. Supersedes the broad claims
in the earlier BP-67 write-up; training quotas and ADR-0010 remain unchanged.

## Source-backed corrections

- App Sandbox is required for Mac App Store apps, not automatically for outside-
  store distribution. Unsandboxed developer tooling can be a deliberate design,
  not a repair agents apply to installed binaries. [Apple App Sandbox](https://developer.apple.com/documentation/security/protecting-user-data-with-app-sandbox).
- Developer ID, notarization and Hardened Runtime concern distribution trust.
  Notarization requires Hardened Runtime for applicable executables; it is not a
  prerequisite for every local test build. App Store submission is a separate
  workflow. None grants arbitrary file access. [Apple notarization](https://developer.apple.com/documentation/security/notarizing-macos-software-before-distribution).
- Helper placement does not determine effective permissions. Spawned children
  inherit restrictions; static inheritance is not every dynamic user-selected
  file grant. Transfer authorized data or bookmarks, not just paths.
  [Apple inheritance](https://developer.apple.com/library/archive/documentation/Miscellaneous/Reference/EntitlementKeyReference/Chapters/EnablingAppSandbox.html).
- Cocoa 513 does not uniquely identify App Sandbox or equal POSIX EPERM. Preserve
  underlying errors. BSD/ACL permissions, App Sandbox, mandatory privacy protection
  and endpoint-security policy differ. Unsandboxed apps still face mandatory
  protection; stable signing identity helps preserve privacy decisions across
  builds. A headless context may deny rather than prompt. [Apple DTS](https://developer.apple.com/forums/thread/678819).
- Persistent bookmarks need resolution, stale-data refresh, access activation and
  balanced release after asynchronous work completes. Cross-process implicit
  bookmarks differ from stored app-scoped bookmarks. [Apple file access](https://developer.apple.com/documentation/security/accessing-files-from-the-macos-app-sandbox).
- Finder/resource-fork metadata can independently prevent signing. Inspect the
  exact generated bundle; do not infer bad certificates. [Apple QA1940](https://developer.apple.com/library/archive/qa/qa1940/_index.html).
- Codex execution sandbox and approval routing are separate. Auto-review does not
  remove sandbox restrictions; protected skill paths may require approval even in
  writable roots. [Official agent security guidance](https://learn.chatgpt.com/docs/agent-approvals-security).

## Choose the smallest remedy

| Observed failure | First check | Next action |
|---|---|---|
| Restricted-agent command fails | Exact binary/command, stderr, permission context | Scoped approval for a safe comparison, not app re-signing |
| Cocoa file access | Actual writer/path and underlying domain/code | Diagnose that process's grant; another writer passing proves little |
| Stale bookmark | Existing app-owned refresh/access result | Refresh valid stored grant or explicitly reselect; no prompt loop |
| Connection refused | Matching endpoint/process/launch mode | Reachability diagnosis; not assumed filesystem denial or automatic restart |
| Privacy denial | Responsible app and privacy category | Narrow maintainer-mediated consent; no blanket Full Disk Access/TCC reset |
| Finder metadata signing error | Read-only `xattr -lr` on exact build product | Scoped owned-output correction if approved; preserve unrelated attributes |
| Export fails after capture | Retained result and pending-operation state | Repair/approve export only; do not recapture |

## Faster execution protocol — repository recommendations

1. Scope the whole tranche once: binaries, target, inputs/time limits, output root,
   owned cleanup, unavoidable platform storage and stop conditions. Ask only for
   missing authority, not every already-authorized checkpoint. Host approval checks
   still apply; previous approval is not a perpetual permission grant.
2. Keep explicit outputs, configurable caches, DerivedData and logs project-local.
   TMPDIR/module-cache/result-bundle settings do not contain every Xcode service or
   runtime write. Declare normal simulator/Xcode storage before setup; if not
   approved, stop that operation. Never spoof HOME or scrape app containers.
3. Reuse the demonstrated execution context for the same tool/action class. Request
   known required scoped host access directly instead of first reproducing a known
   denial. A safe read-only/help comparison can isolate context; uncertain mutations
   must be reconciled, never replayed as a permissions probe.
4. Retain source/binary/toolchain identities and setup evidence; refresh target,
   ownership and observation freshness before input. Rebuild only relevant changes.
   A changed environment requires a fresh diagnosis, not blind reuse.
5. Keep one execution receipt in the existing handoff:
   `actor/launch context | tool/build | action/target | explicit outputs | implicit
   storage approval | error chain | remedy/result | exact resume condition`.
   No bookmark bytes, credentials or private screen text in shared status.

No sudo, chmod widening, global sandbox disablement, TCC reset, service restart,
certificate repair, quarantine stripping or installed-app re-signing is implied.
The isolated unsigned simulator test configuration previously approved is not a
production signing policy. FileProvider/sync involvement in metadata introduction
is a hypothesis until traced; do not relocate the workspace without authority.

## Producer recommendations — separate assignment required

Use a clear writer contract: app-owned staging plus supported hash-verified export,
or bounded data transferred to an authorized caller-owned writer. IPC does not
make a caller unconfined. Test the actual capture/export writer and publication
path, not an unrelated temporary-file writer. Reuse existing TTR job/export and
diagnostic interfaces where qualified; no privileged helper or remote shell.
Return typed stage/actor/path/error and repair outcomes, plus completed-artifact
evidence. Release architecture changes remain TTR maintainer decisions.

## Evidence and behavioral checks

- [OS-FOCUS-01](../reports/work/OS-FOCUS-01/live-20260922-0712/handoff.md): capture
  passed, restricted TestReport export failed, approved export succeeded without
  repeating inputs. Route: execution/export permission, not TTR rebuild.
- [Runner preparation](../reports/work/OS-FOCUS-01/handoff.md): Finder metadata
  signing failure. Route: build artifact inspection, not privacy consent.
- [Iteration review](IterationEfficiency.md): readiness passed before screenshot
  writer EPERM. Route: producer's actual writer, not another broad readiness loop.
- Missing native focus after successful capture is a label-binding failure, not a
  permission failure. No security change can substitute requested focus for truth.

These are case-based walkthroughs, not a new live qualification. Documentation-only
changes need links/frontmatter/diff checks, not another simulator or full build.
Measure repeated denials, approval wait, needless rebuilds and handoffs-to-artifact
in the next three real iterations. No percentage time-saving claim or monitoring.
