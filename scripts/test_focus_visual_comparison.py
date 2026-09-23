import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from focus_dataset_contract import ROOT, FocusDataError, digest
from focus_visual_comparison import samples, score, destination, freeze, run, validate_protocol, sha
from test_perception_native_review import native_case


class VisualComparisonTests(unittest.TestCase):
    def setUp(self):
        parent=ROOT/"reports/work/FOCUS-VISUAL-01/test-tmp"
        parent.mkdir(parents=True,exist_ok=True)
        self.tmp=tempfile.TemporaryDirectory(dir=parent); self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        from PIL import Image
        image=self.root/"image.png"; Image.new("RGB",(100,100)).save(image)
        item=native_case(); item.update(imagePath=str(image),imageSHA256=sha(image))
        self.manifest=self.root/"manifest.json"
        self.manifest.write_text(json.dumps({"formatVersion":"perception-benchmark-v1","cases":[item]}))
        self.models=self.root/"models.json"
        self.models.write_text(json.dumps({n:str(self.root/n) for n in ("shipped","fp16","int8")}))
        self.protocol=self.root/"protocol.json"

    def rows(self): return samples(json.loads(self.manifest.read_text()))

    def test_membership_and_padding(self):
        rows=self.rows()
        self.assertEqual(len(rows),21)
        self.assertEqual(sum(r["label"] for r in rows),7)
        padded=next(r for r in rows if r["elementID"]=="row-a" and r["variant"]=="pad4")
        self.assertEqual(padded["bounds"],[0,0,84,24])

    def test_changed_pixels_rejected(self):
        item=json.loads(self.manifest.read_text()); item["cases"][0]["imageSHA256"]="0"*64
        with self.assertRaisesRegex(ValueError,"image_hash_mismatch"): samples(item)

    def test_missing_competitor_geometry(self):
        item=json.loads(self.manifest.read_text()); del item["cases"][0]["labels"]["rows"][0]["box"]
        with self.assertRaisesRegex(ValueError,"missing_competing_control_boxes"): samples(item)

    def test_false_callback_truth_rejected(self):
        item=json.loads(self.manifest.read_text()); item["cases"][0]["labels"]["focus"]["basis"]="callback"
        with self.assertRaisesRegex(ValueError,"unsupported_native_focus_claim"): samples(item)

    def test_frame_decisions_and_no_forced_argmax(self):
        rows=[r for r in self.rows() if r["variant"]=="base"]
        for probabilities,expected in (([.1,.9,.1],"correct"),([.9,.1,.1],"wrong-focus"),([.1,.7,.1],"no-focus"),([.9,.9,.1],"multiple-focus-abstention")):
            predictions=[{"id":r["id"],"probability":p} for r,p in zip(rows,probabilities)]
            self.assertEqual(score(rows,predictions)["base"]["frameDecisions"][0]["decision"],expected)

    def test_invalid_scores_and_order(self):
        rows=self.rows(); predictions=[{"id":r["id"],"probability":.5} for r in rows]
        with self.assertRaisesRegex(ValueError,"prediction_membership_mismatch"): score(rows,list(reversed(predictions)))
        for invalid in (float("nan"),2,True,None):
            predictions[0]["probability"]=invalid
            with self.assertRaisesRegex(ValueError,"invalid_probability"): score(rows,predictions)

    def test_output_safety(self):
        with self.assertRaisesRegex(ValueError,"output_collision"): destination(self.manifest)
        with self.assertRaisesRegex(ValueError,"report_output_required"): destination(ROOT/"no-report-test")
        link=self.root/"link"; link.symlink_to(self.root)
        with self.assertRaisesRegex(ValueError,"symlink_output"): destination(link/"out")

    def test_actual_freeze_and_run_with_fake_inference(self):
        contract={"sha256":"a"*64,"outputs":["is_focused_prob"]}
        with patch("focus_visual_comparison.model_contract",return_value=contract), patch("focus_visual_comparison.identity",return_value={"testOnly":True}):
            doc=freeze(self.manifest,self.models,self.protocol)
            def fake(items,model):
                self.assertTrue(all(i["bounds"] for i in items))
                return {"results":[{"id":i["id"],"probability":.9 if ":cancel:" in i["id"] else .1} for i in items],"batches":[]}
            with patch("focus_visual_comparison.infer_bounded",side_effect=fake) as inference:
                report=run(self.protocol,self.root/"evaluation")
                self.assertEqual(inference.call_count,3)
                self.assertTrue(all(not r["disagreedThresholds"] for r in report["compressionDifferences"]))
                self.assertFalse(report["trainingEligible"])
                self.assertEqual(report["support"],{"reviewedFrames":1,"reviewedBoxes":3,"correlatedVariantsPerBox":7})
                self.assertNotIn("Photos",str(report["limitations"]))
            broken=dict(doc); broken["thresholds"]=[.1]
            with self.assertRaisesRegex(ValueError,"changed_protocol"): validate_protocol(broken)
            broken["protocolSHA256"]=digest({k:v for k,v in broken.items() if k!="protocolSHA256"})
            with self.assertRaisesRegex(ValueError,"unsupported_protocol"): validate_protocol(broken)
            self.manifest.write_text("{}")
            with self.assertRaisesRegex(ValueError,"changed_manifest"): validate_protocol(doc)

    def test_model_change_blocks_before_inference(self):
        with patch("focus_visual_comparison.model_contract",return_value={"sha256":"a"*64}), patch("focus_visual_comparison.identity",return_value={}):
            doc=freeze(self.manifest,self.models,self.protocol)
        with patch("focus_visual_comparison.model_contract",return_value={"sha256":"b"*64}), patch("focus_visual_comparison.identity",return_value={}):
            with self.assertRaisesRegex(ValueError,"changed_model"): validate_protocol(doc)
