"""Offline assembly/real-CLI contracts. Generated examples are test-only."""
import base64
import copy
import io
import json
import subprocess
import sys
import unittest
from unittest.mock import patch
from PIL import Image

import focus_mixed_assembly as a
from focus_dataset_contract import ROOT, FocusDataError, digest, crop_frame, expanded_box
import test_focus_consumer_integration as fixtures
import test_native_os_focus_dataset as native_fixture
import native_os_focus_dataset as native


class AssemblyTests(unittest.TestCase):
    def setUp(self):
        self.fixture=fixtures.ConsumerTests(); self.fixture.setUp()
        self.addCleanup(self.fixture.tearDown)
        self.root=self.fixture.root
        self.baseline=self.root/"checkpoint.pt"; self.baseline.write_bytes(b"test-only-never-deserialized")
        self.entry=self.review(self.fixture.save(),"fixture")
        self.spec={"version":"focus-assembly-input-v1", "sources":[self.entry], "baseline":a.reference(self.baseline)}

    def review(self,path,sid,**overrides):
        doc=json.loads(path.read_text())
        data={"version":"focus-source-review-v1","manifestSHA256":a.reference(path)["sha256"],
              "reviewer":"unit-test-only", "reviewReference":"deterministic-test", "priorUse":"test-only",
              "relationshipsKnown":True,"trainingApproved":False,
              "pairs":{p["pair_id"]:{"partition":p["split"],"relatedGroup":p.get("lineage",p.get("recipe_group"))} for p in doc["pairs"]},
              **overrides}
        review=self.root/(sid+"-review.json"); review.write_text(json.dumps(data))
        return {"id":sid,"manifest":a.reference(path),"review":a.reference(review)}

    def rewrite_review(self,fn,index=0):
        entry=self.spec["sources"][index]; path=ROOT/entry["review"]["path"]
        doc=json.loads(path.read_text()); fn(doc); path.write_text(json.dumps(doc)); entry["review"]=a.reference(path)

    def write(self,doc,name="assembly"):
        out=self.root/name; out.mkdir()
        (out/"focus_dataset_manifest.json").write_text(json.dumps(doc))
        return out

    def test_determinism_and_loader(self):
        doc=a.assemble(self.spec); self.assertEqual(doc,a.assemble(self.spec))
        out=self.write(doc); self.assertEqual(a.load(out/"focus_dataset_manifest.json"),doc)
        from train_focus_ring_detector import load_samples
        self.assertEqual(len(load_samples(out,"development")),2)
        self.assertEqual(load_samples(out,"train"),[])
        self.assertFalse(doc["trainingEligible"])

    def test_cli_and_real_trainer_refuse_test_only_without_launch(self):
        source=self.root/"input.json"; source.write_text(json.dumps(self.spec))
        cmd=[sys.executable,str(ROOT/"scripts/focus_mixed_assembly.py"),"--input",str(source),"--output",str(self.root/"cli")]
        result=subprocess.run(cmd,capture_output=True,text=True,timeout=20)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(subprocess.run(cmd,capture_output=True,text=True,timeout=20).returncode,2)
        before=set(self.root.rglob("*"))
        command=[sys.executable,str(ROOT/"scripts/train_focus_ring_detector.py"),"--dataset",str(self.root/"cli"),
                 "--name",self.root.name,"--preflight"]
        result=subprocess.run(command,capture_output=True,text=True,timeout=20)
        self.assertEqual(result.returncode,2,result.stderr)
        report=json.loads(result.stdout)
        self.assertTrue(report["configurationValid"])
        self.assertFalse(report["launchEligible"])
        self.assertIn("test_only_evidence",report["diagnosticOnlyBlockers"])
        self.assertIn("underfilled_quota",report["blockers"])
        self.assertEqual(before,set(self.root.rglob("*")))
        self.assertFalse((ROOT/report["output"]).exists())

    def test_changed_bytes_review_baseline_and_unsupported_source(self):
        for field in ("manifest","review"):
            spec=copy.deepcopy(self.spec); spec["sources"][0][field]["sha256"]="0"*64
            with self.assertRaisesRegex(FocusDataError,"changed_assembly_input"): a.assemble(spec)
        self.baseline.write_bytes(b"changed")
        with self.assertRaisesRegex(FocusDataError,"changed_assembly_input"): a.assemble(self.spec)
        self.spec["baseline"]=a.reference(self.baseline)
        path=self.fixture.save(); doc=json.loads(path.read_text()); doc["version"]="future"
        path.write_text(json.dumps(doc)); self.spec["sources"]=[self.review(path,"future")]
        with self.assertRaisesRegex(FocusDataError,"unsupported_assembly_source"): a.assemble(self.spec)

    def test_missing_review_and_visual_only_not_admitted(self):
        self.rewrite_review(lambda r:r.pop("reviewer"))
        with self.assertRaises(FocusDataError): a.assemble(self.spec)
        path=self.root/"visual.json"; path.write_text(json.dumps({"version":"perception-benchmark-v1","pairs":[]}))
        self.spec["sources"]=[self.review(path,"visual")]
        with self.assertRaisesRegex(FocusDataError,"unsupported_assembly_source"): a.assemble(self.spec)

    def test_prediction_label_rejected(self):
        self.fixture.doc["pairs"][0]["labelSource"]="modelPrediction"
        self.spec["sources"]=[self.review(self.fixture.save(),"fixture")]
        with self.assertRaisesRegex(FocusDataError,"untrusted_pair_source"): a.assemble(self.spec)

    def test_partition_and_evaluation_reuse(self):
        self.rewrite_review(lambda r:r["pairs"]["a"].update(partition="train"))
        with self.assertRaisesRegex(FocusDataError,"partition_drift"): a.assemble(self.spec)
        self.fixture.doc["pairs"][0]["split"]="test"
        self.spec["sources"]=[self.review(self.fixture.save(),"fixture",priorUse="development")]
        with self.assertRaisesRegex(FocusDataError,"evaluation_reuse"): a.assemble(self.spec)

    def test_pair_duplication_rejected(self):
        self.spec["sources"].append({**self.entry,"id":"copy"})
        with self.assertRaisesRegex(FocusDataError,"duplicate_pair_content"): a.assemble(self.spec)

    def test_cross_source_pixels_groups_and_contradictory_labels(self):
        rows=a.assemble(self.spec)["samples"]
        extra=copy.deepcopy(rows); extra[0]["id"]="other0"; extra[1]["id"]="other1"
        for r in extra: r.update(split="test",sourceID="other",pairID="b",relatedGroup="different",intrinsicGroup="different",recipeSeed=99)
        with self.assertRaisesRegex(FocusDataError,"split_leakage"): a.isolation(rows+extra)
        extra=copy.deepcopy(rows)
        extra[0]["label"]=1-extra[0]["label"]; extra[0]["id"]="contradiction"
        with self.assertRaisesRegex(FocusDataError,"contradictory_crop_labels"): a.isolation(rows+extra)
        extra=copy.deepcopy(rows)
        for i,r in enumerate(extra):
            r.update(id="new"+str(i),pairID="different",split="test",recipeSeed=99,intrinsicGroup="different")
            r["crop"]["pixelSHA256"]="newcrop"+str(i); r["frame"]["pixelSHA256"]="newframe"+str(i)
        with self.assertRaisesRegex(FocusDataError,"split_leakage"): a.isolation(rows+extra)

    def test_training_weights_ignore_validation_and_development(self):
        rows=a.assemble(self.spec)["samples"]
        for r in rows: r["split"]="train"
        extra=copy.deepcopy(rows)
        for i,r in enumerate(extra): r.update(id="extra"+str(i),scene="another")
        weighted=a.sampling(rows+extra)
        holdout=copy.deepcopy(extra)
        for r in holdout: r["split"]="validation"
        self.assertEqual(weighted,a.sampling(rows+extra+holdout*50))
        self.assertAlmostEqual(sum(weighted["weights"].values()),4.)
        duplicated=copy.deepcopy(rows)
        for i,r in enumerate(duplicated): r["id"]="repeat"+str(i)
        weights=a.sampling(rows+extra+duplicated)["weights"]
        self.assertEqual(weights[extra[0]["id"]],2*weights[rows[0]["id"]])

    def test_additive_retention_and_membership_tampering(self):
        first=a.assemble(self.spec); path=self.write(first)/"focus_dataset_manifest.json"
        new=copy.deepcopy(self.spec); new["previous"]=a.reference(path)
        second=a.assemble(new)
        self.assertEqual(second["delta"]["addedSamples"],[])
        self.rewrite_review(lambda r:r.update(reviewReference="changed"))
        self.spec["previous"]=a.reference(path)
        with self.assertRaisesRegex(FocusDataError,"retention_or_partition_drift"): a.assemble(self.spec)
        first["samples"][0]["label"]=7
        first["assemblySHA256"]=digest({k:v for k,v in first.items() if k!="assemblySHA256"})
        path.write_text(json.dumps(first))
        with self.assertRaises(FocusDataError): a.load(path)

    def test_unknown_relationships_and_approval_hash(self):
        self.rewrite_review(lambda r:r.update(relationshipsKnown=False))
        doc=a.assemble(self.spec); out=self.write(doc)
        (out/"training_approval.json").write_text(json.dumps({"version":"focus-assembly-approval-v1",
            "approved":True,"assemblySHA256":"stale","reviewer":"test","reviewReference":"test"}))
        ready=a.readiness(doc,out)
        self.assertIn("unknown_source_relationships",ready["blockers"])
        self.assertIn("missing_corpus_approval",ready["blockers"])

    def test_review_revision_keeps_membership_and_records_delta(self):
        old=a.assemble(self.spec); path=self.write(old)/"focus_dataset_manifest.json"
        old_entry=copy.deepcopy(self.entry)
        review=json.loads((ROOT/old_entry["review"]["path"]).read_text())
        review.update(supersedesReview=old_entry["review"],trainingApproved=True)
        next_review=self.root/"review-next.json"; next_review.write_text(json.dumps(review))
        self.spec["sources"][0]["review"]=a.reference(next_review)
        self.spec["previous"]=a.reference(path)
        result=a.assemble(self.spec)
        self.assertEqual(result["delta"]["updatedReviews"],["fixture"])
        self.assertEqual(result["delta"]["addedSamples"],[])
        self.assertIn("test_only_evidence",result["samples"][0]["sourceBlockers"])

    def test_positive_preflight_and_training_loader_with_mocked_runtime_and_quota(self):
        # Positive launch-eligibility plumbing only; not genuine corpus qualification.
        f=self.fixture
        f.doc["pairs"][0]["split"]="train"
        f.add_pair("v","validation",2); f.add_pair("t","test",3)
        f.doc.update(version="1.3",evidenceKind="reviewed-fixture")
        self.spec["sources"]=[self.review(f.save(),"fixture",priorUse="untouched",trainingApproved=True)]
        with patch.object(a,"validate_manifest",return_value=[]),patch("focus_ring_readiness.validate",return_value={"testOnlyMock":True}):
            doc=a.assemble(self.spec); out=self.write(doc)
            (out/"training_approval.json").write_text(json.dumps({"version":"focus-assembly-approval-v1", "approved":True,
                "assemblySHA256":doc["assemblySHA256"],"reviewer":"test-only","reviewReference":"mocked-quota-only"}))
            from focus_training_preflight import preflight
            from train_focus_ring_detector import load_samples, main
            report=preflight(out,self.root.name)
            self.assertTrue(report["launchEligible"],report)
            self.assertFalse(report["executionAuthorized"])
            self.assertEqual(report["counts"]["train"],1)
            self.assertEqual(len(load_samples(out,"train")),2)
            self.assertEqual(len(load_samples(out,"validation")),2)
            self.assertEqual({r["id"] for r in load_samples(out,"train")},set(doc["sampling"]["weights"]))
            before="torch" in sys.modules
            with patch.object(sys,"argv",["trainer","--dataset",str(out),"--name",self.root.name,"--preflight"]),patch("builtins.print"):
                self.assertEqual(main(),0)
            self.assertEqual("torch" in sys.modules,before)
            self.assertFalse((ROOT/report["output"]).exists())
            self.assertFalse(preflight(out,self.root.name,epochs=1)["configurationValid"])

    def test_corrupt_missing_crops_and_symlink_output(self):
        source=self.root/"input.json"; source.write_text(json.dumps(self.spec))
        (self.root/"link").symlink_to(self.fixture.data,target_is_directory=True)
        command=[sys.executable,str(ROOT/"scripts/focus_mixed_assembly.py"),"--input",str(source),"--output",str(self.root/"link/new")]
        result=subprocess.run(command,capture_output=True,text=True,timeout=20)
        self.assertEqual(result.returncode,2); self.assertIn("symlink_output",result.stderr)
        crop=self.fixture.data/self.fixture.doc["pairs"][0]["focused_crop"]
        crop.write_bytes(b"broken")
        with self.assertRaisesRegex(FocusDataError,"changed_hash"): a.assemble(self.spec)
        crop.unlink()
        with self.assertRaisesRegex(FocusDataError,"missing_pixels"): a.assemble(self.spec)

    def test_native_adapter_reconstructs_truth_and_mix(self):
        f=native_fixture.NativeIntakeTests(); f.setUp(); self.addCleanup(f.doCleanups)
        # Nonuniform pixels avoid opposite labels on identical uniform crops.
        for i in range(2):
            im=Image.new("RGB",(200,100))
            im.putdata([((x+i*37)%256,(y*2+i*47)%256,(x+y)%256) for y in range(100) for x in range(200)])
            im.save(f.root/f"{i}.png")
            p=f.root/f"{i}.json"; d=json.loads(p.read_text()); d["pngSHA256"]=a.reference(f.root/f"{i}.png")["sha256"]
            p.write_text(json.dumps(d))
        def render(items,model=None):
            values=[]
            for item in items:
                with Image.open(item["path"]) as im: crop=crop_frame(im,expanded_box(item["bounds"],im.size))
                stream=io.BytesIO(); crop.save(stream,format="PNG")
                values.append({"id":item["id"],"png":base64.b64encode(stream.getvalue()).decode()})
            return {"results":values}
        with patch.object(native,"identity",return_value={"test":True}),patch.object(a,"identity",return_value={"test":True}),patch.object(native,"invoke",side_effect=render),patch.object(a,"invoke",side_effect=render):
            doc=native.build(f.root,"exact","native-test",f.root/"out")
            entry=self.review(f.root/"out/manifest.json","native",priorUse="development")
            self.spec["sources"].append(entry)
            result=a.assemble(self.spec)
            self.assertEqual(len(result["samples"]),6)
            self.assertEqual({r["labelSource"] for r in result["samples"]},{"fixtureGroundTruth","nativeAX-capture-interval"})
            self.assertEqual({r["style"] for r in result["samples"] if r["sourceID"]=="native"},{"unknown"})
            self.rewrite_review(lambda r:[v.update(partition="train") for v in r["pairs"].values()],index=1)
            self.assertEqual(len(a.assemble(self.spec)["sampling"]["weights"]),4)
            doc["pairs"][0]["frames"]["focused"]["bounds"][0]+=1
            doc["manifestSHA256"]=digest({k:v for k,v in doc.items() if k!="manifestSHA256"})
            (f.root/"out/manifest.json").write_text(json.dumps(doc))
            self.spec["sources"][1]=self.review(f.root/"out/manifest.json","native",priorUse="development")
            with self.assertRaisesRegex(FocusDataError,"changed_native_geometry_or_label"): a.assemble(self.spec)


if __name__=="__main__": unittest.main()
