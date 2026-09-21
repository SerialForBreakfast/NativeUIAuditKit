"""Offline end-to-end FocusRing tests. Every image and score here is test-only."""
import copy
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image
from focus_dataset_contract import ROOT, PREPROCESSING, FocusDataError, crop_frame, digest, expanded_box, validate_manifest
from focus_training_preflight import preflight
from focus_ring_baseline import BaselineError, prepare_protocol, score_protocol
from simulator_focus_manifest import build, SimulatorManifestError
from train_focus_ring_detector import load_samples


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ConsumerTests(unittest.TestCase):
    def setUp(self):
        base = ROOT / ".build/debug-output"
        base.mkdir(parents=True, exist_ok=True)
        self.root = Path(tempfile.mkdtemp(dir=base, prefix="focus-consumer-"))
        self.raw = self.root / "raw"; self.raw.mkdir()
        self.data = self.root / "data"; self.data.mkdir()
        self.model = self.root / "model.mlmodelc"; self.model.mkdir()
        (self.model / "metadata.json").write_text(json.dumps([{"outputSchema": [{"name": "is_focused_prob"}]}]))
        self.doc = {"version": "1.2", "sourceKind": "simulatorFixture", "producerReference": "test-revision",
                    "corpusID": "offline-test-only", "evidenceKind": "test-only", "sourceRoot": str(self.raw.relative_to(ROOT)),
                    "preprocessing": PREPROCESSING, "pairs": []}
        self.add_pair("a", "development", 1)

    def tearDown(self):
        shutil.rmtree(self.root)

    def add_pair(self, pid, split, seed):
        frames = {}
        pair = {"pair_id": pid, "recipe_group": f"seed:{seed}", "recipe_seed": seed, "elementID": "e",
                "split": split, "sourceKind": "simulatorFixture", "labelSource": "fixtureGroundTruth",
                "fixture_scene": "gridMatrix", "theme": "light", "element_type": "collectionItem"}
        for i, role in enumerate(("focused", "unfocused")):
            name = f"{pid}-{role}.png"
            im = Image.new("RGB", (40, 30))
            im.putdata([((x * 7 + seed * 13 + i) % 256, (y * 9 + seed + i * 50) % 256, (x+y+seed) % 256) for y in range(30) for x in range(40)])
            im.save(self.raw / name)
            bounds = [2.5, 3.5, 20, 15] if i == 0 else [8, 7, 12, 9]
            frame = {"path": name, "sha256": sha(self.raw / name), "bounds": bounds,
                     "frameID": name, "focusFrameID": name, "labelSource": "fixtureCallback", "observedFocusID": "e" if i == 0 else None}
            frames[role] = frame
            box = expanded_box(bounds, im.size)
            crop_frame(im, box).save(self.data / name)
            pair[role + "_crop"] = name
            pair[role + "_crop_sha256"] = sha(self.data / name)
            pair[role + "_crop_box"] = box
        pair["frames"] = frames
        self.doc["pairs"].append(pair)
        self.save()
        return pair

    def save(self):
        path = self.data / "focus_dataset_manifest.json"
        path.write_text(json.dumps(self.doc))
        return path

    def cli(self, script, *args):
        return subprocess.run([sys.executable, str(ROOT / "scripts" / script), *map(str, args)], cwd=ROOT,
                              env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, capture_output=True, text=True, timeout=20)

    def test_frame_specific_geometry_and_determinism(self):
        first = validate_manifest(self.doc, self.data)
        self.assertEqual(first, validate_manifest(self.doc, self.data))
        p = self.doc["pairs"][0]
        self.assertNotEqual(p["focused_crop_box"], p["unfocused_crop_box"])
        self.assertEqual(expanded_box([0, 0, 20, 20], (30, 30)), [0, 0, 23.2, 23.2])
        self.assertEqual(expanded_box([100, 50, 100, 100], (400, 300)), [84, 34, 216, 166])

    def test_wrong_focus_missing_callback_and_prediction_labels(self):
        for key, val, message in (("observedFocusID", "other", "mismatched"), ("focusFrameID", "old", "stale"), ("labelSource", "modelPrediction", "untrusted")):
            doc = copy.deepcopy(self.doc); doc["pairs"][0]["frames"]["focused"][key] = val
            with self.subTest(key=key), self.assertRaisesRegex(FocusDataError, message):
                validate_manifest(doc, self.data)
        doc = copy.deepcopy(self.doc); del doc["pairs"][0]["frames"]["unfocused"]["observedFocusID"]
        with self.assertRaises(FocusDataError): validate_manifest(doc, self.data)

    def test_missing_corrupt_hash_and_wrong_dimensions(self):
        p = self.doc["pairs"][0]; path = self.data / p["focused_crop"]
        path.unlink()
        with self.assertRaisesRegex(FocusDataError, "missing_pixels"): validate_manifest(self.doc, self.data)
        path.write_bytes(b"broken")
        with self.assertRaisesRegex(FocusDataError, "changed_hash"): validate_manifest(self.doc, self.data)
        p["focused_crop_sha256"] = sha(path)
        with self.assertRaisesRegex(FocusDataError, "corrupt_image"): validate_manifest(self.doc, self.data)
        Image.new("RGB", (32, 32)).save(path); p["focused_crop_sha256"] = sha(path)
        with self.assertRaisesRegex(FocusDataError, "dimensions"): validate_manifest(self.doc, self.data)

    def test_changed_crop_even_with_updated_hash_fails_lineage(self):
        p = self.doc["pairs"][0]; path = self.data / p["unfocused_crop"]
        Image.new("RGB", (256, 256), "red").save(path); p["unfocused_crop_sha256"] = sha(path)
        with self.assertRaisesRegex(FocusDataError, "crop_pixel_mismatch"): validate_manifest(self.doc, self.data)

    def test_same_group_distinct_pairs_and_cross_split_leakage(self):
        b = self.add_pair("b", "development", 2)
        b["recipe_seed"] = 1; b["recipe_group"] = "seed:1"
        self.assertEqual(len(validate_manifest(self.doc, self.data)), 2)
        b["split"] = "test"
        with self.assertRaisesRegex(FocusDataError, "split_leakage"): validate_manifest(self.doc, self.data)

    def test_duplicate_and_content_leakage(self):
        self.doc["pairs"].append(copy.deepcopy(self.doc["pairs"][0]))
        with self.assertRaisesRegex(FocusDataError, "duplicate_pair_id"): validate_manifest(self.doc, self.data)
        self.doc["pairs"][1]["pair_id"] = "alias"
        with self.assertRaisesRegex(FocusDataError, "duplicate_pair_content"): validate_manifest(self.doc, self.data)
        self.doc["pairs"][1]["elementID"] = "other"
        self.doc["pairs"][1]["frames"]["focused"]["observedFocusID"] = "other"
        self.doc["pairs"][1].update(split="test", recipe_seed=20, recipe_group="other")
        with self.assertRaisesRegex(FocusDataError, "split_leakage"): validate_manifest(self.doc, self.data)

    def test_unsafe_paths_unknown_versions_and_false_source(self):
        for key, value in (("version", "99"), ("sourceRoot", "../TVTestRig"), ("sourceKind", "unknown")):
            d = copy.deepcopy(self.doc); d[key] = value
            with self.subTest(key=key), self.assertRaises(FocusDataError): validate_manifest(d, self.data)
        self.doc["pairs"][0]["focused_crop"] = "../secret.png"
        with self.assertRaisesRegex(FocusDataError, "unsafe_member"): validate_manifest(self.doc, self.data)

    def test_val_alias_and_no_silent_missing_sample(self):
        self.doc["pairs"][0]["split"] = "validation"; self.save()
        self.assertEqual(len(load_samples(self.data, "val")), 2)
        (self.data / self.doc["pairs"][0]["focused_crop"]).unlink()
        with self.assertRaisesRegex(FocusDataError, "missing_pixels"): load_samples(self.data, "val")

    def test_preflight_no_launch_no_output_and_truthful_errors(self):
        name = self.root.name
        before = set(self.root.rglob("*"))
        r = self.cli("train_focus_ring_detector.py", "--dataset", self.data, "--name", name, "--dry-run")
        self.assertEqual(r.returncode, 2, r.stderr)
        report = json.loads(r.stdout)
        self.assertTrue(report["configurationValid"])
        self.assertFalse(report["launchEligible"])
        self.assertFalse(report["executionAuthorized"])
        self.assertEqual(before, set(self.root.rglob("*")))
        self.assertFalse((ROOT / "NativeUITrainer/focus_ring_runs" / name).exists())
        self.assertNotIn("importing torch", r.stdout)
        r = self.cli("train_focus_ring_detector.py", "--dataset", self.root / "missing", "--name", name, "--execute")
        self.assertEqual(r.returncode, 2)

    def test_preflight_positive_with_test_quota_policy_and_approval_guards(self):
        self.doc["pairs"][0]["split"] = "train"
        self.add_pair("v", "val", 2); self.add_pair("t", "test", 3)
        self.doc["evidenceKind"] = "reviewed-fixture"
        self.doc["trainingApproval"] = {"approved": True, "reviewReference": "test-review-not-real", "membershipSHA256": digest(self.doc["pairs"])}
        self.save()
        with patch("focus_training_preflight.validate", return_value={}) as quotas:
            result = preflight(self.data, self.root.name)
            self.assertFalse(result["launchEligible"], result)
            self.assertIn("runtime_crop_parity_required", result["blockers"])
            quotas.assert_called_once()
            self.doc["evidenceKind"] = "test-only"; self.save()
            self.assertIn("test_only_evidence", preflight(self.data, self.root.name)["blockers"])
        self.assertFalse(preflight(self.data, "../escape")["configurationValid"])
        self.assertFalse(preflight(self.data, self.root.name, epochs=1)["configurationValid"])

    def test_baseline_actual_cli_protocol_scores_and_collision(self):
        protocol_path = self.root / "protocol.json"
        args = ["--manifest", self.save(), "--model", self.model]
        r = self.cli("focus_ring_baseline.py", *args, "--prepare", "--output", protocol_path)
        self.assertEqual(r.returncode, 0, r.stderr)
        protocol = json.loads(protocol_path.read_text())
        self.assertEqual(protocol, prepare_protocol(self.doc, self.data, self.model))
        scores = {"formatVersion": "focus-baseline-scores-v1", "protocolSHA256": protocol["protocolSHA256"],
                  "artifactSHA256": protocol["artifact"]["sha256"], "inferenceKind": "test-only", "scores": {"a:1": .9, "a:0": .1}}
        score_path = self.root / "scores.json"; score_path.write_text(json.dumps(scores))
        output = self.root / "report.json"
        r = self.cli("focus_ring_baseline.py", *args, "--protocol", protocol_path, "--scores", score_path, "--output", output)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(output.read_text())["modelGatePassed"], "not_assessed")
        r = self.cli("focus_ring_baseline.py", *args, "--prepare", "--output", output)
        self.assertEqual(r.returncode, 2)
        scores["scores"]["extra"] = .5
        with self.assertRaisesRegex(BaselineError, "inference"): score_protocol(protocol, scores)
        scores["scores"].pop("extra"); scores["artifactSHA256"] = "wrong"
        with self.assertRaisesRegex(BaselineError, "incompatible"): score_protocol(protocol, scores)

    def test_baseline_rejects_final_holdout_and_changed_model(self):
        protocol = prepare_protocol(self.doc, self.data, self.model)
        (self.model / "weights.bin").write_bytes(b"different")
        self.assertNotEqual(protocol["artifact"], prepare_protocol(self.doc, self.data, self.model)["artifact"])
        self.doc["pairs"][0]["split"] = "test"
        with self.assertRaisesRegex(BaselineError, "development_only"): prepare_protocol(self.doc, self.data, self.model)

    def test_real_bundle_extraction_cli_to_baseline_and_preflight(self):
        pair = self.doc["pairs"][0]
        f = pair["frames"]["focused"]
        # Small real-format producer bundle; the evidence artifact is deliberately separate.
        x, y, w, h = f["bounds"]
        meta = {"id": "sample", "focused_element_id": "e", "is_settled": True,
                "recipe": {"archetype": "grid_matrix", "theme": "light", "seed": 1, "recipe_hash": "hash"},
                "elements": [{"element_id": "e", "taxonomy_class": "collectionItem", "is_focused": True,
                              "pixel_bounds": f["bounds"], "normalized_bounds": [x/40, y/30, (x+w)/40, (y+h)/30]}]}
        (self.raw / "meta.json").write_text(json.dumps(meta))
        row = {"id": "sample", "split": "training", "expectedFocus": "e", "box": f["bounds"],
               "metadata": {"focusedPath": f["path"], "unfocusedPath": pair["frames"]["unfocused"]["path"], "metadataPath": "meta.json"}}
        for name, value in (("manifest.json", [row]), ("training.json", [row]), ("calibration.json", []), ("held-out.json", [])):
            (self.raw / name).write_text(json.dumps(value))
        artifacts = [{"path": p.name, "sha256": sha(p), "byteCount": p.stat().st_size} for p in sorted(self.raw.iterdir())]
        (self.raw / "dataset-index.json").write_text(json.dumps({"datasetLayoutVersion": 1, "telemetryContract": "harvest-canonical-v1; source-version-unverified",
            "provenance": "unverified-pixel-telemetry-binding", "normalizedCoordinates": "xyxy-top-left-unit", "pixelCoordinates": "xywh-top-left-pixels", "producer": "TVTestRig", "artifacts": artifacts}))
        (self.raw / "harvest-receipt.json").write_text(json.dumps({"schemaVersion": 1, "outcome": "completed", "acceptedRowCount": 1, "failure": None}))
        proof = {"version": "focus-pair-evidence-v1", "purpose": "development-pilot", "evidenceKind": "test-only", "sourceKind": "simulatorFixture",
                 "producerReference": "test-revision", "pairs": [{"pairID": "sample", "elementID": "e", "frames": pair["frames"]}]}
        evidence = self.root / "evidence.json"; evidence.write_text(json.dumps(proof))
        out = self.root / "extracted"
        args = ["--fixture-bundle", self.raw, "--output", out, "--corpus-id", "test-only", "--producer-reference", "test-revision"]
        r = self.cli("harvest_focus_pairs.py", *args)
        self.assertEqual(r.returncode, 1); self.assertFalse(out.exists())
        r = self.cli("harvest_focus_pairs.py", *args, "--pair-evidence", evidence, "--dry-run")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr); self.assertFalse(out.exists())
        r = self.cli("harvest_focus_pairs.py", *args, "--pair-evidence", evidence)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        produced = json.loads((out / "focus_dataset_manifest.json").read_text())
        self.assertEqual(validate_manifest(produced, out)[0]["split"], "development")
        self.assertEqual(produced["pairs"][0]["original_split"], "train")
        self.assertNotEqual(produced["pairs"][0]["focused_crop_box"], produced["pairs"][0]["unfocused_crop_box"])
        self.assertEqual(len(prepare_protocol(produced, out, self.model)["samples"]), 2)
        r = self.cli("train_focus_ring_detector.py", "--dataset", out, "--name", self.root.name, "--preflight")
        self.assertEqual(r.returncode, 2); self.assertFalse(json.loads(r.stdout)["launchEligible"])
        r = self.cli("validate_focus_ring_readiness.py", "--manifest", out / "focus_dataset_manifest.json")
        self.assertEqual(r.returncode, 2); self.assertIn("underfilled_quota", r.stderr)

    def test_related_recipe_variants_not_separate_groups(self):
        row = {"id": "a", "recipe": {"seed": 1, "recipe_hash": "a", "archetype": "grid_matrix", "theme": "light"},
               "split": "training", "elements": [], "focusedPath": "f", "unfocusedPath": "u", "focusedSHA256": "a", "unfocusedSHA256": "b"}
        other = copy.deepcopy(row); other["id"] = "b"; other["recipe"]["recipe_hash"] = "b"; other["recipe"]["theme"] = "dark"
        contract = {"usableRows": [row, other]}
        self.assertEqual(len(build(contract, "test", "rev", None)["pairs"]), 2)
        other["split"] = "held-out"
        with self.assertRaisesRegex(SimulatorManifestError, "group_split_leakage"): build(contract, "test", "rev", None)


if __name__ == "__main__":
    unittest.main()
