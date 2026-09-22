# Perception benchmark v1 labeling rubric

`perception-benchmark-v1` is evaluation truth for TTR perception. It is not an
annotation-schema revision, a detector taxonomy change, or a training corpus by itself.

## Required case identity

Each case has a stable `caseID`, original `imageSHA256`, pixel width/height, source kind,
journey ID, split group, and one partition. Keep a complete journey, retries, recipe
variants, and duplicate pixels in the same partition. `imagePath` may be absent for
schema-only test fixtures. The CLI requires byte/hash/PNG-decode/dimension validation
for every non-test-only case even without `--verify-bytes`; the flag additionally
verifies test-only cases. Paths stay in-package, never a directory to scan. Passing
integrity does not authenticate the source/reviewer or authorize training.

## Truth labels

- `labels.origin` is `reviewedVisual` or `fixtureGroundTruth`; it can never be a model
  prediction.
- A visible chevron has an in-frame top-left pixel box and exactly one reviewed row ID.
  A clipped chevron may also supply its visible box and reviewed relation; it is
  then scored only against those visible pixels. Unlocalizable clipped, occluded,
  absent, and unknown cases have no box or relation.
- A dialog records its reviewed box, member button IDs, optional visually observed focus,
  and semantic meaning. A label with unclear or unsupported localized language is
  `unknown`, never guessed as informational or destructive.
- Focus labels name the exact frame that supplied the observation. A callback from another
  frame is stale and invalid.

Predictions use the separate `perception-predictions-v1` document. Each available adapter
must account for every benchmark case twice: `proposals` scores the actual proposed boxes;
`oracle` scores relation/semantic behavior with reviewed boxes supplied. An unavailable
adapter reports a reason and produces no synthetic empty predictions.

Acceptance clarification (2026-09-22): both prediction payloads require explicit
`chevrons` and `dialog` fields; `[]` and `null` mean successful empty results, while
missing fields are invalid. A localized chevron with `rowID: null` increments
`associationAbstentions`, not `wrongRowLink`; a claimed incorrect/unmatched row still
counts as a wrong link. Pixel dimensions must be integers, never booleans.

## Interpretation

The report separately counts chevron localization, correct row association, wrong-row
links, decorative-arrow false positives, abstentions, dialog localization, button membership,
dialog focus, and destructive-as-benign errors. Test-only or unreviewed evidence can verify
software only. It cannot justify a targeted model, physical-data eligibility, or a model gate.

`semanticAbstentions` counts explicit unknown predictions. `destructiveAsBenign`
counts destructive truth predicted informational, not unknown. Nonfinite/boolean
boxes are rejected. Reports explicitly retain `trainingEligible: false` and
`modelGatePassed: not_assessed`; unavailable predictions are not a measured baseline.

## Offline comparison extension (2026-09-22)

`--observations FILE` accepts `perception-observations-v1`:

- `adapter`: `id`, `kind` (`test-only` or `imported-detector-ocr`),
  `artifactSHA256`, `preprocessingSHA256`.
- `cases`: exact case membership, each with `caseID`, `imageSHA256`, and
  `status` (`success`, `failed`, `unavailable`). Failures require `reason`.
- Success rows require `locale`, and explicit `rows`, `chevrons`, `dialogs`,
  `ocr` arrays—even when empty. Every observation has top-left pixel `box` and
  finite unit `confidence`; rows additionally have unique `id`, `role: row|button`,
  optional `focusScore`; OCR has `text`. Truth labels are not adapter inputs.

The simple geometry baseline filters at0.75, associates a right-hand arrow only
when one row meets the vertical-overlap rule, and uses center containment for
dialog buttons. Multiple dialogs/ambiguous row links abstain. Only one button
over0.85 is selected. Reviewed small English phrase lists provide destructive
or informational hypotheses; unsupported locales/text stay unknown. Disabled
row state never authorizes selecting that row. These are benchmark rules, not
navigation policy or a new detector.

Oracle component scoring supplies truth boxes and element roles but preserves
observation-derived OCR and focus scores. Actual proposals never receive truth.
Predicted row IDs are matched to reviewed rows by unambiguous IoU≥0.5, not string
identity. Duplicate proposals are false positives, failed execution is not an
empty success, and absent support yields unavailable/null metrics.

Report v1.1 binds canonical manifest/prediction/observation/settings and evaluator
hashes, declares supplied predictions as external assertions, and separates the
geometry baseline from unavailable TTR-raster artifacts. Slices cover source,
partition, theme, control, locale, focus treatment and row state (missing = unknown).
Deterministic split-group bootstrap intervals require ≥2 supported groups and do
not establish independence of near-duplicate journeys. Decoded-pixel duplicates
cannot cross partitions even when their PNG encodings differ.

Optional `latency` has `kind: test-only|measured-import`, machine, OS,
`scope: inference|end-to-end`, and finite nonnegative millisecond arrays `cold`
and `warm`. Report p50/p95 with support; missing timing stays unavailable.
Imported timing is not independently measured here and never deployment-qualified.
Development error triage and no-training recommendations remain separate from
future reviewed numeric model/latency gates.

Executable examples: `scripts/test_perception_completion.py`; integrated CLI:

```sh
.venv-yolo/bin/python scripts/perception_benchmark.py \
  --manifest <manifest.json> --predictions <predictions.json> \
  --observations <observations.json> --output <new-in-project-report.json>
```
