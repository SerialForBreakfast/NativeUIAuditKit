# FocusRing launch preparation — assigned 2026-09-21

Scope: offline crop parity, actual CoreML baseline adapter, deterministic capture
planning and evidence-based review reconciliation. No capture/training/promotion.
Tests may infer with the shipped artifact on explicit test-only images; results
are integration evidence, never a model gate or genuine baseline.

## Architecture decisions

Observed during implementation: the existing crop's flipped draw context sampled
and vertically inverted a different image region on a known RGB gradient.
Correct top-left pixel coordinates in the unflipped CoreGraphics draw space by
placing the full image at y = canvasHeight - imageHeight + bbox.minY. Add content
orientation tests, not only size tests. Preserve weights; historical inference
scores using the previous preprocessing are not directly comparable.

1. Add a package-only diagnostic executable calling production
   `FocusRingClassifier.makeCrop` and `classify` directly. Package access only;
   no public API or copied crop algorithm. Bounded JSON stdin/stdout, no dataset
   writes. Python owns exclusive in-project publication. No implicit compilation.
2. Preserve v1.2 Pillow crops as historical/inspectable. New v1.3 runtime-crop
   manifests bind production-source and helper hashes. Recrop into a new corpus
   from verified raw frames; training requires this backend. Measure legacy
   pixel differences instead of assuming equivalence. Exact recrop validation.
3. Extend the existing frozen baseline, not a parallel pipeline. Validate all
   inputs before inference, reject missing/nonfinite outputs, report ambiguity
   and cold load/first/warm prediction timing separately. No threshold tuning or
   final evaluation groups. Shipped-model smoke uses test-only generated pixels.
4. Compile a producer-pinned reviewed recipe catalog into immutable 80/10/10
   related-seed groups, <=100-recipe batches, quota feasibility and resume reports.
   Planned targets are claims, not observations. Resume requires matching hashes
   and terminal completion/cleanup evidence. Partial/ambiguous batches block
   reuse. Actual accepted-pair counts remain separate. Emit no device commands.
5. Review PER-01/02/04/FOCUS-CONSUMER evidence against original criteria; accept
   only demonstrated scope and retain specific gaps, not inflated completion.

Verification: integrated positive/negative Python tests, actual CoreGraphics
crop comparisons, shipped CoreML test-only smoke, offline Swift build/test,
reports/work/FOCUS-LAUNCH/handoff.md and independent four-outcome reporting.

## Worker inputs, authority and exit

Inputs: accepted FOCUS-CONSUMER implementation, bundled FocusRing artifact, producer
recipe limits at inspected revision 562bd3a, and existing PER handoffs. Permitted
operations: local code/docs/tests and test-only model inference. No producer edits,
device operation, genuine benchmark, training, promotion or git writes.

Contracts and operator examples:
[runtime crops/baseline](../schemas/focus-consumer-v1.md),
[catalog/ledger](../schemas/focus-capture-plan-v1.md).
Build/test with project-local scratch/cache paths under `.build/debug-output/focus-launch/`;
never build/download implicitly from preflight. The handoff records exact commands.

Acceptance: actual production crop content tests; real test-only CoreML CLI roundtrip;
manifest/backend/byte/collision rejection; deterministic group/quota/ledger tests;
review findings mapped to original packet criteria; required offline Swift checks.
The next independent assignment is the bounded perception/physical review correction.
The next data action requires matching producer deployment, authorized clean smoke
and genuine intake before the pilot. A reviewed real recipe catalog remains an input,
not an artifact fabricated from the compiler's test-only quota fixture.
