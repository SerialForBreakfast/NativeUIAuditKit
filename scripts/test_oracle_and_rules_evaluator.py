#!/usr/bin/env python3
"""Unit tests for oracle_and_rules_evaluator.py (ASD-STE100)."""
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

import oracle_and_rules_evaluator as evaluator


class TestOracleAndRulesEvaluator(unittest.TestCase):
    """Test suite for physical difference oracle, rules, and hybrid gating."""

    def test_compute_frame_difference(self):
        std = np.zeros((100, 100, 3), dtype=np.uint8)
        hcf = np.zeros((100, 100, 3), dtype=np.uint8)
        hcf[10:30, 10:30] = [200, 200, 200]
        diff = evaluator.compute_frame_difference(std, hcf)
        self.assertEqual(diff.shape, (100, 100))
        self.assertEqual(diff[0, 0], 0)
        self.assertEqual(diff[20, 20], 200)

    def test_compute_box_density(self):
        diff_map = np.zeros((100, 100), dtype=np.uint8)
        diff_map[20:40, 20:40] = 100
        density_in = evaluator.compute_box_density(diff_map, (20, 20, 20, 20), margin=0)
        density_out = evaluator.compute_box_density(diff_map, (60, 60, 20, 20), margin=0)
        self.assertEqual(density_in, 100.0)
        self.assertEqual(density_out, 0.0)

    def test_oracle_focus_tagger(self):
        std = np.zeros((200, 200, 3), dtype=np.uint8)
        hcf = np.zeros((200, 200, 3), dtype=np.uint8)
        boxes = [(20, 20, 40, 40), (100, 20, 40, 40), (20, 100, 40, 40)]
        # Inject focus difference at box 1
        hcf[20:60, 100:140] = [180, 180, 180]

        tag_result = evaluator.oracle_focus_tagger(std, hcf, boxes)
        self.assertTrue(tag_result["is_high_confidence"])
        self.assertEqual(tag_result["focused_index"], 1)
        self.assertGreater(tag_result["density_ratio"], 10.0)
        self.assertGreaterEqual(tag_result["concentration_percent"], 80.0)

    def test_outline_stroke_contrast(self):
        # Image with bright 3 px stroke around box (30, 30, 40, 40)
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        # Background is dark (20)
        img[:] = 20
        # Outer ring is bright (220)
        img[27:73, 27:73] = 220
        # Inside of control is dark (20)
        img[30:70, 30:70] = 20

        contrast = evaluator.compute_outline_stroke_contrast(img, (30, 30, 40, 40), stroke_width=3)
        self.assertGreater(contrast, 50.0)

        # Unfocused flat box has low contrast
        contrast_flat = evaluator.compute_outline_stroke_contrast(img, (75, 75, 20, 20), stroke_width=3)
        self.assertLess(contrast_flat, 5.0)

    def test_rules_focus_detector(self):
        img = np.zeros((200, 200, 3), dtype=np.uint8)
        img[:] = 30
        boxes = [(20, 20, 40, 40), (100, 20, 46, 46)]  # Box 1 is 1.15x larger
        # Box 1 has bright outline
        img[97:149, 17:69] = 200
        img[100:146, 20:66] = 30

        result = evaluator.rules_focus_detector(img, [(20, 20, 40, 40), (20, 100, 46, 46)])
        self.assertTrue(result["rule_triggered"])
        self.assertEqual(result["focused_index"], 1)

    def test_hybrid_gating_router(self):
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        boxes = [(10, 10, 30, 30), (50, 50, 30, 30)]

        # High contrast case routes to rule
        img[7:43, 7:43] = 240
        img[10:40, 10:40] = 10
        route_high = evaluator.hybrid_gating_router(img, boxes, high_contrast_threshold=30.0)
        self.assertEqual(route_high["decision_source"], "rule")
        self.assertFalse(route_high["neural_evaluated"])

        # Ambiguous case routes to neural net
        img_flat = np.zeros((100, 100, 3), dtype=np.uint8)
        route_ambiguous = evaluator.hybrid_gating_router(
            img_flat, boxes, neural_probabilities=[0.1, 0.9], high_contrast_threshold=30.0
        )
        self.assertEqual(route_ambiguous["decision_source"], "neural")
        self.assertTrue(route_ambiguous["neural_evaluated"])
        self.assertEqual(route_ambiguous["focused_index"], 1)

    def test_run_experiment_evaluation_all_modes(self):
        modes = [
            "oracle_density",
            "oracle_scrim",
            "rules_stroke_contrast",
            "rules_elevation_ratio",
            "rules_hybrid_gating",
            "four_way_comparison",
            "dual_profile_loss",
        ]
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_p = Path(tmp_dir)
            for mode in modes:
                cfg = {"mode": mode}
                res = evaluator.run_experiment_evaluation(cfg, out_p)
                self.assertEqual(res["mode"], mode)
                self.assertTrue((out_p / "evaluation.json").exists())
                saved = json.loads((out_p / "evaluation.json").read_text())
                self.assertEqual(saved["mode"], mode)


if __name__ == "__main__":
    unittest.main()
