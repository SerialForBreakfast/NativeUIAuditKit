"""Generated offline adversarial tests; no live device or model calls."""
import base64
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image
import human_annotation_review as h
from focus_dataset_contract import FocusDataError, validate_manifest
from focus_surface_evaluation import validate as validate_evaluation


def envelope(kind, value, command):
    return dict(schemaVersion=1, success=True, command=command, data={kind: {"_0": value}})


def stamp(n):
    return dict(monotonic=dict(nanoseconds=n), wallClock=800000000+n)


class ReviewTests(unittest.TestCase):
    def setUp(self):
        parent = h.ROOT/".build/human-review/tests"; parent.mkdir(parents=True, exist_ok=True)
        self.root = Path(tempfile.mkdtemp(dir=parent))
        self.source = self.root/"source"; self.source.mkdir()
        self.frames, events = [], [dict(id="start", kind="sessionStarted", sequenceNumber=1,
                                       sessionID="session", timestamp=stamp(0), observationIDs=[])]
        self.dump(self.source/"start.json", envelope("session", "session", "session start"))
        for n in range(2):
            name = f"frame-{n}"
            Image.new("RGB", (100, 60), "white" if n == 0 else "gray").save(self.source/(name+".png"))
            obs = dict(id=name, sourceDeviceID="office", connectionGeneration=2, providerID="avfoundation-video",
                       capturedAt=stamp(2+n*3), receivedAt=stamp(3+n*3),
                       dimensions=dict(width=100, height=60), orientation="up", mimeType="image/png",
                       freshness=dict(status="current"), outputWritten=False, precedingCommandIDs=[],
                       imageBase64=base64.b64encode((self.source/(name+".png")).read_bytes()).decode())
            self.dump(self.source/(name+".json"), envelope("observation", obs, "observe capture"))
            self.frames.append(dict(id=name, screen="screen", observationID=name,
                                    image=h.ref(self.source/(name+".png")), observation=h.ref(self.source/(name+".json")),
                                    proposals=[dict(id="button", **{"class":"primaryButton"}, bounds=[10.25, 15.5, 50, 20],
                                                    state="focused" if n == 0 else "unfocused")]))
            events.append(dict(id=name, kind="observation", sequenceNumber=n+2, sessionID="session",
                               timestamp=stamp(4+n*3), observationIDs=[name], deviceID="office"))
        events.append(dict(id="end", kind="sessionEnded", sequenceNumber=4, sessionID="session",
                           timestamp=stamp(10), observationIDs=[]))
        self.dump(self.source/"timeline.json", envelope("timeline", events, "session timeline"))
        self.spec = dict(version=h.INDEX, **h.FLAGS, id="test", sessionID="session", sourceDeviceID="office", generation=2,
                         sessionStart=h.ref(self.source/"start.json"), timeline=h.ref(self.source/"timeline.json"), frames=self.frames,
                         pairs=[dict(id="pair", controlID="button", frames=["frame-0", "frame-1"])])
        self.input = self.source/"index.json"; self.save_spec()
        self.batch = self.root/"batch"

    def tearDown(self):
        shutil.rmtree(self.root)

    def dump(self, path, value):
        path.write_text(json.dumps(value))

    def save_spec(self):
        self.spec.pop("seal", None); self.spec["seal"] = h.digest(self.spec)
        self.dump(self.input, self.spec)

    def imported(self):
        return h.import_batch(self.input, self.batch)

    def annotate(self, change=lambda d: None):
        for path in sorted((self.batch/"editor").glob("*.json")):
            doc = h.read(path)
            doc["flags"] = {k: True for k in h.FRAME_FLAGS}
            for s in doc["shapes"]: s["flags"]["confirmed"] = True
            change(doc); self.dump(path, doc)

    def finish(self, kind="human"):
        # 'human' branch is unit-tested exclusively on generated fixture images.
        return h.finish(self.batch/"batch.json", self.root/"revision", reviewer="unit-fixture",
                        reference="generated test only", reviewer_kind=kind, confirm_batch=True)

    def alter_obs(self, change, n=0):
        path = self.source/f"frame-{n}.json"; doc = h.read(path)
        change(doc["data"]["observation"]["_0"]); self.dump(path, doc)
        self.spec["frames"][n]["observation"] = h.ref(path); self.save_spec()

    def test_valid_roundtrip_and_original_preservation(self):
        before = {p.name: h.sha(p) for p in self.source.iterdir()}
        result = self.imported(); self.assertEqual(result["counts"], {"imported":2})
        self.annotate(lambda d: d["shapes"][0]["points"][0].__setitem__(0, 10.75))
        reviewed = self.finish()
        self.assertEqual(reviewed["frameCounts"], {"reviewed":2})
        self.assertEqual(reviewed["frames"][0]["controls"][0]["bounds"][0], 10.75)
        self.assertEqual(reviewed["pairs"][0]["disposition"], "reviewed")
        self.assertFalse(reviewed["trainingEligible"])
        self.assertEqual(before, {p.name: h.sha(p) for p in self.source.iterdir()})

    def test_unchanged_fractional_coordinates(self):
        self.imported(); self.annotate()
        self.assertEqual(self.finish()["frames"][0]["controls"][0]["bounds"], [10.25,15.5,50,20])

    def test_software_test_cannot_confirm(self):
        self.imported(); self.annotate()
        result = self.finish("software-test")
        self.assertEqual(result["frameCounts"], {"blocked":2})
        self.assertEqual(result["pairs"][0]["disposition"], "blocked")

    def test_pending_labels(self):
        self.imported(); result = self.finish()
        self.assertEqual(result["controlCounts"], {"blocked":2})

    def test_unknown_and_conflicting_focus(self):
        for focused, unfocused in ((False,False),(True,True)):
            with self.subTest(focused=focused, unfocused=unfocused):
                self.imported()
                self.annotate(lambda d: d["shapes"][0]["flags"].update(focused=focused,unfocused=unfocused))
                result = self.finish()
                self.assertEqual(result["controlCounts"], {"blocked":2})
                shutil.rmtree(self.root/"revision")

    def test_flagged_and_rejected(self):
        self.imported(); self.annotate(lambda d: d["shapes"][0]["flags"].update(rejected=True))
        self.assertEqual(self.finish()["frameCounts"], {"rejected":2})

    def test_idempotent_import_preserves_edits(self):
        self.imported(); self.annotate()
        before = {p.name:h.sha(p) for p in (self.batch/"editor").iterdir()}
        self.imported()
        self.assertEqual(before, {p.name:h.sha(p) for p in (self.batch/"editor").iterdir()})

    def test_changed_index_rejected(self):
        self.imported(); self.spec["id"] = "changed"; self.save_spec()
        with self.assertRaisesRegex(FocusDataError,"changed_index"): self.imported()

    def test_missing_and_corrupt_images_accounted(self):
        (self.source/"frame-0.png").unlink()
        (self.source/"frame-1.png").write_bytes(b"invalid PNG")
        self.spec["frames"][1]["image"] = h.ref(self.source/"frame-1.png"); self.save_spec()
        result = self.imported(); self.assertEqual(result["counts"], {"blocked":2})
        self.assertEqual(len(result["frames"]), 2)

    def test_changed_hash(self):
        (self.source/"frame-0.png").write_bytes(b"different")
        result = self.imported()
        self.assertIn("changed_hash", result["frames"][0]["reasons"])

    def test_wrong_target(self):
        self.alter_obs(lambda d:d.update(sourceDeviceID="other"))
        self.assertIn("wrong_target",self.imported()["frames"][0]["reasons"])

    def test_wrong_inline_pixels(self):
        self.alter_obs(lambda d:d.update(imageBase64=base64.b64encode(b"other").decode()))
        self.assertIn("inline_image_mismatch",self.imported()["frames"][0]["reasons"])

    def test_wrong_generation(self):
        self.alter_obs(lambda d:d.update(connectionGeneration=3))
        self.assertIn("wrong_generation",self.imported()["frames"][0]["reasons"])

    def test_wrong_timestamp(self):
        self.alter_obs(lambda d:d.update(capturedAt=stamp(100)))
        self.assertIn("capture_time_mismatch",self.imported()["frames"][0]["reasons"])

    def test_duplicate_pixels(self):
        shutil.copyfile(self.source/"frame-0.png",self.source/"frame-1.png")
        self.spec["frames"][1]["image"] = h.ref(self.source/"frame-1.png")
        self.alter_obs(lambda d:d.update(imageBase64=base64.b64encode((self.source/"frame-1.png").read_bytes()).decode()),1)
        result=self.imported(); self.assertEqual(result["distinctPixels"],1)
        self.annotate(); self.assertEqual(self.finish()["pairs"][0]["disposition"],"blocked")

    def test_duplicate_membership(self):
        self.spec["frames"][1]["id"]="frame-0";self.save_spec()
        with self.assertRaisesRegex(FocusDataError,"duplicate_membership"):self.imported()

    def test_timeline_membership(self):
        self.spec["frames"].pop(); self.save_spec()
        with self.assertRaisesRegex(FocusDataError,"timeline_membership"):self.imported()

    def test_unsupported_protocol_and_training_admission(self):
        for key,value in (("version","unsupported"),("partition","final-challenge"),("trainingEligible",True)):
            with self.subTest(key=key):
                original=self.spec[key];self.spec[key]=value;self.save_spec()
                with self.assertRaises(FocusDataError):self.imported()
                self.spec[key]=original
        self.save_spec();self.imported();self.annotate();result=self.finish()
        with self.assertRaises(FocusDataError):validate_manifest(result,self.root)
        with self.assertRaises((FocusDataError,ValueError)):validate_evaluation(result)

    def test_swapped_binding_and_metadata(self):
        self.imported();self.annotate(lambda d:d["nuiak"].update(frameID="other"))
        self.assertIn("changed_image_binding",self.finish()["frames"][0]["reasons"])

    def test_changed_editor_image(self):
        self.imported();self.annotate()
        (self.batch/"editor/001-frame-0.png").write_bytes(b"changed")
        self.assertIn("changed_hash",self.finish()["frames"][0]["reasons"])

    def test_deleted_control(self):
        self.imported();self.annotate(lambda d:d.update(shapes=[]))
        self.assertIn("missing_control_use_rejected_flag",self.finish()["frames"][0]["reasons"])

    def test_bounds_nan_outside_and_degenerate(self):
        self.imported()
        originals={p:h.read(p) for p in (self.batch/"editor").glob("*.json")}
        for value in (float("nan"),-1,200,60.25):
            with self.subTest(value=value):
                for path,doc in originals.items():self.dump(path,doc)
                self.annotate(lambda d:d["shapes"][0].update(points=[[value,15.5],[60.25,35.5]]))
                self.assertEqual(self.finish()["frameCounts"],{"blocked":2})
                shutil.rmtree(self.root/"revision")

    def test_native_evidence_unresolved(self):
        self.spec["frames"][0]["nativeEvidence"] = self.spec["sessionStart"]
        self.save_spec();self.imported();self.annotate()
        self.assertIn("native_evidence_unresolved",self.finish()["frames"][0]["controls"][0]["reasons"])

    def test_incomplete_editor_membership(self):
        self.imported();(self.batch/"editor/001-frame-0.json").unlink()
        with self.assertRaisesRegex(FocusDataError,"editor_membership"):self.finish()

    def test_interrupted_output_and_explicit_finish(self):
        self.batch.mkdir()
        with self.assertRaises(OSError):self.imported()
        self.batch.rmdir();self.imported()
        with self.assertRaisesRegex(FocusDataError,"explicit_completion"):
            h.finish(self.batch/"batch.json",self.root/"revision",reviewer="r",reference="r",reviewer_kind="human",confirm_batch=False)
        self.assertFalse((self.root/"revision").exists())

    def test_real_cli_and_production_crop(self):
        result = subprocess.run([sys.executable,str(h.ROOT/"scripts/human_annotation_review.py"),
                                 "import",str(self.input),str(self.batch)],capture_output=True,text=True,timeout=60)
        self.assertEqual(result.returncode,0,result.stderr)
        report=h.crop_qa(self.batch/"batch.json",self.root/"crops")
        self.assertEqual((report["expected"],report["completed"]),(2,2))
        for c in report["crops"]:
            with Image.open(h.checked(h.ROOT,c["crop"])) as im:self.assertEqual(im.size,(256,256))

    def test_incomplete_crop_results_rejected(self):
        self.imported()
        with patch("focus_runtime.invoke",return_value=dict(results=[])):
            with self.assertRaisesRegex(FocusDataError,"incomplete_crops"):
                h.crop_qa(self.batch/"batch.json",self.root/"crops")
        self.assertFalse((self.root/"crops/crop-qa.json").exists())


if __name__ == "__main__":
    unittest.main()
