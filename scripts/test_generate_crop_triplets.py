#!/usr/bin/env python3
"""Tests for generate_crop_triplets.py. Outputs stay under .build/ (ASD-STE100)."""
import json
from pathlib import Path
import shutil
import sys
import unittest
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generate_crop_triplets as gen

ROOT = Path(__file__).resolve().parents[1]


class TestGenerateCropTriplets(unittest.TestCase):
    def setUp(self):
        if gen.Image is None:
            self.skipTest("Pillow not available")
        self.output_dir = ROOT / ".build" / f"test-crop-triplets-{uuid.uuid4().hex}"
        self.addCleanup(shutil.rmtree, self.output_dir, True)

    def test_definitions(self):
        self.assertEqual(set(gen.THEMES), {"dark_standard", "light_standard", "dark_low_contrast"})
        self.assertEqual(len(gen.ARCHETYPES), 7)

    def test_every_case_is_unique(self):
        manifest = gen.generate_multi_theme_dataset(self.output_dir, cases_per_theme=70)
        self.assertEqual(manifest["total_cases"], 210)
        anchors = {c["crop_anchor_sha256"] for c in manifest["cases"]}
        self.assertEqual(len(anchors), 210)

    def test_manifest_records_actual_geometry_and_polarity(self):
        manifest = gen.generate_multi_theme_dataset(self.output_dir, cases_per_theme=7)
        case = manifest["cases"][0]
        item = json.loads((self.output_dir / "crops" / case["case_id"] / "crop_manifest.json").read_text())
        variation = item["variation"]
        self.assertEqual(item["anchor"]["center"], [variation["cx"], variation["cy"]])
        self.assertEqual(item["negative"]["center"], list(gen.negative_center(variation)))
        self.assertEqual((item["anchor"]["is_focused"], item["positive"]["is_focused"], item["negative"]["is_focused"]),
                         (True, False, False))

    def test_refuses_counts_that_drop_cases(self):
        for count in (0, 5, 71):
            with self.subTest(count=count), self.assertRaisesRegex(ValueError, "multiple of 7"):
                gen.generate_multi_theme_dataset(self.output_dir, cases_per_theme=count)

    def test_render_dimensions(self):
        img = gen.render_crop_canvas("shelf", "dark_standard", is_focused=True)
        self.assertEqual((img.size, img.mode), ((256, 256), "RGB"))


if __name__ == "__main__":
    unittest.main()
