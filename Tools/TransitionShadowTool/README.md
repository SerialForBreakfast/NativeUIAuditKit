# Experimental focus-transition change observer — pinned candidates

This portable Swift6/macOS15+ consumer estimates **did focused control identity change?** from
ordered before/after screenshots. It does **not** locate either element, provide
navigation policy, detect VoiceOver alignment, or authorize actions. CPU-only,
FP32 Core ML. The software allowlist supports exact DTM025 and DTM030 checkpoint
pairs. DTM030 is exported as a separate experimental delivery; compatibility
evidence is pinned in that delivery's parity-summary.json, not inferred from this allowlist.
Use only a separately verified delivery manifest. Scored replies report the loaded
model ID. Off/encode replies retain the legacy DTM025 identifier as a compatibility
placeholder with modelLoaded=false and compiledTreeSHA256=not_loaded; never count
those as artifact loads.
Keep FDR021 single-frame focus scoring separate. Neither replaces a shipped model.

Semantic clarification (SHADOW-CONTRACT110): the trained target compares observed
or reviewed focused control identities, not highlight-box displacement. A stationary
highlight with scrolling may still be a focus change; animation with the same focus
is not. This model receives pixels only, so identity inference may be ambiguous or
fail, and stationary-highlight scrolling is not qualified. Preserve separate identity,
geometry and content observations. Native AX hints alone are not reviewed visual
ground truth. This clarification does not alter weights, thresholds or the immutable
original delivery archive; peer-reported discrepancies require case-bound review.

## Build and smoke without private screenshots

Verify the archive SHA256 and every file against `manifest.json` before use. The
archive contains no binaries, checkpoints, private captures or Python dependency.
Build the included Swift package locally (no dependencies, downloads or TTR rebuild
required). Use project-local Swift build/cache paths according to your repo policy.
The consumer also uses standard Apple-managed Core ML caches; sandboxed TTR must
load it from its approved resource/workspace access, not bypass its sandbox.

```
swift build -c release --product TransitionShadowTool
```

`sample-request.template.json` contains only synthetic image references. Replace
`$ROOT` with the absolute extraction directory in its root and two image paths,
save a new request, and choose a nonexistent output path. `$ROOT` is a placeholder,
not shell interpolation performed by the tool. The expected synthetic score/tensor
hash/decision are in `synthetic-expected.json`.

```
.build/release/TransitionShadowTool \
  --bundle /absolute/extraction/Model \
  --manifest-sha256 <SHA256-of-Model/contract.json> \
  --request /absolute/extraction/request.json \
  --output /absolute/extraction/new-reply.json
```

Use the manifest's pinned contract hash; do not trust a newly calculated hash of
an unverified delivery. The included compiled model is qualified on this delivery's
Apple Silicon/macOS runtime only. The `.mlpackage` is supplied for other deployment
targets; recompilation changes the tree/contract hashes and needs a new manifest
and parity receipt, not disabling integrity checks. Intel/iOS/tvOS host inference
and GPU/ANE are not qualified by this delivery.

## Request and result contract

The request has exactly `schemaVersion:1`, `mode`, absolute `root`, and `pairs`.
Each pair has `id`, `actionID`, `beforeObservationID`, `afterObservationID`, `before`
and `after`; frames have only absolute `path` and SHA256 `sha256`. IDs are nonempty,
at most512UTF8bytes; pair IDs are unique; batch size1–128. No labels, boxes,
requested-focus identity or telemetry enter the model. Duplicate/unknown JSON keys
are rejected. Frame files must remain inside the explicit nonsymlink root.

- `off`: loads neither model nor frames; returns skipped records, no prediction.
- `encode`: validates and encodes frames only; useful for preprocessing diagnosis.
- `score`: loads the hash-verified model once; encodes/scores pairs serially.
- Exit0: requested operation completed. Exit1: one or more pair failures, retained
  individually alongside successes. Exit2: request/model/output failure. Never
  interpret failure, dropped work, or timeout as an unchanged prediction.
- Replies retain pair/action/observation IDs, source hashes, exact encoded-tensor
  hash, actual loaded model tree/backend, load time, per-pair preprocessing and
  inference time. Scores are finite sigmoid outputs, **not calibrated confidence**.
  `>=0.85` changed; `<=0.15` unchanged; otherwise uncertain. No threshold tuning.

Input is opaque8bit RGB/RGBA PNG, orientation1, at most32MiB and20million pixels per
frame; before/after dimensions must match. Grayscale/palette/transparency/rotated
images fail explicitly. Full frames resize to a192×128 black letterbox with pinned
Pillow-compatible antialiased bilinear rounding, then planar beforeRGB/afterRGB
float32 /255. The model computes the absolute difference internally. **Do not use
FocusRing's16%/256crop pipeline for this model.** Swift encoded bytes matched all
the delivery's pinned parity pairs; a different resize/color pipeline requires new parity.

## TTR integration: feedback only

TTR owns the hook and source integration. `Observer.swift` can be compiled directly
into its implementation module; it has no speculative public API. Keep the actor
and image encoding off the UI/navigation-critical path. The batch CLI is also a
complete reference consumer. Use bounded background work (existing shadow request:
queue8, drop-and-report overflow, no navigation waits). Reuse a loaded actor, call
`verifyUnchanged` at session completion, and preserve typed failures. Hash checking
is integrity evidence, not an atomic guarantee against concurrent filesystem edits.

For repeated/adjacent frames, own a `TransitionEncoder` within the bounded worker
or request. It retains at most8encoded frames (2359296tensor payload bytes), not
full-resolution images. Every access still checks current path, size and bytes/hash;
hits reuse only decoding/resizing. Drop this state when the session/request ends.
The CLI owns one encoder per request; `off` never calls it. No shared/global cache
or hidden persistent screenshot store is introduced. The stateless
`TransitionPixels.pair` remains available as a parity reference.

Record the actual action interval and observed frames; never request extra device
actions merely to fill the shadow queue. Review labels separately as changed,
unchanged, or uncertain with annotator/version provenance. Retain content-only
changes, no-ops, scrolling, delayed transitions, missed elements and abstentions.
Preserve journey/recipe ancestry; newly collected feedback is not automatically
training-admitted or independently held out. Privacy approval precedes capture
egress. Run no automatic personalization, training, model replacement or navigation
decision from this package.

## Evidence and limitations

`parity-summary.json` identifies each delivery's exact native compatibility scope.
DTM025 used113retained transitions,122same-frame negatives and5synthetic pairs.
DTM030 uses207retained transitions,226same-frame negatives and5synthetic pairs.
DTM030 fits all433admitted training cases confidently, including previously exposed
Settings examples explicitly admitted to training. This is **not** independent
accuracy. All their related ancestry must stay out of final evaluation. No
production gate passed; localization and navigation decisions remain excluded.

Return a receipt with request ID, archive byte count/SHA256, copied location,
contract/model hashes and intake result. Then separately return local source/build
identity and on/off evidence: loaded artifact/backend, scored/failed/dropped counts,
latency, uncertain results and unchanged navigation behavior. Artifact receipt is
not proof of a live hook. NUIAK retains its original and owns cleanup of the exact
shared archive only after a matching receipt; do not delete peer files.
