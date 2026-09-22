import json
import shutil
import tempfile
import unittest
from pathlib import Path

from focus_ring_baseline import BaselineError, evaluate, model_contract, rows

ROOT = Path(__file__).resolve().parents[1]


def manifest():
    return {"pairs": [
        {"pair_id": "a", "fixture_scene": "mediaShelf", "theme": "dark", "element_type": "collectionItem", "focused_crop": "f", "unfocused_crop": "u", "hardNegative": True},
        {"pair_id": "b", "fixture_scene": "gridMatrix", "theme": "light", "element_type": "imageView", "focused_crop": "f", "unfocused_crop": "u", "hardNegative": True},
    ]}


class BaselineTests(unittest.TestCase):
    def test_grouped_metrics_and_hard_support(self):
        value = evaluate(rows(manifest()), {"a:1": .9, "a:0": .1, "b:1": .9, "b:0": .9})
        self.assertEqual(value["groups"]["overall"]["fp"], 1)
        self.assertEqual(value["hardNegative"], {"n": 2, "fp": 1, "fpr": .5, "status": "available", "gatePassed": "not_assessed"})
        self.assertEqual(value["groups"]["theme:dark"]["n"], 2)
        self.assertEqual(value["threshold"], {
            "value": .85,
            "purpose": "shipped_baseline_comparison",
            "candidatePolicy": "complete_30_epochs_then_select_on_validation_and_lock_before_test",
        })

    def test_missing_score_and_empty_hard_support_fail(self):
        with self.assertRaisesRegex(BaselineError, "missing_or_invalid_inference"):
            evaluate(rows(manifest()), {"a:1": .9})
        no_hard = manifest(); no_hard["pairs"][0]["hardNegative"] = False; no_hard["pairs"][1]["hardNegative"] = False
        with self.assertRaisesRegex(BaselineError, "empty_hard_negative_support"):
            evaluate(rows(no_hard), {"a:1": .9, "a:0": .1, "b:1": .9, "b:0": .1})

    def test_shipped_model_contract_is_bound_by_bytes(self):
        model = ROOT / "NativeUIAuditKitModels/Sources/NativeUIAuditKitModels/Resources/FocusRingDetector.mlmodelc"
        contract = model_contract(model)
        self.assertEqual(len(contract["sha256"]), 64)
        self.assertIn("is_focused_prob", contract["outputs"])


if __name__ == "__main__": unittest.main()
