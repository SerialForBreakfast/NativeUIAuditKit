"""PER-05 causal policy, strict inputs, and real production primitive/CLI tests."""
import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from PIL import Image, ImageDraw, PngImagePlugin
import transition_benchmark as t


def policy():
    return dict(version="transition-policy-v1", reference="test-policy-not-calibrated", frozenOn="test-only",
                distanceThreshold=.001, noiseThreshold=10, stableMs=200, minimumFrames=3,
                maxGapMs=150, maxAgeMs=100, timeoutMs=1000, toolTimeoutSeconds=60)


def sequence(times=(0,100,200,300)):
    return dict(id="s", group="journey", partition="development", sourceKind="test-only",
                sourceReference="deterministic-generator-v1", labelOrigin="synthetic-generator",
                reviewReference="software-test-only", scenario="static", startMs=0,
                foregroundRegions=[[16,16,80,80]], regionOrigin="caller-configured", focusSource="test-only",
                frames=[dict(id=str(i),observationID="obs"+str(i),capturedMs=ms,observedMs=ms,
                             focus="present",truth="ready") for i,ms in enumerate(times)])


def measurements(s, changed=None):
    changed = changed or {}
    return {t.pair_id(a,b): dict(distance=changed.get((a["id"],b["id"]),0),regions=[])
            for i,b in enumerate(s["frames"]) for a in s["frames"][:i]}


class PolicyTests(unittest.TestCase):
    def test_stable_and_causal_future_truth_independence(self):
        s=sequence(); m=measurements(s); original=t.predict(s,m,policy(),"full-frame")
        self.assertEqual([x["state"] for x in original],["wait","wait","ready","ready"])
        s["frames"][-1]["truth"]="unstable"; s["frames"][-1]["focus"]="none"
        new=t.predict(s,m,policy(),"full-frame")
        self.assertEqual(original[:-1],new[:-1]); self.assertEqual(new[-1]["state"],"unknown")
        prefix=copy.deepcopy(s); prefix["frames"]=prefix["frames"][:3]
        self.assertEqual(original[:3],t.predict(prefix,m,policy(),"full-frame"))

    def test_anchor_catches_slow_drift_and_support_bounded(self):
        s=sequence((0,50,100,150,200,250,300))
        m=measurements(s,{("0","4"):.1})
        result=t.predict(s,m,policy(),"full-frame")
        self.assertEqual(result[4]["reason"],"visual_change")
        self.assertTrue(all(x["state"]!="ready" for x in result))
        self.assertTrue(all(len(x["support"])<=3 for x in result))
        stable=t.predict(s,measurements(s),policy(),"full-frame")
        self.assertEqual(stable[4]["state"],"ready")
        self.assertEqual(stable[4]["support"][0],"obs0")

    def test_missing_stale_repeated_outoforder_future_and_focus(self):
        changes=[({"missing":True},"missing"),({"capturedMs":0},"stale_or_future"),
                 ({"observationID":"obs0"},"repeated_observation"),({"capturedMs":250},"stale_or_future"),
                 ({"focus":"none"},"focus_none"),({"focus":"unknown"},"focus_unknown")]
        for change,reason in changes:
            s=sequence(); s["frames"][2].update(change)
            r=t.predict(s,measurements(s),policy(),"foreground-roi")
            self.assertEqual(r[2]["reason"],reason); self.assertNotEqual(r[3]["state"],"ready")
        s=sequence((0,100,110));s["frames"][2]["capturedMs"]=90
        self.assertEqual(t.predict(s,measurements(s),policy(),"full-frame")[2]["reason"],"capture_order")

    def test_cadence_gap_timeout_and_missing_measurement(self):
        s=sequence((0,100,300,400,500,1000,1100))
        r=t.predict(s,measurements(s),policy(),"full-frame")
        self.assertEqual(r[2]["reason"],"cadence_gap");self.assertEqual(r[4]["state"],"ready")
        self.assertEqual([x["state"] for x in r[-2:]],["timeout","timeout"])
        self.assertEqual(t.predict(sequence(),{},policy(),"full-frame")[1]["reason"],"missing_measurement")

    def test_background_motion_vs_foreground_and_metrics_support(self):
        s=sequence();m=measurements(s)
        for x in m.values(): x.update(distance=1,regions=[[110,110,10,10]])
        a=t.predict(s,m,policy(),"full-frame"); b=t.predict(s,m,policy(),"foreground-roi")
        self.assertFalse(any(d["state"]=="ready" for d in a));self.assertEqual(b[-1]["state"],"ready")
        s["frames"][2]["truth"]="unstable";s["frames"][3]["truth"]="unknown"
        score=t.score(s,b);self.assertEqual(score["counts"]["prematureReady"],1)
        self.assertEqual(score["counts"]["unscoredReady"],1)
        self.assertIsNone(t.summarize([])["prematureReadyRate"])
        for x in m.values(): x["regions"]=[[20,20,5,5]]
        self.assertFalse(any(d["state"]=="ready" for d in t.predict(s,m,policy(),"foreground-roi")))

    def test_ready_intervals_and_unknown_not_false_wait(self):
        s=sequence();d=t.predict(s,measurements(s),policy(),"full-frame")
        self.assertEqual(t.score(s,d)["readyIntervalDelayMs"],[200])
        for f in s["frames"]: f["focus"]="none"
        score=t.score(s,t.predict(s,measurements(s),policy(),"full-frame"))
        self.assertEqual(score["readyIntervalDelayMs"],[None]);self.assertNotIn("falseWaits",score["counts"])


class IntegrationTests(unittest.TestCase):
    def setUp(self):
        root=t.ROOT/".build/debug-output/per05-tests";root.mkdir(parents=True,exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(dir=root);self.root=Path(self.temp.name)
        self.s=sequence();self.doc=dict(version="transition-sequences-v1",corpusID="test-only",sequences=[self.s])
        for i,f in enumerate(self.s["frames"]):
            image=Image.new("RGB",(128,128),(30,30,30));draw=ImageDraw.Draw(image)
            draw.rectangle((16,16,95,95),fill=(180,180,180));draw.rectangle((20,25,70,35),fill=(60,60,60))
            path=self.root/f"{i}.png";image.save(path)
            f.update(path=path.name,sha256=t.file_hash(path),width=128,height=128)
        self.helper=t.ROOT/".build/debug/TransitionTool"
        self.assertTrue(self.helper.is_file(),"Build TransitionTool before running integration tests")

    def tearDown(self):self.temp.cleanup()

    def test_validation_corrupt_missing_hash_dimensions_escape_and_bounds(self):
        t.validate(self.doc,self.root,policy())
        for change,error in [({"sha256":"f"*64},"image_hash"),({"path":"absent.png"},"missing"),
                             ({"width":1},"dimensions"),({"path":"../escape.png"},"image_path")]:
            doc=copy.deepcopy(self.doc);doc["sequences"][0]["frames"][0].update(change)
            with self.assertRaisesRegex(t.Invalid,error):t.validate(doc,self.root,policy())
        self.s["foregroundRegions"]=[[120,0,40,40]]
        with self.assertRaisesRegex(t.Invalid,"region_outside"):t.validate(self.doc,self.root,policy())

    def test_leakage_reencoded_pixels_group_and_false_provenance(self):
        other=copy.deepcopy(self.s);other.update(id="other",group="different",partition="test")
        self.doc["sequences"].append(other)
        meta=PngImagePlugin.PngInfo();meta.add_text("changed","encoding")
        with Image.open(self.root/"0.png") as im:im.save(self.root/"encoded.png",pnginfo=meta)
        other["frames"][0].update(path="encoded.png",sha256=t.file_hash(self.root/"encoded.png"))
        with self.assertRaisesRegex(t.Invalid,"pixel_leakage"):t.validate(self.doc,self.root,policy())
        other["group"]="journey"
        with self.assertRaisesRegex(t.Invalid,"group_leakage"):t.validate(self.doc,self.root,policy())
        self.doc["sequences"].pop();self.s["sourceKind"]="physical"
        with self.assertRaisesRegex(t.Invalid,"false_real"):t.validate(self.doc,self.root,policy())

    def test_version_policy_prediction_labels_and_declared_missing(self):
        for field,value,error in [("labelOrigin","modelPrediction","prediction_truth"),("focusSource","labels","focus_source"),("regionOrigin","oracle","regions_origin")]:
            d=copy.deepcopy(self.doc);d["sequences"][0][field]=value
            with self.assertRaisesRegex(t.Invalid,error):t.validate(d,self.root,policy())
        p=policy();p["frozenOn"]="test"
        with self.assertRaisesRegex(t.Invalid,"test_fitted"):t.validate_policy(p)
        f=self.s["frames"][1];f["missing"]=True
        for k in ("path","sha256","width","height"):del f[k]
        t.validate(self.doc,self.root,policy())
        self.doc["version"]="v900"
        with self.assertRaisesRegex(t.Invalid,"version"):t.validate(self.doc,self.root,policy())

    def test_real_swift_primitives_asymmetric_roi_and_replay(self):
        # Bottom-right background motion must not intersect top-left foreground.
        for i in (1,3):
            path=self.root/f"{i}.png"
            with Image.open(path) as im:
                draw=ImageDraw.Draw(im);draw.rectangle((108,108,127,127),fill=(255,255,255));im.save(path)
            self.s["frames"][i]["sha256"]=t.file_hash(path)
        self.s["scenario"]="background-carousel"
        r=t.evaluate(self.doc,self.root,policy(),self.helper)
        self.assertEqual(r["status"],"complete",r["failures"])
        decisions=r["results"][0]["policies"]["foreground-roi"]["decisions"]
        self.assertEqual(decisions[-1]["state"],"ready")
        self.assertGreater(r["latency"]["firstPairMs"]["n"],0)
        r2=t.evaluate(self.doc,self.root,policy(),self.helper)
        self.assertEqual(r["results"],r2["results"]);self.assertEqual(r["summary"],r2["summary"])
        self.assertFalse(r["outcomes"]["dataEligible"])

    def test_real_crossfade_focus_animation_and_scroll(self):
        for scenario in ("crossfade","focus-animation","scroll"):
            self.s["scenario"]=scenario
            for i,f in enumerate(self.s["frames"]):
                path=self.root/f"{i}.png";im=Image.new("RGB",(128,128),(30,30,30));draw=ImageDraw.Draw(im)
                if scenario=="crossfade":draw.rectangle((16,16,95,95),fill=(60+i*50,)*3)
                else:draw.rectangle((20+i*12,20,30+i*12,90),fill=(255,255,255))
                im.save(path);f["sha256"]=t.file_hash(path);f["truth"]="unstable"
            r=t.evaluate(self.doc,self.root,policy(),self.helper)
            self.assertEqual(r["status"],"complete",r["failures"])
            self.assertEqual(r["summary"]["foreground-roi"]["overall"]["counts"].get("readyDecisions",0),0)

    def test_cli_output_collision_json_and_partial_execution(self):
        manifest=self.root/"manifest.json";manifest.write_text(json.dumps(self.doc))
        p=self.root/"policy.json";p.write_text(json.dumps(policy()));out=self.root/"report.json"
        cmd=[sys.executable,str(t.ROOT/"scripts/transition_benchmark.py"),"--manifest",str(manifest),"--policy",str(p),"--output",str(out)]
        result=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,"PYTHONDONTWRITEBYTECODE":"1"})
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        before=out.read_bytes();self.assertEqual(subprocess.run(cmd,capture_output=True).returncode,2);self.assertEqual(out.read_bytes(),before)
        def failed(*args):raise t.Invalid("fake execution failure")
        r=t.evaluate(self.doc,self.root,policy(),self.helper,failed)
        self.assertEqual(r["status"],"partial");self.assertEqual(r["accounting"]["failedSequences"],1)
        self.assertEqual(r["summary"]["full-frame"]["overall"]["sequences"],0)
        manifest.write_text('{"version":1,"version":2}')
        with self.assertRaisesRegex(t.Invalid,"duplicate"):t.read_json(manifest)

    def test_helper_hash_rejection_and_dimension_mismatch(self):
        a=self.s["frames"][0];b=self.s["frames"][1]
        request={"version":1,"root":str(self.root),"noiseThreshold":10,"pairs":[{"id":"pair","previous":{"path":str(self.root/a["path"]),"sha256":"0"*64},"current":{"path":str(self.root/b["path"]),"sha256":b["sha256"]}}]}
        result=subprocess.run([str(self.helper)],input=json.dumps(request),text=True,capture_output=True)
        self.assertEqual(result.returncode,2);self.assertIn("changedBytes",result.stderr)
        request["pairs"][0]["previous"]["sha256"]=a["sha256"]
        image=Image.new("RGB",(64,128));image.save(self.root/b["path"])
        request["pairs"][0]["current"]["sha256"]=t.file_hash(self.root/b["path"])
        result=subprocess.run([str(self.helper)],input=json.dumps(request),text=True,capture_output=True)
        self.assertEqual(result.returncode,2);self.assertIn("dimensionMismatch",result.stderr)

    def test_bounds_timeout_and_unknown_version(self):
        s=copy.deepcopy(self.s);s["frames"]=s["frames"]*17;self.doc["sequences"]=[s]
        with self.assertRaisesRegex(t.Invalid,"frame_bound"):t.validate(self.doc,self.root,policy())
        self.doc["sequences"]=[self.s]
        with patch.object(t.subprocess,"run",side_effect=subprocess.TimeoutExpired("TransitionTool",60)) as call:
            r=t.evaluate(self.doc,self.root,policy(),self.helper)
            self.assertEqual(call.call_count,1);self.assertEqual(r["accounting"]["failedSequences"],1)
            self.assertIsNone(r["summary"]["full-frame"]["scenario:scroll"]["prematureReadyRate"])
        result=subprocess.run([str(self.helper)],input=json.dumps({"version":9,"root":str(self.root),"noiseThreshold":10,"pairs":[]}),text=True,capture_output=True)
        self.assertEqual(result.returncode,2)

    def test_generator_reproducibility_and_cli_fixture_report(self):
        from generate_transition_fixture import generate
        a=generate(self.root/"a");b=generate(self.root/"b")
        self.assertEqual((a/"manifest.json").read_bytes(),(b/"manifest.json").read_bytes())
        with self.assertRaises(t.Invalid):generate(a)
        manifest=t.read_json(a/"manifest.json");p=t.read_json(a/"policy.json")
        r=t.evaluate(manifest,a,p,self.helper)
        self.assertEqual(r["status"],"complete",r["failures"])
        self.assertEqual(r["accounting"]["evaluatedSequences"],9)
        self.assertEqual(r["summary"]["foreground-roi"]["overall"]["timedOutSequences"],1)

    def test_corrupt_primitive_regions_cannot_become_foreground_ready(self):
        rows = [{"id": t.pair_id(a,b), "distance": 0, "milliseconds": 1,
                 "regions": [[200,200,10,10]]}
                for i,b in enumerate(self.s["frames"]) for a in self.s["frames"][:i]]
        for regions in ([[200,200,10,10]], [[127,127,2,2]], [[0,0,1,1]]*129):
            for row in rows: row["regions"] = regions
            reply = subprocess.CompletedProcess([], 0, json.dumps({"version":1,"host":"test","results":rows}), "")
            with patch.object(t.subprocess, "run", return_value=reply):
                result = t.evaluate(self.doc,self.root,policy(),self.helper)
            self.assertEqual(result["status"], "partial")
            self.assertEqual(result["accounting"]["failedSequences"], 1)
            self.assertEqual(result["results"], [])


if __name__=="__main__":unittest.main()
