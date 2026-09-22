"""PER-06 actual production anchor adapter plus adversarial identity contracts."""
import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image, PngImagePlugin
import identity_benchmark as m
from generate_identity_fixture import corpus, policy, base_case, generate


class IdentityTests(unittest.TestCase):
    def setUp(self):
        root=m.ROOT/".build/debug-output/per06-tests";root.mkdir(parents=True,exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(dir=root);self.root=Path(self.temp.name)
        self.helper=m.ROOT/".build/debug/AnchorTool";self.assertTrue(self.helper.is_file(),"Build AnchorTool first")
        self.case=base_case();self.doc=dict(version="identity-benchmark-v1",corpusID="unit-test",cases=[self.case]);self.p=policy()

    def tearDown(self):self.temp.cleanup()

    def predict(self,c=None):
        c=c or self.case;a,_=m.anchor_results(c["references"],c["query"],self.p,self.helper)
        return m.match(c["references"],c["query"],self.p,a,c.get("cachedScreenID"),c.get("cachedEpoch"))

    def test_actual_anchor_and_strict_title_collision(self):
        p=self.predict();self.assertEqual(p["screenID"],"general");self.assertEqual(p["rows"]["q0"]["candidate"],"name")
        self.case["query"]["texts"][0]["text"]="General Information"
        p=self.predict();self.assertEqual(p["anchorOnlyScreenID"],"general");self.assertIsNone(p["screenID"])
        self.assertFalse(p["actionAuthorized"])

    def test_truth_split_cache_id_and_future_cases_do_not_select_match(self):
        p=self.predict();self.case["truth"]={"expectedScreenID":None,"rows":{"q0":None,"q1":None}}
        self.case.update(partition="test",group="other",cachedScreenID="other")
        q=self.predict();self.assertEqual(p["screenID"],q["screenID"]);self.assertEqual(p["rows"],q["rows"])
        self.assertIn("changed_screen",q["routeInvalidations"])
        self.assertEqual(m.score(self.case,q)["conservative"]["falseMatches"],1)

    def test_scroll_hidden_rows_and_changed_values(self):
        for name in ("scroll","hidden-row","changed-value"):
            c=next(c for c in corpus()["cases"] if c["id"]==name);p=self.predict(c)
            self.assertEqual(p["screenID"],"general")
            self.assertEqual({k:v["candidate"] for k,v in p["rows"].items()},c["truth"]["rows"])
        self.assertEqual(len(self.predict(next(c for c in corpus()["cases"] if c["id"]=="hidden-row"))["rows"]),1)

    def test_duplicate_rows_and_screen_ties_abstain(self):
        for name in ("repeated-label","ambiguous-screen"):
            c=next(c for c in corpus()["cases"] if c["id"]==name);p=self.predict(c)
            self.assertIsNone(p["screenID"]);self.assertTrue(all(r["candidate"] is None for r in p["rows"].values()))
        rows=m.match_rows(next(c for c in corpus()["cases"] if c["id"]=="repeated-label")["references"][0],next(c for c in corpus()["cases"] if c["id"]=="repeated-label")["query"],self.p)
        self.assertEqual(rows["q0"]["reason"],"ambiguous_label")

    def test_locale_support_without_translation(self):
        c=next(c for c in corpus()["cases"] if c["id"]=="spanish");self.assertEqual(self.predict(c)["screenID"],"general")
        c["references"].append(base_case()["references"][0])
        self.doc["cases"]=[c];m.validate(self.doc,self.root,self.p)
        self.assertEqual(self.predict(c)["rows"]["q0"]["candidate"],"name")
        c=next(c for c in corpus()["cases"] if c["id"]=="unsupported-french");p=self.predict(c)
        self.assertEqual(p["reason"],"unsupported_locale");self.assertEqual(m.score(c,p)["conservative"]["missedMatches"],1)
        self.p["supportedLocales"].append("fr");self.assertEqual(self.predict(c)["reason"],"unregistered_locale")

    def test_stale_future_overlay_failed_empty_and_epoch(self):
        for change,reason in (({"observedMs":2000},"stale_or_future"),({"capturedMs":300},"stale_or_future"),
                              ({"overlays":[dict(confidence=.9,bounds=[.1,.1,.8,.8])]},"overlay")):
            c=copy.deepcopy(self.case);c["query"].update(change);p=self.predict(c)
            self.assertEqual(p["reason"],reason);self.assertIn(reason,p["routeInvalidations"])
        for state in ("failed","unavailable"):
            c=copy.deepcopy(self.case);c["query"].update(status=state,rows=[],texts=[])
            self.assertEqual(self.predict(c)["reason"],"recognition_"+state)
        c=copy.deepcopy(self.case);c["query"]["texts"]=[]
        self.assertEqual(self.predict(c)["reason"],"missing_or_inexact_anchors")
        self.case["cachedEpoch"]="old";p=self.predict();self.assertEqual(p["screenID"],"general");self.assertIn("changed_epoch",p["routeInvalidations"])

    def test_geometry_mismatch_low_confidence_and_overlapping_rows(self):
        q=self.case["query"];q["rows"][0]["confidence"]=.1
        p=self.predict();self.assertIsNone(p["rows"]["q0"]["candidate"]);self.assertIn("unresolved_rows",p["routeInvalidations"])
        q["rows"][0]["confidence"]=.99;q["rows"][1]["bounds"]=q["rows"][0]["bounds"][:]
        labels=m.labels(q,self.p);self.assertTrue(all(not v for v in labels.values()))
        q=self.case["query"]=base_case()["query"];r=self.case["references"][0]
        r["snapshot"]["rows"][0]["bounds"]=[.1,.3,.4,.12]
        rows=m.match_rows(r,q,self.p);self.assertEqual(rows["q0"]["reason"],"geometry_mismatch")

    def test_false_screen_makes_row_identity_wrong_even_same_local_id(self):
        p=self.predict();c=copy.deepcopy(self.case)
        other=copy.deepcopy(c["references"][0]);other["screenID"]="other";c["references"].append(other);c["truth"]["expectedScreenID"]="other"
        counts=m.score(c,p)["conservative"];self.assertEqual(counts["falseRowMatches"],2);self.assertEqual(counts["correctRows"],0)
        self.assertIsNone(m.summarize([])["retrievalAccuracy"])

    def test_policy_versions_thresholds_and_prediction_labels(self):
        m.validate(self.doc,self.root,self.p)
        for field,value in (("minimumMargin",float('nan')),("maxAgeMs",0),("minimumRowMatches",True),("toolTimeoutSeconds",31),("frozenOn","test")):
            p=copy.deepcopy(self.p);p[field]=value
            with self.assertRaises(m.Invalid):m.validate_policy(p)
        self.case["labelOrigin"]="modelPrediction"
        with self.assertRaisesRegex(m.Invalid,"prediction_truth"):m.validate(self.doc,self.root,self.p)
        self.doc["version"]="v2"
        with self.assertRaisesRegex(m.Invalid,"version"):m.validate(self.doc,self.root,self.p)

    def test_group_and_observation_leakage_and_unmapped_truth(self):
        c=copy.deepcopy(self.case);c.update(id="second",partition="test");self.doc["cases"].append(c)
        with self.assertRaisesRegex(m.Invalid,"journey_leakage"):m.validate(self.doc,self.root,self.p)
        c["group"]="another"
        c["query"]["texts"].reverse();c["references"][0]["snapshot"]["texts"].reverse()
        with self.assertRaisesRegex(m.Invalid,"observation_leakage"):m.validate(self.doc,self.root,self.p)
        self.doc["cases"].pop();self.case["truth"]["rows"]["q0"]="invented"
        with self.assertRaisesRegex(m.Invalid,"truth_row_target"):m.validate(self.doc,self.root,self.p)

    def attach_image(self,s,path):
        with Image.open(path) as im:w,h=im.size
        sha=m.file_hash(path);s.update(imageSHA256=sha,image=dict(path=path.name,sha256=sha,width=w,height=h))

    def test_image_integrity_corruption_binding_and_pixel_leakage(self):
        path=self.root/"image.png";Image.new("RGB",(20,20),(120,30,90)).save(path);self.attach_image(self.case["query"],path)
        m.validate(self.doc,self.root,self.p)
        self.case["query"]["imageSHA256"]="f"*64
        with self.assertRaisesRegex(m.Invalid,"hash_binding"):m.validate(self.doc,self.root,self.p)
        self.attach_image(self.case["query"],path)
        c=copy.deepcopy(self.case);c.update(id="second",group="other",partition="test")
        # Remove equal observation-content overlap, retain reencoded identical pixels.
        c["references"][0]["snapshot"]["texts"][0]["text"]="Different reference"
        c["query"]["texts"][0]["text"]="Different query"
        meta=PngImagePlugin.PngInfo();meta.add_text("different","encoding")
        with Image.open(path) as im:im.save(self.root/"encoded.png",pnginfo=meta)
        self.attach_image(c["query"],self.root/"encoded.png");self.doc["cases"].append(c)
        with self.assertRaisesRegex(m.Invalid,"pixel_leakage"):m.validate(self.doc,self.root,self.p)
        self.doc["cases"].pop();path.write_bytes(b"not a PNG");self.case["query"]["imageSHA256"]=self.case["query"]["image"]["sha256"]=m.file_hash(path)
        with self.assertRaises(OSError):m.validate(self.doc,self.root,self.p)

    def test_recorded_source_requires_bound_pixels_and_non_test_policy(self):
        self.case.update(sourceKind="physical",labelOrigin="reviewed-human");self.p["frozenOn"]="validation"
        with self.assertRaisesRegex(m.Invalid,"missing_recorded_image"):m.validate(self.doc,self.root,self.p)

    def test_real_cli_replay_slices_and_no_overwrite(self):
        source=generate(self.root/"fixture");other=generate(self.root/"same")
        self.assertEqual((source/"manifest.json").read_bytes(),(other/"manifest.json").read_bytes())
        output=self.root/"report.json"
        cmd=[sys.executable,str(m.ROOT/"scripts/identity_benchmark.py"),"--manifest",str(source/"manifest.json"),"--policy",str(source/"policy.json"),"--output",str(output)]
        proc=subprocess.run(cmd,text=True,capture_output=True,env={**os.environ,"PYTHONDONTWRITEBYTECODE":"1"});self.assertEqual(proc.returncode,0,proc.stdout+proc.stderr)
        report=json.loads(output.read_text());self.assertEqual(report["accounting"]["evaluatedCases"],15)
        self.assertIsNone(report["summary"]["conservative"]["sourceKind:physical"]["retrievalAccuracy"])
        again=m.evaluate(corpus(),source,self.p,self.helper);self.assertEqual(report["results"],again["results"]);self.assertEqual(report["summary"],again["summary"])
        self.assertGreater(report["latency"]["anchorEvaluationMs"]["n"],0)
        before=output.read_bytes();self.assertEqual(subprocess.run(cmd,capture_output=True).returncode,2);self.assertEqual(output.read_bytes(),before)

    def test_bounded_timeout_bad_helper_and_partial_accounting(self):
        with patch.object(m.subprocess,"run",side_effect=subprocess.TimeoutExpired("AnchorTool",10)) as run:
            report=m.evaluate(self.doc,self.root,self.p,self.helper);self.assertEqual(run.call_count,1)
        self.assertEqual(report["status"],"partial");self.assertEqual(report["accounting"]["failedCases"],1)
        self.assertIsNone(report["summary"]["conservative"]["overall"]["falseMatchRate"])
        request=dict(version=9,items=[])
        proc=subprocess.run([str(self.helper)],input=json.dumps(request),text=True,capture_output=True);self.assertEqual(proc.returncode,2)
        self.case["query"]["rows"]*=33
        with self.assertRaisesRegex(m.Invalid,"bound_rows"):m.validate(self.doc,self.root,self.p)

    def test_forbidden_anchor_empty_confidence_and_duplicate_reference(self):
        self.case["query"]["texts"][0]["text"]="Delete General"
        p=self.predict();self.assertIsNone(p["anchorOnlyScreenID"])
        self.assertEqual(p["anchorEvidence"]["general"]["matchedForbidden"],["Delete"])
        self.case["query"]["texts"][0]["text"]="General";self.case["query"]["texts"][0]["confidence"]=.1
        self.assertIsNone(self.predict()["screenID"])
        self.case["references"].append(copy.deepcopy(self.case["references"][0]))
        with self.assertRaisesRegex(m.Invalid,"duplicate_reference_locale"):m.validate(self.doc,self.root,self.p)

    def test_helper_bounds_and_invalid_success_payload(self):
        item=dict(id="x",required=["General"],optional=[],forbidden=[],regions=[dict(text="General",bounds=[0,0,2,.1])])
        p=subprocess.run([str(self.helper)],input=json.dumps(dict(version=1,items=[item])),capture_output=True,text=True)
        self.assertEqual(p.returncode,2);self.assertIn("bounds",p.stderr)
        fake=subprocess.CompletedProcess([],0,json.dumps(dict(version=1,results=[])),"")
        with patch.object(m.subprocess,"run",return_value=fake):
            report=m.evaluate(self.doc,self.root,self.p,self.helper)
        self.assertEqual(report["status"],"partial");self.assertIn("anchor_membership",report["failures"][0]["reason"])
        item={"id":m.reference_key(self.case["references"][0]),"status":"verified","milliseconds":0}
        fake.stdout=json.dumps(dict(version=1,results=[item],host="test-only"))
        with patch.object(m.subprocess,"run",return_value=fake):
            report=m.evaluate(self.doc,self.root,self.p,self.helper)
        self.assertIn("anchor_evidence",report["failures"][0]["reason"])

    def test_geometry_not_backend_order_controls_rows(self):
        original=self.predict();self.case["query"]["rows"].reverse();self.case["query"]["texts"].reverse()
        reordered=self.predict();self.assertEqual(original["rows"],reordered["rows"])
        self.assertEqual(original["screenID"],reordered["screenID"])


if __name__=="__main__":unittest.main()
