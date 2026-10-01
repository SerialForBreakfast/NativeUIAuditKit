# TTR experimental FDR021 consumer handoff

Request: `nuiak-20261001-fdr021-rgb-consumer`. No device operation or promotion
requested. Acknowledge the contract and identify the isolated candidate loader/build.

## Required compatibility

- Candidate ID: `focus-ring-experimental-fdr021-reviewed-contrast-rgb-v1`.
- Metadata: `inputPixelContract=png-straight-rgb-v1`, `releaseEligible=false`,
  focusThreshold0.85, ambiguityThreshold0.70.
- Updated source: `Sources/NativeUIAuditKit/Detection/FocusRingClassifier.swift`,
  SHA256 `e04bee2d2e0090d679dfad03051702203c008e4b30dc3bb8314aee7f1599fcad`.
- Production crop remains16%expanded256square. The final crop is losslessly encoded
  to PNG in memory, decoded to straight RGB, then copied explicitly into opaque BGRA.
  Do not blend into black/white or redraw this intermediate RGB into another context.
  Do not feed an uncropped original to the classifier or apply normalization twice.
- Reject unknown input contracts before accepting the model. Older NUA consumers
  ignore this metadata and are incompatible; simply swapping a model file is unsafe.
- NUA's existing public request/session loads the bundled classifier; its alternate
  load helper is internal/package-scoped. Confirm the actual experimental TTR loading
  route. This handoff does not claim a public override API already exists and does
  not authorize replacing the bundled/shipped model to work around it.

## Local candidate identities

Project-relative package:
`reports/work/FDR021-PIXEL-PARITY/export/FocusRingDetector.mlpackage` —3,788,293bytes,
SHA256 `68dba4256a292fa523a8a5e8c94f077fca630f5b2dc84cfbb323ae90ce797653`.

Compiled directory:
`reports/work/FDR021-PIXEL-PARITY/compiled/FocusRingDetector.mlmodelc` —3,795,452bytes,
SHA256 `df524aa79a231389c051e3e9eaffe9fab019f50b108174b35d74c13e59ab55bc`.

Tree hash algorithm: `scripts/focus_ring_baseline.py:artifact_digest` sorts all
file paths, feeds UTF8relative path followed by NUL then exact file bytes into
SHA256. This is not an archive hash. Recompilation may change compiled identity;
record the actual loaded identity. No shared-copy/receiver receipt claimed.

## Acceptance and ownership

NUA local proof:333/333final-input RGB hashes match; CoreML CPU probability
max error0.0000341, zero decision flips at0.5/0.70/0.85. No model-quality improvement
is claimed by conversion parity. Existing artwork failures/coverage gaps remain.

TTR next: report source/build, isolated opt-in loading interface, supported input
contract, backend, actual loaded hash and fallback behavior. Then define an approved
observer-only replay against retained frames, without navigation, using identical
boxes and explicit missed/failed predictions. Device/ANE parity is a separate test.
Keep the shipped default and a straightforward rollback. If the current build omits
NUA or lacks a candidate path, state that gap instead of treating this artifact as
already integrated. No further annotation is required for this compatibility work.
