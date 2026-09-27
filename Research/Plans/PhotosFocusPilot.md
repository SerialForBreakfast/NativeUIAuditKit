# PHOTOS-PILOT-01 — supervised Office diagnostic pilot

Assigned2026-09-27 to the current NUIAK worker. Implement preparation, offline
import/review/crop integration and verification; conduct the live pilot only with
the maintainer present to drive Photos. No agent navigation, model inference,
training, export/promotion, producer edits or qualification-policy changes.

## Design before implementation

Use a separate versioned diagnostic CLI with `import` and `review` stages. Import
the actual TTR stable CLI observation envelope plus PNG, retaining exact bytes,
source-device identity, timestamps, provider and optional generation. A capture
index binds expected device/source/session, session-status evidence, screen IDs
and file hashes. TTR observation envelopes do not carry session IDs: preserve the
operator/session-context binding as declared, not atomic/native evidence.

Render numbered full frames and an editable review template. Human review binds
each frame hash, Photos context, settled/private-content approval, per-control
top-left pixel boxes and focused/unfocused/unknown state, reviewer/time/reference.
Explicit pair requests join the same control across the same screen; related
frames remain one development source. Optional native evidence is preserved raw;
it is not auto-admitted. Human review must resolve any native disagreement or leave
the example blocked. Missing/unconfirmed/unknown evidence fails closed.

Generate accepted diagnostic crops exclusively through `focus_runtime` and the
production16%/256 cropper with bounded batches; never import a model. Full frames
retain competitors. Account for every frame/pair, duplicates and contradictory
identical crops. Human-reviewed evidence never masquerades as native telemetry.
The new format remains rejected by existing training/appearance-evaluation/native
admission; no edits to those schemas or public Swift/taxonomy APIs.

All configurable output is fresh project-local gitignored storage. Preserve
originals and partial failures; no overwrite, symlink/path escape or silent partial
success. Tests use generated fixtures inside `.build`, including real CLI/crop
integration and existing admission rejection. Required offline Swift checks apply.

## Live boundary and completion

Verify exact installed app/helper and Office target, ownership, available capture
and output storage before operating. Existing source is not installed-runtime
qualification. No automatic app launch/connect/restart or alternate host transport.
You open Photos and control all inputs; no automatic audio. First two pairs must
survive export/review before continuing. Target10 usable nonduplicate pairs;
maximum20 attempted pairs, three accessible screen states,45minutes capture within
a60minute supervised session. Stop on contention, wrong target, black/missing
capture, private/unexpected context or uncertain cleanup. Release only owned resources.

Live absence blocks live evidence, not local implementation. Report software,
data, integration and model outcomes separately. No inference is part of this
pilot; all screens are development-exposed, not future pristine challenge members.
Source independence review remains a separate assignment. New cross-host artifacts
use the existing exact-file size/receipt policy; prior transfer approval is not reused.

Deliver capability matrix, operator checklist, CLI contract, tests, raw/review/crop
evidence when available, complete dispositions and one next recommendation. If
native Photos telemetry is unavailable, recommend separately scoped human-label
admission or a native feasibility assignment rather than silently weakening gates.
