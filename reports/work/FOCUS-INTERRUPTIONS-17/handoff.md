# Interruption corpus: verified diagnostic evidence, not new training

October 1, 2026 PDT. Completed the retained-r2 intake and crop-QA tranche using the
fixture-training and worker-execution workflows. No capture, training, admission,
model export, Git write or producer build request.

## What we learned

- Received `ttr-interruptions-20261001-r2.tar.gz`:122,809,544bytes,
  SHA256`ac81aa85be099bcf05fae82acc8b89210adecb76b15c8edd9abd124395d28535`.
  All168manifest files match exact membership, hashes and sizes. Protected-hash
  screening passed before decoding. Original archive and extracted files retained.
- All20screens have matching before/after geometry/semantic brackets and valid
  measured body geometry.447diagnostic crops passed the production Swift16%/256px
  path.34partially covered,63fully covered and1removed body were excluded. No
  covered/removed element was silently labeled an unfocused visual example.
- Five action crops retain the separate interruption-action role.48ordinary body
  crops during modal focus have **unknown** ordinary focus, not negative labels.
  Dimming remains separate from occlusion. Crop expansion can include nearby overlay
  pixels; excluding covered bodies does not promise overlay-free context.
- Eight frames report `is_settled=false`; five also omit normal focus observations
  while the overlay reports focus separately. The two full-screen baseline frames
  and removed-target aftermath have native `verified=false`. Stable geometry is
  useful diagnostic evidence, not permission to rewrite settling or requested-focus
  verification. The removed target correctly stays unavailable while Genres gains focus.
-20files contain only **6unique full-screen PNGs**, and447crops contain50unique PNGs.
  Repeated screenshots are meaningful interruption controls but not diverse training
  samples. All share one recipe ancestry; do not split repeats/related scenarios
  across training and independent evaluation.
- Visually inspected banner, modal, fullscreen, failed-dismissal and removed-target
  previews. Visible sampled rectangles align with rendered bodies/actions; the
  failed-dismissal overlay remains present, and the removed poster has no box.
  This is agent diagnostic review, not a new human annotation approval.

## Concrete producer feedback

1. Preserve the two intentional failed recovery outcomes. A delivered input receipt
   remains `effectStatus=unverified`; it does not prove successful dismissal.
2. For a future trainable export, provide explicit **overlay settling and focus
   ownership**, separate from requested underlay focus. Do not simply set all existing
   `is_settled`/`verified` flags true. Clarify the two fullscreen baseline mismatches.
3. Bind each image hash/capture receipt to its exact observation interval and run/
   generation using the standard harvest envelope. This custom archive has hashes
   and ordered scene brackets but no explicit screenshot-time binding; we have not
   manufactured one. Body generations without ordinary focus are only internally
   consistent body records, not an independently bound native-focus generation.
4. No recapture requested for these originals. Prioritize the four new structural
   family proof **data exports** plus exact Git revision; never send a build/binary.

## Verification and evidence

New `scripts/audit_fixture_interruptions.py` checks the real archive, rejects unsafe
paths/protected hashes/membership drift, preserves negative outcomes and calls the
production crop helper. Nine new negative/positive tests plus84related tests pass.
Offline Swift build and134tests pass (14XCTest+120Swift Testing). Initial sandboxed
Swift invocation failed at nested `sandbox_apply`; the scoped approved rerun passed.

- [Audit JSON](artifacts/audit/audit.json)
- [All20frames and10overlay/aftermath previews](artifacts/audit/review.md)
- [Transfer receipt](artifacts/received/receipt.json)
- [Python93tests](artifacts/python-tests.log)
- [Swift build](artifacts/swift-build-verified.log) / [Swift tests](artifacts/swift-test-verified.log)

Reproduce with project-local TMPDIR and `PYTHONPATH=scripts`:
`python scripts/audit_fixture_interruptions.py --root <retained-r2-root> --protected reports/work/SYN-09-ARTWORK/artifacts/protected-screening.json --output <fresh-project-output>`.

## Current next work

TTR02:16:17UTC reports four-family generation/export proof passed and the remaining
44appearance cases collecting. This is producer evidence, not a delivered consumer
acceptance. Local TTR HEAD remains46dce7b; no source checkout change or stale rebuild.
The intended repair afterbdfac475 still needs publication/exact revision and the new
proof originals need delivery. Next: verify those diverse originals and build the
self-service caller locally from the matching Git source. FDR021 is unchanged.

Receipt and findings published/read back in `nuiak/status.yaml`, packet
FOCUS-INTERRUPTIONS-17; unrelated entries preserved. Peer acknowledgment pending.
[Coordination](coordination.md).
