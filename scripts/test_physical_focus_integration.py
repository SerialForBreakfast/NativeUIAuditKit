"""Actual physical-source CLI integration using generated, explicitly test-only pixels."""
import copy
import hashlib
import json
import unittest
from pathlib import Path

from PIL import Image, PngImagePlugin
import test_focus_consumer_integration as fixture_module
from focus_dataset_contract import ROOT, FocusDataError, validate_manifest, validate_physical_review
from focus_runtime import recrop
from focus_proposal_evaluation import evaluate_proposals
from focus_ring_baseline import prepare_protocol


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


class PhysicalIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.f = fixture_module.ConsumerTests(); self.f.setUp()
        self.root = self.f.root; raw = self.f.raw
        pair = self.f.doc["pairs"][0]; frame = pair["frames"]["focused"]
        x, y, w, h = frame["bounds"]
        metadata = {"id": "sample", "focused_element_id": "e", "is_settled": True,
                    "recipe": {"archetype": "grid_matrix", "theme": "light", "seed": 1, "recipe_hash": "test-hash"},
                    "elements": [{"element_id": "e", "taxonomy_class": "collectionItem", "is_focused": True,
                                  "pixel_bounds": frame["bounds"], "normalized_bounds": [x/40, y/30, (x+w)/40, (y+h)/30]}]}
        (raw/"meta.json").write_text(json.dumps(metadata))
        row = {"id": "sample", "split": "training", "expectedFocus": "e", "box": frame["bounds"],
               "metadata": {"focusedPath": frame["path"], "unfocusedPath": pair["frames"]["unfocused"]["path"], "metadataPath": "meta.json"}}
        for name, value in (("manifest.json", [row]), ("training.json", [row]), ("calibration.json", []), ("held-out.json", [])):
            (raw/name).write_text(json.dumps(value))
        index = {"datasetLayoutVersion": 1, "telemetryContract": "harvest-canonical-v1; source-version-unverified",
                 "provenance": "unverified-pixel-telemetry-binding", "normalizedCoordinates": "xyxy-top-left-unit",
                 "pixelCoordinates": "xywh-top-left-pixels", "producer": "TVTestRig",
                 "artifacts": [{"path": p.name, "sha256": sha(p), "byteCount": p.stat().st_size} for p in sorted(raw.iterdir())]}
        (raw/"dataset-index.json").write_text(json.dumps(index))
        (raw/"harvest-receipt.json").write_text(json.dumps({"schemaVersion": 1, "outcome": "completed", "acceptedRowCount": 1, "failure": None}))
        self.proof = {"version": "focus-pair-evidence-v1", "purpose": "development-pilot", "evidenceKind": "test-only",
                      "sourceKind": "physicalFixture", "producerReference": "test-revision",
                      "sourceReview": {"sourceKind": "physicalFixture", "reviewReference": "unit-test-not-capture",
                                       "deviceReference": "test-device", "runID": "test-run", "captureID": "test-capture",
                                       "indexSHA256": sha(raw/"dataset-index.json"), "receiptSHA256": sha(raw/"harvest-receipt.json")},
                      "pairs": [{"pairID": "sample", "elementID": "e", "frames": pair["frames"]}]}
        for role, frame in self.proof["pairs"][0]["frames"].items():
            frame["nativeObservation"] = {"frameID": frame["frameID"], "imageSHA256": frame["sha256"],
                "nativeFocusResolved": True, "observedElementIDs": ["e" if role == "focused" else "tvtr.reference-focus"],
                "sampleAgeMilliseconds": 10, "stableMilliseconds": 150}

    def tearDown(self): self.f.tearDown()

    def extract(self, *, succeeds=True):
        proof_path = self.root/"proof.json"; proof_path.write_text(json.dumps(self.proof))
        output = self.root/"physical"
        result = self.f.cli("harvest_focus_pairs.py", "--fixture-bundle", self.f.raw, "--output", output,
                            "--corpus-id", "physical-test-only", "--producer-reference", "test-revision", "--pair-evidence", proof_path)
        self.assertEqual(result.returncode, 0 if succeeds else 1, result.stdout+result.stderr)
        if not succeeds: return result
        return json.loads((output/"focus_dataset_manifest.json").read_text()), output

    def test_actual_extraction_runtime_recrop_readiness_and_baseline_cli(self):
        doc, output = self.extract()
        self.assertEqual(doc["sourceKind"], "physicalFixture")
        self.assertEqual(doc["eligibility"]["simulatorUse"], "not-applicable")
        self.assertEqual(doc["pairs"][0]["original_split"], "train")
        self.assertNotEqual(doc["pairs"][0]["focused_crop_box"], doc["pairs"][0]["unfocused_crop_box"])
        runtime = self.root/"runtime"; recrop(doc, output, runtime)
        args = ["--manifest", runtime/"focus_dataset_manifest.json", "--model", self.f.model]
        result = self.f.cli("physical_focus_readiness.py", *args, "--output", self.root/"prepared.json")
        self.assertEqual(result.returncode, 0, result.stderr)
        prepared = json.loads((self.root/"prepared.json").read_text())
        self.assertTrue(prepared["integrityVerified"])
        self.assertFalse(prepared["eligible"])
        self.assertFalse(prepared["executionAuthorized"])
        self.assertEqual(prepared["cropParity"], "production-runtime")
        protocol = prepared["baselineProtocol"]; (self.root/"protocol.json").write_text(json.dumps(protocol))
        scores = {"formatVersion": "focus-baseline-scores-v1", "protocolSHA256": protocol["protocolSHA256"],
                  "artifactSHA256": protocol["artifact"]["sha256"], "inferenceKind": "test-only",
                  "scores": {s["id"]: .95 if s["label"] else .1 for s in protocol["samples"]}}
        (self.root/"scores.json").write_text(json.dumps(scores))
        result = self.f.cli("physical_focus_readiness.py", *args, "--protocol", self.root/"protocol.json",
                            "--scores", self.root/"scores.json", "--output", self.root/"scored.json")
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads((self.root/"scored.json").read_text())
        self.assertEqual(report["baseline"]["sourceKind"], "physicalFixture")
        self.assertEqual(report["baseline"]["evaluation"]["groups"]["overall"]["n"], 2)
        self.assertEqual(report["proposedBoxEvaluation"]["status"], "unavailable")
        runtime_doc = json.loads((runtime/"focus_dataset_manifest.json").read_text())
        pair = runtime_doc["pairs"][0]
        proposals = {"formatVersion": "focus-proposals-v1", "protocolSHA256": protocol["protocolSHA256"],
                     "artifactSHA256": protocol["artifact"]["sha256"], "inferenceKind": "test-only",
                     "samples": [{"id": f"{pair['pair_id']}:{label}", "imageSHA256": pair["frames"][role]["sha256"],
                                  "status": "success", "proposals": [{"bounds": pair["frames"][role]["bounds"], "score": .95 if label else .1}]}
                                 for role, label in (("focused", 1), ("unfocused", 0))]}
        (self.root/"proposals.json").write_text(json.dumps(proposals))
        result = self.f.cli("physical_focus_readiness.py", *args, "--proposals", self.root/"proposals.json",
                            "--output", self.root/"proposals-report.json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads((self.root/"proposals-report.json").read_text())["proposedBoxEvaluation"]["groups"]["overall"]["correct"], 2)
        result = self.f.cli("physical_focus_readiness.py", *args, "--output", self.root/"scored.json")
        self.assertEqual(result.returncode, 2)

    def test_missing_and_changed_physical_review(self):
        del self.proof["sourceReview"]
        self.assertIn("missing_physical_source_review", self.extract(succeeds=False).stdout)

    def test_nonhex_review_and_forged_source_are_rejected(self):
        review = self.proof["sourceReview"]
        review["indexSHA256"] = "z"*64
        with self.assertRaisesRegex(FocusDataError, "invalid_physical_review_hash"): validate_physical_review(review, self.f.raw)
        review["indexSHA256"] = "a"*64
        with self.assertRaisesRegex(FocusDataError, "binding_mismatch"): validate_physical_review(review, self.f.raw)

    def test_corrupt_hash_stale_and_prediction_truth_fail_before_output(self):
        frame = self.proof["pairs"][0]["frames"]["focused"]
        frame["focusFrameID"] = "old"
        self.assertIn("stale", self.extract(succeeds=False).stdout)
        frame["focusFrameID"] = frame["frameID"]; frame["labelSource"] = "modelPrediction"
        self.assertIn("untrusted", self.extract(succeeds=False).stdout)
        frame["labelSource"] = "fixtureCallback"; frame["sha256"] = "a"*64
        self.assertIn("unbound_native_observation", self.extract(succeeds=False).stdout)
        self.assertFalse((self.root/"physical").exists())

    def test_native_callback_missing_multiple_stale_and_wrong_geometry(self):
        frame = self.proof["pairs"][0]["frames"]["focused"]
        original = copy.deepcopy(frame)
        for change, message in (({"nativeFocusResolved": False}, "unknown_or_multiple"),
                                ({"observedElementIDs": ["e", "other"]}, "unknown_or_multiple"),
                                ({"sampleAgeMilliseconds": 151}, "stale_or_unsettled"),
                                ({"stableMilliseconds": 149}, "stale_or_unsettled")):
            frame.update(copy.deepcopy(original)); frame["nativeObservation"].update(change)
            self.assertIn(message, self.extract(succeeds=False).stdout)
        frame.update(copy.deepcopy(original)); frame["bounds"] = [1, 1, 12, 10]
        self.assertIn("evidence_geometry_mismatch", self.extract(succeeds=False).stdout)

    def test_partial_bundle_and_simulator_context_cannot_be_physical(self):
        index_path = self.f.raw/"dataset-index.json"; index = json.loads(index_path.read_text())
        index["sourceDescription"] = {"captureMethod": "simulator-screenshot", "collectedAt": "test-only", "assurance": "reported-source; not-attested"}
        index_path.write_text(json.dumps(index)); self.proof["sourceReview"]["indexSHA256"] = sha(index_path)
        self.assertIn("conflicting_physical_source", self.extract(succeeds=False).stdout)
        receipt = self.f.raw/"harvest-receipt.json"; receipt.write_text(json.dumps({"schemaVersion": 1, "outcome": "failed"}))
        self.proof["sourceReview"]["receiptSHA256"] = sha(receipt)
        self.extract(succeeds=False)

    def test_coordinate_representation_disagreement_rejected(self):
        path = self.f.raw/"meta.json"; metadata = json.loads(path.read_text())
        metadata["elements"][0]["normalized_bounds"] = [.1, .1, .9, .9]
        path.write_text(json.dumps(metadata))
        index_path = self.f.raw/"dataset-index.json"; index = json.loads(index_path.read_text())
        entry = next(a for a in index["artifacts"] if a["path"] == "meta.json")
        entry.update(sha256=sha(path), byteCount=path.stat().st_size)
        index_path.write_text(json.dumps(index)); self.proof["sourceReview"]["indexSHA256"] = sha(index_path)
        self.assertIn("coordinate_representation_mismatch", self.extract(succeeds=False).stdout)

    def test_dark_pilot_has_unavailable_hard_negatives_not_false_gate(self):
        from focus_ring_baseline import score_protocol
        doc, output = self.extract(); doc["pairs"][0]["theme"] = "dark"
        protocol = prepare_protocol(doc, output, self.f.model)
        scores = {"formatVersion": "focus-baseline-scores-v1", "protocolSHA256": protocol["protocolSHA256"],
                  "artifactSHA256": protocol["artifact"]["sha256"], "inferenceKind": "test-only",
                  "scores": {s["id"]: .95 if s["label"] else .1 for s in protocol["samples"]}}
        report = score_protocol(protocol, scores)
        self.assertIsNone(report["evaluation"]["hardNegative"]["fpr"])
        self.assertEqual(report["evaluation"]["hardNegative"]["status"], "unavailable")
        self.assertEqual(report["modelGatePassed"], "not_assessed")

    def test_decoded_content_leakage_not_just_png_hash(self):
        # Use the shared simulator contract to test a different encoding of same pixels.
        f = self.f; second = f.add_pair("b", "test", 2)
        first = f.doc["pairs"][0]
        for role in ("focused", "unfocused"):
            old = first["frames"][role]; new = second["frames"][role]
            metadata = PngImagePlugin.PngInfo(); metadata.add_text("encoding", "different")
            with Image.open(f.raw/old["path"]) as im: im.save(f.raw/new["path"], pnginfo=metadata)
            new["sha256"] = sha(f.raw/new["path"])
            # Crop bytes likewise change while decoded pixels stay identical.
            with Image.open(f.data/first[role+"_crop"]) as im: im.save(f.data/second[role+"_crop"], pnginfo=metadata)
            second[role+"_crop_sha256"] = sha(f.data/second[role+"_crop"])
            self.assertNotEqual(new["sha256"], old["sha256"])
        with self.assertRaisesRegex(FocusDataError, "split_leakage"): validate_manifest(f.doc, f.data)

    def test_proposal_selection_errors_abstentions_and_missing_results(self):
        doc, output = self.extract(); protocol = prepare_protocol(doc, output, self.f.model)
        pair = doc["pairs"][0]
        samples = [{"id": f"{pair['pair_id']}:{label}", "imageSHA256": pair["frames"][role]["sha256"], "status": "success",
                    "proposals": [{"bounds": pair["frames"][role]["bounds"], "score": .95 if label else .1}]}
                   for role, label in (("focused", 1), ("unfocused", 0))]
        proposals = {"formatVersion": "focus-proposals-v1", "protocolSHA256": protocol["protocolSHA256"],
                     "artifactSHA256": protocol["artifact"]["sha256"], "inferenceKind": "test-only", "samples": samples}
        self.assertEqual(evaluate_proposals(doc, protocol, proposals)["groups"]["overall"]["correct"], 2)
        for changes, expected in (([], "no_focus"), ([{"bounds": [25, 20, 10, 8], "score": .99}], "wrong_focus"),
                                  ([{"bounds": pair["frames"]["focused"]["bounds"], "score": .75}], "abstained")):
            samples[0]["proposals"] = changes
            self.assertEqual(evaluate_proposals(doc, protocol, proposals)["outcomes"][0]["outcome"], expected)
        samples[0]["proposals"] *= 2
        for p in samples[0]["proposals"]: p["score"] = .95
        self.assertEqual(evaluate_proposals(doc, protocol, proposals)["outcomes"][0]["outcome"], "multiple_focus")
        samples[0].update(status="failed", reason="model unavailable")
        self.assertEqual(evaluate_proposals(doc, protocol, proposals)["outcomes"][0]["outcome"], "failed")
        proposals["samples"] = []
        with self.assertRaisesRegex(FocusDataError, "membership"): evaluate_proposals(doc, protocol, proposals)


if __name__ == "__main__": unittest.main()
