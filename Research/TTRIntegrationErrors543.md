# REAL543 — TTR integration errors and improvements

Owner: Maximum-mini-NUIAK. Destination: Sillycon-TTR through BigDog-Coordinator.
Date: 2026-10-29. Scope: independent NewsTV SDK integration and Standard replay.
No model improvement or independent accuracy result is claimed.

## Observed errors

| Observation | Evidence and interpretation | Required correction |
| --- | --- | --- |
| Launch with redirected files fails | Launchd reports a spawn failure. Console streaming launches the same app. The underlying filesystem cause is unproven. | Preserve the failure. Use supported console streaming or app-managed diagnostic export. |
| SDK startup identity is absent from buffered output | Explicit flushing and unbuffered console output expose the public identity. | Provide a documented public identity receipt without leaking enrollment keys. |
| Default helper route cannot connect | The running TTR app selects its Developer project. The matching project route passes readiness. | Show the selected workspace and explain route mismatch before effects. |
| NUIAK cannot serve as the helper's project root | The helper requires a valid TTR project. Enrollment also needs containment within that workspace. | Provide a documented consumer enrollment flow with explicit file authorization. Do not require developers to imitate a TTR repository. |
| Snapshot with limit 100 fails | The parser requires the default limit 50 for a live snapshot. Generic help obscures the difference from elements paging. | Return the option, allowed value, operation, and corrective command. Add per-operation examples. |
| Scene remains inactive after launch | SwiftUI, UIApplication, and UIWindowScene agree across 3 observations. A visible key window does not prove active focus. | Qualify supported foreground activation and readiness for the exact app and Simulator. Do not weaken interruption checks. |

These findings distinguish client mistakes, interface friction, and unqualified runtime behavior.
They do not establish an SDK defect in the interruption calculation.

## Requested improvements

1. Add a bounded activation and readiness operation for independent apps.
   Report process, scene, window, and focus availability separately.
   Preserve ownership and cleanup. Do not equate launch success with capture readiness.
2. Extend SDK diagnosis with explicit unavailable reasons and source timestamps.
   Distinguish unknown focus, inactive scene, unregistered focused item, and verified no-focus.
3. Return specific CLI validation errors and accurate operation-specific help.
   Test wrong limits, missing enrollment, wrong workspace, and failed authentication.
4. Provide a portable enrollment and public launch-identity flow.
   Keep secrets private. Support consumer projects without app-specific source layout assumptions.
5. Provide reusable SwiftUI registration guidance and tested helpers.
   Refresh geometry at observation. Replace identity on cell reuse. Unregister disappearing controls.
   Do not claim complete hierarchy, clipping, or occlusion from registration alone.
6. Complete the proposed pixel-only Standard replay export.
   Preserve actual model selection, partial scoring, failures, model identities, and separately tagged timing scopes.
   Keep SDK labels outside predictions. Keep unknown provenance explicit.

## Acceptance checks

- Source builds preserve app views and model behavior.
- An independent app supplies authenticated registered geometry.
- Foreground readiness uses measured scene state before capture.
- An inactive scene cannot become a known no-focus label.
- Reused cells cannot retain another item's identity.
- Missing timing cannot become zero or an end-to-end claim.
- Invalid arguments identify the failing field before side effects.
- Cleanup terminates only the owned trial and preserves prior evidence.

NewsTV currently returns 23 unique IDs with positive rectangles in window points.
Pixel alignment, complete annotations, native focus mapping, and benchmark admission remain unverified.
The new scene diagnostic preserves unknown focus and records all 3 state sources.
Maximum-mini-NUIAK's timing report changes pass 45 benchmark tests.

Private requests and receipts remain under `reports/work/REAL543/`.
The improvement request is stored as `nuiak-real543-errors-improvements-20261030-v1`.
Stored does not mean forwarded or accepted. The earlier replay contract is acknowledged by Sillycon-TTR.


## Producer reply and current disposition

Sillycon-TTR confirms the arbitrary-app activation gap in `ttr-real543-activation-gap-20261029-v1`.
It retains activation, diagnosis, validation errors, and enrollment improvements as follow-up work.
Its `ttr-real543-replay-ready-20261029-v1` reports implementation and 95 checks.
Source publication and actual-model consumer qualification remain pending.
No model invocation passes are claimed from disabled-feature tests.

Maximum-mini-NUIAK sends consumer feedback as `nuiak-real543-replay-review-20261030-v1`.
The coordinator stores it at cursor 1785. Storage does not confirm forwarding.
Required intake includes the Git revision, changed paths, schema example, and test report.
Git-publication permission remains a separate pending maintainer question.


## Publication request authorized — 2026-10-29

The maintainer authorizes the scoped source publication request.
Sillycon-TTR chooses its branch, review, and publication process.
Maximum-mini-NUIAK requests a fetchable commit and test evidence through BigDog-Coordinator.
Request: `nuiak-real543-source-publication-authorized-20261029-v1`.
The coordinator stores the request. Forwarding and publication remain unconfirmed.
No Maximum-mini-TTR files or Git state change for this request.


## Native replay report received

Sillycon-TTR reports 3 retained-image replays with 12 saved files passing hash verification.
Two provider outputs are partial because of out-of-frame boxes. All reported crop scoring attempts complete.
No replay accepts a focus target. This does not establish true no-focus labels.
Partial provider output must remain distinct from model execution failure.
Source remains unpublished at this check. Consumer verification remains pending.
Maximum-mini-NUIAK points the coordinator to the existing publication authorization at cursor 1787.
