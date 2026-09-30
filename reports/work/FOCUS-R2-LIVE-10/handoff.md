# Revision-2 local live preflight — 2026-09-30

Capture remains blocked before dispatch. This supersedes the old-build and shutdown-Simulator blockers in FOCUS-R2-COMPAT-09, not its passing consumer tests.

## Verified runtime

- Local TTR PID 65695, helper SHA-256 `b79b34e4de18477c77c146e9485ed7948b778b38642794356a4dd357d0565fda`.
- Fixture PID 65367, executable SHA-256 `062ddfe7789ea6494f3867aa6d80924b221aff9d8b9014c1104f575230c88e41`.
- Booted tvOS 26.5 Simulator `9026ECA9-77DB-4AE6-8FE6-BB239E9571FA`.
- `readiness.json`: coordinator, companion, storage, Xcode, runner, CoreSimulator, runtime and target ready; ownership clear. Fixture is explicitly not checked by readiness.
- `scene.json`: loopback Fixture responds, but scene has zero dimensions/elements and `no_sample`; native scene readiness remains unverified.
- User grants continuing Simulator use. Scope remains three approved pairs, not remaining21 capture or training.

## Prepared input and failing boundary

`first3-local.json` preserves all three supplied recipes and limits. Only the producer's Sillycon target is rebound to the verified local UUID and a fresh campaign ID `503d53c2-d203-48bb-a31a-f7f1b5bb524e` is assigned. Original manifest is retained unchanged in FOCUS-R2-REVIEW-08.

Matching helper command:

```text
aatv --json campaign validate --manifest /Users/josephmccraw/Documents/GitHub/NativeUIAuditKit/reports/work/FOCUS-R2-LIVE-10/first3-local.json
```

`validate-local.json`: request `5D8E5C2B-FF8B-4F6D-8E33-BCF0D14C665D`, success false, invalidArgument, duration 0ms. Original producer manifest also failed (`validate.json`). No campaign start, lease, or capture was attempted.

Matching DerivedData points to `/Users/josephmccraw/Developer/TVTestRig/TVTestRig/TVTestRig.xcodeproj`, not the historical Documents checkout. Read-only source inspection shows StableCLIRunner campaign validation reads the file locally before IPC. `readManifestFile` attempts a saved project security-scope restore, then discards the underlying Data-read error and throws invalidArgument. Campaign schema errors use separate error types. This points to helper manifest access, but does not establish which OS permission or underlying file error caused it. No broad permission change, app restart, or repeated identical retry is justified.

## Exact resume condition and producer request

TTR needs an actionable manifest-read error (stage/cause and underlying domain/code, consistent with its existing recipe-read path) and a supported least-privilege way to grant/read this project manifest. Specify the exact UI folder-grant action if already supported; otherwise provide an explicit manifest-import path. Do not request Full Disk Access speculatively. Also verify campaign export can deliver back to project-local storage through its supported path.

Once manifest validation passes, qualify the native scene on this target, start only first3, retain/export all terminal results, run consumer intake and production crop QA. No additional approval is needed for the already authorized Simulator proof; a human folder-picker grant may still be required by macOS.

## Independent outcomes

### Capture dispatch check at 21:17 UTC

User explicitly requested three-pair capture and label/crop QA again. Fresh process
inspection confirms the same running host PID65695, Fixture PID65367 and helper
b79b34e4. The installed source interface still accepts only a manifest file; no
manifest-import repair is present. Producer status updated21:09:53UTC now acknowledges
`nuiak-20260930-r2-local-runtime` with state `acknowledged_diagnostic_repair_pending`
and owner `TTR campaign manifest access owner`. Repair is explicitly separate from
release packaging. This is acknowledgment, not delivery or successful validation.
No unchanged failing validation or campaign start was replayed. Three-pair capture,
native-label validation and crop QA remain unexecuted pending that concrete repair.

### Follow-up at 21:02 UTC

Runtime helper hash and TTR/Fixture PIDs remain unchanged. Producer status still
contains no response to the campaign input request. Supported `workspace refresh-access`
passed: request `3A9B2557-5E8C-46EF-BE21-3662A178487F`, workspace_mode `app_managed`,
stage `companion_write_readback`, outcome `ready`. See `workspace-access-followup.json`.
This proves the active TTR evidence store works, not that its helper can read NUIAK inputs.

Matching `WorkspaceAccessRepairView` and `refreshWorkspaceAccess` source restrict
folder reselection to the already-selected project workspace. App-managed mode
does not accept a project grant or switch workspace during repair. Consequently
the current repair UI is not an input-file grant for this campaign. No user retry
of that control, Full Disk Access, or app restart is requested.

Required producer change/answer: a supported caller-to-coordinator manifest import
(analogous to existing `fixture prepare --recipe-json`) or a dedicated user-selected
manifest grant, preserving the current workspace, exact bytes/hash and campaign
budgets. Include actionable manifest-read errors and actual sandboxed-helper tests.
Per-recipe jobs were not substituted: their advertised interface has no one-target
limit and could exceed the approved three-pair proof. No repeat campaign validation
was attempted with unchanged inputs/runtime.

- Software: prior consumer compatibility/tests passed; no code changed in this packet.
- Data: zero new pairs; no admission or crop-QA pass claimed.
- Integration: Simulator readiness passed; campaign entry blocked; native scene unqualified.
- Model: unassessed, shipped artifacts unchanged.
