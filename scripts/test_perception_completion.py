"""Offline integration; observations and labels are intentionally separate fixtures."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from perception_benchmark import ROOT, BenchmarkError, main, score, validate_manifest, verify_evidence
from perception_adapters import baseline, observation_predictions, report, latency_report
from test_perception_benchmark import case, predictions


def observations():
    return {"formatVersion": "perception-observations-v1",
            "adapter": {"id": "unit-test", "kind": "test-only", "artifactSHA256": "a"*64, "preprocessingSHA256": "b"*64},
            "cases": [{"caseID": "c1", "imageSHA256": "a"*64, "status": "success", "locale": "en",
                       "rows": [{"id": "det-row", "box": [0, 0, 80, 20], "role": "row", "confidence": .99},
                                {"id": "det-cancel", "box": [10, 50, 20, 10], "role": "button", "confidence": .99, "focusScore": .95},
                                {"id": "det-delete", "box": [50, 50, 20, 10], "role": "button", "confidence": .99, "focusScore": .1}],
                       "chevrons": [{"box": [80, 5, 10, 10], "confidence": .95}],
                       "dialogs": [{"box": [5, 35, 90, 45], "confidence": .99}],
                       "ocr": [{"box": [20, 40, 30, 5], "text": "Delete history?", "confidence": .99}]}]}


class CompletionTests(unittest.TestCase):
    def setUp(self):
        self.manifest = {"formatVersion": "perception-benchmark-v1", "cases": [case()]}
        self.cases = validate_manifest(self.manifest)

    def test_independent_adapter_geometry_and_truth_not_model_input(self):
        obs = observations(); pred = observation_predictions(obs, self.cases)
        result = score(pred, self.cases)
        self.assertEqual(result["actualProposals"]["counts"]["associatedTP"], 1)
        self.assertEqual(result["actualProposals"]["counts"]["dialogFocusTP"], 1)
        original = copy.deepcopy(pred["cases"][0]["proposals"])
        self.cases[0]["labels"]["dialog"].update(semantic="informational", focusedButtonID="delete")
        changed = observation_predictions(obs, self.cases)
        self.assertEqual(changed["cases"][0]["proposals"], original)
        self.assertEqual(changed["cases"][0]["oracle"]["dialog"]["semantic"], "destructive")

    def test_missing_payload_is_not_empty_success(self):
        for mode in ("proposals", "oracle"):
            for missing in ("chevrons", "dialog"):
                pred = predictions(); del pred["cases"][0][mode][missing]
                with self.assertRaisesRegex(BenchmarkError, "missing_prediction_modality"):
                    score(pred, self.cases)
        pred = predictions()
        for mode in ("proposals", "oracle"):
            pred["cases"][0][mode] = {"chevrons": [], "dialog": None}
        self.assertEqual(score(pred, self.cases)["scoredCases"], 1)

    def test_unknown_row_is_not_a_claimed_wrong_row(self):
        pred = predictions(); proposal = pred["cases"][0]["proposals"]["chevrons"][0]
        proposal["rowID"] = None
        counts = score(pred, self.cases)["actualProposals"]["counts"]
        self.assertEqual(counts["localizedTP"], 1)
        self.assertEqual(counts["associationAbstentions"], 1)
        self.assertEqual(counts.get("wrongRowLink", 0), 0)
        self.assertEqual(report(self.manifest, pred, None, self.cases, {})["developmentErrorAnalysis"][0]["category"], "association_geometry")
        proposal["rowID"] = "wrong"
        self.assertEqual(score(pred, self.cases)["actualProposals"]["counts"]["wrongRowLink"], 1)

    def test_boolean_dimensions_rejected(self):
        for key in ("width", "height"):
            manifest = copy.deepcopy(self.manifest); manifest["cases"][0][key] = True
            with self.assertRaisesRegex(BenchmarkError, "invalid_dimensions"):
                validate_manifest(manifest)

    def test_unknown_language_abstains_and_multiple_focus_does_not_guess(self):
        obs = observations(); row = obs["cases"][0]; row["locale"] = "fr"
        row["rows"][2]["focusScore"] = .95
        result = score(observation_predictions(obs, self.cases), self.cases)
        counts = result["actualProposals"]["counts"]
        self.assertEqual(counts["semanticAbstentions"], 1)
        self.assertEqual(counts.get("destructiveAsBenign", 0), 0)
        self.assertEqual(counts["dialogFocusError"], 1)

    def test_nested_dialog_and_ambiguous_row_abstain(self):
        obs = observations(); row = obs["cases"][0]
        row["dialogs"].append({"box": [10, 40, 70, 30], "confidence": .95})
        row["rows"].append({"id": "nested", "box": [2, 0, 80, 20], "role": "row", "confidence": .95})
        pred = observation_predictions(obs, self.cases)["cases"][0]["proposals"]
        self.assertTrue(pred["ambiguousDialog"])
        self.assertIsNone(pred["dialog"])
        self.assertIsNone(pred["chevrons"][0]["rowID"])

    def test_clipped_visible_pixels_and_duplicate_proposals(self):
        self.cases[0]["labels"]["chevrons"][0]["visibility"] = "clipped"
        validate_manifest(self.manifest)
        pred = predictions(); pred["cases"][0]["proposals"]["chevrons"] *= 2
        counts = score(pred, self.cases)["actualProposals"]["counts"]
        self.assertEqual(counts["localizedTP"], 1)
        self.assertEqual(counts["decorativeArrowFP"], 1)

    def test_failure_unavailable_and_empty_success_separate(self):
        for state in ("failed", "unavailable"):
            obs = observations(); obs["cases"][0].update(status=state, reason="not assigned")
            result = score(observation_predictions(obs, self.cases), self.cases)
            self.assertEqual(result["scoredCases"], 0)
            self.assertEqual(result["failures"][0]["status"], state)
        obs = observations(); row = obs["cases"][0]
        for k in ("rows", "chevrons", "dialogs", "ocr"): row[k] = []
        result = score(observation_predictions(obs, self.cases), self.cases)
        self.assertEqual(result["scoredCases"], 1)
        self.assertEqual(result["actualProposals"]["counts"]["abstentions"], 1)

    def test_frame_binding_and_invalid_payloads(self):
        for mutate in (lambda o: o["cases"][0].update(imageSHA256="b"*64),
                       lambda o: o["cases"][0]["rows"][0].update(confidence=float("nan")),
                       lambda o: o["cases"][0]["rows"][0].update(focusScore=True),
                       lambda o: o["cases"].append(copy.deepcopy(o["cases"][0])),
                       lambda o: o["adapter"].update(artifactSHA256="z"*64)):
            o = observations(); mutate(o)
            with self.assertRaises(BenchmarkError): observation_predictions(o, self.cases)

    def test_zero_support_unknown_slices_and_imported_claim_not_training(self):
        self.cases[0]["sourceKind"] = "physicalFixture"
        self.cases[0]["partition"] = "test"
        result = report(self.manifest, predictions(), observations(), self.cases, {})
        self.assertEqual(result["recommendation"]["action"], "no_training")
        self.assertIn("theme:unknown", result["prediction"]["slices"])
        self.assertEqual(result["comparisons"]["ttrRaster"]["status"], "unavailable")
        self.assertIsNone(result["prediction"]["uncertainty"]["disclosureRecallInterval"])
        empty = score({"formatVersion": "perception-predictions-v1", "status": "available", "cases": []}, [])
        self.assertIsNone(empty["actualProposals"]["endToEndDisclosureRecall"])

    def test_replay_slices_bindings_and_group_bootstrap(self):
        second = case("c2", "b"*64, "journey-b")
        second.update(theme="dark", control="listRow", locale="fr", focusTreatment="scale")
        self.manifest["cases"].append(second); cases = validate_manifest(self.manifest)
        pred = predictions(); pred["cases"].append(predictions("c2")["cases"][0])
        result = report(self.manifest, pred, None, cases, {})
        self.assertEqual(result, report(self.manifest, pred, None, cases, {}))
        self.assertEqual(result["prediction"]["uncertainty"]["disclosureRecallInterval"], [1, 1])
        original = result["bindings"]["manifestSHA256"]
        second["theme"] = "light"
        self.assertNotEqual(original, report(self.manifest, pred, None, cases, {})["bindings"]["manifestSHA256"])

    def test_latency_context_and_no_fake_deployment_claim(self):
        timing = {"kind": "test-only", "machine": "fixture", "os": "fixture", "scope": "inference", "cold": [10], "warm": [1, 2, 3]}
        result = latency_report({"latency": timing})
        self.assertEqual(result["warm"]["p95"], 3)
        self.assertFalse(result["deploymentQualified"])
        timing["warm"] = [float("nan")]
        with self.assertRaises(BenchmarkError): latency_report({"latency": timing})

    def test_actual_cli_with_baseline_and_collision(self):
        base = ROOT/".build/debug-output"; base.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=base) as tmp:
            work = Path(tmp)
            for name, value in (("manifest", self.manifest), ("predictions", predictions()), ("observations", observations())):
                (work/f"{name}.json").write_text(json.dumps(value))
            argv = ["perception_benchmark.py", "--manifest", str(work/"manifest.json"), "--predictions", str(work/"predictions.json"), "--observations", str(work/"observations.json"), "--output", str(work/"report.json")]
            with patch("sys.argv", argv): self.assertEqual(main(), 0)
            result = json.loads((work/"report.json").read_text())
            self.assertEqual(result["comparisons"]["geometryOCR"]["status"], "available")
            with patch("sys.argv", argv): self.assertEqual(main(), 2)

    def test_different_encoding_cannot_evade_pixel_split_check(self):
        import hashlib
        from PIL import Image, PngImagePlugin
        base = ROOT/".build/debug-output"; base.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=base) as tmp:
            members = []
            for i, partition in enumerate(("development", "test")):
                path = Path(tmp)/f"{i}.png"
                metadata = PngImagePlugin.PngInfo(); metadata.add_text("variant", str(i))
                Image.new("RGB", (100, 100), "blue").save(path, pnginfo=metadata)
                c = case(f"c{i}", hashlib.sha256(path.read_bytes()).hexdigest(), f"group{i}", partition)
                c["imagePath"] = str(path); members.append(c)
            with self.assertRaisesRegex(BenchmarkError, "decoded_content_split_leakage"):
                verify_evidence(validate_manifest({"formatVersion": "perception-benchmark-v1", "cases": members}))


if __name__ == "__main__": unittest.main()
