# Human-reviewed focus development evaluation v1

Approved2026-09-28, HUMAN-REVIEW-04. This is an adapter contract, not a change to
human-annotation-review-v1, native journeys, taxonomy or library API.

`human-focus-development-evaluation-v1` seals an explicit approval, immutable human
revision and crop QA references, all original input hashes, ordered sample/pair
membership, one correlated source group, model identities, implementation and runtime.
Only role `development-regression` is allowed. `trainingEligible` and
`independentEvaluationEligible` stay false; `completeFrameCandidates` stays false.
The new `developmentEvaluationEligible` flag is true only in this derived protocol.
Original diagnostic files remain unchanged and incompatible with training loaders.

Admission reconstructs the existing audit, requires human-confirmed labels and zero
hard issues, verifies complete membership and production16%/256 crops, and checks
actual training/retention/protected metadata for hash and source overlap. Protected
members may be hash-compared, never scored or visually mined. Missing ancestry is
unknown, never independence; screen-family similarity is reported separately from
exact overlap. Role audit manifests and results are pinned, not inferred from dates.

The approval binds revision, crops, exact models, output location and maxRuns=1.
Freeze pins runtime/code; execution validates again and uses an exclusive run marker.
No implicit model download or alternate checkpoint. CoreML CPU scores production
crops from original boxes using the identical helper/source/runtime pinned by the
retained crop QA (the existing inference helper does not return PNGs). PyTorch CPU
uses those frozen RGB crops, [0,1] CHW and the vendored backbone. Threshold0.85 only.
Loaded identities, failures and every expected sample are recorded per model.

Metrics reuse focus_ring_baseline.evaluate, with undefined precision/recall explicit
null, per-screen/class support, explicit paired outcomes and duplicate-pixel sensitivity.
No inferred pairs, complete-frame selection accuracy, detector recall or latency-parity
claim. Numbered error evidence keeps original context and sample IDs. A failed run
preserves partial predictions and unavailable metrics; no silent subset scoring.
Retained-score rendering verifies approved membership, pixels and score/model
bindings without requiring model residency, old runtime or protected-corpus reads
(BP-106). It never authorizes another inference run.
