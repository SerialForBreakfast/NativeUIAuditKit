#!/usr/bin/env python3
"""Unit tests for ingest_crop_triplets.py (ASD-STE100)."""
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ingest_crop_triplets import ingest_triplets, check_png_dimensions

class TestIngestCropTriplets(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.crops_dir = self.root / "crops"
        self.crops_dir.mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def _make_dummy_png(self, path, width=256, height=256):
        header = b"\x89PNG\r\n\x1a\n"
        ihdr_data = struct.pack(">II", width, height) + b"\x08\x06\x00\x00\x00"
        ihdr_chunk = b"\x00\x00\x00\x0dIHDR" + ihdr_data + b"\x00\x00\x00\x00"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(header + ihdr_chunk)

    def test_ingest_valid_cases(self):
        case_id = "test_case_01"
        case_dir = self.crops_dir / case_id
        for f in ["crop_anchor.png", "crop_positive.png", "crop_negative.png"]:
            self._make_dummy_png(case_dir / f, 256, 256)
        (case_dir / "crop_manifest.json").write_text("{}")

        manifest = {
            "cases": [
                {
                    "case_id": case_id,
                    "layout": "shelf",
                    "focus_bias": "center",
                    "interruption": "none",
                    "focused_node_id": "item_0",
                    "crop_anchor_sha256": "dummy_anchor",
                    "crop_positive_sha256": "dummy_pos",
                    "crop_negative_sha256": "dummy_neg"
                }
            ]
        }
        (self.root / "bulk_crop_triplets_manifest.json").write_text(json.dumps(manifest))

        out_path = self.root / "out.json"
        summary = ingest_triplets(self.root, out_path)
        self.assertEqual(summary["total_cases_found"], 1)
        self.assertEqual(summary["validated_cases"], 1)
        self.assertEqual(summary["failed_cases"], 0)
        self.assertTrue(out_path.exists())

    def test_invalid_dimensions_flagged(self):
        case_id = "test_case_bad_dim"
        case_dir = self.crops_dir / case_id
        self._make_dummy_png(case_dir / "crop_anchor.png", 100, 100) # Wrong dimensions
        self._make_dummy_png(case_dir / "crop_positive.png", 256, 256)
        self._make_dummy_png(case_dir / "crop_negative.png", 256, 256)
        (case_dir / "crop_manifest.json").write_text("{}")

        manifest = {
            "cases": [
                {
                    "case_id": case_id,
                    "layout": "grid",
                    "focus_bias": "edge"
                }
            ]
        }
        (self.root / "bulk_crop_triplets_manifest.json").write_text(json.dumps(manifest))

        summary = ingest_triplets(self.root)
        self.assertEqual(summary["validated_cases"], 0)
        self.assertEqual(summary["failed_cases"], 1)

    def test_theme_preservation(self):
        case_id = "test_case_light"
        case_dir = self.crops_dir / case_id
        for f in ["crop_anchor.png", "crop_positive.png", "crop_negative.png"]:
            self._make_dummy_png(case_dir / f, 256, 256)
        (case_dir / "crop_manifest.json").write_text("{}")

        manifest = {
            "dataset_name": "Test-Theme-Corpus",
            "cases": [
                {
                    "case_id": case_id,
                    "layout": "hero_detail",
                    "theme": "light_standard",
                    "focus_bias": "balanced",
                    "crop_anchor_sha256": "dummy_anchor",
                    "crop_positive_sha256": "dummy_pos",
                    "crop_negative_sha256": "dummy_neg"
                }
            ]
        }
        (self.root / "bulk_crop_triplets_manifest.json").write_text(json.dumps(manifest))

        summary = ingest_triplets(self.root)
        self.assertEqual(summary["themes"].get("light_standard"), 1)
        self.assertEqual(summary["cases"][0]["theme"], "light_standard")
        focus_manifest = json.loads((self.root / "focus_dataset_manifest.json").read_text())
        self.assertEqual(focus_manifest["pairs"][0]["theme"], "light_standard")

if __name__ == "__main__":
    unittest.main()

