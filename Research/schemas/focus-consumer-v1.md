# FocusRing consumer artifact contracts

2026-09-21. NUIAK-owned review/derived artifacts, **not producer wire changes**.
Canonical validation: `scripts/focus_dataset_contract.py`. JSON hashes use sorted
keys, compact separators and UTF-8. PNG hashes cover exact file bytes.

## Observed pair evidence

`focus-pair-evidence-v1` has `version`, `sourceKind: simulatorFixture`,
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
