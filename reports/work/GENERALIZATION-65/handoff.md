# GENERALIZATION-65 — frozen diagnostics and approved negative admission

Completed with PREPARED-66; see the [integrated handoff](../PREPARED-66/handoff.md).
No model training, capture or promotion occurred.

| Paired-box success on training scenes | DTM009 | DTM010 | DTM011 |
|---|---:|---:|---:|
| Original |24/24|18/24|24/24|
| Axis ±2% |87/96|73/96|76/96|
| Axis ±6% |43/96|58/96|65/96|
| Diagonal ±4% |0/96|86/96|75/96|

Settings localization is zero for every eligible condition. These are transformed
seen scenes, not independent evaluation. Fifteen pair-condition cells are rejected
for off-frame truth, not clipped. 1,086 model evaluations and174 zero-difference
probes; all87 original predictions match retained baseline evidence.37.927s total.

Every model predicts change on18/48 duplicated training-frame inputs and10/10
duplicated Settings inputs. These are synthetic probes, not semantic action labels.
They expose appearance-driven change predictions without proving a unique cause.

The maintainer approved the exact eight negative additions on2026-10-03. New
admission is32train/5development, original29records unchanged, four boundary no-ops
plus four content-only mutations. Eight pairs form four connected groups; all use
native dark theme. Entire related renderer ancestry stays out of final evaluation.
Native cases were independently rebuilt; model predictions are not labels.

Local artifacts (generated JSON stays ignored):
- `probes.json` SHA256 `d2ccbd6c31a7810c62118d2c6beef27c3cc16b7228e84e92e87c9cb02597edd0`.
- `negative-admission-proposal-verified.json` retains historical unapproved proposal.
- `data-role-decision.json` records explicit human approval, not run authority.
- `admission/corpus.json` file SHA256 `a845ac32662e158a6384cd764a663d13037763f8ae497874ce8f42de9d6044fe`.
- `admission/admission.json` SHA256 `f6c50d6afe11874ecd919f4f325d8339ca6997d7fd09c7ef5eeaa6d8ad0fb0ff`.
- Exact semantic corpus SHA256 `335620b1bf79189e04f50a69f35bbac3c5e2d384784897c176ad32d27f8698bb`.

Preserved initial failed admission log: generic diagnostic reader required unrelated
flags. Replaced with explicit proposal-version/seal/role validation, not relaxed
generic checks. Successful actual admission CLI exit0, receipt readback verified.

Earlier producer coordination ranked genuine no-scroll positives, new geometries
and actual theme diversity; published/read back under existing TRANSFER-62 request.
No new SMB publication was needed for local admission/preparation. Peer acknowledgment
and capture authority remain separate. No Simulator or Office operation occurred.
