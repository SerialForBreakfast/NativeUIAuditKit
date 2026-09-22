import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from PIL import Image
from audit_training_evidence import audit_focus, audit_captures, ROOT
import eval_focus_ring_detector as evaluator
from perception_benchmark import verify_evidence, validate_manifest, BenchmarkError, score, main as benchmark_main
from test_perception_benchmark import case, predictions


class AuditTests(unittest.TestCase):
    def setUp(self):
        base=ROOT/".build/debug-output/evidence-audit"; base.mkdir(parents=True,exist_ok=True)
        self.tmp=tempfile.TemporaryDirectory(dir=base); self.root=Path(self.tmp.name)
        self.focus=self.root/"focus"; self.focus.mkdir()
        self.captures=self.root/"captures"; self.captures.mkdir()
        for name,color in (("f.png","red"),("u.png","blue")):
            Image.new("RGB",(256,256),color).save(self.focus/name)
        self.doc={"version":"1.0","pairs":[{"pair_id":"a","recipe_seed":1,"split":"test","theme":"dark",
            "element_type":"collectionItem","focused_crop":"f.png","unfocused_crop":"u.png"}]}
        self.save()
    def tearDown(self): self.tmp.cleanup()
    def save(self): (self.focus/"focus_dataset_manifest.json").write_text(json.dumps(self.doc))

    def test_deterministic_accounting_is_not_qualification(self):
        first=audit_focus(self.focus); self.assertEqual(first,audit_focus(self.focus))
        self.assertEqual(first["decodedCompletePairs"],1); self.assertEqual(first["invalidMembers"],0)
        self.assertFalse(first["trainingEligible"]); self.assertEqual(first["frameEvidencePairs"],0)

    def test_missing_corrupt_wrong_size_and_traversal(self):
        for name in ("missing.png","../u.png"):
            self.doc["pairs"][0]["unfocused_crop"]=name; self.save()
            self.assertEqual(audit_focus(self.focus)["invalidMembers"],1)
        self.doc["pairs"][0]["unfocused_crop"]="u.png"; self.save()
        (self.focus/"u.png").write_bytes(b"not png")
        self.assertEqual(audit_focus(self.focus)["invalidMembers"],1)
        Image.new("RGB",(12,12)).save(self.focus/"u.png")
        self.assertEqual(audit_focus(self.focus)["invalidMembers"],1)

    def test_different_seeds_do_not_prove_pixel_independence(self):
        self.doc["pairs"].append({**self.doc["pairs"][0],"pair_id":"b","recipe_seed":2,"split":"train"})
        self.save(); result=audit_focus(self.focus)
        self.assertFalse(result["seedCrossSplit"])
        self.assertEqual(len(result["crossSplitPixelGroups"]),2)
        self.doc["pairs"][1]["recipe_seed"]=1; self.save()
        self.assertEqual(audit_focus(self.focus)["seedCrossSplit"],["1"])

    def test_capture_hash_decode_orphans_and_prediction_exclusion(self):
        Image.new("RGB",(10,20)).save(self.captures/"a.png")
        Image.new("RGB",(10,20)).save(self.captures/"orphan.png")
        doc={"imageSHA256":hashlib.sha256((self.captures/"a.png").read_bytes()).hexdigest(),"image":{"pixelWidth":10,"pixelHeight":20},"elements":[]}
        (self.captures/"a.json").write_text(json.dumps(doc))
        (self.captures/"a_result.json").write_text('{"elements":[{"prediction":true}]}')
        result=audit_captures(self.captures)
        self.assertEqual(result["sidecarCount"],1); self.assertEqual(len(result["orphans"]),1)
        self.assertTrue(result["captures"][0]["image"]["valid"])
        self.assertTrue(result["captures"][0]["shaMatches"])
        self.assertFalse(result["trainingEligible"])

    def test_real_audit_cli_and_no_overwrite(self):
        output=self.root/"report.json"
        cmd=[sys.executable,str(ROOT/"scripts/audit_training_evidence.py"),"--focus",str(self.focus),"--captures",str(self.captures),"--output",str(output)]
        r=subprocess.run(cmd,capture_output=True,text=True); self.assertEqual(r.returncode,0,r.stderr)
        before=output.read_bytes(); r=subprocess.run(cmd,capture_output=True,text=True)
        self.assertEqual(r.returncode,2); self.assertEqual(output.read_bytes(),before)

    def test_legacy_eval_requires_explicit_diagnostic_and_isolated_output(self):
        weights=self.root/"weights.pt"; weights.write_bytes(b"mock artifact; never loaded")
        out=self.root/"eval"
        args=["eval","--dataset",str(self.focus),"--weights",str(weights),"--output-dir",str(out)]
        with patch("sys.argv",args),patch.object(evaluator,"predict_torch") as predict:
            self.assertEqual(evaluator.main(),2); predict.assert_not_called()
        self.assertFalse(out.exists())
        with patch.dict(os.environ),patch("sys.argv",args+["--diagnostic-only"]),patch.object(evaluator,"predict_torch",return_value=[.99,.01]) as predict:
            self.assertEqual(evaluator.main(),0); predict.assert_called_once()
        result=json.loads((out/"focus_ring_detector_eval_report.json").read_text())
        hard=json.loads((out/"focus_ring_detector_hard_negative_eval.json").read_text())
        self.assertFalse(result["all_gates_pass"]); self.assertEqual(result["modelGatePassed"],"not_assessed")
        self.assertIsNone(hard["fpr"]); self.assertFalse(hard["pass"])
        with patch("sys.argv",args+["--diagnostic-only"]),patch.object(evaluator,"predict_torch") as predict:
            self.assertEqual(evaluator.main(),2); predict.assert_not_called()

    def test_eval_missing_member_fails_before_prediction(self):
        self.doc["pairs"][0]["focused_crop"]="missing.png"; self.save()
        with self.assertRaisesRegex(ValueError,"invalid_test_member"): evaluator.load_split(self.focus,"test")

    def test_perception_real_cli_requires_pixels_without_optional_flag(self):
        c=case(source="physicalFixture"); c["imagePath"]=str(self.root/"missing.png")
        manifest=self.root/"manifest.json"; manifest.write_text(json.dumps({"formatVersion":"perception-benchmark-v1","cases":[c]}))
        pred=self.root/"pred.json"; pred.write_text(json.dumps(predictions(status="unavailable")))
        output=self.root/"perception.json"
        with patch("sys.argv",["benchmark","--manifest",str(manifest),"--predictions",str(pred),"--output",str(output)]):
            self.assertEqual(benchmark_main(),2)
        self.assertFalse(output.exists())

    def test_hash_matching_corrupt_and_wrong_dimension_images_rejected(self):
        image=self.root/"bad.png"; image.write_bytes(b"garbage")
        c=case(image=hashlib.sha256(image.read_bytes()).hexdigest()); c["imagePath"]=str(image)
        with self.assertRaisesRegex(BenchmarkError,"corrupt_image"): verify_evidence([c])
        Image.new("RGB",(10,10)).save(image); c["imageSHA256"]=hashlib.sha256(image.read_bytes()).hexdigest()
        with self.assertRaisesRegex(BenchmarkError,"wrong_crop_dimensions"): verify_evidence([c])

    def test_unknown_semantics_abstains_not_benign(self):
        p=predictions(); p["cases"][0]["proposals"]["dialog"]["semantic"]="unknown"
        counts=score(p,[case()])["actualProposals"]["counts"]
        self.assertEqual(counts["semanticAbstentions"],1); self.assertEqual(counts.get("destructiveAsBenign",0),0)

    def test_nonfinite_and_boolean_boxes_rejected(self):
        for v in (float("nan"),float("inf"),True):
            c=case(); c["labels"]["rows"][0]["box"][0]=v
            with self.assertRaisesRegex(BenchmarkError,"invalid_box"):
                validate_manifest({"formatVersion":"perception-benchmark-v1","cases":[c]})

    def test_physical_cli_cannot_promote_metadata_and_preserves_output(self):
        from test_physical_focus_readiness import pair
        manifest=self.root/"physical.json"; output=self.root/"physical-report.json"
        manifest.write_text(json.dumps({"formatVersion":"focus-ring-physical-readiness-v1","pairs":[pair()]}))
        cmd=[sys.executable,str(ROOT/"scripts/physical_focus_readiness.py"),"--manifest",str(manifest),"--output",str(output)]
        r=subprocess.run(cmd,capture_output=True,text=True); self.assertEqual(r.returncode,0,r.stderr)
        self.assertFalse(json.loads(output.read_text())["eligible"])
        original=output.read_bytes(); r=subprocess.run(cmd,capture_output=True,text=True)
        self.assertEqual(r.returncode,2); self.assertEqual(output.read_bytes(),original)

    def test_empty_incomplete_nonfinite_and_out_of_range_probabilities(self):
        for rows,probs in (([],[]),([{"label":1}],[]),([{"label":1}],[float("nan")]),([{"label":0}],[1.1])):
            with self.assertRaises(ValueError): evaluator.metrics(rows,probs)

    def test_hard_negatives_require_all_strata_and_support(self):
        rows=[{"label":0,"theme":t,"element_type":k} for t in ("light","highContrast") for k in ("imageView","collectionItem") for _ in range(25)]
        self.assertTrue(evaluator.hard_negative_report(rows,[0.0]*100)["pass"])
        self.assertFalse(evaluator.hard_negative_report(rows[:-1],[0.0]*99)["pass"])
        rows[-25:]=copy.deepcopy(rows[:25])
        self.assertFalse(evaluator.hard_negative_report(rows,[0.0]*100)["pass"])

if __name__=="__main__": unittest.main()
