import hashlib
import json
import shutil
import unittest
from pathlib import Path
from unittest.mock import patch

from perception_benchmark import BenchmarkError, ROOT, inventory, main, recommendation, score, validate_manifest, verify_evidence


SHA = "a" * 64


def case(case_id="c1", image=SHA, group="journey-a", partition="development", source="testOnly"):
    return {
        "caseID": case_id, "sourceKind": source, "imageSHA256": image, "width": 100, "height": 100,
        "journeyID": group, "splitGroup": group, "partition": partition,
        "labels": {
            "origin": "reviewedVisual",
            "rows": [{"id": "row-a", "box": [0, 0, 80, 20]}, {"id": "cancel", "box": [10, 50, 20, 10]}, {"id": "delete", "box": [50, 50, 20, 10]}],
            "chevrons": [{"id": "chevron-a", "box": [80, 5, 10, 10], "rowID": "row-a", "visibility": "visible"}],
            "dialog": {"box": [5, 35, 90, 45], "buttonIDs": ["cancel", "delete"], "focusedButtonID": "cancel", "semantic": "destructive", "semanticOrigin": "reviewed"},
            "focus": {"elementID": "cancel", "frameID": case_id},
        },
    }


def predictions(case_id="c1", status="available"):
    document = {"formatVersion": "perception-predictions-v1", "status": status}
    if status == "unavailable": document["reason"] = "shipped inference not assigned"; return document
    item = {
        "caseID": case_id,
        "proposals": {"chevrons": [{"box": [80, 5, 10, 10], "rowID": "row-a"}], "dialog": {"box": [5, 35, 90, 45], "buttonIDs": ["cancel", "delete"], "focusedButtonID": "cancel", "semantic": "destructive"}},
        "oracle": {"chevrons": [{"box": [80, 5, 10, 10], "rowID": "row-a"}], "dialog": {"box": [5, 35, 90, 45], "buttonIDs": ["cancel", "delete"], "focusedButtonID": "cancel", "semantic": "destructive"}},
    }
    document["cases"] = [item]; return document


class PerceptionBenchmarkTests(unittest.TestCase):
    def test_valid_manifest_inventory_and_unavailable_inference(self):
        cases = validate_manifest({"formatVersion": "perception-benchmark-v1", "cases": [case()]})
        self.assertEqual(inventory(cases)["coverage"]["chevron:visible"], 1)
        result = score(predictions(status="unavailable"), cases)
        self.assertEqual(result["status"], "unavailable")
        self.assertEqual(recommendation(cases, result)["action"], "no_training")

    def test_scores_oracle_and_actual_and_flags_safety_error(self):
        cases = validate_manifest({"formatVersion": "perception-benchmark-v1", "cases": [case()]})
        document = predictions(); document["cases"][0]["proposals"]["chevrons"][0]["rowID"] = "cancel"
        document["cases"][0]["proposals"]["dialog"]["semantic"] = "informational"
        result = score(document, cases)
        counts = result["actualProposals"]["counts"]
        self.assertEqual(counts["wrongRowLink"], 1)
        self.assertEqual(counts["destructiveAsBenign"], 1)
        self.assertEqual(result["oracleBoxes"]["endToEndDisclosureRecall"], 1.0)

    def test_rejects_leakage_predictions_as_truth_and_stale_focus(self):
        first, second = case(), case("c2", image="b" * 64, partition="test")
        second["journeyID"] = "journey-b"; second["splitGroup"] = "journey-b"
        with self.assertRaisesRegex(BenchmarkError, "duplicate_content_leakage"):
            validate_manifest({"formatVersion": "perception-benchmark-v1", "cases": [first, case("c3", group="other")]})
        bad = case(); bad["labels"]["origin"] = "modelPrediction"
        with self.assertRaisesRegex(BenchmarkError, "unreviewed_or_prediction"):
            validate_manifest({"formatVersion": "perception-benchmark-v1", "cases": [bad]})
        bad = case(); bad["labels"]["focus"]["frameID"] = "old-frame"
        with self.assertRaisesRegex(BenchmarkError, "stale_or_invalid_focus"):
            validate_manifest({"formatVersion": "perception-benchmark-v1", "cases": [bad]})

    def test_rejects_ambiguous_relation_and_incomplete_prediction_membership(self):
        bad = case(); bad["labels"]["chevrons"][0]["rowID"] = "missing"
        with self.assertRaisesRegex(BenchmarkError, "ambiguous_chevron_relation"):
            validate_manifest({"formatVersion": "perception-benchmark-v1", "cases": [bad]})
        cases = validate_manifest({"formatVersion": "perception-benchmark-v1", "cases": [case(), case("c2", image="b" * 64, group="journey-b")]})
        with self.assertRaisesRegex(BenchmarkError, "incomplete_predictions"):
            score(predictions(), cases)
        document = predictions(); del document["cases"][0]["oracle"]
        single = validate_manifest({"formatVersion": "perception-benchmark-v1", "cases": [case()]})
        with self.assertRaisesRegex(BenchmarkError, "missing_oracle_or_proposal"):
            score(document, single)

    def test_verifies_explicit_bytes_and_refuses_output_collision(self):
        work = ROOT / ".build" / "debug-output" / "perception-benchmark-test"
        shutil.rmtree(work, ignore_errors=True); work.mkdir(parents=True)
        try:
            from PIL import Image
            image = work / "image.png"; Image.new("RGB",(100,100)).save(image)
            original=image.read_bytes()
            document = {"formatVersion": "perception-benchmark-v1", "cases": [case(image=hashlib.sha256(image.read_bytes()).hexdigest())]}
            document["cases"][0]["imagePath"] = str(image)
            cases = validate_manifest(document)
            self.assertEqual(verify_evidence(cases)["verifiedImageCount"], 1)
            image.write_bytes(b"altered")
            with self.assertRaisesRegex(BenchmarkError, "image_hash_mismatch"):
                verify_evidence(cases)
            image.write_bytes(original)
            manifest, prediction, output = work / "manifest.json", work / "predictions.json", work / "report.json"
            manifest.write_text(json.dumps(document)); prediction.write_text(json.dumps(predictions()))
            with patch("sys.argv", ["perception_benchmark.py", "--manifest", str(manifest), "--predictions", str(prediction), "--output", str(output), "--verify-bytes"]):
                self.assertEqual(main(), 0)
            report = json.loads(output.read_text())
            self.assertEqual(report["byteVerification"]["verifiedImageCount"], 1)
            with patch("sys.argv", ["perception_benchmark.py", "--manifest", str(manifest), "--predictions", str(prediction), "--output", str(output)]):
                self.assertEqual(main(), 2)
        finally:
            shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__": unittest.main()
