# Independent tvOS Simulator dataset lane

**Execution paused by user (2026-09-20) until further notice.** Preserve all evidence
and offline review; repaired runtime alone does not authorize resumption. The current
available priority is the [physical Office lane](OfficeFocusRing.md).

Revision 1, 2026-09-20. Maintainer-approved planning contract. State/ownership lives
only in [Tasks.md](../../Tasks.md#tvos-simulator-datasets). Follow the
[common execution contract](../ImplementationPlans.md#common-execution-contract),
[worker workflow](../WorkerWorkflow.md), and mandatory pre-code reading in AGENTS.md.
Each packet is a substantial implementation/integration/verification tranche, not
permission to stop after a helper. This document does not execute or accept a packet.

## Milestone and authority

Priority amendment (2026-09-20): SIM-DATA-01–04 are the highest dispatch-priority
foundation for [usable FocusRing delivery](FocusRingSimulator.md). SIM-DATA-05 is
secondary and nonblocking. After SIM-DATA-03, complete FR-SIM-BASE before SIM-DATA-04
scale-up. Pilot groups are development-only and excluded from final evaluation groups.
The three FR-SIM follow-ons add separately authorized model/TTR work; this document's
five packets remain dataset-only.

Deliver validated simulator-only datasets for visual FocusRing and tvOS detector
augmentation on the NUIAK Mac. No training, export of models, promotion, physical
qualification, or iOS DS-G8 claim. Office remains released until explicit renewed
user authority. Sillycon's runtime remains independent; no SSH, takeover, or remote
execution. Defer Settings mapping, navigation-defect datasets, and VoiceOver alignment
datasets. A visual focus pair does not prove an accessibility mismatch.

Use the initial producer source reference
`c6ec816bd94e9526f890e4894ad6a71f9e840e58`; record actual app/helper/fixture builds and
dirty changes separately. A new producer revision requires an explicit compatibility
record, not silently relabeling an older qualification. Source presence is not runtime
readiness. Existing accepted P4-A/FR-A scopes remain accepted; add targeted extensions
and regression tests rather than rewriting those packets.

Runtime inventory and offline software work are separately dispatchable. Installation,
boot/launch, simulator capture and standard app/simulator storage outside NUA require
explicit setup/execution authority. No automatic runtime download, service reset,
occupied-session restart, permission change, or physical-device fallback is permitted.
Producer code/build changes belong to a separately assigned TVTestRig task under that
repository's rules. NUA scripts do not acquire permission to write its checkout.

## Source evidence and operational lessons

Producer paths below are relative to the separately owned TVTestRig checkout:

- `Skills/tvtestrig/SKILL.md` and `references/interfaces.md`: exact UUID targeting,
  matching helper, current non-attested source-description policy, CLI-only batch,
  partial-publication rejection, and separate control/capture ownership.
- `Skills/tvtestrig/references/capture-protocol.md`: actual start/finalization evidence,
  clock domains, ambiguous completion, owned cleanup, and retained invalid trials.
- `TVTestRig/TVTestRig/CLI/StableCLIRunner.swift`: simulator batch selects
  `productionSimulator`, distinct from physical-device IPC capture.
- `TVTestRig/TVTestRigFixture/Models/FixtureRecipe.swift`: seven archetypes, explicit
  theme vocabulary and source-defined element limits.
- `Docs/Testing/2026-09-20-simulator-navigation-map.md`: six transitions completed,
  but post-teardown `/scene` failed and Fixture crashed. Foreground return and runner
  stop are not proof of healthy Fixture state. This does not establish that ordinary
  fixture harvesting has the same defect; qualify its actual path independently.

Read the relevant source contracts before operation. Do not run `simulator diagnose`
or Settings mapping as a shortcut for fixture-only preflight: those mutate navigation
and are outside this lane. Fixed delays and command success alone do not prove settled
focus. Prediction files are diagnostics, never trusted annotations. Simulator rendering
does not establish physical Apple TV shaders/parallax or device performance.

## Shared outputs and evidence

Use new versioned locations, never existing corpus output directories:

- Raw bundles and full-frame derivatives: `dataset/tvos_captures/simulator/<corpus-id>/`.
- Focus crops/manifests: `dataset/focus_ring/simulator/<corpus-id>/`.
- Recipes, configuration and runtime reports: `reports/work/SIM-DATA-<nn>/` and
  project-local runtime/cache paths explicitly resolved at dispatch.
- Handoffs: `reports/work/SIM-DATA-<nn>/handoff.md`.

Verify data paths are gitignored before generating. Do not add raw data or model weights
to source control. Use relative artifact paths, hashes, complete membership, explicit
source kind and lineage. Reject traversal, symlink escapes, output collisions and
unknown versions. Archive success, rejected and invalid trials separately. Preserve
producer bytes; derived manifests never rewrite receipts or manufacture provenance.

Each handoff maps every acceptance criterion to commands, exit codes, reports/hashes
and limitations. Report software verified / data eligible / integration qualified /
model gate passed separately. Model gates are not assessed throughout this lane.
Fixture tests can qualify software, never genuine capture or complete datasets.

## SIM-DATA-01 — Independent local producer runtime

**Parent:** TASK-SIM-DATA-01. **Inputs:** pinned producer source, approved existing
local artifacts, read-only runtime inventory. **Files:** additive runtime manifest,
readiness report and runbook under its report directory; producer edits excluded.
**Initial permitted scope:** bounded read-only inventory and documented setup plan.
Installation and the minimal capture require explicit operation/storage authority.

1. Inventory local Xcode/runtime/device profiles and app/helper/fixture artifacts.
   Resolve one exact simulator UUID and record runtime/build, availability, app/helper
   hashes, fixture build, workspace and endpoint. Never use `booted` or remembered IDs.
2. Select matching producer artifacts; record any missing installation, build, signing,
   or storage prerequisite instead of silently substituting a binary or downloading.
3. Bind explicit fixture HTTP origin and selected simulator. Determine whether another
   listener/session owns the endpoint before mutation. `localhost:8080` is not target
   evidence. A target/endpoint mismatch or ambiguous binding blocks capture.
4. After setup/capture authorization, use the existing `fixture batch --simulator-udid`
   path for one bounded minimal recipe and a new output destination. Resolve current
   CLI flags from the matching helper; do not invent an MCP batch command.
5. Record operation lifecycle and validate completion. Check `/scene`, selected target
   and fixture health before and after owned cleanup; preserve unresolved-operation
   markers. Do not call return-to-Fixture restoration of an arbitrary prior context.

**Tests/acceptance:** actual matching helper and minimal recipe work; complete target,
build and endpoint record; healthy postflight; wrong target, missing runtime, endpoint
collision and unknown cleanup stop before capture. Local evidence does not qualify
Sillycon or Office. Inventory alone is a partial result, not SIM-DATA-01 completion.
**Blocker/resume:** exact missing setup authority/artifact or target-binding evidence.
Continue SIM-DATA-02 independently. **Next:** SIM-DATA-03 after both prerequisites pass.

## SIM-DATA-02 — Simulator-aware consumer and dataset contracts

**Parent:** TASK-SIM-DATA-01. **Inputs:** accepted P4-A/FR-A implementations, current
producer contracts and deterministic small image/metadata fixtures. No live runtime.
**Files:** targeted changes to `scripts/harvest_bundle_validation.py`,
`scripts/ingest_fixture_batch.py`, `scripts/harvest_focus_pairs.py`,
`scripts/focus_ring_readiness.py`, `scripts/validate_focus_ring_readiness.py`, their
tests, additive manifest helpers, and a versioned schema under `Research/schemas/`.
Update architecture §6 before introducing the manifest/interface.

1. Document and implement a simulator dataset manifest with schema version, corpus ID,
   source kind, producer/build reference, requested target, observed source metadata,
   original/normalized family and theme, seed, split group, pair/element identity,
   source-relative image/annotation paths and hashes, and validation results.
2. Preserve receipt/index/source-description values and distinguish inspection validity,
   eligibility for this simulator dataset milestone, and physical qualification not
   established. Keep general training/production approval false unless separately
   authorized; a simulator-use result must not accidentally open existing launch gates.
   Missing facts remain unknown. Do not require retired attestation machinery or claim
   descriptive context authenticates hardware identity.
3. Explicitly map source snake_case families/themes to existing NUA values, retaining
   originals; reject unsupported values. Do not widen the producer wire schema unless
   an actual missing field is escalated to its owner with a concrete compatibility case.
4. Permit multiple distinct element pairs from one recipe group in the same split.
   Reject duplicate pair IDs and any group/related-seed/content crossing partitions.
   The existing blanket repeated-seed rejection must not reject valid focus sweeps.
5. Integrate extraction through real ingest/extraction entrypoints. Use each frame's
   actual focused/unfocused geometry, 16% expansion and 256×256 crop behavior. Preserve
   crop-to-source lineage and fixture ground truth. Unknown labels are excluded, not
   guessed from detector predictions, filenames, or an absent ring.
6. Derive hard-negative counts from validated unfocused evidence, theme, type and held-out
   membership. A supplied `hardNegative` flag alone cannot pass readiness. Calculate
   theme percentages against actual scene totals, not only minimum quota denominators.
7. Keep visual eligibility independent of optional ADR-0007 alignment metadata. No
   alignment matrix is required for this lane; present metadata must still validate.

**Tests/acceptance:** completed/partial bundles, corrupt PNGs, altered hashes, unsupported
versions, telemetry conflicts, false source claims, missing labels, repeated seeds within
and across splits, duplicate pairs, frame-specific geometry, crop parity, model-derived
labels, output collisions and false eligibility. Include actual CLI/entrypoint integration,
focused tests and required offline Swift build/test checks. Existing supported consumer
formats remain compatible and accepted P4-A/FR-A behavior retains regression coverage.
**Next:** SIM-DATA-03; no software test claims live data eligibility.

## SIM-DATA-03 — Bounded genuine simulator qualification

**Parent:** TASK-SIM-DATA-01. **Inputs:** accepted SIM-DATA-01/02, explicit simulator
capture authority, pinned recipe manifest and runtime record. **Files:** additive
pilot recipes, raw/derived pilot corpus and reports; no producer changes or training.

1. Freeze 42 recipes: seven source archetypes including `kitchen_sink`, three explicit
   themes (`light`, `dark`, `high_contrast`), two pinned seeds per family/theme cell.
   Record exact recipe hashes/configuration before capture; use producer element limits.
2. Precompute expected interactive targets/counts. Capture resting state plus one focused
   state per supported interactive element. Unsupported/unreachable targets remain
   explicit gaps; no fabricated success. Use bounded command deadlines recorded in the
   run configuration, and inspect failures rather than automatically retrying.
3. Record pre/post telemetry, scene/recipe identity, source/target, dimensions, actual
   settled focus and completion receipts. Reconcile expected, captured, accepted and
   rejected counts. Missing support blocks complete matrix coverage.
4. Validate every indexed image/annotation/hash and frame-specific geometry. Inspect
   representative overlays for every family/theme and all flagged anomalies. Check
   focused scaling, clipping and baseline/focused alignment, not just parse success.
5. Validate intake through SIM-DATA-02. Check Fixture health after capture and teardown.
   Retain partial outputs and evidence on failure; never manually promote staging output.

**Acceptance:** genuine simulator bundle(s), complete matrix/count accounting, correct
source labels, verified NUA intake, reproducible recipes, image/annotation alignment,
healthy postflight. This establishes simulator compatibility for the recorded revision
and scope, not physical performance or general model quality.
**Next:** FR-SIM-BASE before SIM-DATA-04 scale-up; secondary SIM-DATA-05 may proceed
without delaying FocusRing, only after architect acceptance of pilot evidence.

## SIM-DATA-04 — Scale and freeze FocusRing simulator data

**Parent:** TASK-SIM-DATA-01. **Inputs:** accepted pilot and FR-SIM-BASE, validated extraction/manifest
interfaces, frozen catalog and partition plan, separately assigned bounded capture.
**Files:** simulator corpus/manifests and scoped recipe/coverage tooling/tests; existing
physical corpora, models and FR-B acceptance remain untouched.

1. Freeze a deterministic 80/10/10 train/validation/test assignment over recipe groups
   before capture; record algorithm, ordering, seed and rounding with membership. All
   focus states, related variants and duplicate content stay in one partition. Do not
   rebalance captured groups to pass quotas. These are recipe-group holdouts, not
   unseen-archetype qualification.
2. Produce at least 6,000 distinct labeled pairs: gridMatrix ≥2,000; mediaShelf ≥1,500;
   settingsList ≥1,000; actionDialog, heroCarousel and focusMaze ≥500 each. Light and
   highContrast each cover ≥20% of actual gridMatrix and mediaShelf totals.
3. Require ≥100 held-out verified hard negatives across light/highContrast ×
   imageView/collectionItem, with all four combinations nonempty and reported. Duplicate
   baselines/crops do not inflate sample support; preserve their grouping and identities.
4. Capture in resumable batches of at most 100 recipes, each with explicit deadlines,
   unique destinations, expected counts and owned cleanup checks. Resume only missing
   planned groups after reconciling prior completion and cleanup. Preserve invalid trials.
5. Run full integrity/crop/coverage/label-source/leakage checks. Freeze immutable membership,
   source-byte hashes, crop lineage, retention owner and verified recovery procedure.
   External backup operations require their own authority; same-checkout copies are not
   independent backup proof.

**Acceptance:** complete quota report, zero cross-partition leakage, valid pair crops,
explicit simulator-use eligibility and preservation evidence. Missing coverage blocks
completion; do not lower quotas. No training or CoreML export. **Next:** dataset handoff;
future model work requires a separate assignment and quality gates.

## SIM-DATA-05 — tvOS detector augmentation corpus

**Parent:** TASK-SIM-DATA-01. **Inputs:** accepted pilot and SIM-DATA-02 interfaces;
the shared frozen source-membership registry used by SIM-DATA-04. Completion of all
6,000 FocusRing pairs is not a prerequisite. **Files:** simulator full-frame corpus,
isolated exports, coverage tooling/tests and intake report; targeted existing exporter
extensions only where necessary under the assigned file scope.

1. Freeze a coverage matrix for supported controls, especially toggles, steppers, sliders,
   segmented controls, menus and collection items. Cover explicit themes and source-supported
   density/layout/typography axes. List unsupported axes/classes as gaps, not assumed support.
2. Reuse qualified frames when appropriate while retaining common lineage and partition
   membership. Two downstream corpora derived from the same frame are not independent
   evaluation evidence. Serialize shared membership changes through one assigned owner.
3. Preserve enclosing/child annotations and explicit taxonomy/category-map versions.
   Unsupported classes are reported; do not silently extend a model's map, remap badge,
   or describe the producer's kitchen-sink catalog as the shipped tvOS model taxonomy.
4. Use existing export infrastructure with explicit inputs and new isolated destinations.
   Validate full-frame geometry, image/label pairs, content hashes, duplicate grouping,
   deterministic output and split leakage. Report per-class instance and scene/seed support
   by split. Dataset counts do not establish a detector-quality threshold.

**Acceptance:** valid paired full-frame corpus, reproducible exports, frozen splits,
class/style coverage and gap report, overlap report with FocusRing data, and a simulator-only
intake receipt. No detector training, production replacement, iOS or physical qualification.

## Maintenance and dispatch completion

Apply current producer guidance rather than historical skill recipes: fixed delays do not
prove settling; `_result.json` is diagnostic; schema selection follows declared version;
simulator pixels are not physical shader evidence. Preserve ADR-0007 and physical FocusRing
requirements. Corrections to protected skills require filesystem authority; if unavailable,
provide an exact proposed patch under the packet report instead of bypassing protection.

SIM-DATA-01 inventory and SIM-DATA-02 offline work can be independently assigned now.
SIM-DATA-01 runtime qualification and SIM-DATA-03/04/05 capture have separate authority
and prerequisite gates. No phase automatically launches another. Workers finish the entire
assigned implementation/integration/test/handoff tranche and keep four outcomes distinct.

Shared status is only for producer/consumer contracts, requests, bundle handoffs and relevant
blockers. Local dataset progress stays in NUA. If the mount is absent, retain relevant
undelivered coordination locally; it does not block software work. Do not recreate the mount
directory or seek SSH. No new producer task is dispatched by this document.
