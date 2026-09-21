# Evidentiary capture protocol

## Before recording

- Identify authorized target, active capture source, owner, app/OS/build and the
  question under test. Distinguish app media, navigation clicks and VoiceOver.
- Record original VoiceOver state using a current settings observation or explicit
  fixture telemetry. Silence and a missing focus border cannot establish Off.
  Announce an authorized toggle and plan verified restoration.
- Use a known media reference as a positive control. Identify a navigation-only
  interval separately from media activation; retain command timestamps and focus
  evidence. Do not claim dispatched arrows necessarily produced audible clicks.
- Prepare the required capture streams before timed stimulus. Don't repeatedly
  rebuild or reconnect an active stream just to start another output file.
- Preflight the writable artifact destination. In the tvOS fixture, use
  `Library/Caches/ReplayKitEvidence`, not an assumed writable Documents directory.
  Export caches promptly; they are purgeable. Create local copy destinations first.

## Timing, consent and focus

Requesting capture is not recording. Wait for the actual start event and operation
ID before stimulus. OS consent may pause start indefinitely: ask the user to handle
the system prompt, and do not send test navigation into that dialog. A user's
“recording” message is not a synchronized start timestamp.

Bound the watcher and stimulus window. If consent or tool latency consumes the
window, preserve the trial as invalid and start a separately identified retry.
Verify no stop/finalization event has occurred before dispatch. Clock comparisons
must account for epoch and units (CLI Foundation dates use seconds since 2001;
Unix dates since 1970), timestamp source, uncertainty and media PTS offsets.

Starting ReplayKit disables Record and may transfer focus to Stop or elsewhere.
VoiceOver changes navigation semantics too. Verify the current focus rather than
reusing a fixed Down/Left/Select sequence from a non-VO run. Capture may end after
20 seconds in the ReplayKit fixture even while the agent is waiting on another
tool. The host audio sampler now allows 30 seconds from its first accepted buffer
(10-second startup / 40-second overall limit); older installed builds may still
use 20 seconds. Check the actual runtime and current status, not this document
alone. Host `remainingSeconds` is conservative whole seconds at status-read time,
not a guarantee that time remains when the next command arrives. For the 15-second
reference reserve dispatch/route latency and a quiet tail; the local qualification
runner requires at least 22 seconds immediately before activation and aborts if
that headroom is unavailable. Do not remove the gate to accommodate a stale build.

## Analyze and classify

Wait for confirmed finalization and analyze the matching operation's immutable
export, never an in-progress file or an older `latest` artifact. Preserve logs,
command times, source identity, media, analysis and hashes in a new trial directory.

Classify separately: consent blocked, start failed, no track, no buffers, invalid
stimulus timing/target, digital-zero samples, nonzero unidentified audio, recognized
reference, and incomplete media. None are interchangeable.

Use decoded sample measurements, not the existence of an AAC track, file size or
TV speaker output. When available compare pre-encoder PCM with decoded output;
zeros before encoding are not fixed by gain, transcoding or jitter buffering.
For tone tests retain windowed detection, duration, peak/RMS and timestamp gaps.
Check audio and video start times and durations separately. Partial tone coverage
is a positive control only for that interval, not full-reference fidelity.

## Current empirical limits, not universal tvOS policy

As of 2026-09-15, office wireless capture recorded media references but produced
digital silence during user-confirmed audible TV navigation/VO tests. A synchronized
ReplayKit trial with VO telemetry true and user-confirmed audible speech/clicks
had a digital-zero navigation prefix in both channels, followed by recognized app
media. This qualifies the omission for that trial, not all routes/apps. Its video
track was shorter than audio; full A/V continuity is not established. One sustained
source delivered 30 seconds without PTS gaps; finite EOF vs player release remains
unresolved. Changing output back to TV Speakers interrupted capture until reconnect;
verify restoration from a fresh image, not only a successful command response.

These observations do not prove all tvOS routes omit VO, nor establish an AWDL,
DRM or clock-watchdog root cause. External reports are hypotheses until supported
by this route's evidence. An accessibility tree, app TTS, or app-generated oracle
does not prove the actual system VoiceOver utterance or accessibility conformance.
Do not substitute a microphone, HDMI hardware, receiver installation or route
change for the user's requested streaming test without explicit scope agreement.

## Cleanup and blocked handoff

Finalize/stop owned recording; verify the original VO setting and release owned
control/capture resources. If awaiting consent, disclose that no test verdict
exists and whether VO is still on. On interruption, preserve operation ID, current
screen/state, original setting and pending cleanup so a later agent can resume
without silently toggling or claiming restoration. If restoration is uncertain,
report the exact state requiring user action rather than repeating blindly.

Use `capture complete` / `capture.task_complete` when this task owns both the
evidence session and the capture-resource lease; session stop alone may leave
preview running. If `resourceContended` or provider state `contended` is returned,
wait the advertised `retryAfterSeconds` — do not collide with another receiver.
`aatv capture acquire --wait` queues until the holder unpublishes. Cooperative
LAN ads use `_tvtr-lease._tcp` (no TCP listener). Idle-warning events expire
on schedule even when no client is connected
(`notDelivered`); a later return sees an expiry receipt and must reacquire.
Hardware proof that another Mac can take `office` is LEASE-07 and is not implied
by local stop confirmation.
