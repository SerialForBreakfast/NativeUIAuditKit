# Selected native geometry review — 2026-10-06

Read-only review of all20selected sidecars in the verified regular-subset archive.
No schema downgrade, source execution, capture, crop export or training occurred.
This extends the [transfer handoff](subset-handoff.md), not training admission.

## Independently checked

- All40endpoints report verified `uikit_focus_system` observations with the expected
  target/competitor identity. Before/after recipe, elements, focus observation and
  semantic inventory agree; endpoint aliases agree with after-capture scenes.
- Capture clocks are ordered within each bracket and across the pair; focused
  generation is greater than baseline generation. These remain correlation checks,
  not proof of atomic callback/frame identity.
- All40target rendered-body rectangles are finite, positive, in image bounds;
  normalized XYXY matches visible XYWH within1e-6. Visible bounds lie within full
  bounds (1e-5pixel tolerance) and body generation matches focus generation.
- **38/40** target visible-body rectangles differ from nominal control rectangles.
  Reusing nominal boxes would change the crop input for nearly every endpoint.
- **18/20focused endpoints are clipped**; all20baseline targets are unclipped.
  Only `streaming-catalog-dark` and `streaming-catalog-light` have two unclipped
  endpoints. This is a triage result, not admission of those two pairs.
- **28/40frames** contain `tabs-0` without measured rendered-body availability.
  Do not claim complete full-screen annotations or label the visible tab absent.

Example: streaming-detail-growth-r2 nominal baseline is533.33×355.56pixels;
measured body is533.33×206.22. Focused full body is616×238.19, clipped visible
body606.90×234.67. Nominal, rendered, visible and artwork geometry must remain separate.

## Decision and next implementation boundary

Keep all20pairs in their existing review/calibration roles. The18clipped cases are
valuable challenges, not silently clean growth examples. Missing other-element bodies
must not prevent an explicitly scoped target-only report, but must prevent a whole-screen
completeness claim. Neither two unclipped cases nor passing telemetry establishes
pixel-level semantic correctness or independent evaluation ancestry.

Local producer HEAD remains46dce7b; `git cat-file -t 550a2d37` fails (object absent).
The supplied source-review patch names base3e9e05d and uncommitted changes. Do not
pretend that this is a qualified source implementation of schema4. Consumer work can
implement strict structural parsing offline, but full semantic support still needs
the exact published source and source-shaped positive/negative vectors. No new archive
or recapture is requested. Preserve schema2/3 acceptance behavior and never relabel
schema4 as3 merely to pass the existing validator.

Verification: two read-only Python audits over all selected metadata, exit0; existing
raw metadata and archive are retained. No repository code changed, so no new Swift
build is claimed. Software implementation remains pending; data admission blocked;
integration qualified only for transfer/structural review; model gates not assessed.

Feedback published and read back at
`nuiak/responses/nuiak-20261006-art191-geometry-review.json`, SHA256
`507b86e15e2602fff3c015a54d621b4340acfa655b3c725cc47219f6a4a2cb18`.
Peer acknowledgment remains pending. Initial publication setup lacked the transfer
requestID field and failed before any write; corrected identity then published once.
