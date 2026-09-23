import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

from PIL import Image
import direct_tvos_capture as d
import direct_tvos_resume as r
from focus_dataset_contract import ROOT, FocusDataError, digest
from direct_focus_manifest import pairs_from_capture, validate_direct_manifest, validate_direct_frames


class ResumeTests(unittest.TestCase):
    def setUp(self):
        scratch = ROOT / ".build/debug-output/direct-resume-tests"
        scratch.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=scratch)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.device = {"schema_version": 1, "fixture_instance_id": "test-instance", "fixture_run_id": "test-run"}
        self.target = {"simulatorUDID": "9026ECA9-77DB-4AE6-8FE6-BB239E9571FA", "runtime": "tvOS-test-only",
                       "deviceProfile": "test-only", "xcode": "test-only", "pid": 1,
                       "endpoint": "http://127.0.0.1:8080", "binaries": {"TVTestRigFixture": "0"*64}}

    def frame(self, root, recipe, name, focused, device=None):
        device = device or self.device
        targets = d.expected_targets(recipe)
        elements = []
        for index, target in enumerate(targets):
            x, y, w, h = 2 + index % 5 * 18, 2 + index // 5 * 18, 10, 10
            elements.append({"element_id": target, "taxonomy_class": "primaryButton", "is_focused": target == focused,
                             "pixel_bounds": [x,y,w,h], "normalized_bounds": [x/100,y/100,(x+w)/100,(y+h)/100]})
        scene = {"schema_version": 1, "recipe": recipe, "is_settled": True, "focused_element_id": focused,
                 "scene_width": 100, "scene_height": 100, "elements": elements,
                 "focus_observation": {"verified": True, "source": "uikit_focus_system", "observedID": focused,
                                       "geometrySource": "uikit_window_converted_bounds", "generation": 1,
                                       "plannedFocusIDs": targets},
                 "observation_diagnostics": {"nativeFocusResolved": True, "reason": "ready", "missingIDs": [],
                                             "sampleAgeMilliseconds": 1, "stableMilliseconds": 200,
                                             "generation": 1, "sampledGeneration": 1}}
        now = time.time()
        def snap(stamp):
            return {"startedAt": stamp, "finishedAt": stamp+.01, "device": copy.deepcopy(device),
                    "scene": {**copy.deepcopy(scene), "timestamp": stamp}}
        # Distinct deterministic test pixels per recipe/state exercise the real
        # duplicate gate; metadata-only variety must not make identical pairs pass.
        color = tuple(bytes.fromhex(digest({"recipe":recipe,"focus":focused}))[:3])
        Image.new("RGB", (100,100), color).save(root/name)
        frame = {"path": name, "sha256": hashlib.sha256((root/name).read_bytes()).hexdigest(),
                 "binding": "native-observation-bracket-v1", "observedFocusID": focused,
                 "captureStartedAt": now+.02, "captureFinishedAt": now+.03,
                 "before": snap(now), "after": snap(now+.04)}
        d.write_json(root/(name+".json"), frame)
        return frame

    def receipt(self, name, start, stop, *, previous=None, failed=False, actual_stop=None, genuine=False):
        root = self.root/name; root.mkdir()
        device = {**self.device, "fixture_instance_id": "instance-"+name}
        doc = {"version": r.SEGMENT_VERSION if previous else "direct-tvos-capture-v1",
               "sourceKind": d.SOURCE, "state": "failed" if failed else "completed", "catalog": d.catalog(),
               "evidenceKind": "fixture-native-capture" if genuine else "test-only", "target": copy.deepcopy(self.target),
               "targetPlanSourceHashes": d.SOURCE_HASHES, "runnerSHA256": "a"*64, "initialDevice": device,
               "postflight": {"responsive": True, "device": device}, "recipes": [], "acceptedPairs": 0}
        if previous is not None:
            doc.update(recipeRange=[start,stop], predecessorSHA256=[hashlib.sha256(p.read_bytes()).hexdigest() for p in previous])
        for index in range(start, stop if actual_stop is None else actual_stop):
            recipe = d.catalog()["recipes"][index]
            targets = d.expected_targets(recipe)
            frames = [self.frame(root, recipe, f"{index:03d}-reference.png", None, device)]
            frames += [self.frame(root, recipe, f"{index:03d}-{n:03d}.png", target, device) for n,target in enumerate(targets)]
            doc["recipes"].append({"recipe": recipe, "expectedTargets": targets, "frames": frames})
            doc["acceptedPairs"] += len(targets)
        path = root/("failed.json" if failed else "segment.json")
        d.write_json(path, doc)
        return path

    def full_chain(self):
        a = self.receipt("a", 0, 42, failed=True, actual_stop=12)
        b = self.receipt("b", 12, 42, previous=[a])
        return [a,b]

    def cli(self, *args):
        return subprocess.run([sys.executable, str(ROOT/"scripts/direct_tvos_resume.py"), *map(str,args)],
                              capture_output=True, text=True, timeout=60)

    def test_real_assembly_cli_and_existing_consumer(self):
        paths = self.full_chain()
        before = [p.read_bytes() for p in paths]
        out = self.root/"assembly"
        result = self.cli("--assemble", "--receipts", *paths, "--output", out)
        self.assertEqual(result.returncode, 0, result.stderr)
        doc = json.loads((out/"direct-capture.json").read_text())
        self.assertEqual(d.validate_capture(doc, out), 246)
        self.assertEqual([p.read_bytes() for p in paths], before)
        self.assertEqual(doc["sources"][0]["state"], "failed")
        self.assertNotEqual(doc["sources"][0]["initialDevice"], doc["sources"][1]["initialDevice"])
        self.assertEqual(len(doc["recipes"]), 42)
        manifest = {"sourceKind": d.SOURCE, "purpose": "development-pilot", "evidenceKind": "test-only",
                    "captureSHA256": digest(doc), "pairs": pairs_from_capture(doc)}
        validate_direct_manifest(manifest, out)
        for pair in manifest["pairs"]: validate_direct_frames(pair, out)
        self.assertEqual(self.cli("--assemble", "--receipts", *paths, "--output", out).returncode, 2)
        # Existing actual validation CLI must dispatch the set contract.
        p = subprocess.run([sys.executable, str(ROOT/"scripts/direct_tvos_capture.py"), "--validate",
                            str(out/"direct-capture.json")], capture_output=True, text=True, timeout=60)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(json.loads(p.stdout)["pairs"], 246)

    def test_projection_and_source_bytes_fail_closed(self):
        paths = self.full_chain(); out = self.root/"assembly"
        doc = r.assemble(paths, out)
        bad = copy.deepcopy(doc); bad["recipes"][0]["frames"][0]["before"]["scene"]["elements"][0]["is_focused"] = True
        with self.assertRaisesRegex(FocusDataError, "changed_capture_projection"): d.validate_capture(bad, out)
        bad = copy.deepcopy(doc); bad["trainingEligible"] = True
        with self.assertRaises(FocusDataError): d.validate_capture(bad, out)
        raw = out/"runs/000/receipt.json"; raw.write_text("{}")
        with self.assertRaisesRegex(FocusDataError, "changed_source_receipt"): d.validate_capture(doc, out)

    def test_actual_crop_and_baseline_protocol_entrypoints(self):
        paths = self.full_chain(); out = self.root/"assembly"; r.assemble(paths,out)
        crops = self.root/"crops"
        result = subprocess.run([sys.executable,str(ROOT/"scripts/direct_focus_manifest.py"),
                                 "--capture",str(out/"direct-capture.json"),"--output",str(crops)],
                                capture_output=True,text=True,timeout=120)
        self.assertEqual(result.returncode,0,result.stderr)
        from focus_training_preflight import preflight
        self.assertFalse(preflight(crops,"test-only-assembled")["launchEligible"])
        manifest = json.loads((crops/"focus_dataset_manifest.json").read_text())
        self.assertEqual(len(manifest["pairs"]),246)
        self.assertEqual(manifest["evidenceKind"],"test-only")
        protocol = self.root/"protocol.json"
        result = subprocess.run([sys.executable,str(ROOT/"scripts/focus_ring_baseline.py"),
                                 "--prepare","--manifest",str(crops/"focus_dataset_manifest.json"),
                                 "--model",str(ROOT/"NativeUIAuditKitModels/Sources/NativeUIAuditKitModels/Resources/FocusRingDetector.mlmodelc"),
                                 "--output",str(protocol)],capture_output=True,text=True,timeout=120)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertTrue(protocol.is_file())

    def test_corrupt_copied_png_and_sidecar_rejected(self):
        paths = self.full_chain(); out = self.root/"assembly"; doc = r.assemble(paths,out)
        frame = doc["recipes"][0]["frames"][0]
        sidecar = out/(frame["path"]+".json"); old = sidecar.read_bytes(); sidecar.write_text("{}")
        with self.assertRaisesRegex(FocusDataError, "changed_frame_sidecar"): d.validate_capture(doc,out)
        sidecar.write_bytes(old); (out/frame["path"]).write_bytes(b"bad")
        with self.assertRaisesRegex(FocusDataError, "changed_hash"): d.validate_capture(doc,out)

    def test_gaps_overlaps_wrong_predecessor_target_and_provenance(self):
        a,b = self.full_chain(); original = json.loads(b.read_text())
        variants = [("recipeRange", [13,42]), ("predecessorSHA256", ["0"*64]),
                    ("evidenceKind", "fixture-native-capture"),
                    ("target", {**self.target, "runtime": "tvOS-other"})]
        for key,value in variants:
            doc = copy.deepcopy(original); doc[key] = value; b.write_text(json.dumps(doc))
            with self.subTest(key=key), self.assertRaises(FocusDataError): r.audit_chain([a,b])
        b.write_text(json.dumps(original))
        with self.assertRaises(FocusDataError): r.audit_chain([a,b,b])
        with self.assertRaises(FocusDataError): d.validate_capture(original,b.parent)

    def test_plan_cli_and_no_incomplete_assembly(self):
        a = self.receipt("a",0,42,failed=True,actual_stop=12)
        out = self.root/"plan.json"
        result = self.cli("--plan", "--receipts", a, "--output", out)
        self.assertEqual(result.returncode,0,result.stderr)
        plan = json.loads(out.read_text())
        self.assertEqual(plan["verifiedPairs"],30)
        self.assertEqual(len(plan["remainingRecipes"]),30)
        self.assertFalse(plan["executionAllowed"])
        self.assertFalse(plan["trainingEligible"])
        self.assertEqual(self.cli("--plan","--receipts",a,"--output",out).returncode,2)
        with self.assertRaisesRegex(FocusDataError,"incomplete_pilot"): r.assemble([a],self.root/"bad")
        self.assertFalse((self.root/"bad").exists())

    def test_multiple_segments_and_failed_prefix(self):
        a = self.receipt("a",0,42,failed=True,actual_stop=12)
        b = self.receipt("b",12,42,previous=[a],failed=True,actual_stop=14)
        c = self.receipt("c",14,42,previous=[a,b])
        doc = r.assemble([a,b,c],self.root/"all")
        self.assertEqual(d.validate_capture(doc,self.root/"all"),246)
        bad = json.loads(b.read_text()); bad["recipes"][-1]["frames"].pop(); b.write_text(json.dumps(bad))
        with self.assertRaisesRegex(FocusDataError,"incomplete_focus_sweep"): r.audit_chain([a,b])

    def test_execution_guards_before_mutation(self):
        a = self.receipt("a",0,42,failed=True,actual_stop=1,genuine=True)
        with patch.object(d,"bind_target",return_value=self.target), patch.object(d,"Fixture") as fixture:
            for target,review,error in [("booted",None,"wrong_resume_target"),
                                         (self.target["simulatorUDID"],None,"repair_review_required")]:
                with self.assertRaisesRegex(FocusDataError,error):
                    r.execute_resume([a],target,self.target["endpoint"],self.root/"out",1,review)
            fixture.assert_not_called()
        review = self.repair_review(a,self.target)
        with patch.object(d,"bind_target",return_value=self.target), patch.object(d,"Fixture") as fixture:
            with self.assertRaisesRegex(FocusDataError,"unchanged_failed_build"):
                r.execute_resume([a],self.target["simulatorUDID"],self.target["endpoint"],self.root/"out",1,review)
            fixture.assert_not_called()

    def repair_review(self, receipt, binding):
        report = self.root/"review.md"; report.write_text("Test double, no live repair qualification.")
        path = self.root/"review.json"
        d.write_json(path,{"version":"direct-tvos-repair-review-v1","accepted":True,
                          "failedReceiptSHA256":hashlib.sha256(receipt.read_bytes()).hexdigest(),
                          "targetPlanSourceHashes":d.SOURCE_HASHES,"replacementBinaries":binding["binaries"],
                          "report":str(report.relative_to(ROOT)),"reportSHA256":hashlib.sha256(report.read_bytes()).hexdigest()})
        return path

    def test_real_resume_execution_calls_only_missing_recipe(self):
        a = self.receipt("a",0,42,failed=True,actual_stop=1,genuine=True)
        binding = {**self.target,"binaries":{"TVTestRigFixture":"1"*64}}
        review = self.repair_review(a,binding)
        owner = self
        calls = []
        class Fixture:
            last_snapshot = None
            def __init__(self,endpoint): self.endpoint = endpoint
            def request(self,path,body=None):
                calls.append((path,body))
                return owner.device
        def frame(fixture,target,output,name,expected,recipe):
            return self.frame(output,recipe,name,expected)
        out = self.root/"continued"
        args = ["direct_tvos_resume.py","--execute","--receipts",str(a),"--output",str(out),
                "--target",binding["simulatorUDID"],"--endpoint",binding["endpoint"],
                "--recipe-limit","1","--repair-review",str(review)]
        with patch.object(d,"bind_target",return_value=binding), patch.object(d,"Fixture",Fixture), \
                patch.object(d,"capture_frame",side_effect=frame),patch.object(sys,"argv",args):
            self.assertEqual(r.main(),0)
        recipes = [body for path,body in calls if path=="/recipe"]
        self.assertEqual(recipes,[d.catalog()["recipes"][1]])
        doc = json.loads((out/"segment.json").read_text())
        self.assertEqual(doc["recipeRange"],[1,2])
        self.assertEqual(r.audit_chain([a,out/"segment.json"])[1:],(2,4))
        self.assertFalse((out/"direct-capture.json").exists())

    def test_resume_failure_preserved_without_mutation_retry(self):
        a = self.receipt("a",0,42,failed=True,actual_stop=1,genuine=True)
        binding = {**self.target,"binaries":{"TVTestRigFixture":"1"*64}}
        review = self.repair_review(a,binding); owner=self; calls=[]
        class Fixture:
            last_snapshot = None
            def __init__(self,endpoint): self.endpoint=endpoint
            def request(self,path,body=None):
                calls.append(path)
                if path=="/recipe": raise FocusDataError("injected_failure")
                return owner.device
        out=self.root/"failed-resume"
        with patch.object(d,"bind_target",return_value=binding),patch.object(d,"Fixture",Fixture):
            with self.assertRaisesRegex(FocusDataError,"injected_failure"):
                r.execute_resume([a],binding["simulatorUDID"],binding["endpoint"],out,1,review)
        self.assertEqual(calls.count("/recipe"),1)
        self.assertEqual(json.loads((out/"failed.json").read_text())["version"],r.SEGMENT_VERSION)
        self.assertFalse((out/"segment.json").exists())

    def test_repair_review_hash_and_changed_binding_rejected(self):
        a=self.receipt("a",0,42,failed=True,actual_stop=1,genuine=True)
        binding={**self.target,"binaries":{"TVTestRigFixture":"1"*64}}
        review=self.repair_review(a,binding)
        with patch.object(d,"bind_target",return_value=binding),patch.object(d,"Fixture") as fixture:
            (self.root/"review.md").write_text("changed")
            with self.assertRaisesRegex(FocusDataError,"changed_repair_report"):
                r.execute_resume([a],binding["simulatorUDID"],binding["endpoint"],self.root/"out",1,review)
            fixture.assert_not_called()

    def test_unsafe_paths_and_test_evidence_cannot_execute(self):
        a=self.receipt("a",0,42,failed=True,actual_stop=1)
        link=self.root/"alias.json"; link.symlink_to(a)
        with self.assertRaisesRegex(FocusDataError,"symlink_input"): r.audit_chain([link])
        with patch.object(d,"bind_target") as bind:
            with self.assertRaisesRegex(FocusDataError,"test_only_resume"):
                r.execute_resume([a],self.target["simulatorUDID"],self.target["endpoint"],self.root/"out",1)
            bind.assert_not_called()


if __name__ == "__main__": unittest.main()
