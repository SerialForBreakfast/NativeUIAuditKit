# GEN-PARITY-199 — TTR knowledge and assets into the iOS generator

## Assigned outcome

Inventory source-backed capabilities, request one consolidated producer handoff,
and implement an offline content-addressed reuse/batch planner now. Then extend
the existing iOS media template with qualified artwork after exact manifest/rights
and renderer prerequisites arrive. No duplicate TTR generator, capture service,
third-party library imports or automatic asset downloads. Tasks.md is the queue.

## Findings from current local evidence

| Area | iOS evidence | TTR evidence / uncertainty | Decision |
|---|---|---|---|
| Seeded recipes | GeneratorConfig.swift, ContentCorpus.swift, MediaCardGridConfig.make | Current local TTR source is46dce7b; peer reports550a2d37 plus newer uncommitted rendering work | Share recipe concepts, pin actual revisions; no claim local parity |
| Visual axes | VisualProbeCatalog v2 has144 development cases; theme/profile/type and clock/charge/connectivity intersections | Richer media, artwork and focus state workflows reported | Preserve requested versus measured state; DynamicTypeOverflow fixed AXXXL remains a gap |
| Media imagery | MediaCardGrid uses hue backgrounds and SF Symbols, four-to-nine cards, two/three columns; no external-artwork input in its config |13generated originals reported:10clean-use candidates,3text-bearing challenges; roles incomplete | Add opt-in asset binding later, leave default seeds/pixels unchanged |
| Licensed assets | No qualified shared image library wired into this template | Big Dog reports500processed images,170automated-clean/330challenge,339human-review cases pending | Screening is not rights/admission clearance; metadata inventory first |
| Native UI sources | UI-SOURCE177 inspected five candidates; selected iOS SwiftUI Catalog views are source candidates | TTR acknowledged Apple/SwiftUI-Kit adapters; custom parallax deferred, Swiftfin feasibility only | Do not describe this as an imported UI-view corpus; request exact implemented file/dependency/notices closure |
| Ground truth | captureFrame measures native layout; IOS172 exposed requested transforms that did not move pixels | Artwork presentation geometry source/offline tests reported; fresh pixel qualification pending | Native iOS measurements required; do not copy tvOS focus/body rectangles |
| Transfer/reuse | shared_transfer.py supports verified immutable transfers and receipt cleanup | ART191 replacement regular-only selected20 bundle offered | Reuse transport; separate artwork inventory from native-capture intake |

Evidence: [source spike](UIComponentIntake.md), [asset plan](GeneratedMediaAssets.md),
`NativeUIDatasetGenerator/Sources/GeneratorConfig.swift`,
`NativeUIDatasetGenerator/Templates/MediaCardGridTemplate.swift`,
`reports/work/IOS-NATIVE-172/handoff.md`, and peer status observed October6UTC.
Peer reports are not independently verified rendering/licensing outcomes.

## Immediate implementation: asset-reuse-plan-v1

Implementation: `scripts/generator_asset_plan.py` can
consume a NUIAK-normalized inventory, not an
invented TTR wire schema. Producer may return existing manifests; NUIAK adapts them
explicitly preserving originals. Input schema `generator-resource-inventory-v1`
has `resources`, each with id, kind (artwork/mockup/native_capture/ui_source),
sha256, bytes, source, sourceRevision, ancestryGroups, dataRole,
rightsStatus, rightsEvidence, reviewStatus and reviewEvidence.

Roles: train/development/validation/test/unassigned. Rights and review statuses:
verified/pending/rejected. A status is a reported assessment with an evidence
reference, not independent legal verification. Unknown/malformed fields fail closed.
Do not encode remote paths or executable commands; hashes identify content.

Planner verifies explicitly listed local cache files via existing transfer hashing,
rejects conflicting sizes/duplicate IDs, and finds connected lineage/hash groups
crossing assigned roles. It emits deterministic <=128MiB batches of missing artwork
with <=64MiB individual objects, retaining aliases and evidence. Pending rights or
review block render selection. UI code routes through Git/source review; mockup
screens remain design references, not UI labels; native captures route through the
existing strict intake. No plan upgrades a resource into training eligibility.
Cache reuse means verified bytes only, not decoded/rendered/admitted data.

CLI contract refinement (199/204): normalized JSON has `schemaVersion` and `resources`.
Cache locations are separate `asset-cache-index-v1` records (`files`, each sha256/path),
relative to an explicit local cache root. Reject unknown core fields, symlinks,
traversal, duplicate cache hashes/IDs and inconsistent sizes. Hash aliases stay in
inventory but are requested once. Check connected ancestry across all resources,
including blocked/unassigned bridges. Optional `sourceRecord` retains producer data
without interpreting its paths. `plan` is read-only unless given a new output file;
it never copies, downloads, renders or admits data. `normalize-image201` explicitly
adapts the received inventory-v1.json, preserving originals/development ancestry and
marking rights/review pending. Worker candidate-for-review is not approval. Caller
supplies cache paths independently. Bound metadata/entry counts and refuse output
collisions. No new renderer, cropper or training schema is introduced.

Run the actual CLI with deterministic positive/negative fixtures, including changed
cache bytes, output collision, traversal/symlinks, unknown schema, disconnected
lineage collisions, role conflicts, oversized files, pending rights and mockups.
Run repository-required offline build/test once after integrated changes. No simulator
or Torch import is required. User request is the implementation authority.

## Efficient producer handoff

Publication checkpoint: both tiered requests were published and read back on the
verified SMB share; no peer acknowledgment or asset receipt claimed. TTR request
SHA256 a3bb8369caae05bce49da44ee4700fb4eb796a7bd2edc7e9f4ba3de5f6f9a06d;
worker request SHA256 274749d6afc1bc0a01302c905ffaf19687416b88cd857e99aa77fa4c9f9d95a6.
No implementation code, native runtime or training was changed at this checkpoint.

Maintainer follow-up prioritizes information up front and independent tiers:
P0 proven source/contracts/lessons; P1 asset inventory and missing-hash pilot;
P2 selected native UI/dependency/notices closure; P3 future platform adapter map.
TTR and Big Dog receive separately addressed linked requests, not duplicate jobs.
macOS design reuse does not waive the existing DS-G8 gate or start AppKit work.
Requests: `reports/coordination/generator-parity199-ttr.yaml` and
`reports/coordination/generator-parity199-worker.yaml`.

One metadata response groups four independently reusable inputs:
1. Published Git revision and selected paths/tests/dependency locks/notices for code.
2. Artwork-only inventory: source and derivative hashes, dimensions, role/genre/style,
   rights evidence, review results, sheet/crop ancestry and any rejected members.
3. Mockups/design references clearly marked non-labels.
4. Genuine capture bundles with existing receipt/schema contracts, kept separate.

Request no binaries, whole repository tarballs, account/player stacks or duplicated
review rasters. NUIAK returns missing-hash batches after inventory inspection.
Producer packages only requested regular files with relative paths and an inventory;
no links/special files. Use existing SMB receipt flow, approved space checks and
USB retention. First batch <=128MiB, target <=24reviewed diverse artwork objects;
bounded decode budget is separately qualified. Larger source libraries stay at the
producer until needed. Exact per-member receipts allow reuse across iOS/tvOS and
Big Dog without repeatedly transmitting the same pixels. Do not silently adopt the
peer's HTTP server or archive-mirror service.

## Follow-on IOS-ASSET-200 — one opt-in native adapter and campaign

Implementation contract refinement: generator-only `ios-generator-artwork-v1` is a
strict development catalogue (schemaVersion, assets), not a public library or training
sidecar change. Each asset records id/path/sha256/bytes/width/height/ancestryGroup,
dataRole=development, verified rights/review statuses and nonempty evidence lists.
The native loader checks bounded single-frame PNG decoding, orientation, exact bytes,
dimensions and root-relative link-free paths. No placeholders on failure. A throwing
MediaCardGridConfig adapter binds one asset per card; original factory/default rendering
is unchanged. Fit/fill rectangles are recorded mathematically relative to the measured
thumbnail viewport, not substituted for the existing native control annotations.
One opt-in hosted test exercises the real adapter/capture path and emits a separate
asset-binding receipt. Ordinary offline tests exercise loader/geometry, not simulator
rendering. Asset review and the full96-scene/two-composition campaign remain separate
acceptance steps; missing detail composition is a reported gap, never renamed grid data.

Inputs: accepted actual asset manifest, decoded dimensions/colorspace, notices,
unchanged existing generator baseline and exact local iOS simulator/build authority.
Implement an optional validated asset catalog in the generator-only media-card path;
existing no-asset configuration must retain original behavior. Native controls/text
remain native; artwork contains no trusted UI annotations. Fail before capture on
unknown/hash-mismatched assets; no silent placeholder success. Retain source hash,
fit/fill/crop, clipping, requested/measured state and generator lineage per scene.
No public library API or taxonomy change.

Start a development-only matched campaign: two native compositions (grid and detail),
two themes, two density levels, four seeds (200–203), three content conditions
(procedural/low-detail artwork/busy artwork):96planned scenes, max48per batch.
This is a proposal, not frozen launch membership. Freeze family/seed/asset-connected
groups together, exclude final evaluation ancestry and inspect support before capture.
Hold controls/geometry fixed across artwork conditions; layout variation is a separate
factor. Native UIKit/SwiftUI distinction remains explicit; don't claim two independent
implementations from one wrapper. Every annotation and asset binding validates;
inspect all flagged cases plus each composition/theme. Record setup/capture/intake
time and accepted scenes/hour. Score the fixed existing model once per scene, report
misses/false positives/geometry by condition, no training or threshold tuning.

Acceptance: default regression tests, missing/corrupt/oversized asset failures,
correct scale/fit/clipping, actual pixel content distinct from requested metadata,
complete counts, zero cross-role lineage leakage and production preprocessing parity.
If asset transfer or runtime fails, preserve evidence and report exact resume inputs.
Next: a separately registered data-only comparison after useful coverage is established.

### Campaign execution refinement — October6 UTC

Correct the original arithmetic:2×2×2×2×3 was48. Four pinned seeds preserve the
96-scene target without adding a confounded placement axis. All artwork uses fill;
fit remains covered by the earlier probe. Grid density is4cards/2columns or6/3;
detail density is220-point hero/short body or300-point hero/full body. These are
explicit layout changes, held fixed across the three content conditions.
Use reviewed thumbnail04 (lower detail) and03 (busier); same subject ancestry,
development only, no independent-content generalization claim. This relative
contrast is not a pure causal clutter intervention: composition/colors differ too.
Reuse existing CardDetail and ScreenshotCapture; opt-in overrides only. Native
batch contract pins target/catalog and96exact recipes; two48-frame shards reuse
one simulator setup. Per-scene seals include PNG and sidecar; resume validates
sealed completed scenes and refuses ambiguous partial files, never overwrites.
Each shard has120seconds capture budget and explicit output name; final complete
receipt is written last. Host validates all matched triplets and native geometry,
then reuses the existing fixed-checkpoint evaluator (not another inference engine).
