# FocusRing consumer artifact contracts

2026-09-21. NUIAK-owned review/derived artifacts, **not producer wire changes**.
Canonical validation: `scripts/focus_dataset_contract.py`. JSON hashes use sorted
keys, compact separators and UTF-8. PNG hashes cover exact file bytes.

## Observed pair evidence

`focus-pair-evidence-v1` has `version`, `sourceKind: simulatorFixture|physicalFixture`,
`producerReference`, `evidenceKind: test-only|reviewed-fixture`, and `pairs`.
Each pair has `pairID`, `elementID`, and `frames.focused` / `frames.unfocused`.
Each frame contains bundle-relative `path`, `sha256`, `bounds` (top-left pixel
xywh), `frameID`, `focusFrameID`, `labelSource: fixtureCallback`, and
`observedFocusID`. Callback and image frame IDs must match. Focused identity
must equal the element; the resting frame must explicitly report null focus.
Requested focus alone is insufficient. Review evidence must come from observed
fixture telemetry; filling in plausible values is prohibited.

Optional `purpose: development-pilot` isolates the complete intake as development
membership. Default extraction preserves original producer partitions.

## Derived manifest 1.2

`focus_dataset_manifest.json` includes `version: "1.2"`, `corpusID`,
`sourceKind`, `producerReference`, `sourceRoot` (project-relative), `evidenceKind`,
`preprocessing`, `pairs`; extraction additionally records `evidenceSHA256`.
Source kind is `simulatorFixture` or `physicalFixture`; the simulator bundle
extractor never emits physical provenance. Physical extraction/qualification
remains separately owned.

Each pair contains `pair_id`, `recipe_group`, integer nonnegative `recipe_seed`,
`split`, `fixture_scene`, `theme`, `element_type`, `elementID`, `sourceKind`,
`labelSource: fixtureGroundTruth`, and the complete `frames` above. For each
role it retains `<role>_crop` (dataset-relative), `<role>_crop_sha256`, and
`<role>_crop_box` (expanded/clipped xyxy). Family/theme mapping is explicit in
`simulator_focus_manifest.py`; unknown values fail. Related seeds and identical
content cannot cross partitions. Distinct element pairs may share a seed/group.

Preprocessing is expansion 0.16 per side, 256×256 output, top-left pixel boxes,
`Pillow-affine-bilinear-v1`. Fractional origins are preserved. Validation
recomputes crops from raw PNGs; changing a crop and updating its hash fails.
This establishes local reproducibility, not CoreGraphics pixel parity.

Hard-negative membership is derived from verified unfocused test frames in
light/highContrast imageView/collectionItem cases. Caller flags do not qualify.
Quota tests require all four combinations and ≥100 total; theme percentages
use actual family totals, not minimum quotas.

## Training preflight

### Runtime crops (manifest 1.3)

Version 1.2 remains inspectable, but cannot pass training preflight. Version 1.3
uses `resize: FocusRingClassifier.makeCrop-v1`, retaining expansion/size/coordinates.
`runtimeCrop` records `sourceSHA256`, `helperSHA256`, `hostOS`, `architecture`;
validation requires the current helper identity and exactly regenerated RGB pixels.
Changing a PNG and updating its hash is insufficient. Rebuild/OS changes require
revalidation and a new derived version, not rewriting frozen historical identity.
`derivedFromManifestSHA256` binds the original manifest. Recropping preserves source
frames/splits but removes `trainingApproval`; newly derived pixels need review.

Build `FocusRingTool` with the repository's offline Swift workflow and explicitly
create `.build/debug-output/focus-launch/tmp` inside the package. No automatic build
or download occurs. Then, with fresh in-project output paths:

```sh
.venv-yolo/bin/python scripts/focus_runtime.py \
  --manifest dataset/focus_ring/intake/focus_dataset_manifest.json \
  --output dataset/focus_ring/runtime-crops
```

The package-only executable calls the actual production crop/classifier; no public
API is added. Raw inputs are hashed and decoded, bounds checked, and requests bounded
before CoreML loading. Python streams batches of 16 frames. Output collisions fail;
partial derived files remain diagnostic evidence, not a completed corpus.

The 2026-09-21 crop-origin correction changes runtime preprocessing, not weights.
Historical runtime scores require re-baselining; test gradients establish location
and orientation, not detector quality. See BP-62 and the launch-preparation handoff.

Run `scripts/train_focus_ring_detector.py --dataset <local-dir> --name <unique-name>
--dry-run` using `.venv-yolo/bin/python`. This imports no training runtime and
creates no outputs. Missing or ineligible inputs exit 2, not success. Fixed
candidate configuration is 30 epochs, batch 64, lr 0.0003, vendored MobileNetV4,
fresh state/seed 42. Train/validation/test must all exist; no fallback or skipping.

Corpus review additionally requires `trainingApproval` with `approved: true`,
`reviewReference`, and canonical `membershipSHA256` of `pairs`. This is a review
record, not authenticated authority. Agents cannot self-approve from parser success.
Execution still requires explicit user authorization, a recorded experiment ID,
and `--execute --experiment-id <id>`. Test data is never used per epoch.

## Frozen development baseline

### Direct native-generator extension — v1.4 (2026-09-22)

`direct-tvos-capture-v1` is a separate completed capture record, not a fabricated
TTR receipt. It binds the exact simulator/listener/build, frozen catalog, native
before/after observations, local capture intervals, PNG hashes, dimensions, counts
and postflight identity. `native-observation-bracket-v1` means temporal correlation,
not authenticated or atomic callback-to-frame identity. Partial captures are rejected.

The derived `1.4` manifest uses `tvos_native_generator`, development membership only,
the existing production 16%-expanded 256×256 runtime crop, and frame-specific bounds.
Visual review must bind the complete receipt hash. Test-only captures retain test-only
provenance. Existing v1.2/v1.3 behavior is preserved; v1.4 cannot pass full training
preflight. `focus_corpus_overlap.py` rejects cross-partition seed/group/decoded-pixel
overlap across source manifests without discarding intentional focus pairs.

Entrypoints: `direct_tvos_capture.py --plan [--smoke] --output <new-catalog>`;
`--execute --catalog <catalog> --target <exact-UUID> --endpoint <loopback-URL>
--output <new-directory>`; then `direct_focus_manifest.py --capture <direct-capture.json>
--visual-review <review.json> --output <new-directory>`. Review JSON contains
`captureSHA256` (canonical receipt digest), `accepted: true`, and `report` identifying
the visual evidence. Use the existing `focus_ring_baseline.py` on the derived manifest.
Full assigned scope and authority: [parallel acquisition](../Plans/ParallelTVOSAcquisition.md).

### Physical-source extension (2026-09-22)

Physical extraction uses the same `harvest_focus_pairs.py --fixture-bundle` path,
never a simulator relabeling or legacy metadata eligibility shortcut. Its explicit
NUA review artifact additionally supplies `sourceReview`: `sourceKind: physicalFixture`,
`reviewReference`, `deviceReference`, `runID`, `captureID`, `indexSHA256`, and
`receiptSHA256`. Hashes bind the original completed bundle's index/receipt bytes;
contradictory explicit simulator source context is rejected. Preserve the producer's
`observedSource` verbatim; review is reported provenance, not authenticated identity.

Each physical frame requires `nativeObservation` binding `frameID` and
`imageSHA256`, `nativeFocusResolved: true`, one `observedElementIDs` member
(the focused element or positively observed `tvtr.reference-focus` baseline),
`sampleAgeMilliseconds` in0–150 and `stableMilliseconds`≥150. These are strict
NUA review-admission bounds, not invented producer wire fields or instructions
to add delays. Missing/unresolved/multiple/stale evidence cannot become truth.
The reviewer must map actual source observations; never manufacture this envelope.
Focused pixel boxes must match metadata and normalized boxes under actual PNG
dimensions. Baseline boxes remain independently frame-specific.

The shared validator rechecks physical source bindings, raw/crop hashes, decoded
pixels, geometry, callback alignment and split isolation. It rejects identical
decoded pixels crossing partitions even with different PNG bytes. New physical
crops use the existing production v1.3 recrop command above. Training approval
remains separate; test-only physical-shaped fixtures are not physical capture.

`physical_focus_readiness.py --manifest <v1.2-or-v1.3-manifest> --output <new-report>`
reports byte-backed inspection separately from provenance, runtime crop parity,
coverage, operation authority and training eligibility. Legacy metadata-only
manifests remain inspectable/ineligible. Add `--model <compiled-model>` to prepare
the existing development baseline protocol; this does not infer. Supply
`--protocol <saved-baselineProtocol-object> --scores <bound-scores>` to score
through the shared baseline. No second model/evaluation pipeline is created.

Optional `--proposals` consumes `focus-proposals-v1`: `protocolSHA256`,
`artifactSHA256`, `inferenceKind: test-only|imported`, and `samples` with exact
`<pair-id>:1|0` membership. Every sample binds `imageSHA256`, has
`status: success|failed|unavailable`; failure needs `reason`, success needs
`proposals: [{bounds: [x,y,w,h], score: probability}]`. Scores come from an
independent proposal/classifier path, not fixture telemetry. Reports count
localization, wrong/no/multiple focus, abstentions and failures by family/theme/control.
This is pair-target scoring, not exhaustive screen or navigation accuracy.
Missing proposals remain unavailable; oracle-box crop metrics stay separate.

Diagnostic baseline reports with no hard-negative support use null FPR and no
gate pass; training/model qualification still requires all established quotas.
Complete CLI fixtures: `scripts/test_physical_focus_integration.py`.

`scripts/focus_ring_baseline.py --manifest <manifest> --model <compiled-model>
--prepare --output <new-protocol>` freezes development-only membership, model,
manifest and implementation hashes, preprocessing, and threshold 0.85. No inference.

Score envelopes have `formatVersion: focus-baseline-scores-v1`,
`protocolSHA256`, `artifactSHA256`, `inferenceKind: test-only|coreml`, and
`scores` mapping every `<pair-id>:1` / `<pair-id>:0` to a finite unit probability.
Run the same command without `--prepare`, adding `--protocol` and `--scores`,
with a new output path. Missing/extra scores, changed membership/artifact/code,
or output collisions fail. Reports include per-theme/control/family confusion
counts, support, FPR/FNR and example errors. Inference kind is supplied evidence,
not verification that a model was executed. Test-only reports never establish
model quality. Final evaluation requires its separate untouched protocol.

For explicitly assigned development inference on a v1.3 corpus, replace `--scores`
with `--infer`. This invokes the actual shipped CoreML artifact, binds model/helper/
source hashes before and after inference, and reports per-slice binary errors plus
abstention count, decision coverage and selective accuracy. Fixed ambiguity band is
[0.70, 0.85); threshold tuning is not performed. All-abstained selective accuracy is
null, not perfect. CLI output retains `evidenceKind`; generated test images remain
test-only even when scored by the genuine model.

CPU-only timings describe this Mac/helper, not tvOS deployment. Each process batch
records model load, crop and per-sample inference milliseconds. Warm p50/p95 exclude
the first sample of each batch; raw first-sample timing remains visible. No timing
or model gate is passed by these measurements. Old frozen protocols fail after code
changes: create new protocols rather than silently comparing incompatible evidence.
