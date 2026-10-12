#!/usr/bin/env python3
"""Unit tests for modular benchmark evaluator (ASD-STE100)."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest

import benchmark_evaluator

class BenchmarkEvaluatorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="test-benchmark-eval-"))
        self.out_dir = self.tmp / "eval_out"
        self.out_dir.mkdir(parents=True, exist_ok=True)
        benchmark_evaluator.OUTPUT_DIR = self.out_dir

        # Create synthetic manifest
        self.manifest_path = self.tmp / "test_manifest.json"
        self.crop_dir = self.tmp / "crops" / "case_01"
        self.crop_dir.mkdir(parents=True, exist_ok=True)

        crop_manifest = {
            "schemaVersion": "contract-v1-focus-triplets",
            "anchor": {"center": [640, 1003], "is_focused": True, "file": "crop_anchor.png"},
            "positive": {"center": [640, 1003], "is_focused": False, "file": "crop_positive.png"},
            "negative": {"center": [660, 1003], "is_focused": False, "file": "crop_negative.png"}
        }
        (self.crop_dir / "crop_manifest.json").write_text(json.dumps(crop_manifest))

        data = {
            "schema_version": "v1",
            "pairs": [
                {
                    "pair_id": "case_01",
                    "element_type": "shelf",
                    "theme": "dark_standard",
                    "split": "val",
                    "focused_crop": "crops/case_01/crop_positive.png"
                },
                {
                    "pair_id": "case_02",
                    "element_type": "grid",
                    "theme": "light_standard",
                    "split": "test",
                    "focused_crop": "crops/case_02/crop_positive.png"
                }
            ]
        }
        self.manifest_path.write_text(json.dumps(data))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_spatial_discrimination_evaluation(self):
        config = {
            "job_id": "test-spatial",
            "dimension": "spatial_discrimination",
            "target_archetype": "shelf",
            "manifest_path": str(self.manifest_path),
            "min_threshold": 0.85
        }
        (self.out_dir / "config.json").write_text(json.dumps(config))
        benchmark_evaluator.run()

        summary_file = self.out_dir / "benchmark_summary.json"
        self.assertTrue(summary_file.exists())
        summary = json.loads(summary_file.read_text())
        self.assertEqual(summary["evaluated_cases"], 1)
        self.assertTrue(summary["metrics"]["passed_threshold"])
        self.assertIn("mean_negative_distance_px", summary["metrics"])
        self.assertEqual(summary["metrics"]["mean_negative_distance_px"], 20.0)

    def test_hcf_dual_mode_evaluation(self):
        config = {
            "job_id": "test-hcf",
            "dimension": "hcf_dual_mode",
            "target_archetype": "grid",
            "manifest_path": str(self.manifest_path),
            "min_threshold": 0.90
        }
        (self.out_dir / "config.json").write_text(json.dumps(config))
        benchmark_evaluator.run()

        summary = json.loads((self.out_dir / "benchmark_summary.json").read_text())
        self.assertEqual(summary["evaluated_cases"], 1)
        self.assertGreaterEqual(summary["metrics"]["accuracy"], 0.95)
        self.assertTrue(summary["metrics"]["passed_threshold"])

    def test_missing_manifest_fallback(self):
        config = {
            "job_id": "test-fallback",
            "manifest_path": str(self.tmp / "nonexistent.json")
        }
        (self.out_dir / "config.json").write_text(json.dumps(config))
        benchmark_evaluator.run()

        summary = json.loads((self.out_dir / "benchmark_summary.json").read_text())
        self.assertIn("metrics", summary)

if __name__ == "__main__":
    unittest.main()
