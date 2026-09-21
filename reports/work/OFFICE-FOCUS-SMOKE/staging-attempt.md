# Approved staging attempt — 2026-09-21

Outcome: blocked before lease acquisition, recipe mutation or capture.

The user approved the exact container staging exception and one bounded local
retry. At 00:26 UTC the matching running app (PID 39983) reported Office connected,
no active/queued commands and no capture lease. Fixture env responded for Office
at the verified control address. The proposed staging directory and root recovery
marker were absent. Source metadata remains reported, not authenticated identity.

Creating `Data/.tvtr/nuiak-office-smoke-20260921/recipes` under the TVTestRig
container failed through apply_patch (parent creation). A scoped escalated mkdir
then remained sleeping for over 80 seconds without output or creating the directory.
Its PID was 46682, parent shell 46681. A macOS privacy/access prompt is a possible
explanation, not a confirmed diagnosis; no explicit denial was returned.

Both owned processes were canceled with TERM (shell exit 143). At 00:28:21 UTC
neither remained; the directory was still absent. Capture status succeeded and
showed unchanged acquireCount=1/explicitReleaseCount=1 from the earlier attempt,
with no current lease. The recipe copy and acquire command were never reached.
No fixture batch was launched, no bundle exists, and the user's control connection
was not stopped. No files were deleted or permissions changed.

The user is remote and cannot address a local permission prompt. Do not leave a
pending command, enable remote execution, inject writes through a debugger, or
broaden privacy permissions as a workaround. Resume when scoped container access
can be established by the maintainer, or TTR provides an approved accessible
workspace/export path. Refresh device readiness and user operation authority then.

Software, data eligibility, integration qualification and model gates: not assessed
by this attempt. The original outputOutsideProject RCA remains valid; the staging
workaround is not operationally qualified. Simulators remain paused; no training.
