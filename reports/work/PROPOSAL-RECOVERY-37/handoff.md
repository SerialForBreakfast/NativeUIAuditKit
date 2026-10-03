# Proposal recovery and experiment runner

| Outcome | Result |
|---|---|
| Software | 44 Python and 134 Swift checks passed; retained-output replay agrees |
| Data | Existing diagnostic roles preserved; no new training admission |
| Integration | Native Vision probe and runner caller wiring exercised; real runner training pending |
| Model gate | Not assessed; proposal recall is not final focus-selection accuracy |

## Main result

On the exact 46 real screenshots from scorecard36, adding existing raster and Apple
Vision rectangles raises focused-control proposal recall from **21/46 to 42/46**.
Reviewed control-body recall rises from **346/583 to 432/583**. At the tighter .75 IoU
requirement, focused coverage rises from 17 to 35; total body coverage from 316 to 389.

| Proposal source | Bodies at IoU .50 | Focused bodies | Candidates |
|---|---:|---:|---:|
| Shipped YOLO | 346 | 21 | 1,084 |
| Existing raster detector | 214 | 20 | 375 |
| Apple Vision rectangles | 298 | 35 | 1,104 |
| Raster wide rows with OCR support | 11 | 5 | 23 |
| YOLO + raster | 393 | 32 | 1,386 |
| YOLO + raster + Vision | 432 | 42 | 2,289 |

The union suppresses 274 near-duplicate proposals at fixed IoU .90. Candidate volume
increases from 23.6 to 49.8 per frame. The 1,857 unmatched union candidates are
**unreviewed**, not proven false positives: these annotations cover focusable controls,
not every visible region. We have recovered geometry, not determined which candidate
is focused. This reused development corpus is not an independent release benchmark.

Focused-body coverage by reviewed role, YOLO → union:

- List rows: 7/16 → 14/16.
- Collection items: 8/21 → 19/21.
- Primary buttons: 3/4 → 4/4.
- Other focusable: 1/2 → 2/2; tab items: 2/3 → 3/3.

Four residual targets: Paramount tall-poster shelf `recorded-614`, system-search
category grid `recorded-479`, App Store now-streaming `recorded-751`, and Paramount
expanded sidebar `recorded-839`. Their original reviewed labels remain intact.

[Machine result](comparison/result.json) · [fixed protocol](comparison/protocol.json) ·
[summary](comparison/result.md) · [replay verification](replay-verification.log).

## iOS companion

Selected 12 localized secondary-button examples and 12 localized cancellation examples,
using sorted distinct image IDs and frozen .25 confidence/.50 IoU. Existing fine-role
predictions are correct on 12/24, while all 24 retain a coarse button-family identity.
Exact OCR `Cancel` confirms 3/24, all correct; it abstains on the rest. The other
cancellation labels read `Dismiss` (4), `Not Now` (3), and `Close` (2). This explains
the low coverage without pretending a word-only rule can distinguish all button roles.

The cancellation hints confirm already-correct examples; they do not improve the
12/24 fine-role baseline. No fallback assigns `secondaryButton` merely because text
is not Cancel. Next semantic test needs contextual role handling and negative examples,
not a dictionary tuned on these same 24 samples and presented as validation.

## Bounded runner completed

`scripts/train_fullscreen_focus.py` provides a model-free validation CLI and a separate
supervised execution path, reusing `train_tvos_model.training_options`. It verifies
exact admission, bytes, complete ordinary-profile annotations, source-group separation,
decoded-pixel duplicates, runtime versions and resident checkpoint. Staging and loader
caches stay inside the fresh output root. The child revalidates inputs before model load.

Tests cover read-only validation CLI, exact YOLO label conversion, split/pixel leakage,
missing weights, admission/runtime mismatch, incomplete/unknown labels, shared recipe
defaults, positive model-double caller wiring, successful/failed children, wall-time and
output-limit stops. Partial artifacts are retained and overshoot reported. This is
software qualification; the first real MPS training execution remains to be performed
with an admitted full-screen contract and assigned training budget.

[Contract and usage](../../../Research/Plans/ProposalRecovery37.md).

## Execution and remaining dependency

- Vision rectangle/OCR: 70 existing images in two batches, PID39036, 5.986 seconds.
- Raster and score computation: 4.465 seconds. No inference repeat; replay uses saved
  Vision results and deterministic raster processing.
- One preflight attempt stopped before inference on existing iOS dataset image links.
  Resolved originals remain in-project and were hash-checked; strict harvest rules
  were preserved. No source data was copied for the comparison.
- [Python checks](python-tests.log), [offline build](swift-build.log),
  [offline Swift tests](swift-test.log): 14 XCTest + 120 Swift Testing tests.
- TTR source recheck: local adjacent checkout remains dirty at46dce7b, advertised
  dedfd613 absent (`git cat-file` fails), grid-density files absent. Exact source
  mapping/build remains blocked until matching source is published and synchronized;
  no older-build substitution. TTR reports new reference-screen data at00:16:51Z,
  which is a separate next intake opportunity, not locally verified in this tranche.

All independent assigned work is complete for review. Source mapping remains the
explicit dependency above. [Coordination](coordination.md) records publication and
TTR's acknowledgment of the prior priority update.

## Next substantial tranche

1. Score recovered candidate boxes with the existing focus selector, handling duplicate
   bodies and uncertain candidates, on the same 46 screens. Measure final selection and
   latency alongside proposal recall—this tests whether the gain actually helps TTR.
2. Intake TTR's named new reference-screen delivery with geometry/crop checks and grouped
   review preparation; establish its actual native-family coverage and data roles.
3. Assemble an admitted, group-pinned full-screen contract and execute one bounded
   crop/full-screen comparison once source/data prerequisites and run scope are met.
   Keep the iOS semantic follow-up separate from the small-control geometry experiment.
