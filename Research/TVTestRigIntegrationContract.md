# TVTestRig / NativeUIAuditKit integration work contract

**Revision:** 4, 2026-09-19. **Status:** NUA coordination proposal and verified source observations; not bilateral acceptance or a claim of live compatibility. H1/P4-L below are canonical independent packets using the ImplementationPlans common contract. TV-I1/TV-I2 are separately specified in [consumer packets](Plans/ConsumersAndRelease.md); their execution belongs to TVTestRig.

## Verified starting point

Read-only inspection of adjacent TVTestRig HEAD `586050e` and `Docs/Testing/harvest-bundle-validation.md` documents:

- Bundles stage in `.NAME.partial-UUID` and publish by exclusive rename; rejected/cancelled partials are retained and must not be ingested or manually promoted.
- An offline validator checks receipt/index versions, paths, byte counts/hashes, decoded PNGs, bounds, focus identity, and split consistency. Its passing result still reports `provenance: "unverified"` and `approvedForTraining: false`.
- Producer-side offline regression cases include malformed PNGs, aborted receipts, unknown versions, changed bytes, traversal, symlinks, stale focus, wrong split, missing pairs, duplicate index, and invalid bounds.
- Shared HTTP/IPC identity attestation is still a separate production gate. This inspection did not execute the validator or its tests.

Relevant producer sources now live under `TVTestRig/TVTestRig/SyntheticFactory/` relative to that repository: `FixtureBatchHarvestEngine.swift`, `HarvestBundleValidator.swift`, `HarvestIdentity.swift`. Verify the revision/working-tree content when assigned; historical consumer references used a different nesting assumption.

## H1 — Pin the current compatibility contract

**Parent:** TASK-INTEGRATION-01. **Scope:** NUA documentation plus tiny offline test-fixture definitions. **Dependencies:** Read access to producer implementation/docs; no Office, original dataset, inference, or completed identity implementation.

**Files:** This document, a new `Research/schemas/harvest-compatibility-v1.md`, optional additive fixtures under `scripts/testdata/harvest_contract/`, and `reports/work/H1/`. Avoid runtime code edits owned by P4-A. Producer checkout is read-only. Follow AGENTS.md and WorkerWorkflow.md before any fixture-generation code.

1. Record producer source revision and relevant dirty changes; inspect receipt/index/metadata/identity types and validator logic. Extract exact version identifiers and mandatory/optional fields. Do not invent JSON keys or attestations from this proposal.
2. Write a compatibility matrix: producer version, consumer support status, coordinate/taxonomy contract, supported limits, expected error for incompatibility, and what remains unverified. Document whether unknown extra fields are allowed; do not silently accept new required semantics.
3. Define a smallest useful positive offline bundle and negative variants from actual source behavior. If generating local fixtures, use tiny non-user images, stable IDs, deterministic bytes, and explicit test-only/unverified provenance. No copied screenshots or real-data claims. Do not execute producer scripts that write outside NUA.
4. Specify a NUA test-result envelope (a consumer-owned interface, not a producer schema): case ID, producer revision, contract version, consumer revision, integrity pass/fail, provenance state, eligibility false/reasons, and evidence path. Keep machine-specific paths and secrets out of fixtures.
5. Record interface decisions and unresolved questions; produce a copyable producer-owner brief. Source-pinned local agreement is enough for P4-A implementation. Bilateral acceptance is recorded only when actual producer feedback arrives.

**Acceptance:** Exact schema/version references and checks are traceable to source; each test case has a deterministic expected result; positive offline cases cannot claim trusted training eligibility; no external files or live systems changed. Open questions affect named cases rather than blocking unrelated development. Handoff: `reports/work/H1/handoff.md`.

## Proposed producer-owned increments

The canonical producer assignments are [TV-I1 identity coordination](Plans/ConsumersAndRelease.md#tv-i1--authoritative-harvest-identity-coordination) and [TV-I2 offline artifacts](Plans/ConsumersAndRelease.md#tv-i2--reproducible-producer-compatibility-artifacts). The summary below is context, not a second acceptance contract.

These are requests for the TVTestRig owner to consider, not assigned tasks in that repository:

1. **Identity adapter tests:** shared device/run/generation binding across HTTP/IPC; mismatched, stale, missing, and cancelled flows fail closed before capture/mutation as appropriate. Existing offline test adapters remain explicitly non-production.
2. **Contract artifacts:** publish a minimal supported bundle example and expected validator outcome with each format change. Retain negative compatibility cases and document limits/publication semantics.
3. **Hardware qualification:** when identity and Office access permit, obtain one small genuine completed bundle with receipt/index/source revision and attestation evidence through a compliant local export. No scale-up prerequisite for the first consumer check.

NUA returns consumer validation failures at each increment, independently of training. Producer-side build/test commands remain governed by the TVTestRig repo and are not required commands for NUA's offline tests.

## P4-L — First genuine-bundle integration

Separately assigned after prerequisites: compatible P4-A consumer, completed real producer bundle, verified identity evidence, explicit hardware/export authority if operations are needed, and outputs confined to NUA. No live operation is implicit in receiving a bundle.

Validate the small bundle's integrity, source/coordinate/taxonomy contracts, provenance evidence, scene/focus annotation alignment, and split mapping. Record rejection reasons or verified supported behavior. Passing this check establishes compatibility for that producer revision and sample scope, not sufficient class coverage, an eligible full training corpus, or a model-quality gate.

If a producer contract changes, preserve the last-known-compatible fixture and create a new compatibility case. Report a small reproducer rather than asking either project to stop all development. Never work around a partial publication or missing identity by manually constructing a completed/trusted receipt.

**Acceptance/handoff:** source-revision-specific integrity/provenance/annotation-alignment report and explicitly limited compatibility conclusion in reports/work/P4-L/handoff.md. Mark model quality and full-corpus eligibility not established. **Next:** independently assigned larger fixture or FocusRing capture once their own recipes/authority are ready.
