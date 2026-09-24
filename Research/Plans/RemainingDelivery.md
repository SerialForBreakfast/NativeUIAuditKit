# Remaining delivery contracts

Revision 1, 2026-09-22. This closes gaps in the full-backlog catalog; it is not a
second queue. [Tasks.md](../../Tasks.md) alone records state and ownership.
Existing detailed contracts remain canonical for their packets. Accepted software
is reused, not reimplemented. Existing active assignments retain their owners.

## Common dispatch and acceptance

Every section below inherits the [execution contract](../ImplementationPlans.md#common-execution-contract):
named owner/repository, current inputs, explicit operation authority, project-local
outputs, focused adversarial tests and one integrated offline Swift build/test for
code changes, criterion-by-criterion handoff, four independent outcomes and exact
next action. Prose-only work uses content/link/diff checks. No capture, inference,
training, external edits, installation, backup transfer or promotion is authorized
by this document. Each is separately named at dispatch. A plan is not peer assignment.

Use `reports/work/<packet-id>/handoff.md` for evidence; include revisions/hashes,
commands/exit codes, test/capture/intake/external-wait durations and retained failures.
Completion means the assigned integrated deliverable, not a helper. Stop only the
affected branch on missing authority, data or a demonstrated failure. No unchanged
live retries or automatic experiment loops. Requests are metadata, not executable orders.

## TV-FIX — Native Fixture focus identity repair

**Repository/parent:** TVTestRig / TASK-INTEGRATION-01. **Inputs:**
[two-lane failure](../../reports/work/TVGEN/handoff.md), request
`nuiak-20260922T061302Z-fixture-nonview-focus`, current producer source and build.
**Scope/authority:** external proposal; producer-owned native probe/identity resolver
and tests only after acceptance in TTR. NUA does not patch or build the producer.

1. Reproduce reference success versus first actual target's `non_view/unmapped_item`.
   Inspect ProceduralSceneView probe and FocusSweepController; distinguish missing
   identity from geometry (both button rectangles exist, missingIDs is empty).
2. Bind actual native focus item to stable Fixture element independently of requested
   focus. Preserve unknown/unmapped rejection, fresh generation and settled layout.
   Do not replace identity with requested IDs, nearest boxes or model predictions.
3. Test reference → each dialog button → reference, including non-UIView items,
   stale generation, wrong/removed element, absent focus and callback/layout changes.
4. Return source/build hashes and observed-state evidence; if runtime tests are
   separately authorized, exercise the actual installed Fixture and postflight.
   Report any remaining screenshot/export failure separately rather than hiding it.

**Acceptance:** independently observed identity for reference and both targets,
negative cases fail closed, no intent-derived labels, matching artifact instructions.
**Next:** TVGEN-02 direct qualification and SIM-DATA-01 TTR smoke, serialized.
If native binding requires a different Fixture design, return that bounded proposal;
do not silently fork Fixture or make a second general-purpose rig.

## TVGEN-01 — Reuse and runtime design review

**Inputs:** ADR-0009, ParallelTVOSAcquisition, delivered inventory/handoff and current
installed artifact hashes. **Files/authority:** read-only source/runtime inventory;
NUA plan/report corrections. No capture or installation for review.

Check that direct call graph uses only Fixture HTTP and exact-UUID simctl, output
paths are isolated, source/build/runtime identities are separate, and listener PID
maps to the selected installed bundle. Reconcile current evidence against the original
source pin without claiming binary/source identity from a checkout hash alone.
Review bounds/timeouts, recipe serialization and owned cleanup; name any missing
installation/runtime permission. Preserve the current runtime rather than restarting it.

**Acceptance:** source-backed reuse design, recorded authority and exact target
selection, no hidden TTR desktop dependency; architect disposition of delivered design.
**Next:** TVGEN-02; review does not qualify pixels.

## TVGEN-02 — Complete direct runner admission and native smoke

**Inputs:** delivered direct runner/v1.4 adapter/tests, TVGEN-01, TV-FIX artifact for
live qualification, frozen two-element catalog. **Files:** direct_tvos_capture.py,
direct_focus_manifest.py, focus_dataset_contract.py, focus_runtime.py,
focus_ring_baseline.py, focus_corpus_overlap.py, corresponding tests/contracts.
**Authority:** review/remediation can run offline now; live portion requires exact
target/endpoint/installed Fixture launch and runtime-storage scope in assignment.

1. Review real CLI paths and address demonstrated gaps, not rewrite accepted crops
   or training. Verify planning cannot mutate simulator, new-only output behavior,
   five-second HTTP/ten-second settling/two-minute recipe bounds and retained failures.
2. Test completed execution as well as early failure; independently reconcile frozen
   expected targets/counts with source-supported controls. A producer list silently
   omitting an element must not yield full coverage. Validate receipt, raw sidecars,
   generation/instance/recipe/focus/geometry across intervals, dimensions and hashes.
3. Audit untrusted source claims, unsupported schema, unsafe paths, altered/missing
   PNGs, stale/conflicting focus, changed target/listener, partial publication and
   crop parity. Keep bracket correlation explicit; no invented atomic frame IDs.
4. Run authorized reference plus both focused captures to a new destination after
   matching repair evidence. Inspect actual focus effect, measured focused/unfocused
   bounds, clipping and production 16%-expanded 256×256 crops. Require healthy
   postflight; no reset/retry if ambiguous. Never publish a partial completed receipt.
5. Derive reviewed development-only v1.4; test-only evidence cannot be upgraded.
   Verify full training readiness still rejects it. Record source-specific integration.

**Acceptance:** offline contract/CLI tests plus genuine two-pair visual/byte/label
qualification, or separate software review and exact live blocker. Existing reference
PNG alone does not complete this packet. **Next:** TVGEN-03 without intermediate
handoff when the assigned tranche includes it; TTR failure does not stop direct work.

## TVGEN-03 — Full development pilot and shipped baseline

**Inputs:** accepted direct smoke, frozen `reports/work/TVGEN/pilot-catalog.json`,
current shipped FocusRing bytes, existing baseline CLI/protocol. **Authority/files:**
explicit 42-recipe capture and inference assignment; new gitignored raw/crop outputs,
reports and targeted runner fixes only. No scale, training or final-test tuning.

1. Freeze expected supported targets from pinned source for seven archetypes ×
   three explicit themes × seeds7/19, regular density/step0. Catalog counts are
   already frozen. Record unsupported/unreachable cells as gaps, never shrink success.
2. Capture reference and every supported focused target, serialize against TTR,
   preserve all trials and reconcile expected/captured/rejected/accepted counts.
   Inspect every family/theme and flagged anomaly, including scaling/clipping.
3. Audit all bytes, annotations, native interval binding and production crops;
   group recipes/related variants/duplicates as development across both lanes.
4. Prepare and execute existing shipped-CoreML baseline with pinned artifact,
   preprocessing and fixed comparison point0.85. Report misses, FPR/FNR, precision/
   recall, abstentions, failed inference, theme/control support and cold/warm latency.
   Test-only CoreML results are not the pilot baseline. Retain zero-support gaps.
5. Rank measured failures and freeze a proposed scale catalog/evaluation protocol.
   Keep final evaluation independent of known failures; no collection at scale yet.

**Acceptance:** all42 recipes accounted for, reviewed genuine membership and complete
reproducible baseline, or explicit unsupported cells blocking full-pilot acceptance.
**Next:** satisfy FR-SIM-BASE with this same evidence (no duplicate inference), then
TVGEN-04; later TTR pilot is incremental compatibility/coverage, not a mandatory
second42-recipe run when existing evidence is reusable.

## TVGEN-04 — Qualified direct scale corpus and training handoff

**Inputs:** TVGEN-03/FR-SIM-BASE, frozen capture-plan interface, production crops,
full training preflight, cross-source ledger; explicit scale assignment.
**Files:** existing capture-plan/quota/consumer/readiness tools and focused tests,
isolated raw/crop/manifests. No new trainer; no candidate launch.

1. Before capture, freeze recipe-group80/10/10 partitions, exclude development
   seeds7/19 and related variants from final evaluation, and bind both producers to
   the same ownership ledger. No quota repair by moving captured groups across splits.
2. Add a separately versioned scale manifest/admission path with actual corpus-review
   evidence. Do not relabel development-only v1.4 as trainable or loosen its validator.
   Bind existing trainer/preflight to this reviewed contract; test false approvals,
   missing classes/strata, changed hashes, duplicate pairs and cross-lane leakage.
3. Collect resumable unique-destination batches≤100 recipes, bounded operations;
   validate completion/health before next batch and inspect previous failure before
   resuming missing groups. Preserve raw bytes and crop lineage, including rejects.
4. Require≥6,000 distinct pairs: gridMatrix≥2,000; mediaShelf≥1,500;
   settingsList≥1,000; actionDialog/heroCarousel/focusMaze≥500 each.
   Light and highContrast each≥20% of actual gridMatrix and mediaShelf totals.
   Test hard negatives≥100; all four light/highContrast×imageView/collectionItem
   combinations nonempty, labels from verified unfocused evidence.
5. Full final integrity/decoded-duplicate/leakage/coverage audit; immutable content
   manifests and DATA-RET retention evidence. Execute configuration-only preflight
   with local weights and isolated candidate outputs, not training.

**Acceptance:** complete quotas, qualified source-specific membership, zero cross-split
leakage, reviewed scale schema and truthful launch eligibility. Missing cells remain
remaining work, never lowered thresholds. **Next:** separately authorized FR-SIM-CAND.
SIM-DATA-04 is the alternative TTR acquisition implementation of these same corpus
requirements, not a demand for a second independent6,000-pair corpus. TTR additions
must pass common membership audit. SIM-DATA-05 full-frame exports stay separate.

## DATA-RET — Corpus retention and recovery verification

2026-09-23 implementation slice: `scripts/corpus_retention.py` provides a versioned,
content-sealed full-tree inventory, read-only copy verification, and new-only
project-local restoration. Inventory/restore includes annotations, manifests and
rejected-trial evidence, not just PNGs. All members are regular files; symlinks,
unsafe paths, changed bytes, incomplete copies and output collisions fail closed.
An inventory is not a backup. A same-volume restore is a procedure drill only;
independent backup qualification requires a maintainer-selected destination and
separate copy authority. Initial real scope is the preserved iOS r6 prefix, not
a claim of final corpus readiness. No source deletion or overwrite operation exists.
Observed Finder `.DS_Store` churn may be excluded only with the explicit
`--exclude-finder-metadata` inventory option. Record that exact auxiliary name and
observed excluded paths in the sealed inventory; never exclude arbitrary unknown
files, symlinks, corpus manifests, annotations or images. Verification and restore
then cover all declared corpus content, not Finder metadata. Preserve failed strict
inventory evidence and original files; this does not alter corpus admission gates.

**Parent:** TASK-DATA-01 and FocusRing corpus qualification. **Inputs:** actual corpus
manifests, export/source dependency inventory, storage sizes and maintainer-selected
retention owner/destination. **Scope:** NUA inventory/verifier/runbook and tests;
external backup writes need an exact separate approval or maintainer execution.

Map raw sources, exports, symlinks, annotations, derived crops and weights to their
dependencies; identify which paths are disposable and which are the only copy.
Write a content-hashed retention manifest and immutable version policy. Estimate
space, prepare bounded copy/restore commands and collision checks; never delete or
overwrite sources. Verify a restore into a new project-local directory against
the recorded hashes, annotations and split manifest. A sample restore tests the
procedure, not full backup completeness; verify the entire backup inventory before
claiming corpus recovery coverage. Record owner and future verification trigger.

**Tests/evidence:** missing member, changed bytes, broken dependency, partial backup,
output collision and restore hash checks; report exact covered corpus versions.
**Acceptance:** verified independent copy/restore evidence or explicit external-copy
blocker, not “another folder in this checkout is a backup.” **Next:** corpus acceptance;
the existing P0-C/TVGEN-04 retention criteria consume this evidence, not a second audit.

## IOS-COV — Reconstruction coverage and 41-class qualification decision

**Parent:** TASK-DATA-01/TASK-6a-10. **Inputs:** completed P0-C r6 configuration,
seal/coverage/lineage in [the r6 handoff](../../reports/work/IOS-R6-20260923/handoff.md),
frozen41-class mapping and retired web renderer evidence. Preserve r5 failures as
history, not current membership. **Scope:**
NUA coverage/gate decision and a bounded native-generation proposal, no runtime or
taxonomy modification without a separately assigned implementation.

Enumerate actual per-class train/validation/test support and withheld families;
report `webContent` absent, not detected with AP0 or silently removed from the map.
The r6 starting support is39/41 train,12/41 validation and13/41 test; training also
lacks dynamicIsland. Enumerate every missing validation/test class explicitly from
the sealed coverage report, not only those two training gaps. Review diagnostic
baseline use separately from all-class training/qualification. Any proposed addon
must declare native-renderable class/family targets, exact quotas, source groups,
coordinate/semantic evidence and preserved evaluation exclusions before capture.
Determine which current gates cannot be assessed and distinguish valid partial
baseline reporting from launch/ship eligibility. Specify a deterministic native
replacement design if meaningful ground truth can be produced, with coordinate,
rendering, variety and family-isolation tests; otherwise request a documented
milestone decision. Do not revive failing WKWebView capture or fabricate web labels.

**Acceptance:** every unsupported class/gate named, remediation or maintainer choice
explicit, frozen IDs unchanged and no unilateral gate reduction. **Next:** approved
targeted generator assignment or P5-B with the reviewed coverage decision. P0-C's
16,940 target and current owner remain untouched by this planning packet.

## PER-DATA — Reviewed real perception benchmark

Assigned bounded local review, 2026-09-22: re-use the 44 hash-bound triage members.
Annotate only visually supported non-sensitive examples; preserve privacy exclusions
and missing relations. Legacy native screenshots are neither Fixture nor test-only
images: introduce an explicit `reviewedNativeCapture` source with mandatory
development partition, unknown historical source/journey evidence, reviewedVisual
origin and trainingEligible=false. This admission is local development only. All
legacy members share one conservative unknown-journey group. Do not invent a
physical identity or native focus callback. Visible focus is appearance-only.
Settings management text remains privacy-blocked pending maintainer review; do not
silently redact/modify originals. Report unsupported gold cells explicitly and
exercise actual byte verification without fabricated model predictions.

**Parent:** TTR-PERCEPTION. **Inputs:** accepted PER-01 software/rubric, supplied44-image
audit, missing-evidence matrix, permitted source captures. **Files/authority:** NUA
labels/manifests/review reports and validator tests; no capture unless explicitly added.

Privacy-screen existing leads; keep originals unchanged and quarantined when rights,
identity or semantic truth are uncertain. Hand-review visible chevron→row and true
dialog→button relations, visibility/clipping and ambiguity; never promote predictions
or infer native focus callbacks. Distinguish informational from destructive intent;
ambiguous text gets unknown. Freeze journey/recipe/duplicate groups, development vs
independent evaluation, reviewer decisions and per-cell support. Request only remaining
evidence through TTR-PER when publication/capture is assigned. Do not enter destructive
confirmations to collect cases; use retained authorized frames or inert fixture replicas.

**Tests/acceptance:** actual validator accepts reviewed image/hash/box relations and
rejects ambiguous unsupported gold labels, changed bytes and split leakage; each required
coverage cell has support or an explicit blocking gap. Existing44 images alone are not
claimed adequate. **Next:** PER-LIVE; known incident frames remain development evidence.

## PER-LIVE — Real chevron/dialog baseline and training decision

**Inputs:** PER-DATA eligible benchmark, accepted PER-02 scorer, shipped model and
fixed evaluator settings; explicit inference assignment. **Files:** existing CLI,
additive reports, only targeted bug fixes; no training or API/category-map expansion.

Execute real entrypoint end-to-end, preserving model/preprocessing/manifest hashes;
report correct-row association, dialog/button/focus errors, misses, false positives,
abstentions, support and latency by platform/theme/control. Separate oracle-box from
end-to-end errors and runtime failures. Compare existing primitives before proposing
new learned outputs. Freeze numeric success/abstention/latency criteria for any
PER-03 experiment before training, with maintainer review where no existing gate
exists; do not invent passing thresholds after results.

**Acceptance:** complete reproducible benchmark and ranked actionable gap decision,
including “insufficient evidence/no training justified” if supported. **Next:** PER-03
only for accepted target/gates/data and separate execution authority; FocusRing work
reuses FR-SIM-CAND/FR-C instead of a duplicate model project.

## TEMP-LIVE — Genuine transition-readiness evaluation

**Inputs:** accepted PER-05 causal scorer/schema and real ordered journeys with
timestamps, arrival times and independently reviewed ready/unstable/unknown intervals.
**Authority:** scoped annotation/inference; new capture and TTR changes separately assigned.

Freeze whole-journey splits and development policy before final evaluation; cover
crossfade, scrolling, focus animation, static screens and background carousels.
Use only information available at the decision time. Score premature-ready, delayed
ready, abstention, wait duration and timeout by condition; do not treat continuing
background animation as permanent transition. Exercise replay through actual adapter,
including missing/reordered frames, stale focus and changed screen epoch.

**Acceptance:** real report with support and causal checks, no fake timing or unsupported
generalization. Missing independent journey truth blocks qualification, not reuse of
accepted software. **Next:** TTR-PER policy integration proposal; no sequence model
without a separate evidence-backed architecture/training decision.

## ID-LIVE — Genuine screen and row identity evaluation

**Inputs:** accepted PER-06/schema, registered reference screens and reviewed queries
with changed values, scrolling, duplicate labels, overlays and supported locales.
**Authority/files:** scoped benchmark annotation/evaluation and reports; no navigation.

Freeze journey/reference relationships and independent evaluation; mark absent or
ambiguous rows unknown. Run existing anchor/identity adapter, test stale epoch and
reference invalidation, and quantify false reuse, missed reuse and abstention with
latency/support. Include unsupported locales as abstention tests, not successful
localization coverage. Keep gold screen identity independent from filename intent.

**Acceptance:** reproducible real-reference/query report and invalidation cases;
document where route reuse remains unsafe. **Next:** TTR-PER consumer integration,
not an automatic identity model or native-navigation authorization.

## R-LABEL — Trustworthy physical holdout annotations

**Parent:** TASK-6b-R-1/TASK-6a-11. **Inputs:** R-A/R-B qualified screenshots and frozen
taxonomy, approved labeling scope. **Authority/files:** labels/review manifests only;
no capture, training, relabeling from predictions or raw-image modification.

Define box/occlusion/partial-element rubric and reviewer adjudication; label visible
supported elements, retaining uncertain examples separately. Verify coordinate/scale
and per-class support against images, freeze hashes and whole-journey splits.
Track screenshot-count completion separately from annotation completion. Qualify
quantitative use only for the reviewed subset and identify remaining unlabeled cells.

**Acceptance:** image-aligned reviewed boxes, reproducible complete membership for
declared labeled scope, no leaked training/benchmark overlap. **Next:** R-C mAP
report; without this, R-C may report capture coverage/latency only.

## DATA-VIS — Controlled visual-state coverage

The source-backed inventory and bounded follow-on contracts are in
[VisualStateCoverage.md](VisualStateCoverage.md); measured prefix/probe evidence is
in [the inventory handoff](../../reports/work/DATA-VIS-20260923/handoff.md).

**Parent:** dataset quality across iOS and tvOS; lower priority than usable focus.
**Inputs:** IterationEfficiency coverage goal, actual generator controls and corpus
audits. **Scope:** NUA coverage matrix/planning and targeted generator tests when
assigned; producer feature changes remain proposals, not edits.

Inventory every relevant controllable visible axis as verified/planned/unsupported/
intentionally-fixed. Prioritize focus/geometry/control states, themes, enabled/selected,
loading/error, text/locales, density/type size, clipping and then clock/connectivity/
charge/charging. Battery health is not a status-bar label. Use deterministic independent
schedules and targeted boundary/pairwise combinations, not an exhaustive Cartesian
product. For each implemented axis hold unrelated state fixed and verify both pixels
and sidecar; test plausible combinations and split grouping. Extend only assigned
families without destabilizing active P0-C or TVGEN captures.

**Acceptance:** source-backed matrix, prioritized bounded generator changes, actual
render evidence for any claimed implemented axis, no unsupported completeness claim.
**Next:** versioned targeted data additions after the current corpus, not a new gate
blocking today's qualified baseline or a reason to discard completed captures.

## DATA-SIM — Near-duplicate similarity feasibility

**Inputs:** accepted exact-pixel/lineage audits and approved small sample corpus;
optional Vision feature-print experiment requires explicit inference authority.
**Scope:** offline research/diagnostic report, no corpus deletion or automatic filtering.

Evaluate whether image-distance screening identifies leakage beyond exact hashes.
Include intentional near-identical focus pairs, different controls/styles, related
recipes and real duplicates. Pin preprocessing/runtime and measure false merges,
misses and cost; compare against exact hashes plus lineage. Calibrate on development
only. Recommend review-only clustering or no adoption; no universal distance threshold
is assumed. If adopted later, keep pair units intact and version/re-evaluate changed
memberships; distance alone does not establish label correctness or model improvement.

**Acceptance:** measured trade-off and go/no-go decision, originals/membership unchanged.
**Next:** separately reviewed implementation only if benefit is demonstrated. This
is deferred and does not block direct pilot, scale or current training gates.

## ALIGN-A — Semantic alignment contract and offline policy

**Parent:** ADR-0007 deferred semantic work. **Inputs:**
[ADR-0007](../ADR-0007-VoiceOver-Navigation-Focus-Alignment.md), existing optional
alignment validator, actual producer metadata capability. **Scope:** source-backed
contract/policy tests; external feature needs are proposals. No visual-model changes.

Distinguish visual focus, navigation focus and VoiceOver cursor; require explicit
interaction mode and expected-versus-intentional-bug relation before scoring mismatch.
Cover directional alignment, VoiceOver exploration/traversal, intentional fixture
fault and absent producer state. Unknown stays notAssessable; expected VoiceOver
decoupling is not a detector error. Reuse accepted envelope tests, add only genuine gaps.

**Acceptance:** exact required source fields, compatibility/missing-field behavior and
deterministic policy examples; no fabricated cursor identity. **Next:** ALIGN-B only
after producer support and dedicated operation authority. Never gate visual-only work.

## ALIGN-B — Semantic dataset qualification

**Inputs:** ALIGN-A, producer-supported actual cursor/navigation observations, approved
fixture matrix and explicit operation/accessibility-setting scope. **Scope:** bounded
separate corpus/evaluation; no implicit Settings mutation or visual-training reuse.

Capture approved matrix with observed states and expected relation, preserve time/
frame correlation and settings restoration/health evidence within authorized scope.
Separate intentional faults and expected decoupling from actual mismatch. Group whole
journeys, validate source/labels and score policy against independent truth.

**Acceptance:** all required matrix cells genuinely supported, unknown state excluded
from positive claims, immutable semantic corpus and policy report. Missing producer
metadata blocks this lane only. **Next:** separately owned TTR alignment integration.

## HIST-B — Maintainer history disposition

**Inputs:** HIST-A impact/recovery assessment and missing-object diagnosis; explicit
maintainer decision. **Owner:** maintainer, not an agent git-writing assignment.

Choose documented defer or reviewed remediation. Before rewrite require recoverable
refs/objects, verified backup, affected-clone/remote inventory and migration notices.
Execute only exact authorized maintainer procedure; verify resulting refs/artifact
removal without reproducing sensitive values. Record rollback/reclone instructions.

**Acceptance:** signed-off defer decision or verified remediation/migration evidence.
No force-push, missing-object guessing or destructive recovery from this plan.
**Next:** close history parent only on its actual maintainer disposition; no model
or software release waits on history work unless a separate policy explicitly requires it.
