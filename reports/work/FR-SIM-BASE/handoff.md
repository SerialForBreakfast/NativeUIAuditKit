# FR-SIM-BASE offline evaluator tranche

Implemented `scripts/focus_ring_baseline.py` and deterministic adversarial tests.
The tool binds the shipped compiled FocusRing model by recursive byte digest and
compiled metadata, and reports metrics by family, theme, and control at 0.85 solely
as a fixed shipped-baseline comparison point. It does not set a candidate's operating
threshold: after the complete planned 30-epoch run, FR-SIM-CAND must select that threshold
from validation membership and lock it before reading the final holdout. Missing scores, invalid
membership/model metadata, output collisions, and empty hard-negative support fail closed.

Verification passed:

- `.venv-yolo/bin/python scripts/test_focus_ring_baseline.py` — 3 tests
- `.venv-yolo/bin/python scripts/test_focus_ring_readiness.py` — 7 tests
- `swift build` and `swift test` — passed (90 Swift Testing tests plus 14 XCTest tests)

Outcomes: software verified **passed**; data eligible **not assessed**; integration
qualified **not assessed**; model gate passed **not assessed**. No genuine pilot,
model inference, training, export, capture, or hardware operation occurred.

Runtime acceptance remains blocked on an accepted SIM-DATA-03 pilot and actual
compiled-model inference. The simulator task queue was concurrently marked paused by
the user during this work; do not run that next step until the pause is lifted.
