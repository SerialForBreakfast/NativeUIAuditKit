# Diagnostic Photos CLI contract

`scripts/photos_focus_pilot.py` is offline: it neither invokes TTR nor loads models.
It reads only files already retained in this repository. Use the resident approved
Python environment with Pillow; no installation or download. Set
`PYTHONDONTWRITEBYTECODE=1` and project-local TMPDIR. Build the existing FocusRingTool
offline before review/cropping; import does not require the helper.

## Actual producer interface

The inspected producer source is TTR `CLI/ObservationCLI.swift`,
`CLI/StableCLIContract.swift`, `CLI/StableCLIRunner.swift` and
`Core/AutomationCoordinator.swift`. This is a source-backed adapter, not a claim
that the unknown Office installed build has been qualified.

Retain each successful `observe capture --output <new.png>` JSON response and PNG
from the same invocation. The accepted stable envelope is schemaVersion1,
success=true, command=`observe capture`, `data.observation._0`. The observation
contains id,capturedAt,providerID,sourceDeviceID,dimensions,orientation,mimeType,
freshness,outputWritten, with optional connectionGeneration/receivedAt. Swift
wallClock is retained as its default numeric seconds since2001; do not convert it
to Unix implicitly. Optional missing metadata stays missing. Only up-oriented PNGs
with current freshness and reported age≤1000ms are supported. Other modes/versions
require inspection and an explicit adapter update, not heuristic field guessing.

`session status` returns `data.status._0`, not `data.session._0`. Bind its actual
selectedDeviceID,sessionID and idle connected state. Observation responses lack a
sessionID or native Photos focus: the capture index records operator-declared
session/source context, not atomic source attestation. `sourceBindingReference`
records the operator's target/provider verification; sourceDeviceID may differ
from the control targetID. Do not invent a mapping from an old capture.

## Input index

Place an index beside the source PNG/JSON files. All references are relative to
that index, cannot traverse or use symlinks, and have independently computed SHA-256.
Each PNG≤32MiB; each JSON≤2MiB. At most60 frames/three declared screen states.
Import requires2GB free reserve and a fresh project-local ignored destination.

```json
{
  "version": "photos-focus-capture-index-v1",
  "targetID": "EXACT_DISCOVERED_OFFICE_ID",
  "sourceDeviceID": "EXACT_OBSERVED_SOURCE_ID",
  "sessionID": "EXACT_OWNED_SESSION_ID",
  "operator": "reviewer name",
  "sourceBindingReference": "local session/target verification receipt",
  "sessionEvidence": {"path": "session.json", "sha256": "EXACT_HASH"},
  "frames": [
    {"id": "f01", "screenID": "photos-state-1",
     "image": {"path": "f01.png", "sha256": "EXACT_HASH"},
     "observation": {"path": "f01.json", "sha256": "EXACT_HASH"}}
  ]
}
```

An optional `nativeEvidence` hash reference retains raw producer JSON without
interpreting it as qualified native truth. Genuine provider availability must be
established separately. No label comes from requested remote input or prediction.

```sh
env PYTHONDONTWRITEBYTECODE=1 .venv-yolo/bin/python scripts/photos_focus_pilot.py import \
  --input dataset/tvos_captures/PHOTOS_SESSION/index.json \
  --output dataset/tvos_captures/PHOTOS_SESSION-intake
```

Import creates sealed `intake.json`, original-byte `raw/`, numbered full-frame
`sheets/` and `review-template.json`. Expected frame membership is never silently
reduced: invalid inputs receive blocked dispositions. Hash-valid corrupt images
are retained but blocked; absent/hash-invalid originals remain untouched at source.
All-black captures, repeated observation IDs, generation changes and backwards or
over45minute capture spans block the affected evidence. Declared source metadata
is evidence, not proof of current hardware availability or Photos context.

## Human review and pairs

Copy the template into a new review file using normal repository editing tools.
The agent may propose boxes after viewing the full frame; only explicit human
confirmation sets confirmed=true. Preserve a meaningful conversation/receipt
reference and timezone-bearing review time. No synthetic reviewer confirmations.

For each frame: confirm imageSHA256, reviewer, reviewedAt, reviewReference,
photosConfirmed, settled, contentApproved. Controls contain local stable `id`,
`bounds:[x,y,width,height]` in original-image top-left pixels, and
`state:focused|unfocused|unknown`. Bounds are per-frame, not copied across focus
scaling. Include visible competitors; no complete-candidate accuracy is claimed.
Full frames and overlay sheets retain context. Unknown states never become negatives.

`nativeAssessment` is unavailable when no native evidence exists. When present,
it starts not-reviewed; only explicit human review can mark consistent. Conflict
or unresolved evidence blocks the frame. This does not grant native qualification.

Add at most20 explicit pair requests (empty list is allowed for preliminary review):

```json
{"id":"p01","elementID":"shared-button",
 "focusedFrame":"f01","unfocusedFrame":"f02"}
```

Each pair requires the same reviewed control/screen, different frame pixels and
one known focused control in both frames. All frame-review membership is required;
unconfirmed frames and incomplete pair requests are accounted for as blocked.

```sh
env PYTHONDONTWRITEBYTECODE=1 .venv-yolo/bin/python scripts/photos_focus_pilot.py review \
  --intake dataset/tvos_captures/PHOTOS_SESSION-intake/intake.json \
  --review dataset/tvos_captures/PHOTOS_SESSION-review.json \
  --output dataset/focus_ring/PHOTOS_SESSION-diagnostics
```

Review uses production16%/256 cropping in bounded item/pixel batches. It creates
`diagnostic.json`, retained review bytes, annotated full-frame sheets and paired
crop sheets. Duplicate pairs count once; contradictory crop pixels block involved
pairs. Runtime/helper failures remain explicit. No alternative Pillow cropper,
threshold, model argument, detector inference or device control exists in this CLI.

Exit0 means no blocked entries, **not** that any pairs were collected or training
is permitted. Read counts: an empty pair list remains zero. Exit2 means blocked
entries or a structural failure; retain partial output and inspect evidence. A
failed structural/runtime fence never publishes a completed diagnostic manifest.
Retry only into a new destination. Review corrections produce a new immutable
output and preserve the earlier evidence.

All formats are development-only, trainingEligible=false,
independentEvaluationEligible=false and modelGatePassed=not_assessed. Existing
training, appearance evaluation and native-journey contracts remain unchanged.
