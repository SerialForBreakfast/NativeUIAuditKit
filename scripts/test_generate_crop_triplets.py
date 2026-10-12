#!/usr/bin/env python3
"""Unit tests for generate_crop_triplets.py (ASD-STE100)."""
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generate_crop_triplets as gen

class TestGenerateCropTriplets(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.output_dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_theme_and_archetype_definitions(self):
        self.assertIn("dark_standard", gen.THEMES)
        self.assertIn("light_standard", gen.THEMES)
        self.assertIn("dark_low_contrast", gen.THEMES)
        self.assertEqual(len(gen.ARCHETYPES), 7)

    def test_render_crop_canvas_dimensions(self):
        if gen.Image is None:
            self.skipTest("Pillow not available in environment")
        img = gen.render_crop_canvas("shelf", "dark_standard", is_focused=True)
        self.assertEqual(img.size, (256, 256))
        self.assertEqual(img.mode, "RGB")

    def test_dataset_generation_structure(self):
        if gen.Image is None:
            self.skipTest("Pillow not available in environment")
        # Generate minimal sample (7 cases per theme = 1 per archetype)
        manifest = gen.generate_multi_theme_dataset(self.output_dir, cases_per_theme=7)
        self.assertEqual(manifest["total_cases"], 21)
        self.assertEqual(manifest["themeDistribution"]["dark_standard"], 7)
        self.assertEqual(manifest["themeDistribution"]["light_standard"], 7)
        self.assertEqual(manifest["themeDistribution"]["dark_low_contrast"], 7)

        # Verify bulk manifest file
        bulk_file = self.output_dir / "bulk_crop_triplets_manifest.json"
        self.assertTrue(bulk_file.exists())

        # Verify individual case output
        first_case = manifest["cases"][0]
        case_dir = self.output_dir / "crops" / first_case["case_id"]
        self.assertTrue((case_dir / "crop_anchor.png").exists())
        self.assertTrue((case_dir / "crop_positive.png").exists())
        self.assertTrue((case_dir / "crop_negative.png").exists())
        self.assertTrue((case_dir / "crop_manifest.json").exists())

        # Verify PNG dimensions
        with (case_dir / "crop_anchor.png").open("rb") as f:
            header = f.read(24)
            w, h = struct.unpack(">II", header[16:24])
            self.assertEqual((w, h), (256, 256))

if __name__ == "__main__":
    unittest.main()
