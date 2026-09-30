# FOCUS-GEOMETRY-ADAPTER-01 — diagnostic geometry consumer

Assigned by “Ok do the next tranche”; current NUIAK worker. Implementation complete
for review; [handoff](../../reports/work/FOCUS-GEOMETRY-ADAPTER-01/handoff.md).
No inference, training, capture, export, promotion or admission.

The existing TTR intake continues to emit unchanged v1.5 wrapper manifests. A new
offline CLI consumes a hash-pinned, validated v1.5 manifest and explicitly selects
`measured_control_wrapper` or `artwork_layout_view_bounds`. It emits only
`focus-geometry-diagnostic-v1`, not a training/evaluation dataset manifest.
Native focus labels and all original geometry remain untouched. Missing layout
geometry is recorded per frame as blocked, never replaced with wrapper estimates.

Validate the optional geometry in all four native bracket endpoints, including
their existing equality/element/frame binding. Producer source archive SHA256
`a8d7d219fc91f428901c4c80b840dc028bdffa05d11f5efc5b49b043c9576059`,
FixtureAppearance.swift `FixtureArtworkGeometry.isValid`: version1, nominal layout
source, explicit native-effect-unavailable status, finite in-image pixel xywh and
normalized xyxy agreeing within **1 pixel**. Explicit unavailable reasons are
not_rendered/clipped/projection_failed with neither rectangle. Null optional
values follow Swift decodeIfPresent semantics. Unknown geometry fields are rejected
by this closed diagnostic consumer rather than silently interpreted.

Crop identity binds role, exact source manifest hash, pair/element/state, frame
hash, selected and original bounds, production runtime and preprocessing. Use the
existing bounded production makeCrop path (16%,256square), never a custom cropper.
Revalidate source and runtime after rendering; verify output hashes on replay.
Reject held-out/test/final-challenge sources before any diagnostic crop work.

Acceptance: actual CLI with source-shaped offline fixture; valid/unavailable/absent
geometry; malformed versions, coordinates, contradictions and bracket changes;
changed inputs/output hashes; no fallback; legacy crop parity; ordinary dataset
admission rejection; retained source preservation; offline Swift build/test and
legacy intake tests. Real retained input demonstrates wrapper parity/unavailability
only. A new measured producer sample remains necessary for live qualification.
