# Office trial02 — annotation open; producer export defect independent

## Human review completion — 2026-09-28 22:51Z

Operator completed Finish review. Verified snapshot-bound revision at
`review-batch/review-revisions/20260928T225131Z-056fc495/revision/revision.json`:
human-review-revision-v2,8 reviewed frames,82 reviewed controls, including tabItem
roles. Separate completeness receipt validates all8 frame IDs. No blocked controls
in this revision. Diagnostic-only, trainingEligible=false. No model inference or
training; production crop QA and audit remain next. This supersedes earlier
pending-review statements below without changing historical capture/export evidence.

User explicitly approved TTR's app-managed recording folder and continuing the
human-operated capture. Fresh coordinator confirmed connected/selected Office.
No agent navigation or audio recording. TTR acquire/start owns its recorder lease.

Session:2D659D7E-4F11-4A0D-B848-05CBAF2570F0.
Source bundle:
`/Users/josephmccraw/Library/Containers/com.showblender.TVTestRig/Data/.tvtr/.local-work/recordings/c882b454-250c-4412-b070-0caf806b168d`.
Evidence:start.jsonl and stderr; prepare/start/status all succeeded. Initial status
isRecording=true with zero frames immediately after start; later receipt required
before claiming useful image capture. User operates TTR controls only.
Follow-up ready-status.json at39 seconds confirms44 received frames,0 actions,
1 gap, recording true. Gap classification/semantic quality awaits completed bundle.
Operator invited to make10–20 safe TTR focus moves over about a minute, then say
done for Stop/export. This is not an automatic timer or background agent monitor.

Next: a short safe directional walkthrough, then Stop, verify own session cleanup,
export this completed bundle to a fresh project-local directory, inspect schema2
frame/action accounting and prepare review. Do not stop another recording if the
session changed. No model or training admission. No automatic deletion of source.

## Non-blocking feature request — consumer delivery profile

User requested a better workflow while continuing current capture. Reuse existing
prepare/start/stop/export, rather than build another recorder or label application.
Add a generic named consumer destination profile (NUIAK as first consumer):

1. Human selects/approves destination once; retain a scoped bookmark/grant. Display
   exact target, app-owned source and consumer destination in one readiness view.
2. Start normally in TTR-owned storage. On Stop, optionally export to a unique
   versioned consumer inbox. Never overwrite, silently relocate or recapture.
3. Produce a receipt with session/target/schema, image/action/gap counts, sizes and
   hashes, cleanup state, exact destination and delivery status; notify the consumer
   through its approved MCP connection. Labels/intake acceptance remain separate.
4. If delivery fails, preserve source, show actionable retry-export, and resume only
   the transfer. Do not repeat device inputs/capture or delete originals automatically.
5. Provide one bounded trial preset with a visible duration/data cap and safe Stop;
   expiry/contended ownership must be explicit. No per-press human confirmations.

This is a future convenience/robustness request, not a new gate for the approved
trial. Local app-managed recording plus explicit export remains the current route.

## Completed capture and workload boundary

User finished and expressed concern about duplicates/review burden. Verified own
session then stopped it once. Final counts:166 actions,1082 frame observations,
193 gaps,552.23 seconds. Recorder false, activeOCRCount0, cleanupStatus
owned_provider_released. Fresh coordinator confirms Office remains connected.
These counts do not establish complete action/frame coverage or settled labels.

Source approximately945MiB; local free space37GiB before attempted export. Exact
source-to-fresh-project export failed immediately with serviceUnavailable; no output
directory created. Later coordinator status succeeds. Export is local in the
inspected runner, so generic 'open TTR' message does not establish app absence or
the actual underlying filesystem/decoding failure. No blind retry or manual-copy
substitution. Preserve source; producer must diagnose exact failing export operation.
Evidence:stop.json, post-stop.json, export-receipt.json, export.stderr, postflight.json.

Read-only source audit verifies inventory byte hashes and decoded pixels; results
in bundle-audit.json. No screenshots sent externally. No originals deleted. App
storage remains approved only for the scoped capture/delivery workflow.
Audit complete:1009 inventory images/983113949 bytes, all size/SHA256 checks pass;
1009 distinct decoded pixels across1082 observations (73 exact repeats). Roles:
24 postInputSettled,972 postInputUnverified,86 transition. Gap reasons:150 inputOverlap,
36 advisorySkipped,7 settlementUnavailable. Settled is a producer observation, not
human ground truth or guaranteed eligibility. No inference performed.

**Annotation budget:** first batch capped at8 varied settled candidates, not1082
frames or166 actions. Exact-pixel repeats need only one annotation with explicit
identity mapping; retain every event/time reference. Similar-but-not-identical
screens require selection checks, not automatic label reuse: focus scaling,
animations and artwork can change geometry. Keep uncertain/gap-adjacent frames out
of automatic settled admission. Prefer layout diversity and matched focus switches,
reuse compatible rectangles as unconfirmed proposals, and stop after the first
batch to assess effort. Remaining frames stay archived, not a human assignment.
On the user's explicit request, direct local diagnostic subset intake was prepared
and opened without waiting for producer export repair. The sealed batch is
`review-batch/batch.json`, version `human-recording-review-batch-v1`.
Sequences:303,319,416,456,488,656,676,687 (five Settings, three App Store).
Original PNGs and complete source metadata were copied into fresh project-local
storage, with SHA/pixel checks and unchanged recording-event bindings. No native
focus labels or human confirmations were invented. All eight editor documents
start with no boxes and unchecked review flags. Human review and subsequent crop
QA remain pending. The rest of the recording is not an annotation assignment.

The local rectangle editor was launched against this batch. Existing copy/paste,
navigation shortcuts and Finish review are retained. Direct intake does not claim
that TTR's failed export is repaired, nor that these images are training eligible.
