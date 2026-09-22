# Authorized P0-C resumption — 2026-09-22

The maintainer explicitly assigned iOS reconstruction to this architect task.
Base revision `5b24dd0eb9e9b1d0b1927bc93b539e84cb93a5aa`; initial tree clean;
no GeneratorRunner/NativeUIDatasetGenerator/xcodebuild process observed.
The existing P0-C scope permits only GeneratorRunner app-container reset/staging
on iPhone 17 Pro `F3EF9DB8-0B0F-4757-B653-D1628269F6FF`. This is not TTR/Office
or tvOS simulator authority. No training or model inference.

Read-only preflight: simulator shutdown/available, iOS 26.5 build 23F77;
Xcode 26.6 build 17F113; approximately 163 GiB available on project volume.
`NativeUITrainer/reconstructed_corpora/ios-41class-r1` does not exist.
Retain existing split/family/seed configuration and exclusion of HardNegative_2.
Actual source hashes and rendering environment will be pinned before generation.

## Research-first safety corrections

- The orchestration test invocation must select only
  `GeneratorRunnerTests/GenerateDatasetTests`, not unrelated model benchmark tests.
  Serial generation only. This does not change rendering recipes or seeds.
- Before launch, keep outputs/caches/results in the approved project paths; standard
  simulator runtime and this app's container staging are the previously approved exception.
- The existing validator checks PNG headers but not full decoding, annotation schema/
  dimensions/boxes, exact split counts, decoded-pixel leakage or immutable membership.
  Extend it before accepting the result. Reject path escapes/symlinks, corrupt members,
  incorrect split/family bindings, missing/extra members and output collisions. Preserve
  every rejected entry and report train/validation/test readiness separately.
- A successful renderer exit does not approve a corpus. Record coverage gaps and require
  a reviewed DS-G8 protocol; the 41-class map remains frozen, webContent uncovered.
  No silent dropping/deduplication/repartitioning. Retention belongs to the maintainer;
  a verified in-project copy is not an independent external backup.

## First attempt: stopped on demonstrated writer/schema mismatch

The owned generation began successfully (family policy and early render families passed).
Early read-only validation found safe-area `leading/trailing` instead of v1.0 `left/right`
and auto-detected `tabBarItem` outside the frozen map. BP-28 already requires excluding
that chrome artifact (its parent tabBar remains). An in-memory diagnostic projection
of those two fixes passes schema checks on all 1,150 manifested partial images.
SIGINT stopped only the owned xcodebuild; it exited 73 after reporting TEST INTERRUPTED
and a result-log finalization error. Preserve partial staging before any reset; it is
not a completed corpus. No training occurred.

Correct the writer's serialized keys, apply BP-28 at annotation/manifest output, and
test the existing normalized-box clipping bug with a rectangle crossing the top/left
image boundary. Use true visible intersection, marking wholly invisible elements excluded
and partial clipping as imageBoundary; preserve raw point/pixel geometry for diagnostics.
This changes neither schema nor taxonomy. Validate these changes on a bounded generator
test before a fresh isolated `ios-41class-r2` capture; never retrofit old partial pixels.

## Corrected run: early audit and acceptance limits

The first 1,950 corrected pairs pass full decoding/schema/binding/geometry checks;
92 offline Swift tests and both bounded simulator writer/policy tests pass. A later
2,000-member snapshot already contains 91 identical decoded-pixel groups (examples:
ActionSheet seeds 11704/11752 and 11708/11964). Different seed/status metadata does not
prove visual diversity. Keep generation as a complete raw inventory; do not discard or
repartition records. Full-corpus duplicate accounting remains an acceptance gate.

The validator must also reject an invisible element that is not explicitly excluded,
require image-boundary labeling for partially clipped elements, and distinguish
per-split structural readiness from corpus-wide qualification. An error localized to
one partition must not falsely imply another partition's pixels are missing; global
manifest/provenance errors still block every split.

## Visual audit: stop r2 before further scaling

First-frame-per-family overlays expose ordinary list content under large navigation
titles (SettingsList, SettingsDisclosure, SearchResults, Stepper, TabViewNavigation).
SearchResults uses a hardcoded top strip as `searchField_0`, while iOS 26.5 renders
the actual search control at the bottom. This is demonstrated incorrect geometry,
not a model-quality concern. Preserve the diagnostic selection and sheets in
`.build/debug-output/p0c-resume/early-visual-review/` and stop the owned capture.

Before another full corpus: replace proxy search boxes with visible UIKit control
geometry, and test safe-area handling in native-navigation template content. BP-02
applies to manually positioned fullscreen canvases, not an instruction to push
native List/Form content underneath its enclosing navigation chrome. Use bounded
real rendering and visual verification across the affected families/profiles;
preserve all earlier outputs and pin a new source version if corrections succeed.

The fresh-install all-family probe contains 108 fully decoded/schema-valid pairs
with no duplicate pixels or family leakage at that sample scope. Visual review also
found MapOverlays' offset tile grid centered inside its frame, leaving most of its
annotated map blank, and NotificationCenter's date-label box including positioning
padding. Apply BP-01/BP-18 directly: top-leading padding-based map layout/clipping,
and capture the date text before padding. Recheck real rendered samples.

Incremental xcodebuild once omitted the newly compiled probe and ran an older
ten-image version despite matching installed/built bundle hashes. Resetting only the
authorized, already-preserved GeneratorRunner app allowed all four intended tests
to execute (108 family samples plus 26 navigation samples). Require actual named
test execution and generated sample counts, not just TEST SUCCEEDED.

## Maintainer decision: preserve counts, expand deterministic variants

The maintainer approved retaining 16,940 distinct accepted images rather than a
smaller deduplicated corpus. Implement the bounded candidate schedule and meaningful
loading-backdrop expansion in [the decision record](next-corpus-decision.md).
All three real generation loops use the same decoded-pixel selector. Rejected
duplicates keep their original pixels/sidecars and accepted-member relation in a
versioned capture ledger. Independent Python validation still rejects any duplicate
accepted content; the native selector is not the sole acceptance check.

The maintainer also identified hardcoded painted connectivity/battery glyphs.
ChromeCoverage now consumes sidecar status configuration, with fixed-clock tests
for separate cellular, Wi-Fi and battery-charge axes. This is synthetic status-bar
appearance coverage, not battery-health labels or proof of actual network state.

## r3 early stop: preserve the frozen cellular-state enum

The painted bar has four physical bars, but schema v1.0's declared cellular scale
is `[0,1,3,5]`. Changing the generator's full-signal value to 4 made early r3
sidecars invalid. Stop only owned xcodebuild 84500 (verified child of the r3
orchestrator); it exited 73 after interrupted-result finalization. Preserve all
Documents under `.build/debug-output/p0c-resume/rejected-r3-evidence/` before reset.
Restore declared value 5 and retain its explicit four-painted-bars representation;
do not modify the frozen schema. The status-axis probe now emits sidecars as well
as PNGs and uses only schema-supported values. Require their independent schema
validation before r4; visually distinct PNGs alone did not verify metadata.

Final coverage reporting must separate all annotated instances from visible,
non-excluded instances. A wholly off-screen, explicitly excluded control is useful
diagnostic evidence but cannot establish visible training-class coverage. Preserve
the raw distribution for manifest reconciliation and report the visible subset
separately; this changes the consumer audit, not the frozen r4 rendering source.

## r4 stop: MenuButton's finite visual space and missing fail-stop guard

The MenuButton test failed after 134 seconds. XCTest surfaced `InvalidTransition`
with `failed(deinit)`, but retained candidates identify the actionable cause:
`MenuButton-24304-0` through `-31` all duplicate earlier accepted screens. The
ledger stops at 103 accepted MenuButton slots. Fixed filler text and a small
selection/title pool do not provide the requested independent visual variants.
Expand seeded contextual row content; retain native Menu controls and class/split
contracts. Verify the complete 200-image MenuButton batch before another scale run.

The manifest was saved only after a family, while the ledger was saved at teardown.
XCTest then began MultiSectionForm at the same uncommitted image indices. The
incomplete r4 corpus is therefore invalid as a whole; preserved at
`.build/debug-output/p0c-resume/rejected-r4-evidence/`. Stop exact owned xcodebuild
86125 after checking its parent 86060; interrupted result finalization is separate
from the original failure. No simulator daemon or other app was stopped.

Add a persisted generation-failure guard: any thrown generation error records its
diagnostic context; subsequent generation tests skip without writing. Keep complete
prior batches and incomplete evidence distinct. Do not silently lower counts or
increase the candidate bound. A later reconstruction may reuse only independently
verified, completely manifested r4 batches in a new destination, with explicit
source/build lineage and exact preserved hashes; never import uncommitted MenuButton
or post-failure files. All rejected r4 evidence remains unchanged.

## r5 stop: seed-stride aliasing in UIKitControls

After 14,340 complete manifested images, UIKitControls exhausted all 32 candidates
for original seed 6021. Its control values used `seed % 2/4/5/8`; adding 1,000,000
preserves all those residues. The bounded retry therefore could not meaningfully
vary these controls. Replace those directly coupled residues with successive draws
from the seeded RNG, including meaningful slider/progress percentages. Preserve
native controls, layout, annotation collection, taxonomy and the candidate bound.

The r5 failure guard worked: five later tests skipped before writes; no subsequent
family overwrote unfinished output. Status-override cleanup exited 0. Xcode returned
65; the one-off driver's stale-container evidence copy then failed, as anticipated.
Preserve the actual current container in `rejected-r5-evidence`, not the stale path.
The valid 14,340-member prefix may continue under the existing verified-prefix rules.

With capture stopped, also correct ChromeCoverage's unused optional-status fallback:
use schema full-scale cellular value 5 and canonical HH:mm for legacy one-digit hours.
Actual r4/r5 captures always supplied valid explicit status values and are unaffected.

Qualify representative fixed-seed UIKit variations and the fallback in native tests.
Then execute the five remaining complete recipe batches as one bounded qualification
tranche (2,600 images), retaining successful output as the final corpus rather than
rerendering it. Every full family count, global uniqueness and the unchanged total
must pass before freezing. This is not a quota reduction or automatic retry of the
failed build. Re-resolve the app container after Xcode installation/teardown.
