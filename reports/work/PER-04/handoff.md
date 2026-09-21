# PER-04 physical FocusRing readiness

`scripts/physical_focus_readiness.py` validates a physical-only pair manifest before any
baseline or training stage. It rejects source relabeling, stale callback/frame alignment,
wrong crop dimensions or expansion, recipe-group leakage, and unsupported hard negatives.
An empty physical manifest is reported as `eligible: false, reason: no_physical_pairs`, not as
a passing corpus.

Verification: ` .venv-yolo/bin/python scripts/test_physical_focus_readiness.py` — 3 passed.
Existing `scripts/test_focus_ring_readiness.py` also passes (7 tests), preserving the broader
quota/alignment validator.

| Outcome | Status |
|---|---|
| Software verified | Passed (offline provenance/geometry contract) |
| Data eligible | Not assessed; P4-L has no completed transferred bundle |
| Integration qualified | Not assessed; Office staging access blocks the smoke before capture |
| Model gate passed | Not applicable; FR-B/FR-C remain blocked |

Next unblocked action: producer provides the completed P4-L bundle through an approved accessible
export route; intake then runs the physical readiness check against its real callback and crop
lineage. No Office operation, simulator action, or training occurred here.
