import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from PIL import Image
import temporal_focus_replay as r
from focus_mixed_assembly import reference


class TemporalTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=r.ROOT/".build/debug-output")
        self.root=Path(self.tmp.name)
        for name,color in (("before",(10,10,10)),("after",(220,220,220))):
            Image.new("RGB",(32,32),color).save(self.root/(name+".png"))
        def frame(name):
            ref=reference(self.root/(name+".png"))
            return {**ref,"width":32,"height":32}
        before,after=frame("before"),frame("after")
        source={"sourceKind":"test-only","sourceRoot":str(self.root.relative_to(r.ROOT)),
                "pairs":[{"split":"development","recipe_group":"test",
                "frames":{role:{"path":name+".png","sha256":ref["sha256"],"observedFocusID":focus}
                          for role,name,ref,focus in (("unfocused","before",before,None),("focused","after",after,"a"))}}]}
        source_ref=self.write("source.json",source)
        candidates=[{"id":name,"bounds":bounds,"scoreID":name,
                     "scores":{m:p for m in ("fdr007","fdr008","shipped")}}
                    for name,bounds,p in (("a",[0,0,8,8],.95),("b",[16,16,8,8],.9))]
        prior={"version":"appearance-family-development-evaluation-v1","manifests":{"test":source_ref},
               "competitionSamples":[{"id":c["id"],"elementID":c["id"],"frameID":"f","variant":"base",
                                       "bounds":c["bounds"],"path":after["path"],"sha256":after["sha256"],
                                       "label":int(c["id"]=="a")} for c in candidates]}
        prior["protocolSHA256"]=r.t.digest(prior)
        scores={"protocolSHA256":prior["protocolSHA256"],"results":{m:{"scores":{c["id"]:c["scores"][m] for c in candidates}}
                                                                             for m in ("fdr007","fdr008","shipped")}}
        self.doc={"version":"temporal-focus-development-v1","partition":"development","policy":r.POLICY,
                  "cachedProtocol":self.write("prior.json",prior),"cachedResults":self.write("scores.json",scores),
                  "cases":[{"id":"case","frameID":"f","kind":"reference-to-focus","group":"test",
                  "geometryOrigin":"reviewed-native-current-frame","before":before,"after":after,
                  "candidates":candidates,"truthID":"a"}]}
        self.seal(self.doc)

    def tearDown(self): self.tmp.cleanup()

    def write(self,name,value):
        path=self.root/name; path.write_text(json.dumps(value)); return reference(path)

    def seal(self,doc): doc["protocolSHA256"]=r.t.digest({k:v for k,v in doc.items() if k!="protocolSHA256"})

    def test_decisions_are_truth_independent_and_diff_does_not_become_box(self):
        c=self.doc["cases"][0]["candidates"]
        original=copy.deepcopy(c)
        regions=[[0,0,8,8]]
        self.assertIsNone(r.predict(c,regions,"shipped","single-frame")["selected"])
        for mode in ("diff-only","combined"):
            self.assertEqual(r.predict(c,regions,"shipped",mode)["selected"],"a")
        self.assertEqual(c,original)
        for x in c: x["truthID"]="b"
        self.assertEqual(r.predict(c,regions,"shipped","combined")["selected"],"a")

    def test_departure_arrival_ambiguity_background_and_no_change(self):
        c=self.doc["cases"][0]["candidates"]
        for regions in ([[0,0,8,8],[16,16,8,8]],[[10,10,2,2]]):
            self.assertIsNone(r.predict(c,regions,"shipped","combined")["selected"])
        c[1]["scores"]["shipped"]=.2
        self.assertEqual(r.predict(c,[],"shipped","combined")["selected"],"a")
        self.assertIsNone(r.predict(c,[],"shipped","diff-only")["selected"])
        c[0]["scores"]["shipped"]=.1
        self.assertIsNone(r.predict(c,[[0,0,8,8]],"shipped","combined")["selected"])

    def test_corrupt_dimensions_paths_missing_scores_and_labels_rejected(self):
        r.validate(self.doc)
        changes=[lambda c:c["after"].update(width=33),lambda c:c["after"].update(sha256="0"*64),
                 lambda c:c.update(truthID="b"),lambda c:c.update(geometryOrigin="diff-rectangle"),
                 lambda c:c["candidates"][0].update(bounds=[-1,0,8,8]),
                 lambda c:c["candidates"][0]["scores"].update(shipped=.1),
                 lambda c:c["candidates"].pop(),lambda c:c.update(kind="constructed-focus-switch")]
        for change in changes:
            doc=copy.deepcopy(self.doc);change(doc["cases"][0]);self.seal(doc)
            with self.assertRaises((ValueError,KeyError)):r.validate(doc)

    def test_holdout_policy_and_changed_protocol_rejected(self):
        for key,value in (("partition","test"),("version","new"),("policy",{})):
            doc=copy.deepcopy(self.doc);doc[key]=value;self.seal(doc)
            with self.assertRaises(ValueError):r.validate(doc)
        self.doc["cases"][0]["group"]="altered"
        with self.assertRaisesRegex(ValueError,"changed_protocol"):r.validate(self.doc)

    def test_timeout_invalid_regions_and_wrong_decision_accounted(self):
        def timeout(*args):raise subprocess.TimeoutExpired("test",1)
        result=r.evaluate(self.doc,Path("unused"),measure=timeout)
        self.assertEqual(result["completedCases"],0);self.assertEqual(len(result["errors"]),1)
        def measured(sequence,*args):
            return {r.t.pair_id(*sequence["frames"]):{"regions":[[16,16,8,8]]}},{}
        result=r.evaluate(self.doc,Path("unused"),measure=measured)
        self.assertEqual(result["summary"]["reference-to-focus/shipped/combined"]["wrong"],1)
        self.assertFalse(result["integrationQualified"])
        def bad_region(sequence,*args):
            return {r.t.pair_id(*sequence["frames"]):{"regions":[[31,31,8,8]]}},{}
        result=r.evaluate(self.doc,Path("unused"),measure=bad_region)
        self.assertEqual(result["completedCases"],0)
        self.assertIn("out_of_frame_box",result["errors"][0]["error"])

    def test_real_cli_and_output_collision(self):
        manifest=self.root/"input.json";manifest.write_text(json.dumps(self.doc))
        out=self.root/"report.json"
        cmd=[sys.executable,str(r.ROOT/"scripts/temporal_focus_replay.py"),"--manifest",str(manifest),"--output",str(out)]
        run=subprocess.run(cmd,cwd=r.ROOT,capture_output=True,text=True,timeout=90)
        self.assertEqual(run.returncode,0,run.stdout+run.stderr)
        result=json.loads(out.read_text());self.assertEqual(result["completedCases"],1)
        before=out.read_bytes()
        run=subprocess.run(cmd,cwd=r.ROOT,capture_output=True,text=True,timeout=15)
        self.assertEqual(run.returncode,2);self.assertEqual(out.read_bytes(),before)


if __name__=="__main__":unittest.main()
