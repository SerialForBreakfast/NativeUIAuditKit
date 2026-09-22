import json
from pathlib import Path
import tempfile
import unittest

from focus_dataset_contract import ROOT, FocusDataError
from export_focus_ring_coreml import export_paths
from focus_export_parity import compare, run, validate_model_identity


class ExportParityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT/".build/debug-output")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.weights = self.root/"model.pt"
        self.weights.write_bytes(b"test-only")

    def test_new_isolated_paths(self):
        self.assertEqual(export_paths(self.weights, self.root/"export", "fdr-test"), (self.weights, self.root/"export"))

    def test_collision_outside_missing_production_and_symlink(self):
        for weights, output, identifier in [
            (self.weights, self.root, "fdr-test"),
            (self.root/"absent", self.root/"new", "fdr-test"),
            (self.weights, Path("/outside-project"), "fdr-test"),
            (self.weights, ROOT/"NativeUIAuditKitModels/new", "fdr-test"),
            (self.weights, self.root/"new", "../bad")]:
            with self.assertRaises((ValueError, FocusDataError)): export_paths(weights, output, identifier)
        (self.root/"link").symlink_to(self.weights)
        with self.assertRaisesRegex(ValueError, "symlink"):
            export_paths(self.root/"link", self.root/"new", "fdr-test")

    def test_parity_and_threshold_crossing(self):
        a = [{"id": "one", "label": 1, "probability": .849}]
        self.assertTrue(compare(a, a)["passed"])
        result = compare(a, [{**a[0], "probability": .851}])
        self.assertFalse(result["passed"])
        self.assertEqual(result["differences"][0]["disagreedThresholds"], [.85])
        self.assertFalse(compare(a, [{**a[0], "probability": .82}])["passed"])

    def test_compiled_identity_binding(self):
        model = self.root/"model.mlmodelc"; model.mkdir()
        export = {"experimentalID": "test-only", "checkpointSHA256": "abc"}
        metadata = {"outputSchema": [{"name": "is_focused_prob"}], "userDefinedMetadata": {
            "modelID": "focus-ring-experimental-test-only", "checkpointSHA256": "abc",
            "releaseEligible": "false", "focusThreshold": "0.85", "ambiguityThreshold": "0.70"}}
        path = model/"metadata.json"; path.write_text(json.dumps([metadata]))
        self.assertIn("sha256", validate_model_identity(model, export))
        metadata["userDefinedMetadata"]["checkpointSHA256"] = "other"
        path.write_text(json.dumps([metadata]))
        with self.assertRaisesRegex(FocusDataError, "compiled_identity_mismatch"):
            validate_model_identity(model, export)

    def test_invalid_and_changed_evidence(self):
        a = [{"id": "one", "label": 1, "probability": .8}]
        for b in ([], [{**a[0], "id": "other"}], [{**a[0], "label": 0}], [{**a[0], "probability": float("nan")}], [{**a[0], "probability": 2}]):
            with self.assertRaises(FocusDataError): compare(a, b)
        with self.assertRaises(FocusDataError): compare(a+a, a+a)
        source = self.root/"source.json"; source.write_text("{}")
        with self.assertRaisesRegex(FocusDataError, "changed_experiment_input"):
            run(source, "wrong", self.root/"model", source, source, self.root/"out.json")
        with self.assertRaisesRegex(FocusDataError, "output_collision"):
            run(source, "wrong", self.root/"model", source, source, source)


if __name__ == "__main__": unittest.main()
