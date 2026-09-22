# Focus integration replay — FOCUS-PARITY-01

Assigned 2026-09-22: test the proposed record/replay/compare workflow. First isolate
crop/input parity on existing recorded images, then record a bounded native OS
journey if runtime authority and target availability permit. No training, promotion,
Office use or producer edits. Preserve existing work and model artifacts.

Compile the actual TTR FocusDetectorService and FocusScoring source read-only in
an isolated NUIAK diagnostic harness. Mechanically extract its crop and rectangle
dependencies and bind them to source hashes. Reuse NUIAK FocusRingTool for the
production crop and model path; do not add another production cropper or trainer.
Compare identical image bytes and manually specified boxes first, holding the
shipped model constant. This isolates preprocessing, not candidate-box detection.
TTR's compute selection and failure-to-zero behavior remain explicitly reported;
do not treat cross-backend timing as a model speed comparison.

Use hash-verified historical TTR pilot screenshots as development-only cases,
plus deterministic asymmetric synthetic images to expose origin/context differences.
Historical approximate boxes are not new gold annotations. Preserve unexpanded
and production crops, pixel differences, probabilities, thresholds and model/source
hashes. Runtime inference failure is not a confident negative. No corpus admission
or model gate follows from these few examples.

Acceptance: real crop entrypoints exercised, dimensions and pixel differences
reported, identical model identity recorded, deterministic input accounting,
unchanged external sources, and scoped producer feedback. A complete navigation
benefit comparison still requires an ordered, independently labeled journey and
separately verified live controller. Missing such evidence must remain explicit.
