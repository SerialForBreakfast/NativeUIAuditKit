# Perception benchmark v1 labeling rubric

`perception-benchmark-v1` is evaluation truth for TTR perception. It is not an
annotation-schema revision, a detector taxonomy change, or a training corpus by itself.

## Required case identity

Each case has a stable `caseID`, original `imageSHA256`, pixel width/height, source kind,
journey ID, split group, and one partition. Keep a complete journey, retries, recipe
variants, and duplicate pixels in the same partition. `imagePath` is optional until a
bounded byte-verification run; when used it must be an explicit in-package path, never a
directory to scan.

## Truth labels

- `labels.origin` is `reviewedVisual` or `fixtureGroundTruth`; it can never be a model
  prediction.
- A visible chevron has an in-frame top-left pixel box and exactly one reviewed row ID.
  Occluded, clipped, absent, and unknown chevrons have no box or row relation.
- A dialog records its reviewed box, member button IDs, optional visually observed focus,
  and semantic meaning. A label with unclear or unsupported localized language is
  `unknown`, never guessed as informational or destructive.
- Focus labels name the exact frame that supplied the observation. A callback from another
  frame is stale and invalid.

Predictions use the separate `perception-predictions-v1` document. Each available adapter
must account for every benchmark case twice: `proposals` scores the actual proposed boxes;
`oracle` scores relation/semantic behavior with reviewed boxes supplied. An unavailable
adapter reports a reason and produces no synthetic empty predictions.

## Interpretation

The report separately counts chevron localization, correct row association, wrong-row
links, decorative-arrow false positives, abstentions, dialog localization, button membership,
dialog focus, and destructive-as-benign errors. Test-only or unreviewed evidence can verify
software only. It cannot justify a targeted model, physical-data eligibility, or a model gate.
