"""Offline surface admission and frozen evaluation regressions; generated inputs only."""
import copy
import io
import json
from pathlib import Path
import shutil
import tarfile
import tempfile
import unittest

from focus_dataset_contract import ROOT, FocusDataError, digest
from focus_surface_intake import safe_members, inspect_group, sha, FREEZE
from focus_surface_evaluation import score, validate_rows, seal_check
from focus_surface_audit import overlap
from harvest_bundle_validation import validate_bundle, HarvestValidationError
from harvest_sidecar_v2 import recipe_hash, SidecarError
from simulator_focus_manifest import build
from test_ttr_sidecar_v2 import write_bundle, reindex
from test_ttr_appearance import replace_recipes

VECTORS = {
    "cinema_rows": "e03721c83f9d88d0ce522a2d5cab0ac91fee43995a85d02190d83ab1a237cad8",
    "album_grid": "162cd1d7b574f1884ba621285e50d838a598c8a1ff9467751ab50342a4beaf85",
    "memory_mosaic": "db36f50b350a373ba4950ee068ee8ebef90c7fcec8db5bffcf51abe3575a33eb",
    "icon_shelf": "85c6d2ead83e660b6c2fc414a6794f72d70d763ea229cf6b0f68b74c009a12ce",
}


def recipe(template="cinema_rows"):
    return {"schema_version": 1, "archetype": "surface_template", "element_count": 24,
            "theme": "dark", "density": "regular", "seed": 7, "step_index": 0,
            "surface": {"version": 1, "template": template, "family_id": "surface-v1." + template}}


def samples():
    return [{"id": f"id-{i}", "label": int(i == 0), "group": "cinema_rows", "role": "appearance-validation",
             "kind": "competition", "frameID": "frame", "elementID": f"element-{i}",
             "candidateCount": 2, "candidateComplete": True, "family": "cinema_rows", "theme": "dark",
             "control": "collectionItem", "hard": False, "stratum": "dense-dark-media"} for i in range(2)]


class SurfaceTests(unittest.TestCase):
    def setUp(self):
        (ROOT / ".build/debug-output").mkdir(parents=True, exist_ok=True)
        self.root = Path(tempfile.mkdtemp(prefix="surface-test-", dir=ROOT / ".build/debug-output"))

    def tearDown(self):
        shutil.rmtree(self.root)

    def test_all_received_producer_vectors(self):
        for template, expected in VECTORS.items():
            r = recipe(template)
            self.assertEqual(recipe_hash(r), expected)
            del r["surface"]["family_id"]
            self.assertEqual(recipe_hash(r), expected)

    def test_surface_closed_contract(self):
        for key, values in {"version": [True, 2, "1"], "template": [[], "new"],
                            "family_id": ["surface-v1.other"]}.items():
            for value in values:
                r = recipe(); r["surface"][key] = value
                with self.assertRaises(SidecarError): recipe_hash(r)
        r = recipe(); r["surface"]["unexpected"] = 1
        with self.assertRaises(SidecarError): recipe_hash(r)
        r = recipe(); r["archetype"] = "grid_matrix"
        with self.assertRaises(SidecarError): recipe_hash(r)
        r = recipe(); del r["surface"]
        with self.assertRaises(SidecarError): recipe_hash(r)

    def bundle(self):
        group = self.root / "cinema_rows"; group.mkdir()
        bundle = group / "export"; meta = write_bundle(bundle)
        r = recipe(); r["element_count"] = 1; r["recipe_hash"] = recipe_hash(r)
        replace_recipes(meta, r)
        (bundle / "m.json").write_text(json.dumps(meta)); reindex(bundle)
        entry = {"group_id": "surface-v1.cinema_rows", "role": "appearance-validation", "job_id": "test-only",
                 "accepted_rows": 1, "manifest_sha256": sha(bundle / "manifest.json")}
        provenance = {**entry, "seed": 7, "frozen_by_nuiak_at": FREEZE,
                      "source_revision": "test-only", "canonical_recipe_sha256": r["recipe_hash"]}
        (group / "provenance.json").write_text(json.dumps(provenance))
        (group / "recipe.json").write_text(json.dumps(r))
        return group, bundle, entry, meta

    def test_real_intake_native_binding_and_role_preservation(self):
        group, bundle, entry, _ = self.bundle()
        original = (bundle / "manifest.json").read_bytes()
        result = inspect_group(group, entry)
        self.assertEqual(result["members"][0]["role"], "appearance-validation")
        self.assertEqual(result["members"][0]["originalSplit"], "validation")
        self.assertFalse(result["independentEvaluationEligible"])
        self.assertEqual((bundle / "manifest.json").read_bytes(), original)
        self.assertEqual(build(validate_bundle(bundle), "test", "test", None)["pairs"][0]["family"], "surfaceTemplate")

    def test_role_conflict_rejected(self):
        group, _, entry, _ = self.bundle(); entry["role"] = "final-challenge"
        with self.assertRaisesRegex(FocusDataError, "changed_provenance_role"): inspect_group(group, entry)

    def test_changed_membership_rejected(self):
        group, bundle, entry, _ = self.bundle()
        (bundle / "manifest.json").write_text("[]")
        with self.assertRaisesRegex(FocusDataError, "changed_export_manifest"): inspect_group(group, entry)

    def test_training_bucket_is_not_consumer_training_authority(self):
        group, bundle, entry, _ = self.bundle()
        rows = json.loads((bundle / "manifest.json").read_text()); rows[0]["split"] = "training"
        for name, content in (("manifest",rows), ("training",rows), ("calibration",[])):
            (bundle / (name + ".json")).write_text(json.dumps(content))
        reindex(bundle); entry["manifest_sha256"] = sha(bundle / "manifest.json")
        result = inspect_group(group, entry)
        self.assertEqual(result["members"][0]["originalSplit"], "train")
        self.assertEqual(result["members"][0]["role"], "appearance-validation")
        self.assertFalse(result["independentEvaluationEligible"])

    def test_pixel_leakage_and_contradictions_are_reported(self):
        rows = [{"id": "a", "group": "cinema_rows", "role": "appearance-validation", "label": 1,
                 "framePixelSHA256": "frame1", "crop": {"pixelSHA256": "shared"}},
                {"id": "b", "group": "memory_mosaic", "role": "final-challenge", "label": 0,
                 "framePixelSHA256": "frame2", "crop": {"pixelSHA256": "shared"}}]
        result = overlap(rows, {"shared": {"training"}})
        self.assertEqual(len(result["priorOverlap"]), 2)
        self.assertEqual(len(result["crossRolePixelGroups"]), 1)
        self.assertEqual(len(result["contradictoryCropGroups"]), 1)
        self.assertFalse(result["independenceEstablished"])

    def test_corrupt_image_rejected(self):
        group, bundle, entry, _ = self.bundle()
        (bundle / "f.png").write_bytes(b"bad")
        with self.assertRaises(HarvestValidationError): inspect_group(group, entry)

    def test_missing_image_rejected(self):
        group, bundle, entry, _ = self.bundle(); (bundle / "f.png").unlink()
        with self.assertRaises(HarvestValidationError): inspect_group(group, entry)

    def test_unobserved_focus_and_legacy_surface_rejected(self):
        _, bundle, _, meta = self.bundle()
        del meta["schema_version"]
        (bundle / "m.json").write_text(json.dumps(meta)); reindex(bundle)
        with self.assertRaisesRegex(HarvestValidationError, "surface_requires_v2_brackets"): validate_bundle(bundle)
        meta["schema_version"] = 2
        meta["focused_capture"]["before_scene"]["focus_observation"]["verified"] = False
        (bundle / "m.json").write_text(json.dumps(meta)); reindex(bundle)
        with self.assertRaisesRegex(HarvestValidationError, "native_focus"): validate_bundle(bundle)

    def test_archive_paths_types_and_duplicates(self):
        for names, kind in [(["../escape"], tarfile.REGTYPE), (["/escape"], tarfile.REGTYPE),
                            (["safe"], tarfile.SYMTYPE), (["a", "A"], tarfile.REGTYPE)]:
            data = io.BytesIO()
            with tarfile.open(fileobj=data, mode="w") as archive:
                for name in names:
                    info = tarfile.TarInfo(name); info.type = kind; archive.addfile(info)
            data.seek(0)
            with tarfile.open(fileobj=data) as archive, self.assertRaises(FocusDataError): safe_members(archive)

    def test_challenge_rejected_even_with_validation_role_claim(self):
        rows = samples(); rows[0]["group"] = "memory_mosaic"
        with self.assertRaisesRegex(FocusDataError, "final_challenge"): validate_rows(rows)
        rows = samples(); rows[0]["role"] = "final-challenge"
        with self.assertRaisesRegex(FocusDataError, "final_challenge"): validate_rows(rows)

    def test_incomplete_and_duplicate_candidate_sets(self):
        for rows in [samples()[:1], [samples()[0]] * 2]:
            with self.assertRaises(FocusDataError): validate_rows(rows)
        rows = samples(); rows[0]["candidateComplete"] = False
        with self.assertRaises(FocusDataError): validate_rows(rows)

    def test_all_four_decisions_and_unavailable_support(self):
        for probabilities, expected in [([.9,.1], "unique-correct"), ([.1,.9], "wrong-focus"),
                                         ([.1,.1], "no-focus"), ([.9,.9], "multiple-focus")]:
            rows = samples(); result = score(rows, [{"id": r["id"], "probability": p} for r,p in zip(rows,probabilities)])
            self.assertEqual(result["frameCounts"], {expected: 1})
            unsupported = result["metrics"]["competition"]["groups"]["stratum:photos-buttons"]
            self.assertIsNone(unsupported["recall"])
            self.assertEqual(unsupported["status"], "unavailable")

    def test_identical_input_and_full_prediction_accounting(self):
        rows = samples(); predictions = [{"id": r["id"], "probability": .5} for r in rows]
        for bad in (predictions[:1], list(reversed(predictions)), predictions + predictions):
            with self.assertRaisesRegex(FocusDataError, "prediction_membership"): score(rows,bad)
        for invalid in (float("nan"), True, -1, 2, None):
            bad = copy.deepcopy(predictions); bad[0]["probability"] = invalid
            with self.assertRaisesRegex(FocusDataError, "invalid_probability"): score(rows,bad)

    def test_changed_protocol_seal(self):
        doc = {"membership": ["a", "b"]}; doc["seal"] = digest(doc); seal_check(doc)
        doc["membership"].pop()
        with self.assertRaisesRegex(FocusDataError, "changed_protocol"): seal_check(doc)


if __name__ == "__main__": unittest.main()
