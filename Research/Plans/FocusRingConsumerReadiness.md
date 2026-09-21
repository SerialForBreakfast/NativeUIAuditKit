# FocusRing consumer readiness tranche — 2026-09-21

User-assigned offline extensions to SIM-DATA-02 / FR-A and FR-SIM-BASE/CAND
preparation. No capture, new model benchmark, training, export or producer edits.
Required package tests may exercise existing bundled-model smoke inference.
PER-04 physical validator and its handoff remain untouched.

Implementation contract: [artifact formats and commands](../schemas/focus-consumer-v1.md).
The optional `development-pilot` extraction purpose explicitly isolates pilot pairs
from all final partitions; the original producer split is retained in each record.
Ordinary extraction preserves producer partitions rather than silently converting
its split policy into the planned 80/10/10 corpus policy.

Geometry parity is tested; Pillow bilinear interpolation is recorded explicitly
and is **not** proven pixel-equivalent to CoreGraphics. Actual Swift/CoreML crop
comparison remains a genuine-pilot qualification requirement.

## Contract decisions before implementation

- Add a NUIAK-owned `focus-pair-evidence-v1` review artifact, separate from the
  producer wire format. Extraction requires it explicitly; current producer
  requested-focus sidecars alone fail. Each pair binds focused/unfocused PNG paths
  and hashes, element ID, frame-specific top-left pixel boxes, frame ID and
  callback frame ID, observed focus ID, and fixtureCallback label source. Null
  observed focus is required for the resting baseline. Test-only evidence stays
  test-only. This adapter is not a claim of producer compatibility or authenticated
  identity. Producer changes require separate review and assignment.
- Derived crop manifest v1.2 preserves raw lineage and separate crop hashes,
  16% per-side expansion and 256-square output. Source root is explicit; all paths
  must resolve within the project and their designated roots. No fallback to one
  focused box for both frames. Old manifests remain inspectable but cannot launch
  the new candidate path without evidence migration/requalification.
- One shared validator checks bytes, dimensions, callbacks, duplicate pairs,
  split/content/related-seed isolation. Multiple elements in one group/partition
  are valid. `val` and `validation` normalize to validation; no train fallback.
  Quotas use actual scene totals and only verified test-partition unfocused
  light/highContrast imageView/collectionItem examples count as held-out negatives.
- A source review artifact does not grant training authority. Candidate preflight
  additionally requires explicit corpus approval, full quotas and a unique local
  output. `--dry-run` becomes a true preflight alias; execution requires an explicit
  launch switch and prior experiment-log record. No heavy imports or cache writes
  in preflight. Keep fixed 30 epochs, vendored backbone and fresh initialization.
  Test pixels/scores never participate in per-epoch selection.
- Baseline preparation freezes development-only sample IDs, artifact/manifest
  hashes, preprocessing and threshold 0.85. Score reports bind that protocol and
  exact membership, including errors/support per theme/control/family. Final
  evaluation stays a separately authorized stage. Deterministic fake scores do not
  become a shipped-model performance result.

## Completion evidence

Actual extraction → validation → trainer preflight and baseline preparation/report
entrypoints exercised with in-project test-only fixtures; positive and adversarial
tests; offline Swift build/test; no training or baseline inference. Report software,
data, live integration and model outcomes separately in
`reports/work/FOCUS-CONSUMER/handoff.md`. Preserve all historical data and unrelated
dirty files. Producer contract requests already published remain independent.
