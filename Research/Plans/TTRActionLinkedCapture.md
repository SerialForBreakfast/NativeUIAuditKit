# P0 — Human demonstration recorder, not chat-paced screenshots

2026-09-28. Consumer owner: current NUIAK TTR worker. Producer implementation owner
must be assigned by TTR. Follow-up to request
`nuiak-20260927T182937Z-supervised-external-control`; not a competing transport design.

## User outcome

**Start once → navigate normally with TTR controls → stop once → review a batch.**
No chat acknowledgment, manual capture, or terminal command per remote input.
Local Max is the primary proven still-capture path. Remote pairing may use the
same recorder later; it must not block local recording or create a second format.

The maintainer rejected the observed interaction loop as unacceptable. NUIAK
mistakenly continued checkpoint capture after input logging worked; successful
button receipts did not imply automatic screenshots. Preserve the useful data,
but do not call the demonstrated workflow complete.

## Reproduction / evidence

[FOCUS-HUMAN-OFFICE-01](../../reports/work/FOCUS-HUMAN-OFFICE-01/session.md): same
Office target/session,8 retained1920×1080 images,9 completed human TTR commands.
Session timeline sequences15–17 are Right,Up,Select; no observations between them.
Sequence18 contains the final General-focused Settings screenshot. Earlier single
presses correlate with after-frame command IDs only because the agent explicitly
captured after chat replies. Inter-command images cannot be reconstructed.

The inspected installed help exposes session timeline and explicit capture/poll/
wait-stable primitives, but no verified action-triggered recording command.
The source checkout also has command/observation event persistence; matching source
identity is unverified. This is a demonstrated workflow gap, not proof no internal
recording hook exists. TTR should first map its current implementation to this contract.

## Required first tranche

1. **One bounded recording session.** Human explicitly starts/stops collection in
   TTR (or approves the equivalent client start). Show exact target, recording state,
   retained-frame/event counts, storage/time bounds and failures. No automatic audio.
   Bind existing ownership, consent, session and connection-generation checks.
2. **Record at the shared input dispatcher.** The human GUI and future agent controls
   use the same event/image recording mechanism. Keep action, press/hold/swipe details
   when supported, timestamps, dispatch/result/failure/uncertain outcome and IDs.
   Start with actual supported directional/select/back/home semantics; declare gaps.
3. **Retain pixels around the action without waiting on chat.** A warm buffer or
   equivalent supplies a fresh before-frame; retain intermediate/after evidence and
   a bounded settled-after result. Keep original bytes, image IDs/hashes, target and
   generation binding, monotonic timing and clock basis. Reuse only genuinely fresh
   previous after-frames. A polling-only client cannot guarantee every intermediate
   focus state and must not claim to satisfy this contract.
4. **Be honest about rapid input and settling.** Never invent a settled state between
   inputs that arrived before settling. Preserve every input and available sequence;
   label overlap, missing before/after, timeout, stale/black/missing pixels and gaps.
   If an optional collection mode gates/queues human inputs, show and obtain consent
   for that behavior; never silently drop, replay, coalesce or delay them. Pixel
   stability and command completion are not proof of focus stability or delivery.
5. **Keep no-ops and errors.** A completed input with unchanged focus remains useful
   sequence evidence. Deduplicate storage if desired without deleting event mappings.
   No claim of unique training diversity based merely on PNG-byte differences.
6. **Asynchronous OCR evidence.** Where available, attach actual text/confidence/
   bounds, engine identity and source image ID/hash; unavailable is explicit. OCR
   must not block durable raw capture or become a native focus label. No requirement
   to enable NUIAK inference or wait for better focus models to record sequences.
7. **One verified consumer handoff.** Versioned original images plus full event/frame
   index, session/source provenance, completeness/gap report and file hashes. Support
   resumable/idempotent receipt without recapture. NUIAK adapts the producer's exact
   schema to existing review/import tooling; no speculative alternate schema/server.
8. **Owned cleanup.** Stop recording, finalize manifests, release only owned capture
   resources and report outcomes. Keep an already-user-owned control connection
   where supported; do not silently disconnect it. Revoke/expiry/target change,
   contention, disk-full and interrupted finalization must preserve partial evidence
   and stop or mark gaps, not lose input records silently.

## Acceptance before asking for another collection

First offline tests of actual dispatcher/recorder integration, then a separately
authorized short live run on the current signed local build. Proposed acceptance
target: a roughly5-minute,20-input demonstration with **zero per-input chat turns**
and one Start/Stop cycle. These are workflow trial targets, not model thresholds.

- For every input, an event with exact identity/outcome and mapped before/after
  evidence, or a typed explained gap; no silent omission.
- Include single moves, a return, a safe boundary/no-op, rapid directional input,
  and an app transition. Exercise failures/expiry/storage interruption offline
  where appropriate; don't deliberately disrupt hardware without authorization.
- Validate original file/hash receipts, ordering, timestamps, target/generation,
  overlap/settle classification and final resource cleanup. Report observed latency
  and counts, not theoretical guarantees or command duration as settle latency.
- Review numbered filmstrip/contact sheet after the run; confirm/correct focus and
  control bounds in batches. No model-derived training labels quietly accepted.
- Qualification fails for silent missing images, per-button user relay, or nominal
  completion without evidence delivery/cleanup. Explicit gaps remain partial data,
  not an excuse to claim a complete trajectory.

## Ownership and resume condition

TTR: map existing capabilities, implement/qualify shared-dispatch recording and
publish exact interface/schema plus representative bundle. NUIAK: retain this
session, provide consumer requirements and integrate the exact bundle with existing
review tooling once available. User: approve sensitive screens and review labels,
not coordinate each press. No producer edits, build/restart/install or broad new
capture are performed from this NUIAK assignment. Separate producer-repository
assignment is required to implement the missing hook there.

Resume broad human collection only after a representative local recording/receipt
pass demonstrates the above low-friction loop. Capture must not wait for new model
training, native Photos telemetry, remote transport or independent-model qualification.
