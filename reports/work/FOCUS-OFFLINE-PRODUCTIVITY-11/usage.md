# Offline commands

Run from repository root with `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=scripts` and
`TMPDIR="$PWD/.build/debug-output"`. Supply recorded SHA256 values from each report's
input index; do not silently replace a frozen hash after an input changes. All output
directories must be new and project-local. No command below runs a model.

```text
.venv-review/bin/python scripts/annotation_proposal_filter.py --comparison COMPARISON_JSON --sha256 COMPARISON_SHA --protocol PROTOCOL_JSON --protocol-sha256 PROTOCOL_SHA --output NEW_DIRECTORY
.venv-review/bin/python scripts/focus_decision_report.py --protocol FROZEN_PROTOCOL --protocol-sha256 PROTOCOL_SHA --result SAVED_RESULT --result-sha256 RESULT_SHA --campaign FIRST3_MANIFEST --campaign-sha256 CAMPAIGN_SHA --output NEW_DIRECTORY
.venv-review/bin/python scripts/training_efficiency_audit.py --run-dir NativeUITrainer/yolo_runs/phase6a_r013 --dataset NativeUITrainer/yolo_dataset_41class_r7 --site .venv-yolo/lib/python3.13/site-packages --log NativeUITrainer/training_6a13.log --output NEW_DIRECTORY
.venv-review/bin/python -m unittest test_offline_productivity test_annotation_proposal_comparison test_human_vision_import test_ohem_callback test_human_review_editor_interactions test_ttr_revision2 -v
```

Qt tests use `QT_QPA_PLATFORM=offscreen`; they never operate the user's editor.
Current actual input paths/hashes and output counts are in the generated reports.

Optional consumer-side paired-delivery descriptor (not a new TTR wire format):

```json
{
  "version": "focus-decision-pairs-v1",
  "cases": [{
    "caseID": "an-exact-first3-case-id",
    "manifest": {"path": "project-relative-production-crop-manifest", "sha256": "verified-sha256"},
    "models": [{
      "name": "a-pinned-model-name",
      "protocol": {"path": "existing-baseline-protocol", "sha256": "verified-sha256"},
      "scores": {"path": "existing-baseline-score-envelope", "sha256": "verified-sha256"}
    }]
  }]
}
```

Pass its path/hash as `--delivery` / `--delivery-sha256`. Missing cases remain pending.
No scored descriptor currently exists for the new first3capture; do not generate
predictions from labels or reuse older pairs under these case IDs. Source manifests
must already pass production crop/native binding validation. These outputs do not
admit samples to training or grant inference authority.
