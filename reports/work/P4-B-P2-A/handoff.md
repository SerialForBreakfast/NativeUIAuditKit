# Combined P4-B / P2-A software tranche

**State:** review-ready, 2026-09-19.

P4-B delivers deterministic split-safe corpus assembly: source/split provenance is retained,
cross-split duplicate content or family reuse fails, calibration/held-out are isolated, and
coverage/class-weight inputs are training-only. P2-A delivers strict completed prediction
artifact compatibility validation: corpus, labels, taxonomy, settings and membership must
match before aggregate deltas are calculated; timestamps do not affect the stable input hash.

| Outcome | P4-B | P2-A |
|---|---|---|
| Software verified | PASS — deterministic and leakage tests pass | PASS — zero-delta and incompatibility tests pass |
| Data eligible | FAIL — toy records only | FAIL — synthetic artifact records only |
| Integration qualified | N/A | N/A |
| Model gate | N/A | N/A |

P4-B's real assembly/P5-B remains blocked on eligible corpora. P2-B remains blocked on P1-B.
