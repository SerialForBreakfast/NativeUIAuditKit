# Local replacement capture

**Latest result:** all 4 local pairs complete and pass intake. Earlier failures remain below for diagnosis.

## Completed local capture

NUIAK builds the signed TTR candidate from `0be978b3` in the updated Developer checkout.
The build takes 63.24 s. Its signature and packaged-runner checks pass.
Candidate digest: `ae88f6f6c13705df25c7f7d616e6c573d155d22d1c48b3ae7a4fea4b6887a49e`.
The matching Fixture build passes and runs on the approved Simulator.
Normal Apple tools maintain their runtime storage. Explicit build outputs stay in the TTR checkout.

The supported MCP `fixture.job_prepare` imports the unchanged recipes with explicit calibration membership.
CLI standard-input staging fails; MCP byte import succeeds without changing permissions or recipes.
The earlier size diagnosis applies only to the old checkout, not the updated candidate.

| Case | Local job | Result |
| --- | --- | --- |
| custom-dark | 06CE19F2-8D24-4026-9C5A-F452B92DD4EF | 1 accepted pair |
| custom-light | 97D4F0B8-F3D8-4471-8DFF-7295F0C5A9A9 | 1 accepted pair |
| apple-first | 1209CA32-9AD5-47AB-9362-1E4CACADFF07 | 1 accepted pair |
| apple-middle | B376050E-B7A8-42D7-8792-7CB7546AA50D | 1 accepted pair |

The jobs run sequentially. Each has a 10 min host limit. No capture retry occurs.
The supported Ruby exporter verifies each copied file and preserves the producer originals.
NUIAK independently checks all 48 exported files and every indexed artifact.
All 8 PNG files decode at 3840 × 2160.
All 4 pairs pass the existing strict schema 4 checker.
All 8 crops use production `makeCrop`, with 16% expansion and 256 × 256 output.
Intake report SHA-256: `585b62e389c7cc9216565b81ac827fbb093fe0a057f203d1d8a4115376ca5925`.

Visual review covers all 8 original images with measured body boxes.
The dark custom card grows when focused. The light custom card grows with visible clipping.
Both Apple-style targets grow and brighten when focused. Their captions remain outside the measured image bodies.
Repeated artwork and busy backgrounds remain deliberate features of these recipes.
These 4 cases do not establish broad style coverage.

Fixture responds after capture. TTR reports `can_run: true` and clear ownership records.
The task leaves the healthy local app and Fixture running. It does not operate Office.
Raw outputs remain ignored under `artifacts/exports`; crops and review sheets remain under `artifacts`.

Software: signed build checks pass; no source changes or unit-suite claim.
Data: accepted for calibration and development review only.
Integration: local capture, export, intake, and crop checks pass for these 4 recipes.
Models: no inference, training, or promotion in this capture tranche.
Next: compare focus results on these cases within their existing calibration role.

The maintainer requests local capture instead of another remote capture request.
The scope contains custom-dark, custom-light, apple-first, and apple-middle.
Keep their calibration role and related groups outside final evaluation.

## Local checks

- The installed TTR app and its bundled helper are available in DerivedData.
- TTR starts successfully. Its helper connects to the app.
- Simulator 9026ECA9-77DB-4AE6-8FE6-BB239E9571FA starts with tvOS 26.5.
- The installed Fixture starts with process ID 32984.
- Xcode reports version 27.0, build 27A266a.
- The sandbox rejects Simulator access. The same inventory check passes outside the sandbox.
- TTR reports ready storage, companion, runner, and Simulator services.

## Capture blocker

TTR retains cleanup record 63CC9F0D-E2D1-4262-85E0-5E407CD34804 for this Simulator.
The supported `simulator reconcile` command returns `can_run: false`.
The record remains after that command. No capture starts.
TTR reports no active command, observation, or queued command.
These facts do not establish that every earlier Simulator resource is released.

Evidence: `artifacts/reconcile.json`, `artifacts/reconcile.log`, and `artifacts/status.json`.
The app and Fixture remain running. No service reset or manual record deletion occurs.
No remote capture request occurs.

## Next action

Resolve the retained cleanup through the supported local recovery path.
A Simulator restart requires explicit approval under repository rules.
After readiness passes, verify Fixture identity and capture the 4 cases locally.
Then export, check hashes and labels, and review the resulting crops.

Software changes: none. New data: none. Local capture: blocked. Model qualification: not assessed.

## Approved restart result

The maintainer approves the exact-target restart.
TTR completes the restart and returns `can_run: true`.
Evidence: `artifacts/restart.json` and `artifacts/restart.log`.
Fixture restarts as process 33498 on the selected Simulator.
That process owns port 8080. Its environment request passes.

Recipe staging then fails before capture.
The helper cannot read the repository path directly.
Passing the same bytes through standard input reaches TTR, which returns `invalidArgument`.
The installed help supports this staging operation, but does not advertise `--split`.
Removing that option does not change the rejection.

The local checkout is at `46dce7b`.
Its `FixtureJobWorkspace` accepts at most 262,144 recipe bytes.
The retained recipes contain 3,904,550 to 7,474,130 bytes.
All use composition version 5 and embedded artwork.
This source limit explains why these recipes cannot use the documented local staging path.
The running binary's exact recipe limit remains unverified.
Do not remove artwork or change recipes and claim equivalent replacement captures.

Next: update local TTR source and matching app/Fixture to the producer revision that supports these recipes.
The maintainer performs Git updates. NUIAK then builds and captures locally.
Do not request replacement images from the remote worker.
The local app and Fixture remain running. No images, training, or model changes occur.

## Check after the reported update

The local TTR process remains PID 32776 at the same DerivedData path.
Its executable has modification time 2026-10-05 16:22:46.
The local checkout still reports commit `46dce7b` and contains uncommitted changes.
Its recipe limit remains 262,144 bytes.
The Fixture process remains PID 33498 at the same installed path.
The fresh status request succeeds. Evidence: `artifacts/status-after-update.json`.

The reported update is not visible in this running app or the checked source limit.
Do not repeat the rejected capture or overwrite the dirty checkout.
The remaining input is the location of the updated local app or source checkout.

## Correction: wrong checkout

The updated checkout is `/Users/josephmccraw/Developer/TVTestRig`.
Its Git record shows a successful pull to `0be978b3` on October 6 at 16:59:20 local time.
The earlier checks used the old Documents checkout and its old build.
The maintainer completed the update. No additional Git update is needed.
Use the Developer checkout and its matching build for the remaining capture work.
Do not apply the old checkout's recipe limit to this revision.
