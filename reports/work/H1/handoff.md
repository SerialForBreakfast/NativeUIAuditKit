# H1 handoff — source-pinned harvest compatibility contract

**Status:** Review-ready. **Packet:** H1, revision 4. **Parent:**
TASK-INTEGRATION-01. **Completed:** 2026-09-19.

## Outcome and changed paths

H1 records a source-pinned offline consumer contract for the current TVTestRig
harvest format. It distinguishes bundle integrity from provenance and training
eligibility, defines deterministic positive/negative cases for P4-A, and adds a
copyable producer-owner brief. It does not create a bundle, run a producer
script, access hardware, or change TVTestRig.

Changed paths:

- `Research/TVTestRigIntegrationContract.md`
- `Research/schemas/harvest-compatibility-v1.md`
- `Tasks.md`
- `reports/work/H1/handoff.md`

Base NUA revision: `96e4b0e83229ab0578b830262dea839930a89264`.
NUA working tree was already dirty with untracked `reports/coordination/` before
this packet; it was not inspected, changed, or claimed by H1. Producer snapshot:
TVTestRig `586050e043bddd742c701963650e2fc5815afe36`, observed clean.

## Acceptance evidence

| H1 acceptance condition | Result | Evidence |
|---|---|---|
| Exact schema/version references trace to source | PASS | Contract names the producer commit, exact index/receipt/coordinate/provenance identifiers, artifact layout, field requirements, validator limits, and source paths. |
| Deterministic cases have expected results | PASS | `H1-positive-v1` and ten negative cases are defined in `Research/schemas/harvest-compatibility-v1.md`. |
| Positive offline case cannot assert eligibility | PASS | Every case is explicitly ineligible; the positive case retains `unverified-pixel-telemetry-binding` and no identity attestation. |
| No external/live changes | PASS | TVTestRig was read-only; no producer command, app, device, or hardware action ran. |
| Open questions are bounded | PASS | Missing exported taxonomy version and serialized identity are confined to named cases and P4-L/TV-I1 follow-up. |

## Verification

| Command | Exit | Result |
|---|---:|---|
| `git -C /Users/josephmccraw/Documents/GitHub/TVTestRig rev-parse HEAD` | 0 | `586050e043bddd742c701963650e2fc5815afe36` |
| `git -C /Users/josephmccraw/Documents/GitHub/TVTestRig status --short` | 0 | No output (clean producer checkout). |
| Read-only source/document inspection of engine, index, receipt, validator, and identity definitions | 0 | Extracted contract facts are recorded in the schema document. |
| `git diff --check` | 0 | No whitespace errors. |
| `rg` content/link review for H1 references | 0 | Contract and task link targets resolve within NUA. |

This packet changes documentation only. No runtime code changed, so no focused
behavioral test or Swift build/test was required by the worker workflow.

Evidence-file SHA-256 values from the final review:

- `Research/schemas/harvest-compatibility-v1.md` — `a52b1532f58f82e2817efc935102b8f05b57b50ee69d31b17e266d310554e5f7`
- `Research/TVTestRigIntegrationContract.md` — `35fed611cec1a24bff3cb4e5e65dbb0d3b7f1fd6e052625d0f2c29b20ee67dd4`

## Separate outcomes

| Outcome | Status | Reason / evidence |
|---|---|---|
| Software verified | PASS | Source-derived contract, result envelope, and deterministic consumer cases are complete for P4-A implementation. |
| Data eligible | FAIL | No genuine pixels/provenance; the defined positive is test-only and explicitly unverified. |
| Integration qualified | FAIL | No bilateral producer acceptance, shared identity attestation, or genuine completed bundle has been validated. |
| Model gate passed | NOT APPLICABLE | H1 has no model evaluation or release gate. |

## Risks, blockers, and continuation

- P4-A may implement the offline consumer validator against this source-pinned
  contract. Its positive fixture must use real decodable non-user PNG bytes and
  a complete receipt/index; existing loose parser mocks do not meet that bar.
- A producer change to identifiers, coordinates, split vocabulary, provenance
  semantics, or required fields needs a new compatibility case and review.
- P4-L remains blocked on a genuine completed bundle and shared identity
  evidence. Do not infer either from a passing offline fixture.
- Producer owner brief is at the end of
  `Research/schemas/harvest-compatibility-v1.md`; bilateral acceptance must be
  recorded only after actual feedback.
