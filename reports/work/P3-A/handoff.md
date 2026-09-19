# P3-A handoff — deterministic regression selector

**State:** review-ready (2026-09-19)

Implemented `synthetic-regression-v1` and an inference-free selector that freezes
deterministic ordering from seed 42 and family/class/aspect/small-element metadata.
Every selected member carries source split, platform, family, dimensions, and image/
label hashes. It rejects missing pixels/labels and train/val source, content, or family
leakage; unavailable class coverage is reported explicitly.

| Outcome | Result |
| --- | --- |
| Software verified | PASS — repeatability, coverage-gap and missing/leakage tests pass. |
| Data eligible | FAIL (expected) — toy artifacts only. |
| Integration qualified | N/A |
| Model gate passed | N/A — no inference. |

P3-B remains blocked on eligible P0 corpus and compatible real prediction artifacts.
Next substantial unblocked work: P4-B split-safe assembly software.
