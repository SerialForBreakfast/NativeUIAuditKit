# Human annotation review v1 — local diagnostic contract

2026-09-28, HUMAN-REVIEW-01. Implements the assigned local review plan, not a
training admission lane. No public API, taxonomy, native journey or legacy Photos
contract change. Human-reviewed real screens complement native generator truth;
the historical generate-only guidance in architecture §6.1 does not prohibit
this separately assigned diagnostic lane.

## Immutable inputs and revisions

`human-review-index-v1` explicitly enumerates frames with stable IDs, image and
observation references (project-relative path, SHA256), source/session/generation,
screen grouping, optional status/native evidence references, context notes and
agent/manual proposals. Index has a hash seal. The original finalized TTR timeline
and session-start receipt are required. No directory scan defines membership.
Only the v1 observe-capture inline envelope is admitted by this adapter: exact
decoded base64 bytes must match the PNG, source, size, orientation, freshness,
generation and observation IDs must agree with the session timeline. Raw receipts
remain unchanged, including outputWritten=false. Receipt limit32MiB, image limit
24MiB/40M pixels, index8MiB, maximum256 frames/100 controls per frame; these are
resource bounds for this adapter only. Status snapshots are context, not atomic
native labels. Foundation wall-clock and monotonic timestamps remain distinct.

`human-review-batch-v1` records every row as imported or blocked, copied raw
evidence, numbered full-frame sheets, exact pixel identities, event/observation
links and typed transition gaps. Extra/missing timeline observations reject the
batch rather than silently reducing membership. Uncaptured intermediates are never
reconstructed. Source bytes are rechecked before publication. Interrupted output
has no final sealed batch and cannot be reused. Identical imports validate and
reuse the completed batch without resetting annotations; changed index fails.

Proposals have per-frame control ID, class from the frozen category map, top-left
pixel xywh bounds and focused/unfocused/unknown. They are explicitly proposals,
not truth. Native evidence, if supplied, is retained opaquely: no adapter in this
version attests it, and review stays blocked pending separate reconciliation.

## Editor bridge and completion

Maintainer rejected Docker/CVAT and deferred FiftyOne. Current adapter uses
Labelme5.2.1 JSON, not a service bridge. New CLI: import, validate, finish, crop-qa;
separate `human_review_editor.py` starts the stock version-pinned editor with
project-local Qt settings/config. No model code. See the canonical plan for the
superseded service proposal and the pinned Qt constructor integration.

Labelme rectangles have two top-left-origin pixel corners, stable integer group_id
mapped by sealed batch to control ID, and taxonomy class as label. Per-shape flags
focused/unfocused are proposal states; confirmed/flagged/rejected default false. Neither focus flag means
unknown; both is a conflict. Top-level flags reviewed/settled/content_approved
default false. NUIAK binding in otherData contains exact batch/frame/image identity.
Additional shapes require a new unique positive group ID entered in the UI or
assigned locally by Copy/Finish review; these IDs do not establish native identity. Missing
original controls reject reimport (use rejected flag). All shapes remain accounted
for. Native evidence is retained but unresolved in this version, never auto-approved.
Finish requires reviewer identity/reference/kind and explicit completion; test edits
are software-test only. Tool save/reopen is not human review. No class changes to
the library. Manual box proposals and repeated states remain diagnostic.

Crop batches retain80M total pixels and16-item batching. Unchanged coordinates
round-trip exactly in the tested editor, including fractions. Index `pairs`
explicitly names two frame IDs and a stable control ID; no automatic all-pairs
expansion. Matching class/screen, opposite known states and reviewed controls are
required for a reviewed pair. Duplicate pixels and unresolved native evidence block
acceptance. Same source/layout repetitions remain development-exposed context.

An explicit `finish` command supplies reviewer identity, evidence reference
and `--confirm-batch`; saving in Labelme alone is insufficient. Agent integration
tests use reviewerKind=software-test and can never accept real labels. Human
confirmation is per-control; pending/unknown/flagged/native-unresolved remain
blocked, rejected stays rejected. Frame coverage stays partial/unknown in this
tranche, so no unique-focus accuracy claim. Human mode requires content/settled
confirmation per frame in the review workspace; chat focus confirmations alone
do not confirm bounds. Every frame and control receives a disposition.

Finish review now supplies a batch confirmation UI: list ready frames and blocked
exceptions, require reviewer name and explicit attestation for the listed ready
frames, then set their per-control confirmed and per-frame review/content/settled
flags together. All other labels and coordinates are unchanged. Missing IDs on
newly drawn controls can be allocated without assigning original proposal identity.
The preview is hash-bound and revalidated at application; source JSON backups and
an operation receipt accompany the existing immutable revision. Blocked frames
remain untouched. This does not relax any data admission gate or imply complete
frame coverage. A software-test invocation cannot produce accepted human labels.

`human-review-revision-v1` records parent batch hash, editor snapshot, reviewer
kind/identity/time/reference, completion declaration, frame/control dispositions,
pair candidates (same screen/control, opposite states), and eligibility flags:
trainingEligible=false; independentEvaluationEligible=false; partition=development.
All current training/evaluation paths must reject it. Human-role admission is
Tranche4, not a flag edit. Every output is new/no-overwrite; no source mutation.

## Crop and UI verification boundaries

Crop QA consumes either explicit proposal boxes (labeled proposal-only) or a sealed
revision, invokes `focus_runtime.bounded_batches` and `invoke` with **no model**,
pins runtime identity, checks complete outputs/PNG256×256 and retains hashes and
numbered sheets. Geometry is not reimplemented in Python. Proposal crop success
does not confirm human labels. Stock-editor load/edit/save/close/reopen tests use
an isolated copy and are software evidence only. Human confirmation is separate.
`verify_human_review_editor.py` exercises that installed window and its checkbox
dialog with no model loading. See HUMAN-REVIEW-01 handoff for actual evidence.
