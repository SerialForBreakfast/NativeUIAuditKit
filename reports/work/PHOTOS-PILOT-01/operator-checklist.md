# Office Photos pilot — operator checklist

Live state: pending. Do not execute commands based only on this document.
You drive the remote; the NUIAK worker records/reviews only.60minutes supervision,
45minutes capture maximum; target10 nonduplicate pairs, at most20 attempts and
three already-accessible Photos screen states. No model inference or audio recording.

## Before the first frame

- Identify which Mac actually hosts TTR and its installed app/build. Obtain that
  running app's Automation → Copy Helper Launch Check. Inspect matching help and
  read-only status; never substitute an unrelated build product or launch another
  instance to bypass readiness. No SSH or desktop automation fallback.
- Discover the exact Office Apple TV control ID and its image-source mapping.
  Record matching app/helper identity, target/provider, owned session and permitted
  project-local output root. Do not use remembered IDs in a new command.
- Confirm fresh human availability and exclusive control/capture ownership. An
  absent SMB reservation or stale status is not free hardware. Do not take over an
  existing session. If disconnected, any setup/connection is deliberate and
  operator-mediated; this checklist is not an unattended connect sequence.
- Verify capture ownership through current installed commands. Capture leases are
  separate from controller/session ownership, generally expire after30minutes;
  keep alive only our lease or pause and reacquire according to actual interface.
  The18:03Z pilot diagnosis finds a selection prerequisite: device list/get does
  not select the coordinator target; the inspected producer acquires leases only
  for its selected device. After human exclusivity/occupancy checks, explicitly
  connect Office control, then acquire the owned lease before image capture.
  Stop on connection error, timeout or pairing request. Do not impose a lease-before-
  control-connect loop or treat control connection as capture qualification.
- You open Photos, handle prompts and choose non-sensitive content. Identify the
  first approved screen. No agent Select/Home/Back/directional commands. No account,
  settings, privacy-consent, installation or recording-route changes are incidental.
- Pin session status and record start time. Confirm storage reserve and approved
  image destination. Default screenshots only; do not enable an audio workflow.

## Two-pair smoke, then bounded continuation

1. You settle focus on a visible button and say ready. Capture once with the exact
   installed CLI's `observe capture --output NEW.png --json`, retaining stdout as
   a separate NEW.json. Prefix the discovered exact helper and explicit device ID
   as its help requires; paths are fresh, inside the agreed workspace. No blind
   retry after timeout or ambiguous completion. Never use observe focus for labels.
2. Inspect target, current freshness, timestamp, image bytes and source mapping.
   You confirm this is the intended Photos screen and there is no sensitive content
   in the retained frame. Stop if blank/black, wrong target or unsettled.
3. You move focus away without activating the button. Repeat capture. The original
   control must remain visible; preserve actual focused/unfocused geometry.
4. Repeat for the second pair. Import the retained files, inspect full-frame views,
   propose boxes, obtain your explicit label/bounds confirmation and run crop review.
   Verify exported pixels, metadata and pair sheets before collecting more.
5. Continue only while you are present. Track attempted pairs, accepted/blocked
   counts, elapsed capture time and distinct screen states. Repeated identical
   pairs are duplicates, not additional coverage. Retain full competitors. A
   short focus-switch/no-op sequence may be recorded without forcing pair creation.
6. Stop at the cap, user request, contention, unknown modal/private content,
   missing/black capture or uncertain context. Preserve failures; do not click
   through, reconnect automatically, reset a service or switch to another device.

## Review and cleanup

Record every attempted frame/pair, including incomplete and ambiguous examples.
Use [the CLI contract](cli-contract.md); leave all uncertain confirmations false.
Human-reviewed labels remain visual diagnostics even if native evidence is absent.
No automatic training import and no challenge reservation for these exposed screens.

Finalize/export the owned evidence session with current TTR-supported commands;
verify files/hashes before reporting export complete. Stop/release only resources
owned by this pilot. Session stop does not prove capture release. Retain cleanup
receipt and exact terminal app/context; do not promise restoration or health merely
because a process remains present.

If TTR is on another host, its operator retains approved project-local originals.
Transfer only named approved files via the verified SMB receipt protocol. Every
file over10,000,000bytes needs explicit size approval; prior four-archive approvals
do not apply. No private images enter shared status metadata. Do not recapture
successful frames merely because export/transfer is blocked.

Resume requires: exact host/build/target identified, exclusive readiness verified,
maintainer available to drive Photos, approved outputs, and no uncertain prior
capture cleanup. If unavailable, report pending live pilot, not completed capture.
