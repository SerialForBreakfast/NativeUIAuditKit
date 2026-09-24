# Review, compatibility and maintenance completion contracts

Revision1,2026-09-23. Status/ownership stays in [Tasks](../../Tasks.md).
Use the [common execution contract](../ImplementationPlans.md#common-execution-contract).
These contracts fill planning gaps; they do not redispatch delivered software or
grant capture, inference, training, external-repository, transfer or Git authority.
Each handoff reports software, data, integration and model outcomes separately.

## Review-ready work

For every review row, compare its existing handoff with the linked acceptance
criteria and actual caller integration. Reuse unchanged tests/hashes; rerun only
checks affected by intervening changes. Record accepted scope and residual gaps.
An architect may accept supported criteria; a worker returns review evidence, not
self-acceptance. Do not rerun models/capture to review offline software. Missing
evidence blocks that criterion only; follow the named successor instead of reopening
the implementation. A failed model experiment can be accepted as a completed
experiment without accepting its model for deployment.

## REPO-CLEANUP-20260923

**Inputs:** current read-only Git status/diff, .gitignore, artifact policy, retained
cleanup commands and r6 inventory. **Files:** ignore rules, concise report indexes,
tests for artifact-independent fixtures, maintainer command document. No deletion,
de-indexing, staging or Git writes in this assignment.

1. Treat the previous94-path command list as a snapshot, not a current commit list.
   Reconcile tracked/untracked changes and distinguish code, concise evidence,
   generated bulk artifacts, sensitive paths and pre-existing worker ownership.
2. Check representative generated weights/corpora/logs with `git check-ignore` and
   tracked-file inventory. Ignore rules do not untrack existing files. Preserve raw
   evidence; propose exact maintainer-only removals from the index separately.
3. Verify tests do not depend on gitignored live reports; use deterministic fixtures.
   Produce an exact reviewed file list and commands for the maintainer, excluding
   unrelated work and explaining recoverability before any proposed removal.

**Tests/acceptance:** diff whitespace, ignore behavior for generated versus intended
source, referenced evidence availability, no dataset/checkpoint accidentally proposed
for commit. If code changes, focused tests and offline package checks. If docs only,
link/content checks suffice. **Blocker:** unknown ownership or retention target stops
that file's cleanup. **Next:** maintainer reviews commands; no agent commit.

## P2-METRICS

**Inputs:** accepted P2-A, [repair evidence](../../reports/work/P2-METRICS/handoff.md),
actual reference comparator/export integration and r6 class-support report.
**Files:** existing comparator, focused/integrated tests and metric contract only.

Review the delivered correction: absent/null AP is unavailable, never zero; shared
finite keys alone produce deltas. Validate compatible corpus/taxonomy/settings and
metric implementation before comparing. Reject booleans, NaN/infinity, overflow,
invalid completion and duplicate/empty membership. Preserve partial availability
and explicit unsupported-class support. Do not build another evaluator.

**Tests/acceptance:** identical artifacts yield zero, disjoint metrics no delta,
partial support stays partial, corrupted/incompatible artifacts reject through the
actual caller. Reuse14-test and package evidence unless implementation changed.
**Blocker:** incompatible evidence needs corrected provenance, not imputed scores.
**Next:** accepted correction consumed by P1-B/P2-B; no inference in this review.

## TTR-PROVIDER-01

**Inputs:** [FOCUS-RECEIPT-01](FocusExecutionReceipt.md), committed API/migration
example, exact peer package pin and source-backed adapter contract.
**Files/authority:** NUIAK compatibility fixtures, migration notes and scoped
coordination metadata. TTR implementation requires its own assigned owner.

1. Reconcile the old source assessment with the additive receipt now present in
   baseline7588a92. Record separately package availability, peer adoption and live use.
2. Supply deterministic examples for CoreML success, heuristic fallback, disabled,
   load failure, partial/all-failed scoring and unknown custom-model identity.
3. Confirm peer mapping retains actual backend, artifact identity, candidate
   dispositions and selection policy. Old results without a receipt remain unknown,
   not inferred CoreML. Request only evidenced missing adapter behavior.
4. After separate peer assignment and inference authority, compare identical frozen
   inputs and receipt semantics; keep native telemetry as scorer, not model decision.

**Acceptance:** versioned consumer compatibility matrix and source-backed peer
adoption evidence; fake checks do not establish live integration or model quality.
**Blocker:** missing peer revision/acknowledgment blocks live claims, not migration
fixtures. **Next:** FR-SIM-TTR when candidate/comparison prerequisites are satisfied.

## TTR-DIALOG-01

**Inputs:** retained c25fa8fa producer contract, [software handoff](../../reports/work/TTR-DIALOG-01/handoff.md),
current source/build identities and a genuinely completed repaired-dialog bundle.
**Files:** existing ingest, recipe hashing, sidecar-v2 tests, crop intake and local
qualification report. Producer edits and new capture need separate assignments.

1. Review/reuse the closed144-style software contract; preserve null/legacy behavior
   and original source fields. Verify canonical hash vectors and bracket agreement.
2. On authorized delivery, verify transferred hashes, all indexed bytes and labels,
   observed focused/unfocused bounds, clipping/long-label rendering and production
   crops. Preserve rejected trials and distinguish parser success from visual truth.
3. Join seed/style siblings across all prior data; classify development versus
   reserved evaluation from source history, not a new style or filename.

**Tests/acceptance:** legacy vectors, unknown fields/versions, changed hashes,
conflicting brackets, missing pixels, false labels and cross-split siblings reject
through actual ingest/crop callers. Software may pass independently; genuine intake
requires a byte-bound visual review and exact producer scope.144 offline combinations
are not144 captured styles. **Blocker:** absent/invalid bundle leaves integration
open. **Next:** APPEAR-EVAL-RESERVE if genuinely untouched membership is supported.

## TTR-CATALOG-01

**Inputs:** retained [two-control smoke](../../reports/work/TTR-CATALOG-01/smoke-0514/handoff.md),
[catalog/appearance contract](CatalogAppearanceQualification.md), exact source/build
pins, supported-control exclusions and retained completed-job exports.
**Files:** NUIAK intake/coverage reports and targeted compatibility tests only.

1. Reconcile existing smoke/catalog/appearance evidence before any operation. Record
   the tested chunk-export workaround separately from the signed export CLI defect.
   Reuse verified completed output, not duplicate captures to bypass export failures.
2. Audit catalog membership: eight real sample controls are not41 supported classes;
   preserve the33 placeholder exclusions. Reconcile expected/actual counts, crop
   geometry and visible theme differences against the already delivered APPEAR-C data.
3. Keep optional Top Shelf live qualification separate. Before an assigned bounded
   check, freeze expected artwork seed/hash, target, observation/label source and
   postflight procedure. Seeing artwork alone establishes neither Home focus labels
   nor independent model-evaluation membership. No Home navigation by this plan.

**Acceptance:** exact-build compatibility/rejection matrix, complete source/exclusion
accounting, qualified original-scope intake and separately marked untested features.
Unknown current runtime health stays unknown. **Tests:** reuse unchanged v2/crop
checks; add targeted tests only for an actual contract change. **Blocker:** absent
Top Shelf execution authority blocks only that optional check, not appearance intake.
**Next:** missing source coverage goes to APPEAR-EVAL-RESERVE; formal pilot gaps stay
TVGEN-03/SIM-DATA-03, not silently closed by a two-element or catalog smoke.
