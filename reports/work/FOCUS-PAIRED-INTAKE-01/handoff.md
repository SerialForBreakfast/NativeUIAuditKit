# FOCUS-PAIRED-INTAKE-01 — complete for review

Scope: one approved cached paired-learning experiment plus named native100-r2/
native12 receipt, validation and production crop QA. No new capture, encoder
inference, calibration, export, promotion or data admission.

| Acceptance | Observable evidence |
|---|---|
| Research before implementation | Research/Plans/FocusPairedIntake.md; architecture section8; ExperimentLog FDR016 |
| Actual integrated paired execution | scripts/focus_paired_experiment.py + train_focus_ring_detector.py; FDR-016/backend.json, execution.json; one PID82133,30epochs |
| Frozen membership/features/init | FDR-016/protocol-ready.json, comparison.json;363train/9retention pairs+453real crops; original cache SHA rechecked; identical initial predictions |
| Unchanged guards/no cherry-pick | zero eligible epochs; weights contains last.pt only;14,601predictions replayed by existing metrics |
| Complete comparison | FDR-016/diagnostics/report.json, comparison.json;31snapshots, nine paired-retention margins each; Home cases explicitly failed target |
| Named archive receipt/safety | NATIVE112-INTAKE-01/received/receipt.json and qa/input-index.json; bounded safe extraction and source-preservation recheck |
| Native112 intake/compatibility | qa/intake.json records first12unsupported; qa-v2/intake.json records all112mechanical passes; producer-vector tests cover supported v2 subset |
| Production crop/visual QA | qa-v2/review-sheets/inventory.json;28pages/224crops reviewed; three old Library clips held;12repaired bodies enclosed |
| Duplication/protected evidence | pair-dispositions.json:96usable/13duplicates/3holds; hash-only reserved checks, no protected imagery viewed/scored |
| Focused/legacy verification | FDR-016/tests-final.log:60pass, cache/order/approval/rejection/paired-loss and legacy contracts |
| Offline package verification | FDR-016/swift-build-final.log and swift-test-final.log |
| TTR handoff | NATIVE112-INTAKE-01/publication.json: exact receipts and geometry answer read back, other YAML preserved; peer acknowledgment not observed |
| Local status | Tasks,CurrentState,CompletedTasks,ExperimentLog reconciled |

Software passes. Data diagnostic intake passes with explicit exclusions; training
eligibility not granted. Transfer/crop integration passes, not a device qualification.
Model gate fails: no selected checkpoint; shipped unchanged.

Next assignment: geometry-aligned artwork data proposal, not another unchanged
training run. See [model outcome](../FDR-016/handoff.md),
[data outcome](../NATIVE112-INTAKE-01/handoff.md), and
[consumer geometry contract](../NATIVE112-INTAKE-01/geometry-response.md).
