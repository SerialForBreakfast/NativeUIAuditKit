# FOCUS-PAIRED-11 handoff

Assigned retained-pair comparison complete, not a production promotion.
[Results and next decision](results.md).

| Acceptance | Evidence |
|---|---|
| Eligibility/exclusions | artifacts/inventory/inventory.json;513native/9retention/227realcontrol pairs |
| Actual native fixed-window pixels | artifacts/rendered/receipt.json;1702crops,84.22s |
| Matched comparison | artifacts/evaluation-final/result.json;2996exact decision replays; existing frame eligibility preserved |
| Normalization/oracle separation | normalized-growth control; separately named oracle-box-growth |
| Failure analysis/follow-up | artifacts/audit/audit.json; scroll,light,content failures preserved |
| Caller integration | focus_paired_growth.py inventory/render/evaluate; audit_focus_paired.py;7CLI negatives |
| Verification | python-tests.log23pass; swift-build.logpass; swift-test.log134pass |
| Visual QA | sixmatching sheets/all18pairs;4fixed/normalized panels; retention scroll failure |
| Decision | Useful paired signal; movement/context unreliable. No neural fit/export/promotion |
| Peer consequence | coordination.md; existing transfer10coverage request follow-up |

Run from root with project-local TMPDIR and PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts.
All output paths must be new:

```sh
.venv-yolo/bin/python scripts/focus_paired_growth.py inventory --output <new-inventory-dir>
.venv-yolo/bin/python scripts/focus_paired_growth.py render --inventory <inventory.json> --output <new-render-dir>
.venv-yolo/bin/python scripts/focus_paired_growth.py evaluate --inventory <inventory.json> --rendered <receipt.json> --output <new-result-dir>
.venv-yolo/bin/python scripts/audit_focus_paired.py --output <new-audit-dir>
```

Audit is pinned to this experiment, not a live caller. Context/settlement/freshness
flags are offline assumptions, not runtime verification. The scroll failure falsifies
universal stability. Source roles, labels, model and user/prior working-tree changes
preserved. No git writes or device operations.
