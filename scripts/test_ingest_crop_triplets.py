#!/usr/bin/env python3
"""Tests for ingest_crop_triplets.py. Outputs stay under .build/ (ASD-STE100)."""
import json
from pathlib import Path
import shutil
import sys
import unittest
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generate_crop_triplets as gen
from ingest_crop_triplets import compute_sha256, ingest_triplets

ROOT = Path(__file__).resolve().parents[1]


class TestIngestCropTriplets(unittest.TestCase):
    def setUp(self):
        if gen.Image is None:
            self.skipTest("Pillow not available")
        self.root = ROOT / ".build" / f"test-ingest-triplets-{uuid.uuid4().hex}"
        self.addCleanup(shutil.rmtree, self.root, True)
        self.manifest = gen.generate_multi_theme_dataset(self.root, cases_per_theme=14)

    def test_focused_crop_is_the_focused_render(self):
        summary = ingest_triplets(self.root, self.root / "out.json")
        self.assertEqual((summary["validated_cases"], summary["failed_cases"]), (42, 0))
        pairs = json.loads((self.root / "focus_dataset_manifest.json").read_text())["pairs"]
        first = pairs[0]
        case = next(c for c in self.manifest["cases"] if c["case_id"] == first["pair_id"])
        self.assertEqual(compute_sha256(self.root / first["focused_crop"]), case["crop_anchor_sha256"])
        self.assertEqual(compute_sha256(self.root / first["unfocused_crop"]), case["crop_positive_sha256"])

    def test_groups_do_not_cross_splits(self):
        # Copy 1 case so 2 cases share identical pixels.
        cases = self.manifest["cases"]
        source, copy = cases[0], dict(cases[0], case_id="copy_of_first")
        shutil.copytree(self.root / "crops" / source["case_id"], self.root / "crops" / "copy_of_first")
        manifest = dict(self.manifest, cases=cases + [copy])
        (self.root / "bulk_crop_triplets_manifest.json").write_text(json.dumps(manifest))
        summary = ingest_triplets(self.root)
        self.assertEqual(summary["unique_anchor_images"], 42)
        by_id = {c["case_id"]: c for c in summary["cases"]}
        self.assertEqual(by_id["copy_of_first"]["split"], by_id[source["case_id"]]["split"])
        splits_by_group = {}
        for c in summary["cases"]:
            splits_by_group.setdefault(c["group"], set()).add(c["split"])
        self.assertTrue(all(len(s) == 1 for s in splits_by_group.values()))

    def test_hash_mismatch_and_wrong_polarity_fail(self):
        cases = self.manifest["cases"]
        bad_hash = dict(cases[0], crop_anchor_sha256="0" * 64)
        item_path = self.root / "crops" / cases[1]["case_id"] / "crop_manifest.json"
        item = json.loads(item_path.read_text())
        item["anchor"]["is_focused"] = False
        item_path.write_text(json.dumps(item))
        manifest = dict(self.manifest, cases=[bad_hash, cases[1]] + cases[2:])
        (self.root / "bulk_crop_triplets_manifest.json").write_text(json.dumps(manifest))
        summary = ingest_triplets(self.root)
        errors = {f["case_id"]: f["error"] for f in summary["failures"]}
        self.assertIn("hash_mismatch", errors[cases[0]["case_id"]])
        self.assertIn("polarity_unknown_or_wrong", errors[cases[1]["case_id"]])
        self.assertEqual(summary["validated_cases"], 40)

    def test_reencoded_pixels_join_declared_groups(self):
        source = self.manifest['cases'][0]
        duplicate = dict(source, case_id='reencoded', group='different-lineage')
        folder = self.root / 'crops' / 'reencoded'
        shutil.copytree(self.root / 'crops' / source['case_id'], folder)
        for role in ('anchor', 'positive', 'negative'):
            path = folder / f'crop_{role}.png'
            with gen.Image.open(path) as image:
                image.load()
                image.save(path, compress_level=0)
            duplicate[f'crop_{role}_sha256'] = compute_sha256(path)
        manifest = dict(self.manifest, cases=self.manifest['cases'] + [duplicate])
        (self.root / 'bulk_crop_triplets_manifest.json').write_text(json.dumps(manifest))
        result = ingest_triplets(self.root)
        rows = {row['case_id']: row for row in result['cases']}
        self.assertEqual(rows[source['case_id']]['group'], rows['reencoded']['group'])
        self.assertEqual(result['unique_anchor_images'], 42)


if __name__ == "__main__":
    unittest.main()
