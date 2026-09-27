"""Generated, project-local fixtures; no TTR connection, capture or model inference."""
import base64
import copy
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

from PIL import Image, ImageDraw
import photos_focus_pilot as p
from focus_dataset_contract import ROOT, FocusDataError, validate_manifest
from focus_appearance_experiment import assemble
from focus_surface_evaluation import validate as validate_evaluation


def envelope(kind, value, command):
    return dict(schemaVersion=1, success=True, command=command, requestID="fixture-request",
                durationMilliseconds=10, data={kind: {"_0": value}})


class PhotosPilotTests(unittest.TestCase):
    def setUp(self):
        (ROOT/".build/debug-output").mkdir(parents=True, exist_ok=True)
        self.root = Path(tempfile.mkdtemp(prefix="photos-pilot-test-", dir=ROOT/".build/debug-output"))
        self.source = self.root/"source"; self.source.mkdir()
        status = envelope("status", dict(selectedDeviceID="office-test", sessionID={"rawValue": "session-test"},
            connectionStatus="connected", commandActive=False, queuedCommandCount=0), "session status")
        self.dump(self.source/"status.json", status)
        self.spec = dict(version=p.INDEX, targetID="office-test", sourceDeviceID="provider-office-test",
                         sessionID="session-test", operator="test-only", sourceBindingReference="test-only-fixture",
                         sessionEvidence=self.relative("status.json"), frames=[])
        for i in range(2):
            name = f"frame-{i}"
            im = Image.new("RGB", (320, 180), (20, 25, 30))
            draw = ImageDraw.Draw(im)
            draw.rectangle((35, 50, 110, 105), fill="white" if i == 0 else "gray")
            draw.rectangle((170, 50, 260, 105), fill="gray" if i == 0 else "white")
            im.save(self.source/(name+".png"))
            stamp = dict(wallClock=800000000+i, monotonic={"nanoseconds": i*1_000_000_000})
            obs = dict(id={"rawValue": name}, sourceDeviceID="provider-office-test", capturedAt=stamp,
                       receivedAt=stamp, providerID="capture-test", connectionGeneration=1,
                       dimensions=dict(width=320, height=180), mimeType="image/png", orientation="up",
                       freshness=dict(status="current", confidence="exact", estimatedAgeMilliseconds=0),
                       captureDurationMilliseconds=10, precedingCommandIDs=[], outputWritten=True)
            self.dump(self.source/(name+".json"), envelope("observation", obs, "observe capture"))
            self.spec["frames"].append(dict(id=name, screenID="photos-dialog", image=self.relative(name+".png"),
                                             observation=self.relative(name+".json")))
        self.input = self.source/"index.json"; self.save_spec()

    def tearDown(self):
        shutil.rmtree(self.root)

    def dump(self, path, value):
        path.write_text(json.dumps(value))

    def relative(self, name):
        return dict(path=name, sha256=p.sha(self.source/name))

    def save_spec(self): self.dump(self.input, self.spec)

    def alter_obs(self, change, i=0):
        path = self.source/f"frame-{i}.json"; doc=p.read(path)
        change(doc["data"]["observation"]["_0"])
        self.dump(path, doc); self.spec["frames"][i]["observation"]=self.relative(path.name); self.save_spec()

    def imported(self):
        out=self.root/"intake"; p.import_capture(self.input, out)
        return out

    def review_input(self, intake):
        doc=p.read(intake/"review-template.json")
        for i, row in enumerate(doc["frames"]):
            row.update(confirmed=True, reviewer="test-only-reviewer", reviewedAt=datetime.now(timezone.utc).isoformat(),
                       reviewReference="test-only-generated-labels", photosConfirmed=True, settled=True, contentApproved=True,
                       controls=[dict(id="button-a", bounds=[35.25,50.5,75,54], state="focused" if i==0 else "unfocused"),
                                 dict(id="button-b", bounds=[170,50,90,55], state="unfocused" if i==0 else "focused")])
        doc["pairs"]=[dict(id="pair-1", elementID="button-a", focusedFrame="frame-0", unfocusedFrame="frame-1")]
        path=self.root/"review.json"; self.dump(path,doc)
        return path

    def fake_crop(self, items):
        result=[]
        for item in items:
            # Unit-only stand-in; a separate CLI test invokes the actual production helper.
            im=Image.new("RGB", (256,256), "white" if item["id"].endswith(":focused") else "gray")
            stream=io.BytesIO(); im.save(stream,format="PNG")
            result.append(dict(id=item["id"],png=base64.b64encode(stream.getvalue()).decode()))
        return dict(results=result)

    def review(self, change=lambda d: None):
        intake=self.imported(); path=self.review_input(intake); doc=p.read(path);change(doc);self.dump(path,doc)
        with patch.object(p,"invoke",side_effect=self.fake_crop):
            return p.review_capture(intake/"intake.json",path,self.root/"reviewed")

    def test_actual_cli_and_production_crop(self):
        before={f.name:p.sha(f) for f in self.source.iterdir()}
        intake=self.root/"intake"
        def cli(*args):
            result=subprocess.run([sys.executable,str(ROOT/"scripts/photos_focus_pilot.py"),*map(str,args)],
                                  capture_output=True,text=True,timeout=60)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        cli("import","--input",self.input,"--output",intake)
        review=self.review_input(intake); output=self.root/"reviewed"
        cli("review","--intake",intake/"intake.json","--review",review,"--output",output)
        doc=p.sealed(output/"diagnostic.json",p.DIAGNOSTIC)
        self.assertEqual(doc["pairCounts"],{"accepted-diagnostic":1})
        self.assertEqual(doc["runtime"],p.identity())
        self.assertEqual(doc["preprocessing"],p.RUNTIME_PREPROCESSING)
        self.assertFalse(doc["trainingEligible"])
        self.assertEqual(before,{f.name:p.sha(f) for f in self.source.iterdir()})
        self.assertTrue((output/"sheets/pair-1-pair.png").is_file())
        self.assertEqual(len(list((output/"crops").glob("*.png"))),2)
        with self.assertRaises(FocusDataError): validate_manifest(doc,output)
        with self.assertRaises(FocusDataError): assemble(doc)
        with self.assertRaises(FocusDataError): validate_evaluation(doc)
        # Even copying into the trainer's expected filename cannot grant admission.
        self.dump(output/"focus_dataset_manifest.json", doc)
        rejected=subprocess.run([sys.executable,str(ROOT/"scripts/train_focus_ring_detector.py"),
            "--dataset",str(output),"--name","photos-pilot-rejection-only","--preflight"],
            capture_output=True,text=True,timeout=30)
        self.assertEqual(rejected.returncode,2,rejected.stdout+rejected.stderr)
        self.assertIn("unsupported_crop_manifest",json.loads(rejected.stdout)["blockers"])
        self.assertFalse((ROOT/"NativeUITrainer/focus_ring_runs/photos-pilot-rejection-only").exists())

    def test_wrong_source_device_accounted(self):
        self.alter_obs(lambda o:o.update(sourceDeviceID="wrong"))
        doc=p.import_capture(self.input,self.root/"out")
        self.assertEqual(doc["counts"],{"blocked":1,"imported":1})
        self.assertEqual(doc["frames"][0]["reason"],"wrong_source_device")

    def test_wrong_session_fails_before_output(self):
        self.spec["sessionID"]="other";self.save_spec()
        with self.assertRaisesRegex(FocusDataError,"wrong_session"):
            p.import_capture(self.input,self.root/"out")
        self.assertFalse((self.root/"out").exists())

    def test_missing_and_changed_inputs_accounted(self):
        (self.source/"frame-0.png").unlink();(self.source/"frame-1.png").write_bytes(b"changed")
        doc=p.import_capture(self.input,self.root/"out")
        self.assertEqual(doc["counts"],{"blocked":2})

    def test_corrupt_png_preserved_and_blocked(self):
        (self.source/"frame-0.png").write_bytes(b"not a png")
        self.spec["frames"][0]["image"]=self.relative("frame-0.png");self.save_spec()
        doc=p.import_capture(self.input,self.root/"out")
        self.assertEqual(doc["frames"][0]["state"],"blocked")
        self.assertEqual((self.root/"out/raw/frames/frame-0/frame.png").read_bytes(),b"not a png")

    def test_black_capture_blocked(self):
        Image.new("RGB",(320,180),"black").save(self.source/"frame-0.png")
        self.spec["frames"][0]["image"]=self.relative("frame-0.png");self.save_spec()
        self.assertEqual(p.import_capture(self.input,self.root/"out")["frames"][0]["reason"],"black_capture")

    def test_stale_observation_blocked(self):
        self.alter_obs(lambda o:o["freshness"].update(status="stale"))
        self.assertEqual(p.import_capture(self.input,self.root/"out")["frames"][0]["reason"],"stale_observation")

    def test_generation_change_blocks_entire_segment(self):
        self.alter_obs(lambda o:o.update(connectionGeneration=2),1)
        self.assertEqual(p.import_capture(self.input,self.root/"out")["counts"],{"blocked":2})

    def test_duplicate_observation_blocks_second(self):
        self.alter_obs(lambda o:o.update(id={"rawValue":"frame-0"}),1)
        self.assertEqual(p.import_capture(self.input,self.root/"out")["frames"][1]["reason"],"duplicate_observation_id")

    def test_output_collision_and_symlink_rejected(self):
        out=self.imported()
        with self.assertRaises(FocusDataError): p.import_capture(self.input,out)
        alias=self.root/"link";alias.symlink_to(self.source,target_is_directory=True)
        with self.assertRaises(FocusDataError): p.import_capture(self.input,alias/"out")

    def test_storage_reserve_includes_copy_size(self):
        with patch.object(p.shutil,"disk_usage",return_value=SimpleNamespace(free=2_000_000_001)):
            with self.assertRaisesRegex(FocusDataError,"storage_reserve"):
                p.import_capture(self.input,self.root/"out")
        self.assertFalse((self.root/"out").exists())

    def test_input_traversal_rejected_and_accounted(self):
        self.spec["frames"][0]["image"]["path"]="../frame.png";self.save_spec()
        self.assertEqual(p.import_capture(self.input,self.root/"out")["frames"][0]["state"],"blocked")

    def test_unconfirmed_review_blocks_pair(self):
        doc=self.review(lambda d:d["frames"][0].update(confirmed=False))
        self.assertEqual(doc["pairCounts"],{"blocked":1});self.assertIsNone(doc["runtime"])

    def test_invalid_bounds_blocks_pair(self):
        doc=self.review(lambda d:d["frames"][0]["controls"][0].update(bounds=[-1,0,30,20]))
        self.assertEqual(doc["pairCounts"],{"blocked":1})

    def test_unknown_focus_blocks_pair(self):
        doc=self.review(lambda d:d["frames"][0]["controls"][0].update(state="unknown"))
        self.assertEqual(doc["pairCounts"],{"blocked":1})

    def test_multiple_focus_blocks_pair(self):
        doc=self.review(lambda d:d["frames"][0]["controls"][1].update(state="focused"))
        self.assertEqual(doc["pairCounts"],{"blocked":1})

    def test_missing_pair_frame_accounted(self):
        doc=self.review(lambda d:d["pairs"][0].update(unfocusedFrame="missing"))
        self.assertEqual(doc["pairCounts"],{"blocked":1})

    def test_changed_review_hash_blocks_pair(self):
        doc=self.review(lambda d:d["frames"][0].update(imageSHA256="0"*64))
        self.assertEqual(doc["pairCounts"],{"blocked":1})

    def test_native_conflict_preserved_and_blocks(self):
        self.dump(self.source/"native.json",dict(testOnly=True,reportedFocus="other"))
        self.spec["frames"][0]["nativeEvidence"]=self.relative("native.json");self.save_spec()
        doc=self.review(lambda d:d["frames"][0].update(nativeAssessment="conflict"))
        self.assertEqual(doc["pairCounts"],{"blocked":1})
        self.assertTrue((self.root/"intake/raw/frames/frame-0/native.json").exists())

    def test_frame_names_cannot_overwrite_metadata(self):
        for row, name in zip(self.spec["frames"],("index","session")):
            row["id"]=name
        self.save_spec();original=self.input.read_bytes()
        doc=p.import_capture(self.input,self.root/"out")
        self.assertEqual(doc["counts"],{"imported":2})
        self.assertEqual((self.root/"out/raw/index.json").read_bytes(),original)

    def test_duplicates_do_not_inflate_accepted_pair_count(self):
        def change(d): d["pairs"].append({**d["pairs"][0],"id":"pair-2"})
        doc=self.review(change)
        self.assertEqual(doc["pairCounts"],{"accepted-diagnostic":1,"duplicate":1})

    def test_identical_frames_cannot_be_focus_pair(self):
        shutil.copyfile(self.source/"frame-0.png",self.source/"frame-1.png")
        self.spec["frames"][1]["image"]=self.relative("frame-1.png");self.save_spec()
        doc=self.review()
        self.assertEqual(doc["pairCounts"],{"blocked":1})
        self.assertEqual(doc["distinctFramePixels"],1)

    def test_crop_failure_explicit(self):
        intake=self.imported(); review=self.review_input(intake)
        with patch.object(p,"invoke",side_effect=FocusDataError("test crop failure")):
            doc=p.review_capture(intake/"intake.json",review,self.root/"out")
        self.assertEqual(doc["pairCounts"],{"blocked":1})

    def test_missing_crop_runtime_explicit(self):
        intake=self.imported(); review=self.review_input(intake)
        with patch.object(p,"identity",side_effect=FocusDataError("missing_runtime")), patch.object(p,"invoke") as invoke:
            doc=p.review_capture(intake/"intake.json",review,self.root/"out")
            invoke.assert_not_called()
        self.assertEqual(doc["pairCounts"],{"blocked":1})

    def test_legacy_optional_metadata_is_not_fabricated(self):
        for i in range(2):
            self.alter_obs(lambda o:(o.pop("connectionGeneration"),o.pop("receivedAt")),i)
        doc=p.import_capture(self.input,self.root/"out")
        self.assertEqual(doc["counts"],{"imported":2})
        self.assertNotIn("connectionGeneration",doc["frames"][0]["metadata"])

    def test_review_frame_omission_rejected(self):
        intake=self.imported(); review=self.review_input(intake);doc=p.read(review);doc["frames"].pop();self.dump(review,doc)
        with self.assertRaisesRegex(FocusDataError,"membership"):
            p.review_capture(intake/"intake.json",review,self.root/"out")

    def test_malformed_pair_stays_accounted(self):
        doc=self.review(lambda d:d["pairs"][0].pop("elementID"))
        self.assertEqual(doc["pairCounts"],{"blocked":1})

    def test_pair_and_screen_caps(self):
        intake=self.imported();review=self.review_input(intake);doc=p.read(review)
        doc["pairs"]=[{**doc["pairs"][0],"id":f"pair-{i}"} for i in range(21)];self.dump(review,doc)
        with self.assertRaisesRegex(FocusDataError,"pair_limit"):
            p.review_capture(intake/"intake.json",review,self.root/"out")

    def test_sensitive_or_unsettled_review_blocks(self):
        doc=self.review(lambda d:d["frames"][0].update(contentApproved=False,settled=False))
        self.assertEqual(doc["pairCounts"],{"blocked":1})

    def test_crop_contradiction_blocks_both_labels(self):
        intake=self.imported(); review=self.review_input(intake)
        def same(items):
            reply=self.fake_crop(items)
            for row in reply["results"]: row["png"]=reply["results"][0]["png"]
            return reply
        with patch.object(p,"invoke",side_effect=same):
            doc=p.review_capture(intake/"intake.json",review,self.root/"out")
        self.assertEqual(doc["pairCounts"],{"blocked":1})

    def test_changed_intake_fails_closed(self):
        intake=self.imported(); review=self.review_input(intake)
        d=p.read(intake/"intake.json");d["trainingEligible"]=True;self.dump(intake/"intake.json",d)
        with self.assertRaises(FocusDataError): p.review_capture(intake/"intake.json",review,self.root/"out")

    def test_no_model_or_navigation_dependencies(self):
        source=(ROOT/"scripts/photos_focus_pilot.py").read_text()
        for forbidden in ("import torch", "model_contract", "infer_bounded", "subprocess", "remote navigate"):
            self.assertNotIn(forbidden,source)


if __name__ == "__main__": unittest.main()
