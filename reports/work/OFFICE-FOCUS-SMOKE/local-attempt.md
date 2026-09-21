# Local Office smoke — 2026-09-20

The user corrected execution to the local running TTR app. The Sillycon smoke request
was closed on shared status to prevent a second operator running it.

## Runtime and preflight evidence

- Running local process PID 39983, Debug TVTestRig.app from Xcode DerivedData.
  Its matching app executable supports `--tvtr-stable-cli`; no separate aatv is required.
- Read-only process inventory first failed under the shell sandbox; scoped escalation
  succeeded. This was not evidence TTR was absent.
- `device list/get`: exact office resolved and paired; discovery reported disconnected.
- `session status` and `doctor`: same target selected and control connected, no active/
  queued command; doctor findings empty. Session status is distinct from discovery.
- `fixture env`: office / AppleTV5,3 / 1920×1080 / scale 1, Fixture version 1.0 build 1,
  same authenticated control address. Reported source only; capture binding unverified.
- `observe status`: avfoundation-video idle, camera/audio authorized, not warm.
- Acquired smoke-owned lease at 23:58:00Z:
  client `nuiak-office-smoke-20260920`, lease `36985298-A393-431E-91F9-D9992A289C27`.

## Attempt and cleanup

Recipe copied into this report's recipes/action-dialog.json: two-element high-contrast
action_dialog, seed 7. Destination requested:
`dataset/tvos_captures/office/smoke-20260920T235800Z` under NUIAK.

The initial command used timeout 60000 and was rejected by the parser (exit 64,
invalidArgument, no dispatch). Source help established the supported maximum 30000.
Correcting only that argument reached batch validation, which failed at 23:58:41Z:

- Exit 64; request 856C8573-F9D9-4D9D-82CB-0D59A20CCE56.
- stage: validation; cause: outputOutsideProject; retryable: false.
- No successful batch or capture reported. No automatic retry or alternate output.

Released the exact smoke lease at 23:58:59Z: success, videoOutcome/controlOutcome
released, explicitRelease. No session stop/disconnect or settings change was sent.
Fresh Fixture scene at 23:59:01Z succeeded, isSettled true, nine elements; no harvest
challenge active. No simulator operation, training or model export occurred.

Helper stderr repeatedly reported diagnostic_file_sink_failed / persistenceFailed;
diagnostics remained on stderr. This is separate from the typed batch path failure.

## Resume condition

Reconcile the installed helper's accepted workspace/output boundary with NUIAK's
project-only output rule, or obtain explicit approval for an exact TTR-owned output
location and subsequent copy. Do not guess another path, retarget the running GUI,
restart it, or weaken the boundary. A retry needs separate authorization after this
failure is resolved.

Software/data/integration/model gates are not passed. The runtime connection works;
the observed smoke blocker is output-path validation, not Sillycon availability.
